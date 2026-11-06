#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) slop checks over generated markup and styles.

Standard library only. Runs checks S1-S37 against the files an implementation step
produced. The source of record for these checks is references/slop-checklist.md;
change that file first when a check or a threshold changes.

Errors mean a value was used that the token set does not contain, or an
implementation is missing. Warnings mark tendencies, which is all the evidence
behind them supports.

CLI:
    python check_slop.py <path>... [--theme <theme.css>] [--json]

Each <path> may be a file or a directory. Without --theme, the script looks for
theme.css or tokens.css beneath the paths, then up to four directories above them.

A finding ruled on and kept is silenced from the file itself:
    product-ui: ignore S8 <reason>        the line before, or the same line
    product-ui: ignore-file S9 <reason>   anywhere in the file; S4-S7 for the run
A form with no reason is reported as S0 and silences nothing.

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors).
"""

import argparse
import bisect
import json
import math
import os
import re
import sys

from colour import hex_to_oklch

SCOPE_SUFFIXES = (".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".css")

SKIP_DIRS = {"node_modules", "vendor", "dist", "build", ".next", ".git", ".svelte-kit", "out"}
SKIP_NAMES = {"theme.css", "tokens.css"}
SKIP_PATTERNS = (".min.css", ".test.", ".spec.")

HEX = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
FUNC_COLOR = re.compile(r"\b(?:rgba?|hsla?)\([^)]*\)", re.IGNORECASE)
OKLCH_CALL = re.compile(r"\boklch\([^)]*\)", re.IGNORECASE)
MODERN_COLOR = re.compile(r"\b(?:oklch|oklab|lab|lch)\((?:[^()]|\([^()]*\))*\)", re.IGNORECASE)
# Arguments that read var() or the relative "from" syntax are built from tokens.
TOKEN_COLOR = re.compile(r"\bvar\(|^\w+\(\s*from\b", re.IGNORECASE)
# oklch(0% 0 0 / a), oklch(100% 0 0 / a) and the number forms 0 and 1: black and white shadows carry no hue to tokenise.
ACHROMATIC_SHADOW = re.compile(r"oklch\(\s*(?:0%|100%|0|1)\s+0\s+0\s*/(?:[^()]|\([^()]*\))*\)", re.IGNORECASE)

# S1 - Tailwind's default palette: <utility>-<family>-<step>[/<opacity>].
TW_FAMILIES = ("slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|"
               "blue|indigo|violet|purple|fuchsia|pink|rose")
PALETTE_CLASS = re.compile(
    r"(?<![\w-])(?:bg|text|border|ring|outline|fill|stroke|from|via|to|divide|decoration|placeholder|"
    r"caret|accent|shadow)-(" + TW_FAMILIES + r")-(50|100|200|300|400|500|600|700|800|900|950)(?![\w-])(?:/[\w.\[\]%]+)?")
THEME_COLOR_NAME = re.compile(r"--color-([a-z]+-\d+)\s*:")
CSS_IMPORT = re.compile(r"""@import\s+(?:url\(\s*)?["']([^"']+)["']""", re.IGNORECASE)
# [stroke='#ccc'] inside a class token selects on an attribute value; it sets no colour.
ATTRIBUTE_SELECTOR = re.compile(r"""\[[\w-]+\s*[~|^$*]?=\s*(?:'[^']*'|"[^"]*"|[^\]'"\s]*)\s*[is]?\]""")

FONT_FAMILY = re.compile(r"(?<![\w-])font-family\s*:\s*([^;}\n]+)", re.IGNORECASE)
FONT_ARBITRARY = re.compile(r"\bfont-\[([^\]]+)\]")
FONT_FACE_BLOCK = re.compile(r"@font-face\s*\{[^{}]*\}", re.IGNORECASE)

FORBIDDEN_FAMILIES = {"space grotesk", "poppins", "montserrat", "geist", "geist sans"}
MONOSPACE_HINTS = ("mono", "consolas", "menlo", "courier", "fira code", "source code")
# S4 counts type systems, so names that are no family of one are left out.
GENERIC_FAMILIES = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy", "math", "emoji", "fangsong", "system-ui",
    "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded", "-apple-system", "blinkmacsystemfont",
    "inherit", "initial", "unset", "revert", "null", "caption", "icon", "menu", "message-box",
    "small-caption", "status-bar",
}
ICON_FACE_HINTS = ("icon", "symbol", "awesome", "material", "glyph")
SCRIPT_FACE = re.compile(
    r"(?<![a-z0-9])(?:jp|sc|tc|kr|cjk)(?![a-z0-9])|hiragino|meiryo|メイリオ|yu gothic|游|ゴシック|明朝|mincho"
    r"|biz ud|yakuhan|ms pgothic")

GRADIENT_CALL = re.compile(r"\b(?:linear|radial|conic)-gradient\(", re.IGNORECASE)
STYLE_BLOCK = re.compile(r"<style\b[^>]*>.*?</style\s*>", re.DOTALL | re.IGNORECASE)
CLASS_SELECTOR = re.compile(r"\.(-?[A-Za-z_][\w-]*)")
TW_GRADIENT_STOP = re.compile(r"\b(?:from|via|to)-(\w+)-\d{2,3}\b")
# impeccable ai-color-palette: TW_FROM_PURPLE with TW_TO_PURPLE (crates/core/src/checks/rules.rs).
TW_FROM_PURPLE = re.compile(r"\bfrom-(?:purple|violet|indigo)-\d+\b")
TW_TO_PURPLE = re.compile(r"\bto-(?:purple|violet|indigo|blue|cyan|pink|fuchsia)-\d+\b")
BLUE_WORDS = {"blue", "indigo", "sky", "cyan"}
PURPLE_WORDS = {"purple", "violet", "fuchsia"}
PINK_WORDS = {"pink", "rose"}
# OKLCH hue bands; 286 sits between Tailwind's indigo (max 281) and violet (min 291).
BLUE_HUES = (200, 286)
PURPLE_HUES = (286, 330)
MIN_CHROMA = 0.12

RADIUS_DECL = re.compile(r"border-radius\s*:\s*([^;}\n]+)", re.IGNORECASE)
TW_ROUNDED = re.compile(r"\brounded(?:-(?:t|b|l|r|tl|tr|bl|br|s|e|ss|se|es|ee))?-([\w.\[\]/%-]+)\b")
NEUTRAL_RADII = {"0", "0px", "none", "9999px", "full", "50%"}

SHADOW_DECL = re.compile(r"box-shadow\s*:\s*([^;}\n]+)", re.IGNORECASE)
SHADOW_COLOR = re.compile(r"\b(?:rgba?|hsla?|oklch|oklab|lab|lch|hwb)\(((?:[^()]|\([^()]*\))*)\)", re.IGNORECASE)

# An emoji: an astral pictograph or flag; a BMP code point with Emoji_Presentation=Yes; a symbol
# followed by U+FE0F, keycaps included. Arrows, stars and ticks without U+FE0F are text glyphs.
_EMOJI_BMP = ("\u231a\u231b\u23e9-\u23ec\u23f0\u23f3\u25fd\u25fe\u2614\u2615\u2648-\u2653\u267f\u2693\u26a1"
              "\u26aa\u26ab\u26bd\u26be\u26c4\u26c5\u26ce\u26d4\u26ea\u26f2\u26f3\u26f5\u26fa\u26fd\u2705"
              "\u270a\u270b\u2728\u274c\u274e\u2753-\u2755\u2757\u2795-\u2797\u27b0\u27bf\u2b1b\u2b1c\u2b50"
              "\u2b55")
EMOJI = re.compile(
    "(?:(?:[\U0001F300-\U0001FAFF\U0001F1E6-\U0001F1FF" + _EMOJI_BMP + "]"
    "|[#*0-9]\ufe0f?\u20e3"
    "|[\u00a9\u00ae\u203c\u2049\u2122\u2139\u2190-\u2bff\u3030\u303d\u3297\u3299]\ufe0f)"
    "\ufe0f?[\U000E0020-\U000E007F]*|\u200d)+"
)
EM_DASH = "—"

# S12-S18 patterns.
BG_CLIP_TEXT = re.compile(r"(?<![\w-])(?:-webkit-)?background-clip\s*:\s*text\b", re.IGNORECASE)
BACKDROP_CLASS = re.compile(r"(?<![\w-])backdrop-blur(?:-[\w\[\]./%-]+)?(?![\w-])")
BACKDROP_DECL = re.compile(r"(?<![\w-])(?:-webkit-)?backdrop-filter\s*:\s*[^;}\n]*blur\(", re.IGNORECASE)
# Loops and state animations; a class behind a variant prefix (data-[open]:animate-x) marks a state change.
STATIC_ANIMATIONS = ("spin", "ping", "pulse", "bounce", "marquee", "none")
ENTRANCE_CLASS = re.compile(r"(?<![\w:-])animate-([\w\[\]./-]+)")
PULSE_CLASS = re.compile(r"(?<![\w-])animate-(?:pulse|ping)(?![\w-])")
PULSE_TEXT = re.compile(r"\s*(?:new|live|新着)\s*</", re.IGNORECASE)
AOS_ATTR = re.compile(r"""\bdata-aos\s*=\s*["']([^"']*)["']""")
INITIAL_HIDDEN = re.compile(r"\binitial\s*=\s*\{\{[^}]*\bopacity\s*:\s*0\b")
TRACKING_ARBITRARY = re.compile(r"(?<![\w-])tracking-\[([\d.]+)(em|px|rem)\]")
UPPERCASE_DECL = re.compile(r"text-transform\s*:\s*uppercase", re.IGNORECASE)
LETTER_SPACING_DECL = re.compile(r"letter-spacing\s*:\s*([\d.]+)(em|px|rem)", re.IGNORECASE)
EYEBROW_EM = 0.05
EYEBROW_NEXT = {"h1", "h2", "h3"}
ARROW_LINK = re.compile(r"<(?:a|button|Link|Button)\b([^>]*)>([^<>{}]*?)(\u2192|\u2197|\u203a|\u00bb|->)\s*</")
HIDDEN_CLASS = re.compile(r"sr-only|visually-hidden", re.IGNORECASE)
HEAD_BLOCK = re.compile(r"<(title|head|script|style)\b.*?</\1\s*>", re.DOTALL | re.IGNORECASE)
DOT_JOINED = re.compile(r">[^<>{}]*\u00b7[^<>{}]*\u00b7[^<>{}]*<")
MAP_RENDERS = re.compile(
    r"\.map\(\s*(?:async\s*)?(?:\([^()]*\)|\w+)\s*=>\s*(?:\(\s*|\{[^{}]{0,200}?return\s*\(?\s*)?<[A-Za-z>]")
FETCH_CALL = re.compile(r"\bfetch\(|\buseQuery\b|\buseSWR\b|\baxios\b")
EMPTY_BRANCH = re.compile(
    r"\.length\s*===?\s*0|!\s*[\w.?\[\]]+\.length\b|\.length\s*\?|\bisEmpty\b|\bEmpty(?:[A-Z]\w*)?\b")
LOADING_BRANCH = re.compile(
    r"\b(?:loading(?!\s*=\s*[\"'])|sending|submitting|saving|pending|isLoading|isPending|isSubmitting|isFetching"
    r"|Skeleton|Spinner|Suspense)\b")
CONST_ARRAY = r"\bconst\s+{name}\s*(?::[^=;]+)?=\s*(?:\[|Array\.from\(\s*\{{\s*length\b)"
ERROR_BRANCH = re.compile(r"\b(?:error|isError|ErrorBoundary|catch)\b")
IMPORT_STMT = re.compile(r"(?ms)^[ \t]*import\b.*?[\"'][^\"'\n]+[\"'][ \t]*;?")
CSS_MEMBER = re.compile(r"\b(?:styles|classes|css|cls)\.\w+")
SHORT_STRING = re.compile(r"\"[^\"\n]*\"|'[^'\n]*'")
TEMPLATE_STRING = re.compile(r"`[^`]*`")
TOAST_HANDLER = re.compile(
    r"\bon(?:Click|Select|Submit)\s*=\s*\{\s*(?:async\s*)?(?:\([^()]*\)|\w+)\s*=>\s*(\{\s*)?"
    r"(?:toast(?:\.(?:success|error|info|warning|message))?|alert)\s*\(")

