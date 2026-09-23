#!/usr/bin/env python3
"""Deterministic (non-LLM) checks on whether a string should exist.

Standard library only. Runs checks ST1-ST10 against the files an implementation step
produced. The source of record for these checks is references/ban-list.md; change
that file first when a check or a threshold changes.

Errors mean a pattern settles it: the string describes the interface, describes the
layout, or is filler. Warnings mark tendencies, which is all the evidence behind
them supports.

Wording is out of scope. Whether a string that has earned its place is worded well
belongs to product-ui's check_copy.py.

CLI:
    python check_shippable_text.py <path> [--surface lp|app] [--css <file.css>]...
                                          [--checks ST7,ST10] [--dom <dump.json>] [--json]

<path> may be a file or a directory. The surface comes from meta.surface in the
nearest tokens.json unless --surface overrides it. --css adds a stylesheet to the
cascade ST7 resolves against. --checks limits the run to the named check IDs.
--dom runs ST7 over a cdp.js dump instead of over markup, and the dump is then the
only input.

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors),
2 = a directory was given and no file in it is in scope.
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# .scss joins the scope for ST10 only, read as plain CSS: a nested rule contributes
# its own declarations but not its parent's selector, which ST10 does not need.
STYLESHEET_SUFFIXES = {".css", ".scss"}
SCOPE_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte",
                  ".astro"} | STYLESHEET_SUFFIXES
SKIP_DIRS = {"node_modules", "dist", "build", ".next", ".git", ".svelte-kit", "out",
             "coverage", "fixtures"}
SKIP_PATTERNS = (".min.", ".test.", ".spec.")

# ST3 allows a capability sentence on a promotional surface. meta.surface in the
# nearest tokens.json settles it; the path heuristics are the fallback when no
# tokens.json and no --surface are available.
LANDING_SURFACES = {"lp", "landing", "marketing"}
LANDING_DIRS = {"marketing", "landing", "lp"}
LANDING_NAMES = ("landing", "hero")

# --- ST1: the screen describing itself -----------------------------------

ST1 = [
    re.compile(r"(?:この|本)(?:画面|ページ|ダッシュボード|タブ|セクション|アプリ|サービス|機能)(?:では|から|で|には)"),
    re.compile(r"^\s*ここでは"),
    re.compile(r"\b(?:This|The)\s+(?:page|screen|dashboard|view|section|tab|app)\s+"
               r"(?:lets|allows|enables|shows|displays|helps)\b", re.IGNORECASE),
]

# --- ST2: an instruction that points at the layout ------------------------

JA_POSITION = re.compile(
    r"(?:下記|上記|以下|左記|右記|下|上|右|左)の"
    r"(?:フォーム|入力欄|ボタン|欄|メニュー|タブ|カード|リンク|チェックボックス|プルダウン)"
)
JA_INSTRUCTION = re.compile(r"ください|入力|選択|押|クリック|タップ|参照|ご覧")
EN_POSITION = [
    re.compile(r"\b(?:enter|fill|select|choose|click|tap|see|use|complete|review)\b"
               r"[^.!?]{0,60}\b(?:form|field|button|table|list|menu|section|input|box|link)\b"
               r"[^.!?]{0,20}\b(?:below|above)\b", re.IGNORECASE),
    re.compile(r"\bthe\s+(?:form|field|button|table|list|menu|section|input|box|link)\s+"
               r"(?:below|above)\b", re.IGNORECASE),
]

# --- ST3: the capability explainer ----------------------------------------

ST3_JA = re.compile(r"(?:でき|出来)ます。?\s*$|が表示されます。?\s*$|をご覧いただけます。?\s*$")
ST3_EN = re.compile(r"^\s*(?:You can|You'll be able to|You are able to)\b", re.IGNORECASE)
ST3_MAX_CHARS = 80
EMPTY_STATE = re.compile(r"empty|no-?data|nodata|空|ありません|ございません|0件", re.IGNORECASE)
# A tooltip states what a control does; that is the job of a tooltip, not a caption.
TOOLTIP_SOURCES = {"title", "tooltip"}

# --- ST4: helper text restating its label ---------------------------------

HELPER_PROPS = {"helpertext", "helptext", "hint", "description", "caption", "subtitle"}
LABEL_PROPS = {"label", "aria-label"}
HELPER_CLASS = re.compile(
    r"<(?P<tag>[A-Za-z][\w.-]*)\b(?P<attrs>[^<>]*\bclass(?:Name)?\s*=\s*[\"'][^\"']*"
    r"(?:help|hint|description|caption|form-text|field-note)[^\"']*[\"'][^<>]*)>"
    r"(?P<text>[^<>{}]+)<"
)
LABEL_TAG = re.compile(r"<(?:label|FormLabel|Label)\b[^<>]*>(?P<text>[^<>{}]+)<")
CONSTRAINT = re.compile(
    r"[0-9０-９]|半角|全角|文字|以内|以上|以下|必須|任意|形式|拡張子|桁|バイト|@|"
    r"\b(?:format|max|min|maximum|minimum|required|optional|characters?|digits?|"
    r"must|at least|up to|MB|KB)\b",
    re.IGNORECASE,
)
ST4_OVERLAP = 0.6
ST4_WINDOW = 600

# --- ST5: a legend for the self-evident -----------------------------------

ST5_JA = re.compile(r"(?:色|アイコン|マーク|バッジ|印|ラベル)[^。]{0,20}?(?:示し|表し|意味し)ます")
ST5_EN = re.compile(r"\b(?:red|green|amber|yellow|orange|grey|gray|blue)\b[^.]{0,30}"
                    r"\b(?:means|indicates|shows|denotes)\b", re.IGNORECASE)

# --- ST6: inline tutorial prose -------------------------------------------

ST6_FIRST = re.compile(r"まず|最初に|はじめに")
ST6_NEXT = re.compile(r"次に|その後|続いて|最後に")
ST6_IMPERATIVE = re.compile(r"してください|して下さい")
ST6_EN = re.compile(r"\bFirst,")
ST6_EN_NEXT = re.compile(r"\bThen\b")
# Markup-only signals: the bare word "steps" in visible prose is not a stepper.
WIZARD = re.compile(r"stepper|wizard|role\s*=\s*[\"']tablist[\"']|aria-current\s*=\s*[\"']step[\"']"
                    r"|<ol\b|<Steps?\b|[\"']steps?[\"']", re.IGNORECASE)

# --- ST7 / ST10: the size a run actually gets ------------------------------

# Japanese glyphs lose their strokes where Latin letters still read, so the Latin
# allowance does not extend to a run holding a single CJK character.
CJK = re.compile(r"[぀-ヿ一-鿿]")
MIN_PX = 14.0
LATIN_MIN_PX = 12.0
LATIN_MAX_RUN = 24
ST10_ROOT_PX = 16.0  # ST10 judges a declaration on its own, so rem is 16px there.

CSS_KEYWORDS = {"xx-small": 9.0, "x-small": 10.0, "small": 13.0, "medium": 16.0,
                "large": 18.0, "x-large": 24.0, "xx-large": 32.0}
CSS_RELATIVE = {"smaller": 0.83, "larger": 1.2}
ABSOLUTE_UNITS = {"px": 1.0, "pt": 4.0 / 3.0}
TW_SCALE = {"xs": 12.0, "sm": 14.0, "base": 16.0, "lg": 18.0, "xl": 20.0,
            "2xl": 24.0, "3xl": 30.0, "4xl": 36.0, "5xl": 48.0, "6xl": 60.0,
            "7xl": 72.0, "8xl": 96.0, "9xl": 128.0}

LENGTH = re.compile(r"^(-?\d*\.?\d+)\s*(px|rem|em|pt|%)?$", re.IGNORECASE)
PX_LITERAL = re.compile(r"(\d*\.?\d+)\s*px", re.IGNORECASE)
VAR_CALL = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,([^()]*))?\)", re.IGNORECASE)
MATH_CALL = re.compile(r"\b(?:clamp|min|max)\s*\(", re.IGNORECASE)
IMPORTANT = re.compile(r"!\s*important", re.IGNORECASE)

# Stylesheets.
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
FONT_SIZE_DECL = re.compile(r"(?<![\w-])font-size\s*:\s*([^;{}]+)", re.IGNORECASE)
CUSTOM_DECL = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+)")
MEDIA_PRELUDE = re.compile(r"@media\b(.*)", re.IGNORECASE | re.DOTALL)
PRINT_TYPE = re.compile(r"\bprint\b", re.IGNORECASE)
# A combinator, a pseudo-class, a pseudo-element and an attribute selector are all
# out of reach (ban-list.md, "Out of reach"), so a selector carrying one is skipped.
UNREADABLE_SELECTOR = re.compile(r"[:\[\]*,>+~]")
COMPOUND = re.compile(r"^(?P<tag>[A-Za-z][\w-]*)?(?P<rest>(?:[#.][\w.-]*)*)$")
ROOT_SELECTORS = {"html", ":root"}
THEME_NAMES = ("theme.css", "tokens.css")
LINK_OR_STYLE = re.compile(r"<link\b[^<>]*>|<style\b[^<>]*>.*?</style>",
                           re.DOTALL | re.IGNORECASE)
STYLE_BODY = re.compile(r"<style\b[^<>]*>(.*?)</style>", re.DOTALL | re.IGNORECASE)
REL_STYLESHEET = re.compile(r"\brel\s*=\s*[\"']stylesheet[\"']", re.IGNORECASE)
HREF = re.compile(r"\bhref\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)

# Markup.
HIDDEN_TAGS = {"script", "style", "template", "noscript", "title"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
             "meta", "param", "source", "track", "wbr"}
ATTR_CLASS = re.compile(r"\bclass(?:Name)?\s*=\s*[\"']([^\"']*)[\"']")
ATTR_ID = re.compile(r"\bid\s*=\s*[\"']([^\"']*)[\"']")
STYLE_SIZE = re.compile(r"(?<![\w-])font-size\s*:\s*([^;\"'}]+)", re.IGNORECASE)
JSX_SIZE = re.compile(r"\bfontSize\s*:\s*[\"']?([^,}\"']+)[\"']?")
SVG_SIZE = re.compile(r"(?<![\w-])font-size\s*=\s*[\"']?([\w.%-]+)[\"']?", re.IGNORECASE)
# A variant prefix - md:text-xs, hover:text-lg - is not read: the size it sets is
# conditional, and the unprefixed class on the same element is the one that always lands.
TW_SIZE = re.compile(r"\btext-(xs|sm|base|lg|xl|[2-9]xl)\b")
TW_ARBITRARY_SIZE = re.compile(r"\btext-\[(\d*\.?\d+)(px|rem|pt)\]")
# A JSX expression standing alone is code, not text.
JSX_ONLY = re.compile(r"^\{[^{}]*\}$", re.DOTALL)
HAS_RUN = re.compile(r"[0-9A-Za-z぀-ヿ一-鿿]")

# --- ST8: placeholder filler ----------------------------------------------

ST8 = re.compile(
    r"説明テキスト|ダミーテキスト|サンプルテキスト|テキストが入ります|ここにテキスト|"
    r"lorem ipsum|description goes here|placeholder text|^\s*TODO[:：]",
    re.IGNORECASE,
)

# --- ST9: a note defending the method ------------------------------------

ST9_JA_METHOD = re.compile(
    r"検定|仮説|p値|有意|偽陽性|信頼区間|記述統計|標準誤差|パラメータ|パラメーター|補正|調整|推定|"
    r"集計|標本|サンプル|ベンチマーク|閾値|しきい値|最適化|統計"
)
ST9_JA_NEGATION = re.compile(r"[てで]いない|[てで]いません|[てで]いなかった|ではない|ではなく|ではありません|しない|しません|せず")
ST9_EN_METHOD = re.compile(
    r"\b(?:tests?|tested|hypothesis|p-values?|significan\w*|false positives?|confidence intervals?|"
    r"parameters?|tuned|fitted|adjusted|optimi[sz]ed|samples?|benchmarks?|models?|statistics?)\b",
    re.IGNORECASE,
)
ST9_EN_NEGATION = re.compile(
    r"\b(?:not|never|without|un(?:tested|adjusted|tuned|fitted))\b|n't\b|"
    r"\bno\s+(?:significance|tests?|adjustments?|corrections?|hypothesis)\b",
    re.IGNORECASE,
)
# Test talk explains a statistic; a column heading only names it.
ST9_TEST_TALK = re.compile(
    r"検定|仮説|p値|偽陽性|信頼区間|記述統計|有意水準|帰無|"
    r"\b(?:hypothesis|p-values?|false positives?|confidence intervals?|null hypothesis|descriptive statistics?)\b",
    re.IGNORECASE,
)
ST9_TEST_TALK_MIN = 10

# --- extraction -----------------------------------------------------------

PROP_TEXT = re.compile(
    r"\b(?P<name>label|placeholder|description|helperText|helpText|hint|title|aria-label|"
    r"alt|caption|subtitle|legend|tooltip)\s*=\s*\{?\s*[\"'](?P<text>[^\"'{}]+)[\"']",
    re.IGNORECASE,
)
TEXT_NODE = re.compile(r">(?P<text>[^<>{}]+)<")
HAS_WORD = re.compile(r"[぀-ヿ一-鿿A-Za-z]")

FIX = {
    "ST1": "delete it; the screen is used, not read about",
    "ST2": "delete the positional phrase; copy never describes the layout",
    "ST3": "delete it, or replace it with the data or the action it stands in front of",
    "ST4": "delete it, or replace it with the format, the limit or the consequence",
    "ST5": "delete it, or make the encoding unambiguous instead",
    "ST6": "move the sequence into a dismissible first-run surface, or drop it",
    "ST7": "raise the size to 14px (12px for a Latin-only run of at most 24 characters), "
           "or delete the run",
    "ST8": "replace it with real content, or leave the slot empty and ask the user",
    "ST9": "move the definition into a tooltip or a help page; a kept data-fact note is restated in the positive",
    "ST10": "raise the declared size to 14px (12px only where every element the rule "
            "reaches is a Latin-only run of at most 24 characters), or delete the rule",
}


class Report:
    def __init__(self, checks=None):
        self.findings = []
        self.checks = set(checks) if checks else None

    def add(self, severity, check_id, path, line, text, message):
        if self.checks is not None and check_id not in self.checks:
            return
        self.findings.append({
            "severity": severity,
            "id": check_id,
            "file": str(path),
            "line": line,
            "text": collapse(text)[:120],
            "message": message,
            "fix": FIX[check_id],
        })

    @property
    def errors(self):
        return [f for f in self.findings if f["severity"] == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f["severity"] == "WARN"]


class Seg:
    """One string a user will see, with where it came from."""

    def __init__(self, text, line, start, source):
        self.text = text.strip()
        self.line = line
        self.start = start
        self.source = source  # "text" or a prop name, lowercased


def collapse(text):
    return re.sub(r"\s+", " ", text).strip()


def visible_length(text):
    return len(re.sub(r"\s+", "", text))


def blank(match):
    """Keep the newlines so line numbers stay put."""
    return re.sub(r"[^\n]", " ", match.group(0))


def strip_hidden(text):
    text = re.sub(r"<script\b.*?</script>", blank, text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style\b.*?</style>", blank, text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<(code|pre)\b.*?</\1>", blank, text, flags=re.DOTALL | re.IGNORECASE)
    # Lower case only: a JSX <Title> component is visible text.
    text = re.sub(r"<(noscript|title)(?=[\s>]).*?</\1\s*>", blank, text, flags=re.DOTALL)
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.DOTALL)
    # Not a comment after a scheme, a word, or inside a quoted attribute value:
    # href="//cdn.example.com" must survive.
    text = re.sub(r"(?m)(?<![:\w\"'=])//[^\n]*", blank, text)
    return text


def line_of(body, index):
    return body.count("\n", 0, index) + 1


def collect_files(root):
    root = Path(root)
    if root.is_file():
        return [root]
    found = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCOPE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if any(p in path.name for p in SKIP_PATTERNS):
            continue
        found.append(path)
    return found


def find_tokens(root):
    """The nearest tokens.json at or above the scanned path, as check_copy.py finds it."""
    base = Path(root).resolve()
    if not base.is_dir():
        base = base.parent
    for _ in range(4):
        candidate = base / "tokens.json"
        if candidate.is_file():
            return candidate
        if base.parent == base:
            break
        base = base.parent
    return None


def surface_of(root):
    """meta.surface from the nearest tokens.json, or None."""
    path = find_tokens(root)
    if not path:
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    surface = (doc.get("meta") or {}).get("surface")
    return surface.lower() if isinstance(surface, str) else None


def is_landing(path):
    parts = {part.lower() for part in Path(path).parts}
    if parts & LANDING_DIRS:
        return True
    name = Path(path).name.lower()
    return any(hint in name for hint in LANDING_NAMES)


def segments(body):
    found = []
    for match in TEXT_NODE.finditer(body):
        text = match.group("text")
        if not HAS_WORD.search(text) or len(text.strip()) < 2:
            continue
        found.append(Seg(text, line_of(body, match.start()), match.start(), "text"))
    for match in PROP_TEXT.finditer(body):
        text = match.group("text")
        if not HAS_WORD.search(text):
            continue
        found.append(Seg(text, line_of(body, match.start()),
                         match.start(), match.group("name").lower()))
    return found


def bigrams(text):
    packed = re.sub(r"\s+", "", text)
    return {packed[i:i + 2] for i in range(len(packed) - 1)} or {packed}


def overlap(label, helper):
    """How much of the label survives inside the helper text."""
    left, right = bigrams(label), bigrams(helper)
    if not left:
        return 0.0
    return len(left & right) / len(left)


def defends_method(text):
    """ST9 - a method word next to a negation, or test talk long enough to be a sentence."""
    negated = (ST9_JA_METHOD.search(text) and ST9_JA_NEGATION.search(text)) or \
        (ST9_EN_METHOD.search(text) and ST9_EN_NEGATION.search(text))
    return bool(negated) or (visible_length(text) > ST9_TEST_TALK_MIN
                             and bool(ST9_TEST_TALK.search(text)))


# --- ST7 / ST10: sizes -----------------------------------------------------

def resolve_size(value, parent, root, custom, depth=0):
    """A font-size value in px, or None where a browser is needed to settle it."""
    if value is None or depth > 4:
        return None
    value = IMPORTANT.sub("", value).strip().lower()
    if not value:
        return None
    if value == "inherit":
        # `inherit` takes the parent's size, as the keyword means.
        return parent
    if value in CSS_KEYWORDS:
        return CSS_KEYWORDS[value]
    if value in CSS_RELATIVE:
        return parent * CSS_RELATIVE[value]
    match = VAR_CALL.search(value)
    if match:
        name, fallback = match.group(1), match.group(2)
        if name in custom:
            return resolve_size(custom[name], parent, root, custom, depth + 1)
        # A var() fallback is used when the property is undefined, as a browser does.
        return resolve_size(fallback, parent, root, custom, depth + 1) if fallback else None
    if MATH_CALL.search(value):
        literals = [float(found) for found in PX_LITERAL.findall(value)]
        return min(literals) if literals else None
    match = LENGTH.match(value)
    if not match:
        return None
    number, unit = float(match.group(1)), (match.group(2) or "px").lower()
    if unit in ABSOLUTE_UNITS:
        return number * ABSOLUTE_UNITS[unit]
    if unit == "rem":
        return number * root
    if unit == "em":
        return number * parent
    return number * parent / 100.0  # %


def literal_size(value):
    """What ST10 judges: px, rem against 16px, pt, and the keywords. Else None."""
    value = IMPORTANT.sub("", value).strip().lower()
    if value in CSS_KEYWORDS:
        return CSS_KEYWORDS[value]
    match = LENGTH.match(value)
    if not match:
        return None
    number, unit = float(match.group(1)), (match.group(2) or "px").lower()
    if unit in ABSOLUTE_UNITS:
        return number * ABSOLUTE_UNITS[unit]
    return number * ST10_ROOT_PX if unit == "rem" else None


def px_of(value):
    """A plain px measurement, as a cdp.js dump writes it."""
    match = LENGTH.match(str(value or "").strip().lower())
    if not match or (match.group(2) or "px").lower() != "px":
        return None
    return float(match.group(1))


class Rule:
    """One selector's font-size, with what the cascade sorts it by."""

    __slots__ = ("selector", "chain", "value", "important", "specificity", "order")

    def __init__(self, selector, chain, value, important, order):
        self.selector = selector
        self.chain = chain
        self.value = value
        self.important = important
        self.specificity = (sum(len(ids) for _, ids, _ in chain),
                            sum(len(cls) for _, _, cls in chain),
                            sum(1 for tag, _, _ in chain if tag))
        self.order = order

    @property
    def rank(self):
        return (self.important, self.specificity, self.order)


