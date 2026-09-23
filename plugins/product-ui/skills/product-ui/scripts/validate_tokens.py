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
import re
import sys

OKLCH = re.compile(r"^oklch\(\s*[^)]+\)$", re.IGNORECASE)
MS = re.compile(r"^(\d+(?:\.\d+)?)ms$")

# Families a model reaches for when no choice has been made. See S2 in
# references/slop-checklist.md for the same list applied to generated markup.
FORBIDDEN_FAMILIES = {
    "inter", "roboto", "open sans", "lato", "arial", "helvetica",
    "system-ui", "-apple-system", "space grotesk", "poppins", "montserrat",
}

# T8: permitted surface/renderer pairings, from references/stack-defaults.md.
PAIRINGS = {
    ("saas", "vite-react"),
    ("saas", "next-react"),
    ("lp", "astro-react"),
    ("lp", "next-react"),
    ("lp", "html"),
}

# T8 warns instead of failing on these: an existing project the skill did not
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

ALPHA = re.compile(r"/\s*(\d*\.?\d+)\s*\)")


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
        if family.strip().lower() in FORBIDDEN_FAMILIES:
            # A named reference means the family was chosen upstream rather than
            # defaulted to, which is the only thing T5 is looking for.
            report = rep.warn if get(doc, "meta.reference") else rep.error
            report("T5", f"typography.{key}.family",
                   f"{family!r} is on the forbidden list; see references/tokens-format.md")

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

    alphas = set()
    for step in SHADOW_STEPS:
        found = ALPHA.search(str(shadow[step]))
        if found:
            alphas.add(found.group(1))
    if len(alphas) == 1:
        rep.warn("T10", "shadow", f"every step uses alpha {alphas.pop()}")


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

    allow = voice.get("allow")
    if allow is not None and not isinstance(allow, list):
        rep.error("T13", "voice.allow", "must be an array of strings")


def validate(doc):
    rep = Report()
    check_meta(doc, rep)
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
