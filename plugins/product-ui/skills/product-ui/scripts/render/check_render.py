#!/usr/bin/env python3
"""Measure what the rendered page's DOM dumps settle without judgement.

    python check_render.py <dump.json> [<dump.json> ...] [--console <txt> ...]
                           [--tokens tokens.json] [--plan ui-brief.md] --out findings.json [--text]

Reads the dumps cdp.js wrote (one per width, or per width and theme), and the console
files beside them, and writes one findings file in the auditors' shape, perspective
"P0 Measured", so the review lead merges it like any auditor's report. The design
auditors get the same file and judge what it cannot: overlap, alignment, images,
whether anything guides the eye, whether the copy is true.

Checks:

  R1  contrast below the WCAG threshold for the text's size (4.5:1, or 3:1 for text of
      24px and up, or 18.66px and up at weight 700 and up). CRITICAL under 2:1.
      Text inside a disabled control is exempt, as WCAG exempts inactive controls; so is
      text whose background no ancestor paints, or whose nearest painted background is an
      image or a gradient (`backgroundFallback`), because the white cdp.js reports there
      is nobody's choice and a lone colour cannot stand for an image. The count of those is in checked_scope.
  R2  a text colour or background outside the token set, when --tokens is given; a colour a root
      custom property of the dump resolves to (a color-mix of tokens included) counts as on-token
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
  R12 an enclosure inside an enclosure: a box drawn inside another box (dump `boxes`, depth 1 or more)
  R13 fewer than 3 distinct spacing steps among the gaps between siblings, from 6 measured
      gaps up (dump `gaps`; gaps of 4px and more)
  R14 fewer than 3 distinct (font size, weight) pairs among the text inside the first
      <main>, from 8 text entries up
  R15 a row of 3 or more equal tiles (same size within 2px, on one line with y within 2px,
      each carrying a digit) in the
      top 40% of the viewport. A WARNING unless the plan's `- Job class:` line is
      `monitor`, which suppresses it; a NOTE when --plan is absent or names no job class.
      R12, R13 and R15 skip a dump that carries no `boxes` / `gaps` (an older dump).
  R16 text whose computed background clip is `text` over a gradient (gradient text) — WARNING
      (research T2)
  R17 a box with a `backdrop-filter` other than `none`, except a box that covers the viewport
      (glass) — WARNING (research T7)
  R18 five or more boxes share one computed non-zero border radius and no box has another
      non-zero radius — WARNING (research T4)
  R19 the page `lang` starts with `ja` and the computed font family of Japanese text names no
      Japanese family before its generic family; one finding per page with the count — WARNING
      (research T23)
  R20 a row of 3 or more equal tiles, each with an icon or image and a heading, on any screen
      (R15's shared-parent, row and size rules without the digit): the feature-card row —
      WARNING (research T5). A feature row with no enclosure is no box, and the P2 reviewer
      judges it.
      R16 to R20 skip a dump that lacks the fields they read (an older dump).
  R21 body text of 16 to 18px (p, li, dd, blockquote; 2 or more lines inside the first <main>) with a line
      height under 1.5 times its size — WARNING (WCAG 1.4.8, DADS)
  R22 a text element of 2 or more lines wider than 40 full-width characters per line (text with CJK) or
      80 characters per line (other text) — WARNING (WCAG 1.4.8)
  R23 two or more links with the same name (aria-label, else text) and different destinations — WARNING
  R24 a text element equal to `meta.name` of --tokens while the plan's `- Brand area:` line is `none` or
      absent — WARNING. Skipped without --tokens.

Ported from pbakaus/impeccable (Apache-2.0, commit df3a4ab; thresholds from its Rust checks). A check that reads a
dump field an older dump lacks is skipped. Severity: impeccable error is CRITICAL, warning WARNING, advisory NOTE.

  R25 an italic serif h1, or h2 of 48px and up (italic-serif-display)
  R26 a tracked uppercase label directly above an h1 to h4; nav, list, form, table, figure and breadcrumb exempt
      (kicker-above-heading)
  R27 a tracked-caps, accent-bold or dash-prefixed label directly above an h1 of 48px and up (hero-eyebrow-chip)
  R28 two or more tiny numbered labels with distinct indexes beside h2 to h4 — NOTE (numbered-section-labels)
  R29 an h1 of 40 characters and 72px or more that fills 28% of the viewport height or 25% of its area (oversized-h1)
  R30 letter spacing under -0.07em (-0.09em from 40px) on text over 20 characters, not CJK (extreme-negative-tracking)
  R31 150 characters and over 30% of 200 or more at opacity 0 or visibility hidden — CRITICAL (content-hidden-at-rest)
  R32 text 30% covered by an opaque box, or 45% by text on a layer, by an elementFromPoint probe (text-occlusion)
  R33 gray ink (HSL lightness 0.3 to 0.85, saturation under 0.2) on a coloured background (gray-on-color)
  R34 under max(4px, 0.3em) above and below, or max(8px, 0.5em) beside, between a bordered or filled box and its
      text (cramped-padding)
  R35 paragraph text under 16px (12px at 480px and under) from the viewport edge (body-text-viewport-edge)
  R36 two or more h2 to h4 with under 75% of the space below, and 12px less, above them (heading-rhythm)
  R37 text-align: justify without hyphens in a column of 45 characters or fewer; CJK, Thai and Arabic exempt
  R38 text-transform: uppercase on 80 characters or more outside headings (all-caps-body)
  R39 letter spacing over 0.05em on body text of over 20 characters (wide-tracking)
  R40 the same text at 3 or more distinct spots inside one card (repeated-container-text)
  R41 a hairline border on two or more sides plus a 32px halo on 3 or more cards of a row — NOTE
      (gpt-thin-border-wide-shadow)
Pattern conformance, from the dump's `patterns` (elements with data-pattern) and the library under
patterns/ (references/patterns.md). All are WARNINGs until the calibration in research/20261103-real-site-patterns
settles which become errors. A dump with no `patterns` field, or a page with no data-pattern element, skips them.

  R42 in an item, the slot the pattern marks `emphasis: 1` (the name, the title, the value) is not the strongest
      text: another slot has a larger size, or the same size at a heavier weight
  R43 items of one pattern under one parent show different sets of fields (data-pattern-field)
  R44 a table pattern's cell slot holding a number is not aligned to the end, or lacks tabular-nums
  R45 a table pattern's cell holding only a placeholder (-, —, x, ×, N/A) where the cell should stay blank
  R46 an item whose required slot renders empty, or is missing from the rendered item
  R47 an enclosure (a box) inside <main> that sits in no data-pattern element and holds no form control,
      on a page that carries patterns

  Extensions: R4 also fires on text that overflows its box by 16px or more and meets another box, probed after
  scrolling to it (text-overflow); R20 also fires once per page on single icon tiles of 32 to 128px above a heading
  (icon-tile-stack); R21 also fires on multi-line text under 1.3 times its size (tight-leading; 24px and up, lead
  text, bold titles of 2 lines or fewer exempt), at most one R21 finding per element

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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "patterns"))
try:
    import library as pattern_library  # noqa: E402
except ImportError:  # the render scripts copied without the pattern library
    pattern_library = None

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
NEST_DEPTH = 1            # R12: a box this many boxes deep is an enclosure inside an enclosure
SPACING_MIN_GAP = 4       # R13: a smaller gap is two items that touch
SPACING_MIN_STEPS = 3
SPACING_MIN_GAPS = 6
EMPHASIS_MIN_LEVELS = 3   # R14
EMPHASIS_MIN_TEXTS = 8
TILE_MIN = 3              # R15
TILE_TOLERANCE = 2
TILE_TOP_FRACTION = 0.4
JOB_CLASS = re.compile(r"^\s*-\s*(?i:Job class):\s*(monitor|enter|lookup|decide)\b", re.M)
BLUR_BOX_MIN = 1          # R17: a box within this many px of the viewport size covers the viewport
RADIUS_MIN_BOXES = 5      # R18
# R19: lower-case substrings, shared with validate_tokens.py (T22)
JA_FAMILIES = tuple(json.loads((Path(__file__).resolve().parents[2] / "assets" / "ja_families.json")
                               .read_text(encoding="utf-8"))["families"])
READING_TAGS = ("p", "li", "dd", "blockquote")   # R21
READING_PX = (16.0, 18.0)
READING_LEADING = 1.5
CJK_LINE_MAX = 40         # R22: full-width characters per line
LATIN_LINE_MAX = 80
BRAND_AREA = re.compile(r"^\s*-\s*(?i:Brand area):\s*(.*)$", re.M)   # R24
GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif",
                    "ui-serif", "ui-monospace", "ui-rounded", "math", "emoji", "fangsong"}
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


BUILT_FILES = re.compile(r"^\s*-\s*Built files:\s*(.+)$", re.M)
BLOCK_ROUTE = re.compile(r"`(/[^`\s]*)`")


def _route_of(built):
    """The hash route of a Built files line (`index.html#/stores/s1?as=manager` gives `/stores/s1`, `tab=…`)."""
    m = re.search(r"#(/[^\s?]*)(\?[^\s]*)?", built)
    if not m:
        return "", ""
    query = m.group(2) or ""
    tab = re.search(r"[?&]tab=([^&\s]+)", query)
    return m.group(1), (tab.group(1) if tab else "")


def _route_matches(pattern, path, tab):
    """`/stores/:id?tab=targets` matches `/stores/s1` with tab `targets`; `/` matches only `/`."""
    head, _, query = pattern.partition("?")
    want_tab = re.search(r"tab=([^&]+)", query)
    if want_tab and want_tab.group(1) != tab:
        return False
    regex = "^" + re.sub(r":[A-Za-z_]+", "[^/]+", re.escape(head)) + "$"
    return re.match(regex, path) is not None


def read_plan_job(path):
    """The `- Job class:` value of the block whose route matches the plan's Built files line, else the
    first Job class in the plan, else "". A brief that holds one block per screen names each block's
    route in its heading (### 契約 `/contracts`), and the Built files line names the screen captured."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    built = BUILT_FILES.search(text)
    route, tab = _route_of(built.group(1)) if built else ("", "")
    if route:
        blocks = re.split(r"^(?=### )", text, flags=re.M)
        best, best_len = None, -1
        for block in blocks:
            heading = block.split("\n", 1)[0]
            for pattern in BLOCK_ROUTE.findall(heading):
                if _route_matches(pattern, route, tab):
                    want_tab = "tab=" in pattern
                    score = len(pattern) + (100 if want_tab and tab else 0)
                    if score > best_len:
                        best, best_len = block, score
        if best is not None:
            m = JOB_CLASS.search(best)
            if m:
                return m.group(1).lower()
    m = JOB_CLASS.search(text)
    return m.group(1).lower() if m else ""


def box_location(b):
    r = b.get("rect") or {}
    return "%s %dx%d (x=%d, y=%d) at %s" % (selector(b), r.get("w") or 0, r.get("h") or 0,
                                          r.get("x") or 0, r.get("y") or 0, LABEL)


def tile_runs(boxes, qualifies=lambda b: bool(b.get("hasDigit"))):
    """Runs of TILE_MIN or more boxes that share a parent box, follow one another in document
    order, satisfy `qualifies` (R15: carry a digit; R20: carry an icon or image and a heading), match in
    width and height within TILE_TOLERANCE, and sit on one line (y within TILE_TOLERANCE). A feature row
    with no enclosure is no box, so R20 cannot see it; the P2 reviewer judges it."""
    by_parent = {}
    for b in boxes:
        by_parent.setdefault(b.get("parentBox"), []).append(b)
    runs = []
    for group in by_parent.values():
        run = []
        for b in group + [None]:
            r = (b or {}).get("rect") or {}
            fits = bool(b) and qualifies(b) and r.get("w") is not None and r.get("h") is not None
            if fits and run:
                ws = [t["rect"]["w"] for t in run] + [r["w"]]
                hs = [t["rect"]["h"] for t in run] + [r["h"]]
                ys = [t["rect"].get("y", 0) for t in run] + [r.get("y", 0)]
                fits = (max(ws) - min(ws) <= TILE_TOLERANCE and max(hs) - min(hs) <= TILE_TOLERANCE
                        and max(ys) - min(ys) <= TILE_TOLERANCE)
            if fits:
                run.append(b)
                continue
            if len(run) >= TILE_MIN:
                runs.append(run)
            run = [b] if b and qualifies(b) and r.get("w") is not None and r.get("h") is not None else []
    return runs


def check_composition(label, dump, texts, job, report):
    """R12 to R15: how the screen is composed, from the dump's boxes, gaps and text."""
    boxes, gaps = dump.get("boxes"), dump.get("gaps")

    # R12 nested enclosures
    if boxes is not None:
        nested = [b for b in boxes if (b.get("depth") or 0) >= NEST_DEPTH]
        if nested:
            report.add(("R12",), "WARNING", "; ".join(box_location(b) for b in nested[:MAX_LOCATIONS]),
                       "an enclosure inside an enclosure: %d box%s drawn inside another box (depth %d or more); flatten to spacing, type and dividers"
                       % (len(nested), "" if len(nested) == 1 else "es", NEST_DEPTH),
                       "Remove the border, fill or shadow of the inner box; group with spacing, type size and dividers.", label)

    # R13 spacing steps
    if gaps is not None:
        values = [n for g in gaps for n in (g.get("values") or []) if n >= SPACING_MIN_GAP]
        steps = sorted(set(values))
        if len(values) >= SPACING_MIN_GAPS and len(steps) < SPACING_MIN_STEPS:
            report.add(("R13",), "WARNING", "gaps at " + LABEL,
                       "%d distinct spacing step%s among %d gaps at %s: %s px; a scale needs at least %d"
                       % (len(steps), plural(len(steps)), len(values), LABEL,
                          ", ".join("%g" % n for n in steps), SPACING_MIN_STEPS),
                       "Use a spacing scale of at least %d steps, so related items sit close and separate groups sit apart."
                       % SPACING_MIN_STEPS, label)

    # R14 emphasis levels
    scope = (dump.get("scope") or {}).get("rect")
    pairs, counted = set(), 0
    for el in texts:
        r = el.get("rect") or {}
        size = px(el.get("fontSize"))
        if not (el.get("text") or "").strip() or size is None:
            continue
        if scope and not (r.get("x", 0) >= scope.get("x", 0) - 1 and r.get("y", 0) >= scope.get("y", 0) - 1
                          and r.get("x", 0) + r.get("w", 0) <= scope.get("x", 0) + scope.get("w", 0) + 1
                          and r.get("y", 0) + r.get("h", 0) <= scope.get("y", 0) + scope.get("h", 0) + 1):
            continue
        counted += 1
        pairs.add((size, weight_of(el.get("fontWeight"))))
    if counted >= EMPHASIS_MIN_TEXTS and len(pairs) < EMPHASIS_MIN_LEVELS:
        report.add(("R14",), "WARNING", "text at " + LABEL,
                   "%d emphasis level%s among %d text entries at %s: %s; a hierarchy needs at least %d"
                   % (len(pairs), plural(len(pairs)), counted, LABEL,
                      ", ".join("%gpx/%d" % p for p in sorted(pairs)), EMPHASIS_MIN_LEVELS),
                   "Separate the levels by size and weight: one dominant figure or heading, a body level, a quiet level.", label)

    # R15 a row of equal tiles
    height = (dump.get("viewport") or {}).get("height")
    if boxes is not None and height and job != "monitor":
        for run in tile_runs(boxes):
            first = run[0]["rect"]
            if first.get("y", 0) >= TILE_TOP_FRACTION * height:
                continue
            message = ("%d equal tiles of %dx%d at y=%d; a tile row needs a dominant tile and a monitoring job"
                       % (len(run), first["w"], first["h"], first["y"]))
            severity = "WARNING"
            if job is None:
                severity, message = "NOTE", message + " (no plan: pass --plan ui-brief.md to settle)"
            elif job == "":
                severity, message = "NOTE", message + " (the plan has no `- Job class:` line: add one to settle)"
            report.add(("R15", len(run), first["w"], first["h"]), severity, box_location(run[0]),
                       message, "Give one tile the dominant size and the figure the reader acts on, or drop the tiles.", label)


def is_gradient(value):
    return value is True or (isinstance(value, str) and "gradient" in value)


def radius_of(b):
    """The computed radius string when it is non-zero, else None."""
    value = str(b.get("borderRadius") or "").strip()
    return value if re.search(r"[1-9]", value) else None


def check_tells(label, dump, texts, report):
    """R16 to R18 and R20: named tells of template-made screens, from the dump's style fields."""
    boxes = dump.get("boxes")

    # R16 gradient text
    clipped = [e for e in texts if is_gradient(e.get("backgroundImage"))
               and "text" in (e.get("backgroundClip"), e.get("webkitBackgroundClip"))]
    if clipped:
        n = len(clipped)
        report.add(("R16",), "WARNING", "; ".join(location(e) for e in clipped[:MAX_LOCATIONS]),
                   "gradient text: %d element%s clip a gradient to the glyphs at %s" % (n, plural(n), LABEL),
                   "Set the text in one solid token colour; emphasise with weight or size.", label)

    if boxes is None:
        return

    # R17 glass
    viewport = dump.get("viewport") or {}
    vw, vh = viewport.get("width") or 0, viewport.get("height") or 0
    glass = [b for b in boxes if (b.get("backdropFilter") or "none") != "none"
             and not ((b.get("rect") or {}).get("w", 0) >= vw - BLUR_BOX_MIN and (b.get("rect") or {}).get("h", 0) >= vh - BLUR_BOX_MIN)]
    if glass:
        n = len(glass)
        report.add(("R17",), "WARNING", "; ".join(box_location(b) for b in glass[:MAX_LOCATIONS]),
                   "backdrop blur on %d box%s that do%s not cover the viewport at %s"
                   % (n, "" if n == 1 else "es", "es" if n == 1 else "", LABEL),
                   "Give the box a solid token fill and a border; keep blur for a full-viewport overlay.", label)

    # R18 one radius everywhere
    radii = [r for r in map(radius_of, boxes) if r]
    if len(set(radii)) == 1 and len(radii) >= RADIUS_MIN_BOXES:
        report.add(("R18",), "WARNING", "boxes at " + LABEL,
                   "%d boxes share the radius %s and no box has another; controls, cards and containers need radii of their own"
                   % (len(radii), radii[0]),
                   "Give controls, cards and containers their own radius from the radius tokens.", label)

    # R20 a row of icon-and-heading tiles
    for run in tile_runs(boxes, lambda b: bool(b.get("hasMedia") and b.get("hasHeading"))):
        first = run[0]["rect"]
        report.add(("R20", len(run), first["w"], first["h"]), "WARNING", box_location(run[0]),
                   "%d equal tiles of %dx%d, each with an icon or image and a heading at %s; a feature-card row"
                   % (len(run), first["w"], first["h"], LABEL),
                   "Replace the row by one dominant item, or list the features as text with differing weight.", label)


def check_japanese_face(label, dump, texts, report):
    """R19: Japanese text on a page whose `lang` is ja, with no Japanese family before the generic one."""
    if not str(dump.get("lang") or "").lower().startswith("ja"):
        return
    bare = []
    for e in texts:
        family = e.get("fontFamily")
        if not family or not CJK.search(e.get("text") or ""):
            continue
        names = []
        for part in family.split(","):
            name = part.strip().strip("\"'").lower()
            if name in GENERIC_FAMILIES:
                break
            names.append(name + " ")
        if not any(j in name for name in names for j in JA_FAMILIES):
            bare.append(e)
    if bare:
        n = len(bare)
        report.add(("R19",), "WARNING", "; ".join(location(e) for e in bare[:MAX_LOCATIONS]),
                   "%d text element%s of Japanese text at %s name%s no Japanese font family before the generic family (%s)"
                   % (n, plural(n), LABEL, "s" if n == 1 else "", bare[0]["fontFamily"][:80]),
                   "Name a Japanese family (for example Noto Sans JP) in the font stack before the generic family.", label)


def multiline_text(el, scope):
    """(font px, line height px, content width px) of a text element inside `scope` that holds
    2 or more lines, else None. Lines are counted on the rect of the element's own text (`ownH`); an older
    dump without it falls back to the element box less its padding and borders (`pad`)."""
    r = el.get("rect") or {}
    pad = el.get("pad") or {}
    size, lh = px(el.get("fontSize")), px(el.get("lineHeight"))
    if not size or not lh or not (el.get("text") or "").strip() or text_height(el) < 2 * lh - 1:
        return None
    if scope and not (r.get("x", 0) >= scope.get("x", 0) - 1 and r.get("y", 0) >= scope.get("y", 0) - 1
                      and r.get("x", 0) + r.get("w", 0) <= scope.get("x", 0) + scope.get("w", 0) + 1
                      and r.get("y", 0) + r.get("h", 0) <= scope.get("y", 0) + scope.get("h", 0) + 1):
        return None
    return size, lh, r.get("w", 0) - pad.get("x", 0)


def check_reading(label, dump, texts, report):
    """R21 leading and R22 line length of multi-line text inside the scope. Returns the ids of the entries R21 flagged."""
    scope = (dump.get("scope") or {}).get("rect")
    tight, long_ = [], []
    for e in texts:
        m = multiline_text(e, scope)
        if not m:
            continue
        size, lh, width = m
        if e.get("tag") in READING_TAGS and READING_PX[0] <= size <= READING_PX[1] and lh < READING_LEADING * size:
            tight.append((e, lh / size))
        spacing = px(e.get("letterSpacing")) or 0.0
        if CJK.search(e["text"]):
            per_line, limit = width / (size + spacing), CJK_LINE_MAX
        else:
            per_line, limit = width / (0.5 * size), LATIN_LINE_MAX
        if per_line > limit:
            long_.append((e, per_line, limit))
    if tight:
        n = len(tight)
        report.add(("R21",), "WARNING", "; ".join(location(e) for e, _ in tight[:MAX_LOCATIONS]),
                   "line height %.2f times the font size on %d text element%s at %s (needs %.1f)"
                   % (min(ratio for _, ratio in tight), n, plural(n), LABEL, READING_LEADING),
                   "Set the line height of reading text to 1.5 times the size or more.", label)
    if long_:
        n = len(long_)
        report.add(("R22",), "WARNING", "; ".join(location(x) for x, _, _ in long_[:MAX_LOCATIONS]),
                   "%d text element%s at %s hold%s up to %.0f characters per line (limit %d)"
                   % (n, plural(n), LABEL, "s" if n == 1 else "", max(p for _, p, _ in long_), long_[0][2]),
                   "Cap the measure: max-w-[40em] for Japanese reading text, max-w-prose for Latin.", label)
    return {id(e) for e, _ in tight}


def check_link_names(label, controls, report):
    """R23: links that share a name (aria-label, else text) and point at different destinations."""
    names = {}
    for c in controls:
        href = (c.get("href") or "").strip()
        name = (c.get("ariaLabel") or c.get("text") or "").strip()
        if c.get("tag") == "a" and name and href and href != "#" and not href.startswith("javascript:"):
            names.setdefault(name, []).append(href)
    for name, hrefs in names.items():
        if len(set(hrefs)) >= 2:
            report.add(("R23", name), "WARNING", "links %s at %s" % (snippet(name), LABEL),
                       "%d links named %s go to %d destinations at %s" % (len(hrefs), snippet(name), len(set(hrefs)), LABEL),
                       "Give each link its own aria-label, or write link text that names its destination.", label)


def check_brand(label, texts, brand, report):
    """R24: the product name drawn on a screen whose brief lists no brand area."""
    hits = [e for e in texts if (e.get("text") or "").strip() == brand]
    if hits:
        report.add(("R24",), "WARNING", "; ".join(location(e) for e in hits[:MAX_LOCATIONS]),
                   "product name %s drawn at %s while the plan's Brand area is none" % (snippet(brand), LABEL),
                   "Remove the name, or list it in the brief's `- Brand area:` line.", label)


# ---- R25 to R41 and the extensions of R4, R20, R21: thresholds from pbakaus/impeccable @ df3a4ab ----

SAFE_TAGS = frozenset("blockquote nav a input textarea select pre code span th td tr li label button hr html head "
                      "body script style link meta title br img svg path circle rect line polyline polygon g defs use".split())
HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
# impeccable constants.rs KNOWN_SERIF_FONTS and GENERIC_FONTS
SERIF_FACES = frozenset(["fraunces", "recoleta", "newsreader", "playfair display", "playfair", "cormorant",
                         "cormorant garamond", "garamond", "eb garamond", "tiempos", "tiempos headline",
                         "tiempos text", "lora", "vollkorn", "spectral", "source serif pro", "source serif 4",
                         "source serif", "ibm plex serif", "merriweather", "libre caslon", "libre baskerville",
                         "baskerville", "georgia", "times new roman", "times", "dm serif display", "dm serif text",
                         "instrument serif", "gt sectra", "ogg", "canela", "freight display", "freight text"])
IMP_GENERIC = frozenset(["serif", "sans-serif", "monospace", "cursive", "fantasy", "inherit", "initial", "unset",
                         "revert", "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded",
                         "-apple-system", "blinkmacsystemfont", "segoe ui"])
ITALIC_SERIF_PX = 48.0            # R25 (rules.rs check_italic_serif)
LABEL_RATIO, LABEL_MAX_PX = 0.45, 16.0   # R26/R28 (text_rules.rs label_size_ceiling)
KICKER_BASE_PX, NUMBERED_BASE_PX = 14.0, 13.0
KICKER_MIN_TRACK_EM = 0.06
HERO_H1_PX, HERO_LABEL_PX = 48.0, 14.0   # R27 (rules.rs check_hero_eyebrow)
HERO_TRACK_PX, HERO_TRACK_EM = 1.6, 0.08
OVERSIZED_H1_PX, OVERSIZED_H1_CHARS = 72.0, 40   # R29 (measures.rs check_oversized_h1)
OVERSIZED_H1_HEIGHT, OVERSIZED_H1_AREA = 0.28, 0.25
CRUSHED_EM, CRUSHED_EM_DISPLAY, DISPLAY_PX = -0.07, -0.09, 40.0   # R30 (text_rules.rs tracking_is_crushed)
HIDDEN_MIN_CHARS, HIDDEN_MIN_HIDDEN, HIDDEN_SHARE = 200, 150, 0.3   # R31 (measures.rs content_hidden_reports)
OCCLUDED_BOX, OCCLUDED_TEXT = 0.3, 0.45   # R32 (page_checks.rs check_text_occlusion_dom)
GRAY_MIN_L, GRAY_MAX_L, GRAY_MAX_S = 0.3, 0.85, 0.2   # R33 (color.rs is_gray_ink)
GRAY_BG_SPREAD, GRAY_DARK_LUM, GRAY_PALE_L, GRAY_PALE_C = 40.0, 0.01, 0.9, 0.09   # R33 (rules.rs)
EDGE_PHONE_MAX, EDGE_GUTTER_PHONE, EDGE_GUTTER = 480.0, 12.0, 16.0   # R35 (quality.rs)
EDGE_FILL, FIXED_BAR_EDGE = 0.9, 4.0
RHYTHM_MIN_HEADINGS, RHYTHM_MAX_BELOW, RHYTHM_MIN_BELOW = 2, 160.0, 6.0   # R36 (page_checks.rs)
RHYTHM_RATIO, RHYTHM_DEFICIT, RHYTHM_EVEN_SLACK = 0.75, 12.0, 0.5
JUSTIFY_NARROW_CHARS = 45.0       # R37 (rules/text.rs)
ALL_CAPS_RUN = 80                 # R38
WIDE_TRACK_EM = 0.05              # R39
REPEAT_MIN, REPEAT_SPOTS = 3, 3   # R40
HAIRLINE_MAX_PX, HAIRLINE_MIN_ALPHA, HALO_MIN_ALPHA, HALO_MIN_BLUR = 1.5, 0.28, 0.12, 32.0   # R41 (measures.rs)
SHADOW_ROW_MIN, SHADOW_SIZE_TOL = 3, 0.25
OWN_TEXT_MIN = 10                 # R30, R39, R21 tight: own characters; the subtree needs 20 (50 for R21)
TILE_MIN_PX, TILE_MAX_PX, TILE_RATIO, TILE_MIN_ALPHA = 32.0, 128.0, (0.7, 1.4), 0.05   # R20 extension (check_icon_tile)
LEAD_DISPLAY_PX, LEAD_TEXT_PX, LEAD_TEXT_RATIO, LEAD_TEXT_LINES = 24.0, 20.0, 1.15, 3   # R21 extension (rules/text.rs)
LEAD_MIN_RATIO, LEAD_MIN_CHARS, LEAD_WRAP_BOXES = 1.3, 50, 1.5
LEAD_BOLD_WEIGHT, LEAD_BOLD_LINES = 600, 2
OVERFLOW_MIN_PX = 16.0            # R4 extension (element_checks.rs TEXT_OVERFLOW_MIN_PX)
META_TEXT = re.compile(r"[·•|]|\s[/›»>]\s|\b(19|20)\d{2}\b")
YEAR = re.compile(r"\b(19|20)\d{2}\b")
DOC_NUMBERING = re.compile(r"^(§|\d+(\.\d+)+\b|(section|article|clause|appendix|exhibit|schedule|chapter|part|rule|title)\s+"
                           r"([0-9ivxlcIVXLC]+\b|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b)", re.I)
STEP_LABEL = re.compile(r"^step\s*\d+", re.I)
TWO_DIGITS = re.compile(r"^\d{1,2}$")
NUMBERED_TWO = re.compile(r"^(\d{2})$")
NUMBERED_SEP = re.compile(r"^(\d{1,2})\s*[^0-9A-Za-z_\s]\s*\S")
NUMBERED_TAGS = ("span", "p", "div", "small", "em", "strong", "b")
NO_SPACE_SCRIPTS = ((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0x0E00, 0x0E7F), (0x1100, 0x11FF),
                    (0x2E80, 0x9FFF), (0xA960, 0xA97F), (0xAC00, 0xD7FF), (0xF900, 0xFAFF), (0xFB50, 0xFDFF),
                    (0xFE70, 0xFEFF), (0xFF66, 0xFF9F), (0x20000, 0x3134F))
CJK_SCRIPTS = ((0x1100, 0x11FF), (0x3040, 0x30FF), (0x3130, 0x318F), (0x31F0, 0x31FF), (0x3400, 0x4DBF),
               (0x4E00, 0x9FFF), (0xA960, 0xA97F), (0xAC00, 0xD7FF), (0xF900, 0xFAFF), (0xFF66, 0xFF9F),
               (0x20000, 0x3FFFF))


def u16(text):
    return len(text.encode("utf-16-le")) // 2


def rounded(x):
    return int(math.floor(x + 0.5))


def families(stack):
    return [f.strip().strip("\"'").strip().lower() for f in re.findall(r"\"[^\"]*\"|'[^']*'|[^,]+", stack or "")]


def primary_family(stack):
    return next((f for f in families(stack) if f and f not in IMP_GENERIC), "")


def resolve_serif(stack):
    """(primary family, is serif): a known serif face, or a stack that names the generic `serif`."""
    primary = primary_family(stack)
    return primary, bool(primary) and (primary in SERIF_FACES or "serif" in families(stack))


def script_share(text, ranges, sample=256):
    """(letters in `ranges`, other letters) among the first `sample` characters."""
    inside = other = 0
    for ch in text[:sample]:
        if not ch.isalpha():
            continue
        if any(lo <= ord(ch) <= hi for lo, hi in ranges):
            inside += 1
        else:
            other += 1
    return inside, other


def is_cjk_text(text):
    """impeccable is_cjk_text: some CJK letter, and CJK letters make up half of the scripted letters or more."""
    inside, other = script_share(text, CJK_SCRIPTS)
    return inside > 0 and inside * 2 >= inside + other


def has_text_run(e, text, subtree_min):
    """impeccable's gate: more than 10 characters of the element's own text and more than `subtree_min` in its subtree
    (`fullLen`; an older dump without it counts the own text)."""
    own = u16(text)
    return own > OWN_TEXT_MIN and (e.get("fullLen") if e.get("fullLen") is not None else own) > subtree_min


def typed_caps(text):
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and len(text.strip()) < ALL_CAPS_RUN and all(not c.islower() for c in letters)


def has_context_flags(texts):
    """True when the dump's text entries carry `inHeading` / `inControl` (cdp.js writes both as booleans);
    R38, R39 and the R21 tight form read them and skip an older dump."""
    return any("inHeading" in e or "inControl" in e for e in texts)


def is_heading_el(e):
    return e.get("tag") in HEADING_TAGS or bool(e.get("inHeading"))


def text_height(e):
    """Height of the element's own text: its text-node rect (`ownH`), else the box less padding and borders."""
    if e.get("ownH") is not None:
        return e["ownH"]
    r, pad = e.get("rect") or {}, e.get("pad") or {}
    return r.get("h", 0) - pad.get("y", 0)


def line_count(e):
    lh = px(e.get("lineHeight"))
    if not lh:
        return 1
    return max(1, rounded(text_height(e) / lh))


def rgb255(colour):
    return tuple(c * 255 for c in colour[:3])


def hex_of(colour):
    return "#%02x%02x%02x" % tuple(int(round(c)) for c in rgb255(colour))


def hsl_ls(c):
    r, g, b = (v / 255 for v in c)
    hi, lo = max(r, g, b), min(r, g, b)
    l, d = (hi + lo) / 2, hi - lo
    s = 0.0 if d <= 0 or l <= 0 or l >= 1 else d / (1 - abs(2 * l - 1))
    return l, s


def oklch_lc(c):
    r, g, b = (_linear(v / 255) for v in c)
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb)