def parse_selector(selector):
    """A descendant chain of (tag, ids, classes), or None where the resolver stops.

    A selector the resolver cannot read matches nothing rather than being guessed at:
    reading `.a > .b` as a descendant chain reports a grandchild the rule never
    reaches. ST10 and --dom are what see those rules.
    """
    if UNREADABLE_SELECTOR.search(selector):
        return None
    chain = []
    for part in selector.split():
        match = COMPOUND.match(part)
        if not match:
            return None
        rest = match.group("rest") or ""
        chain.append(((match.group("tag") or "").lower(),
                      tuple(found[1:] for found in re.findall(r"#[\w-]+", rest)),
                      frozenset(found[1:] for found in re.findall(r"\.[\w-]+", rest))))
    return chain or None


def compound_matches(compound, frame):
    tag, ids, classes = compound
    if tag and tag != frame["tag"]:
        return False
    if any(one != frame["id"] for one in ids):
        return False
    return classes <= frame["classes"]


def selector_matches(chain, stack):
    """The last compound matches the element, the rest match ancestors in order."""
    if not compound_matches(chain[-1], stack[-1]):
        return False
    need = list(chain[:-1])
    for frame in stack[:-1]:
        if need and compound_matches(need[0], frame):
            need.pop(0)
    return not need


