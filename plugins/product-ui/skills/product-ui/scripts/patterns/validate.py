#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) validation of the pattern library.

Standard library only. Checks every pattern file under patterns/ and the decision table
patterns/index.json. The source of record for these rules is references/patterns.md;
change that file first when a rule changes.

Errors mean a pattern or the table cannot be used: resolve.py, scaffold.py or
check_pattern.py would read it wrongly. Warnings mean it can be used but something in the
library is unreachable.

CLI:
    python validate.py [<patterns dir>] [--json]

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors).
"""

import argparse
import itertools
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library  # noqa: E402

ID = re.compile(r"^[a-z]+(\.[a-z0-9-]+)+$")


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, check_id, path, message):
        self.errors.append({"id": check_id, "path": path, "message": message})

    def warn(self, check_id, path, message):
        self.warnings.append({"id": check_id, "path": path, "message": message})


def check_pattern(name, doc, rep):
    """PV1 to PV5 on one pattern file."""
    if not isinstance(doc, dict):
        rep.error("PV1", name, "a pattern file holds one JSON object")
        return
    for key, kind in library.PATTERN_KEYS.items():
        if key not in doc:
            rep.error("PV1", name, f"missing field `{key}`")
        elif not isinstance(doc[key], kind):
            rep.error("PV1", name, f"`{key}` must be a {kind.__name__}")
    pid = doc.get("id")
    if isinstance(pid, str):
        if not ID.match(pid):
            rep.error("PV2", name, f"id `{pid}` is not dotted lower case (`collection.row.resource`)")
        if name != pid + ".json":
            rep.error("PV2", name, f"the file name must be the id: `{pid}.json`")
    if doc.get("kind") not in library.KINDS:
        rep.error("PV1", name, f"kind `{doc.get('kind')}` is outside {', '.join(library.KINDS)}")

    seen = set()
    for i, slot in enumerate(doc.get("slots") or []):
        where = f"{name} slots[{i}]"
        if not isinstance(slot, dict) or not isinstance(slot.get("id"), str):
            rep.error("PV3", where, "a slot is an object with a string `id`")
            continue
        if slot["id"] in seen:
            rep.error("PV3", where, f"slot `{slot['id']}` appears twice")
        seen.add(slot["id"])
        if slot.get("takes") not in library.TAKES:
            rep.error("PV3", where, f"takes `{slot.get('takes')}` is outside {', '.join(library.TAKES)}")
        if not isinstance(slot.get("required"), bool):
            rep.error("PV3", where, "`required` must be true or false")
        lo, hi = slot.get("min"), slot.get("max", 1)
        if hi is not None and (not isinstance(hi, int) or hi < 1):
            rep.error("PV3", where, "`max` is a whole number of 1 or more, or null for no limit")
        if lo is not None and (not isinstance(lo, int) or lo < 0 or (isinstance(hi, int) and lo > hi)):
            rep.error("PV3", where, "`min` is a whole number from 0 to `max`")
        if slot.get("required") and lo == 0:
            rep.error("PV3", where, "a required slot cannot take `min: 0`")
    if not doc.get("slots"):
        rep.error("PV3", name, "a pattern has at least one slot")
    elif not any(s.get("required") for s in doc["slots"] if isinstance(s, dict)):
        rep.error("PV3", name, "a pattern has at least one required slot")

    evidence_ids = set()
    for i, ev in enumerate(doc.get("evidence") or []):
        where = f"{name} evidence[{i}]"
        if not isinstance(ev, dict):
            rep.error("PV5", where, "an evidence entry is an object")
            continue
        for key in ("id", "source", "url", "says"):
            if not isinstance(ev.get(key), str) or not ev.get(key).strip():
                rep.error("PV5", where, f"missing `{key}`")
        if isinstance(ev.get("url"), str) and not ev["url"].startswith("https://"):
            rep.error("PV5", where, "the url starts with https://")
        evidence_ids.add(ev.get("id"))
    if not doc.get("evidence"):
        rep.error("PV5", name, "a pattern names at least one source")
    if doc.get("evidence_status") not in library.EVIDENCE_STATUS:
        rep.error("PV5", name, f"evidence_status is one of {', '.join(library.EVIDENCE_STATUS)}")

    for i, rule in enumerate(doc.get("rules") or []):
        where = f"{name} rules[{i}]"
        if not isinstance(rule, dict) or not isinstance(rule.get("rule"), str) or not isinstance(rule.get("from"), list):
            rep.error("PV5", where, "a rule is an object with `rule` (text) and `from` (a list)")
            continue
        for ref in rule["from"]:
            if ref != library.OWN_RULE and ref not in evidence_ids:
                rep.error("PV5", where, f"`from` names `{ref}`, which is neither an evidence id of this pattern nor `{library.OWN_RULE}`")

    for stack in (doc.get("maps_to") or {}):
        if stack not in library.STACKS:
            rep.error("PV1", f"{name} maps_to", f"`{stack}` is outside {', '.join(library.STACKS)}")


def check_index(index, patterns, rep):
    """PV6 and PV7 on the decision table."""
    rows = index.get("rows") if isinstance(index, dict) else None
    if not isinstance(rows, list) or not rows:
        rep.error("PV6", library.INDEX_FILE, "the table holds a non-empty `rows` list")
        return set()
    reached = set()
    for i, row in enumerate(rows):
        where = f"{library.INDEX_FILE} rows[{i}]"
        if row.get("content") not in library.CONTENT:
            rep.error("PV6", where, f"content `{row.get('content')}` is outside {', '.join(library.CONTENT)}")
        if "job" in row and (not isinstance(row["job"], list) or not set(row["job"]) <= set(library.JOBS)):
            rep.error("PV6", where, f"job is a list drawn from {', '.join(library.JOBS)}")
        if "compare" in row and not isinstance(row["compare"], bool):
            rep.error("PV6", where, "compare is true or false")
        pid = row.get("pattern")
        if pid is None:
            if not isinstance(row.get("say"), str) or not row["say"].strip():
                rep.error("PV6", where, "a row without a pattern says why in `say`")
        elif pid not in patterns:
            rep.error("PV6", where, f"pattern `{pid}` has no file")
        else:
            reached.add(pid)
    for content, job, compare in itertools.product(library.CONTENT, library.JOBS, (True, False)):
        hits = [r for r in rows if library.row_matches(r, content, job, compare)]
        case = f"content {content}, job {job}, compare {'yes' if compare else 'no'}"
        if not hits:
            rep.error("PV7", library.INDEX_FILE, f"no row admits {case}")
        elif len(hits) > 1:
            rep.error("PV7", library.INDEX_FILE, f"{len(hits)} rows admit {case}")
    return reached


def validate(directory):
    rep = Report()
    patterns = {}
    for name in library.pattern_files(directory):
        try:
            with open(os.path.join(directory, name), encoding="utf-8") as handle:
                doc = json.load(handle)
        except ValueError as exc:
            rep.error("PV1", name, f"not valid JSON: {exc}")
            continue
        check_pattern(name, doc, rep)
        if isinstance(doc, dict) and isinstance(doc.get("id"), str):
            if doc["id"] in patterns:
                rep.error("PV2", name, f"id `{doc['id']}` is used by another file")
            patterns[doc["id"]] = doc
    for pid, doc in patterns.items():
        for used in doc.get("uses") or []:
            if used not in patterns:
                rep.error("PV4", f"{pid}.json uses", f"`{used}` has no file")
    try:
        index = library.load_index(directory)
    except (OSError, ValueError) as exc:
        rep.error("PV6", library.INDEX_FILE, f"cannot read the table: {exc}")
        return rep
    reached = check_index(index, patterns, rep)
    used = {u for doc in patterns.values() for u in (doc.get("uses") or [])}
    for pid in sorted(set(patterns) - reached - used):
        rep.warn("PV8", f"{pid}.json", "no table row selects it and no pattern uses it")
    return rep


def main():
    parser = argparse.ArgumentParser(description="Validate the product-ui pattern library.")
    parser.add_argument("dir", nargs="?", default=library.PATTERN_DIR, help="the patterns directory")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    if not os.path.isdir(args.dir):
        print(f"FAIL: no such directory: {args.dir}", file=sys.stderr)
        return 1
    rep = validate(args.dir)
    status = "FAIL" if rep.errors else "PASS"
    if args.json:
        print(json.dumps({"status": status, "error_count": len(rep.errors), "warning_count": len(rep.warnings),
                          "errors": rep.errors, "warnings": rep.warnings}, indent=2, ensure_ascii=False))
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
