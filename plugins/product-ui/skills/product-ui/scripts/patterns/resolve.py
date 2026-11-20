#!/usr/bin/env python3
"""product-ui: choose each section's pattern and fill its slots, deterministically.

Standard library only. Reads ui-brief.md: the `## Objects` table, and in each Composition
block the `- Job class:` line and the `- Sections:` list. For every section it looks the
pattern up in patterns/index.json, writes the id back into the section's line, and writes the
`## Slots` table: which property of the object each slot shows. It reads `meta.profile` and
`meta.profile_product` from the tokens.json beside the brief and writes the `## Conventions`
section: the keys, the words and the messages of that profile (references/profiles.md). Where that
tokens.json has `meta.surface: desktop` it also completes `## Window` and writes `## Command set`
after `## Conventions` (desktop/command_set.py, references/desktop.md). The
source of record for these rules is references/patterns.md; change that file first when a rule
changes.

The same brief and the same tokens.json give the same pattern ids, the same Slots table and the
same Conventions section on every run. A section
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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "desktop"))
import command_set  # noqa: E402
import conventions  # noqa: E402
import library  # noqa: E402

SECTION_HEAD = re.compile(r"^## (?P<name>.+?)\s*$")
BLOCK_HEAD = re.compile(r"^### (?P<name>.+?)\s*$")
JOB_LINE = re.compile(r"^\s*-\s*Job class:\s*`?(?P<job>[a-z]+)`?", re.IGNORECASE)
SECTIONS_LINE = re.compile(r"^(?P<indent>\s*)-\s*Sections:")
SECTION_ITEM = re.compile(r"^(?P<indent>\s+)-\s*(?P<name>[^:]+?):\s*(?P<body>.+?)\s*$")
TAG = re.compile(r"^(?P<name>.+?)\s*\[(?P<tag>price|rating|variations|offer)\]$")
NONE = {"", "none", "-", "—", "なし"}
OBJECT_CONTENT = {"records", "record-header", "record-detail", "record-fields", "items", "products", "tasks",
                  "slip", "master", "closing", "import", "approval"}
OBJECT_SOURCES = ("Identifier", "Status", "Image", "Key property")  # how a Slots row names a value of an object
CONVENTION_REF = re.compile(r"^(?P<item>[a-z_.]+)(?:\[(?P<index>\d+)\])?$")
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
        props, tagged, ranked = [], {}, []
        for raw in [p.strip() for p in re.split(r"[,、]", cells[4]) if p.strip()]:
            m = TAG.match(raw)
            if m:
                tagged.setdefault(m.group("tag"), []).append(m.group("name").strip())
                ranked.append((m.group("name").strip(), m.group("tag")))
            else:
                props.append(raw)
                ranked.append((raw, None))
        objects[cells[0]] = {
            "identifier": None if cells[1] in NONE else cells[1],
            "status": None if cells[2] in NONE else cells[2],
            "image": None if cells[3] in NONE else cells[3],
            "properties": props,
            "tagged": tagged,
            "ranked": ranked,
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


def names(value):
    """The names of a comma-separated section key (`totals 小計, 消費税, 合計`)."""
    return [p.strip() for p in re.split(r"[,、]", value or "") if p.strip()]


def groups(value):
    """[(group name, [property])] of a `groups` key: `得意先情報=コード, フリガナ / 住所情報=郵便番号, 住所`."""
    out = []
    for part in [p.strip() for p in re.split(r"\s+/\s+", value or "") if p.strip()]:
        name, _, props = part.partition("=")
        out.append((name.strip(), names(props)))
    return out


def key_names(fields, key):
    """The entries a section's key lists; a `groups` key lists its group names."""
    if key == "groups":
        return [name for name, _ in groups(fields.get(key))]
    return names(fields.get(key))


def load_conventions(brief):
    """The conventions of the tokens.json beside a brief: {"profile", "product", "rows", "values"}.

    `rows` is None when tokens.json names no profile; `values` then holds this skill's own. On a desktop surface the
    rows and the values carry the desktop adjustment (`conventions.desktop_rows`).
    """
    tokens = os.path.join(os.path.dirname(os.path.abspath(brief)), "tokens.json")
    try:
        pid, product, rows = conventions.for_tokens(tokens)
    except conventions.ProfileError as exc:
        raise Stop(str(exc))
    try:
        with open(tokens, encoding="utf-8") as handle:
            meta = (json.load(handle) or {}).get("meta") or {}
    except (OSError, ValueError, AttributeError):
        meta = {}
    if rows is not None and meta.get("surface") == "desktop":
        try:
            with open(brief, encoding="utf-8") as handle:
                help_listed = any("F1" in row["keys"] for row in command_set.read_commands(handle.read().split("\n"))[0])
        except (OSError, command_set.CommandSetError):
            help_listed = False
        rows = conventions.desktop_rows(rows, help_listed)
    return {"profile": pid, "product": product, "rows": rows, "surface": meta.get("surface"), "name": meta.get("name"),
            "values": {r["item"]: r["value"] for r in (rows or conventions.defaults())}}


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


