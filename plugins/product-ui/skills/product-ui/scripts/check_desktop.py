#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) checks of an Electron desktop window's source against its brief.

Standard library only. Reads the main process (src/main), the preload script (src/preload) and the renderer
(src/renderer/src) of a project, the command table (the command-set.ts the renderer holds, else
scaffold/command-set.ts), and the `## Window` and `## Command set` sections of the ui-brief.md beside the nearest tokens.json.
The source of record for these rules is references/desktop.md; change that file first when a check changes.

DK1 a BrowserWindow whose webPreferences sets contextIsolation false, sandbox false, nodeIntegration true or
    webSecurity false
DK2 the titleBarOverlay height differs from the title row, or minWidth and minHeight differ from `minimum`
DK3 no element of the title row carries app-region: drag, or a control inside it lacks no-drag
DK4 a call of globalShortcut.register
DK5 a command of `## Command set` missing from the command table, or one whose word, tab, group or keys differ
DK6 two commands with one key, or a Ctrl+Alt combination
DK7 no handler of the window's close event that waits for the renderer, or no data-confirm="close" in the renderer
DK8 Electron's default menu left in place (no Menu.setApplicationMenu), or optimizer.watchWindowShortcuts called

The checks read literal code with regular expressions: a value written as an expression is passed over.
DK1 to DK8 are errors, and DK0 (an ignore without a reason) is a warning. A project whose tokens.json is not on `desktop` gives no finding; with no tokens.json
the checks that need no brief run.

CLI:
    python check_desktop.py <project-dir> [--brief ui-brief.md] [--json]

A finding ruled on and kept is silenced from the file itself:
    product-ui: ignore DK2 <reason>        the line before, or the same line
    product-ui: ignore-file DK4 <reason>   anywhere in the file
A form with no reason is reported as DK0 and silences nothing.

Exit codes: 0 = PASS (no finding), 1 = FAIL (one or more findings), 2 = no file in scope.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "patterns"))
sys.path.insert(0, HERE)
import check_pattern  # noqa: E402

SKIP_DIRS = {"node_modules", "dist", "build", "out", ".git", "coverage"}
CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}
RENDERER_EXT = CODE_EXT | {".html", ".htm", ".vue", ".svelte", ".astro", ".css"}
MARKUP_EXT = {".html", ".htm", ".vue", ".svelte", ".astro"}
TITLE_ROW_HEIGHT = 48     # references/desktop.md, The window
EMPTY_CELL = {"", "-", "—", "–"}
WEB_PREFERENCE = re.compile(r"\b(?P<name>contextIsolation|sandbox|webSecurity|nodeIntegration)\s*:\s*(?P<value>true|false)\b")
UNSAFE = {"contextIsolation": "false", "sandbox": "false", "webSecurity": "false", "nodeIntegration": "true"}
IGNORE = re.compile(r"product-ui:\s*ignore(?P<file>-file)?\s+(?P<id>DK\d+)(?P<reason>[^\n*]*?)\s*(?:-->|\*/|\}|$)", re.MULTILINE)
HTML_COMMENT = re.compile(r"<!--.*?-->|\{/\*.*?\*/\}|/\*.*?\*/", re.S)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
DRAG = re.compile(r"""app-?region['"]?\s*:\s*['"]?drag\b""", re.I)
NO_DRAG = re.compile(r"no-drag", re.I)
CONTROL_TAGS = {"button", "a", "input", "select", "textarea", "Button", "IconButton", "Link"}
ROLE_BUTTON = re.compile(r"""\brole\s*=\s*["']button["']""")
TITLE_ROW = re.compile(r"""data-region\s*=\s*(?:"title-row"|'title-row'|\{\s*["']title-row["']\s*\})""")
CONFIRM_CLOSE = re.compile(r"""data-confirm["']?\s*(?:=|:)\s*(?:\{\s*)?["']close["']""")
GLOBAL_SHORTCUT = re.compile(r"\bglobalShortcut\s*\.\s*register(?:All)?\s*\(")
APPLICATION_MENU = re.compile(r"\bMenu\s*\.\s*setApplicationMenu\s*\(")
WATCH_SHORTCUTS = re.compile(r"\boptimizer\s*\.\s*watchWindowShortcuts\s*\(")
CLOSE_HANDLER = re.compile(r"""\.\s*(?:on|once)\s*\(\s*["']close["']\s*,""")
KEY_SPLIT = re.compile(r"\s*,\s+|\s+/\s+|\s+or\s+")
OBJECT_FIELD = re.compile(r"""\b(?P<name>\w+)\s*:\s*(?:"(?P<d>[^"]*)"|'(?P<s>[^']*)')""")