FORM_TAG = re.compile(r"<form\b", re.IGNORECASE)
FORM_LIB = re.compile(r"\b(?:useForm|react-hook-form|Formik|zodResolver)\b")
STATE_SIGNALS = (
    "required", "aria-required", "aria-invalid", "aria-describedby",
    "pattern=", 'role="alert"', "role='alert'", "errors.", "errorMessage",
    "helperText", "FormMessage",
)
# S10 - a form that holds an entry field a reader fills in, and is no search, filter or lookup.
FORM_END = re.compile(r"</form\s*>|<form\b", re.IGNORECASE)
ENTRY_INPUT = re.compile(r"""<input\b[^>]*?\btype\s*=\s*["']?(?:email|password|tel|url|file)\b""", re.IGNORECASE)
ENTRY_TEXTAREA = re.compile(r"<textarea\b", re.IGNORECASE)
FIELD_TAG = re.compile(r"<(?:input|textarea|select)\b[^>]*>", re.IGNORECASE)
FORM_SEARCH_ROLE = re.compile(r"""(?<![\w-])role\s*=\s*["']?search\b""", re.IGNORECASE)
FORM_VALUE_ATTR = re.compile(
    r"""(?<![\w-])(?:action|id|class(?:Name)?)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", re.IGNORECASE)
FORM_SEARCH_WORDS = {"search", "filter", "sort", "lookup", "track"}
SEARCH_FIELD = re.compile(r"""\btype\s*=\s*["']?search\b|\bname\s*=\s*["']?(?:q|query|keyword|kw|search)\b""", re.IGNORECASE)
# S11 - a card element opening inside another card element.
TAG_OPEN = re.compile(r"<(/?)([A-Za-z][\w.:-]*)")
RAW_BLOCK = re.compile(r"<(script|style|pre)\b.*?</\1\s*>", re.DOTALL | re.IGNORECASE)
CLASS_ATTR = re.compile(r"(?<![\w:-])(?:class|className)\s*=\s*")
STRING_LITERAL = re.compile(r"\"([^\"]*)\"|'([^']*)'|`([^`]*)`")
CARD_TOKEN = re.compile(r"(?:^|[-_])(?:card|panel)$")
# A colour utility on the card colour (bg-card, hover:border-card) paints an element and draws no card.
CARD_UTILITY = re.compile(r"^(?:[\w\[\]=&.-]+:)*(?:bg|text|border|ring|outline|fill|stroke|from|via|to|divide|decoration|placeholder|caret|accent|shadow)-(?:card|panel)$")
CARD_STEM_EXCLUDED = ("tab", "tabs", "dropdown", "menu", "nav", "popover", "tooltip", "flyout", "drawer")
ROLE_DIALOG = re.compile(r"""(?<![\w:-])role\s*=\s*["']dialog["']""")
VOID_TAGS = {"img", "br", "hr", "input", "meta", "link", "source", "track", "wbr",
             "area", "base", "col", "embed", "param"}


SUPPRESS = re.compile(r"product-ui:\s*ignore(?P<file>-file)?\s+(?P<id>[SC]\d+)(?P<rest>[^\n]*)")
RUN_WIDE = {"S4", "S5", "S6", "S7"}


def parse_suppressions(text):
    """Return (by_line, by_file, bare): line->ids, ids, and lines of reason-less forms."""
    by_line, by_file, bare = {}, set(), []
    for match in SUPPRESS.finditer(text):
        line = line_of(text, match.start())
        reason = re.sub(r"(\*/\}?|-->)\s*$", "", match.group("rest")).strip()
        if not reason:
            bare.append(line)
            continue
        check_id = match.group("id")
        if match.group("file"):
            by_file.add(check_id)
        else:
            by_line.setdefault(line, set()).add(check_id)
            by_line.setdefault(line + 1, set()).add(check_id)
    return by_line, by_file, bare


class Report:
    def __init__(self):
        self.findings = []
        self.by_line = {}
        self.by_file = set()
        self.run_ids = set()

    def begin_file(self, text, path):
        self.by_line, self.by_file, bare = parse_suppressions(text)
        self.run_ids |= self.by_file & RUN_WIDE
        for line in bare:
            self.findings.append({"severity": "WARN", "id": "S0", "file": path, "line": line,
                                  "message": "suppression carries no reason, so it suppresses nothing"})

    def add(self, severity, check_id, path, line, message):
        """Record a finding; False when a suppression silenced it."""
        if path == "(project)":
            if check_id in self.run_ids:
                return False
        elif check_id in self.by_file or check_id in self.by_line.get(line, ()):
            return False
        self.findings.append({
            "severity": severity,
            "id": check_id,
            "file": path,
            "line": line,
            "message": message,
        })
        return True

    @property
    def errors(self):
        return [f for f in self.findings if f["severity"] == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f["severity"] == "WARN"]


def strip_comments(text):
    """Blank out comment bodies, keeping newlines so line numbers stay put."""
    def blank(match):
        return re.sub(r"[^\n]", " ", match.group(0))

    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.DOTALL)
    text = re.sub(r"(?m)(?<![:\w])//[^\n]*", blank, text)
    return text


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def safe_float(text):
    """float(text), or None for a malformed number such as "." or "1.2.3"."""
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def collect_files(roots):
    found = set()
    for root in roots:
        if os.path.isfile(root):
            found.add(root)
            continue
        for base, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in names:
                if not name.endswith(SCOPE_SUFFIXES):
                    continue
                if name in SKIP_NAMES or any(p in name for p in SKIP_PATTERNS):
                    continue
                found.add(os.path.join(base, name))
    return sorted(found)


def find_theme(roots):
    """theme.css beneath the paths, then up to four directories above them."""
    start = os.path.commonpath([os.path.abspath(r) for r in roots])
    if os.path.isfile(start):
        start = os.path.dirname(start)
    for base, dirs, names in os.walk(start):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in SKIP_NAMES:
            if name in names:
                return os.path.join(base, name)
    base = start
    for _ in range(4):
        base = os.path.dirname(base)
        if not base or base == os.path.dirname(base):
            break
        for name in SKIP_NAMES:
            candidate = os.path.join(base, name)
            if os.path.isfile(candidate):
                return candidate
    return None


def theme_colors(theme_path):
    """Every colour literal the theme declares. Anything else is off-token."""
    known = set()
    for text in theme_texts(theme_path):
        for pattern in (HEX, FUNC_COLOR, MODERN_COLOR):
            for match in pattern.finditer(text):
                known.add(normalize_color(match.group(0)))
    return known


def theme_texts(theme_path):
    """The text of the theme and of the local stylesheets it imports, nested; both theme readers share this set."""
    seen, queue = set(), [theme_path]
    while queue:
        path = queue.pop()
        if not path or not os.path.isfile(path) or os.path.abspath(path) in seen:
            continue
        seen.add(os.path.abspath(path))
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        yield text
        queue += [resolve_import(path, spec) for spec in CSS_IMPORT.findall(text)]


def theme_color_names(theme_path):
    """The <family>-<step> names the theme defines as --color-<family>-<step>."""
    names = set()
    for text in theme_texts(theme_path):
        names.update(THEME_COLOR_NAME.findall(text))
    return names


def resolve_import(from_path, spec):
    """The local stylesheet an @import names, or None: a relative path, or a package path under the nearest node_modules.

    Tailwind's own stylesheets define its default palette, so they are left out.
    """
    if spec.startswith(("http:", "https:", "//", "tailwindcss")):
        return None
    base = os.path.dirname(os.path.abspath(from_path))
    candidates = [os.path.normpath(os.path.join(base, spec))]   # a bare name is first a sibling file
    if not spec.startswith((".", "/")):
        while True:
            candidates.append(os.path.join(base, "node_modules", spec))
            if os.path.isdir(os.path.join(base, "node_modules")) or os.path.dirname(base) == base:
                break
            base = os.path.dirname(base)
    for candidate in candidates:
        for option in (candidate, candidate + ".css", exported_file(candidate)):
            if option and os.path.isfile(option):
                return option
    return None


def exported_file(candidate):
    """The file a package's package.json "exports" names for the subpath of <node_modules>/<name>/<subpath>, or None."""
    head, _, rest = candidate.replace("\\", "/").rpartition("/node_modules/")
    if not rest:
        return None
    parts = rest.split("/")
    size = 2 if rest.startswith("@") else 1
    root = os.path.join(head, "node_modules", *parts[:size])
    try:
        with open(os.path.join(root, "package.json"), encoding="utf-8") as handle:
            exports = json.load(handle).get("exports")
    except (OSError, ValueError):
        return None
    sub = "/".join(parts[size:])
    target = exports.get("./" + sub if sub else ".") if isinstance(exports, dict) else None
    if isinstance(target, dict):
        target = target.get("style") or target.get("default")
    return os.path.normpath(os.path.join(root, target)) if isinstance(target, str) else None


def normalize_color(value):
    return re.sub(r"\s+", "", value).lower()


def check_file(path, text, known_colors, rep, totals):
    rep.begin_file(text, path)
    body = strip_comments(text)
    rel = path

    # S1 - Tailwind default palette classes the theme does not define.
    for match in PALETTE_CLASS.finditer(body):
        name = f"{match.group(1)}-{match.group(2)}"
        if name not in totals["theme_names"]:
            rep.add("ERROR", "S1", rel, line_of(body, match.start()),
                    f"{match.group(0)} is a Tailwind default palette class; use a token utility "
                    f"or define --color-{name} in the theme")

    # S1 / S5 - colour literals outside the token set.
    selector_spans = [m.span() for m in ATTRIBUTE_SELECTOR.finditer(body)]
    style_spans = [m.span() for m in STYLE_BLOCK.finditer(body)]
    for pattern in (HEX, FUNC_COLOR, MODERN_COLOR):
        for match in pattern.finditer(body):
            raw = match.group(0)
            if any(a <= match.start() < b for a, b in selector_spans):
                continue
            if pattern is HEX and is_fragment_reference(body, match.start()):
                continue
            if pattern is HEX and not path.endswith(".css") and in_element_text(body, match.start(), style_spans):
                continue
            if pattern is MODERN_COLOR:
                raw = raw.replace("_", " ")  # Tailwind writes spaces inside [...] as underscores
                if TOKEN_COLOR.search(raw) or ACHROMATIC_SHADOW.fullmatch(raw):
                    continue
            norm = normalize_color(raw)
            if norm in known_colors:
                continue
            totals["off_token_colors"].add(norm)
            rep.add("ERROR", "S1", rel, line_of(body, match.start()),
                    f"{raw} is not declared in the theme; use a token variable")

    # S2 / S4 - font families.
    faces_blanked = FONT_FACE_BLOCK.sub(lambda m: blank(m.group(0)), body)  # a declared face is no usage
    for match in FONT_FAMILY.finditer(faces_blanked):
        stack = [part.strip().strip("'\"") for part in match.group(1).split(",")]
        if not stack:
            continue
        leading = stack[0].strip().strip("'\"")
        record_family(leading, rel, line_of(body, match.start()), rep, totals)
    for match in FONT_ARBITRARY.finditer(body):
        leading = match.group(1).replace("_", " ").split(",")[0].strip().strip("'\"")
        if leading.isdigit():
            continue  # font-[600] sets the weight
        record_family(leading, rel, line_of(body, match.start()), rep, totals)

    # S3 - blue-to-purple gradients.
    unused = unused_style_spans(body, path)
    for match in GRADIENT_CALL.finditer(body):
        end = balanced_end(body, match.end() - 1)
        if end > 0 and gradient_is_blue_purple(body[match.start():end]):
            if any(a <= match.start() < b for a, b in unused):
                continue
            rep.add("ERROR", "S3", rel, line_of(body, match.start()),
                    "gradient runs from a purple family to a blue or pink family")
    for start, attrs in gradient_class_groups(body):
        stops = {m.group(1).lower() for m in TW_GRADIENT_STOP.finditer(attrs)}
        if stops & PURPLE_WORDS and stops & (BLUE_WORDS | PINK_WORDS):
            rep.add("ERROR", "S3", rel, line_of(body, start),
                    "gradient utility classes mix a purple family with a blue or pink family")
        elif TW_FROM_PURPLE.search(attrs) and TW_TO_PURPLE.search(attrs):
            rep.add("ERROR", "S3", rel, line_of(body, start),
                    "gradient utility classes run from a purple, violet or indigo stop")

    # S6 - radius values.
    for match in RADIUS_DECL.finditer(body):
        for value in match.group(1).split():
            norm = value.strip().lower()
            if norm not in NEUTRAL_RADII:
                totals["radii"].setdefault(norm, 0)
                totals["radii"][norm] += 1
    for match in TW_ROUNDED.finditer(body):
        norm = match.group(1).strip().lower()
        if norm not in NEUTRAL_RADII:
            totals["radii"].setdefault(norm, 0)
            totals["radii"][norm] += 1

    # S7 - shadow alpha.
    for match in SHADOW_DECL.finditer(body):
        for color in SHADOW_COLOR.finditer(match.group(1)):
            value = color_alpha(color.group(1))
            if value is not None:
                totals["shadow_alphas"][value] = totals["shadow_alphas"].get(value, 0) + 1

    # S8 - emoji standing in for icons.
    for match in re.finditer(r"<([A-Za-z][\w.:-]*)\b[^>]*>\s*(" + EMOJI.pattern + r")\s*</\1\s*>", body):
        if not spans_aria_hidden(body, match):
            rep.add("WARN", "S8", rel, line_of(body, match.start(2)),
                    f"{match.group(2)} sits alone in an element; use an icon from a set")
    for match in re.finditer(r"<(li|button|a|h[1-6])\b[^>]*>\s*(" + EMOJI.pattern + r")", body):
        if not spans_aria_hidden(body, match):
            rep.add("WARN", "S8", rel, line_of(body, match.start(2)),
                    f"{match.group(2)} leads the content of a <{match.group(1)}>; use an icon from a set")

    # S9 - em-dashes in visible text.
    visible = re.sub(r"<(code|pre|script|style)\b.*?</\1\s*>", " ", body, flags=re.DOTALL | re.IGNORECASE)
    for tag in reversed(list(TAG_OPEN.finditer(visible))):
        if not tag.group(1):
            parsed = read_tag(visible, tag.end())
            if parsed:
                visible = visible[:tag.end()] + " " + visible[parsed[0]:]
    count = visible.count(EM_DASH)
    if count >= 3:
        rep.add("WARN", "S9", rel, 1, f"{count} em-dashes in visible text")

    # S10 - forms without state design.
    form = FORM_LIB.search(body)
    form_at = form.start() if form else entry_form(body)
    if form_at is not None and not any(sig in body for sig in STATE_SIGNALS):
        rep.add("ERROR", "S10", rel, line_of(body, form_at),
                "form has no validation, error state or required marking")

    check_template_tells(path, body, rep)
    check_generated_tells(path, body, rep, totals)

    # S11 - a card element inside a card element.
    if not path.endswith(".css"):
        markup = RAW_BLOCK.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), body)
        for index, name, exact in nested_cards(markup, path):
            rep.add("ERROR" if exact else "WARN", "S11", rel, line_of(markup, index),
                    f"<{name}> opens inside another card; a box in a box asserts a second "
                    "grouping around the same content, so drop the inner enclosure")


def blank(text):
    return re.sub(r"[^\n]", " ", text)


def unused_style_spans(body, path):
    """(open, close) offsets of each rule in a markup file's <style> blocks whose class selectors match no class of the file."""
    if path.endswith(".css"):
        return []
    styles = [m.span() for m in STYLE_BLOCK.finditer(body)]
    if not styles:
        return []
    outside = body
    for a, b in styles:
        outside = outside[:a] + blank(outside[a:b]) + outside[b:]
    used = set(re.findall(r"[\w-]+", outside))   # a bound class (:class, class:, classList) names the class outside a class attribute
    spans = []
    for before, start, end in innermost_blocks(body):
        if not any(a <= start < b for a, b in styles):
            continue
        classes = CLASS_SELECTOR.findall(body[before + 1:start])
        if classes and not used.intersection(classes):
            spans.append((start, end))
    return spans


def balanced_end(text, open_index):
    """Index just after the parenthesis that closes text[open_index], or -1."""
    depth, quote, skip = 0, None, False
    for i in range(open_index, len(text)):
        ch = text[i]
        if skip:
            skip = False
        elif quote:
            if ch == "\\":
                skip = True
            elif ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    return -1


BRACES = re.compile(r"[{}]")


def innermost_blocks(text):
    """(index of the brace before the open one or -1, open index, close index) of each { } pair that holds no brace."""
    out, before_open, last_char, last_pos = [], -1, None, -1
    for match in BRACES.finditer(text):
        char, pos = match.group(0), match.start()
        if char == "}" and last_char == "{":
            out.append((before_open, last_pos, pos))
        before_open, last_char, last_pos = last_pos, char, pos
    return out


def open_tags(body):
    """Yield (offset, tag name, attribute text) for each opening tag and each @apply line."""
    for tag in TAG_OPEN.finditer(body):
        parsed = None if tag.group(1) else read_tag(body, tag.end())
        if parsed:
            yield tag.start(), tag.group(2), parsed[1]
    for apply in re.finditer(r"@apply\b[^;}]*", body):
        yield apply.start(), "@apply", apply.group(0)


def state_view(text):
    """Code with imports, string contents and CSS-module members blanked.

    Offsets and newlines stay put. An identifier that survives is code, so a class named
    "error" in a string or an imported type named error does not count as a state branch.
    """
    text = IMPORT_STMT.sub(lambda m: blank(m.group(0)), text)
    text = CSS_MEMBER.sub(lambda m: blank(m.group(0)), text)

    def template(match):
        raw, out, last = match.group(0), [], 0
        for hole in re.finditer(r"\$\{[^}]*\}", raw):
            out += [blank(raw[last:hole.start()]), hole.group(0)]
            last = hole.end()
        return "".join(out) + blank(raw[last:])

    text = TEMPLATE_STRING.sub(template, text)
    return SHORT_STRING.sub(lambda m: m.group(0)[0] + blank(m.group(0)[1:-1]) + m.group(0)[-1], text)


def has_token(attrs, name):
    return bool(re.search(r"(?<![\w-])" + name + r"(?![\w-])", attrs))


def constant_array_receiver(code, dot):
    """True when the receiver of the .map( at dot is a constant: a name in capitals, or one bound in the file with const to an array literal or to Array.from({ length })."""
    before = code[max(0, dot - 80):dot]
    # A name in capitals is a constant by convention, imported ones included: STATUSES.map, Object.entries(LABELS).map.
    if re.search(r"(?:\bObject\.(?:entries|values|keys)\(\s*)?(?<![\w$.])[A-Z][A-Z0-9_]+\s*\)?\??$", before):
        return True
    found = re.search(r"([\w$]+)\??$", before)
    return bool(found) and bool(re.search(CONST_ARRAY.format(name=re.escape(found.group(1))), code))


