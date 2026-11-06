#!/usr/bin/env python3
"""product-ui: choose each section's pattern and fill its slots, deterministically.

Standard library only. Reads ui-brief.md: the `## Objects` table, and in each Composition
block the `- Job class:` line and the `- Sections:` list. For every section it looks the
pattern up in patterns/index.json, writes the id back into the section's line, and writes the
`## Slots` table: which property of the object each slot shows. The source of record for these
rules is references/patterns.md; change that file first when a rule changes.

The same brief gives the same pattern ids and the same Slots table on every run. A section
the table cannot decide stops the run with the question that decides it: nothing is guessed.

CLI:
    python resolve.py <ui-brief.md> [--check] [--json]

--check writes nothing and fails when the brief is not what a run would write.

Exit codes: 0 = resolved (or, with --check, up to date), 1 = a section cannot be resolved,
or (with --check) the brief is out of date.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library  # noqa: E402

SECTION_HEAD = re.compile(r"^## (?P<name>.+?)\s*$")
BLOCK_HEAD = re.compile(r"^### (?P<name>.+?)\s*$")
JOB_LINE = re.compile(r"^\s*-\s*Job class:\s*`?(?P<job>[a-z]+)`?", re.IGNORECASE)
SECTIONS_LINE = re.compile(r"^(?P<indent>\s*)-\s*Sections:\s*$")
SECTION_ITEM = re.compile(r"^(?P<indent>\s+)-\s*(?P<name>[^:]+?):\s*(?P<body>.+?)\s*$")
TAG = re.compile(r"^(?P<name>.+?)\s*\[(?P<tag>price|rating|variations)\]$")
NONE = {"", "none", "-", "—", "なし"}
OBJECT_CONTENT = {"records", "record-header", "record-detail", "record-fields", "items", "products", "tasks"}
SLOTS_INTRO = ("Written by `scripts/patterns/resolve.py` from the `- Sections:` lines and the `## Objects` table. "
               "Change those and run it again; an edit here is overwritten.")


class Stop(Exception):
    """A section the brief does not settle."""


def split_sections(lines):
    """[(name, start, end)] for each `## ` section; end is exclusive."""
    heads = [(i, SECTION_HEAD.match(line).group("name")) for i, line in enumerate(lines) if SECTION_HEAD.match(line)]
    out = []
    for n, (start, name) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        out.append((name, start, end))
    return out


def find_section(lines, title):
    for name, start, end in split_sections(lines):
        if name.strip().lower() == title.lower():
            return start, end
    return None


def table_rows(lines):
    """The data rows of the first Markdown table in lines, as lists of cells."""
    rows, seen_rule = [], False
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            if rows or seen_rule:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            seen_rule = True
            continue
        if seen_rule:
            rows.append(cells)
    return rows


def read_objects(lines):
    found = find_section(lines, "Objects")
    if not found:
        return {}
    objects = {}
    for cells in table_rows(lines[found[0] + 1:found[1]]):
        if len(cells) < 5 or cells[0] in NONE or cells[0].startswith("{{"):
            continue
        props, tagged = [], {}
        for raw in [p.strip() for p in re.split(r"[,、]", cells[4]) if p.strip()]:
            m = TAG.match(raw)
            if m:
                tagged.setdefault(m.group("tag"), []).append(m.group("name").strip())
            else:
                props.append(raw)
        objects[cells[0]] = {
            "identifier": None if cells[1] in NONE else cells[1],
            "status": None if cells[2] in NONE else cells[2],
            "image": None if cells[3] in NONE else cells[3],
            "properties": props,
            "tagged": tagged,
        }
    return objects


def parse_body(body):
    fields = {}
    for part in [p.strip() for p in body.split(";") if p.strip()]:
        key, _, value = part.partition(" ")
        fields[key.strip().lower()] = value.strip()
    return fields


def yes_no(value, key, where):
    if value is None or value == "":
        return None
    if value.lower() in ("yes", "true", "はい"):
        return True
    if value.lower() in ("no", "false", "いいえ"):
        return False
    raise Stop(f"{where}: `{key}` is yes or no, not `{value}`")


def read_blocks(lines):
    """Each Composition block: its screen name, job class and section lines (with line numbers)."""
    found = find_section(lines, "Composition")
    if not found:
        return []
    start, end = found
    heads = [i for i in range(start + 1, end) if BLOCK_HEAD.match(lines[i])]
    spans = [(h, heads[n + 1] if n + 1 < len(heads) else end) for n, h in enumerate(heads)] or [(start, end)]
    blocks = []
    for b_start, b_end in spans:
        name = BLOCK_HEAD.match(lines[b_start]).group("name") if b_start != start else "(screen)"
        job, sections, in_sections = None, [], None
        for i in range(b_start + 1, b_end):
            line = lines[i]
            m = JOB_LINE.match(line)
            if m:
                job = m.group("job").lower()
            m = SECTIONS_LINE.match(line)
            if m:
                in_sections = len(m.group("indent"))
                continue
            if in_sections is not None:
                item = SECTION_ITEM.match(line)
                if item and len(item.group("indent")) > in_sections and not item.group("name").startswith("{{"):
                    sections.append({"line": i, "indent": item.group("indent"), "name": item.group("name").strip(),
                                     "fields": parse_body(item.group("body"))})
                    continue
                if line.strip():
                    in_sections = None
        blocks.append({"screen": name, "job": job, "sections": sections})
    return blocks


def assign(pattern, obj, section, where):
    """The Slots table rows for one section: [(slot, shows, from)]."""
    rows = []
    pool = list(obj["properties"]) if obj else []
    media = section.get("media")
    for slot in pattern["slots"]:
        takes, sid = slot["takes"], slot["id"]
        if takes not in library.OBJECT_TAKES:
            if slot.get("label_of"):
                rows.append((sid, f"the label of each `{slot['label_of']}`", "Objects"))
            elif slot.get("required"):
                rows.append((sid, "(on the screen)", f"{takes}, written on the screen"))
            continue
        if not obj:
            raise Stop(f"{where}: pattern `{pattern['id']}` fills `{sid}` from an object; name one with `object`")
        if takes == "identifier":
            if not obj["identifier"]:
                raise Stop(f"{where}: the object has no Identifier in ## Objects")
            rows.append((sid, obj["identifier"], "Identifier"))
        elif takes == "status":
            if obj["status"]:
                rows.append((sid, obj["status"], "Status"))
            elif slot.get("required"):
                raise Stop(f"{where}: `{sid}` needs the object's Status in ## Objects")
        elif takes == "image":
            if media is False and not slot.get("required"):
                continue
            if obj["image"]:
                rows.append((sid, obj["image"], "Image"))
            elif slot.get("required"):
                raise Stop(f"{where}: `{sid}` needs the object's Image in ## Objects (a property, or `placeholder`)")
        elif takes in ("price", "rating", "variations"):
            if takes in obj["tagged"]:
                for name in obj["tagged"][takes]:
                    rows.append((sid, name, f"Key property [{takes}]"))
            elif slot.get("required"):
                raise Stop(f"{where}: `{sid}` needs a Key property tagged [{takes}] in ## Objects")
        elif takes == "property":
            low = slot.get("min", 1 if slot.get("required") else 0)
            high = slot.get("max", 1)
            take = pool if high is None else pool[:high]
            if len(take) < low:
                raise Stop(f"{where}: `{sid}` needs {low} key propert{'y' if low == 1 else 'ies'}; ## Objects ranks {len(pool)}")
            ranks = {p: obj["properties"].index(p) + 1 for p in take}
            for p in take:
                rows.append((sid, p, f"Key property {ranks[p]}"))
            pool = pool[len(take):]
    return rows


def resolve(lines, index, patterns):
    """(new lines, [result per section]); raises Stop on the first unresolved section."""
    objects = read_objects(lines)
    blocks = read_blocks(lines)
    if not any(b["sections"] for b in blocks):
        raise Stop("no `- Sections:` list in the Composition section; write one per screen (references/patterns.md)")
    out = list(lines)
    results = []
    for block in blocks:
        for sec in block["sections"]:
            where = f"{block['screen']} / {sec['name']}"
            f = sec["fields"]
            content = f.get("content")
            if content not in library.CONTENT:
                raise Stop(f"{where}: `content` is one of {', '.join(library.CONTENT)}")
            if block["job"] not in library.JOBS:
                raise Stop(f"{where}: the block's `- Job class:` is one of {', '.join(library.JOBS)}")
            compare = yes_no(f.get("compare"), "compare", where)
            media = yes_no(f.get("media"), "media", where)
            rows, needs = library.decide(index, content, block["job"], compare)
            if not rows:
                if "compare" in needs:
                    raise Stop(f"{where}: add `compare yes` when the reader compares these by property, "
                               f"`compare no` when the reader finds one by name")
                raise Stop(f"{where}: no row of patterns/index.json admits content {content}, job {block['job']}")
            if len(rows) > 1:
                raise Stop(f"{where}: {len(rows)} rows of patterns/index.json admit it; run validate.py")
            row = rows[0]
            obj_name = f.get("object")
            obj = None
            if content in OBJECT_CONTENT:
                if not obj_name:
                    raise Stop(f"{where}: name the object with `object <name>` (a row of ## Objects)")
                if obj_name not in objects:
                    raise Stop(f"{where}: object `{obj_name}` has no row in ## Objects")
                obj = objects[obj_name]
            pid = row.get("pattern")
            slot_rows = []
            if pid:
                slot_rows = assign(patterns[pid], obj, {"media": media}, where)
            results.append({"screen": block["screen"], "section": sec["name"], "object": obj_name, "pattern": pid,
                            "say": row.get("say"), "slots": slot_rows})
            keep = [f"{k} {v}" for k, v in f.items() if k != "pattern"]
            out[sec["line"]] = f"{sec['indent']}- {sec['name']}: {'; '.join(keep + ['pattern ' + (pid or 'none')])}"
    return write_slots(out, results), results


def write_slots(lines, results):
    table = ["## Slots", "", SLOTS_INTRO, "",
             "| Screen | Section | Pattern | Slot | Shows | From |", "|---|---|---|---|---|---|"]
    for r in results:
        if not r["pattern"]:
            table.append(f"| {r['screen']} | {r['section']} | none | — | — | {r['say']} |")
            continue
        for slot, shows, source in r["slots"]:
            table.append(f"| {r['screen']} | {r['section']} | {r['pattern']} | {slot} | {shows} | {source} |")
    table.append("")
    found = find_section(lines, "Slots")
    if found:
        return lines[:found[0]] + table + lines[found[1]:]
    comp = find_section(lines, "Composition")
    at = comp[1] if comp else len(lines)
    return lines[:at] + table + lines[at:]


def main():
    parser = argparse.ArgumentParser(description="Resolve each section of ui-brief.md to a pattern and its slots.")
    parser.add_argument("brief", help="path to ui-brief.md")
    parser.add_argument("--check", action="store_true", help="write nothing; fail when the brief is out of date")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    try:
        with open(args.brief, encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError:
        print(f"FAIL: no such file: {args.brief}", file=sys.stderr)
        return 1
    lines = text.split("\n")
    try:
        new_lines, results = resolve(lines, library.load_index(), library.load_library())
    except Stop as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "question": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {exc}")
        return 1
    new_text = "\n".join(new_lines)
    changed = new_text != text
    if args.check:
        status = "FAIL" if changed else "PASS"
    else:
        status = "PASS"
        if changed:
            with open(args.brief, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(new_text)
    if args.json:
        print(json.dumps({"status": status, "changed": changed, "sections": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['screen']} / {r['section']}: {r['pattern'] or 'none'}" + (f" ({r['say']})" if r["say"] else ""))
        if args.check and changed:
            print("FAIL: the brief differs from what resolve.py writes; run it without --check")
        else:
            print(f"{status}: {len(results)} section(s)" + (", brief updated" if changed and not args.check else ""))
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
