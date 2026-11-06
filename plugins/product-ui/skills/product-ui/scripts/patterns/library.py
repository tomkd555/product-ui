"""product-ui: the pattern library and its decision table, read by validate.py, resolve.py,
scaffold.py and check_pattern.py.

Standard library only. The source of record for the format is references/patterns.md;
change that file first when a field or a vocabulary changes.
"""

import json
import os

SKILL_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PATTERN_DIR = os.path.join(SKILL_DIR, "patterns")
INDEX_FILE = "index.json"

# What a section of a screen holds; the brief's `content` value.
CONTENT = ("records", "record-header", "record-detail", "record-fields", "items", "products",
           "measures", "tasks", "form", "prose")
JOBS = ("monitor", "enter", "lookup", "decide")
KINDS = ("collection-row", "collection-table", "record-header", "record-body", "record-fields",
         "task-list", "card", "product-item", "badge", "empty-state", "tile")
# What a slot holds. resolve.py fills identifier, status, image, property, price, rating and
# variations from the brief's Objects table; the rest are written by hand on the screen.
TAKES = ("identifier", "status", "image", "property", "price", "rating", "variations",
         "action", "label", "text", "link", "control", "count", "measure", "comparison", "section")
# A pattern of these kinds describes one item, and each item carries data-pattern; the other
# kinds describe the whole block, which carries it once.
ITEM_KINDS = ("collection-row", "task-list", "card", "product-item", "tile", "badge")
OBJECT_TAKES = ("identifier", "status", "image", "property", "price", "rating", "variations")
STACKS = ("shadcn", "html", "dads", "smarthr")
EVIDENCE_STATUS = ("documented", "cross-specimen", "inferred")
OWN_RULE = "product-ui"

PATTERN_KEYS = {
    "id": str, "version": int, "kind": str, "summary": str, "not_for": str, "slots": list,
    "rules": list, "labels": dict, "uses": list, "maps_to": dict, "evidence": list,
    "evidence_status": str,
}


def pattern_files(directory=PATTERN_DIR):
    return sorted(f for f in os.listdir(directory) if f.endswith(".json") and f != INDEX_FILE)


def load_library(directory=PATTERN_DIR):
    """Every pattern, keyed by id. A file that does not parse is skipped here; validate.py reports it."""
    library = {}
    for name in pattern_files(directory):
        try:
            with open(os.path.join(directory, name), encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict) and isinstance(doc.get("id"), str):
            library[doc["id"]] = doc
    return library


def load_index(directory=PATTERN_DIR):
    with open(os.path.join(directory, INDEX_FILE), encoding="utf-8") as handle:
        return json.load(handle)


def row_matches(row, content, job, compare):
    """Whether a decision-table row admits a section. A key the row leaves out matches anything;
    a key the row sets and the section leaves unknown (None) matches nothing."""
    if row.get("content") != content:
        return False
    if "job" in row and job not in row["job"]:
        return False
    if "compare" in row and (compare is None or row["compare"] != compare):
        return False
    return True


def decide(index, content, job, compare):
    """(rows that match, the keys a row needs that the section left unknown)."""
    rows = [r for r in index.get("rows", []) if row_matches(r, content, job, compare)]
    needs = sorted({k for r in index.get("rows", []) if r.get("content") == content
                    for k in ("job", "compare") if k in r and {"job": job, "compare": compare}[k] is None})
    return rows, needs


def slot_order(pattern):
    return [s["id"] for s in pattern.get("slots", [])]


def required_slots(pattern):
    return [s["id"] for s in pattern.get("slots", []) if s.get("required")]