def print_only(prelude):
    """@media print and nothing else. `@media screen, print` still lands on a screen."""
    match = MEDIA_PRELUDE.match(prelude.strip())
    if not match:
        return False
    queries = match.group(1).split(",")
    return len(queries) == 1 and bool(PRINT_TYPE.search(queries[0]))


def css_blocks(text):
    """(prelude stack, declaration text, its offset) for every block in a stylesheet."""
    stack, out, start, index = [], [], 0, 0
    while index < len(text):
        char = text[index]
        if char == "{":
            stack.append(text[start:index].strip())
            index += 1
            start = index
        elif char == "}":
            out.append((tuple(stack), text[start:index], start))
            if stack:
                stack.pop()
            index += 1
            start = index
        else:
            index += 1
    return out


class Cascade:
    """The stylesheets behind one file: its rules, its custom properties, its root."""

    def __init__(self):
        self.rules = []
        self.custom = {}
        self.root_px = 16.0
        self.order = 0

    def read(self, text):
        text = CSS_COMMENT.sub(blank, text)
        for preludes, decls, offset in css_blocks(text):
            if any(print_only(prelude) for prelude in preludes):
                continue
            selector = preludes[-1] if preludes else ""
            if selector.startswith("@"):
                selector = ""
            if selector in ROOT_SELECTORS or any(p.lower().startswith("@theme")
                                                 for p in preludes):
                for name, value in CUSTOM_DECL.findall(decls):
                    self.custom.setdefault(name, value.strip())
            for match in FONT_SIZE_DECL.finditer(decls):
                self.add_rule(selector, match.group(1).strip())
        return self

    def add_rule(self, selector, value):
        for one in selector.split(","):
            one = one.strip()
            if one in ROOT_SELECTORS:
                plain = LENGTH.match(IMPORTANT.sub("", value).strip().lower())
                if plain and (plain.group(2) or "px").lower() == "px":
                    self.root_px = float(plain.group(1))
            chain = parse_selector(one) if one else None
            if chain:
                self.rules.append(Rule(one, chain, value, bool(IMPORTANT.search(value)),
                                       self.order))
                self.order += 1

    def best(self, stack):
        """The winning rule for the element on top of the stack, or None."""
        matched = [rule for rule in self.rules if selector_matches(rule.chain, stack)]
        return max(matched, key=lambda rule: rule.rank) if matched else None


