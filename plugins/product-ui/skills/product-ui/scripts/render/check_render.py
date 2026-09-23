#!/usr/bin/env python3
"""Measure what the rendered page's DOM dumps settle without judgement.

    python check_render.py <dump.json> [<dump.json> ...] [--console <txt> ...]
                           [--tokens tokens.json] --out findings.json [--text]

Reads the dumps cdp.js wrote (one per width, or per width and theme), and the console
files beside them, and writes one findings file in the auditors' shape, perspective
"P0 Measured", so the review lead merges it like any auditor's report. The design
auditors get the same file and judge what it cannot: overlap, alignment, images,
whether anything guides the eye, whether the copy is true.

Checks:

  R1  contrast below the WCAG threshold for the text's size (4.5:1, or 3:1 for text of
      24px and up, or 18.66px and up at weight 700 and up). CRITICAL under 2:1.
      Text inside a disabled control is exempt, as WCAG exempts inactive controls; so is
      text whose background no ancestor paints (`backgroundFallback`), because the white
      cdp.js reports there is nobody's choice. The count of those is in checked_scope.
  R2  a text colour or background outside the token set, when --tokens is given
      (color and color_dark, matched within 2/255 per sRGB channel)
  R3  horizontal overflow at a width
  R4  an element whose text is clipped
  R5  a control whose shorter side is under 24px; disabled controls and links inline in a
      sentence are exempt (WCAG 2.2 SC 2.5.8)
  R6  an input with no label; submit, button, reset, image and hidden inputs are exempt
  R7  text under the minimum size (CRITICAL): 14px, or 12px for a Latin-only run of at
      most 24 characters — the rule in product-ui's references/ban-list.md
  R8  heading hierarchy: not exactly one h1, or a skipped level
  R9  console: an uncaught exception (CRITICAL), an error (WARNING), a warning (NOTE)
  R10 a link with no destination (no href, `#`, or `javascript:`) — NOTE, because a mock
      has them by design; the brief says whether the screen is wired
  R11 the viewport the page reported differs from the width the file name asks for —
      CRITICAL, because every other measurement was then taken at the wrong width

The same defect measured at two widths, or in the light and the dark theme, is one
finding listing every label it held at; the element list and the count come from the
first capture that showed it. `rgb`, `rgba`, `hsl`, `hsla`, hex, `oklch`, `oklab` and
`color(srgb …)` are parsed — Chrome keeps oklch() as the computed value of a colour
declared in oklch() — and every other notation is listed under `out_of_scope_notes`
and skipped. Exit 0 once the file is written, 2 on unusable input.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

MIN_HIT = 24
# The text-size minimum from product-ui's references/ban-list.md.
MIN_TEXT_PX = 14.0
MIN_TEXT_LATIN_PX = 12.0
LATIN_SHORT_MAX = 24
CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
MAX_LOCATIONS = 3
LARGE_PX = 24.0
LARGE_BOLD_PX = 18.66
TOKEN_TOLERANCE = 2 / 255
EXEMPT_INPUT_TYPES = ("hidden", "submit", "button", "reset", "image")
SEVERITY_ORDER = {"CRITICAL": 3, "WARNING": 2, "NOTE": 1}
LABEL = "{L}"   # stands for the width or theme label until the findings are written out

NAMED = {"white": (1.0, 1.0, 1.0, 1.0), "black": (0.0, 0.0, 0.0, 1.0),
         "transparent": (0.0, 0.0, 0.0, 0.0)}


# ---- colour parsing: every string -> (r, g, b, a) in gamma sRGB 0..1 ----

def _num(token, scale=1.0, pct_scale=None):
    token = token.strip()
    if token == "none":
        return 0.0
    if token.endswith("%"):
        value = float(token[:-1]) / 100.0
        return value * (pct_scale if pct_scale is not None else 1.0)
    return float(token) / scale


def _split(body):
    body = body.strip()
    alpha = 1.0
    if "/" in body:
        body, alpha_token = body.rsplit("/", 1)
        alpha = _num(alpha_token)
    parts = [p for p in re.split(r"[\s,]+", body.strip()) if p]
    return parts, alpha


def _oklab_to_linear(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def _gamma(c):
    # Limitation: a per-channel clip stands in for CSS Color 4 gamut mapping, so an
    # out-of-gamut oklch can report a ratio that differs from the painted one. Replace
    # with a chroma-reducing map if a brand colour ever sits on the gamut edge.
    c = min(1.0, max(0.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _hsl_to_rgb(h, s, l):
    h = (h % 360) / 360.0
    if s == 0:
        return l, l, l

    def hue(p, q, t):
        t = t % 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return hue(p, q, h + 1 / 3), hue(p, q, h), hue(p, q, h - 1 / 3)


def parse_colour(text):
    """Return (r, g, b, a) in gamma-encoded sRGB, or None when the notation is unknown."""
    if not text:
        return None
    s = text.strip().lower()
    if s in NAMED:
        return NAMED[s]
    if s.startswith("#"):
        h = s[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return None
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return (r, g, b, a)
    m = re.match(r"^([a-z]+)\((.*)\)$", s)
    if not m:
        return None
    fn, body = m.group(1), m.group(2)
    parts, alpha = _split(body)
    try:
        if fn in ("rgb", "rgba"):
            if len(parts) == 4:
                alpha = _num(parts[3])
            r, g, b = (_num(p, scale=255.0) for p in parts[:3])
            return (r, g, b, alpha)
        if fn in ("hsl", "hsla"):
            if len(parts) == 4:
                alpha = _num(parts[3])
            h = float(parts[0].rstrip("deg"))
            r, g, b = _hsl_to_rgb(h, _num(parts[1]), _num(parts[2]))
            return (r, g, b, alpha)
        if fn == "oklch":
            L = _num(parts[0])
            C = _num(parts[1], pct_scale=0.4)
            H = float(parts[2].rstrip("deg")) if parts[2] != "none" else 0.0
            a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
            lr, lg, lb = _oklab_to_linear(L, a, b)
            return (_gamma(lr), _gamma(lg), _gamma(lb), alpha)
        if fn == "oklab":
            L = _num(parts[0])
            a = _num(parts[1], pct_scale=0.4)
            b = _num(parts[2], pct_scale=0.4)
            lr, lg, lb = _oklab_to_linear(L, a, b)
            return (_gamma(lr), _gamma(lg), _gamma(lb), alpha)
        if fn == "color" and parts and parts[0] in ("srgb", "srgb-linear"):
            r, g, b = (_num(p) for p in parts[1:4])
            if parts[0] == "srgb-linear":
                r, g, b = _gamma(r), _gamma(g), _gamma(b)
            return (r, g, b, alpha)
    except (ValueError, IndexError):
        return None
    return None


def composite(fg, bg):
    """Lay a translucent colour over an opaque one, in gamma space as browsers do."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


