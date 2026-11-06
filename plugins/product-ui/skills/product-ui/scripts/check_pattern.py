#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) checks that each built container follows its pattern.

Standard library only. Reads the markup for the three attributes scaffold.py writes and the
build keeps: data-pattern on a pattern's item or block, data-pattern-slot on each slot, and
data-pattern-field on a slot that shows a property of the object. A slot belongs to the nearest
data-pattern element around it; an element carrying both attributes is a slot of the pattern
around it and the root of its own. The source of record for these rules is
references/patterns.md; change that file first when a check or a threshold changes.

PT1, PT2, PT4 and PT5 mean a container cannot be the pattern it names: a required slot is
missing, a limit is passed, the id is unknown or unplanned, a whole-item link holds another
control. They are warnings until the calibration in research/20261103-real-site-patterns
settles which become errors (decision D3 of its plan); --strict reports them as errors now.
PT3, PT6 and PT7 mean the screen departs from the plan: slots out of order, a field the
Slots table does not hold, a planned pattern with no element on the screen.

The brief is ui-brief.md beside the nearest tokens.json above the paths (up to three
directories), unless --brief names it. Without a brief, PT2's plan half, PT6 and PT7 are
skipped. The scaffold/ directory beside the brief is skipped: it is the input.

CLI:
    python check_pattern.py <path>... [--brief ui-brief.md] [--strict] [--json]

A finding ruled on and kept is silenced from the markup itself:
    product-ui: ignore PT3 <reason>        the line before, or the same line
    product-ui: ignore-file PT6 <reason>   anywhere in the file
A form with no reason is reported as PT0 and silences nothing.

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors),
2 = no file in scope.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "patterns"))
import library  # noqa: E402
import resolve  # noqa: E402

MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
EXCLUDE_DIRS = {"node_modules", "dist", "build", ".next", ".git", ".svelte-kit", "coverage", "scaffold"}
EXCLUDE_FILE = re.compile(r"\.(test|spec|min|stories)\.", re.IGNORECASE)

OPEN_TAG = re.compile(r"<(?P<name>[A-Za-z][\w.]*)(?=[\s/>])")
ATTR = re.compile(r"""(?<![\w:@-])(?P<name>data-pattern(?:-slot|-field)?)\s*=\s*(?:"(?P<d>[^"]*)"|'(?P<s>[^']*)'|\{\s*["'](?P<j>[^"']*)["']\s*\})""")
LINK_TAGS = {"a", "Link", "NavLink", "RouterLink", "router-link", "NuxtLink"}
CONTROL_TAGS = {"a", "Link", "NavLink", "RouterLink", "router-link", "NuxtLink", "button", "Button"}
IGNORE = re.compile(r"product-ui:\s*ignore(?P<file>-file)?\s+(?P<id>PT\d+)(?P<reason>[^\n*]*?)\s*(?:-->|\*/|\}|$)", re.MULTILINE)
SHOWN_NONE = ("(on the screen)", "the label of each", "placeholder", "—")


class Report:
    def __init__(self):
        self.findings = []

    def add(self, severity, check_id, path, line, message):
        self.findings.append({"severity": severity, "id": check_id, "file": path, "line": line, "message": message})

    @property
    def errors(self):
        return [f for f in self.findings if f["severity"] == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f["severity"] == "WARN"]


def tag_end(text, start):
    """Index just past the `>` that closes the tag opening at start, skipping quotes and braces."""
    depth, quote, i = 0, None, start + 1
    while i < len(text):
        c = text[i]
        if quote:
            if c == quote:
                quote = None
        elif c in "\"'`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth = max(0, depth - 1)
        elif c == ">" and depth == 0:
            return i + 1
        i += 1
    return len(text)


def element_end(text, name, open_start, open_end):
    """Index just past the element's closing tag, counting only tags of the same name."""
    if text[open_end - 2] == "/":
        return open_end
    depth, i = 1, open_end
    pattern = re.compile(r"<(/?)" + re.escape(name) + r"(?=[\s/>])")
    while depth:
        m = pattern.search(text, i)
        if not m:
            return len(text)
        end = tag_end(text, m.start())
        if m.group(1):
            depth -= 1
        elif text[end - 2] != "/":
            depth += 1
        i = end
    return i