def skip_link(attrs, text):
    """True for a skip link (href="#..." and text starting with Skip) and for visually hidden text."""
    if HIDDEN_CLASS.search(attrs):
        return True
    return bool(re.search(r"""(?<![\w-])href\s*=\s*["']#""", attrs)) and text.strip().lower().startswith("skip")


def next_sibling_tag(body, offset, name):
    """Lower-cased name of the opening tag that follows the element opened at offset, or None."""
    parsed = read_tag(body, offset + 1 + len(name))
    if not parsed or parsed[2] or name in VOID_TAGS:
        return None
    depth, pos = 1, parsed[0]
    while depth:
        tag = TAG_OPEN.search(body, pos)
        if not tag:
            return None
        end = body.find(">", tag.end())
        pos = len(body) if end < 0 else end + 1
        if tag.group(2) != name:
            continue
        if tag.group(1):
            depth -= 1
        else:
            opened = read_tag(body, tag.end())
            if opened:
                pos = opened[0]
                depth += 0 if opened[2] else 1
    following = TAG_OPEN.search(body, pos)
    if not following or following.group(1):
        return None
    return following.group(2).lower()


def tracking_em(text, size):
    """Letter-spacing in em that Tailwind tracking classes or style declarations set, the largest of them, or 0."""
    values = [0.05 if m.group(0).endswith("wider") else 0.1
              for m in re.finditer(r"(?<![\w-])tracking-(?:wider|widest)(?![\w-])", text)]
    for pattern in (TRACKING_ARBITRARY, LETTER_SPACING_DECL):
        for m in pattern.finditer(text):
            number = safe_float(m.group(1))
            if number is not None:
                values.append(number / (size or 16) if m.group(2).lower() == "px" else number)
    return max(values, default=0)


def eyebrow_offsets(body, tags):
    """Offsets of the elements that are uppercase, track 0.05em or more and sit before an h1, h2 or h3.

    Uppercase and tracking come from the element's classes, its style attribute and the rules of
    the file whose class selectors it carries.
    """
    rules = {}  # class -> [uppercase, tracking em]
    for before, start, end in innermost_blocks(body):
        declarations = body[start + 1:end]
        if "letter-spacing" not in declarations and "text-transform" not in declarations:
            continue
        upper, em = bool(UPPERCASE_DECL.search(declarations)), tracking_em(declarations, None)
        if upper or em:
            for cls in CLASS_SELECTOR.findall(body[before + 1:start]):
                entry = rules.setdefault(cls, [False, 0])
                entry[0], entry[1] = entry[0] or upper, max(entry[1], em)
    found = []
    for offset, name, attrs in tags:
        if name == "@apply":
            continue
        upper = has_token(attrs, "uppercase") or bool(UPPERCASE_DECL.search(attrs))
        em = tracking_em(attrs, tag_font_px(attrs))
        for cls in class_tokens(attrs):
            if cls in rules:
                upper, em = upper or rules[cls][0], max(em, rules[cls][1])
        if upper and em >= EYEBROW_EM and next_sibling_tag(body, offset, name) in EYEBROW_NEXT:
            found.append(offset)
    return found


def check_template_tells(path, body, rep):
    """S12-S16 and S18 (warnings) and S17 (error): default-looking effects and controls that do nothing."""
    rel = path
    tags = list(open_tags(body))

    # S12 - gradient text.
    for offset, _, attrs in tags:
        if has_token(attrs, "bg-clip-text") and has_token(attrs, "text-transparent"):
            rep.add("WARN", "S12", rel, line_of(body, offset),
                    "gradient text (bg-clip-text with text-transparent); set the text in a plain colour")
    # The -webkit- form and the standard one usually sit together: one finding per line.
    for line in sorted({line_of(body, match.start()) for match in BG_CLIP_TEXT.finditer(body)}):
        rep.add("WARN", "S12", rel, line,
                "background-clip: text paints gradient text; set the text in a plain colour")

    # S13 - glass, except a full-viewport overlay.
    for offset, name, attrs in tags:
        overlay = name.endswith("Overlay") or (has_token(attrs, "fixed") and has_token(attrs, "inset-0"))
        if BACKDROP_CLASS.search(attrs) and not overlay:
            rep.add("WARN", "S13", rel, line_of(body, offset),
                    "backdrop blur on content; a blurred translucent panel is glass, so use a solid surface")
    glass_lines = set()
    for match in BACKDROP_DECL.finditer(body):
        start = body.rfind("{", 0, match.start()) + 1
        end = body.find("}", match.end())
        block = body[start:len(body) if end < 0 else end]
        selector = body[body.rfind("}", 0, max(start - 1, 0)) + 1:max(start - 1, 0)]
        covers_viewport = re.search(r"position\s*:\s*fixed", block) and re.search(r"inset\s*:\s*0\b", block)
        line = line_of(body, match.start())
        if "overlay" in selector.lower() or covers_viewport or line in glass_lines:
            continue
        glass_lines.add(line)
        rep.add("WARN", "S13", rel, line,
                "backdrop-filter blur on content; a blurred translucent panel is glass, so use a solid surface")

    # S14 - one entrance animation repeated.
    entrances = {}
    for offset, _, attrs in tags:
        keys = {"animate-" + m.group(1) for m in ENTRANCE_CLASS.finditer(attrs)
                if not m.group(1).lstrip("[").startswith(STATIC_ANIMATIONS)
                and not ("infinite" in m.group(1) and m.group(1).startswith("["))}
        keys |= {"data-aos " + m.group(1) for m in AOS_ATTR.finditer(attrs)}
        if "whileInView" in attrs:
            keys.add("whileInView")
        if INITIAL_HIDDEN.search(attrs):
            keys.add("initial opacity 0")
        for key in keys:
            entrances.setdefault(key, []).append(offset)
    for key, offsets in entrances.items():
        if len(offsets) >= 3:
            rep.add("WARN", "S14", rel, line_of(body, offsets[0]),
                    f"the same entrance animation ({key}) on {len(offsets)} elements; animate what changes state")

    # S15 - template chrome.
    chrome = eyebrow_offsets(body, tags)
    if len(chrome) >= 2:
        rep.add("WARN", "S15", rel, line_of(body, min(chrome)),
                f"{len(chrome)} spaced uppercase labels above a heading; the small uppercase eyebrow is template chrome")
    for match in ARROW_LINK.finditer(body):
        if skip_link(match.group(1), match.group(2)):
            continue
        rep.add("WARN", "S15", rel, line_of(body, match.start(3)),
                f"link or button text ends in {match.group(3)}; the label alone names the action")
    visible = HEAD_BLOCK.sub(lambda m: blank(m.group(0)), body)
    for tag, parsed in [(t, read_tag(visible, t.end())) for t in TAG_OPEN.finditer(visible) if not t.group(1)]:
        if parsed:
            visible = visible[:tag.end()] + blank(visible[tag.end():parsed[0] - 1]) + visible[parsed[0] - 1:]
    for match in DOT_JOINED.finditer(visible):
        rep.add("WARN", "S15", rel, line_of(body, match.start() + 1),
                "text joins three or more parts with a middle dot; use a list or separate elements")

    # S16 - empty, loading and error states.
    if path.endswith((".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro")):
        code = state_view(body)
        listing = next((m for m in MAP_RENDERS.finditer(code) if not constant_array_receiver(code, m.start())), None)
        if listing and not EMPTY_BRANCH.search(code):
            rep.add("WARN", "S16", rel, line_of(code, listing.start()),
                    "the file renders a collection and has no empty state")
        fetching = FETCH_CALL.search(code)
        if fetching:
            for pattern, state in ((LOADING_BRANCH, "loading"), (ERROR_BRANCH, "error")):
                if not pattern.search(code):
                    rep.add("WARN", "S16", rel, line_of(code, fetching.start()),
                            f"the file fetches data and has no {state} state")

    # S18 - a pulsing badge whose whole text is New, Live or 新着.
    for offset, name, attrs in tags:
        if name == "@apply" or not PULSE_CLASS.search(attrs):
            continue
        parsed = read_tag(body, offset + 1 + len(name))
        if parsed and not parsed[2] and PULSE_TEXT.match(body, parsed[0]):
            rep.add("WARN", "S18", rel, line_of(body, offset),
                    "a pulsing New or Live badge; name the state or the action, or drop the badge")

    # S17 - a handler whose whole body is a toast or alert.
    for match in TOAST_HANDLER.finditer(body):
        end = balanced_end(body, match.end() - 1)
        tail = r"\s*;?\s*\}\s*\}" if match.group(1) else r"\s*\}"
        if end > 0 and re.match(tail, body[end:]):
            rep.add("ERROR", "S17", rel, line_of(body, match.start()),
                    "the handler only shows a toast or alert, so the control reports an effect it does not have; "
                    "do the work, or show the control disabled or leave it out")


def read_tag(text, start):
    """From just after a tag name: (end, attrs, self_closing), or None when the tag never closes."""
    depth, quote = 0, None
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        elif ch == ">" and depth == 0:
            return i + 1, text[start:i], text[i - 1] == "/"
    return None


def class_tokens(attrs):
    """Tokens of a class/className attribute; a {...} expression yields its string literals only."""
    found = CLASS_ATTR.search(attrs)
    if not found:
        return []
    rest = attrs[found.end():]
    if rest[:1] in ("\"", "'"):
        close = rest.find(rest[0], 1)
        return rest[1:close if close > 0 else len(rest)].split()
    if rest[:1] == "{":
        depth, end = 0, len(rest)
        for i, ch in enumerate(rest):
            depth += (ch == "{") - (ch == "}")
            if depth == 0:
                end = i
                break
        return [token for m in STRING_LITERAL.finditer(rest[:end])
                for token in next(g for g in m.groups() if g is not None).split()]
    return rest.split()[:1]


def search_form_attrs(attrs):
    """True when the form tag has role=search, or an action, id or class value that holds a search word as a whole token."""
    if FORM_SEARCH_ROLE.search(attrs):
        return True
    for m in FORM_VALUE_ATTR.finditer(attrs):
        value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", next(g for g in m.groups() if g is not None))
        if FORM_SEARCH_WORDS & set(re.split(r"[\s_/-]+", value.lower())):
            return True
    return False


def entry_form(body):
    """Offset of the first <form> that holds an entry field and is no search, filter or lookup, else None.

    An entry field is an email, password, tel, url or file input, or a textarea. A form that holds
    one visible field, an email input, is a subscription and passes.
    """
    for form in FORM_TAG.finditer(body):
        parsed = read_tag(body, form.end())
        if not parsed:
            continue
        end = FORM_END.search(body, parsed[0])
        inner = body[parsed[0]:end.start() if end else len(body)]
        if search_form_attrs(parsed[1]) or SEARCH_FIELD.search(inner):
            continue
        if not (ENTRY_INPUT.search(inner) or ENTRY_TEXTAREA.search(inner)):
            continue
        fields = [f for f in FIELD_TAG.findall(inner)
                  if not re.search(r"""type\s*=\s*["']?(?:hidden|submit|button|image|reset)""", f, re.IGNORECASE)]
        if len(fields) == 1 and re.search(r"""type\s*=\s*["']?email""", fields[0], re.IGNORECASE):
            continue
        return form.start()
    return None


def card_kind(name, attrs):
    """None for an element that is no card, "Card" for <Card>, "card" for an exact card token, else "suffix"."""
    if name == "Card":
        return "Card"
    kind = None
    for token in class_tokens(attrs):
        found = CARD_TOKEN.search(token)
        if not found or "--" in token or CARD_UTILITY.match(token):
            continue
        if token[:found.start()].lower().endswith(CARD_STEM_EXCLUDED):
            continue
        if token == "card":
            return "card"
        kind = "suffix"
    return kind


def is_hidden(attrs):
    """True for a tag that carries role="tabpanel", hidden or aria-hidden="true"."""
    if re.search(r"""(?<![\w:-])role\s*=\s*["']tabpanel["']""", attrs):
        return True
    aria = re.search(r"""(?<![\w:-])aria-hidden(?:\s*=\s*("[^"]*"|'[^']*'|\{[^{}]*\}))?""", attrs)
    if aria and (aria.group(1) is None or "true" in aria.group(1)):
        return True
    bare = re.sub(r"\"[^\"]*\"|'[^']*'", '""', attrs)
    return bool(re.search(r"(?<![\w:@.-])hidden(?![\w-])(?!\s*=\s*\{)", bare))


def nested_cards(markup, path):
    """Yield (offset, tag name, is_error) of each card element that opens while another card is open.

    A dialog is its own surface: the search for an enclosing card stops at one, and a
    card that is itself a dialog is never nested. A tab panel, a hidden element and what it
    holds are no cards. The pair is an error when both are <Card>, or both hold the exact token card.
    """
    stack, pos = [], 0  # entries: (tag name, card kind, is_dialog, is_hidden)
    generics = path.endswith((".tsx", ".jsx"))  # useState<Card>( holds a type argument, not a tag
    while True:
        tag = TAG_OPEN.search(markup, pos)
        if not tag:
            return
        closing, name = tag.group(1), tag.group(2)
        if closing:
            end = markup.find(">", tag.end())
            pos = len(markup) if end < 0 else end + 1
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
            continue
        before = markup[tag.start() - 1] if tag.start() else " "
        if generics and (before.isalnum() or before in "_)]"):
            pos = tag.end()
            continue
        parsed = read_tag(markup, tag.end())
        if not parsed:
            return
        pos, attrs, self_closing = parsed
        is_dialog = name == "dialog" or bool(ROLE_DIALOG.search(attrs))
        hidden = is_hidden(attrs) or bool(stack and stack[-1][3])
        kind = None if hidden else card_kind(name, attrs)
        if kind and not is_dialog:
            for _, enclosing_kind, enclosing_dialog, _ in reversed(stack):
                if enclosing_dialog:
                    break
                if enclosing_kind:
                    yield tag.start(), name, kind == enclosing_kind and kind != "suffix"
                    break
        if not self_closing and name not in VOID_TAGS:
            stack.append((name, kind, is_dialog, hidden))


def in_element_text(text, index, style_spans):
    """True when index sits in the text between a tag's closing > and the next <, outside <style> blocks (`#1284` is no colour there)."""
    if any(a <= index < b for a, b in style_spans):
        return False
    gt, lt = text.rfind(">", 0, index), text.rfind("<", 0, index)
    return gt > lt and text[gt - 1] != "=" and not re.search(r"[;=()<>]", text[gt + 1:index])


def is_fragment_reference(text, index):
    """True for href="#id" and the like, where # opens a fragment reference."""
    window = text[max(0, index - 300):index]
    return bool(re.search(
        r"(?:(?:href|src|id|xlink:href|action)\s*=\s*[\"']?[^\"'\s>]*|url\(\s*[\"']?[^)\"'\s]*)$",
        window, re.IGNORECASE))


def spans_aria_hidden(text, match):
    """True when a line the match touches carries aria-hidden."""
    start = text.rfind("\n", 0, match.start()) + 1
    end = text.find("\n", match.end())
    return "aria-hidden" in text[start:len(text) if end < 0 else end]


def color_alpha(args):
    """Alpha written in the arguments of a colour function, or None when it has none."""
    if "/" in args:
        part = args.split("/", 1)[1]
    else:
        parts = args.split(",")
        if len(parts) < 4:
            return None
        part = parts[3]
    part = part.strip()
    try:
        return round(float(part[:-1]) / 100 if part.endswith("%") else float(part), 4)
    except ValueError:
        return None