def luminance(rgb):
    r, g, b = (_linear(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    if bg[3] < 1.0:
        bg = composite(bg, (1.0, 1.0, 1.0, 1.0))
    fg = composite(fg, bg) if fg[3] < 1.0 else fg
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def is_large(font_px, weight):
    return font_px >= LARGE_PX or (font_px >= LARGE_BOLD_PX and weight >= 700)


# ---- the dump ----

def px(value):
    try:
        return float(str(value).replace("px", ""))
    except ValueError:
        return None


def weight_of(value):
    text = str(value).lower()
    if text == "bold":
        return 700
    if text == "normal":
        return 400
    try:
        return int(float(text))
    except ValueError:
        return 400


def selector(el):
    s = el.get("tag", "?")
    if el.get("id"):
        s += "#" + el["id"]
    elif el.get("cls"):
        s += "." + el["cls"].split()[0]
    return s


def snippet(text, cap=24):
    """Quote the element's own text. A colon before a digit becomes full-width so
    a reader splitting `file:line` reads a clock time as text."""
    text = re.sub(r":(?=\d)", "：", (text or "").strip())
    return '"%s"' % (text[:cap] + ("…" if len(text) > cap else ""))


def location(el):
    return "%s %s at %s" % (selector(el), snippet(el.get("text")), LABEL)


def plural(n):
    return "" if n == 1 else "s"


def with_opacity(colour, el):
    """Fold the element's `opacity` into the colour's alpha."""
    if colour is None:
        return None
    try:
        opacity = float(el.get("opacity", 1) or 1)
    except ValueError:
        opacity = 1.0
    if opacity >= 1.0:
        return colour
    return colour[:3] + (colour[3] * opacity,)


def load_tokens(path):
    """Every colour tokens.json declares, light and dark, as parsed sRGB."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = {}
    for block in ("color", "color_dark"):
        for key, value in (data.get(block) or {}).items():
            parsed = parse_colour(value)
            if parsed:
                out["%s.%s" % (block, key)] = parsed
    return out


def token_name(colour, tokens):
    for name, value in tokens.items():
        if all(abs(colour[i] - value[i]) <= TOKEN_TOLERANCE for i in range(3)):
            return name
    return None


class Report:
    """Findings keyed by the identity of the defect, so one defect at two widths is one row.

    `key` names the defect (the check plus what makes it one defect: the colour pair, the
    control, the heading); the location and evidence carry `{L}` where the label goes.
    The first capture that showed the defect supplies the element list and the count; a
    later capture only adds its label, and raises the severity when it measured worse.
    """

    def __init__(self):
        self.findings = {}
        self.unparsed = set()
        self.scope = []

    def add(self, key, severity, loc, evidence, fix, label):
        entry = self.findings.get(key)
        if entry is None:
            self.findings[key] = {"check": key[0], "severity": severity, "location": loc,
                                  "evidence": evidence, "fix": fix, "labels": [label]}
        else:
            if label not in entry["labels"]:
                entry["labels"].append(label)
            if SEVERITY_ORDER[severity] > SEVERITY_ORDER[entry["severity"]]:
                entry["severity"] = severity

    def rows(self):
        out = []
        for i, entry in enumerate(self.findings.values(), 1):
            at = ", ".join(entry["labels"])
            out.append({"id": "R-%d" % i, "check": entry["check"], "severity": entry["severity"],
                        "location": entry["location"].replace(LABEL, at),
                        "evidence": entry["evidence"].replace(LABEL, at), "fix": entry["fix"]})
        return out


def asked_width(label):
    try:
        return int(label.split("-")[-1])
    except ValueError:
        return None


def check_dump(label, dump, tokens, report):
    texts = dump.get("text", [])
    controls = dump.get("controls", [])
    viewport = (dump.get("viewport") or {}).get("width")
    skipped_fallback = 0

    # R11 viewport
    wanted = asked_width(label)
    if wanted is not None and viewport is not None and viewport != wanted:
        report.add(("R11", label), "CRITICAL", "document at " + LABEL,
                   "viewport %s reported where %s was asked for; every measurement below was taken at %s"
                   % (viewport, wanted, viewport),
                   "Rerun the capture; the page or the emulation did not honour the width.", label)

    # R3 overflow
    if dump.get("horizontalOverflow"):
        report.add(("R3",), "WARNING", "document at " + LABEL,
                   "horizontal overflow scrollWidth %s at %s" % (dump.get("scrollWidth"), LABEL),
                   "Let the widest element wrap or shrink below the viewport width.", label)

    # R1 contrast, R2 tokens, R4 clipped, R7 size — one pass over the text elements
    seen_contrast, seen_off_token, seen_small = {}, {}, {}
    for el in texts:
        fg, bg = parse_colour(el.get("color")), parse_colour(el.get("background"))
        for raw, parsed in ((el.get("color"), fg), (el.get("background"), bg)):
            if raw and parsed is None:
                report.unparsed.add(raw)
        fg = with_opacity(fg, el)
        size, weight = px(el.get("fontSize")), weight_of(el.get("fontWeight"))
        text = el.get("text") or ""
        fallback = bool(el.get("backgroundFallback"))
        if fg and bg and size and not el.get("disabled"):
            if fallback:
                skipped_fallback += 1
            else:
                ratio = contrast(fg, bg)
                needed = 3.0 if is_large(size, weight) else 4.5
                if ratio < needed:
                    key = (el.get("color"), el.get("background"), needed)
                    entry = seen_contrast.setdefault(key, {"ratio": ratio, "size": size, "locs": []})
                    entry["locs"].append(location(el))
        if tokens:
            for raw, parsed, kind in ((el.get("color"), fg, "colour"), (el.get("background"), bg, "background")):
                if parsed is None or parsed[3] == 0 or (fallback and kind == "background"):
                    continue
                if token_name(parsed, tokens) is None:
                    seen_off_token.setdefault((kind, raw), []).append(location(el))
        if el.get("clipped") and text:
            report.add(("R4", selector(el), text), "WARNING", location(el),
                       "clipped text: scrollWidth exceeds clientWidth at " + LABEL,
                       "Let the text wrap, or widen the container.", label)
        run = text.strip()
        if size and run:
            visible = re.sub(r"\s+", "", run)
            latin_short = size >= MIN_TEXT_LATIN_PX and len(visible) <= LATIN_SHORT_MAX and not CJK.search(run)
            if size < MIN_TEXT_PX and not latin_short:
                seen_small.setdefault(("CRITICAL", el.get("fontSize")), []).append(location(el))

    for (fg_raw, bg_raw, needed), entry in seen_contrast.items():
        severity = "CRITICAL" if entry["ratio"] < 2.0 else "WARNING"
        n = len(entry["locs"])
        report.add(("R1", fg_raw, bg_raw, needed), severity, "; ".join(entry["locs"][:MAX_LOCATIONS]),
                   "contrast %.2f:1 %s on %s at %gpx (needs %.1f:1; %d element%s)"
                   % (entry["ratio"], fg_raw, bg_raw, entry["size"], needed, n, plural(n)),
                   "Darken the text or lighten the background until the pair reaches %.1f:1." % needed, label)
    for (kind, raw), locs in seen_off_token.items():
        n = len(locs)
        report.add(("R2", kind, raw), "WARNING", "; ".join(locs[:MAX_LOCATIONS]),
                   "off-token %s %s at %s (%d element%s); no entry in tokens.json color or color_dark matches it"
                   % (kind, raw, LABEL, n, plural(n)),
                   "Replace the literal with the theme.css variable that carries the intended token.", label)
    for (severity, raw), locs in seen_small.items():
        n = len(locs)
        report.add(("R7", severity, raw), severity, "; ".join(locs[:MAX_LOCATIONS]),
                   "font size %s at %s (%d element%s)" % (raw, LABEL, n, plural(n)),
                   "Raise the size to 14px (12px only for a Latin-only run of at most 24 characters), or delete the run.", label)

    # R5 hit area, R6 labels, R10 dead links
    for c in controls:
        w, h = c.get("w") or 0, c.get("h") or 0
        tag, text = c.get("tag"), c.get("text")
        if w and h and min(w, h) < MIN_HIT and not c.get("disabled") and not c.get("inline"):
            report.add(("R5", tag, text), "WARNING", "%s %s at %s" % (tag, snippet(text), LABEL),
                       "hit area %dx%d px at %s (needs %dpx on the shorter side)" % (w, h, LABEL, MIN_HIT),
                       "Add padding until the control is at least %dpx on its shorter side." % MIN_HIT, label)
        if tag == "input" and not c.get("labelled") and c.get("type") not in EXEMPT_INPUT_TYPES:
            report.add(("R6", text, c.get("type")), "WARNING",
                       "input %s at %s" % (snippet(text or c.get("type") or ""), LABEL),
                       "unlabelled input: no <label>, aria-label, aria-labelledby or title at " + LABEL,
                       "Add a visible <label for> naming what the field holds.", label)
        if tag == "a" and not c.get("disabled"):
            href = (c.get("href") or "").strip()
            if not href or href == "#" or href.startswith("javascript:"):
                report.add(("R10", text, href), "NOTE", "a %s at %s" % (snippet(text), LABEL),
                           "link without a destination: href=%r at %s" % (href, LABEL),
                           "Point the link at its page, or make it a <button> if it acts in place.", label)

    # R8 headings
    headings = dump.get("headings") or []
    h1 = [h for h in headings if h.get("level") == 1]
    if headings and len(h1) != 1:
        report.add(("R8", "h1", len(h1)), "WARNING", "headings at " + LABEL,
                   "heading hierarchy: %d h1 at %s" % (len(h1), LABEL),
                   "Keep exactly one h1 naming the screen.", label)
    prev = None
    for h in headings:
        level = h.get("level")
        if prev is not None and level > prev + 1:
            report.add(("R8", level, prev, h.get("text")), "WARNING",
                       "h%d %s at %s" % (level, snippet(h.get("text")), LABEL),
                       "heading hierarchy: h%d follows h%d at %s" % (level, prev, LABEL),
                       "Use h%d, or add the missing level." % (prev + 1), label)
        prev = level

    report.scope.append("%s: %d text elements (%d skipped for an unpainted background), %d controls, %d headings, viewport %s"
                        % (label, len(texts), skipped_fallback, dump.get("controlsTotal", len(controls)),
                           len(headings), viewport))


def check_console(label, lines, report):
    for line in lines:
        if not line.startswith("CONSOLE_ERRORS"):
            continue
        try:
            entries = json.loads(line[len("CONSOLE_ERRORS"):].strip())
        except ValueError:
            entries = [line]
        for entry in entries:
            kind, _, message = entry.partition(":")
            severity = {"exception": "CRITICAL", "error": "WARNING"}.get(kind, "NOTE")
            report.add(("R9", entry), severity, "console at " + LABEL,
                       "console %s: %s" % (kind, message.strip()[:160]),
                       "Fix the page code the message names; a message from a library or the browser is an accepted pattern.", label)


def label_of(path, prefix=""):
    stem = Path(path).stem
    if prefix and stem.startswith(prefix):
        stem = stem[len(prefix):]
    return stem


def run(dump_paths, console_paths, tokens_path):
    report = Report()
    tokens = load_tokens(tokens_path) if tokens_path else {}
    for p in dump_paths:
        dump = json.loads(Path(p).read_text(encoding="utf-8"))
        check_dump(label_of(p), dump, tokens, report)
    for p in console_paths:
        lines = Path(p).read_text(encoding="utf-8", errors="replace").splitlines()
        check_console(label_of(p, "console-"), lines, report)
    scope = "; ".join(report.scope)
    scope += ("; tokens: %d colours from %s" % (len(tokens), tokens_path)) if tokens else "; no tokens.json given, R2 skipped"
    return {
        "perspective": "P0 Measured",
        "viewport": "both",
        "findings": report.rows(),
        "out_of_scope_notes": ["unparsed colour notation: %s" % c for c in sorted(report.unparsed)],
        "checked_scope": scope,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Measure the DOM dumps cdp.js wrote and emit findings in the auditors' shape")
    parser.add_argument("dumps", nargs="+", help="DOM dump JSON files from cdp.js; the file stem names the width or theme")
    parser.add_argument("--console", action="append", default=[], help="console text file from cdp.js (repeatable)")
    parser.add_argument("--tokens", help="tokens.json; enables R2")
    parser.add_argument("--out", required=True, help="findings JSON to write")
    parser.add_argument("--text", action="store_true", help="print a readable list as well")
    args = parser.parse_args(argv)
    for p in list(args.dumps) + args.console + ([args.tokens] if args.tokens else []):
        if not Path(p).is_file():
            print("expected a file: %s" % p, file=sys.stderr)
            return 2
    try:
        result = run(args.dumps, args.console, args.tokens)
    except (ValueError, AttributeError) as exc:  # a file that is not JSON, or JSON of the wrong shape
        print("unusable input: %s" % exc, file=sys.stderr)
        return 2
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    counts = {}
    for f in result["findings"]:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    print(json.dumps({"out": args.out, "findings": len(result["findings"]), "by_severity": counts,
                      "unparsed_colours": len(result["out_of_scope_notes"])}, ensure_ascii=False))
    if args.text:
        for f in result["findings"]:
            print("%s %s %s — %s" % (f["severity"], f["check"], f["location"], f["evidence"]))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