def find_theme(root):
    """theme.css or tokens.css beneath the path, then up to four directories above."""
    base = Path(root).resolve()
    if base.is_file():
        base = base.parent
    for parent, dirs, names in os.walk(base):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        for name in THEME_NAMES:
            if name in names:
                return Path(parent) / name
    for _ in range(4):
        if base.parent == base:
            break
        base = base.parent
        for name in THEME_NAMES:
            if (base / name).is_file():
                return base / name
    return None


def read_css(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        # A stylesheet that will not open leaves its elements inheriting, by design.
        return ""


def stylesheets(path, raw, theme, extra_css):
    """(text, line offset, is a <style> block in this file) in cascade order."""
    sheets, seen = [], set()
    for match in LINK_OR_STYLE.finditer(raw):
        chunk = match.group(0)
        if chunk[:6].lower() == "<style":
            body = STYLE_BODY.match(chunk)
            if body:
                sheets.append((body.group(1),
                               line_of(raw, match.start() + body.start(1)) - 1, True))
            continue
        if not REL_STYLESHEET.search(chunk):
            continue
        href = HREF.search(chunk)
        if not href or re.match(r"[a-z]+:|//", href.group(1), re.IGNORECASE):
            continue
        target = (path.parent / href.group(1).split("?")[0].split("#")[0])
        # The file scope excludes *.min.*, so the cascade excludes a minified
        # vendor sheet too.
        if not target.is_file() or any(p in target.name for p in SKIP_PATTERNS):
            continue
        resolved = target.resolve()
        if resolved not in seen:
            seen.add(resolved)
            sheets.append((read_css(resolved), 0, False))
    for extra in ([theme] if theme else []) + list(extra_css):
        resolved = Path(extra).resolve()
        if resolved.is_file() and resolved not in seen:
            seen.add(resolved)
            sheets.append((read_css(resolved), 0, False))
    return sheets


class SizeWalker(HTMLParser):
    """Walks markup with a stack of computed sizes and hands every run to a callback."""

    def __init__(self, cascade, on_run, vue=False):
        super().__init__(convert_charrefs=True)
        self.cascade = cascade
        self.on_run = on_run
        self.vue = vue
        self.root = {"tag": "", "id": "", "classes": frozenset(), "class_list": [],
                     "hidden": False, "size": cascade.root_px,
                     "source": "the root size", "owner": None}
        self.stack = []

    # -- the element's own size -------------------------------------------

    def resolve(self, value):
        parent = self.stack[-2] if len(self.stack) > 1 else self.root
        return resolve_size(value, parent["size"], self.cascade.root_px,
                            self.cascade.custom)

    def tailwind(self, frame):
        """(size, source) from the last text-* size class on the element, or None.

        Last in source order, because that is the class a stylesheet cannot reorder
        away: `text-xs text-lg` renders at the size Tailwind's own sheet puts later,
        and the author's last word is the readable guess.
        """
        for name in reversed(frame["class_list"]):
            arbitrary = TW_ARBITRARY_SIZE.fullmatch(name)
            if arbitrary:
                size = self.resolve(arbitrary.group(1) + arbitrary.group(2))
                if size is not None:
                    return size, f"the class {name}"
            step = TW_SIZE.fullmatch(name)
            if step:
                declared = self.cascade.custom.get(f"--text-{step.group(1)}")
                size = self.resolve(declared) if declared else None
                return (size if size is not None else TW_SCALE[step.group(1)],
                        f"the class {name}")
        return None

    def declared(self, raw, frame):
        """(size, source) from this element's own declarations, or (None, None).

        Precedence, as ban-list.md sets it: an inline !important, a stylesheet
        !important rule, the inline style, the SVG presentation attribute, a Tailwind
        class, then the matching rules.
        """
        inline = STYLE_SIZE.search(raw) or JSX_SIZE.search(raw)
        inline_size = self.resolve(inline.group(1)) if inline else None
        rule = self.cascade.best(self.stack)
        rule_size = self.resolve(rule.value) if rule else None

        if inline_size is not None and IMPORTANT.search(inline.group(1)):
            return inline_size, "inline !important"
        if rule_size is not None and rule.important:
            return rule_size, rule.selector
        if inline_size is not None:
            return inline_size, "inline"
        svg = SVG_SIZE.search(raw)
        if svg:
            size = self.resolve(svg.group(1))
            if size is not None:
                return size, "the font-size attribute"
        utility = self.tailwind(frame)
        if utility:
            return utility
        if rule_size is not None:
            return rule_size, rule.selector
        return None, None

    # -- the stack ---------------------------------------------------------

    def hides(self, tag, raw):
        """A Vue <template> renders at any depth, and so does a JSX component such as <Title>."""
        if raw[1:2].isupper() or (tag == "template" and self.vue):
            return False
        return tag in HIDDEN_TAGS

    def push(self, tag, raw):
        parent = self.stack[-1] if self.stack else self.root
        names = []
        for match in ATTR_CLASS.finditer(raw):
            names.extend(match.group(1).split())
        ident = ATTR_ID.search(raw)
        frame = {"tag": tag.lower(), "id": ident.group(1) if ident else "",
                 "classes": frozenset(names), "class_list": names,
                 "hidden": parent["hidden"] or self.hides(tag.lower(), raw)}
        self.stack.append(frame)
        size, source = self.declared(raw, frame)
        if size is None:
            frame["size"] = parent["size"]
            frame["owner"] = parent["owner"]
            frame["source"] = (f"inherited from {frame['owner']}" if frame["owner"]
                               else parent["source"])
        else:
            frame["size"] = size
            frame["owner"] = describe_element(frame)
            frame["source"] = source
        return frame

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text() or ""
        self.push(tag, raw)
        if tag.lower() in VOID_TAGS or raw.rstrip().endswith("/>"):
            self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        self.push(tag, self.get_starttag_text() or "")
        self.stack.pop()

    def handle_endtag(self, tag):
        tag = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        frame = self.stack[-1] if self.stack else self.root
        text = data.strip()
        if frame["hidden"] or not text or JSX_ONLY.match(text) or not HAS_RUN.search(text):
            return
        self.on_run(collapse(text), frame, self.getpos()[0])


def describe_element(frame):
    name = frame["tag"] or "html"
    if frame["classes"]:
        name += "." + sorted(frame["classes"])[0]
    elif frame["id"]:
        name += "#" + frame["id"]
    return f"<{name}>"


def report_small_run(rep, path, line, text, size, source):
    """The one ST7 rule, shared by the markup walker and --dom."""
    if size >= MIN_PX:
        return
    length = visible_length(text)
    if not CJK.search(text) and length <= LATIN_MAX_RUN and size >= LATIN_MIN_PX:
        return
    rep.add("ERROR", "ST7", path, line, text,
            f"{length} characters at {size:g}px, from {source}; "
            f"the minimum is {MIN_PX:g}px, and {LATIN_MIN_PX:g}px only for a Latin-only "
            f"run of at most {LATIN_MAX_RUN} characters")


# --- checks ---------------------------------------------------------------

def check_file(path, raw, rep, surface=None, theme=None, extra_css=()):
    body = strip_hidden(raw)
    segs = segments(body)
    landing = surface in LANDING_SURFACES if surface else is_landing(path)

    for seg in segs:
        described = False

        # ST1 - the screen describing itself.
        if any(pattern.search(seg.text) for pattern in ST1):
            described = True
            rep.add("ERROR", "ST1", path, seg.line, seg.text,
                    "the screen introduces itself to the reader already on it")

        # ST2 - an instruction that points at the layout.
        if (JA_POSITION.search(seg.text) and JA_INSTRUCTION.search(seg.text)) or \
                any(pattern.search(seg.text) for pattern in EN_POSITION):
            rep.add("ERROR", "ST2", path, seg.line, seg.text,
                    "the copy points at where another element sits")

        # ST3 - the capability explainer.
        if not described and not landing and seg.source not in TOOLTIP_SOURCES \
                and visible_length(seg.text) <= ST3_MAX_CHARS \
                and seg.text.count("。") <= 1 and seg.text.count(".") <= 1 \
                and (ST3_JA.search(seg.text) or ST3_EN.search(seg.text)) \
                and not EMPTY_STATE.search(body[max(0, seg.start - 200):seg.start + 200]):
            rep.add("WARN", "ST3", path, seg.line, seg.text,
                    "a caption stating what the screen can do stands where the data belongs")

        # ST5 - a legend for the self-evident.
        if ST5_JA.search(seg.text) or ST5_EN.search(seg.text):
            rep.add("WARN", "ST5", path, seg.line, seg.text,
                    "a legend explains an encoding the element already carries")

        # ST9 - a note defending the method.
        if defends_method(seg.text) \
                and not EMPTY_STATE.search(body[max(0, seg.start - 200):seg.start + 200]):
            rep.add("WARN", "ST9", path, seg.line, seg.text,
                    "the note says what was not done, or explains the test; the screen does not defend its numbers")

        # ST8 - placeholder filler.
        if ST8.search(seg.text):
            rep.add("ERROR", "ST8", path, seg.line, seg.text, "filler text reached the screen")

    check_helper_text(path, body, segs, rep)
    check_tutorial(path, body, segs, rep)

    sheets = stylesheets(path, raw, theme, extra_css)
    cascade = Cascade()
    for text, _, _ in sheets:
        cascade.read(text)
    check_size(path, body, rep, cascade)
    for text, offset, own in sheets:
        if own:
            check_declared_sizes(path, text, rep, offset)


def check_helper_text(path, body, segs, rep):
    """ST4 - helper text restating its label."""
    labels = [(match.start(), match.group("text").strip())
              for match in LABEL_TAG.finditer(body)]
    labels += [(seg.start, seg.text) for seg in segs if seg.source in LABEL_PROPS]

    helpers = [(seg.start, seg.line, seg.text) for seg in segs if seg.source in HELPER_PROPS]
    helpers += [(match.start(), line_of(body, match.start()), match.group("text").strip())
                for match in HELPER_CLASS.finditer(body)]

    for start, line, text in helpers:
        if CONSTRAINT.search(text):
            continue
        near = [(abs(start - pos), label) for pos, label in labels
                if abs(start - pos) <= ST4_WINDOW]
        if not near:
            continue
        _, label = min(near, key=lambda pair: pair[0])
        if overlap(label, text) >= ST4_OVERLAP:
            rep.add("WARN", "ST4", path, line, text,
                    f"helper text restates the label {label!r} and carries no constraint")


def check_tutorial(path, body, segs, rep):
    """ST6 - inline tutorial prose, judged over the whole file."""
    if WIZARD.search(body):
        return
    visible = " ".join(seg.text for seg in segs)
    japanese = ST6_FIRST.search(visible) and ST6_IMPERATIVE.search(visible) \
        and ST6_NEXT.search(visible)
    english = ST6_EN.search(visible) and ST6_EN_NEXT.search(visible)
    if not (japanese or english):
        return
    hit = next((seg for seg in segs if ST6_FIRST.search(seg.text) or ST6_EN.search(seg.text)), None)
    rep.add("WARN", "ST6", path, hit.line if hit else 1, hit.text if hit else "",
            "a step-by-step sequence is baked into the layout, outside any wizard")


def check_size(path, body, rep, cascade):
    """ST7 - every visible run at the size the cascade actually gives it."""
    walker = SizeWalker(cascade, lambda text, frame, line:
                        report_small_run(rep, path, line, text, frame["size"],
                                         frame["source"]),
                        vue=Path(path).suffix.lower() == ".vue")
    walker.feed(body)
    walker.close()


def check_declared_sizes(path, css, rep, line_offset=0):
    """ST10 - a size below the minimum written into a stylesheet, wherever it lands.

    Runs over a .css file the scan collected and over a <style> block in a scanned
    file. A sheet reached only through a <link> is reported when it is itself scanned,
    so one declaration is never reported once per page that links it.
    """
    css = CSS_COMMENT.sub(blank, css)
    for preludes, decls, offset in css_blocks(css):
        if any(print_only(prelude) for prelude in preludes):
            continue
        selector = preludes[-1] if preludes else ""
        if not selector or selector.startswith("@"):
            continue
        for match in FONT_SIZE_DECL.finditer(decls):
            value = match.group(1).strip()
            size = literal_size(value)
            if size is None or size >= MIN_PX:
                continue
            line = line_offset + line_of(css, offset + match.start())
            declaration = f"{selector} {{ font-size: {value} }}"
            if size < LATIN_MIN_PX:
                rep.add("ERROR", "ST10", path, line, declaration,
                        f"{selector} declares {size:g}px, which no screen has a reader for")
            else:
                rep.add("WARN", "ST10", path, line, declaration,
                        f"{selector} declares {size:g}px, which holds only where every "
                        f"element it reaches is a Latin-only run of at most "
                        f"{LATIN_MAX_RUN} characters")


def check_dump(path, rep):
    """ST7 over a cdp.js dump: the size the browser actually gave each run."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    for index, entry in enumerate(doc.get("text") or [], start=1):
        text = collapse(entry.get("text") or "")
        rect = entry.get("rect") or {}
        size = px_of(entry.get("fontSize"))
        if not text or not rect.get("w") or not rect.get("h") or size is None:
            continue
        # A dump has no lines, so the finding points at the entry that carried the run.
        report_small_run(rep, path, index, text, size, "rendered")


def run(target, surface=None, extra_css=(), checks=None, dump=None):
    rep = Report(checks)
    if dump:
        check_dump(dump, rep)
        return rep, [Path(dump)]
    files = collect_files(target)
    surface = surface or surface_of(target)
    theme = find_theme(target)
    extra_css = [Path(one) for one in extra_css]
    for path in files:
        raw = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() in STYLESHEET_SUFFIXES:
            check_declared_sizes(path, raw, rep)
            continue
        check_file(path, raw, rep, surface, theme, extra_css)
    return rep, files


def main():
    parser = argparse.ArgumentParser(
        description="Run shippable-text existence checks ST1-ST10.")
    parser.add_argument("path", nargs="?", help="file or directory to check")
    parser.add_argument("--surface", choices=["lp", "app"],
                        help="override meta.surface from tokens.json")
    parser.add_argument("--css", action="append", default=[], metavar="FILE.CSS",
                        help="add a stylesheet to the cascade ST7 resolves against")
    parser.add_argument("--checks", metavar="ID,ID",
                        help="run only these check IDs; any other ID is skipped")
    parser.add_argument("--dom", nargs="?", const=True, metavar="DUMP.JSON",
                        help="run ST7 over a cdp.js dump instead of over markup")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    dump = args.dom if isinstance(args.dom, str) else (args.path if args.dom else None)
    target = dump or args.path
    if not target:
        parser.error("a path is required")
    if not Path(target).exists():
        print(f"FAIL: no such path: {target}", file=sys.stderr)
        return 1

    checks = {one.strip().upper() for one in args.checks.split(",")} if args.checks else None
    rep, files = run(args.path, args.surface, args.css, checks, dump)

    # A directory that collected nothing is a wrong path or a wrong scope, not a pass.
    if not files and Path(target).is_dir():
        print(f"FAIL: no files in scope: {target}", file=sys.stderr)
        return 2
    status = "FAIL" if rep.errors else "PASS"

    if args.json:
        print(json.dumps({
            "status": status,
            "files_checked": len(files),
            "error_count": len(rep.errors),
            "warning_count": len(rep.warnings),
            "findings": rep.findings,
        }, indent=2, ensure_ascii=False))
    else:
        for item in rep.findings:
            print(f"{item['severity']:<5} [{item['id']}] {item['file']}:{item['line']}: "
                  f"{item['message']}")
            print(f"      {item['text']!r} -> {item['fix']}")
        print(f"{status}: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s) "
              f"across {len(files)} file(s)")

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
