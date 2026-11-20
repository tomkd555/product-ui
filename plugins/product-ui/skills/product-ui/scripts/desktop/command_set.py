"""product-ui: the desktop window's sections of ui-brief.md, read by patterns/resolve.py and patterns/scaffold.py.

Standard library only. On `meta.surface: desktop` the brief carries `## Window`, `## Commands` and `## File view`
(written at Step 3); `apply` fills the rows of `## Window` that the brief leaves out, adds the rows of the fixed
regions and writes `## Command set` after `## Conventions`. The same brief and the same profile give the same
section on every run. `command_set_ts` and `window_spec_ts` print the two files scaffold.py writes from it. The
source of record is references/desktop.md; change that file first when a rule changes.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import colour  # noqa: E402
import conventions  # noqa: E402

SECTION_HEAD = re.compile(r"^## (?P<name>.+?)\s*$")
OPERATIONS_LINE = re.compile(r"^\s*-\s*Operations:\s*(?P<body>.*?)\s*$")
COLLAPSE_LINE = re.compile(r"^\s*-\s*Collapse:\s*(?P<body>.*?)\s*$")
PANE = re.compile(r"^(?P<title>.+?)\s+(?P<width>\d+)\s+(?P<min>\d+)-(?P<max>\d+)\s+(?P<state>open|closed)$")
SIZE = re.compile(r"^(?P<w>\d+)\s*x\s*(?P<h>\d+)$")
DOCUMENT_MINIMUM = re.compile(r"minimum width\s+(?P<px>\d+)")
KEY_TIP = re.compile(r"^[A-Z0-9]{1,3}$")
NONE_WORDS = ("", "none", "-", "—", "なし")

SECTION_TITLE = "Command set"
INTRO = ("Written by `scripts/patterns/resolve.py` from `## Commands`, `## File view` and the profile "
         "(`references/desktop.md`). Change those and run it again; an edit here is overwritten.")
COLUMNS = ("Id", "Place", "Tab", "Group", "Command", "Size", "Action", "Keys", "Key tip", "Enabled when", "Runs")
SIZES = ("large", "small", "menu", "check")

OPERATIONS = ("new", "open", "save", "save-as", "close", "undo", "redo", "cut", "copy", "paste", "select-all",
              "delete", "export", "print", "find", "replace", "zoom")
WORD_ITEM = {"new": "words.new", "open": "words.open", "save": "words.save", "save-as": "words.save_as",
             "close": "words.close", "undo": "words.undo", "redo": "words.redo", "cut": "words.cut",
             "copy": "words.copy", "paste": "words.paste", "select-all": "words.select_all",
             "delete": "words.delete", "export": "words.export", "print": "words.print",
             "find": "words.search", "replace": "words.replace"}
QUICK_ACCESS = ("save", "undo", "redo")
FILE_VIEW = ("new", "open", "save", "save-as", "print", "export", "close")
CLIPBOARD = ("クリップボード", (("paste", "large"), ("cut", "small"), ("copy", "small")))
EDITING = ("編集", (("select-all", "small"), ("delete", "small"), ("find", "small"), ("replace", "small")))
HOME, VIEW, ZOOM_GROUP = "ホーム", "表示", "ズーム"
ZOOM_LABEL, FIT_LABEL, BACK_LABEL = "ズーム", "ウィンドウに合わせる", "戻る"

TAB_TIPS = {"ファイル": "F", "ホーム": "H", "挿入": "N", "表示": "W", "ヘルプ": "Y"}
FILE_TIPS = {"back": "B", "new": "N", "open": "O", "save": "S", "save-as": "A", "print": "P", "export": "E",
             "close": "C"}
FILE_APP_TIPS = {"オプション": "T"}
RIBBON_TIPS = {"paste": "V", "cut": "X", "copy": "C", "select-all": "A", "delete": "D", "find": "FD",
               "replace": "R", "zoom": "Q", "zoom-fit": "J"}
ENABLED = {"undo": "元に戻せる操作がある", "redo": "やり直せる操作がある", "cut": "文書内で範囲を選択している",
           "copy": "文書内で範囲を選択している", "delete": "文書内で範囲を選択している"}
RUNS = {"new": "新しい文書を作る", "open": "文書を開く", "save": "文書を上書き保存する",
        "save-as": "文書に名前を付けて保存する", "close": "文書を閉じる", "undo": "直前の操作を元に戻す",
        "redo": "元に戻した操作をやり直す", "cut": "選択範囲を切り取る", "copy": "選択範囲をコピーする",
        "paste": "クリップボードの内容を貼り付ける", "select-all": "すべてを選択する",
        "delete": "選択範囲を削除する", "export": "文書を別の形式で書き出す", "print": "文書を印刷する",
        "find": "文書内を検索する", "replace": "文書内を置換する", "zoom": "表示倍率を選ぶ",
        "zoom-fit": "表示倍率をウィンドウに合わせる", "back": "文書に戻る"}

WINDOW_DEFAULTS = (("size", "1280x720"), ("minimum", "500x480"), ("title", None), ("left pane", "none"),
                   ("right pane", "none"), ("document", "minimum width 200"), ("status bar", None))
FIXED_HEIGHTS = (("title row height", 48), ("tab row height", 36), ("command area height", 112),
                 ("status bar height", 28))
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class CommandSetError(Exception):
    """A desktop section the brief does not settle."""


def find_section(lines, title):
    heads = [(i, SECTION_HEAD.match(line).group("name")) for i, line in enumerate(lines) if SECTION_HEAD.match(line)]
    for n, (start, name) in enumerate(heads):
        if name.strip().lower() == title.lower():
            return start, heads[n + 1][0] if n + 1 < len(heads) else len(lines)
    return None


def table_rows(lines):
    """The data rows of the first Markdown table in lines, as lists of cells; an empty cell stays."""
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


def items(body):
    """The names of a comma-separated line, without backticks."""
    return [p.strip().strip("`") for p in re.split(r"[,、]", body or "") if p.strip().strip("`")]


def cell(text):
    return text.replace("|", "/")


def norm_keys(text):
    """Keys as the profile writes them: `ctrl+g` becomes `Ctrl+G`."""
    out = []
    for part in text.split("+"):
        part = part.strip()
        low = part.lower()
        if low in ("ctrl", "shift", "alt"):
            out.append(low.capitalize())
        else:
            out.append(part.upper() if len(part) == 1 else part)
    return "+".join(out)


def key_list(text):
    """The keys a Keys cell holds; `none` and an empty cell hold none."""
    if text.strip() in NONE_WORDS:
        return []
    return [norm_keys(k) for k in re.split(r",\s*", text.strip()) if k.strip()]


# ---------------------------------------------------------------- the brief's desktop sections

def read_window(lines):
    """[(item, value)] of the `## Window` table; raises when the section is missing."""
    found = find_section(lines, "Window")
    if not found:
        raise CommandSetError("a desktop brief needs a `## Window` section (references/desktop.md, The brief's desktop sections)")
    return [(c[0], c[1]) for c in table_rows(lines[found[0] + 1:found[1]]) if len(c) >= 2 and c[0] and not c[0].startswith("{{")]


def read_commands(lines):
    """(rows, operations, collapse): the `## Commands` rows as dicts, the `- Operations:` names and the `- Collapse:` groups."""
    found = find_section(lines, "Commands")
    if not found:
        raise CommandSetError("a desktop brief needs a `## Commands` section (references/desktop.md, The brief's desktop sections)")
    body = lines[found[0] + 1:found[1]]
    rows = []
    for n, c in enumerate(table_rows(body), 1):
        if not c or c[0].startswith("{{"):
            continue
        if len(c) < 8:
            raise CommandSetError(f"`## Commands` row {n} has {len(c)} columns; it takes 8 (Tab, Group, Command, Size, Keys, Key tip, Enabled when, Runs)")
        tab, group, label, size, keys, tip, enabled, runs = c[:8]
        if not (tab and group and label):
            raise CommandSetError(f"`## Commands` row {n}: Tab, Group and Command are required")
        if size not in SIZES:
            raise CommandSetError(f"`## Commands` row `{label}`: Size is one of {', '.join(SIZES)}, not `{size}`")
        rows.append({"tab": tab, "group": group, "label": label, "size": size, "keys": key_list(keys),
                     "keytip": tip.strip().upper() if tip.strip() not in NONE_WORDS else "", "enabled": enabled or "always",
                     "enabled_given": bool(enabled.strip()), "runs": runs})
    operations, collapse = [], []
    for line in body:
        m = OPERATIONS_LINE.match(line)
        if m:
            operations = items(m.group("body"))
        m = COLLAPSE_LINE.match(line)
        if m:
            collapse = items(m.group("body"))
    unknown = [o for o in operations if o not in OPERATIONS]
    if unknown:
        raise CommandSetError(f"`- Operations:` names {', '.join(unknown)}; the operations are {', '.join(OPERATIONS)}")
    return rows, operations, collapse


def read_file_view(lines):
    """{item: page} of the `## File view` table; empty where the section is missing."""
    found = find_section(lines, "File view")
    if not found:
        return {}
    return {c[0]: (c[1] if len(c) > 1 else "") for c in table_rows(lines[found[0] + 1:found[1]])
            if c and c[0] and not c[0].startswith("{{")}


# ---------------------------------------------------------------- the profile

def profile_keys(values):
    """[(keys, label, action)] of the profile's function keys and shortcuts."""
    out = []
    for item in ("keys.shortcuts", "keys.function"):
        for e in values.get(item) or []:
            out.append((norm_keys(e.get("keys") or e.get("key")), e["label"], e["action"]))
    return out