def bg_reads_as_colour(c):
    """impeccable background_reads_as_colour: a channel spread of 40 (more on a near-black), and a pale tint needs chroma 0.09."""
    lum = luminance(tuple(v / 255 for v in c))
    scale = 1.0 if lum >= GRAY_DARK_LUM else math.sqrt(GRAY_DARK_LUM / max(lum, 1e-4))
    if max(c) - min(c) < GRAY_BG_SPREAD * scale:
        return False
    L, C = oklch_lc(c)
    return L < GRAY_PALE_L or C >= GRAY_PALE_C


def check_italic_serif(label, texts, report):
    """R25: an italic serif h1, or an h2 of 48px and up (the heading element or a descendant that holds its text)."""
    for e in texts:
        tag = e.get("hTag") or (e.get("tag") if e.get("tag") in ("h1", "h2") else "")
        size = px(e.get("fontSize"))
        if tag not in ("h1", "h2") or e.get("fontStyle") != "italic" or not size or size < ITALIC_SERIF_PX:
            continue
        primary, serif = resolve_serif(e.get("fontFamily"))
        if serif:
            report.add(("R25", tag, primary, size), "WARNING", location(e),
                       "italic serif %s (%s) at %gpx at %s" % (tag, primary, size, LABEL),
                       "Set the headline in roman, or in a non-serif display face; an editorial register may keep it.", label)