def scan(text):
    """Every element that carries a pattern attribute, or is a link or a control: dicts with
    name, start, open_end, end, pattern, slot, field."""
    els = []
    for m in OPEN_TAG.finditer(text):
        name = m.group("name")
        end_open = tag_end(text, m.start())
        attrs = {}
        for a in ATTR.finditer(text, m.start(), end_open):
            attrs[a.group("name")] = a.group("d") or a.group("s") or a.group("j") or ""
        if not attrs and name not in CONTROL_TAGS:
            continue
        els.append({"name": name, "start": m.start(), "open_end": end_open,
                     "end": element_end(text, name, m.start(), end_open),
                     "pattern": attrs.get("data-pattern"), "slot": attrs.get("data-pattern-slot"),
                     "field": attrs.get("data-pattern-field")})
    return els


def owner(el, roots):
    """The nearest pattern root strictly around el (el itself never owns its own slot)."""
    best = None
    for r in roots:
        if r is el:
            continue
        if r["start"] < el["start"] < r["end"] and (best is None or r["start"] > best["start"]):
            best = r
    return best


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def suppressions(text, path, rep):
    lines, whole = {}, set()
    for m in IGNORE.finditer(text):
        line = line_of(text, m.start())
        if not m.group("reason").strip():
            rep.add("WARN", "PT0", path, line, f"`product-ui: ignore{m.group('file') or ''} {m.group('id')}` without a reason silences nothing")
            continue
        if m.group("file"):
            whole.add(m.group("id"))
        else:
            lines.setdefault(m.group("id"), set()).update({line, line + 1})
    return lines, whole


def find_brief(paths, explicit):
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    start = os.path.abspath(paths[0])
    d = start if os.path.isdir(start) else os.path.dirname(start)
    for _ in range(4):
        if os.path.isfile(os.path.join(d, "tokens.json")):
            brief = os.path.join(d, "ui-brief.md")
            return brief if os.path.isfile(brief) else None
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def read_plan(brief):
    """(pattern ids the brief resolved, {pattern id: set of fields its Slots rows show}, why the plan is unread)."""
    if not brief:
        return None, None, "no brief found"
    with open(brief, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    try:
        _, results = resolve.resolve(lines, library.load_index(), library.load_library())
    except resolve.Stop as exc:
        return None, None, f"the brief cannot be resolved ({exc})"
    planned, fields = set(), {}
    for r in results:
        if not r["pattern"]:
            continue
        planned.add(r["pattern"])
        for _, shows, _ in r["slots"]:
            if not shows.startswith(SHOWN_NONE):
                fields.setdefault(r["pattern"], set()).add(shows)
    return planned, fields, None


def files_in(paths):
    out = []
    for p in paths:
        if os.path.isfile(p):
            if os.path.splitext(p)[1].lower() in MARKUP_EXT:
                out.append(p)
            continue
        for root, dirs, names in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith("."))
            for n in sorted(names):
                if os.path.splitext(n)[1].lower() in MARKUP_EXT and not EXCLUDE_FILE.search(n):
                    out.append(os.path.join(root, n))
    return out