def word_of(values, op):
    """The word of a window operation: the profile's, else the label of its shortcut."""
    word = values.get(WORD_ITEM[op])
    if word in (None, "", conventions.VOICE_TERMS):
        word = next((label for _, label, action in profile_keys(values) if action == op), None)
    if not word:
        raise CommandSetError(f"the profile has no word for the operation `{op}`; set `{WORD_ITEM[op]}` in it")
    return word


def keys_of(values, op):
    return [k for k, _, action in profile_keys(values) if action == op]


def split_app_rows(rows, values, pid, has):
    """(own, overrides): the rows of the application's own commands, and `{operation: {"keys", "enabled", "runs"}}` from the rows that name a profile command.

    A row that names a command of the profile may give it keys where the profile gives none, a condition for
    `Enabled when` and the sentence of `Runs`; it stops the run when it changes a key the profile gives, or takes a key another command holds.
    The profile's help (F1) is not in the command set, so a row of the application's own may take that label and key.
    """
    by_label = {}
    for keys, label, action in profile_keys(values):
        if action != "help":
            by_label.setdefault(label, []).append(keys)
    op_of = {values[item]: op for op, item in WORD_ITEM.items() if values.get(item) not in (None, "", conventions.VOICE_TERMS)}
    owner = {keys: label for keys, label, action in profile_keys(values) if action != "help"}
    taken, own, overrides = {}, [], {}
    for row in rows:
        label = row["label"]
        op = op_of.get(label)
        if label in by_label or op:
            theirs = keys_of(values, op) if op else by_label.get(label, [])
            if not op or op not in has:
                raise CommandSetError(f"`## Commands` row `{label}` is a command of the profile `{pid}` (keys: {', '.join(theirs) or 'none'}); "
                                      f"list its action in `- Operations:` and take its keys from the profile")
            if row["keys"] and theirs and set(row["keys"]) != set(theirs):
                raise CommandSetError(f"`## Commands` row `{label}` is a command of the profile `{pid}` (keys: {', '.join(theirs)}); "
                                      f"a row may give keys only to a profile command that has none")
            keys = theirs or row["keys"]
            overrides[op] = {"keys": keys, "enabled": row["enabled"] if row["enabled_given"] else None,
                             "runs": row["runs"].strip() or None}
            added = [k for k in keys if k not in theirs]
        else:
            own.append(row)
            added = row["keys"]
        for k in added:
            if k in owner:
                raise CommandSetError(f"`## Commands` row `{label}`: the key {k} is the profile `{pid}`'s key for `{owner[k]}`")
            if k in taken:
                raise CommandSetError(f"`## Commands` rows `{taken[k]}` and `{label}` take the key {k}")
            taken[k] = label
    return own, overrides


