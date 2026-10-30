#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) validation of tokens.json.

Standard library only. Checks the token set that Step 1 produces, before any
markup exists. The source of record for these rules is references/tokens-format.md;
change that file first when a rule changes.

Errors mean the token set does not hold together. Warnings mean it holds but
departs from what the skill recommends.

CLI:
    python validate_tokens.py <tokens.json> [--json]

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors).
"""

import argparse
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import colour  # noqa: E402

OKLCH = re.compile(r"^oklch\(\s*[^)]+\)$", re.IGNORECASE)
MS = re.compile(r"^(\d+(?:\.\d+)?)ms$")

# Families a model reaches for when no choice has been made. See S2 in
# references/slop-checklist.md for the same list applied to generated markup.
FORBIDDEN_FAMILIES = {
    "inter", "roboto", "open sans", "lato", "arial", "helvetica",
    "system-ui", "-apple-system", "space grotesk", "poppins", "montserrat",
    "geist", "geist sans",
}

# T8: permitted surface/renderer pairings, from references/stack-defaults.md.
PAIRINGS = {
    ("saas", "vite-react"),
    ("saas", "next-react"),
    ("lp", "astro-react"),
    ("lp", "next-react"),
    ("lp", "html"),
}

# T8 raises a warning for these: an existing project the skill did not
# choose the stack for. See the pairing table in references/stack-defaults.md.
WARNED_PAIRINGS = {
    ("saas", "server-templates"),
}

COLOR_KEYS = [
    "background", "foreground", "primary", "primary_foreground",
    "muted", "muted_foreground", "border", "destructive", "accent",
]

RADIUS_STEPS = ["sm", "md", "lg"]
SHADOW_STEPS = ["sm", "md", "lg"]

NUMBER = r"(\d*\.?\d+)(%?)"
ALPHA_SLASH = re.compile(r"/\s*" + NUMBER + r"\s*\)")
ALPHA_FUNC = re.compile(r"(?:rgba|hsla)\(\s*[^,()]+,[^,()]+,[^,()]+,\s*" + NUMBER + r"\s*\)", re.IGNORECASE)
ALPHA_HEX = re.compile(r"#(?:[0-9a-f]{6}([0-9a-f]{2})|[0-9a-f]{3}([0-9a-f]))(?![0-9a-f])", re.IGNORECASE)

# T18: the sets a meta.users entry draws from. See references/tokens-format.md.
USER_SETS = {
    "frequency": ("daily", "weekly", "occasional", "first"),
    "expertise": ("novice", "intermediate", "expert"),
    "basis": ("observed", "reported", "assumed"),
}

# T22: the Japanese faces, one list shared with render/check_render.py (R19).
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ja_families.json"),
          encoding="utf-8") as _handle:
    JA_FAMILIES = tuple(json.load(_handle)["families"])

# T19: the visible choices whose source meta.provenance records, and the
# prefixes a source starts with. T20 accepts the first three as a decision.
PROVENANCE_KEYS = ("color.primary", "color.accent", "typography.display", "typography.body")
PROVENANCE_PREFIXES = ("brand:", "reference:", "user:", "lookup:", "derived:")
DECIDED_PREFIXES = ("brand:", "reference:", "user:")

# T21: the neutrals that share the primary hue at low chroma (tokens-format.md, rule 1).
NEUTRAL_KEYS = ("background", "muted", "muted_foreground", "border")
NEUTRAL_MAX_CHROMA = 0.012
NEUTRAL_TINT_CHROMA = 0.004
NEUTRAL_MAX_HUE_GAP = 15


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, check_id, path, message):
        self.errors.append({"id": check_id, "path": path, "message": message})

    def warn(self, check_id, path, message):
        self.warnings.append({"id": check_id, "path": path, "message": message})


def get(obj, path):
    """Walk a dotted path, returning None when any segment is missing."""
    node = obj
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def shadow_alpha(text):
    """Return the alpha of the first colour in a shadow value as a float, or None."""
    found = ALPHA_SLASH.search(text) or ALPHA_FUNC.search(text)
    if found:
        value = float(found.group(1))
        return round(value / 100 if found.group(2) else value, 2)
    found = ALPHA_HEX.search(text)
    if found:
        byte = found.group(1) or found.group(2) * 2
        return round(int(byte, 16) / 255, 2)
    return None


def check_meta(doc, rep):
    for path in ("meta.name", "meta.surface", "meta.stack.renderer",
                 "meta.stack.tailwind", "meta.stack.base", "meta.defaults_applied"):
        if get(doc, path) is None and path != "meta.stack.base":
            rep.error("T1", path, "required field is missing")
    if "reference" not in (get(doc, "meta") or {}):
        rep.error("T1", "meta.reference", "required field is missing (write null when nothing is referenced)")
    name = get(doc, "meta.name")
    if name is not None and not (isinstance(name, str) and name.strip()):
        rep.error("T1", "meta.name", "must be a non-empty string")

    surface = get(doc, "meta.surface")
    if surface is not None and surface not in ("saas", "lp"):
        rep.error("T1", "meta.surface", f"expected 'saas' or 'lp', found {surface!r}")

    structure = get(doc, "meta.structure")
    if structure is not None and structure not in ("ooui", "task"):
        rep.error("T1", "meta.structure", f"expected 'ooui' or 'task', found {structure!r}")

    tailwind = get(doc, "meta.stack.tailwind")
    if tailwind is not None and str(tailwind) != "4":
        rep.error("T7", "meta.stack.tailwind", f"expected '4', found {tailwind!r}; version 3 is out of scope")

    renderer = get(doc, "meta.stack.renderer")
    if surface and renderer:
        if (surface, renderer) in WARNED_PAIRINGS:
            rep.warn("T8", "meta.stack",
                     f"pairing {surface}/{renderer} is admitted for an existing project only; "
                     "record the missing component base in defaults_applied")
        elif (surface, renderer) not in PAIRINGS:
            rep.error("T8", "meta.stack", f"pairing {surface}/{renderer} is not in the table in stack-defaults.md")

    base = get(doc, "meta.stack.base")
    if renderer in ("html", "server-templates"):
        if base is not None:
            rep.error("T1", "meta.stack.base", f"must be null when renderer is {renderer!r}")
    elif base not in ("base-ui", "radix", "react-aria", "smarthr-ui"):
        rep.error("T1", "meta.stack.base",
                  f"expected base-ui, radix, react-aria or smarthr-ui, found {base!r}")

    applied = get(doc, "meta.defaults_applied")
    if applied is not None and not isinstance(applied, list):
        rep.error("T1", "meta.defaults_applied", "must be an array of strings")


def check_provenance(doc, rep):
    """T19 - meta.provenance: where each visible choice came from."""
    provenance = get(doc, "meta.provenance")
    if not isinstance(provenance, dict):
        rep.warn("T19", "meta.provenance",
                 "missing; record the source of " + ", ".join(PROVENANCE_KEYS) + " (references/tokens-format.md)")
        return
    for key in PROVENANCE_KEYS:
        value = provenance.get(key)
        if value is None:
            rep.warn("T19", f"meta.provenance.{key}", "missing; record where this choice came from")
        elif not (isinstance(value, str) and value.startswith(PROVENANCE_PREFIXES)):
            rep.warn("T19", f"meta.provenance.{key}",
                     f"expected a source starting with {', '.join(PROVENANCE_PREFIXES)}, found {value!r}")


def check_logo(doc, rep):
    logo = get(doc, "meta.logo")
    if "logo" in (get(doc, "meta") or {}) and logo is not None and not (isinstance(logo, str) and logo.strip()):
        rep.error("T1", "meta.logo", "must be a path to the logo file, or null")


def check_users(doc, rep):
    """T18 - meta.users: required on saas, validated wherever it is present."""
    users = get(doc, "meta.users")
    if users is None or users == []:
        if get(doc, "meta.surface") == "saas":
            rep.error("T18", "meta.users", "required and non-empty when surface is 'saas'; "
                      "name each user group (role, frequency, expertise, job, basis)")
        return
    if not isinstance(users, list):
        rep.error("T18", "meta.users", "must be an array of user groups")
        return
    for index, entry in enumerate(users):
        where = f"meta.users[{index}]"
        if not isinstance(entry, dict):
            rep.error("T18", where, "must be an object")
            continue
        for field in ("role", "job"):
            value = entry.get(field)
            if not (isinstance(value, str) and value.strip()):
                rep.error("T18", f"{where}.{field}", "required, a non-empty string")
        for field, allowed in USER_SETS.items():
            value = entry.get(field)
            if field not in entry:
                rep.error("T18", f"{where}.{field}", "required field is missing")
            elif value not in allowed:
                rep.error("T18", f"{where}.{field}", f"expected one of {', '.join(allowed)}, found {value!r}")


def check_color(doc, rep):
    color = get(doc, "color")
    if not isinstance(color, dict):
        rep.error("T1", "color", "required field is missing")
        return

    for key in COLOR_KEYS:
        if key not in color:
            rep.error("T1", f"color.{key}", "required colour is missing")

    for key, value in color.items():
        if not isinstance(value, str) or not OKLCH.match(value.strip()):
            rep.error("T2", f"color.{key}", f"expected oklch(...) notation, found {value!r}")

    check_default_colours(doc, color, rep)
    check_neutrals(doc, rep)

    if len(color) > 12:
        rep.warn("T9", "color", f"{len(color)} colours declared; twelve is the ceiling this skill recommends")

    dark = get(doc, "color_dark")
    if dark is not None:
        if not isinstance(dark, dict):
            rep.error("T1", "color_dark", "must be an object")
            return
        for key, value in dark.items():
            if key not in color:
                rep.error("T3", f"color_dark.{key}", "has no counterpart in color")
            if not isinstance(value, str) or not OKLCH.match(value.strip()):
                rep.error("T2", f"color_dark.{key}", f"expected oklch(...) notation, found {value!r}")


def check_default_colours(doc, color, rep):
    """T20 - a colour equal to a known default needs a recorded decision behind it. One error per key."""
    data = colour.load_defaults()
    provenance = get(doc, "meta.provenance")
    provenance = provenance if isinstance(provenance, dict) else {}
    flagged = set()

    def undecided(key):
        return not str(provenance.get(f"color.{key}", "")).startswith(DECIDED_PREFIXES)

    def flag(key, message):
        if key not in flagged:
            flagged.add(key)
            rep.error("T20", f"color.{key}", message)

    for key in ("primary", "accent"):
        value = color.get(key)
        match = colour.match_default(value, threshold=colour.THRESHOLD, data=data) if isinstance(value, str) else None
        if match and undecided(key):
            flag(key, f"{value} matches the default {match}; take the colour from the brand, the reference or the user "
                      "and record it as brand:, reference: or user: in meta.provenance")
    background = color.get("background")
    if isinstance(background, str) and colour.match_default(background, names=["cream"], data=data) and undecided("background"):
        flag("background", "matches the default cream ground; record a brand:, reference: or user: source in meta.provenance")
    dark = get(doc, "color_dark.background")
    ground = [g for g in (background, dark) if isinstance(g, str)]
    cyan = data.get("cyan_on_dark")
    palette = [v for table in (color, get(doc, "color_dark")) if isinstance(table, dict) for v in table.values() if isinstance(v, str)]
    for key in ("primary", "accent"):
        value = color.get(key)
        if isinstance(value, str) and undecided(key) and any(colour.match_acid_green(value, g, data=data) for g in ground):
            flag(key, f"{value} is acid green beside a near-black ground, a default of generated screens; "
                      "record a brand:, reference: or user: source in meta.provenance")
        if cyan and isinstance(value, str) and undecided(key) and any(match_cyan_on_dark(value, g, cyan, palette) for g in ground):
            flag(key, f"{value} is cyan beside a near-black ground with a purple in the palette, the pairing of generated screens; "
                      "record a brand:, reference: or user: source in meta.provenance")


def oklch_to_rgb(text):
    """(r, g, b) in 0-255, clipped to sRGB, for an oklch(...) string; None when it does not parse."""
    parsed = colour.parse_oklch(text)
    if parsed is None:
        return None
    lightness, chroma, hue = parsed
    a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    l_, m_, s_ = ((lightness + x) ** 3 for x in (0.3963377774 * a + 0.2158037573 * b,
                                                 -0.1055613458 * a - 0.0638541728 * b,
                                                 -0.0894841775 * a - 1.2914855480 * b))
    linear = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
              -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
              -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
    return tuple(255 * min(1.0, max(0.0, 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)) for v in linear)


def hsl_hue_saturation(rgb):
    """(hue in degrees, saturation 0-1) of an (r, g, b) in 0-255, as CSS hsl() reads it."""
    r, g, b = (c / 255 for c in rgb)
    high, low = max(r, g, b), min(r, g, b)
    if high == low:
        return 0.0, 0.0
    delta = high - low
    hue = (60 * ((g - b) / delta % 6) if high == r else 60 * ((b - r) / delta + 2) if high == g else 60 * ((r - g) / delta + 4))
    return hue, delta / (1 - abs(high + low - 1))


def relative_luminance(rgb):
    def linear(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linear(rgb[0]) + 0.7152 * linear(rgb[1]) + 0.0722 * linear(rgb[2])


def in_tell_band(rgb, low, high, rule):
    """A neon colour (channels spread by 80 or more) whose HSL hue lies in [low, high]."""
    hue, _ = hsl_hue_saturation(rgb)
    return max(rgb) - min(rgb) >= rule["min_channel_spread"] and low - 1e-6 <= hue <= high + 1e-6


def match_cyan_on_dark(value, background, rule, palette):
    """impeccable ai-color-palette (core/src/checks/element_checks.rs:4233-4243): a cyan beside a near-black ground,
    reported once a second tell hue (a purple) sits in the palette.

    The cyan lies at HSL hue 170-197 and saturation 0.4 or more; the purple at HSL hue 260-310; the ground has a
    relative luminance under 0.1. palette holds every colour of the token set.
    """
    ink, ground = oklch_to_rgb(value), oklch_to_rgb(background)
    if ink is None or ground is None:
        return False
    hue, saturation = hsl_hue_saturation(ink)
    if saturation < rule["min_saturation"] or not in_tell_band(ink, rule["hsl_hue_min"], rule["hsl_hue_max"], rule):
        return False
    if relative_luminance(ground) >= rule["background_max_luminance"]:
        return False
    second = rule["second_tell"]
    return any(rgb is not None and in_tell_band(rgb, second["hsl_hue_min"], second["hsl_hue_max"], rule)
               for rgb in (oklch_to_rgb(other) for other in palette))


def check_neutrals(doc, rep):
    """T21 - rule 1 of "Deriving the colours": neutrals share the primary hue at low chroma."""
    primary = colour.parse_oklch(get(doc, "color.primary") or "")
    for mode in ("color", "color_dark"):
        palette = get(doc, mode)
        if not isinstance(palette, dict):
            continue
        for key in NEUTRAL_KEYS:
            parsed = colour.parse_oklch(palette.get(key) or "")
            if parsed is None:
                continue
            _, chroma, hue = parsed
            gap = None
            if primary and chroma > NEUTRAL_TINT_CHROMA:
                gap = abs((hue - primary[2] + 180) % 360 - 180)
            if chroma > NEUTRAL_MAX_CHROMA:
                reason = f"chroma {chroma:.3g} is above {NEUTRAL_MAX_CHROMA}"
            elif gap is not None and gap > NEUTRAL_MAX_HUE_GAP:
                reason = f"hue is {gap:.0f} degrees from the primary hue"
            else:
                continue
            rep.warn("T21", f"{mode}.{key}", f"{reason}; neutrals share the primary hue at chroma {NEUTRAL_MAX_CHROMA} or less")


def check_typography(doc, rep):
    typo = get(doc, "typography")
    if not isinstance(typo, dict):
        rep.error("T1", "typography", "required field is missing")
        return

    slots = {k: v for k, v in typo.items() if k != "scale"}
    for required in ("display", "body"):
        if required not in slots:
            rep.error("T1", f"typography.{required}", "required slot is missing")

    if len(slots) > 2:
        rep.error("T4", "typography", f"{len(slots)} font slots declared; two is the maximum")

    families = []
    for key, slot in slots.items():
        family = slot.get("family") if isinstance(slot, dict) else None
        if not family:
            rep.error("T1", f"typography.{key}.family", "required field is missing")
            continue
        families.append(family)
        if any(c in family for c in "\"',"):
            rep.error("T1", f"typography.{key}.family",
                      f"{family!r} must be one bare family name; the template adds the quotes and the fallback")
        leading = family.split(",")[0].strip().strip("'\"").lower()
        if leading in FORBIDDEN_FAMILIES:
            # A named reference means the family was chosen upstream; T5 looks
            # only for a family nobody chose.
            report = rep.warn if get(doc, "meta.reference") else rep.error
            report("T5", f"typography.{key}.family",
                   f"{family!r} is on the forbidden list; see references/tokens-format.md")

        family_ja = slot.get("family_ja")
        if family_ja is not None and (not isinstance(family_ja, str) or any(c in family_ja for c in "\"',")):
            rep.error("T1", f"typography.{key}.family_ja",
                      f"{family_ja!r} must be one bare family name; the template adds the quotes")
        elif get(doc, "voice.lang") == "ja" and not any(
                ja in name for name in (family.lower(), (family_ja or "").lower()) for ja in JA_FAMILIES):
            report = rep.warn if get(doc, "meta.reference") else rep.error
            report("T22", f"typography.{key}.family_ja",
                   f"{family!r} has no Japanese glyphs and family_ja is missing or not a Japanese face; "
                   "set family_ja (references/tokens-format.md)")

    if len(set(f.strip().lower() for f in families)) > 2:
        rep.error("T4", "typography", "three or more distinct families")

    ratio = get(doc, "typography.scale.ratio")
    if ratio is None:
        rep.error("T1", "typography.scale.ratio", "required field is missing")
    elif not isinstance(ratio, (int, float)) or not (1.067 <= ratio <= 1.618):
        rep.warn("T12", "typography.scale.ratio", f"{ratio} falls outside 1.067-1.618")

    base_px = get(doc, "typography.scale.base_px")
    if base_px is None:
        rep.error("T1", "typography.scale.base_px", "required field is missing")
    elif not isinstance(base_px, (int, float)) or not (16 <= base_px <= 18):
        rep.error("T1", "typography.scale.base_px", f"{base_px} falls outside 16-18; 16px is the standard body size")


def check_spacing(doc, rep):
    base_px = get(doc, "spacing.base_px")
    if base_px is None:
        rep.error("T1", "spacing.base_px", "required field is missing")
    elif base_px not in (4, 8):
        rep.error("T1", "spacing.base_px", f"expected 4 or 8, found {base_px!r}")

    steps = get(doc, "spacing.steps")
    if not isinstance(steps, list):
        rep.error("T1", "spacing.steps", "required field is missing")
    elif len(steps) < 5:
        rep.error("T1", "spacing.steps", f"{len(steps)} steps; five is the minimum")
    elif steps != sorted(steps):
        rep.error("T1", "spacing.steps", "must be in ascending order")


def check_radius(doc, rep):
    radius = get(doc, "radius")
    if not isinstance(radius, dict):
        rep.error("T1", "radius", "required field is missing")
        return

    missing = [s for s in RADIUS_STEPS if s not in radius]
    if missing:
        rep.error("T6", "radius", f"missing step(s): {', '.join(missing)}")
        return

    scale = [str(radius[s]).strip() for s in RADIUS_STEPS]
    if len(set(scale)) == 1:
        rep.error("T6", "radius", f"all three steps carry {scale[0]!r}; a single radius flattens the hierarchy")


def check_shadow(doc, rep):
    shadow = get(doc, "shadow")
    if not isinstance(shadow, dict):
        rep.error("T1", "shadow", "required field is missing")
        return

    missing = [s for s in SHADOW_STEPS if s not in shadow]
    if missing:
        rep.error("T1", "shadow", f"missing step(s): {', '.join(missing)}")
        return

    alphas = [shadow_alpha(str(shadow[step])) for step in SHADOW_STEPS]
    if None not in alphas and len(set(alphas)) == 1:
        rep.warn("T10", "shadow", f"every step uses alpha {alphas[0]:g}")


def check_motion(doc, rep):
    for name in ("fast", "base", "slow"):
        value = get(doc, f"motion.duration.{name}")
        if value is None:
            rep.error("T1", f"motion.duration.{name}", "required field is missing")
        elif not MS.match(str(value).strip()):
            rep.error("T1", f"motion.duration.{name}", f"expected a value in ms, found {value!r}")

    base = get(doc, "motion.duration.base")
    found = MS.match(str(base).strip()) if base else None
    if found:
        ms = float(found.group(1))
        if not (120 <= ms <= 400):
            rep.warn("T11", "motion.duration.base", f"{ms:g}ms falls outside 120-400ms")

    if get(doc, "motion.easing.standard") is None:
        rep.error("T1", "motion.easing.standard", "required field is missing")


def check_voice(doc, rep):
    voice = get(doc, "voice")
    if not isinstance(voice, dict):
        rep.error("T13", "voice", "required field is missing; settle the wording before any string is written")
        return

    lang = voice.get("lang")
    if lang not in ("ja", "en"):
        rep.error("T13", "voice.lang", f"expected 'ja' or 'en', found {lang!r}")

    if lang == "ja":
        register = voice.get("register")
        if register not in ("敬体", "常体"):
            rep.error("T14", "voice.register", f"expected '敬体' or '常体', found {register!r}")
    elif lang == "en":
        case = voice.get("case")
        if case not in ("sentence", "title"):
            rep.error("T15", "voice.case", f"expected 'sentence' or 'title', found {case!r}")

    terms = voice.get("terms")
    if terms is None:
        rep.error("T13", "voice.terms", "required field is missing (write {} when nothing is settled yet)")
    elif not isinstance(terms, dict):
        rep.error("T13", "voice.terms", "must be an object mapping a word to stop using to the word to use")
    else:
        for key, value in terms.items():
            if key == value:
                rep.error("T16", f"voice.terms.{key}", "maps a word to itself")
            elif value in terms:
                rep.error("T16", f"voice.terms.{key}",
                          f"replacement {value!r} is itself a key, so the check contradicts itself")
        if not terms and lang == "ja":
            rep.warn("T17", "voice.terms", "empty; settle the word for each operation the screens offer (references/ui-copy.md)")

    choon = voice.get("katakana_choon")
    if choon is not None and choon not in ("jtf", "wordrabbit"):
        rep.error("T13", "voice.katakana_choon", f"expected 'jtf' or 'wordrabbit', found {choon!r}")

    allow = voice.get("allow")
    if allow is not None and not isinstance(allow, list):
        rep.error("T13", "voice.allow", "must be an array of strings")


def validate(doc):
    rep = Report()
    check_meta(doc, rep)
    check_provenance(doc, rep)
    check_logo(doc, rep)
    check_users(doc, rep)
    check_voice(doc, rep)
    check_color(doc, rep)
    check_typography(doc, rep)
    check_spacing(doc, rep)
    check_radius(doc, rep)
    check_shadow(doc, rep)
    check_motion(doc, rep)
    return rep


def main():
    parser = argparse.ArgumentParser(description="Validate a product-ui tokens.json.")
    parser.add_argument("tokens", help="path to tokens.json")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    try:
        with open(args.tokens, encoding="utf-8") as handle:
            doc = json.load(handle)
    except FileNotFoundError:
        print(f"FAIL: no such file: {args.tokens}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: {args.tokens} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    rep = validate(doc)
    status = "FAIL" if rep.errors else "PASS"

    if args.json:
        print(json.dumps({
            "status": status,
            "error_count": len(rep.errors),
            "warning_count": len(rep.warnings),
            "errors": rep.errors,
            "warnings": rep.warnings,
        }, indent=2))
    else:
        for item in rep.errors:
            print(f"ERROR [{item['id']}] {item['path']}: {item['message']}")
        for item in rep.warnings:
            print(f"WARN  [{item['id']}] {item['path']}: {item['message']}")
        print(f"{status}: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
