#!/usr/bin/env python3
"""product-ui: compare captured specimens with a pattern.

Standard library only. Reads specimen files written by specimen.py and one pattern from
patterns/, maps each specimen's parts onto the pattern's slots, and reports whether the
specimen carries every required slot, in the pattern's order. The source of record is
references/patterns.md, "Adding a pattern from specimens".

A part maps to a slot by what it holds:

- a heading, or the first link of the item when no value comes before it: the identifier
- a part whose value is a status word: status
- an image: image
- any other link, or a button: action
- a value typed date, time, money, percent, count, number or free text: property
  (an id-typed value is the identifier when the item has none yet)

Two or more specimens from different sources that fit, with no required slot missing, are
the evidence a pattern needs for `evidence_status: cross-specimen`; a pattern most real
specimens fail is one to revise before its checks become errors.

CLI:
    python compare.py <pattern id> <specimen.json>... [--json]

Exit codes: 0 = compared, 1 = no such pattern or no readable specimen.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "patterns"))
import library  # noqa: E402

PROPERTY_TYPES = ("date", "time", "money", "percent", "count", "number", "free")


def map_parts(anatomy):
    """The takes each part fills, in reading order."""
    out, have_id, links = [], False, 0
    for part in anatomy:
        role, kind = part["role"], part["type"]
        if role == "heading" or (role == "link" and links == 0 and not have_id and "property" not in out):
            out.append("identifier")
            have_id = True
        elif role == "link" or role == "button":
            out.append("action")
        elif role == "image":
            out.append("image")
        elif kind == "status":
            out.append("status")
        elif kind == "id" and not have_id:
            out.append("identifier")
            have_id = True
        elif kind in PROPERTY_TYPES or kind == "id":
            out.append("property")
        else:
            continue
        if role == "link":
            links += 1
    return out


def fit(pattern, takes):
    """(missing required slots, whether the mapped slots follow the pattern's order)."""
    counts = {}
    for t in takes:
        counts[t] = counts.get(t, 0) + 1
    alias = {"price": "property", "rating": "property", "variations": "property", "label": "property", "text": "property"}
    missing = []
    for slot in pattern["slots"]:
        if not slot.get("required"):
            continue
        want = alias.get(slot["takes"], slot["takes"])
        need = slot.get("min", 1)
        if counts.get(want, 0) < need:
            missing.append(slot["id"])
        else:
            counts[want] -= need
    order = [alias.get(s["takes"], s["takes"]) for s in pattern["slots"]]
    positions = [order.index(t) for t in takes if t in order]
    return missing, positions == sorted(positions)


def main():
    parser = argparse.ArgumentParser(description="Compare captured specimens with a pattern.")
    parser.add_argument("pattern")
    parser.add_argument("specimens", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    patterns = library.load_library()
    if args.pattern not in patterns:
        print(f"FAIL: no pattern `{args.pattern}` in patterns/")
        return 1
    pattern = patterns[args.pattern]
    rows = []
    for path in args.specimens:
        try:
            with open(path, encoding="utf-8") as handle:
                spec = json.load(handle)
        except (OSError, ValueError):
            continue
        takes = map_parts(spec.get("anatomy", []))
        missing, ordered = fit(pattern, takes)
        rows.append({"specimen": spec.get("id"), "source": (spec.get("source") or {}).get("url"),
                     "maps_to": takes, "missing": missing, "in_order": ordered, "fits": not missing})
    if not rows:
        print("FAIL: no readable specimen")
        return 1
    fits = sum(1 for r in rows if r["fits"])
    if args.json:
        print(json.dumps({"pattern": args.pattern, "fits": fits, "specimens": rows}, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            verdict = "fits" if r["fits"] else "misses " + ", ".join(r["missing"])
            print(f"{r['specimen']}: {' → '.join(r['maps_to'])}: {verdict}" + ("" if r["in_order"] else "; out of order"))
        print(f"{args.pattern}: {fits} of {len(rows)} specimen(s) fit")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