# ---------------------------------------------------------------- key tips

def clash(a, b):
    return a.startswith(b) or b.startswith(a)


def free_tip(candidates, used, what):
    for c in candidates:
        if not any(clash(c, u) for u in used):
            return c
    raise CommandSetError(f"no key tip is free for {what}")


def tab_keytips(tabs):
    """{tab: key tip}: Office's letters for its own tabs, else the first free letter of the tab's name, then A to Z."""
    out, used = {}, ["F"]
    for tab in tabs:
        if tab in TAB_TIPS:
            out[tab] = TAB_TIPS[tab]
            used.append(TAB_TIPS[tab])
    for tab in tabs:
        if tab not in out:
            letters = [c for c in tab.upper() if c in LATIN]
            out[tab] = free_tip(letters + list(LATIN), used, f"the tab `{tab}`")
            used.append(out[tab])
    return out


def assign_tips(entries, what):
    """Fills `keytip` of each entry dict, in place: fixed and explicit tips first, then the first free letter.

    An entry holds `label`, `keytip` ('' to choose one) and `hint`, the letters tried before A to Z.
    """
    used = []
    for e in entries:
        if e["keytip"]:
            if not KEY_TIP.match(e["keytip"]):
                raise CommandSetError(f"the key tip `{e['keytip']}` of `{e['label']}` is one to three letters or digits")
            hit = next((u for u in used if clash(e["keytip"], u[0])), None)
            if hit:
                raise CommandSetError(f"the key tips of `{hit[1]}` and `{e['label']}` clash in {what}: {hit[0]} and {e['keytip']}")
            used.append((e["keytip"], e["label"]))
    for e in entries:
        if not e["keytip"]:
            e["keytip"] = free_tip(e.get("hint", "") + LATIN, [u[0] for u in used], f"`{e['label']}` in {what}")
            used.append((e["keytip"], e["label"]))


