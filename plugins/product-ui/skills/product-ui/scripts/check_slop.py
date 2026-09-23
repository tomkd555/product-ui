#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) slop checks over generated markup and styles.

Standard library only. Runs checks S1-S10 against the files an implementation step
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
import json
import os
import re
import sys

SCOPE_SUFFIXES = (".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".css")

SKIP_DIRS = {"node_modules", "dist", "build", ".next", ".git", ".svelte-kit", "out"}
SKIP_NAMES = {"theme.css", "tokens.css"}
SKIP_PATTERNS = (".min.css", ".test.", ".spec.")

HEX = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
FUNC_COLOR = re.compile(r"\b(?:rgba?|hsla?)\([^)]*\)", re.IGNORECASE)
OKLCH_CALL = re.compile(r"\boklch\([^)]*\)", re.IGNORECASE)

FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.IGNORECASE)
FONT_ARBITRARY = re.compile(r"\bfont-\[([^\]]+)\]")

FORBIDDEN_FAMILIES = {
    "inter", "roboto", "open sans", "lato", "arial", "helvetica",
    "system-ui", "-apple-system", "space grotesk", "poppins", "montserrat",
}
MONOSPACE_HINTS = ("mono", "consolas", "menlo", "courier", "fira code", "source code")

GRADIENT = re.compile(r"\b(?:linear|radial|conic)-gradient\([^;{}]*\)", re.IGNORECASE)
TW_GRADIENT_STOP = re.compile(r"\b(?:from|via|to)-(\w+)-\d{2,3}\b")
BLUE_WORDS = {"blue", "indigo", "sky", "cyan"}
PURPLE_WORDS = {"purple", "violet", "fuchsia"}

RADIUS_DECL = re.compile(r"border-radius\s*:\s*([^;}\n]+)", re.IGNORECASE)
TW_ROUNDED = re.compile(r"\brounded(?:-(?:t|b|l|r|tl|tr|bl|br|s|e|ss|se|es|ee))?-([\w.\[\]/%-]+)\b")
NEUTRAL_RADII = {"0", "0px", "none", "9999px", "full", "50%"}

SHADOW_DECL = re.compile(r"box-shadow\s*:\s*([^;}\n]+)", re.IGNORECASE)
SHADOW_ALPHA = re.compile(r"(?:/\s*(\d*\.?\d+)\s*\)|,\s*(\d*\.?\d+)\s*\))")

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U0001F1E6-\U0001F1FF☀-➿⬀-⯿️←-⇿]+"
)
EM_DASH = "—"