def gradient_class_groups(body):
    """Yield (offset, class text) for each opening tag, each @apply line and each string outside a tag."""
    spans = []
    for tag in TAG_OPEN.finditer(body):
        parsed = None if tag.group(1) else read_tag(body, tag.end())
        if parsed:
            spans.append((tag.start(), parsed[0]))
            yield tag.start(), parsed[1]
    for literal in STRING_LITERAL.finditer(body):
        if TW_GRADIENT_STOP.search(literal.group(0)) and not any(a <= literal.start() < b for a, b in spans):
            yield literal.start(), literal.group(0)
    for apply in re.finditer(r"@apply\b[^;}]*", body):
        yield apply.start(), apply.group(0)


def hex_hue(value):
    """OKLCH hue in degrees for a hex colour, or None when its chroma is below MIN_CHROMA."""
    digits = value.lstrip("#")
    if len(digits) in (3, 4):
        digits = "".join(ch * 2 for ch in digits[:3])
    if len(digits) < 6:
        return None
    try:
        _, chroma, hue = hex_to_oklch(digits[:6])
    except ValueError:
        return None
    return None if chroma < MIN_CHROMA else hue


def gradient_is_blue_purple(fragment):
    lowered = fragment.lower()
    purple_word = any(word in lowered for word in PURPLE_WORDS)
    if purple_word and any(word in lowered for word in BLUE_WORDS):
        return True
    if purple_word and re.search(r"\b(?:" + "|".join(PINK_WORDS) + r")\b", lowered):
        return True

    hues = []
    for match in OKLCH_CALL.finditer(fragment):
        parts = re.findall(r"[-+]?\d*\.?\d+", match.group(0))
        if len(parts) >= 3 and float(parts[1]) >= MIN_CHROMA:
            hues.append(float(parts[2]))
    for match in HEX.finditer(fragment):
        hue = hex_hue(match.group(0))
        if hue is not None:
            hues.append(hue)

    return (any(PURPLE_HUES[0] <= h <= PURPLE_HUES[1] for h in hues)
            and any(BLUE_HUES[0] <= h < BLUE_HUES[1] or h > PURPLE_HUES[1] or h < 10 for h in hues))


def record_family(family, path, line, rep, totals):
    lowered = re.sub(r"\s*!important\s*$", "", family.strip().lower()).strip("'\" ")
    lowered = re.sub(r"\s+fallback$", "", lowered)
    if not lowered or lowered.startswith("var(") or lowered in GENERIC_FAMILIES:
        return
    if any(hint in lowered for hint in MONOSPACE_HINTS + ICON_FACE_HINTS) or SCRIPT_FACE.search(lowered):
        return
    totals["families"].add(lowered)
    if lowered in FORBIDDEN_FAMILIES:
        rep.add("WARN", "S2", path, line,
                f"{family!r} leads a font stack; it is what gets picked when no choice is made")


def check_totals(rep, totals):
    if len(totals["off_token_colors"]) > 5:
        rep.add("WARN", "S5", "(project)", 1,
                f"{len(totals['off_token_colors'])} distinct colours outside the token set")

    if len(totals["families"]) >= 3:
        listed = ", ".join(sorted(totals["families"]))
        rep.add("ERROR", "S4", "(project)", 1,
                f"{len(totals['families'])} font families in leading position: {listed}")

    radii = totals["radii"]
    if len(radii) == 1:
        value, count = next(iter(radii.items()))
        if count >= 5:
            rep.add("WARN", "S6", "(project)", 1,
                    f"radius {value} appears {count} times and is the only one in use")

    alphas = totals["shadow_alphas"]
    if len(alphas) == 1:
        value, count = next(iter(alphas.items()))
        if 0.05 <= value <= 0.15 and count >= 3:
            rep.add("WARN", "S7", "(project)", 1,
                    f"every shadow uses alpha {value} across {count} declarations")


# --- S19-S37: generated-UI tells ported from impeccable (Apache-2.0, pbakaus/impeccable @ df3a4abe) ---

NAMED_COLORS = {
    "black": (0, 0, 0, 1), "white": (255, 255, 255, 1), "transparent": (0, 0, 0, 0),
    "gray": (128, 128, 128, 1), "grey": (128, 128, 128, 1), "silver": (192, 192, 192, 1),
    "red": (255, 0, 0, 1), "blue": (0, 0, 255, 1), "green": (0, 128, 0, 1), "lime": (0, 255, 0, 1),
    "yellow": (255, 255, 0, 1), "orange": (255, 165, 0, 1), "purple": (128, 0, 128, 1),
    "magenta": (255, 0, 255, 1), "fuchsia": (255, 0, 255, 1), "cyan": (0, 255, 255, 1),
    "aqua": (0, 255, 255, 1), "pink": (255, 192, 203, 1), "teal": (0, 128, 128, 1),
    "navy": (0, 0, 128, 1), "indigo": (75, 0, 130, 1), "violet": (238, 130, 238, 1),
}
COLOR_TOKEN = re.compile(
    r"\b(?:rgba?|hsla?|oklch)\((?:[^()]|\([^()]*\))*\)|#[0-9a-fA-F]{3,8}\b|(?<![\w-])(?:" + "|".join(NAMED_COLORS) + r")(?![\w-])",
    re.IGNORECASE)
NEUTRAL_KEYWORDS = {"transparent", "currentcolor", "black", "white", "gray", "grey", "silver", "dimgray", "dimgrey",
                    "darkgray", "darkgrey", "lightgray", "lightgrey", "gainsboro", "whitesmoke"}


def _num(token):
    token = token.strip()
    return float(token[:-1]) / 100 if token.endswith("%") else float(token)