# ---------------------------------------------------------------- building the command set

def make_row(id_, place, tab, group, label, size, action, keys, keytip, enabled, runs):
    return {"id": id_, "place": place, "tab": tab, "group": group, "label": label, "size": size, "action": action,
            "keys": ", ".join(keys) if keys else "none", "keytip": keytip or "none", "enabled": enabled, "runs": runs}


def build(lines, conv):
    """The rows of `## Command set` as dicts, in the order the section lists them."""
    if not conv or conv.get("rows") is None:
        raise CommandSetError("meta.surface desktop needs a profile: set meta.profile (for example ms-office) in tokens.json")
    values, pid = conv["values"], conv["profile"]
    rows_given, operations, collapse = read_commands(lines)
    pages = read_file_view(lines)
    has = set(operations)
    app_rows, over = split_app_rows(rows_given, values, pid, has)

    def keys_for(op):
        return over[op]["keys"] if op in over else keys_of(values, op)

    def enabled_for(op):
        return (over.get(op) or {}).get("enabled") or ENABLED.get(op, "always")

    def runs_for(op):
        return (over.get(op) or {}).get("runs") or RUNS[op]

    word = {op: word_of(values, op) for op in WORD_ITEM if op in has or word_of_safe(values, op) in pages}
    file_ops = [op for op in FILE_VIEW if op in word]
    rows = []

    quick = [op for op in QUICK_ACCESS if op in has]
    for n, op in enumerate(quick, 1):
        rows.append(make_row(op, "quick-access", "", "", word[op], "small", op, keys_for(op), str(n),
                             enabled_for(op), runs_for(op)))

    app_n = len(app_rows)
    file_items = [{"id": "back", "label": BACK_LABEL, "keytip": FILE_TIPS["back"], "action": "back", "keys": [],
                   "runs": RUNS["back"]}]
    file_items += [{"id": op, "label": word[op], "keytip": FILE_TIPS[op], "action": op, "keys": keys_for(op),
                    "runs": runs_for(op)} for op in file_ops]
    claimed = {word[op] for op in file_ops} | {BACK_LABEL}
    for name, page in pages.items():
        if name not in claimed:
            app_n += 1
            file_items.append({"id": f"app-{app_n:02d}", "label": name, "keytip": FILE_APP_TIPS.get(name, ""),
                               "action": "app", "keys": [], "runs": page})
    assign_tips(file_items, "the file view")
    for it in file_items:
        rows.append(make_row(it["id"], "file-view", "", "", it["label"], "small" if it["id"] == "save" else "",
                             it["action"], it["keys"], it["keytip"], enabled_for(it["id"]), it["runs"]))

    # tab -> group -> commands; the author's groups keep their order, the operations' groups join them
    tabs = {}

    def group_of(tab, group):
        return tabs.setdefault(tab, {}).setdefault(group, [])

    for n, row in enumerate(app_rows, 1):
        group_of(row["tab"], row["group"]).append(
            {"id": f"app-{n:02d}", "label": row["label"], "size": row["size"], "action": "app", "keys": row["keys"],
             "keytip": row["keytip"], "enabled": row["enabled"], "runs": row["runs"], "hint": "".join(
                 c for c in row["tab"].upper() if c in LATIN)})
    for name, members in (CLIPBOARD, EDITING):
        present = [(op, size) for op, size in members if op in has]
        if present:
            fresh = name not in tabs.get(HOME, {})
            bucket = group_of(HOME, name)
            bucket.extend(ribbon_entry(word, op, size, keys_for(op), enabled_for(op), runs_for(op)) for op, size in present)
            if fresh and name == CLIPBOARD[0]:
                tabs[HOME] = {name: tabs[HOME].pop(name), **tabs[HOME]}
    if "zoom" in has:
        bucket = group_of(VIEW, ZOOM_GROUP)
        bucket.append({"id": "zoom", "label": ZOOM_LABEL, "size": "menu", "action": "zoom", "keys": [],
                       "keytip": RIBBON_TIPS["zoom"], "enabled": "always", "runs": RUNS["zoom"], "hint": ""})
        bucket.append({"id": "zoom-fit", "label": FIT_LABEL, "size": "large", "action": "zoom-fit", "keys": [],
                       "keytip": RIBBON_TIPS["zoom-fit"], "enabled": "always", "runs": RUNS["zoom-fit"], "hint": ""})
    order = [t for t in tabs if t != HOME]
    if HOME in tabs:
        order.insert(0, HOME)
    if "zoom" in has and VIEW in order and not any(r["tab"] == VIEW for r in app_rows):
        order.remove(VIEW)
        order.append(VIEW)

    collapse_unknown = [g for g in collapse if not any(g in tabs[t] for t in tabs)]
    if collapse_unknown:
        raise CommandSetError(f"`- Collapse:` names {', '.join(collapse_unknown)}, which no group of `## Commands` or the operations has")
    for tab in order:
        flat = [c for group in tabs[tab].values() for c in group]
        assign_tips(flat, f"the tab `{tab}`")
        for group, commands in tabs[tab].items():
            for c in commands:
                rows.append(make_row(c["id"], "ribbon", tab, group, c["label"], c["size"], c["action"], c["keys"],
                                     c["keytip"], c["enabled"], c["runs"]))
    return rows