FORM_TAG = re.compile(r"<form\b", re.IGNORECASE)
FORM_LIB = re.compile(r"\b(?:useForm|react-hook-form|Formik|zodResolver)\b")
STATE_SIGNALS = (
    "required", "aria-required", "aria-invalid", "aria-describedby",
    "pattern=", 'role="alert"', "role='alert'", "errors.", "errorMessage",
    "helperText", "FormMessage",
)
SEARCH_FORM = re.compile(r'role=["\']search["\']|type=["\']search["\']', re.IGNORECASE)


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
        if path == "(project)":
            if check_id in self.run_ids:
                return
        elif check_id in self.by_file or check_id in self.by_line.get(line, ()):
            return
        self.findings.append({
            "severity": severity,
            "id": check_id,
            "file": path,
            "line": line,
            "message": message,
        })

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
    if not theme_path or not os.path.isfile(theme_path):
        return set()
    with open(theme_path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    known = set()
    for pattern in (HEX, FUNC_COLOR, OKLCH_CALL):
        for match in pattern.finditer(text):
            known.add(normalize_color(match.group(0)))
    return known


def normalize_color(value):
    return re.sub(r"\s+", "", value).lower()


def check_file(path, text, known_colors, rep, totals):
    rep.begin_file(text, path)
    body = strip_comments(text)
    rel = path

    # S1 / S5 - colour literals outside the token set.
    for pattern in (HEX, FUNC_COLOR):
        for match in pattern.finditer(body):
            raw = match.group(0)
            if pattern is HEX and is_fragment_reference(body, match.start()):
                continue
            norm = normalize_color(raw)
            if norm in known_colors:
                continue
            totals["off_token_colors"].add(norm)
            rep.add("ERROR", "S1", rel, line_of(body, match.start()),
                    f"{raw} is not declared in the theme; use a token variable")

    # S2 / S4 - font families.
    for match in FONT_FAMILY.finditer(body):
        stack = [part.strip().strip("'\"") for part in match.group(1).split(",")]
        if not stack:
            continue
        leading = stack[0].strip().strip("'\"")
        record_family(leading, rel, line_of(body, match.start()), rep, totals)
    for match in FONT_ARBITRARY.finditer(body):
        leading = match.group(1).replace("_", " ").split(",")[0].strip().strip("'\"")
        record_family(leading, rel, line_of(body, match.start()), rep, totals)

    # S3 - blue-to-purple gradients.
    for match in GRADIENT.finditer(body):
        if gradient_is_blue_purple(match.group(0)):
            rep.add("ERROR", "S3", rel, line_of(body, match.start()),
                    "gradient runs from a blue family to a purple family")
    stop_matches = list(TW_GRADIENT_STOP.finditer(body))
    stops = {m.group(1).lower() for m in stop_matches}
    if stops & BLUE_WORDS and stops & PURPLE_WORDS:
        rep.add("ERROR", "S3", rel, line_of(body, stop_matches[0].start()),
                "gradient utility classes mix a blue family with a purple family")

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
        for alpha in SHADOW_ALPHA.finditer(match.group(1)):
            value = alpha.group(1) or alpha.group(2)
            totals["shadow_alphas"].setdefault(value, 0)
            totals["shadow_alphas"][value] += 1

    # S8 - emoji standing in for icons.
    for line_no, line in enumerate(body.split("\n"), start=1):
        if "aria-hidden" in line:
            continue
        for match in re.finditer(r">\s*(" + EMOJI.pattern + r")\s*<", line):
            rep.add("WARN", "S8", rel, line_no,
                    f"{match.group(1)} sits alone in an element; use an icon from a set")
        for match in re.finditer(r"<(?:li|button|a)\b[^>]*>\s*(" + EMOJI.pattern + r")", line):
            rep.add("WARN", "S8", rel, line_no,
                    f"{match.group(1)} leads the content of an interactive element")

    # S9 - em-dashes in visible text.
    visible = re.sub(r"<(code|pre)\b.*?</\1>", " ", body, flags=re.DOTALL | re.IGNORECASE)
    visible = re.sub(r"=\s*[\"'][^\"']*[\"']", " ", visible)
    count = visible.count(EM_DASH)
    if count >= 3:
        rep.add("WARN", "S9", rel, 1, f"{count} em-dashes in visible text")

    # S10 - forms without state design.
    form = FORM_TAG.search(body) or FORM_LIB.search(body)
    if form:
        if not SEARCH_FORM.search(body) and not any(sig in body for sig in STATE_SIGNALS):
            rep.add("ERROR", "S10", rel, line_of(body, form.start()),
                    "form has no validation, error state or required marking")


def is_fragment_reference(text, index):
    """True for href="#id" and the like, where # opens a fragment reference."""
    window = text[max(0, index - 12):index]
    return bool(re.search(r"(?:href|id|xlink:href|url)\s*=?\s*[\"'(]?\s*$", window, re.IGNORECASE))


def hex_hue(value):
    """Hue angle in degrees for a hex colour, or None when it has no hue."""
    digits = value.lstrip("#")
    if len(digits) in (3, 4):
        digits = "".join(ch * 2 for ch in digits[:3])
    if len(digits) < 6:
        return None
    try:
        red, green, blue = (int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return None
    high, low = max(red, green, blue), min(red, green, blue)
    span = high - low
    if span == 0:
        return None
    if high == red:
        hue = ((green - blue) / span) % 6
    elif high == green:
        hue = (blue - red) / span + 2
    else:
        hue = (red - green) / span + 4
    return hue * 60


def gradient_is_blue_purple(fragment):
    lowered = fragment.lower()
    if any(word in lowered for word in BLUE_WORDS) and any(word in lowered for word in PURPLE_WORDS):
        return True

    hues = []
    for match in OKLCH_CALL.finditer(fragment):
        parts = re.findall(r"[-+]?\d*\.?\d+", match.group(0))
        if len(parts) >= 3:
            hues.append(float(parts[2]))
    for match in HEX.finditer(fragment):
        hue = hex_hue(match.group(0))
        if hue is not None:
            hues.append(hue)

    return sum(1 for hue in hues if 240 <= hue <= 300) >= 2


def record_family(family, path, line, rep, totals):
    lowered = family.strip().lower()
    if not lowered or lowered.startswith("var(") or lowered in {"inherit", "initial", "unset"}:
        return
    if any(hint in lowered for hint in MONOSPACE_HINTS):
        return
    totals["families"].add(lowered)
    if lowered in FORBIDDEN_FAMILIES:
        rep.add("ERROR", "S2", path, line,
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
        try:
            numeric = float(value)
        except ValueError:
            numeric = None
        if numeric is not None and 0.05 <= numeric <= 0.15 and count >= 3:
            rep.add("WARN", "S7", "(project)", 1,
                    f"every shadow uses alpha {value} across {count} declarations")


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

    files = collect_files(targets)
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        check_file(path, text, known, rep, totals)

    check_totals(rep, totals)
    return rep, files, known


def main():
    parser = argparse.ArgumentParser(description="Run product-ui slop checks S1-S10.")
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
