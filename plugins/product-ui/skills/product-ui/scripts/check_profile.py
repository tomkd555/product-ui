#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) checks that a built screen follows the conventions of its brief.

Standard library only. Reads the `## Conventions` section of ui-brief.md, which patterns/resolve.py
writes from the profile tokens.json names, and the attributes scaffold.py writes and the build keeps:
data-action on a control that runs an operation, data-key (or the kit's keyName) on a control a key
runs, data-confirm on the dialog before an operation, data-enter on an entry form, data-guard on a
control that takes one click per run, and the values the kit's parts take (requiredMark, useMessages).
The source of record for these rules is references/profiles.md; change that file first when a check
changes.

PF1 to PF7 mean the screen departs from the conventions: another word on an operation, a key the
section lacks, a registration without its confirmation, another required mark, an entry form that
keeps the browser's Enter, a message in another form or for another time, a registering control a
second click reaches. They are errors.

The brief is ui-brief.md beside the nearest tokens.json above the paths (up to three directories),
unless --brief names it. A brief without the section, or whose section holds `none`, gives no finding.
The scaffold/ directory beside the brief is skipped: it is the input.

CLI:
    python check_profile.py <path>... [--brief ui-brief.md] [--json]

A finding ruled on and kept is silenced from the file itself:
    product-ui: ignore PF1 <reason>        the line before, or the same line
    product-ui: ignore-file PF2 <reason>   anywhere in the file
A form with no reason is reported as PF0 and silences nothing.

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors),
2 = no file in scope.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "profiles"))
sys.path.insert(0, HERE)
import check_pattern  # noqa: E402
import conventions  # noqa: E402

SCRIPT_EXT = {".ts", ".js", ".mjs"}
ENTRY_PATTERNS = ("entry.slip", "master.form")
# The word of the Conventions section that names each operation a control is marked with.
WORD_OF = {"register": ("words.save", "words.create"), "delete": ("words.delete",), "new": ("words.new",),
           "lookup": ("words.lookup",), "search": ("words.search",), "clear": ("words.clear",), "cancel": ("words.cancel",),
           "save": ("words.save",), "save-as": ("words.save_as",), "undo": ("words.undo",), "redo": ("words.redo",),
           "cut": ("words.cut",), "copy": ("words.copy",), "paste": ("words.paste",), "open": ("words.open",),
           "close": ("words.close",), "print": ("words.print",), "export": ("words.export",),
           "select-all": ("words.select_all",), "replace": ("words.replace",), "find": ("words.search",)}
ATTR = re.compile(r"""(?<![\w:@-])(?P<name>data-action|data-key|keyName|data-confirm|data-enter|data-guard|data-pattern|"""
                  r"""data-message-kind|data-duration|kind|durationMs)\s*=\s*"""
                  r"""(?:"(?P<d>[^"]*)"|'(?P<s>[^']*)'|\{\s*["'](?P<j>[^"']*)["']\s*\}|\{\s*`(?P<t>[^`$]*)`\s*\}|\{\s*(?P<n>null|\d+)\s*\})""")