def check_file(path, text, patterns, planned, plan_fields, used_ids, seen_fields, rep, strict=False):
    lines_ok, file_ok = suppressions(text, path, rep)
    hard = "ERROR" if strict else "WARN"

    def report(severity, cid, index, message):
        line = line_of(text, index)
        if cid in file_ok or line in lines_ok.get(cid, set()):
            return
        rep.add(severity, cid, path, line, message)

    els = scan(text)
    roots = [e for e in els if e["pattern"]]
    allowed_inner = {u for pid in (planned or set()) if pid in patterns for u in patterns[pid].get("uses", [])}
    for root in roots:
        pid = root["pattern"]
        used_ids.add(pid)
        if pid not in patterns:
            report(hard, "PT2", root["start"], f"data-pattern `{pid}` is not in the library (patterns/)")
            continue
        if planned is not None and pid not in planned and pid not in allowed_inner:
            report(hard, "PT2", root["start"], f"`{pid}` is not the pattern of any section in the brief; "
                   "add the section, or run resolve.py after changing it")
        pattern = patterns[pid]
        slots = [e for e in els if e["slot"] and owner(e, roots) is root]
        order = library.slot_order(pattern)
        counts = {}
        for s in slots:
            counts[s["slot"]] = counts.get(s["slot"], 0) + 1
            if s["slot"] not in order:
                report(hard, "PT1", s["start"], f"`{pid}` has no slot `{s['slot']}`; its slots are {', '.join(order)}")
            if s["field"]:
                seen_fields.setdefault(pid, set()).add(s["field"])
                if plan_fields is not None and pid in plan_fields and s["field"] not in plan_fields[pid]:
                    report("WARN", "PT6", s["start"], f"slot `{s['slot']}` shows `{s['field']}`, which no Slots row of `{pid}` "
                           "assigns; change the Objects ranking or the section in the brief, and run resolve.py")
        for spec in pattern["slots"]:
            n = counts.get(spec["id"], 0)
            low = spec.get("min", 1 if spec.get("required") else 0)
            if spec.get("required") and n == 0:
                report(hard, "PT1", root["start"], f"`{pid}` is missing its required slot `{spec['id']}` ({spec['takes']})")
            elif n and n < low:
                report(hard, "PT1", root["start"], f"`{pid}` slot `{spec['id']}` appears {n} time(s); it needs {low}")
            high = spec.get("max", 1)
            if high is not None and n > high:
                report(hard, "PT4", root["start"], f"`{pid}` slot `{spec['id']}` appears {n} times; the pattern allows {high}")
        seen, last = [], -1
        for s in sorted(slots, key=lambda e: e["start"]):
            if s["slot"] in seen or s["slot"] not in order:
                continue
            seen.append(s["slot"])
            pos = order.index(s["slot"])
            if pos < last:
                report("WARN", "PT3", s["start"], f"`{pid}` slot `{s['slot']}` comes after `{order[last]}`; "
                       f"the pattern reads {', '.join(order)}")
                break
            last = pos
        # PT5: a link that wraps every slot of the item holds no other control.
        if slots:
            links = [e for e in els if e["name"] in LINK_TAGS and root["start"] <= e["start"] < root["end"]]
            for link in links:
                if all(link["start"] <= s["start"] < link["end"] for s in slots):
                    inner = [e for e in els if e["name"] in CONTROL_TAGS and e is not link
                             and link["open_end"] <= e["start"] < link["end"]]
                    if inner:
                        report(hard, "PT5", inner[0]["start"], f"`{pid}` is a link as a whole and holds another "
                               f"`<{inner[0]['name']}>`; move the control to the single view, or drop the whole-item link")
                    break


def main():
    parser = argparse.ArgumentParser(description="Check that each built container follows its pattern.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--brief", help="path to ui-brief.md")
    parser.add_argument("--strict", action="store_true", help="report PT1, PT2, PT4 and PT5 as errors")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    files = files_in(args.paths)
    if not files:
        print("No markup file in scope.", file=sys.stderr)
        return 2
    patterns = library.load_library()
    brief = find_brief(args.paths, args.brief)
    planned, plan_fields, unread = read_plan(brief)
    rep = Report()
    used_ids, seen_fields = set(), {}
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        check_file(path, text, patterns, planned, plan_fields, used_ids, seen_fields, rep, args.strict)
    if planned is not None:
        for pid in sorted(planned - used_ids):
            rep.add("WARN", "PT7", brief, 0, f"the brief plans `{pid}`, and no element carries data-pattern=\"{pid}\"; "
                    "build the section from its skeleton")
        for pid, wanted in sorted((plan_fields or {}).items()):
            missing = sorted(wanted - seen_fields.get(pid, set()))
            if pid in used_ids and missing:
                rep.add("WARN", "PT6", brief, 0, f"the Slots rows of `{pid}` assign {', '.join(missing)}, and no slot "
                        "shows it (data-pattern-field)")
    status = "FAIL" if rep.errors else "PASS"
    if args.json:
        print(json.dumps({"status": status, "brief": brief, "plan_unread": unread, "files_checked": len(files),
                          "error_count": len(rep.errors), "warning_count": len(rep.warnings),
                          "findings": rep.findings}, indent=2, ensure_ascii=False))
    else:
        for item in rep.findings:
            print(f"{item['severity']:5} [{item['id']}] {item['file']}:{item['line']}: {item['message']}")
        print(f"{status}: {len(files)} file(s), {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)"
              + (f"; {unread}, the plan checks were skipped" if unread else ""))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