HEADER_KEYS = 4  # key fields of a record's header on a screen that also lists the record's fields


def assign(pattern, obj, section, where):
    """The Slots table rows for one section: [(slot, shows, from)].

    Where the screen lists the record's fields (``section["fields_follow"]``), the header takes the first
    HEADER_KEYS properties and the list takes the others (``section["shown"]`` holds the header's); an object
    of HEADER_KEYS properties or fewer shows them all in the list.
    """
    rows = []
    # A tagged property fills the slot that takes its tag; in a pattern with no such slot it ranks with the others.
    own = {s["takes"] for s in pattern["slots"]}
    pool = [name for name, tag in obj["ranked"] if tag is None or tag not in own] if obj else []
    order = [name for name, _ in obj["ranked"]] if obj else []
    # A slot with `of` reads a second object (the lines of a slip), which keeps a pool of its own.
    others = {key: {"obj": other, "name": name, "pool": [n for n, _ in other["ranked"]],
                    "order": [n for n, _ in other["ranked"]]}
              for key, (name, other) in (section.get("others") or {}).items()}
    fields, values = section.get("fields") or {}, section.get("conventions") or {}
    if pattern.get("kind") == "record-fields":
        pool = [p for p in pool if p not in section.get("shown", ())]
    if section.get("show"):
        unknown = [p for p in section["show"] if p not in order]
        if unknown:
            raise Stop(f"{where}: `show` names {', '.join(unknown)}, which the object's Key properties lack")
        pool = [p for p in section["show"] if p in pool]
    header_cap = None
    if pattern.get("kind") == "record-header" and section.get("fields_follow"):
        header_cap = HEADER_KEYS if len(pool) > HEADER_KEYS else 0
    media = section.get("media")
    for slot in pattern["slots"]:
        takes, sid = slot["takes"], slot["id"]
        if slot.get("from_key"):
            key = slot["from_key"]
            listed = key_names(fields, key)
            low, high = slot.get("min", 1 if slot.get("required") else 0), slot.get("max", 1)
            if len(listed) < low or (high is not None and len(listed) > high):
                raise Stop(f"{where}: `{key}` lists {len(listed)} name(s), and `{sid}` of `{pattern['id']}` takes "
                           f"{low} to {high if high is not None else 'any number'}; write `{key} <name>, <name>` in the section's line")
            rows += [(sid, name, f"section key `{key}`") for name in listed]
            continue
        if slot.get("from_convention"):
            ref = CONVENTION_REF.match(slot["from_convention"])
            item, value = ref.group("item"), values.get(ref.group("item"))
            if ref.group("index") is not None and isinstance(value, list):
                value = value[int(ref.group("index"))]
            if item == "keys.function":
                shown = [f"{k['key']} {k['label']}" for k in value or []]
                if not shown and slot.get("required"):
                    raise Stop(f"{where}: the conventions show function keys (keys.display) and list none (keys.function)")
            else:
                # Where a registration asks first, the dialog's operation is the registration; elsewhere it is the caller's.
                word = values.get("words.save") if values.get("confirm.register") == "always" else None
                if isinstance(value, str) and word and word != conventions.VOICE_TERMS:
                    value = value.replace(conventions.OPERATION, word)
                shown = [] if value in (None, "none") else [str(value)]
            rows += [(sid, text, f"Conventions {item}") for text in shown]
            continue
        if slot.get("of"):
            other = others.get(slot["of"])
            if not other:
                raise Stop(f"{where}: pattern `{pattern['id']}` fills `{sid}` from the object of `{slot['of']}`; "
                           f"name it with `{slot['of']} <object>` (a row of ## Objects)")
            if takes == "identifier":
                if not other["obj"]["identifier"]:
                    raise Stop(f"{where}: object `{other['name']}` has no Identifier in ## Objects")
                rows.append((sid, other["obj"]["identifier"], f"Identifier of {other['name']}"))
            elif takes == "property":
                low, high = slot.get("min", 1 if slot.get("required") else 0), slot.get("max", 1)
                take = other["pool"] if high is None else other["pool"][:high]
                if len(take) < low:
                    raise Stop(f"{where}: `{sid}` needs {low} key propert{'y' if low == 1 else 'ies'} of `{other['name']}`; "
                               f"## Objects ranks {len(other['pool'])}")
                rows += [(sid, p, f"Key property {other['order'].index(p) + 1} of {other['name']}") for p in take]
                other["pool"] = other["pool"][len(take):]
            continue
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
        elif takes in ("price", "rating", "variations", "offer"):
            if takes in obj["tagged"]:
                for name in obj["tagged"][takes]:
                    rows.append((sid, name, f"Key property [{takes}]"))
            elif slot.get("required"):
                raise Stop(f"{where}: `{sid}` needs a Key property tagged [{takes}] in ## Objects")
        elif takes == "property":
            low = slot.get("min", 1 if slot.get("required") else 0)
            high = slot.get("max", 1)
            if header_cap is not None:
                high = header_cap
            take = pool if high is None else pool[:high]
            if len(take) < low:
                raise Stop(f"{where}: `{sid}` needs {low} key propert{'y' if low == 1 else 'ies'}; ## Objects ranks {len(pool)}")
            ranks = {p: order.index(p) + 1 for p in take}
            for p in take:
                rows.append((sid, p, f"Key property {ranks[p]}"))
            pool = pool[len(take):]
    return rows