# A key written as an expression is unread: the checks compare literals.
KEY_UNREAD = re.compile(r"""(?<![\w:@-])(?:data-key|keyName)\s*=\s*\{(?!\s*["'`])""")
LINE_KEY = re.compile(r"""\b(?P<prop>insert|remove|add)=\{\{(?P<body>[^{}]*)\}\}""")
LINE_KEYS = re.compile(r"""\bkeys:\s*["'](?P<keys>[^"']+)["']""")
LINE_LABEL = re.compile(r"""\blabel:\s*["'](?P<label>[^"']+)["']""")
REQUIRED_PROP = re.compile(r"""\brequiredMark\s*=\s*(?:["'](?P<mark>[\w-]+)["']|\{\s*["'](?P<braced>[\w-]+)["']\s*\})""")
REQUIRED_ATTR = re.compile(r"""data-required-mark\s*=\s*(?:["'](?P<mark>[\w-]+)["']|\{\s*["'](?P<braced>[\w-]+)["']\s*\})""")
# The kit's own parts hold both forms of the mark, one per branch.
BOTH_MARKS = {"form-field.tsx", "line-grid.tsx"}
MESSAGE_RULES = re.compile(r"""useMessages\(\{(?P<body>[^{}]*)\}""")
MESSAGE_RESULT = re.compile(r"""\bresult:\s*["'](?P<kind>[\w-]+)["']""")
MESSAGE_MS = re.compile(r"""\bdurationMs:\s*(?P<ms>null|\d+)""")
COMMENT = re.compile(r"<!--.*?-->|\{/\*.*?\*/\}|/\*.*?\*/", re.S)
IGNORE = re.compile(r"product-ui:\s*ignore(?P<file>-file)?\s+(?P<id>PF\d+)(?P<reason>[^\n*]*?)\s*(?:-->|\*/|\}|$)", re.MULTILINE)
TAG = re.compile(r"<[^<>]*>")
LINE_ACTION = {"insert": "row-insert", "remove": "row-delete", "add": "row-new"}


def read_conventions(brief):
    """({item: value text}, why the section is unread)."""
    if not brief:
        return None, "no brief found"
    with open(brief, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    inside, section = False, []
    for line in lines:
        if line.startswith("## "):
            inside = line.strip().lower() == "## conventions"
        elif inside:
            section.append(line)
    table = conventions.parse_table(section)
    return table, None if table else "the brief holds no conventions"


def files_in(paths):
    out = []
    for p in paths:
        if os.path.isfile(p):
            if os.path.splitext(p)[1].lower() in check_pattern.MARKUP_EXT | SCRIPT_EXT:
                out.append(p)
            continue
        for root, dirs, names in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in check_pattern.EXCLUDE_DIRS and not d.startswith("."))
            for n in sorted(names):
                if os.path.splitext(n)[1].lower() in check_pattern.MARKUP_EXT | SCRIPT_EXT and not check_pattern.EXCLUDE_FILE.search(n):
                    out.append(os.path.join(root, n))
    return out


def scan(text):
    """Every element that carries one of the attributes: {"name", "start", "attrs", "text"}; text is None when it is computed."""
    els = []
    for m in check_pattern.OPEN_TAG.finditer(text):
        end_open = check_pattern.tag_end(text, m.start())
        attrs = {a.group("name"): a.group("d") or a.group("s") or a.group("j") or a.group("t") or a.group("n") or ""
                 for a in ATTR.finditer(text, m.start(), end_open)}
        if not attrs:
            continue
        end = check_pattern.element_end(text, m.group("name"), m.start(), end_open)
        inner = TAG.sub(" ", text[end_open:end]) if end > end_open else ""
        if "{" in inner:
            literal = re.fullmatch(r"""\s*\{\s*["']([^"'{}]*)["']\s*\}\s*""", inner)
            words = literal.group(1) if literal else None
        else:
            words = " ".join(inner.split())
        els.append({"name": m.group("name"), "start": m.start(), "attrs": attrs, "text": words})
    return els