def blank_comments(text, ext):
    """text with every comment replaced by spaces (newlines kept), so offsets and lines stay those of the file."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    if ext == ".css":
        return CSS_COMMENT.sub(blank, text)
    if ext in MARKUP_EXT:
        return HTML_COMMENT.sub(blank, text)
    out, i, n, quote = [], 0, len(text), None
    while i < n:
        c = text[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == quote or (c == "\n" and quote != "`"):
                quote = None
        elif c in "\"'`":
            quote = c
            out.append(c)
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j]))
            i = j
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def block_at(code, open_index):
    """(start, end) of the braces that open at open_index, strings skipped; end is just past the closing brace."""
    depth, quote, i = 0, None, open_index
    while i < len(code):
        c = code[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = None
        elif c in "\"'`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return open_index, i + 1
        i += 1
    return open_index, len(code)


def object_after(code, match):
    """(start, end) of the `{...}` literal that follows a match such as `webPreferences:`, or None when it is not a literal."""
    m = re.compile(r"\s*\{").match(code, match.end())
    if not m:
        return None
    start, end = block_at(code, m.end() - 1)
    return start, end


def find_tokens(start):
    """The nearest tokens.json at or above start (up to four directories), or None."""
    d = os.path.abspath(start)
    for _ in range(4):
        if os.path.isfile(os.path.join(d, "tokens.json")):
            return os.path.join(d, "tokens.json")
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def surface_of(tokens):
    try:
        with open(tokens, encoding="utf-8") as handle:
            return str((json.load(handle).get("meta") or {}).get("surface") or "").lower()
    except (OSError, ValueError, AttributeError):
        return ""


def read_lines(brief):
    if not brief:
        return []
    with open(brief, encoding="utf-8", errors="replace") as handle:
        return handle.read().split("\n")


def section(lines, heading):
    """[(line number, cells)] of the table rows under `## heading`."""
    rows, inside = [], False
    for number, line in enumerate(lines, 1):
        if line.startswith("## "):
            inside = line.strip().lower() == "## " + heading
        elif inside and line.strip().startswith("|"):
            rows.append((number, [c.strip() for c in line.strip().strip("|").split("|")]))
    return rows


def read_window(lines):
    """({"minimum": (w, h) or None, "title_row": px}, whether the brief holds the section)."""
    window = {"minimum": None, "title_row": TITLE_ROW_HEIGHT}
    rows = section(lines, "window")
    for _, cells in rows:
        if len(cells) < 2:
            continue
        item = " ".join(cells[0].lower().split())
        if item == "minimum":
            m = re.fullmatch(r"(\d+)\s*[x×]\s*(\d+)", cells[1])
            window["minimum"] = (int(m.group(1)), int(m.group(2))) if m else None
        elif item == "title row height":
            m = re.fullmatch(r"(\d+)\s*(?:px)?", cells[1])
            if m:
                window["title_row"] = int(m.group(1))
    return window


def read_command_set(lines):
    """[{"line", "id", "place", "tab", "group", "label", "keys"}] of the brief's `## Command set`; None without the section."""
    rows = section(lines, "command set")
    header = next((cells for _, cells in rows if cells and cells[0] == "Id"), None)
    if header is None:
        return None
    column = {name: header.index(name) for name in ("Id", "Place", "Tab", "Group", "Command", "Keys") if name in header}
    out = []
    for number, cells in rows:
        if cells == header or set("".join(cells)) <= set("-: ") or len(cells) < len(header):
            continue
        out.append({"line": number, "id": cells[column["Id"]], "place": cells[column.get("Place", 0)],
                    "tab": cells[column["Tab"]] if "Tab" in column else "", "group": cells[column["Group"]] if "Group" in column else "",
                    "label": cells[column["Command"]] if "Command" in column else "", "keys": cells[column["Keys"]] if "Keys" in column else ""})
    return out