def word_of_safe(values, op):
    try:
        return word_of(values, op)
    except CommandSetError:
        return None


def ribbon_entry(word, op, size, keys, enabled, runs):
    return {"id": op, "label": word[op], "size": size, "action": op, "keys": keys,
            "keytip": RIBBON_TIPS[op], "enabled": enabled, "runs": runs, "hint": ""}


def command_set_lines(rows):
    out = [f"## {SECTION_TITLE}", "", INTRO, "", "| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for r in rows:
        cells = [r["id"], r["place"], r["tab"], r["group"], r["label"], r["size"], r["action"], r["keys"],
                 r["keytip"], r["enabled"], r["runs"]]
        out.append("| " + " | ".join(cell(c) for c in cells) + " |")
    return out + [""]


def read_command_set(lines):
    """The rows of `## Command set` as dicts keyed like COLUMNS in lower case (`enabled when` is `enabled`)."""
    found = find_section(lines, SECTION_TITLE)
    if not found:
        raise CommandSetError("the brief has no `## Command set` section; run resolve.py first")
    keys = ("id", "place", "tab", "group", "label", "size", "action", "keys", "keytip", "enabled", "runs")
    return [dict(zip(keys, c)) for c in table_rows(lines[found[0] + 1:found[1]]) if len(c) == len(COLUMNS)]


# ---------------------------------------------------------------- the window

def status_items(value):
    left, _, right = (value or "").partition("/")
    return ([p for p in items(left) if p not in NONE_WORDS], [p for p in items(right) if p not in NONE_WORDS])


def window_rows(lines, name, zoom):
    """[(item, value)] of `## Window` as it stands after resolve: the author's rows in the order of the reference."""
    given = read_window(lines)
    known = {item for item, _ in WINDOW_DEFAULTS} | {item for item, _ in FIXED_HEIGHTS}
    by_item = dict(given)
    out = []
    for item, default in WINDOW_DEFAULTS:
        if item == "title":
            default = f"{{file}} - {name or '{product}'}"
        if item == "status bar":
            default = "none / ズーム" if zoom else "none"
        out.append((item, by_item.get(item) or default))
    out += [(item, value) for item, value in given if item not in known]
    out += [(item, str(px)) for item, px in FIXED_HEIGHTS]
    return out


def parse_pane(value, item):
    if value.strip() in NONE_WORDS:
        return None
    m = PANE.match(value.strip())
    if not m:
        raise CommandSetError(f"`## Window` row `{item}`: write `<title> <width> <min>-<max> <open|closed>`, or none")
    lo, hi, width = int(m.group("min")), int(m.group("max")), int(m.group("width"))
    if not lo <= width <= hi:
        raise CommandSetError(f"`## Window` row `{item}`: the width {width} lies outside {lo}-{hi}")
    return {"title": m.group("title"), "width": width, "min": lo, "max": hi, "open": m.group("state") == "open"}


def parse_window(rows):
    """The window as a dict from the (item, value) rows."""
    by_item = dict(rows)
    defaults = dict(WINDOW_DEFAULTS)
    out = {}
    for key, item in (("size", "size"), ("minimum", "minimum")):
        m = SIZE.match(by_item.get(item) or defaults[item])
        if not m:
            raise CommandSetError(f"`## Window` row `{item}`: write `<width>x<height>`, not `{by_item.get(item)}`")
        out[key] = {"width": int(m.group("w")), "height": int(m.group("h"))}
    if out["minimum"]["width"] > out["size"]["width"] or out["minimum"]["height"] > out["size"]["height"]:
        raise CommandSetError("`## Window`: the minimum size is larger than the size")
    out["title"] = by_item.get("title") or "{file}"
    out["leftPane"] = parse_pane(by_item.get("left pane", "none"), "left pane")
    out["rightPane"] = parse_pane(by_item.get("right pane", "none"), "right pane")
    m = DOCUMENT_MINIMUM.search(by_item.get("document", ""))
    out["documentMinWidth"] = int(m.group("px")) if m else 200
    left, right = status_items(by_item.get("status bar", ""))
    out["statusBar"] = {"left": left, "right": right}
    out["heights"] = {"titleRow": 48, "tabRow": 36, "commandArea": 112, "statusBar": 28}
    for key, item in (("titleRow", "title row height"), ("tabRow", "tab row height"),
                      ("commandArea", "command area height"), ("statusBar", "status bar height")):
        if item in by_item:
            out["heights"][key] = int(by_item[item])
    return out


def apply(lines, conv):
    """The brief with `## Window` completed and `## Command set` written after `## Conventions`."""
    rows = build(lines, conv)
    window = window_rows(lines, conv.get("name"), "zoom" in read_commands(lines)[1])
    parse_window(window)
    start, end = find_section(lines, "Window")
    body = lines[start:end]
    first = next((i for i, line in enumerate(body) if line.strip().startswith("|")), None)
    table = ["| Item | Value |", "|---|---|"] + [f"| {item} | {cell(value)} |" for item, value in window]
    if first is None:
        body = body[:1] + [""] + table + [""]
    else:
        last = first
        while last < len(body) and body[last].strip().startswith("|"):
            last += 1
        body = body[:first] + table + body[last:]
    lines = lines[:start] + body + lines[end:]
    section = command_set_lines(rows)
    found = find_section(lines, SECTION_TITLE)
    if found:
        return lines[:found[0]] + section + lines[found[1]:]
    conv_section = find_section(lines, "Conventions")
    at = conv_section[1] if conv_section else len(lines)
    return lines[:at] + section + lines[at:]


# ---------------------------------------------------------------- the files scaffold.py writes

def command_set_ts(lines):
    """`scaffold/command-set.ts`: one object per line, in the order of `## Command set`."""
    out = ["// Written by scripts/patterns/scaffold.py from the ## Command set section of ui-brief.md; change the brief and run it again.",
           'import type { CommandSpec } from "@/lib/commands"', "", "export const COMMAND_SET: CommandSpec[] = ["]
    for r in read_command_set(lines):
        fields = [("id", r["id"]), ("place", r["place"]), ("tab", r["tab"]), ("group", r["group"]), ("label", r["label"]),
                  ("size", r["size"]), ("action", r["action"]), ("keys", r["keys"]), ("keytip", r["keytip"]),
                  ("enabledWhen", r["enabled"])]
        out.append("  { " + ", ".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fields) + " },")
    return "\n".join(out + ["]", ""])