def label_ceiling(heading_px, base):
    relative = heading_px * LABEL_RATIO if heading_px and heading_px > 0 else 0.0
    return max(base, min(relative, LABEL_MAX_PX))


def is_accent(colour):
    parsed = parse_colour(colour)
    return bool(parsed) and (max(parsed[:3]) - min(parsed[:3])) * 255 >= 40


def kicker_candidate(p):
    text, htext = (p.get("lText") or "").strip(), (p.get("hText") or "").strip()
    hsize, lsize = px(p.get("hSize")) or 0.0, px(p.get("lSize")) or 0.0
    if not (0 < (p.get("hLevel") or 0) <= 4) or u16(htext) < 3 or re.match(r"^/[0-9A-Za-z_-]+", htext.strip("\"'“”‘’")):
        return False
    if hsize < 20 or p.get("lTag") not in ("p", "span", "div", "small") or not 2 <= u16(text) <= 34:
        return False
    if STEP_LABEL.match(text) or TWO_DIGITS.match(text) or META_TEXT.search(text) or DOC_NUMBERING.match(text):
        return False
    upper = (p.get("lTransform") == "uppercase" or (re.search("[A-Z]", text) and not re.search("[a-z]", text))
             or "small-caps" in (p.get("lVariant") or ""))
    return bool(upper) and 0 < lsize <= label_ceiling(hsize, KICKER_BASE_PX) \
        and (px(p.get("lSpacing")) or 0.0) >= lsize * KICKER_MIN_TRACK_EM