def check_file(path, text, table, state, rep, hard):
    lines_ok, file_ok = {}, set()
    for m in IGNORE.finditer(text):
        line = check_pattern.line_of(text, m.start())
        if not m.group("reason").strip():
            rep.add("WARN", "PF0", path, line, f"`product-ui: ignore{m.group('file') or ''} {m.group('id')}` without a reason silences nothing")
        elif m.group("file"):
            file_ok.add(m.group("id"))
        else:
            lines_ok.setdefault(m.group("id"), set()).update({line, line + 1})
    state["ignored"] |= file_ok
    # A comment holds notes and examples: what it says about an attribute is no part of the screen.
    code = COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    if KEY_UNREAD.search(code):
        state["keys_unread"] = True

    def report(cid, index, message):
        line = check_pattern.line_of(text, index)
        if cid not in file_ok and line not in lines_ok.get(cid, set()):
            rep.add(hard, cid, path, line, message)

    duration = table.get("messages.duration_ms")

    def message(index, kind, ms):
        ms = {"null": conventions.UNTIL_CLOSED}.get(ms, ms)
        if kind and kind != table.get("messages.result"):
            report("PF6", index, f"the result shows as `{kind}`, and the Conventions section gives `{table.get('messages.result')}`")
        elif ms and ms != duration:
            report("PF6", index, f"the message stays `{ms}`, and the Conventions section gives `{duration}` (messages.duration_ms)")

    wanted = {k: (label, action) for k, label, action in state["keys"]}
    markup = os.path.splitext(path)[1].lower() in check_pattern.MARKUP_EXT
    for el in scan(code) if markup else []:
        attrs = el["attrs"]
        key = attrs.get("data-key") or attrs.get("keyName")
        action = attrs.get("data-action")
        if key:
            state["seen_keys"].add(key)
            label = el["text"]
            if label and label.startswith(key):
                label = label[len(key):].strip()
            if key not in wanted:
                report("PF2", el["start"], f"the key `{key}` is outside the keys of the Conventions section "
                       f"({', '.join(wanted) or 'none'})")
            else:
                if action and wanted[key][1] != action:
                    report("PF2", el["start"], f"`{key}` runs `{action}`, and the Conventions section gives it `{wanted[key][1]}`")
                if label and label != wanted[key][0]:
                    report("PF2", el["start"], f"`{key}` is labelled 「{label}」, and the Conventions section gives 「{wanted[key][0]}」")
        elif action in WORD_OF and el["text"]:
            words = [table.get(item) for item in WORD_OF[action]]
            # A word the project settles in voice.terms is unread here, and the control may hold it.
            words = [] if conventions.VOICE_TERMS in words else [w for w in words if w]
            if words and el["text"] not in words:
                report("PF1", el["start"], f"the control of `{action}` reads 「{el['text']}」, and the Conventions section gives 「{words[0]}」")
        if action == "register":
            state["registers"] = True
            if table.get("waiting.block") == "button" and attrs.get("data-guard") != "button":
                report("PF7", el["start"], "the control that registers takes a second click while the first run is under way; "
                       "wrap its handler in useSubmitGuard and mark it data-guard=\"button\" (waiting.block)")
        if attrs.get("data-guard") == "screen":
            state["screen_guard"] = True
        if "data-message-kind" in attrs or "data-duration" in attrs:
            message(el["start"], attrs.get("data-message-kind"), attrs.get("data-duration"))
        elif el["name"] == "Messages":
            message(el["start"], attrs.get("kind"), attrs.get("durationMs"))
        if attrs.get("data-confirm") == "register":
            state["confirms"].append((path, check_pattern.line_of(text, el["start"])))
        if attrs.get("data-pattern") in ENTRY_PATTERNS:
            state["entry"] = True
            marked = attrs.get("data-enter") == "next-field"
            if table.get("keys.enter") == "next-field" and not marked:
                report("PF5", el["start"], f"the form of `{attrs['data-pattern']}` keeps the browser's Enter; the Conventions section gives "
                       "keys.enter next-field (useEnterKeys, with data-enter=\"next-field\" on the form)")
            elif table.get("keys.enter") == "none" and marked:
                report("PF5", el["start"], "the form moves the focus on Enter, and the Conventions section gives keys.enter none")
    for m in LINE_KEY.finditer(code):
        keys, label = LINE_KEYS.search(m.group("body")), LINE_LABEL.search(m.group("body"))
        if not keys or not label:
            continue
        keys, label = keys.group("keys"), label.group("label")
        state["seen_keys"].add(keys)
        if keys not in wanted:
            report("PF2", m.start(), f"the key `{keys}` is outside the keys of the Conventions section ({', '.join(wanted) or 'none'})")
        elif wanted[keys] != (label, LINE_ACTION[m.group("prop")]):
            report("PF2", m.start(), f"`{keys}` is 「{label}」 ({LINE_ACTION[m.group('prop')]}), and the Conventions "
                   f"section gives 「{wanted[keys][0]}」 ({wanted[keys][1]})")
    marks = list(REQUIRED_PROP.finditer(code)) + ([] if os.path.basename(path) in BOTH_MARKS else list(REQUIRED_ATTR.finditer(code)))
    for m in marks:
        mark = m.group("mark") or m.group("braced")
        if mark != table.get("required_mark"):
            report("PF4", m.start(), f"the required mark is `{mark}`, and the Conventions section gives `{table.get('required_mark')}`")
    for m in MESSAGE_RULES.finditer(code):
        kind, ms = MESSAGE_RESULT.search(m.group("body")), MESSAGE_MS.search(m.group("body"))
        message(m.start(), kind and kind.group("kind"), ms and ms.group("ms"))