def title_colors(tokens):
    """(colors, darkColors) of the title row in hex: `muted` for the ground, `foreground` for the symbols.

    `darkColors` is None where tokens.json declares no `color_dark`; a key the dark theme leaves out takes the light value.
    """
    light = (tokens or {}).get("color") or {}
    dark = (tokens or {}).get("color_dark")

    def pick(theme, fallback):
        out = {}
        for key, name in (("background", "muted"), ("symbol", "foreground")):
            value = theme.get(name) or fallback.get(name)
            hexed = colour.oklch_to_hex(value) if value else None
            if hexed is None:
                raise CommandSetError(f"tokens.json: `{name}` is not an oklch(...) colour, which the title row's caption buttons need in hex")
            out[key] = hexed
        return out

    return pick(light, {}), (pick(dark, light) if dark else None)


def window_spec(lines, values, tokens=None):
    """`WINDOW_SPEC` as a dict: the window, the title row's colours, the tabs with their key tips, the collapse order and the save prompt."""
    spec = parse_window(window_rows(lines, None, False))
    spec["colors"], dark = title_colors(tokens)
    if dark:
        spec["darkColors"] = dark
    set_rows = read_command_set(lines)
    tabs = []
    for r in set_rows:
        if r["place"] == "ribbon" and r["tab"] not in tabs:
            tabs.append(r["tab"])
    tips = tab_keytips(tabs)
    spec["tabs"] = [{"name": t, "keytip": tips[t]} for t in tabs]
    spec["collapse"] = read_commands(lines)[2]
    buttons = values.get("confirm.close_buttons")
    sentence = values.get("confirm.close_sentence")
    if not sentence or not buttons or len(buttons) != 3:
        raise CommandSetError("the profile gives no save prompt: set confirm.close_sentence and confirm.close_buttons (three words)")
    spec["closePrompt"] = {"sentence": sentence, "buttons": list(buttons)}
    return spec


def window_spec_ts(lines, values, tokens=None):
    """`scaffold/window-spec.ts`: `WINDOW_SPEC`, read by the kit's main process and renderer."""
    body = json.dumps(window_spec(lines, values, tokens), ensure_ascii=False, indent=2)
    return ("// Written by scripts/patterns/scaffold.py from the ## Window section of ui-brief.md; change the brief and run it again.\n"
            'import type { WindowSpec } from "./window-types"\n\n'
            f"export const WINDOW_SPEC: WindowSpec = {body}\n")