def hero_eyebrow(p):
    """R27: the style name of a tracked-caps, accent-bold or dash-prefixed label directly above a display h1, else None."""
    text = (p.get("lFull") or "").strip()
    hsize, lsize = px(p.get("hSize")) or 0.0, px(p.get("lSize")) or 0.0
    if p.get("hTag") != "h1" or p.get("levels") != 0 or p.get("app") or hsize < HERO_H1_PX:
        return None
    if not p.get("lTag") or p.get("lTag") in HEADING_TAGS or not 2 <= u16(text) <= 60 or not 0 < lsize <= HERO_LABEL_PX:
        return None
    spacing = px(p.get("lSpacing")) or 0.0
    upper = p.get("lTransform") == "uppercase" or (re.search("[A-Z]", text) and not re.search("[a-z]", text))
    dated = spacing < HERO_TRACK_PX and (p.get("hasTime") or YEAR.search(text))
    tracked = spacing >= HERO_TRACK_PX or (spacing > 0 and spacing >= lsize * HERO_TRACK_EM - 1e-9)
    if upper and not dated and tracked:
        return "tracked-caps"
    if weight_of(p.get("lWeight")) >= 700 and is_accent(p.get("lColor")):
        return "accent-bold"
    return "dash-prefix" if p.get("dash") or (p.get("dashColor") and is_accent(p["dashColor"])) else None