def run(paths, brief_path=None):
    """(report, the brief read, why its conventions are unread, the files checked) for the paths of one screen."""
    files = files_in(paths)
    brief = check_pattern.find_brief(paths, brief_path)
    table, unread = read_conventions(brief)
    rep = check_pattern.Report()
    if table and files:
        hard = "ERROR"
        shown = table.get("keys.display") != "none"
        state = {"keys": (conventions.parse_keys(table.get("keys.function")) if shown else [])
                 + conventions.parse_keys(table.get("keys.shortcuts")),
                 "seen_keys": set(), "registers": False, "confirms": [], "entry": False, "screen_guard": False,
                 "ignored": set(), "keys_unread": False}
        for path in files:
            with open(path, encoding="utf-8", errors="replace") as handle:
                check_file(path, handle.read(), table, state, rep, hard)

        def whole(cid, message):
            """A finding on the screen as a whole, which `ignore-file` in any of its files silences."""
            if cid not in state["ignored"]:
                rep.add(hard, cid, brief, 0, message)

        # The registering key on a screen that holds an entry form. A key whose operation the screen lacks is left out of the build.
        for key, label, action in state["keys"]:
            if action == "register" and state["entry"] and key not in state["seen_keys"] and not state["keys_unread"]:
                whole("PF2", f"the Conventions section gives `{key}` 「{label}」 ({action}), and no control carries it (data-key)")
        if table.get("waiting.block") == "screen" and state["registers"] and not state["screen_guard"]:
            whole("PF7", "the Conventions section blocks the screen while a registration runs (waiting.block screen), "
                    "and no element carries data-guard=\"screen\"")
        confirm = table.get("confirm.register")
        if confirm == "always" and state["registers"] and not state["confirms"]:
            whole("PF3", "the Conventions section asks before a registration (confirm.register always), and no dialog "
                    "carries data-confirm=\"register\"; build it from the feedback.confirm skeleton")
        elif confirm == "never":
            for path, line in state["confirms"]:
                rep.add(hard, "PF3", path, line, "a dialog asks before the registration, and the Conventions section gives confirm.register never")
    return rep, brief, unread, files


def main():
    parser = argparse.ArgumentParser(description="Check that a built screen follows the conventions of its brief.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--brief", help="path to ui-brief.md")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    rep, brief, unread, files = run(args.paths, args.brief)
    if not files:
        print("No file in scope.", file=sys.stderr)
        return 2
    status = "FAIL" if rep.errors else "PASS"
    if args.json:
        print(json.dumps({"status": status, "brief": brief, "conventions_unread": unread, "files_checked": len(files),
                          "error_count": len(rep.errors), "warning_count": len(rep.warnings),
                          "findings": rep.findings}, indent=2, ensure_ascii=False))
    else:
        for item in rep.findings:
            print(f"{item['severity']:5} [{item['id']}] {item['file']}:{item['line']}: {item['message']}")
        print(f"{status}: {len(files)} file(s), {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)"
              + (f"; {unread}, the checks were skipped" if unread else ""))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
