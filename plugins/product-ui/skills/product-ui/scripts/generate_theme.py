#!/usr/bin/env python3
"""product-ui: generate theme.css from tokens.json.

Standard library only. Fills assets/theme.template.css from a tokens.json that
validate_tokens.py has already passed. Runs in Step 2, after validation, never
before it.

Rules:
    {{a.b.c}}       replaced by that value from tokens.json. A missing value fails
                    the run, except for the optional tokens below, whose line is
                    dropped instead
    --brand-surface any line naming it is dropped when color.surface is absent;
                    radius.full and motion.easing.spring are the other optional ones
    {{color_dark}}  expands to a .dark block with one --brand-<key> line per key
                    in color_dark, or to nothing when color_dark is absent

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