def read_table_file(path):
    """[{"line", "id", "place", "tab", "group", "label", "keys"}] of the objects in a command-set.ts."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    code = blank_comments(text, ".ts")
    out = []
    for m in re.finditer(r"\{[^{}]*\bid\s*:[^{}]*\}", code):
        fields = {f.group("name"): f.group("d") if f.group("d") is not None else f.group("s") for f in OBJECT_FIELD.finditer(m.group(0))}
        if "id" in fields:
            out.append({"line": check_pattern.line_of(code, m.start()), "id": fields["id"], "place": fields.get("place", ""),
                        "tab": fields.get("tab", ""), "group": fields.get("group", ""), "label": fields.get("label", ""),
                        "keys": fields.get("keys", "")})
    return out


def source_files(root, subdir, extensions):
    base = os.path.join(root, *subdir.split("/"))
    out = []
    for folder, dirs, names in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(names):
            if os.path.splitext(name)[1].lower() in extensions and not check_pattern.EXCLUDE_FILE.search(name):
                out.append(os.path.join(folder, name))
    return out


def normal_cell(value):
    return "" if value in EMPTY_CELL else value


def normal_keys(value):
    return "none" if value in ("", "none") else value


def key_parts(key):
    """(frozenset of lower-case modifiers, lower-case key) of `Ctrl+Shift+F10`; `Ctrl++` keeps `+` as the key."""
    parts = [p.lower() for p in re.split(r"\+(?=.)", key.strip())]
    return frozenset(parts[:-1]), parts[-1]


class Scan:
    """The files of one project and the suppressions they carry."""

    def __init__(self, rep):
        self.rep = rep
        self.lines_ok = {}    # path -> {id: lines}
        self.file_ok = {}     # path -> ids
        self.code = {}        # path -> comment-free text

    def load(self, path):
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        lines, whole = {}, set()
        for m in IGNORE.finditer(text):
            line = check_pattern.line_of(text, m.start())
            if not m.group("reason").strip():
                self.rep.add("WARN", "DK0", path, line, f"`product-ui: ignore{m.group('file') or ''} {m.group('id')}` without a reason silences nothing")
            elif m.group("file"):
                whole.add(m.group("id"))
            else:
                lines.setdefault(m.group("id"), set()).update({line, line + 1})
        self.lines_ok[path], self.file_ok[path] = lines, whole
        self.code[path] = blank_comments(text, os.path.splitext(path)[1].lower())

    def ignored_anywhere(self, cid):
        return any(cid in ids for ids in self.file_ok.values())

    def report(self, cid, path, index, message):
        """A finding at an offset of a loaded file."""
        line = check_pattern.line_of(self.code[path], index)
        if cid not in self.file_ok.get(path, ()) and line not in self.lines_ok.get(path, {}).get(cid, ()):
            self.rep.add("ERROR", cid, path, line, message)

    def report_whole(self, cid, where, message):
        """A finding on the project as a whole, which `ignore-file` in any file silences."""
        if not self.ignored_anywhere(cid):
            self.rep.add("ERROR", cid, where, 0, message)


def check_dk1(scan, main):
    for path in main:
        code = scan.code[path]
        if "BrowserWindow" not in code:
            continue
        for m in re.finditer(r"\bwebPreferences\s*:", code):
            span = object_after(code, m)
            if not span:
                continue
            for pref in WEB_PREFERENCE.finditer(code, *span):
                if UNSAFE[pref.group("name")] == pref.group("value"):
                    scan.report("DK1", path, pref.start(), f"webPreferences sets `{pref.group('name')}: {pref.group('value')}`; "
                                "the window keeps contextIsolation true, sandbox true, nodeIntegration false and webSecurity on")


def check_dk2(scan, main, window, specs=()):
    # The kit's main process reads both values from WINDOW_SPEC, which scaffold.py writes into window-spec.ts.
    for path in specs:
        code = scan.code[path]
        row = re.search(r'"titleRow"\s*:\s*(\d+)', code)
        if row and int(row.group(1)) != window["title_row"]:
            scan.report("DK2", path, row.start(), f"WINDOW_SPEC gives the title row {row.group(1)}px, and ## Window gives {window['title_row']}px")
        minimum = re.search(r'"minimum"\s*:\s*\{\s*"width"\s*:\s*(\d+)\s*,\s*"height"\s*:\s*(\d+)', code)
        if minimum and window["minimum"] and (int(minimum.group(1)), int(minimum.group(2))) != tuple(window["minimum"]):
            scan.report("DK2", path, minimum.start(), f"WINDOW_SPEC gives the minimum {minimum.group(1)}x{minimum.group(2)}, "
                        f"and ## Window gives {window['minimum'][0]}x{window['minimum'][1]}")
    for path in main:
        code = scan.code[path]
        for m in re.finditer(r"\btitleBarOverlay\s*:", code):
            span = object_after(code, m)
            height = re.search(r"\bheight\s*:\s*(\d+)\b", code[span[0]:span[1]]) if span else None
            if height and int(height.group(1)) != window["title_row"]:
                scan.report("DK2", path, span[0] + height.start(),
                            f"the titleBarOverlay height is {height.group(1)}, and the title row is {window['title_row']}px")
        if window["minimum"]:
            for name, wanted in zip(("minWidth", "minHeight"), window["minimum"]):
                for m in re.finditer(r"\b" + name + r"\s*:\s*(\d+)\b", code):
                    if int(m.group(1)) != wanted:
                        scan.report("DK2", path, m.start(), f"{name} is {m.group(1)}, and `minimum` of ## Window gives {wanted}")


def check_dk3(scan, renderer):
    found_row, drag = False, False
    for path in renderer:
        code = scan.code[path]
        drag = drag or bool(DRAG.search(code))
        if os.path.splitext(path)[1].lower() == ".css":
            continue
        tags = [(m.start(), check_pattern.tag_end(code, m.start()), m.group("name")) for m in check_pattern.OPEN_TAG.finditer(code)]
        for start, end_open, name in tags:
            if not TITLE_ROW.search(code, start, end_open):
                continue
            found_row = True
            end = check_pattern.element_end(code, name, start, end_open)
            inner = [t for t in tags if start < t[0] < end]
            for c_start, c_end, c_name in inner:
                if not (c_name in CONTROL_TAGS or ROLE_BUTTON.search(code, c_start, c_end)):
                    continue
                marked = NO_DRAG.search(code, c_start, c_end) or any(
                    a_start < c_start < check_pattern.element_end(code, a_name, a_start, a_end) and NO_DRAG.search(code, a_start, a_end)
                    for a_start, a_end, a_name in inner)
                if not marked:
                    scan.report("DK3", path, c_start, f"the control `<{c_name}>` in the title row lacks `app-region: no-drag`, so the drag region takes its clicks")
    if found_row and not drag:
        scan.report_whole("DK3", os.path.dirname(renderer[0]), "no element of the title row carries `app-region: drag`, so the window cannot be moved by its title row")
    elif renderer and not found_row:
        scan.report_whole("DK3", os.path.dirname(renderer[0]), "no element with data-region=\"title-row\" in the renderer")


def check_dk4(scan, files):
    for path in files:
        for m in GLOBAL_SHORTCUT.finditer(scan.code[path]):
            scan.report("DK4", path, m.start(), "globalShortcut takes the key while the application is out of focus; handle the key in the renderer's command table")


def check_dk5(scan, rep, brief, expected, table, table_path):
    if expected is None:
        return
    if table is None:
        scan.report_whole("DK5", brief, "the command table (scaffold/command-set.ts) is missing, and ## Command set holds %d command%s"
                          % (len(expected), "" if len(expected) == 1 else "s"))
        return
    have = {(row["id"], row["place"]): row for row in table}
    for row in expected:
        mine = have.get((row["id"], row["place"]))
        if mine is None:
            rep.add("ERROR", "DK5", brief, row["line"], f"the command `{row['id']}` ({row['place']}) of ## Command set is missing from the command table")
            continue
        diffs = [f"{name} 「{mine_value}」 against 「{want}」" for name, mine_value, want in (
            ("word", mine["label"], row["label"]), ("tab", normal_cell(mine["tab"]), normal_cell(row["tab"])),
            ("group", normal_cell(mine["group"]), normal_cell(row["group"])),
            ("keys", normal_keys(mine["keys"]), normal_keys(row["keys"]))) if mine_value != want]
        if diffs:
            rep.add("ERROR", "DK5", table_path, mine["line"], f"the command `{row['id']}` ({row['place']}) differs from ## Command set: " + ", ".join(diffs))


def check_dk6(scan, rows, where):
    seen = {}
    for row in rows:
        if normal_keys(row["keys"]) == "none":
            continue
        for key in KEY_SPLIT.split(row["keys"]):
            mods, name = key_parts(key)
            if {"ctrl", "alt"} <= mods or {"control", "alt"} <= mods:
                scan.rep.add("ERROR", "DK6", where, row["line"], f"the command `{row['id']}` uses `{key}`; Windows reads AltGr as Ctrl+Alt, so the key types a character on many keyboards")
            first = seen.setdefault((mods, name), row)
            if first["id"] != row["id"]:
                scan.rep.add("ERROR", "DK6", where, row["line"], f"`{key}` runs `{first['id']}` and `{row['id']}`")


def handler_body(code, after):
    """The text of the close handler that starts at `after`: a function literal, or the function a name refers to; None when unread."""
    m = re.compile(r"\s*(?:async\s*)?(?:function\b[^{]*|\([^()]*\)\s*(?::\s*[\w<>\[\]]+\s*)?=>\s*|\w+\s*=>\s*)\{").match(code, after)
    if m:
        start, end = block_at(code, m.end() - 1)
        return code[start:end]
    name = re.compile(r"\s*(\w+)\s*[,)]").match(code, after)
    if name:
        d = re.search(r"(?:function\s+%s\b[^{]*|(?:const|let|var)\s+%s\s*=\s*(?:async\s*)?(?:function\b[^{]*|\([^()]*\)\s*=>\s*|\w+\s*=>\s*))\{"
                      % (name.group(1), name.group(1)), code)
        if d:
            start, end = block_at(code, d.end() - 1)
            return code[start:end]
    return None


def check_dk7(scan, main, renderer, where):
    if main:
        handlers = [(path, m) for path in main for m in CLOSE_HANDLER.finditer(scan.code[path])]
        waits = False
        for path, m in handlers:
            body = handler_body(scan.code[path], m.end())
            if body is None or ("preventDefault" in body and re.search(r"\.send\s*\(", body)):
                waits = True
        if not waits:
            if handlers:
                path, m = handlers[0]
                scan.report("DK7", path, m.start(), "the close handler does not stop the event and send the renderer a close request, so a changed document closes unsaved")
            else:
                scan.report_whole("DK7", os.path.dirname(main[0]), "no handler of the window's close event: a changed document closes without the save prompt")
    if renderer and not any(CONFIRM_CLOSE.search(scan.code[path]) for path in renderer):
        scan.report_whole("DK7", os.path.dirname(renderer[0]), "no element with data-confirm=\"close\" in the renderer: no save prompt")


def check_dk8(scan, main, files):
    if main and not any(APPLICATION_MENU.search(scan.code[path]) for path in main):
        scan.report_whole("DK8", os.path.dirname(main[0]), "Menu.setApplicationMenu is never called, so Electron's default menu and its keys stay in place")
    for path in files:
        for m in WATCH_SHORTCUTS.finditer(scan.code[path]):
            scan.report("DK8", path, m.start(), "optimizer.watchWindowShortcuts binds F12 to DevTools, and F12 is 名前を付けて保存")


def run(project, brief_path=None):
    """(report, the brief read, why no check ran or None, the files checked) for a project directory."""
    root = os.path.abspath(project)
    main = source_files(root, "src/main", CODE_EXT)
    preload = source_files(root, "src/preload", CODE_EXT)
    renderer = source_files(root, "src/renderer/src", RENDERER_EXT)
    files = main + preload + renderer
    rep = check_pattern.Report()
    tokens = find_tokens(root)
    brief = brief_path if brief_path and os.path.isfile(brief_path) else (
        os.path.join(os.path.dirname(tokens), "ui-brief.md") if tokens and os.path.isfile(os.path.join(os.path.dirname(tokens), "ui-brief.md")) else None)
    if not files:
        return rep, brief, None, files
    if tokens and surface_of(tokens) != "desktop":
        return rep, brief, "tokens.json is not on desktop", files
    scan = Scan(rep)
    for path in files:
        scan.load(path)
    lines = read_lines(brief)
    window = read_window(lines)
    expected = read_command_set(lines)
    # The table the application runs is the renderer's copy; scaffold/ holds what scaffold.py wrote from the brief.
    table_path = next((p for p in renderer if os.path.basename(p) == "command-set.ts"), None)
    table_path = table_path or next((p for p in (os.path.join(root, "scaffold", "command-set.ts"),
                                                 os.path.join(os.path.dirname(brief), "scaffold", "command-set.ts") if brief else None)
                                     if p and os.path.isfile(p)), None)
    table = read_table_file(table_path) if table_path else None
    check_dk1(scan, main)
    specs = [p for p in source_files(root, "src", CODE_EXT) + source_files(root, "scaffold", CODE_EXT)
             if os.path.basename(p) == "window-spec.ts"]
    for path in specs:
        if path not in files:
            scan.load(path)
    check_dk2(scan, main, window, specs)
    check_dk3(scan, renderer)
    check_dk4(scan, files)
    check_dk5(scan, rep, brief, expected, table, table_path)
    check_dk6(scan, table if table is not None else (expected or []), table_path or brief)
    check_dk7(scan, main, renderer, root)
    check_dk8(scan, main, files)
    return rep, brief, None, files


def main():
    parser = argparse.ArgumentParser(description="Check an Electron desktop window's source against the brief of the desktop surface.")
    parser.add_argument("project", help="project directory holding src/main, src/preload and src/renderer/src")
    parser.add_argument("--brief", help="path to ui-brief.md")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    rep, brief, skipped, files = run(args.project, args.brief)
    if not files:
        print("No file in scope.", file=sys.stderr)
        return 2
    status = "FAIL" if rep.findings else "PASS"
    if args.json:
        print(json.dumps({"status": status, "brief": brief, "skipped": skipped, "files_checked": len(files),
                          "error_count": len(rep.errors), "warning_count": len(rep.warnings), "findings": rep.findings}, indent=2, ensure_ascii=False))
    else:
        for item in rep.findings:
            print(f"{item['severity']:5} [{item['id']}] {item['file']}:{item['line']}: {item['message']}")
        print(f"{status}: {len(files)} file(s), {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)" + (f"; {skipped}, the checks were skipped" if skipped else ""))
    return 1 if rep.findings else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
