#!/usr/bin/env python3
"""product-ui: generate theme.css from tokens.json.

Standard library only. Fills assets/theme.template.css from a tokens.json that
validate_tokens.py has already passed. Runs in Step 2, after validation, never
before it.

Rules:
    {{a.b.c}}       replaced by that value from tokens.json. A missing value fails
                    the run, except for the optional tokens below, whose line is
                    dropped
    --brand-surface any line naming it is dropped when color.surface is absent;
                    radius.full and motion.easing.spring are the other optional ones
    {{color_dark}}  expands to a .dark block with one --brand-<key> line per key
                    in color_dark, or to nothing when color_dark is absent
    {{type_ramp}}   expands to the --text-base ... --text-9xl lines: base is
                    typography.scale.base_px, each step above multiplies by
                    typography.scale.ratio; line heights are unitless
    {{spacing_unit}} expands to --spacing: <spacing.base_px / 16>rem;
    {{body_text}}   expands to the body line-height and letter-spacing for voice.lang
                    and meta.surface; the same line height goes to --text-base
    {{family_ja.display}}, {{family_ja.body}}
                    expand to "<typography.<slot>.family_ja>", or to nothing when
                    the slot has no family_ja

CLI:
    python generate_theme.py <tokens.json> [--out theme.css] [--template path]

Without --out, theme.css is written beside tokens.json.

Exit codes: 0 = written, 1 = tokens.json unreadable or a required placeholder unfilled.
"""

import argparse
import json
import os
import re
import sys

PLACEHOLDER = re.compile(r"\{\{([a-z_]+(?:\.[a-z_]+)+)\}\}")
DARK_MARKER = "{{color_dark}}"
RAMP_MARKER = "{{type_ramp}}"
SPACING_MARKER = "{{spacing_unit}}"
BODY_MARKER = "{{body_text}}"
FAMILY_JA = re.compile(r"\{\{family_ja\.(display|body)\}\}")

# Line heights of Tailwind's own steps, unitless, for text-base and up.
LINE_HEIGHTS = [1.5, 1.556, 1.4, 1.333, 1.2, 1.111, 1, 1, 1, 1, 1]
STEPS = ["base", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl", "7xl", "8xl", "9xl"]


def body_leading(doc):
    """Body line height and letter spacing: DADS reading text for ja on a landing page,
    1.5 and no tracking otherwise (SmartHR paragraphs, WCAG 1.4.8)."""
    if get(doc, "voice.lang") == "ja" and get(doc, "meta.surface") == "lp":
        return 1.7, "0.02em"
    return 1.5, "0"


# tokens-format.md does not require these; their line is dropped when absent.
OPTIONAL = {"color.surface", "radius.full", "motion.easing.spring"}


def get(doc, path):
    node = doc
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def dark_block(color_dark):
    if not color_dark:
        return ""
    lines = [f"  --brand-{key.replace('_', '-')}: {value};" for key, value in color_dark.items()]
    return ".dark {\n" + "\n".join(lines) + "\n}"


def rem(value):
    """Round to two places and print without trailing zeros, as 1rem or 1.25rem."""
    return f"{round(value, 2):g}rem"


def ja_line_height(size_px, body_height):
    """Line height of a Japanese step by its size, after DADS's standard text styles:
    160% at 18px, 150% from 20 to 32px, 140% from 36px."""
    if size_px < 18:
        return body_height
    if size_px < 20:
        return 1.6
    if size_px < 36:
        return 1.5
    return 1.4


def type_ramp(base_px, ratio, body_height, lang=None):
    sizes = [base_px * ratio ** n for n in range(len(STEPS))]
    if lang == "ja":
        heights = [body_height] + [ja_line_height(size, body_height) for size in sizes[1:]]
    else:
        heights = [body_height] + LINE_HEIGHTS[1:]
    return [f"--text-{step}: {rem(size / 16)}; --text-{step}--line-height: {height:g};"
            for step, size, height in zip(STEPS, sizes, heights)]


def render(template, doc):
    """Return (css, unfilled). unfilled lists placeholders that had no value and
    were not on a droppable line."""
    has_surface = get(doc, "color.surface") is not None
    out, unfilled = [], []
    for line in template.split("\n"):
        if line.strip() == DARK_MARKER:
            block = dark_block(get(doc, "color_dark"))
            if block:
                out.append(block)
            continue
        if line.strip() in (RAMP_MARKER, SPACING_MARKER):
            indent = line[:len(line) - len(line.lstrip())]
            if line.strip() == RAMP_MARKER:
                base_px, ratio = get(doc, "typography.scale.base_px"), get(doc, "typography.scale.ratio")
                if base_px is None or ratio is None:
                    unfilled.extend(k for k, v in (("typography.scale.base_px", base_px),
                                                   ("typography.scale.ratio", ratio)) if v is None)
                    continue
                out.extend(indent + text for text in type_ramp(base_px, ratio, body_leading(doc)[0],
                                                               get(doc, "voice.lang")))
            else:
                unit = get(doc, "spacing.base_px")
                if unit is None:
                    unfilled.append("spacing.base_px")
                    continue
                out.append(f"{indent}--spacing: {rem(unit / 16)};")
            continue
        if line.strip() == BODY_MARKER:
            indent = line[:len(line) - len(line.lstrip())]
            height, tracking = body_leading(doc)
            out.extend([f"{indent}line-height: {height:g};", f"{indent}letter-spacing: {tracking};"])
            continue
        line = FAMILY_JA.sub(lambda m: f'"{get(doc, f"typography.{m.group(1)}.family_ja")}", '
                             if get(doc, f"typography.{m.group(1)}.family_ja") else "", line)
        if "--brand-surface" in line and not has_surface:
            continue
        missing = []

        def fill(match):
            value = get(doc, match.group(1))
            if value is None:
                missing.append(match.group(1))
                return match.group(0)
            return str(value)

        filled = PLACEHOLDER.sub(fill, line)
        if missing:
            if all(key in OPTIONAL for key in missing):
                continue
            unfilled.extend(key for key in missing if key not in OPTIONAL)
        out.append(filled)
    css = "\n".join(out)
    css = re.sub(r"\n{3,}", "\n\n", css)
    return css, unfilled


def main():
    parser = argparse.ArgumentParser(description="Generate theme.css from a product-ui tokens.json.")
    parser.add_argument("tokens", help="path to tokens.json")
    parser.add_argument("--out", help="where to write theme.css (default: beside tokens.json)")
    parser.add_argument("--template", help="template path (default: assets/theme.template.css)")
    args = parser.parse_args()

    try:
        with open(args.tokens, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read {args.tokens}: {exc}", file=sys.stderr)
        return 1

    here = os.path.dirname(os.path.abspath(__file__))
    template_path = args.template or os.path.join(here, "..", "assets", "theme.template.css")
    with open(template_path, encoding="utf-8") as handle:
        template = handle.read()

    css, unfilled = render(template, doc)
    if unfilled:
        print("FAIL: unfilled placeholders: " + ", ".join(sorted(set(unfilled))), file=sys.stderr)
        return 1

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.tokens)), "theme.css")
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(css if css.endswith("\n") else css + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