def numbered_index(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text or u16(text) > 40:
        return None
    m = NUMBERED_TWO.match(text) or NUMBERED_SEP.match(text)
    return int(m.group(1)) if m and int(m.group(1)) <= 40 else None


def numbered_candidate(p):
    hsize, lsize = px(p.get("hSize")) or 0.0, px(p.get("lSize")) or 0.0
    index = numbered_index(p.get("lText"))
    if index is None or p.get("hTag") not in ("h2", "h3", "h4") or u16((p.get("hText") or "").strip()) < 3:
        return None
    if p.get("lTag") not in NUMBERED_TAGS or not 0 < lsize <= label_ceiling(hsize, NUMBERED_BASE_PX):
        return None
    if hsize and hsize < lsize * 1.3:
        return None
    style = (px(p.get("lSpacing")) or 0.0) >= 0.5 or weight_of(p.get("lWeight")) >= 600 \
        or "mono" in (p.get("lFamily") or "").lower() or p.get("lTransform") == "uppercase" or is_accent(p.get("lColor"))
    return index if style else None


def check_labels(label, dump, report):
    """R26 kicker above heading, R27 hero eyebrow, R28 numbered section labels, from the dump's `labels`."""
    pairs = dump.get("labels")
    if pairs is None:
        return
    kickers, heroes, numbered = [], [], []
    for p in pairs:
        hero = hero_eyebrow(p)
        if hero:
            heroes.append((p, hero))
        if p.get("skip") or p.get("app") or p.get("inCard") or p.get("beside") or (p.get("levels", 0) > 0 and not p.get("near")):
            continue
        spacing = px(p.get("lSpacing")) or 0.0
        handed_off = p.get("hTag") == "h1" and (px(p.get("hSize")) or 0.0) >= HERO_H1_PX and (spacing >= HERO_TRACK_PX or bool(hero))
        if kicker_candidate(p) and not handed_off:
            kickers.append(p)
        index = numbered_candidate(p) if p.get("levels", 0) <= 1 or p.get("near") else None
        if index is not None and not p.get("media") and p.get("lTag") not in HEADING_TAGS:
            numbered.append((p, index))

    def pair_text(p):
        return '"%s" above %s "%s"' % ((p.get("lText") or "")[:40], p.get("hTag"), (p.get("hText") or "")[:60])
    if kickers:
        n = len(kickers)
        report.add(("R26",), "WARNING", "; ".join("label %s at %s" % (pair_text(p), LABEL) for p in kickers[:MAX_LOCATIONS]),
                   "%d tracked uppercase label%s sit%s directly above a heading at %s" % (n, plural(n), "s" if n == 1 else "", LABEL),
                   "Delete the label and let the heading carry the weight; work the words into the heading or the body.", label)
    if heroes:
        report.add(("R27",), "WARNING", "; ".join("eyebrow %s at %s" % (pair_text(p), LABEL) for p, _ in heroes[:MAX_LOCATIONS]),
                   "hero eyebrow (%s) above a display h1 at %s" % (heroes[0][1], LABEL),
                   "Drop the eyebrow, fold its words into the headline, or make it a breadcrumb.", label)
    if len(numbered) >= 2 and len({i for _, i in numbered}) >= 2:
        n = len(numbered)
        report.add(("R28",), "NOTE", "; ".join("label %s at %s" % (pair_text(p), LABEL) for p, _ in numbered[:MAX_LOCATIONS]),
                   "%d tiny numbered section labels beside headings at %s" % (n, LABEL),
                   "Let hierarchy, content and rhythm carry the sequence; drop the numbers.", label)


def check_h1_size(label, dump, report):
    """R29: a long h1 (40 characters or more) of 72px and up that fills 28% of the viewport height or 25% of its area."""
    vp = dump.get("viewport") or {}
    vw, vh = vp.get("width") or 0, vp.get("height") or 0
    for h in dump.get("h1s") or []:
        size, text = px(h.get("fontSize")) or 0.0, (h.get("text") or "").strip()
        if size < OVERSIZED_H1_PX or u16(text) < OVERSIZED_H1_CHARS:
            continue
        r, detail = h.get("rect"), ""
        if r and vw > 0 and vh > 0:
            height_ratio, area_ratio = r.get("h", 0) / vh, r.get("w", 0) * r.get("h", 0) / (vw * vh)
            if height_ratio < OVERSIZED_H1_HEIGHT and area_ratio < OVERSIZED_H1_AREA:
                continue
            detail = ", %d%% of the viewport height" % rounded(height_ratio * 100)
        report.add(("R29", text), "WARNING", 'h1 "%s" at %s' % (text[:24], LABEL),
                   "%gpx h1 of %d characters%s at %s" % (size, u16(text), detail, LABEL),
                   "Set a long headline smaller, or cut the copy to a short one.", label)


def check_tracking(label, texts, report):
    """R30 crushed negative tracking, R37 justified text, R38 all-caps body, R39 wide tracking."""
    crushed, wide, caps, justified = [], [], [], []
    flags = has_context_flags(texts)
    for e in texts:
        text, size = (e.get("text") or "").strip(), px(e.get("fontSize")) or 0.0
        spacing = px(e.get("letterSpacing")) or 0.0
        if size > 0 and has_text_run(e, text, 20) and spacing < 0:
            limit = CRUSHED_EM_DISPLAY if size >= DISPLAY_PX else CRUSHED_EM
            if spacing / size < limit and not is_cjk_text(text):
                crushed.append((e, spacing / size))
        if flags and size > 0 and has_text_run(e, text, 20) and spacing > 0 and spacing / size > WIDE_TRACK_EM:
            caps_label = e.get("textTransform") == "uppercase" or (e.get("textTransform") != "lowercase" and typed_caps(text))
            control = e.get("inControl") and line_count(e) == 1
            if not caps_label and not control and not is_cjk_text(text):
                wide.append((e, spacing / size))
        if flags and e.get("textTransform") == "uppercase" and not is_heading_el(e) and u16(re.sub(r"\s+", " ", text)) >= ALL_CAPS_RUN:
            caps.append(e)
        if e.get("textAlign") == "justify" and e.get("hyphens") != "auto":
            inside, other = script_share(text, NO_SPACE_SCRIPTS, 400)
            if multiline_text(e, None) and size > 0 and (e.get("rect") or {}).get("w", 0) / (0.5 * size) <= JUSTIFY_NARROW_CHARS \
                    and not inside > other:
                justified.append(e)
    if crushed:
        n = len(crushed)
        report.add(("R30",), "WARNING", "; ".join(location(e) for e, _ in crushed[:MAX_LOCATIONS]),
                   "letter-spacing %.2fem at %s (%d element%s; limit %.2fem, %.2fem from %gpx)"
                   % (min(r for _, r in crushed), LABEL, n, plural(n), CRUSHED_EM, CRUSHED_EM_DISPLAY, DISPLAY_PX),
                   "Tighten display type optically: keep the tracking above -0.07em (-0.09em from 40px).", label)
    if wide:
        n = len(wide)
        report.add(("R39",), "WARNING", "; ".join(location(e) for e, _ in wide[:MAX_LOCATIONS]),
                   "letter-spacing %.2fem on body text at %s (%d element%s; limit %.2fem)"
                   % (max(r for _, r in wide), LABEL, n, plural(n), WIDE_TRACK_EM),
                   "Keep body text at 0.05em of tracking or less; wide tracking belongs to short uppercase labels.", label)
    if caps:
        n = len(caps)
        report.add(("R38",), "WARNING", "; ".join(location(e) for e in caps[:MAX_LOCATIONS]),
                   "text-transform: uppercase on %d element%s of %d characters or more at %s" % (n, plural(n), ALL_CAPS_RUN, LABEL),
                   "Set sentences in sentence case; keep uppercase for short labels and headings.", label)
    if justified:
        n = len(justified)
        report.add(("R37",), "WARNING", "; ".join(location(e) for e in justified[:MAX_LOCATIONS]),
                   "text-align: justify without hyphens: auto on %d element%s of %g characters per line or fewer at %s"
                   % (n, plural(n), JUSTIFY_NARROW_CHARS, LABEL),
                   "Use text-align: left, widen the measure, or enable hyphens: auto.", label)


def check_hidden_text(label, dump, report):
    """R31: 200 characters of text or more, 150 or more of them and over 30% at opacity 0 or visibility hidden."""
    hidden = dump.get("hiddenText")
    if not hidden:
        return
    total, gone = hidden.get("total", 0), hidden.get("hidden", 0)
    if total >= HIDDEN_MIN_CHARS and gone >= HIDDEN_MIN_HIDDEN and gone / total > HIDDEN_SHARE:
        sample = (hidden.get("samples") or [""])[0]
        report.add(("R31",), "CRITICAL", "page text at " + LABEL,
                   "%d%% of the page text (%d of %d characters) stays at opacity 0 or visibility hidden%s at %s"
                   % (rounded(gone / total * 100), gone, total, ' (for example "%s")' % sample if sample else "", LABEL),
                   "Make the content visible by default; let JavaScript enhance the entrance and never gate its existence.", label)


def check_occlusion(label, dump, report):
    """R32: the probe found text covered by an opaque box (30% of its points) or by other text on a layer (45%)."""
    for o in dump.get("occlusions") or []:
        text_like = o.get("kind") == "text"
        if o.get("frac", 0) >= (OCCLUDED_TEXT if text_like else OCCLUDED_BOX) and (not text_like or o.get("layered")):
            report.add(("R32", o.get("sel"), o.get("by")), "WARNING", '%s "%s" at %s' % (o.get("sel"), (o.get("text") or "")[:24], LABEL),
                       "%d%% of the text is covered by %s (%s) at %s"
                       % (rounded(o.get("frac", 0) * 100), "overlapping text" if text_like else "an opaque element", o.get("by"), LABEL),
                       "Give the layers room, or move the text out from under the layer above it.", label)


def check_gray_on_color(label, texts, report):
    """R33: gray ink (lightness 0.3 to 0.85, saturation under 0.2) on a background that reads as colour."""
    seen = {}
    for e in texts:
        if e.get("tag") in SAFE_TAGS or e.get("backgroundFallback") or e.get("disabled"):
            continue
        fg, bg = parse_colour(e.get("color")), parse_colour(e.get("background"))
        base = parse_colour(e.get("backgroundBase")) if e.get("backgroundBase") else None
        if fg is None or bg is None:
            continue
        if bg[3] < 1 and base:
            bg = composite(bg, base)
        ink = composite(with_opacity(fg, e), bg) if with_opacity(fg, e)[3] < 1 else fg
        l, s = hsl_ls(rgb255(ink))
        if s < GRAY_MAX_S and GRAY_MIN_L < l < GRAY_MAX_L and bg_reads_as_colour(rgb255(bg)):
            seen.setdefault((hex_of(ink), hex_of(bg)), []).append(e)
    for (ink, ground), els in seen.items():
        n = len(els)
        report.add(("R33", ink, ground), "WARNING", "; ".join(location(e) for e in els[:MAX_LOCATIONS]),
                   "gray text %s on a coloured background %s at %s (%d element%s)" % (ink, ground, LABEL, n, plural(n)),
                   "Use a darker shade of the background colour for the text, or white or near-white.", label)


def check_cramped(label, texts, report):
    """R34: the space between the text and the border box is under max(4px, 0.3em) above and below, or max(8px, 0.5em) beside."""
    v_hits, h_hits = [], []
    for e in texts:
        c, size = e.get("cramp"), px(e.get("fontSize")) or 0.0
        if not c or size <= 0:
            continue
        bv, bg, bleed = c.get("bv") or [False] * 4, bool(c.get("bg")), bool(c.get("bleed"))
        v_sides = [i for i in (0, 2) if bg or bv[i]]
        h_sides = [i for i in (3, 1) if (bg and not bleed) or bv[i]]

        def low(sides, thresh):
            return bool(sides) and min(c["pad"][i] for i in sides) < thresh and min(c["inset"][i] for i in sides) < thresh
        v_thresh, h_thresh = max(4.0, size * 0.3), max(8.0, size * 0.5)
        if low(v_sides, v_thresh):
            v_hits.append((e, min(c["inset"][i] for i in v_sides), v_thresh, size))
        elif low(h_sides, h_thresh):
            h_hits.append((e, min(c["inset"][i] for i in h_sides), h_thresh, size))
    for hits, where, tag in ((v_hits, "above and below", "v"), (h_hits, "beside", "h")):
        if hits:
            e, inset, thresh, size = min(hits, key=lambda x: x[1])
            n = len(hits)
            report.add(("R34", tag), "WARNING", "; ".join(location(x[0]) for x in hits[:MAX_LOCATIONS]),
                       "%gpx of space %s the text at %s (needs %.1fpx for %gpx text; %d element%s)"
                       % (round(inset * 10) / 10, where, LABEL, thresh, size, n, plural(n)),
                       "Add at least 8px (ideally 12 to 16px) of padding inside bordered or coloured containers.", label)


def check_edge_text(label, dump, report):
    """R35: a paragraph's text closer than 16px (12px at 480px and under) to the left or right viewport edge."""
    vw = (dump.get("viewport") or {}).get("width") or 0
    entries = dump.get("edgeText")
    if not entries or vw <= 0:
        return
    floor = EDGE_GUTTER_PHONE if vw <= EDGE_PHONE_MAX else EDGE_GUTTER
    hits = []
    for t in entries:
        if t.get("inNav") or t.get("ownBg") or t.get("positioned") or not t.get("w", 0) / vw > 0.5:
            continue
        tl, tr, cl, cr = t["tl"], t["tr"], t["cl"], t["cr"]
        keeps_gutter = t.get("align") != "justify" and tl >= EDGE_GUTTER and tr <= vw - EDGE_GUTTER
        if t.get("lines", 1) >= 2 and tr - tl >= (cr - cl) * EDGE_FILL and not keeps_gutter:
            left, right = cl, cr
        elif t.get("listItem"):
            left, right = min(tl, cl), tr
        else:
            left, right = tl, tr
        if t.get("fixedBar") and min(left, vw - right) >= FIXED_BAR_EDGE:
            continue
        if not (right > 0 and left < vw):
            continue
        l, r = rounded(left), rounded(vw - right)
        if (l >= 0 and left < floor) or (r >= 0 and right > vw - floor):
            hits.append((t, l, r))
    if hits:
        t, l, r = hits[0]
        n = len(hits)
        report.add(("R35",), "WARNING", "; ".join('%s "%s" at %s' % (h.get("sel"), (h.get("text") or "")[:24], LABEL) for h, _, _ in hits[:MAX_LOCATIONS]),
                   "body text %dpx from the left and %dpx from the right edge at %s (needs %gpx; %d element%s)"
                   % (l, r, LABEL, floor, n, plural(n)),
                   "Wrap the content in a container with at least 16px (ideally 24 to 32px) of horizontal padding.", label)


def check_heading_rhythm(label, dump, report):
    """R36: two or more h2 to h4 headings with under 75% of their gap below, and 12px less, between them and the block above."""
    crowded = []
    for g in dump.get("headingGaps") or []:
        above, below = g.get("above"), g.get("below")
        if above is None or below is None or g.get("topEdge") or g.get("inCard") or g.get("aboveSeparates"):
            continue
        if below < RHYTHM_MIN_BELOW or below > RHYTHM_MAX_BELOW:
            continue
        deficit = above < below * RHYTHM_RATIO and below - above >= RHYTHM_DEFICIT
        # impeccable also reads an even gap under running prose (`aboveProse`) as a heading bound to the paragraph above
        if deficit or (g.get("aboveProse") and above <= below + RHYTHM_EVEN_SLACK):
            crowded.append((g, deficit))
    if len(crowded) >= RHYTHM_MIN_HEADINGS:
        n = len(crowded)
        first = crowded[0][0]
        report.add(("R36",), "WARNING", "; ".join('%s "%s" at %s' % (g.get("tag"), (g.get("text") or "")[:24], LABEL) for g, _ in crowded[:MAX_LOCATIONS]),
                   "%d headings sit %s the block above than %s their own content at %s (%gpx above against %gpx below on the first)"
                   % (n, "closer to" if all(d for _, d in crowded) else "no farther from", "to" if all(d for _, d in crowded) else "from",
                      LABEL, first["above"], first["below"]),
                   "Open up the space above each heading so it exceeds the space below it.", label)


def check_repeats(label, dump, report):
    """R40: the same text (4 to 48 characters) at 3 or more distinct spots inside one card."""
    for g in dump.get("repeatGroups") or []:
        if g.get("count", 0) >= REPEAT_MIN and g.get("distinct", 0) >= REPEAT_SPOTS:
            report.add(("R40", g.get("container"), g.get("text")), "WARNING", "%s at %s" % (g.get("container"), LABEL),
                       '"%s" rendered %d times in distinct spots inside one container at %s' % ((g.get("text") or "")[:40], g["count"], LABEL),
                       "Say it once, in the slot where it matters most.", label)


def shadow_layers(value):
    """(inset, alpha, x, y, blur, spread) per layer of a computed box-shadow."""
    out = []
    for layer in re.split(r",(?![^(]*\))", value or ""):
        colour = re.search(r"(?:rgba?|hsla?|oklch|oklab|color)\([^)]*\)|#[0-9a-fA-F]{3,8}", layer)
        parsed = parse_colour(colour.group(0)) if colour else (0.0, 0.0, 0.0, 1.0)
        rest = layer.replace(colour.group(0), "") if colour else layer
        lengths = [float(n) for n in re.findall(r"-?\d*\.?\d+(?=px)", rest)]
        if len(lengths) >= 2:
            lengths += [0.0] * (4 - len(lengths))
            out.append(("inset" in layer, parsed[3] if parsed else 1.0, *lengths[:4]))
    return out


def halo_blur(value):
    """The widest blur drawn outside the box with at least 0.12 alpha whose halo (blur less a negative spread) reaches 32px."""
    best = None
    for inset, alpha, _, _, blur, spread in shadow_layers(value):
        if not inset and alpha >= HALO_MIN_ALPHA and blur + min(spread, 0.0) >= HALO_MIN_BLUR:
            best = blur if best is None else max(best, blur)
    return best


def check_shadow_rows(label, dump, report):
    """R41: a hairline border on two or more sides plus a halo of 32px blur on 3 or more boxes of one row (siblings under one DOM parent)."""
    boxes = dump.get("boxes")
    if not boxes or not any("borderW" in b for b in boxes):
        return
    pairs = []
    for b in boxes:
        widths, alphas = b.get("borderW") or [], b.get("borderA") or [1] * 4
        thin = [w for w, a in zip(widths, alphas) if 0 < w <= HAIRLINE_MAX_PX and a >= HAIRLINE_MIN_ALPHA]
        blur = halo_blur(b.get("boxShadow"))
        r = b.get("rect") or {}
        if len(thin) >= 2 and blur is not None and r.get("w") is not None and r.get("h") is not None:
            pairs.append((b, max(thin), blur))

    def close(x, y):
        return max(x, y) > 0 and abs(x - y) / max(x, y) <= SHADOW_SIZE_TOL

    def row_of(b):
        """The siblings of one DOM parent (`domParent`) form a row; an older dump falls back to the parent box."""
        return b["domParent"] if b.get("domParent") is not None else b.get("parentBox")
    for b, thin, blur in pairs:
        mates = [m for m, _, _ in pairs if row_of(m) == row_of(b)
                 and close(m["rect"]["w"], b["rect"]["w"]) and close(m["rect"]["h"], b["rect"]["h"])]
        if len(mates) >= SHADOW_ROW_MIN:
            report.add(("R41", thin, round(blur)), "NOTE", box_location(b),
                       "%gpx border and %dpx shadow blur repeated across a row of %d boxes at %s" % (thin, round(blur), len(mates), LABEL),
                       "Commit to one across the row: a defined edge or a soft elevation.", label)
            break


def check_icon_tiles(label, dump, report):
    """R20 extension: rounded-square icon containers (32 to 128px, ratio 0.7 to 1.4) stacked above a heading.
    One finding per page and capture; its evidence lists the headings."""
    hits = []
    for t in dump.get("iconTiles") or []:
        w, h = t.get("w") or 0, t.get("h") or 0
        if not (TILE_MIN_PX <= w <= TILE_MAX_PX and TILE_MIN_PX <= h <= TILE_MAX_PX and TILE_RATIO[0] <= w / h <= TILE_RATIO[1]):
            continue
        painted = (t.get("bgAlpha") or 0) >= TILE_MIN_ALPHA or t.get("bgImage") or (t.get("borderW") or 0) > 0
        if not painted or (t.get("radius") or 0) >= w / 2 or not t.get("hasIcon"):
            continue
        if t.get("iconW") and t["iconW"] >= w * 0.95:
            continue
        if t.get("hTop") and t.get("bottom") and t["bottom"] > t["hTop"] + 4:
            continue
        hits.append(t)
    if hits:
        n = len(hits)
        first = hits[0]
        report.add(("R20", "tile"), "WARNING", "; ".join('%s "%s" at %s' % (t.get("hTag"), (t.get("hText") or "")[:24], LABEL) for t in hits[:MAX_LOCATIONS]),
                   "%dx%dpx icon tile above %s \"%s\" at %s%s"
                   % (rounded(first["w"]), rounded(first["h"]), first.get("hTag"), (first.get("hText") or "")[:40], LABEL,
                      "" if n == 1 else "; %d icon tiles in all, above %s" % (n, ", ".join(
                          '%s "%s"' % (t.get("hTag"), (t.get("hText") or "")[:40]) for t in hits[:MAX_LOCATIONS * 2]))),
                   "Put the icon beside the heading, or let it sit in flow without its own container.", label)


def check_tight_leading(label, texts, reading_hits, report):
    """R21 extension: multi-line text under 1.3 times its size (display text of 24px and up, lead text, bold titles of 2 lines or fewer exempt).
    An element the 1.5 rule of check_reading already flagged is left to that finding."""
    hits = []
    if not has_context_flags(texts):
        return
    for e in texts:
        text, size, lh = (e.get("text") or "").strip(), px(e.get("fontSize")) or 0.0, px(e.get("lineHeight"))
        if id(e) in reading_hits or not has_text_run(e, text, LEAD_MIN_CHARS) or is_heading_el(e)                 or not (0 < size < LEAD_DISPLAY_PX) or not lh:
            continue
        ratio = lh / size
        shown = math.floor(ratio * 100 + 0.5) / 100
        if shown >= LEAD_MIN_RATIO or e.get("tag") in ("pre", "code", "samp"):
            continue
        if text_height(e) < lh * LEAD_WRAP_BOXES:
            continue
        lines = line_count(e)
        if size >= LEAD_TEXT_PX and shown >= LEAD_TEXT_RATIO and lines <= LEAD_TEXT_LINES:
            continue
        if weight_of(e.get("fontWeight")) >= LEAD_BOLD_WEIGHT and lines <= LEAD_BOLD_LINES:
            continue
        if shown >= 1.0 and ((e.get("textTransform") == "uppercase" and lines <= LEAD_TEXT_LINES) or typed_caps(text)):
            continue
        hits.append((e, ratio))
    if hits:
        n = len(hits)
        report.add(("R21", "tight"), "WARNING", "; ".join(location(e) for e, _ in hits[:MAX_LOCATIONS]),
                   "line height %.2f times the font size on %d multi-line text element%s at %s (needs %.1f)"
                   % (min(r for _, r in hits), n, plural(n), LABEL, LEAD_MIN_RATIO),
                   "Set the line height of running text to 1.5 to 1.7 times the size.", label)


def check_text_collisions(label, dump, report):
    """R4 extension: text that overflows its box (16px or more) and meets another box."""
    for o in dump.get("textOverflow") or []:
        if o.get("delta", 0) >= OVERFLOW_MIN_PX and o.get("meets"):
            report.add(("R4", "collide", o.get("sel"), o.get("text")), "WARNING", '%s "%s" at %s' % (o.get("sel"), (o.get("text") or "")[:24], LABEL),
                       "text overflows its box by %dpx and meets %s at %s" % (rounded(o["delta"]), o["meets"], LABEL),
                       "Let the text wrap, constrain the width, or give the region room.", label)


def check_impeccable(label, dump, texts, reading_hits, report):
    """The checks ported from impeccable; each one skips a dump that lacks the fields it reads."""
    check_italic_serif(label, texts, report)
    check_labels(label, dump, report)
    check_h1_size(label, dump, report)
    check_tracking(label, texts, report)
    check_hidden_text(label, dump, report)
    check_occlusion(label, dump, report)
    check_gray_on_color(label, texts, report)
    check_cramped(label, texts, report)
    check_edge_text(label, dump, report)
    check_heading_rhythm(label, dump, report)
    check_repeats(label, dump, report)
    check_shadow_rows(label, dump, report)
    check_icon_tiles(label, dump, report)
    check_tight_leading(label, texts, reading_hits, report)
    check_text_collisions(label, dump, report)


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


def check_dump(label, dump, tokens, report, job=None, brand=None):
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
    # The dump's root custom properties that resolve to a colour (color-mix of tokens included) count as
    # tokens too: a value a theme variable gives is on-token.
    if tokens:
        tokens = dict(tokens)
        for prop, value in (dump.get("tokens") or {}).items():
            parsed = parse_colour(value) if isinstance(value, str) else None
            if parsed:
                tokens.setdefault("root.%s" % prop, parsed)
    seen_contrast, seen_off_token, seen_small = {}, {}, {}
    for el in texts:
        fg, bg = parse_colour(el.get("color")), parse_colour(el.get("background"))
        bg_raw_parsed = bg
        # A translucent background is laid over the nearest opaque ancestor colour the dump recorded (R1);
        # R2 matches the raw value, so a tint of a token (the token at a low alpha) stays on-token.
        base = parse_colour(el.get("backgroundBase")) if el.get("backgroundBase") else None
        if bg and bg[3] < 1 and base:
            bg = composite(bg, base)
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
            for raw, parsed, kind in ((el.get("color"), fg, "colour"), (el.get("background"), bg_raw_parsed, "background")):
                if parsed is None or parsed[3] == 0 or (fallback and kind == "background"):
                    continue
                if token_name(parsed, tokens) is None:
                    seen_off_token.setdefault((kind, raw), []).append(location(el))
        hidden = "sr-only" in (el.get("cls") or "") or min((el.get("rect") or {}).get("w", 99), (el.get("rect") or {}).get("h", 99)) <= 1
        if el.get("clipped") and text and not hidden:
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

    check_composition(label, dump, texts, job, report)
    check_tells(label, dump, texts, report)
    check_japanese_face(label, dump, texts, report)
    reading_hits = check_reading(label, dump, texts, report)
    check_link_names(label, controls, report)
    if brand:
        check_brand(label, texts, brand, report)
    check_impeccable(label, dump, texts, reading_hits, report)
    check_patterns(label, dump, report)

    report.scope.append("%s: %d text elements (%d skipped for an unpainted background), %d controls, %d headings, viewport %s"
                        % (label, len(texts), skipped_fallback, dump.get("controlsTotal", len(controls)),
                           len(headings), viewport))


NUMBER_CELL = re.compile(r"^[-+]?[¥$€£]?\s*[-+]?\d[\d,]*(?:\.\d+)?\s*(?:円|%|％|件|個|人|名|点|pt)?$")
PLACEHOLDER_CELL = {"-", "—", "–", "－", "ー", "x", "×", "✕", "N/A", "n/a", "NA"}


def check_patterns(label, dump, report):
    """R42 to R47: whether each rendered element that names its pattern carries it."""
    patterns = dump.get("patterns")
    if not patterns or pattern_library is None:
        return
    library = pattern_library.load_library()
    by_id = {}
    for p in patterns:
        by_id.setdefault(p.get("id"), []).append(p)
    for pid, items in by_id.items():
        spec = library.get(pid)
        if not spec:
            continue
        emphasis = [s["id"] for s in spec["slots"] if s.get("emphasis") == 1]
        # R42 compares the emphasis slot with the slots that carry the item's data, not with a heading or a control
        peers = {s["id"] for s in spec["slots"] if s["takes"] in pattern_library.OBJECT_TAKES + ("measure", "comparison", "text")}
        required = [s["id"] for s in spec["slots"] if s.get("required")]
        weak, empty, missing = [], {}, {}
        for p in items:
            slots = [s for s in p.get("slots", []) if not s.get("hidden")]
            # R42 the emphasis slot is the strongest text of the item
            for sid in emphasis:
                top = [s for s in slots if s.get("slot") == sid and not s.get("empty")]
                rest = [s for s in slots if s.get("slot") != sid and s.get("slot") in peers and not s.get("empty")]
                if top and rest:
                    t = max((s["fontSize"], s["fontWeight"]) for s in top)
                    over = [s for s in rest if (s["fontSize"], s["fontWeight"]) > t]
                    if over:
                        weak.append((p, sid, over[0], t))
            # R46 a required slot empty or missing
            for sid in required:
                found = [s for s in p.get("slots", []) if s.get("slot") == sid]
                if not found:
                    missing.setdefault(sid, []).append(p)
                elif all(s.get("empty") or s.get("hidden") for s in found):
                    empty.setdefault(sid, []).append(p)
        if weak:
            p, sid, other, t = weak[0]
            report.add(("R42", pid), "WARNING", "%s at %s" % (pid, LABEL),
                       "in %d of %d `%s` items the `%s` slot (%.0fpx/%s) is outweighed by `%s` (%.0fpx/%s) at %s"
                       % (len(weak), len(items), pid, sid, t[0], t[1], other.get("slot"), other["fontSize"], other["fontWeight"], LABEL),
                       "Make the %s the strongest text of the item: the larger size, or the same size at the heavier weight." % sid, label)
        for sid, ps in sorted(missing.items()):
            report.add(("R46", pid, sid, "missing"), "WARNING", "%s at %s" % (pid, LABEL),
                       "%d of %d `%s` items render no `%s` slot at %s" % (len(ps), len(items), pid, sid, LABEL),
                       "Render the slot the pattern requires, or change the section in the brief and run resolve.py.", label)
        for sid, ps in sorted(empty.items()):
            report.add(("R46", pid, sid), "WARNING", "%s at %s" % (pid, LABEL),
                       "%d of %d `%s` items render the required `%s` slot empty at %s" % (len(ps), len(items), pid, sid, LABEL),
                       "Fill the slot from the record, or leave the item out until the record holds it.", label)
        # R43 same fields across the items of one collection
        if spec.get("kind") in pattern_library.ITEM_KINDS:
            groups = {}
            for p in items:
                groups.setdefault(p.get("group"), []).append(p)
            for group, members in groups.items():
                if len(members) < 2:
                    continue
                sets = [frozenset(s["field"] for s in m.get("slots", []) if s.get("field") and not s.get("hidden")) for m in members]
                common = max(set(sets), key=sets.count)
                odd = [m for m, fs in zip(members, sets) if fs != common]
                if odd:
                    diff = sorted(set().union(*sets) - set.intersection(*[set(x) for x in sets]))
                    report.add(("R43", pid, group), "WARNING", "%s at %s" % (pid, LABEL),
                               "%d of %d `%s` items under one parent show a different set of fields (%s) at %s"
                               % (len(odd), len(members), pid, ", ".join(diff[:4]) or "order", LABEL),
                               "Show the same fields on every item; an item without a value keeps the slot, blank.", label)
        if spec.get("kind") == "collection-table":
            # R44 numbers aligned to the end with tabular figures; R45 placeholder cells
            bad = []
            for p in items:
                for s in p.get("slots", []):
                    if s.get("slot") in ("property", "price", "count") and NUMBER_CELL.match(s.get("text") or ""):
                        aligned = s.get("textAlign") in ("right", "end")
                        tabular = "tabular-nums" in (s.get("numeric") or "")
                        if not (aligned and tabular):
                            bad.append((s, aligned, tabular))
            if bad:
                fields = sorted({b[0].get("field") or b[0].get("slot") for b in bad})
                report.add(("R44", pid), "WARNING", "%s at %s" % (pid, LABEL),
                           "%d number cells (%s) %s at %s" % (len(bad), ", ".join(fields[:4]),
                           "not aligned to the end" if not all(b[1] for b in bad) else "without tabular-nums", LABEL),
                           "Align number columns to the end and set font-variant-numeric: tabular-nums (text-right tabular-nums).", label)
            cells = [c for p in items for c in p.get("shortCells", []) if c in PLACEHOLDER_CELL]
            if cells:
                report.add(("R45", pid), "WARNING", "%s at %s" % (pid, LABEL),
                           "%d cells hold only %s at %s" % (len(cells), " ".join(sorted(set(cells))), LABEL),
                           "Leave a cell without a value blank; keep a dash only for a field that cannot take a value.", label)
    # R47 an enclosure outside every pattern
    stray = [b for b in dump.get("boxes", []) if not b.get("inPattern") and not b.get("hasField")
             and (b.get("rect") or {}).get("w", 0) >= 120 and (b.get("rect") or {}).get("h", 0) >= 48]
    if stray:
        report.add(("R47",), "WARNING", "; ".join(box_location(b) for b in stray[:MAX_LOCATIONS]),
                   "%d enclosures carry no pattern at %s" % (len(stray), LABEL),
                   "Give each container the pattern its section resolves to (data-pattern), or drop the enclosure "
                   "and group by distance (references/composition.md).", label)


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


def read_plan_brand_area(path):
    """True when the plan's `- Brand area:` line lists an element; False for `none`, an unfilled placeholder or no line."""
    m = BRAND_AREA.search(Path(path).read_text(encoding="utf-8", errors="replace"))
    value = m.group(1).strip().strip("{} ").lower() if m else "none"
    return not (value == "" or value.startswith("none"))


def load_brand_name(path):
    meta = json.loads(Path(path).read_text(encoding="utf-8")).get("meta") or {}
    return str(meta.get("name") or "").strip()


def label_of(path, prefix=""):
    stem = Path(path).stem
    if prefix and stem.startswith(prefix):
        stem = stem[len(prefix):]
    return stem


def run(dump_paths, console_paths, tokens_path, plan_path=None):
    report = Report()
    job = read_plan_job(plan_path) if plan_path else None
    tokens = load_tokens(tokens_path) if tokens_path else {}
    brand = load_brand_name(tokens_path) if tokens_path else ""
    if plan_path and read_plan_brand_area(plan_path):
        brand = ""
    for p in dump_paths:
        dump = json.loads(Path(p).read_text(encoding="utf-8"))
        check_dump(label_of(p), dump, tokens, report, job, brand)
    for p in console_paths:
        lines = Path(p).read_text(encoding="utf-8", errors="replace").splitlines()
        check_console(label_of(p, "console-"), lines, report)
    scope = "; ".join(report.scope)
    scope += ("; tokens: %d colours from %s" % (len(tokens), tokens_path)) if tokens else "; no tokens.json given, R2 skipped, R24 skipped"
    scope += "; plan job class: %s" % (job or "unknown" if plan_path else "no --plan given")
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
    parser.add_argument("--tokens", help="tokens.json; enables R2 and R24")
    parser.add_argument("--plan", help="ui-brief.md; its `- Job class:` line settles R15 and its `- Brand area:` line R24")
    parser.add_argument("--out", required=True, help="findings JSON to write")
    parser.add_argument("--text", action="store_true", help="print a readable list as well")
    args = parser.parse_args(argv)
    for p in list(args.dumps) + args.console + ([args.tokens] if args.tokens else []) + ([args.plan] if args.plan else []):
        if not Path(p).is_file():
            print("expected a file: %s" % p, file=sys.stderr)
            return 2
    try:
        result = run(args.dumps, args.console, args.tokens, args.plan)
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