def check_listed(fields, key, allowed, where, what):
    unknown = [n for n in names(fields.get(key)) if n not in allowed]
    if unknown:
        raise Stop(f"{where}: `{key}` names {', '.join(unknown)}, which {what} lack")


def resolve(lines, index, patterns, conv=None):
    """(new lines, [result per section]); raises Stop on the first unresolved section.

    `conv` is what load_conventions returns; without it the conventions are this skill's own and the
    brief's `## Conventions` section is left as it stands.
    """
    values = conv["values"] if conv else {r["item"]: r["value"] for r in conventions.defaults()}
    objects = read_objects(lines)
    blocks = read_blocks(lines)
    if not any(b["sections"] for b in blocks):
        raise Stop("no `- Sections:` list in the Composition section; write one per screen (references/patterns.md)")
    out = list(lines)
    results = []
    for block in blocks:
        shown = {}
        listed = {s["fields"].get("object") for s in block["sections"] if s["fields"].get("content") == "record-fields"}
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
            others = {}
            for key in library.OF_KEYS:
                if f.get(key):
                    if f[key] not in objects:
                        raise Stop(f"{where}: `{key} {f[key]}` has no row in ## Objects")
                    others[key] = (f[key], objects[f[key]])
            section = {"media": media, "shown": shown.get(obj_name, ()), "fields_follow": obj_name in listed,
                       "show": names(f.get("show")), "others": others, "fields": f, "conventions": values}
            if obj:
                own = [n for n, _ in obj["ranked"]]
                line_props = [n for _, other in others.values() for n, _ in other["ranked"]]
                check_listed(f, "auto", line_props, where, "the Key properties of the `lines` object")
                check_listed(f, "required", own + [obj["identifier"]] + line_props
                             + [other["identifier"] for _, other in others.values()], where, "the objects of this section")
                grouped = [p for _, props in groups(f.get("groups")) for p in props]
                check_listed({"groups": ", ".join(grouped)}, "groups", own, where, "the object's Key properties")
                shows = section["show"] or own
                if grouped and content == "master" and [p for p in shows if p not in grouped]:
                    raise Stop(f"{where}: `groups` leaves out {', '.join(p for p in shows if p not in grouped)}; "
                               f"every Key property the section shows sits in one group")
            for extra in library.attached(index, {content}, {k for k in f if f[k]}, values):
                results.append({"screen": block["screen"], "section": sec["name"], "object": obj_name,
                                "pattern": extra["pattern"], "say": None,
                                "slots": assign(patterns[extra["pattern"]], obj, section, where)})
            if pid:
                slot_rows = assign(patterns[pid], obj, section, where)
                if patterns[pid].get("kind") == "record-header":
                    shown[obj_name] = [s for _, s, source in slot_rows if source.startswith("Key property")]
            results.append({"screen": block["screen"], "section": sec["name"], "object": obj_name, "pattern": pid,
                            "say": row.get("say"), "slots": slot_rows})
            keep = [f"{k} {v}" for k, v in f.items() if k != "pattern"]
            out[sec["line"]] = f"{sec['indent']}- {sec['name']}: {'; '.join(keep + ['pattern ' + (pid or 'none')])}"
        # The patterns a whole screen takes beside its sections' own (patterns/index.json, attach).
        contents = {s["fields"].get("content") for s in block["sections"]}
        entry = next((s["fields"].get("object") for s in block["sections"]
                      if s["fields"].get("content") in ("slip", "master")), None)
        for extra in library.attached(index, contents, None, values):
            where = f"{block['screen']} / {library.SCREEN_SECTION}"
            results.append({"screen": block["screen"], "section": library.SCREEN_SECTION, "object": entry,
                            "pattern": extra["pattern"], "say": None,
                            "slots": assign(patterns[extra["pattern"]], None, {"conventions": values}, where)})
    out = write_conventions(write_slots(out, results), conv)
    if conv and conv.get("surface") == "desktop":
        try:
            out = command_set.apply(out, conv)
        except command_set.CommandSetError as exc:
            raise Stop(str(exc))
    return out, results


def write_conventions(lines, conv):
    """The brief with its `## Conventions` section brought up to date, after `## Slots`.

    Without a profile the section, where the brief has one, holds `none`; a brief without the section stays without it.
    """
    found = find_section(lines, "Conventions")
    if not conv or conv["rows"] is None:
        if not found:
            return lines
        return lines[:found[0]] + conventions.table(None, None, None) + lines[found[1]:]
    table = conventions.table(conv["profile"], conv["product"], conv["rows"])
    if found:
        return lines[:found[0]] + table + lines[found[1]:]
    slots = find_section(lines, "Slots")
    at = slots[1] if slots else len(lines)
    return lines[:at] + table + lines[at:]


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
        new_lines, results = resolve(lines, library.load_index(), library.load_library(), load_conventions(args.brief))
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