def to_rgba(text):
    """(r, g, b, a) with channels 0..255 and alpha 0..1 for a hex, rgb(), hsl(), oklch() or named colour; else None."""
    text = text.strip().lower()
    if text in NAMED_COLORS:
        return NAMED_COLORS[text]
    try:
        if text.startswith("#"):
            digits = text[1:]
            if len(digits) in (3, 4):
                digits = "".join(ch * 2 for ch in digits)
            if len(digits) not in (6, 8):
                return None
            alpha = int(digits[6:], 16) / 255 if len(digits) == 8 else 1.0
            return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16), alpha)
        match = re.match(r"(rgba?|hsla?|oklch)\((.*)\)$", text, re.DOTALL)
        if not match:
            return None
        parts = [p for p in re.split(r"[\s,/]+", match.group(2).strip()) if p]
        if len(parts) < 3:
            return None
        alpha = _num(parts[3]) if len(parts) > 3 else 1.0
        kind = match.group(1)
        if kind.startswith("rgb"):
            return tuple(255 * _num(p) if p.endswith("%") else float(p) for p in parts[:3]) + (alpha,)
        if kind.startswith("hsl"):
            hue, sat, light = float(parts[0].replace("deg", "")), _num(parts[1]), _num(parts[2])
            chroma = (1 - abs(2 * light - 1)) * sat
            x = chroma * (1 - abs((hue / 60) % 2 - 1))
            m = light - chroma / 2
            r, g, b = [(chroma, x, 0), (x, chroma, 0), (0, chroma, x), (0, x, chroma), (x, 0, chroma),
                       (chroma, 0, x)][int(hue % 360 // 60)]
            return ((r + m) * 255, (g + m) * 255, (b + m) * 255, alpha)
        lightness, chroma, hue = _num(parts[0]), float(parts[1]), math.radians(float(parts[2].replace("deg", "")))
        a, b = chroma * math.cos(hue), chroma * math.sin(hue)
        l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
        linear = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
                  -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
                  -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
        gamma = [255 * min(1, max(0, 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)) for v in linear]
        return (*gamma, alpha)
    except (ValueError, IndexError, OverflowError):
        return None


def spread(rgba):
    return max(rgba[:3]) - min(rgba[:3])


def luminance(rgba):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(rgba[0]) + 0.7152 * lin(rgba[1]) + 0.0722 * lin(rgba[2])


def is_neutral_colour(color):
    """impeccable isNeutralAuthoredColor: a keyword, or a colour whose channels spread under 30."""
    color = re.sub(r"\s*!important\s*$", "", color.strip().lower())
    if color in NEUTRAL_KEYWORDS:
        return True
    rgba = to_rgba(color)
    return rgba is not None and spread(rgba) < 30


def is_neutral_border(text):
    """impeccable is_neutral_border_color: the colour after "solid" is neutral; a border with no colour word is not."""
    found = NEUTRAL_BORDER.search(text)
    return bool(found) and is_neutral_colour(found.group(1))


def split_top(text, sep=","):
    """Split on sep outside parentheses."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == sep and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return [p.strip() for p in parts if p.strip()]


def decl_scope(body, idx):
    """The declaration block, or the tag, that holds the offset idx."""
    open_b, close_b, lt = body.rfind("{", 0, idx), body.find("}", idx), body.rfind("<", 0, idx)
    if lt > open_b:
        end = body.find(">", idx)
        return body[lt:len(body) if end < 0 else end]
    return body[open_b + 1:len(body) if close_b < 0 else close_b]


def parse_decls(block):
    decls = {}
    for part in block.split(";"):
        if ":" in part:
            prop, value = part.split(":", 1)
            decls[prop.strip().lower()] = value.strip()
    return decls


def px_length(text):
    match = re.fullmatch(r"(-?[\d.]+)(px|rem|em)?", text.strip().lower())
    number = safe_float(match.group(1)) if match else None
    if number is None or (match.group(2) is None and number != 0):
        return None
    return number * (16 if match.group(2) in ("rem", "em") else 1)


def block_end(body, start):
    """Index just after the brace block whose opening brace sits just before start."""
    depth, i = 1, start
    while i < len(body) and depth:
        depth += (body[i] == "{") - (body[i] == "}")
        i += 1
    return i


def parse_keyframes(body):
    """name -> keyframes body for every @keyframes in the text."""
    return {m.group(1): body[m.end():block_end(body, m.end()) - 1]
            for m in re.finditer(r"@(?:-webkit-)?keyframes\s+([\w-]+)\s*\{", body)}


def rule_blocks(body):
    """(selector, decls, selector offset, open brace, close brace) of each innermost rule that is not a keyframe step.

    One pass over the braces, so the cost is linear in the text.
    """
    ranges = [(m.start(), block_end(body, m.end())) for m in re.finditer(r"@(?:-webkit-)?keyframes\s+[\w-]+\s*\{", body)]
    starts = [a for a, _ in ranges]
    for before, start, end in innermost_blocks(body):
        i = bisect.bisect_right(starts, start) - 1
        if i >= 0 and start < ranges[i][1]:
            continue
        group = body[before + 1:start]
        selector = group.strip().split("\n")[-1].strip()
        if selector and not selector.startswith("@"):
            yield selector, parse_decls(body[start + 1:end]), before + 1 + len(group.rstrip()) - len(selector), start, end


SCALE_FN = re.compile(r"scale(?:[xyz]|3d)?\(([^()]*)\)", re.IGNORECASE)
BEZIER = re.compile(r"cubic-bezier\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)", re.IGNORECASE)


def factors_within_unit(text):
    tokens = [t for t in re.split(r"[\s,]+", text.strip()) if t]
    return bool(tokens) and all(re.fullmatch(r"\d*\.?\d+", t) and float(t) <= 1 for t in tokens)


def transform_only_shrinks(value):
    rest, found = value, False
    while rest:
        match = SCALE_FN.match(rest)
        if not match or not factors_within_unit(match.group(1)):
            return False
        found, rest = True, rest[match.end():].lstrip()
    return found


def keyframes_only_pulse(kf_body):
    """impeccable keyframes_only_pulse: every declaration scales within 0..1, fades, or eases inside its range."""
    any_decl = False
    for step in re.finditer(r"\{([^{}]*)\}", kf_body):
        for prop, value in parse_decls(step.group(1)).items():
            value = re.sub(r"\s*!important$", "", value, flags=re.IGNORECASE).strip().lower()
            any_decl = True
            if prop == "opacity":
                continue
            if prop == "scale":
                ok = value == "none" or factors_within_unit(value)
            elif prop == "transform":
                ok = value == "none" or transform_only_shrinks(value)
            elif prop == "animation-timing-function":
                curves = [[safe_float(g) for g in b] for b in BEZIER.findall(value)]
                ok = "var(" not in value and "linear(" not in value and all(
                    None not in b and 0 <= b[1] <= 1 and 0 <= b[3] <= 1 for b in curves)
            else:
                ok = False
            if not ok:
                return False
    return any_decl


# --- pulsing dot: impeccable collect_pulse_keyframes (foundation/src/css/scan.rs) ---

OPACITY_DECL = re.compile(r"\bopacity\s*:", re.IGNORECASE)
BOX_SHADOW_DECL = re.compile(r"\bbox-shadow\s*:", re.IGNORECASE)
TRANSFORM_SCALE = re.compile(r"\btransform\s*:[^;{}]*\bscale", re.IGNORECASE)
KEYFRAME_STEP = re.compile(r"([^{};]+)\{([^{}]*)\}")
SCALE_NAME = re.compile(r"\b(scale(?:x|y|z|3d)?)\(", re.IGNORECASE)
TRANSLATE_FN = re.compile(r"translate(?:x|y|z|3d)?\([^)]*\)", re.IGNORECASE)
ZERO_OFFSET = re.compile(r"-?0(?:px|%|rem|em)?")
PULSE_TRAVEL_MIN_PX = 4.0
PULSE_OFFSET_PROPS = ("left", "right", "top", "bottom", "inset-inline-start", "inset-inline-end",
                      "inset-block-start", "inset-block-end", "margin-left", "margin-right", "margin-top",
                      "margin-bottom", "margin-inline-start", "margin-inline-end", "margin-block-start",
                      "margin-block-end")
OPPOSITE = dict(zip(PULSE_OFFSET_PROPS, ("right", "left", "bottom", "top", "inset-inline-end", "inset-inline-start",
                                         "inset-block-end", "inset-block-start", "margin-right", "margin-left",
                                         "margin-bottom", "margin-top", "margin-inline-end", "margin-inline-start",
                                         "margin-block-end", "margin-block-start")))


def decl_map(block):
    """parse_decls with a trailing !important removed from each value."""
    return {prop: re.sub(r"\s*!important\s*$", "", value, flags=re.IGNORECASE).strip()
            for prop, value in parse_decls(block).items()}


def length_px(value):
    match = re.fullmatch(r"(-?[0-9.]+)(px|rem|em)", value.strip(), re.IGNORECASE)
    number = safe_float(match.group(1)) if match else None
    if number is None:
        return None
    return number if match.group(2).lower() == "px" else number * 16


def translate_component(value):
    """(px, percent) of one translation component, or None when it cannot be read."""
    value = value.strip()
    if ZERO_OFFSET.fullmatch(value):
        return (0.0, 0.0)
    if value.endswith("%"):
        number = value[:-1].strip()
        parsed = safe_float(number) if re.fullmatch(r"[0-9.+-]+", number) else None
        return None if parsed is None else (0.0, parsed)
    px = length_px(value)
    return None if px is None else (px, 0.0)


def add_axis(axes, i, part):
    axes[i] = (axes[i][0] + part[0], axes[i][1] + part[1]) if axes[i] is not None and part is not None else None


def step_translation(decls):
    """Per axis (x, y, z) the (px, percent) a step translates by, None for an axis it cannot read; None without a transform or translate."""
    transform, translate = decls.get("transform"), decls.get("translate")
    if transform is None and translate is None:
        return None
    transform = transform.strip().lower() if transform is not None else None
    out = [(0.0, 0.0)] * 3
    if transform is not None:
        if "matrix" in transform:
            return [None] * 3
        first = TRANSLATE_FN.search(transform)
        if first and any(word in transform[:first.start()] for word in ("scale", "rotate", "skew", "perspective")):
            return [None] * 3
        for m in TRANSLATE_FN.finditer(transform):
            call = m.group(0)
            name, inner = call[:call.index("(")], call[call.index("(") + 1:-1]
            if "(" in inner:
                for i in {"translatex": [0], "translatey": [1], "translatez": [2]}.get(name, [0, 1, 2]):
                    out[i] = None
                continue
            args = [a.strip() for a in inner.split(",")]
            if name in ("translatex", "translatey", "translatez"):
                add_axis(out, "xyz".index(name[-1]), translate_component(args[0]))
            else:
                for i in range(3):
                    add_axis(out, i, (0.0, 0.0) if i >= len(args) else translate_component(args[i]))
    if translate is not None and translate.strip().lower() != "none":
        for i, token in enumerate(translate.lower().split()[:3]):
            add_axis(out, i, translate_component(token))
    return out


def axis_travels(a, b):
    return a is not None and b is not None and abs(a[1] - b[1]) < 1e-9 and abs(a[0] - b[0]) >= PULSE_TRAVEL_MIN_PX


def squash(value):
    return "".join(value.split()).lower()


def keyframes_move_or_resize(body):
    """impeccable keyframes_move_or_resize: steps that travel 4px or more, or a height that changes at the same width."""
    translations, sizes, offsets = [], [], []
    for step in KEYFRAME_STEP.finditer(body):
        decls = decl_map(step.group(2))
        moved = step_translation(decls)
        if moved is not None:
            translations.append(moved)
        offsets.append({p: " ".join(decls[p].lower().split()) for p in (*PULSE_OFFSET_PROPS, "width", "height") if p in decls})
        if "height" in decls:
            sizes.append((squash(decls["height"]), squash(decls["width"]) if "width" in decls else None))
    travels = any(axis_travels(a[i], b[i]) for a in translations for b in translations for i in range(3))

    def same(x, y):
        px, py = length_px(x), length_px(y)
        return abs(px - py) < 1e-6 if px is not None and py is not None else x == y
    resizes = any(not same(h, sizes[0][0]) for h, _ in sizes) and all(
        (w is None and sizes[0][1] is None) or (w is not None and sizes[0][1] is not None and same(w, sizes[0][1]))
        for _, w in sizes)

    def offset_px(value):
        return 0.0 if ZERO_OFFSET.fullmatch(value.strip()) else length_px(value)

    def changed(a, b, prop):
        if prop not in a or prop not in b:
            return False
        x, y = offset_px(a[prop]), offset_px(b[prop])
        return abs(x - y) >= PULSE_TRAVEL_MIN_PX if x is not None and y is not None else a[prop] != b[prop]
    offset_travels = any(
        not (changed(a, b, "width") or changed(a, b, "height"))
        and any(changed(a, b, prop) and not changed(a, b, OPPOSITE[prop]) for prop in PULSE_OFFSET_PROPS)
        for a in offsets for b in offsets)
    return travels or resizes or offset_travels


def scales_on_one_axis(body):
    """Every scale in the keyframes runs along one axis (all scaleX or all scaleY): an eye that blinks, a bar that fills."""
    axis = None
    for step in KEYFRAME_STEP.finditer(body):
        decls = decl_map(step.group(2))
        if decls.get("scale", "none").strip().lower() != "none":
            return False
        for m in SCALE_NAME.finditer(decls.get("transform", "")):
            name = m.group(1).lower()
            if name not in ("scalex", "scaley") or (axis is not None and axis != name):
                return False
            axis = name
    return axis is not None


def collect_pulse_keyframes(body):
    """name -> whether the keyframes pulse: opacity, box-shadow or a scale at any factor, without moving or resizing the box."""
    pulses = {}
    for m in re.finditer(r"@(?:-webkit-)?keyframes\s+([\w-]+)\s*\{", body):
        inner = body[m.end():block_end(body, m.end()) - 1]
        result = bool(OPACITY_DECL.search(inner) or BOX_SHADOW_DECL.search(inner)
                      or (TRANSFORM_SCALE.search(inner) and not scales_on_one_axis(inner))) \
            and not keyframes_move_or_resize(inner)
        pulses[m.group(1)] = pulses.get(m.group(1), False) or result
    return pulses


# --- S19 card gate: impeccable DeclaredCorners (core/src/checks/rules.rs) and SIDE_ACCENT_MIN_RADIUS_PX ---

SIDE_ACCENT_MIN_RADIUS_PX = 4.0
NOMINAL_CARD_WIDTH_PX = 1000.0
TW_ROUNDED_CLASS = re.compile(
    r"rounded(?:-(tl|tr|br|bl|ss|se|ee|es|t|r|b|l|s|e))?(?:-([a-z0-9-]+|\[[^\]]*\]|\([^)]*\)))?")
TW_RADIUS_PX = {None: 4.0, "sm": 4.0, "none": 0.0, "xs": 2.0, "md": 6.0, "lg": 8.0, "xl": 12.0, "2xl": 16.0,
                "3xl": 24.0, "4xl": 32.0, "full": 9999.0}
TW_CORNER_GROUP = {None: (0, (0, 1, 2, 3)), "t": (1, (0, 1)), "r": (1, (1, 2)), "e": (1, (1, 2)), "b": (1, (2, 3)),
                   "l": (1, (0, 3)), "s": (1, (0, 3)), "tl": (2, (0,)), "ss": (2, (0,)), "tr": (2, (1,)),
                   "se": (2, (1,)), "br": (2, (2,)), "ee": (2, (2,)), "bl": (2, (3,)), "es": (2, (3,))}
RADIUS_DECL_ANY = re.compile(
    r"(?<![\w-])(border-radius|border-(?:top-left|top-right|bottom-right|bottom-left|start-start|start-end|end-end|"
    r"end-start)-radius|borderRadius|border(?:TopLeft|TopRight|BottomRight|BottomLeft|StartStart|StartEnd|EndEnd|"
    r"EndStart)Radius)\s*[:=]\s*\{?\s*[\"'`]?([^;}\"'`,<>]+)", re.IGNORECASE)
LONGHAND_CORNER = {"topleft": 0, "startstart": 0, "topright": 1, "startend": 1, "bottomright": 2, "endend": 2,
                   "bottomleft": 3, "endstart": 3}
STYLESHEET_IMPORT = re.compile(
    r"""\bimport\s+(?:[\w*${},\s]+\s+from\s+)?["'][^"']+\.(?:css|scss|sass|less)["']"""
    r"""|\brequire\(\s*["'][^"']+\.(?:css|scss|sass|less)["']\s*\)|@import\b|@use\s+["'](?!sass:)"""
    r"""|<link\b[^>]*rel\s*=\s*["']?stylesheet|<style\b[^>]*\bsrc\s*=""", re.IGNORECASE)
STYLE_ATTR = re.compile(r"""(?<![\w-])style\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)


class Corners:
    """The corner radii (px) a box declares, [top-left, top-right, bottom-right, bottom-left]; None is a corner that cannot be read."""

    def __init__(self, unknown=False):
        self.declared = unknown
        self.c = [None if unknown else 0.0] * 4

    def set_corner(self, i, px):
        self.declared, self.c[i] = True, px

    def raise_corner(self, i, px):
        self.declared = True
        self.c[i] = max(self.c[i], px) if self.c[i] is not None and px is not None else None

    def raise_to(self, other):
        if other.declared:
            for i in range(4):
                self.raise_corner(i, other.c[i])

    def rounded_away(self, side):
        """Rounded at least 4px on both corners the stripe on side [top, right, bottom, left][side] does not touch; unreadable counts as rounded."""
        if not self.declared:
            return False
        a, b = ((self.c[3], self.c[2]), (self.c[0], self.c[3]), (self.c[0], self.c[1]), (self.c[1], self.c[2]))[side]
        return True if a is None or b is None else a >= SIDE_ACCENT_MIN_RADIUS_PX and b >= SIDE_ACCENT_MIN_RADIUS_PX


def radius_token_px(token):
    match = re.fullmatch(r"([+-]?(?:\d+\.?\d*|\.\d+))([a-z%]*)", token.strip().lower())
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2)
    if unit == "px":
        return number
    if unit == "%":
        return number / 100 * NOMINAL_CARD_WIDTH_PX
    if unit in ("em", "rem"):
        return number * 16
    return 0.0 if unit == "" and number == 0 else None


def radius_half(text):
    parts = text.split()
    sizes = [radius_token_px(t) for t in parts]
    if not parts or len(parts) > 4 or None in sizes:
        return None
    if len(sizes) == 1:
        return sizes * 4
    if len(sizes) == 2:
        return [sizes[0], sizes[1], sizes[0], sizes[1]]
    return [sizes[0], sizes[1], sizes[2], sizes[1]] if len(sizes) == 3 else sizes


def radius_corners(value):
    """The four corners of a border-radius shorthand; a zero vertical radius squares a corner; None when a token cannot be read."""
    halves = value.split("/")
    horizontal = radius_half(halves[0])
    if horizontal is None:
        return None
    if len(halves) > 1:
        vertical = radius_half(halves[1])
        if vertical is None:
            return None
        horizontal = [0.0 if v <= 0 else h for h, v in zip(horizontal, vertical)]
    return horizontal


def apply_radius_decls(corners, text):
    """Apply each radius declaration in text, in order, to corners."""
    for m in RADIUS_DECL_ANY.finditer(text):
        key = re.sub(r"[-]", "", m.group(1).lower())
        value = re.sub(r"\s*!important\s*$", "", m.group(2).strip(), flags=re.IGNORECASE).strip()
        if "-" not in m.group(1) and re.fullmatch(r"-?[\d.]+", value):
            value += "px"  # a bare number in a style object is px
        if key == "borderradius":
            values = radius_corners(value)
            corners.declared = True
            corners.c = list(values) if values is not None else [None] * 4
        else:
            corner = LONGHAND_CORNER[key[len("border"):-len("radius")]]
            parts = value.split()
            first = radius_token_px(parts[0]) if parts else None
            second = radius_token_px(parts[1]) if len(parts) > 1 else None
            corners.set_corner(corner, 0.0 if len(parts) > 1 and second is not None and second <= 0 else first)


def tw_corners(text):
    """The corners a run of Tailwind classes gives a box; a class behind a variant can only raise a corner."""
    base, variants = [], []
    for raw in re.split(r"[\s\"'`{}]+", text):
        token = raw.strip("!")
        bracket = token.find("[")
        colon = token[:len(token) if bracket < 0 else bracket].rfind(":")
        variant, cls = (True, token[colon + 1:].lstrip("!")) if colon >= 0 else (False, token)
        m = TW_ROUNDED_CLASS.fullmatch(cls)
        if not m:
            continue
        group, indexes = TW_CORNER_GROUP[m.group(1)]
        size = m.group(2)
        if size is None or size in TW_RADIUS_PX:
            px = TW_RADIUS_PX[size]
        elif size.startswith("["):
            px = radius_token_px(size[1:-1].replace("_", " ").split()[0]) if size[1:-1].strip() else None
        else:
            px = None
        (variants if variant else base).append((group, indexes, px) if not variant else (indexes, px))
    corners = Corners()
    for _, indexes, px in sorted(base, key=lambda entry: entry[0]):
        for i in indexes:
            corners.set_corner(i, px)
    for indexes, px in variants:
        for i in indexes:
            corners.raise_corner(i, px)
    return corners


def tag_corners(attrs, unknown=False):
    """Corners a tag declares: its rounded-* classes, then the radius in its style attribute or style object."""
    corners = tw_corners(attrs)
    if unknown and not corners.declared:
        corners = Corners(unknown=True)
    apply_radius_decls(corners, attrs)
    return corners


def has_radius(decls):
    return any(p == "border-radius" or re.fullmatch(r"border-(?:top|bottom|start|end)-(?:left|right|start|end)-radius", p)
               for p in decls)


def last_compound(selector):
    """Class names and the tag name of the last compound of one selector; None for a pseudo-element or a compound with neither."""
    compound = re.split(r"[\s>+~]+", selector.strip())[-1]
    if "::" in compound:
        return None
    tokens = {"." + c for c in re.findall(r"\.([\w-]+)", compound)}
    tag = re.match(r"[a-zA-Z][\w-]*", compound)
    if tag:
        tokens.add(tag.group(0).lower())
    return tokens or None


def rules_corners(rules, applies):
    """The largest radius, corner by corner, that the rules for which applies(tokens) holds declare."""
    corners = Corners()
    for selector, decls, *_ in rules:
        if not has_radius(decls):
            continue
        if any(applies(t) for t in (last_compound(s) for s in selector.split(",")) if t):
            one = Corners()
            apply_radius_decls(one, "".join(f"{p}: {v};" for p, v in decls.items()))
            corners.raise_to(one)
    return corners


# --- S26 / S27: a dark page (impeccable css_text_has_dark_root_bg, core/src/checks/css_scan.rs) ---

DARK_BG = re.compile(
    r"(?<![\w-])background(?:-color)?\s*:\s*(?:#(?:0[0-9a-f]|1[0-9a-f]|2[0-3])[0-9a-f]{4}\b|#[01][0-9a-f]{2}\b"
    r"|rgb\(\s*\d{1,2}\s*,\s*\d{1,2}\s*,\s*\d{1,2}\s*\))", re.IGNORECASE)
TW_DARK_BG = re.compile(r"(?<![\w-])bg-(?:gray|slate|zinc|neutral|stone)-(?:9\d{2}|800)(?![\w-])")
ROOT_BLOCK = re.compile(r"(?:^|[}\s,;>])(?:body|html|:root)\s*(?:,[^{]*)?\{([^}]*)\}", re.IGNORECASE)
INLINE_BODY_STYLE = re.compile(r'<body[^>]*\bstyle\s*=\s*"([^"]*)"', re.IGNORECASE)
BG_DECL_ANY = re.compile(r"(?<![\w-])background(?:-color)?\s*:\s*([^;{}]+)", re.IGNORECASE)
CUSTOM_PROP = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+)")
VAR_REF = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)", re.IGNORECASE)


def resolve_vars(value, props, depth=0):
    """Replace var(--x[, fallback]) by what the file declares for --x, up to 8 levels deep."""
    def sub(match):
        found = props.get(match.group(1))
        if found is None:
            found = match.group(2)
        return match.group(0) if found is None or depth >= 8 else resolve_vars(found.strip(), props, depth + 1)
    return VAR_REF.sub(sub, value)


def colour_of(text):
    token = COLOR_TOKEN.search(text)
    return to_rgba(token.group(0)) if token else None


def dark_page(body):
    """True when the file paints a near-black ground: a dark background on any selector, a dark Tailwind ground, or a root background."""
    for match in DARK_BG.finditer(body):
        rgba = colour_of(match.group(0).split(":", 1)[1])
        if rgba is None or luminance(rgba) < 0.1:
            return True
    if TW_DARK_BG.search(body):
        return True
    props = {m.group(1): m.group(2).strip() for m in CUSTOM_PROP.finditer(body)}
    scopes = [m.group(1) for m in ROOT_BLOCK.finditer(body)]
    inline = INLINE_BODY_STYLE.search(body)
    scopes += [inline.group(1)] if inline else []
    for scope in scopes:
        for decl in BG_DECL_ANY.finditer(scope):
            rgba = colour_of(resolve_vars(decl.group(1).strip(), props))
            if rgba and rgba[3] > 0.5 and luminance(rgba) < 0.1:
                return True
    return False


INFINITE = re.compile(r"(?<![\w-])infinite(?![\w-])", re.IGNORECASE)
ANIM_KEYWORDS = {"ease", "ease-in", "ease-out", "ease-in-out", "linear", "step-start", "step-end", "infinite", "normal",
                 "reverse", "alternate", "alternate-reverse", "forwards", "backwards", "both", "none", "running",
                 "paused", "initial", "inherit", "unset", "revert"}


def infinite_animation_names(decls):
    names = []
    for layer in split_top(decls.get("animation", "")):
        if INFINITE.search(layer):
            for token in layer.split():
                if re.fullmatch(r"[A-Za-z_-][\w-]*", token) and token.lower() not in ANIM_KEYWORDS:
                    names.append(token)
                    break
    if INFINITE.search(decls.get("animation-iteration-count", "")):
        names += [n.strip() for n in decls.get("animation-name", "").split(",")
                  if n.strip() and n.strip().lower() != "none"]
    return names


ROUNDED_NONE = re.compile(r"(?<![\w-])rounded-none(?![\w-])")
ROUNDED_ANY = re.compile(r"(?<![\w-])rounded(?:-[\w.\[\]/%-]+)?(?![\w-])")
SAFE_ELEMENT = re.compile(r"<(?:blockquote|nav|pre|code|input|span|a)(?=[\s>])", re.IGNORECASE)
SAFE_TAGS = {"blockquote", "nav", "pre", "code", "input", "span", "a"}
SIDE_TAB_TW = re.compile(r"(?<![\w-])border-[lrse]-(\d+)(?![\w-])")
SIDE_TAB_CSS = re.compile(r"border-(?:left|right)\s*:\s*(\d+)px\s+solid([^;}\n]*)", re.IGNORECASE)
SIDE_TAB_WIDTH = re.compile(r"border-(?:left|right)-width\s*:\s*(\d+)px", re.IGNORECASE)
SIDE_TAB_INLINE = re.compile(r"border-inline-(?:start|end)\s*:\s*(\d+)px\s+solid", re.IGNORECASE)
SIDE_TAB_INLINE_WIDTH = re.compile(r"border-inline-(?:start|end)-width\s*:\s*(\d+)px", re.IGNORECASE)
NEUTRAL_BORDER = re.compile(
    r"solid\s+((?:rgba?|hsla?|oklch|oklab|lab|lch|hwb|color)\([^)]*\)|#[0-9a-fA-F]{3,8}\b|[a-zA-Z]+)", re.IGNORECASE)
RADIAL_GLOW_MIN_EFFECTIVE_ALPHA = 0.14
SIDE_TAB_JS = re.compile(r"border(?:Left|Right)\s*[:=]\s*[\"'`](\d+)px\s+solid", re.IGNORECASE)
ACCENT_TW = re.compile(r"(?<![\w-])border-[tb]-(\d+)(?![\w-])")
ACCENT_CSS = re.compile(r"border-(?:top|bottom)\s*:\s*(\d+)px\s+solid", re.IGNORECASE)
TW_BOUNCE = re.compile(r"(?<![\w-])animate-bounce(?![\w-])")
BOUNCE_ANIM = re.compile(r"(?<![\w-])animation(?:-name)?\s*:\s*([^;{}]*(?:bounce|elastic|wobble|jiggle|spring)[^;{}]*)",
                         re.IGNORECASE)
SHADOW_PROP = re.compile(r"""(?<![\w-])(box-shadow|text-shadow)\s*:\s*([^;{}\n"'<>]+)""", re.IGNORECASE)
TW_SHADOW = re.compile(r"(?<![\w-])shadow-\[([^\]]+)\]")
RADIAL = re.compile(r"(?<![\w-])(repeating-)?radial-gradient\(", re.IGNORECASE)
BG_DECL = re.compile(r"(?<![\w-])background(?:-image)?\s*:\s*([^;{}]+)", re.IGNORECASE)
REPEATING = re.compile(r"repeating-(linear|radial|conic)-gradient\s*\(", re.IGNORECASE)
HAIRLINE = re.compile(r"\b\d{1,3}px\s*,\s*transparent\s+\d{1,3}px", re.IGNORECASE)
HAIRLINE_INVERTED = re.compile(r"transparent\s+calc\(100%\s*-\s*\d{1,3}px\)", re.IGNORECASE)
GRID_BLOCK = re.compile(r"\{([^{}]*)\}|style\s*=\s*\"([^\"]*)\"|style\s*=\s*'([^']*)'", re.IGNORECASE)
BG_SIZE_PX = re.compile(r"background-size\s*:[^;{}\"']*\b\d{1,3}px\b", re.IGNORECASE)
SHORTHAND_PX = re.compile(r"/\s*\d{1,3}px\b")
CLIP_PATH = re.compile(r"clip-path\s*:\s*(polygon|path)\s*\(", re.IGNORECASE)
CLIP_CURVE = re.compile(r"[CSQTAcsqta]")
SIGNED_NUM = re.compile(r"-?[0-9.]+")
MARQUEE_TAG = re.compile(r"<marquee\b", re.IGNORECASE)
TRANSLATE_X_PCT = re.compile(r"translate(?:[xX]|3[dD])?\(\s*(?:calc\(\s*)?(-?[0-9.]+)%", re.IGNORECASE)
SCALE_OR_OPACITY = re.compile(r"scale\(|opacity\s*:", re.IGNORECASE)
IMG_TAG = re.compile(r"<img(?![\w-])", re.IGNORECASE)
ATTR = re.compile(r"""([^\s=/>{}]+)(?:\s*=\s*("[^"]*"|'[^']*'|\{(?:[^{}]|\{[^{}]*\})*\}|[^\s>]+))?""")
FONT_STACK = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.IGNORECASE)
FONT_JS = re.compile(r"fontFamily\s*[:=]\s*[\"'`]([^\"'`]+)[\"'`]")
RADIUS_JS = re.compile(r"borderRadius\s*[:=]\s*[\"'`]([^\"'`]+)[\"'`]")
FONT_SIZE_DECL = re.compile(r"(?<![\w-])font-size\s*:\s*([^;}\n]+)", re.IGNORECASE)
FONT_SIZE_JS = re.compile(r"fontSize\s*[:=]\s*[\"'`]([^\"'`]+)[\"'`]")
TW_FONT_SIZE = re.compile(r"(?<![\w-])text-\[(-?[0-9.]+(?:px|rem))\]")
FONT_SIZE_LITERAL = re.compile(r"-?[0-9.]+(?:px|rem)")
GENERIC_FONTS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-serif", "ui-sans-serif",
                 "ui-monospace", "ui-rounded", "emoji", "math", "fangsong", "inherit", "initial", "unset"}
LETTER_SPACING_ANY = re.compile(r"(?<![\w-])letter-spacing\s*:\s*(-?[\d.]+)(em|px|rem)?(?![\w-])", re.IGNORECASE)
TW_TRACKING = re.compile(r"(?<![\w-])tracking-(tighter|tight|normal|wide|wider|widest|\[(-?[\d.]+)em\])(?![\w-])")
TRACKING_EM = {"tighter": -0.05, "tight": -0.025, "normal": 0.0, "wide": 0.025, "wider": 0.05, "widest": 0.1}
CRUSHED_EM, CRUSHED_EM_DISPLAY, DISPLAY_PX, WIDE_EM = -0.07, -0.09, 40.0, 0.05
CJK = re.compile("[ᄀ-ᇿ぀-ヿ㄰-㆏ㇰ-ㇿ㐀-䶿一-鿿가-퟿豈-﫿ｦ-ﾟ]")
PULSE_NAME = re.compile(r"pulse|blink|ping", re.IGNORECASE)
CURSOR_GLYPH = re.compile(r"[_|▀-▟■▮❙❚｜]")
TW_PULSE = re.compile(r"(?<![\w-])animate-(?:ping|pulse)(?![\w-])")
TW_DOT_SIZE = re.compile(r"(?<![\w-])(w|h|size)-(1|1\.5|2|2\.5|3|3\.5|4)(?![\w-])")
REDUCED_MOTION = re.compile(r"@media[^{]*prefers-reduced-motion\s*:\s*reduce[^{]*\{", re.IGNORECASE)


def is_cjk_text(text):
    head = text[:256]
    cjk = len(CJK.findall(head))
    scripted = cjk + len([c for c in head if c.isalpha() and not CJK.match(c)])
    return cjk > 0 and cjk * 2 >= scripted


def is_round_dot(radius, w, h):
    first = (radius or "").strip().lower().split()
    if not first:
        return False
    if first[0].endswith("%"):
        try:
            return float(first[0][:-1]) >= 40
        except ValueError:
            return False
    px = px_length(first[0])
    return px is not None and (px >= 999 or px >= 0.4 * min(w, h))


def shadow_layers(value):
    """(x, y, blur, spread, rgba, inset) per layer of a shadow value; layers it cannot read are skipped."""
    layers = []
    for layer in split_top(value):
        color = COLOR_TOKEN.search(layer)
        rgba = to_rgba(color.group(0)) if color else (0, 0, 0, 1)
        if rgba is None:
            continue
        rest = layer[:color.start()] + " " + layer[color.end():] if color else layer
        lengths = [px_length(t) for t in re.sub(r"(?i)\binset\b", " ", rest).split()]
        if not 2 <= len(lengths) <= 4 or None in lengths:
            continue
        layers.append((*lengths, *([0.0] * (4 - len(lengths))), rgba, "inset" in layer.lower()))
    return layers


def gradient_position(token):
    token = re.sub(r"\s", "", token.lower())
    while token.startswith("calc(") and token.endswith(")"):
        token = token[5:-1]
    match = re.fullmatch(r"(-?[\d.]+)(%|deg|grad|turn)?", token)
    number = safe_float(match.group(1)) if match else None
    if number is None:
        return None
    if number == 0:
        return 0.0
    return number / {"%": 100, "deg": 360, "grad": 400, "turn": 1}[match.group(2)] if match.group(2) else None


def repeating_gradient_repeats(args, radial):
    """impeccable repeating_gradient_repeats: a ramp from 0 to the full length draws once and is no stripe."""
    stops = split_top(args)
    first_tokens = stops[0].split() if stops else []
    if first_tokens and "var(" in first_tokens[0].lower():
        return True
    first_is_color = bool(first_tokens) and (to_rgba(first_tokens[0]) is not None
                                             or first_tokens[0].lower() in ("transparent", "currentcolor"))
    index = 0 if first_is_color else 1
    if len(stops) < index + 2:
        return True
    if radial and index == 1:
        prelude, i = stops[0].lower().split(), 0
        while i < len(prelude):
            if prelude[i] == "at":
                i += 1
                while i < len(prelude) and prelude[i] != "in":
                    i += 1
            elif prelude[i] == "in":
                i += 2
            elif prelude[i] in ("circle", "ellipse", "farthest-corner"):
                i += 1
            else:
                return True
    first, last = stops[index].lower().split(), stops[-1].lower().split()
    if len(last) == 1 and "var(" in last[0]:
        return True
    starts_at_zero = len(first) < 2 or gradient_position(first[1]) == 0.0
    ends_at_full = len(last) == 1 or gradient_position(last[-1]) == 1.0
    return not (starts_at_zero and ends_at_full)


def polygon_vertices(points):
    """(x, y) strings per vertex, or None when a vertex is not two coordinates; a leading fill rule is skipped."""
    vertices = []
    for i, point in enumerate(points):
        coords = split_top(re.sub(r"\s+", " ", point), " ")  # a calc() or var() vertex stays whole
        if i == 0 and len(coords) == 1 and coords[0].lower() in ("nonzero", "evenodd"):
            continue
        if len(coords) != 2:
            return None
        vertices.append(tuple(coords))
    return vertices


def polygon_is_rectilinear(points):
    """Every vertex shares its x or its y with the next: a notched rectangle, whatever the vertex count."""
    vertices = polygon_vertices(points)
    if not vertices or len(vertices) < 3:
        return False

    def key(coord):
        match = re.fullmatch(r"(-?[\d.]+)([a-z%]*)", coord.lower())
        return "0" if match and safe_float(match.group(1)) == 0 else coord.lower().replace(" ", "")
    keyed = [(key(x), key(y)) for x, y in vertices]
    return all(keyed[i][0] == keyed[(i + 1) % len(keyed)][0] or keyed[i][1] == keyed[(i + 1) % len(keyed)][1]
               for i in range(len(keyed)))


def polygon_is_zigzag(points):
    """Vertices take two to four values on one axis and step evenly along the other, swinging like teeth."""
    vertices = polygon_vertices(points)
    if not vertices or len(vertices) < 3:
        return False
    xs, ys = [], []
    for x, y in vertices:
        pair = []
        for c in (x, y):
            m = re.fullmatch(r"(-?[\d.]+)([a-z%]*)", c.lower())
            number = safe_float(m.group(1)) if m else None
            if number is None:
                return False
            pair.append((number, "" if number == 0 else m.group(2)))
        xs.append(pair[0])
        ys.append(pair[1])
    if len({u for _, u in xs if u}) > 1 or len({u for _, u in ys if u}) > 1:
        return False

    def distinct(v):
        out = []
        for n, _ in v:
            if not any(abs(o - n) < 0.01 for o in out):
                out.append(n)
        return sorted(out)

    def even_steps(d):
        if len(d) < 3:
            return False
        step = d[1] - d[0]
        return step > 0 and all(abs((d[i + 1] - d[i]) - step) <= 0.5 for i in range(len(d) - 1))

    def teeth(along, step, across):
        n, swings, last = len(along), 0, None
        for i in range(n):
            j = (i + 1) % n
            if abs(abs(along[j] - along[i]) - step) > 0.5:
                last = None
                continue
            swing = across[j] - across[i]
            if abs(swing) < 0.01:
                continue
            if last is not None and ((last > 0) == (swing > 0) or abs(abs(last) - abs(swing)) > 0.5):
                return False
            last, swings = swing, swings + 1
        return swings >= 3
    dx, dy = distinct(xs), distinct(ys)
    xv, yv = [n for n, _ in xs], [n for n, _ in ys]
    return (2 <= len(dx) <= 4 and even_steps(dy) and teeth(yv, dy[1] - dy[0], xv)) or \
           (2 <= len(dy) <= 4 and even_steps(dx) and teeth(xv, dx[1] - dx[0], yv))


def image_source_missing(attrs, path=""):
    """impeccable image_source_is_missing: no src or srcset attribute carries a value."""
    if re.search(r"\{\s*\.\.\.", attrs):
        return False
    if path.endswith((".svelte", ".astro")) and re.search(r"\{\s*(?:src|srcset)\s*\}", attrs):
        return False  # the shorthand {src} binds the attribute
    for match in ATTR.finditer(attrs):
        name, value = match.group(1), match.group(2)
        base = name.lower().split(".")[0]
        if path.endswith(".vue") and base == "v-bind":
            return False  # v-bind="object" binds attributes the scan cannot see
        if not (base in ("src", "srcset") or re.search(r"[:-](?:src|srcset)$", base)):
            continue
        if ":" in base:
            return False
        if value is not None and (value.startswith("{") or value.strip("\"'").strip() not in ("", "#")):
            return False
    return True


def alpha_of(args):
    """Alpha written in the arguments of an rgb() or hsl() call; 1 when it has none."""
    if "/" in args:
        token = args.split("/", 1)[1]
    else:
        parts = args.split(",")
        token = parts[3] if len(parts) > 3 else ""
    try:
        return _num(token) if token.strip() else 1.0
    except ValueError:
        return 1.0


def wash_alphas(gradient):
    alphas = [alpha_of(m.group(1)) for m in re.finditer(r"(?:rgba?|hsla?)\(([^)]*)\)", gradient, re.IGNORECASE)]
    stripped = re.sub(r"(?:rgba?|hsla?)\([^)]*\)", "", gradient, flags=re.IGNORECASE)
    for digits in re.findall(r"#([0-9a-fA-F]{3,8})\b", stripped):
        if len(digits) == 4:
            alphas.append(int(digits[3] * 2, 16) / 255)
        elif len(digits) == 8:
            alphas.append(int(digits[6:], 16) / 255)
        else:
            alphas.append(1.0)
    if re.search(r"\b(?:white|black|ivory|beige|linen|snow|cream)\b", stripped, re.IGNORECASE):
        alphas.append(1.0)
    if re.search(r"(?<![\w-])transparent(?![\w-])", stripped, re.IGNORECASE):
        alphas.append(0.0)  # a fade to transparent is a scrim, not a wash
    return alphas


def check_generated_tells(path, body, rep, totals):
    """S19-S37 over one file; sources in references/slop-checklist.md."""
    rel = path
    tags = list(open_tags(body))
    rules = list(rule_blocks(body))
    motion = [(m.start(), block_end(body, m.end())) for m in REDUCED_MOTION.finditer(body)]
    live_rules = [r for r in rules if not any(a <= r[2] < b for a, b in motion)]

    def at(idx):
        return line_of(body, idx)

    def line_text(idx):
        start = body.rfind("\n", 0, idx) + 1
        end = body.find("\n", idx)
        return body[start:len(body) if end < 0 else end]

    def direct_text(offset, name):
        parsed = read_tag(body, offset + 1 + len(name))
        found = re.match(r"([^<]*)<", body[parsed[0]:]) if parsed else None
        return parsed, (re.sub(r"\s+", " ", found.group(1)).strip() if found else "")

    # S19 / S20 - an accent border on one side of a card, or on a rounded one.
    # S19 reports only a box rounded 4px or more on both corners away from the stripe (impeccable side-tab).
    sheet_declares = any(has_radius(r[1]) for r in rules)
    imports_sheet = bool(STYLESHEET_IMPORT.search(body))
    style_spans = [(m.start(), m.end()) for m in re.finditer(r"<style\b[^>]*>.*?</style\s*>", body, re.DOTALL | re.IGNORECASE)]
    markup_tags = [(offset, offset + 1 + len(name) + len(attrs) + 1, name, attrs)
                   for offset, name, attrs in tags if name != "@apply"]
    accent_boxes = set()

    def in_stylesheet(idx):
        return path.endswith(".css") or any(a <= idx < b for a, b in style_spans)

    def enclosing_tag(idx):
        found = [t for t in markup_tags if t[0] <= idx < t[1]]
        return found[-1] if found else None

    def rule_around(idx):
        found = [r for r in rules if r[3] < idx < r[4]]
        return found[-1] if found else None

    def literal_classes(attrs):
        """Class names a tag spells out, or None when a class expression hides some."""
        found = CLASS_ATTR.search(attrs)
        if not found:
            return []
        rest = attrs[found.end():]
        if rest[:1] in ("\"", "'"):
            return class_tokens(attrs)
        lone = re.match(r"\{\s*([\"'`])([^\"'`{}$]*)\1\s*\}", rest)
        return lone.group(2).split() if lone else None

    def markup_known_square(name, attrs, side):
        """A tag known square: it squares itself off, or the file's stylesheets cannot round the classes it carries."""
        if not sheet_declares and not imports_sheet:
            return True
        own = tag_corners(attrs, unknown=True)
        if own.declared and not own.rounded_away(side):
            return True
        if imports_sheet or re.search(r"(?:^|\s)css\s*=", attrs):
            return False
        classes = literal_classes(attrs)
        if classes is None:
            return False
        tag_type = None if name[:1].isupper() or "." in name else name.lower()
        return not rules_corners(rules, lambda t: all(
            (c in {"." + k for k in classes}) if c.startswith(".") else c == tag_type for c in t)).rounded_away(side)

    def stylesheet_known_square(idx, side):
        """A declaration in a rule is known square when no rule tied to its box rounds the corners away from the stripe."""
        own = rule_around(idx)
        if own is None:
            return True
        mine = [t for t in (last_compound(s) for s in own[0].split(",")) if t]
        return not rules_corners(rules, lambda t: any(t <= m or m <= t for m in mine)).rounded_away(side)

    def accent(kind, idx, side, key, message, corners, tag=None, utility=False):
        """Add one S19 per element when the box it sits on is rounded."""
        if key in accent_boxes:
            return
        if corners.rounded_away(side):
            ok = True
        elif tag is not None and not in_stylesheet(idx):
            ok = not markup_known_square(tag[2], tag[3], side)
        elif in_stylesheet(idx):
            ok = utility or not stylesheet_known_square(idx, side)
        else:
            ok = False
        if ok and rep.add("WARN", "S19", rel, at(idx), message):
            accent_boxes.add(key)

    for offset, name, attrs in tags:
        rounded = bool(ROUNDED_ANY.search(ROUNDED_NONE.sub("", attrs)))
        if name.lower() not in SAFE_TAGS:
            for m in SIDE_TAB_TW.finditer(attrs):
                if int(m.group(1)) >= (2 if rounded else 4):
                    tag = None if name == "@apply" else (offset, 0, name, attrs)
                    accent("tw", offset, 3 if m.group(0)[7] in "ls" else 1, ("tag", offset),
                           f"{m.group(0)} is a thick accent border on one side of a card; "
                           "drop it or use a subtler accent", tag_corners(attrs), tag, utility=True)
        if rounded and not has_token(attrs, "animate-spin"):
            for m in (m for m in ACCENT_TW.finditer(attrs) if int(m.group(1)) >= 1):
                rep.add("WARN", "S20", rel, at(offset),
                        f"{m.group(0)} on a rounded element; the border clashes with the corners, "
                        "so drop the border or the radius")
    for pattern in (SIDE_TAB_CSS, SIDE_TAB_WIDTH, SIDE_TAB_INLINE, SIDE_TAB_INLINE_WIDTH, SIDE_TAB_JS):
        for m in pattern.finditer(body):
            if pattern is SIDE_TAB_CSS and is_neutral_border(m.group(0)):
                continue
            if SAFE_ELEMENT.search(line_text(m.start())):
                continue
            scope = decl_scope(body, m.start())
            rounded = bool(re.search(r"border-radius", scope, re.IGNORECASE))
            if int(m.group(1)) < (2 if rounded and pattern is SIDE_TAB_CSS else 3):
                continue
            side = 3 if re.search(r"left|start", m.group(0), re.IGNORECASE) else 1
            tag = enclosing_tag(m.start())
            if tag is not None:
                key, corners = ("tag", tag[0]), tag_corners(tag[3])
            else:
                open_brace = body.rfind("{", 0, m.start())
                key, corners = ("block", open_brace), Corners()
                apply_radius_decls(corners, scope)
            accent("decl", m.start(), side, key,
                   f"{m.group(0).strip()} is a thick accent border on one side of a card; "
                   "drop it or use a subtler accent", corners, tag)
    for m in ACCENT_CSS.finditer(body):
        radius = re.search(r"border-radius\s*:\s*([^;}]+)", decl_scope(body, m.start()), re.IGNORECASE)
        if int(m.group(1)) >= 3 and radius and radius.group(1).strip().lower() not in ("0", "0px", "none"):
            rep.add("WARN", "S20", rel, at(m.start()),
                    f"{m.group(0)} on a rounded element; the border clashes with the corners, "
                    "so drop the border or the radius")

    # S21 - bounce and elastic easing.
    keyframes = parse_keyframes(body)
    for m in TW_BOUNCE.finditer(body):
        rep.add("WARN", "S21", rel, at(m.start()), "animate-bounce; use exponential ease-out instead")
    for m in BOUNCE_ANIM.finditer(body):
        for token in re.split(r"[,\s]+", m.group(1)):
            if re.search(r"bounce|elastic|wobble|jiggle|spring", token, re.IGNORECASE) \
                    and not (token in keyframes and keyframes_only_pulse(keyframes[token])):
                rep.add("WARN", "S21", rel, at(m.start()),
                        f"animation {token!r} reads as a bounce; real objects decelerate smoothly, "
                        "so use exponential ease-out")
                break
    for m in BEZIER.finditer(body):
        values = [safe_float(g) for g in m.groups()]
        if None in values or -0.1 <= values[1] <= 1.1 and -0.1 <= values[3] <= 1.1:
            continue
        before = body[:m.start()]
        custom = re.search(r"(--[\w-]+)\s*:\s*$", before[max(before.rfind(c) for c in ";{}") + 1:])
        if custom and not re.search(r"var\(\s*" + re.escape(custom.group(1)) + r"\s*[,)]", body):
            continue  # a custom property nothing reads moves nothing
        rep.add("WARN", "S21", rel, at(m.start()), f"{m.group(0)} overshoots its end value; use exponential ease-out instead")

    # S29 marquee, S18 pulsing dot and S22 blinking cursor: infinite animations read through their keyframes.
    marquee_names = set()
    for name, kf in keyframes.items():
        pct = [f for f in (safe_float(p) for p in TRANSLATE_X_PCT.findall(kf)) if f is not None]
        if pct and not (len(pct) == 1 and SCALE_OR_OPACITY.search(kf)):
            if (max(pct) - min(pct) if len(pct) > 1 else abs(pct[0])) >= 20:
                marquee_names.add(name)

    def toggles_visibility(kf):
        """impeccable keyframes_toggle_visibility: opacity down to 0.15 or visibility hidden, and nothing else but easing."""
        toggles = False
        for step in re.finditer(r"\{([^{}]*)\}", kf):
            for prop, value in parse_decls(step.group(1)).items():
                if prop == "opacity":
                    lead = re.match(r"\s*[-+]?(?:\d+\.?\d*|\.\d+)", value)
                    toggles = toggles or (float(lead.group(0)) <= 0.15 if lead else True)
                elif prop == "visibility":
                    toggles = toggles or "hidden" in value.lower()
                elif prop != "animation-timing-function":
                    return False
        return toggles

    for m in MARQUEE_TAG.finditer(body):
        rep.add("WARN", "S29", rel, at(m.start()),
                "<marquee> element; auto-scrolling content hides half of itself, so let readers move at their own pace")
    seen, pulse_merged = set(), {}
    for selector, decls, offset, *_ in live_rules:
        width = px_length(decls.get("width", decls.get("inline-size", "")))
        height = px_length(decls.get("height", decls.get("block-size", "")))
        sized = width is not None and height is not None
        round_dot = sized and is_round_dot(decls.get("border-radius", ""), width, height)
        for part in selector.split(","):
            if part.strip():
                merged = pulse_merged.setdefault(part.strip(), (offset, {}))
                merged[1].update(decls)
        for name in infinite_animation_names(decls):
            if name in marquee_names and (selector, name) not in seen:
                seen.add((selector, name))
                rep.add("WARN", "S29", rel, at(offset),
                        f"{selector}: infinite horizontal loop animation {name!r}; "
                        "auto-scrolling content hides half of itself")
            if name in keyframes and toggles_visibility(keyframes[name]) and sized and not round_dot:
                vertical = 1 <= width <= 24 and 6 <= height <= 48 and height >= width
                underscore = 1 <= height <= 6 and 4 <= width <= 24
                if vertical or underscore:
                    rep.add("WARN", "S22", rel, at(offset),
                            f"{selector}: a {width:g}x{height:g}px box blinks like a text cursor; "
                            "real fields draw their own caret")

    # S18 - a small round element with an infinite pulse (impeccable pulsing-dot): one finding per selector.
    pulses = collect_pulse_keyframes(body)
    for selector, (offset, decls) in pulse_merged.items():
        pulse_name = next((n for n in infinite_animation_names(decls)
                           if (pulses[n] if n in pulses else PULSE_NAME.search(n))), None)
        width = px_length(decls.get("width", decls.get("inline-size", "")))
        height = px_length(decls.get("height", decls.get("block-size", "")))
        if pulse_name and width is not None and height is not None and 2 <= width <= 16 and 2 <= height <= 16 \
                and max(width, height) <= 1.5 * min(width, height) \
                and is_round_dot(decls.get("border-radius", ""), width, height):
            rep.add("WARN", "S18", rel, at(offset),
                    f"{selector}: {width:g}x{height:g}px dot with an infinite {pulse_name!r} animation simulates liveness; "
                    "keep a static indicator with a label")
    seen_classes = set()
    for offset, name, attrs in tags:
        if name == "@apply" or not TW_PULSE.search(attrs):
            continue
        classes = " ".join(class_tokens(attrs))
        if not has_token(classes, "rounded-full") or not TW_DOT_SIZE.search(classes) or classes in seen_classes:
            continue
        w, h = tw_side_px(classes, "w"), tw_side_px(classes, "h")
        if w is not None and h is not None and (not (2 <= w <= 16 and 2 <= h <= 16) or max(w, h) > 1.5 * min(w, h)):
            continue
        seen_classes.add(classes)
        rep.add("WARN", "S18", rel, at(offset),
                "a small rounded element with animate-ping or animate-pulse simulates liveness; "
                "keep a static indicator with a label")
    blink_classes = {s.lstrip(".") for s, decls, *_ in live_rules if re.fullmatch(r"\.[\w-]+", s)
                     for n in infinite_animation_names(decls) if n in keyframes and toggles_visibility(keyframes[n])}
    for offset, name, attrs in tags:
        if name == "@apply" or not blink_classes & set(class_tokens(attrs)):
            continue
        _, text = direct_text(offset, name)
        if len(text) == 1 and CURSOR_GLYPH.fullmatch(text):
            rep.add("WARN", "S22", rel, at(offset), f"{text!r} blinks like a text cursor; real fields draw their own caret")

    # S23 - an organic clip-path.
    for m in CLIP_PATH.finditer(body):
        kind = m.group(1).lower()
        end = balanced_end(body, m.end() - 1)
        args = body[m.end():end - 1] if end > 0 else re.split(r"[;}]", body[m.end():], maxsplit=1)[0]
        if kind == "path":
            curves = len(CLIP_CURVE.findall(args))
            if curves >= 3:
                rep.add("WARN", "S23", rel, at(m.start()),
                        f"clip-path: path() with {curves} curve segments approximates a blob or torn edge")
            continue
        points = split_top(args)
        off_grid = sum(1 for p in points for n in SIGNED_NUM.findall(p)
                       if safe_float(n) is not None and abs(safe_float(n) - round(safe_float(n) / 25) * 25) > 0.5)
        if len(points) >= 10 and off_grid >= len(points) \
                and not polygon_is_rectilinear(points) and not polygon_is_zigzag(points):
            rep.add("WARN", "S23", rel, at(m.start()),
                    f"clip-path: polygon() with {len(points)} vertices approximates an organic contour")

    # S24 - a raster under a near-opaque gradient wash.
    for m in BG_DECL.finditer(body):
        value = m.group(1)
        first_url = value.lower().find("url(")
        if first_url < 0 or "gradient(" not in value.lower():
            continue
        if re.search(r"(?:background|mix)-blend-mode\s*:\s*(?!normal)\S", decl_scope(body, m.start()), re.IGNORECASE):
            continue
        for g in re.finditer(r"(?:linear|radial|conic)-gradient\([^()]*(?:\([^()]*\)[^()]*)*\)", value[:first_url], re.IGNORECASE):
            alphas = wash_alphas(g.group(0))
            if alphas and all(a >= 0.9 for a in alphas):
                if rep.add("WARN", "S24", rel, at(m.start()),
                           "background image under a near-opaque gradient wash; the page shows the wash, "
                           "so the image ships unseen"):
                    break

    # S25 hard offset shadow, S26 coloured glow.
    shadows = [(m.start(), m.group(1).lower(), m.group(2)) for m in SHADOW_PROP.finditer(body)]
    shadows += [(m.start(), "box-shadow", m.group(1).replace("_", " ")) for m in TW_SHADOW.finditer(body)]
    glow_dark = None
    for index, prop, value in shadows:
        layers = shadow_layers(value)
        if prop == "box-shadow" and any(not inset and rgba[3] > 0.1 and blur == 0 and spread_px >= 0
                                        and max(abs(x), abs(y)) >= 4
                                        for x, y, blur, spread_px, rgba, inset in layers):
            rep.add("WARN", "S25", rel, at(index),
                    f"box-shadow {value.strip()!r}: hard offset with no blur; keep it only for a deliberate "
                    "neobrutalist direction")
        for x, y, blur, spread_px, rgba, inset in layers:
            if spread(rgba) < 30 or blur <= 4 or blur * rgba[3] < 3.0 or blur / 2 + spread_px <= 0:
                continue
            if glow_dark is None:
                glow_dark = dark_page(body)
            if (x == 0 and y == 0) or glow_dark:
                if rep.add("WARN", "S26", rel, at(index), f"{prop} {value.strip()!r}: a coloured glow; use a neutral shadow or none"):
                    break

    # S27 radial halo on a dark page, S28 faint accent spotlight.
    halo_dark = None
    for m in BG_DECL.finditer(body):
        value = m.group(1)
        if re.search(r"url\s*\(", value, re.IGNORECASE):
            continue
        for g in RADIAL.finditer(value):
            if g.group(1):
                continue
            end = balanced_end(value, g.end() - 1)
            args = split_top(value[g.end():(end if end > 0 else len(value) + 1) - 1])
            stops = [a for a in args if COLOR_TOKEN.search(a)]
            if len(args) < 2 or len(stops) < 2:
                continue
            colors = [to_rgba(COLOR_TOKEN.search(s).group(0)) for s in stops]
            first, last = colors[0], colors[-1]
            if first is None or last is None or last[3] > 0.05:
                continue
            px_stop = any(abs(f) <= 24 for s in stops for f in (safe_float(p) for p in re.findall(r"(-?[0-9.]+)px\b", s))
                          if f is not None)
            if not px_stop and first[3] >= 0.7 and spread(first) >= 24:
                if halo_dark is None:
                    halo_dark = dark_page(body)
                if halo_dark:
                    if rep.add("WARN", "S27", rel, at(m.start()),
                               f"radial-gradient halo ({stops[0].split()[0]} to transparent) on a dark page; "
                               "the same tell as a glowing shadow"):
                        break
            tinted = [c for c in colors if c is not None and c[3] > 0.05]
            decls = scope_decls(body, m.start())
            w, h = px_length(decls.get("width", "")), px_length(decls.get("height", ""))
            opacity = safe_float(decls.get("opacity", "1"))
            opacity = 1.0 if opacity is None else min(1.0, max(0.0, opacity))
            if tinted and len(tinted) <= 2 and all(c[3] < 0.45 for c in tinted) and any(spread(c) >= 24 for c in tinted) \
                    and any(spread(c) >= 24 and c[3] * opacity >= RADIAL_GLOW_MIN_EFFECTIVE_ALPHA for c in tinted) \
                    and not (w is not None and h is not None and (w < 240 or h < 160)):
                if rep.add("WARN", "S28", rel, at(m.start()),
                           "accent-coloured radial-gradient fading to transparent behind a section reads as a "
                           "spotlight cloud; use a plain surface"):
                    break

    # S30 - an <img> with no source.
    for m in IMG_TAG.finditer(body):
        parsed = read_tag(body, m.end())
        if parsed and image_source_missing(parsed[1], path):
            rep.add("WARN", "S30", rel, at(m.start()),
                    "<img> has no src, or an empty or placeholder one; use a real image or remove the tag")

    # S31 - repeating-gradient stripes. A suppressed finding leaves the scan running.
    for m in REPEATING.finditer(body):
        end = balanced_end(body, m.end() - 1)
        if end > 0 and repeating_gradient_repeats(body[m.end():end - 1], m.group(1).lower() == "radial"):
            if rep.add("WARN", "S31", rel, at(m.start()),
                       "repeating-gradient stripes as surface decoration; use a deliberate texture or a plain surface"):
                break

    # S32 - a two-axis grid-line background.
    for block in GRID_BLOCK.finditer(body):
        inner = block.group(1) or block.group(2) or block.group(3) or ""
        values = [d.group(1) for d in re.finditer(r"(?<![\w-])background(?:-image)?\s*:\s*([^;{}\"']*)", inner, re.IGNORECASE)]
        hairlines = sum(len(HAIRLINE.findall(v)) + len(HAIRLINE_INVERTED.findall(v)) for v in values)
        if hairlines >= 2 and (BG_SIZE_PX.search(inner) or SHORTHAND_PX.search(";".join(values))):
            if rep.add("WARN", "S32", rel, at(block.start()),
                       "two-axis grid-line gradient background; reserve grids for a real canvas, map or chart"):
                break

    check_theme_scales(rel, body, rep, totals["scales"])
    check_tracking(rel, path, body, tags, rep, direct_text)


def theme_scales(theme_path):
    """Font families, radii (px) and font sizes (px) the theme declares as --font-*, --radius-* and --text-*."""
    scales = {"fonts": set(), "radii": set(), "sizes": set()}
    if not theme_path or not os.path.isfile(theme_path):
        return scales
    with open(theme_path, encoding="utf-8", errors="replace") as handle:
        text = strip_comments(handle.read())
    for value in re.findall(r"--font-[\w-]+\s*:\s*([^;]+);", text):
        for family in split_top(value):
            family = family.strip().strip("'\"").lower()
            if family and not family.startswith("var(") and family != "initial":
                scales["fonts"].add(family)
    for key, pattern in (("radii", r"--radius-[\w-]+\s*:\s*([^;]+);"), ("sizes", r"--text-[a-z0-9]+\s*:\s*([^;]+);")):
        for value in re.findall(pattern, text):
            px = px_length(value)
            if px is not None:
                scales[key].add(px)
    return scales


def check_theme_scales(rel, body, rep, scales):
    """S33-S35: fonts, radii and font sizes outside the scales the theme declares."""
    if scales["fonts"]:
        for m in list(FONT_STACK.finditer(body)) + list(FONT_JS.finditer(body)):
            stack = m.group(1)
            if re.search(r"[$`{}]|var\(", stack):
                continue
            primary = next((f.strip().strip("'\"") for f in stack.split(",")
                            if f.strip().strip("'\"").lower() not in GENERIC_FONTS), "")
            low = primary.lower()
            if primary and low not in scales["fonts"] and not any(h in low for h in MONOSPACE_HINTS):
                rep.add("WARN", "S33", rel, line_of(body, m.start()),
                        f"font {primary!r} is outside the theme's --font-* tokens; use a token font or add the face to the theme")
    if scales["radii"]:
        has_pill = any(r >= 99 for r in scales["radii"])
        for m in list(RADIUS_DECL.finditer(body)) + list(RADIUS_JS.finditer(body)):
            off = []
            for token in re.split(r"[\s/]+", re.sub(r"\s*!important\s*$", "", m.group(1), flags=re.IGNORECASE).strip().lower()):
                if not token or re.search(r"[()%]", token) or token in ("0", "none", "initial", "inherit"):
                    continue
                px = px_length(token)
                if px is None or px <= 0.5 or (has_pill and px >= 99) or any(abs(r - px) <= 0.5 for r in scales["radii"]):
                    continue
                if token not in off:
                    off.append(token)
            # One finding per declaration: a shorthand repeats its corners.
            if off:
                rep.add("WARN", "S34", rel, line_of(body, m.start()),
                        f"border-radius {', '.join(off)} is outside the theme's --radius-* tokens; use a token radius")
    if scales["sizes"]:
        for m in list(FONT_SIZE_DECL.finditer(body)) + list(FONT_SIZE_JS.finditer(body)) + list(TW_FONT_SIZE.finditer(body)):
            value = re.sub(r"\s*!important\s*$", "", m.group(1).strip().lower())
            clamp = re.fullmatch(r"clamp\((.*)\)", value)
            args = split_top(clamp.group(1)) if clamp else []
            off = []
            for token in ([args[0], args[2]] if len(args) == 3 else [value]):
                px = px_length(token) if FONT_SIZE_LITERAL.fullmatch(token.strip()) else None
                if px and px > 0 and not any(abs(s - px) <= 0.5 for s in scales["sizes"]):
                    off.append(token.strip())
            # One finding per declaration: both ends of a clamp() can be off the ramp.
            if off:
                rep.add("WARN", "S35", rel, line_of(body, m.start()),
                        f"font size {', '.join(off)} is off the theme's --text-* ramp; use a ramp step")


TW_TEXT_PX = {"xs": 12, "sm": 14, "base": 16, "lg": 18, "xl": 20, "2xl": 24, "3xl": 30, "4xl": 36, "5xl": 48,
              "6xl": 60, "7xl": 72, "8xl": 96, "9xl": 128}
TW_TEXT_SIZE = re.compile(r"(?<![\w-])text-(xs|sm|base|lg|xl|[2-9]xl)(?![\w-])")


def scope_decls(body, idx):
    """Declarations around idx: the rule block, or the style attribute of the tag that holds it."""
    scope = decl_scope(body, idx)
    if scope.startswith("<"):
        found = STYLE_ATTR.search(scope)
        scope = (found.group(1) or found.group(2) or "") if found else ""
    return parse_decls(scope)


def tw_side_px(classes, side):
    """The px size the first unprefixed Tailwind spacing class (w-2, h-1.5) of side gives, at the 4px step; else None."""
    for token in classes.split():
        number = safe_float(token[len(side) + 1:]) if token.startswith(side + "-") and re.fullmatch(r"[\d.]+", token[len(side) + 1:]) else None
        if number is not None:
            return number * 4
    return None


def font_size_px(value):
    """A font size in px; a clamp() is judged by its larger readable endpoint."""
    value = re.sub(r"\s*!important\s*$", "", value.strip().lower())
    clamp = re.fullmatch(r"clamp\((.*)\)", value)
    if clamp:
        args = split_top(clamp.group(1))
        ends = [px_length(a) for a in (args[0], args[2])] if len(args) == 3 else []
        return max([e for e in ends if e], default=None)
    return px_length(value)


def tag_font_px(attrs):
    """The largest font size a tag sets through Tailwind classes or its style attribute, in px."""
    sizes = [TW_TEXT_PX[m.group(1)] for m in TW_TEXT_SIZE.finditer(attrs)]
    sizes += [px_length(m.group(1)) for m in TW_FONT_SIZE.finditer(attrs)]
    style = STYLE_ATTR.search(attrs)
    if style:
        sizes.append(font_size_px(decl_map(style.group(1) or style.group(2) or "").get("font-size", "")))
    return max([x for x in sizes if x], default=None)


def check_tracking(rel, path, body, tags, rep, direct_text):
    """S36 crushed and S37 wide letter-spacing (impeccable extreme-negative-tracking and wide-tracking).

    The Japanese exemption reads the text of a markup file. A stylesheet carries no element text, so it takes none.
    """
    visible = re.sub(r"<[^>]*>", " ", re.sub(r"<(script|style)\b.*?</\1\s*>", " ", body, flags=re.DOTALL | re.IGNORECASE))
    cjk_file = not path.endswith(".css") and is_cjk_text(visible)
    for m in LETTER_SPACING_ANY.finditer(body):
        value, unit = safe_float(m.group(1)), (m.group(2) or "").lower()
        if value is None:
            continue
        scope = scope_decls(body, m.start())
        size = font_size_px(scope.get("font-size", ""))
        if unit == "em":
            em = value
        elif size:
            em = value * (16 if unit == "rem" else 1) / size
        else:
            continue
        if cjk_file:
            continue
        if em < (CRUSHED_EM_DISPLAY if size and size >= DISPLAY_PX else CRUSHED_EM):
            rep.add("WARN", "S36", rel, line_of(body, m.start()),
                    f"letter-spacing {em:.2f}em is tighter than the letters keep their shapes; tighten display type optically")
        elif em > WIDE_EM and scope.get("text-transform", "").lower() != "uppercase":
            rep.add("WARN", "S37", rel, line_of(body, m.start()),
                    f"letter-spacing {em:.2f}em on body text; reserve wide tracking for short uppercase labels")
    for offset, name, attrs in tags:
        if name == "@apply":
            continue
        for m in TW_TRACKING.finditer(attrs):
            em = safe_float(m.group(2)) if m.group(2) else TRACKING_EM[m.group(1)]
            _, text = direct_text(offset, name)
            if em is None or len(text) <= 20 or is_cjk_text(text):
                continue
            size = tag_font_px(attrs)
            if em < (CRUSHED_EM_DISPLAY if size and size >= DISPLAY_PX else CRUSHED_EM):
                rep.add("WARN", "S36", rel, line_of(body, offset), f"{m.group(0)} is tighter than the letters keep their shapes")
            elif em > WIDE_EM and not has_token(attrs, "uppercase") and not (text.upper() == text and len(text) <= 40):
                rep.add("WARN", "S37", rel, line_of(body, offset),
                        f"{m.group(0)} on body text; reserve wide tracking for short uppercase labels")


def run(targets, theme_path):
    if isinstance(targets, str):
        targets = [targets]
    rep = Report()
    totals = {
        "off_token_colors": set(),
        "families": set(),
        "radii": {},
        "shadow_alphas": {},
    }
    known = theme_colors(theme_path)
    totals["theme_names"] = theme_color_names(theme_path)
    totals["scales"] = theme_scales(theme_path)

    files = collect_files(targets)
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        check_file(path, text, known, rep, totals)

    check_totals(rep, totals)
    return rep, files, known


def main():
    parser = argparse.ArgumentParser(description="Run product-ui slop checks S1-S37.")
    parser.add_argument("path", nargs="+", help="files or directories to check")
    parser.add_argument("--theme", help="path to theme.css (found automatically when omitted)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    missing = [p for p in args.path if not os.path.exists(p)]
    if missing:
        print(f"FAIL: no such path: {', '.join(missing)}", file=sys.stderr)
        return 1

    theme_path = args.theme or find_theme(args.path)
    rep, files, known = run(args.path, theme_path)
    status = "FAIL" if rep.errors else "PASS"

    if args.json:
        print(json.dumps({
            "status": status,
            "theme": theme_path,
            "theme_colors": len(known),
            "files_checked": len(files),
            "error_count": len(rep.errors),
            "warning_count": len(rep.warnings),
            "findings": rep.findings,
        }, indent=2))
    else:
        if not theme_path:
            print("note: no theme.css found; every colour literal counts as off-token")
        for item in rep.findings:
            print(f"{item['severity']:<5} [{item['id']}] {item['file']}:{item['line']}: {item['message']}")
        print(f"{status}: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s) "
              f"across {len(files)} file(s)")

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
