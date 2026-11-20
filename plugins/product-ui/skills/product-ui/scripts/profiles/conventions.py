"""product-ui: the profiles of product families and the conventions each resolves to, read by
validate.py, validate_tokens.py, patterns/resolve.py, patterns/scaffold.py, check_profile.py and
render/check_render.py. The module is named apart from patterns/library.py, which the same scripts import.

Standard library only. The source of record for the format is references/profiles.md;
change that file first when a field or a vocabulary changes.
"""

import json
import os
import re

SKILL_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PROFILE_DIR = os.path.join(SKILL_DIR, "profiles")

INHERIT = "inherit"
UNTIL_CLOSED = "until-closed"
OPERATION = "{操作}"

ENTER = ("next-field", "none")
ENTER_LAST = ("register", "none")
DISPLAY = ("bottom", "toolbar", "tooltip", "none")
FUNCTION_KEYS = tuple(f"F{n}" for n in range(1, 13))
# What a function key runs. A shortcut may also act on the lines of a slip, or on the document of a
# desktop window (references/desktop.md).
ACTIONS = ("register", "delete", "new", "lookup", "edit", "recall", "print", "search",
           "save-as", "help", "next-region", "keytips")
SHORTCUT_ACTIONS = ACTIONS + ("row-insert", "row-delete", "row-new",
                              "undo", "redo", "cut", "copy", "paste", "select-all", "open", "save", "close",
                              "find", "replace", "ribbon", "context-menu")
# The operations a profile fixes a word for.
WORDS = ("create", "save", "delete", "new", "lookup", "search", "clear", "cancel")
REQUIRED_MARK = ("text", "asterisk")
CONFIRM_REGISTER = ("always", "never")
MESSAGE_ERROR = ("field", "top-and-field")
MESSAGE_RESULT = ("toast", "bar", "near-control", "new-entry")
WAITING_BLOCK = ("screen", "button", "none")
MOTION_STEPS = ("fast", "base", "slow")
KEYTIPS = ("alt", "none")
CONFIRM_CLOSE = ("always", "never")
# The operations of a desktop window a profile may fix a word for (references/desktop.md).
WINDOW_WORDS = ("save_as", "undo", "redo", "cut", "copy", "paste", "open", "close", "print", "export",
                "select_all", "replace")

# Every item of a profile, in the order the Conventions table prints them.
ITEMS = (("keys.enter", "keys.enter_last", "keys.display", "keys.function", "keys.shortcuts")
         + tuple(f"words.{w}" for w in WORDS)
         + ("required_mark", "confirm.register", "confirm.sentence", "confirm.buttons",
            "messages.error", "messages.result", "messages.duration_ms", "messages.max",
            "waiting.block", "waiting.delay_ms", "motion"))
# The items of a desktop window. A profile may leave them out, and the Conventions table prints the
# ones a profile or its product sets, after ITEMS.
OPTIONAL_ITEMS = (tuple(f"words.{w}" for w in WINDOW_WORDS)
                  + ("keys.keytips", "confirm.close", "confirm.close_sentence", "confirm.close_buttons"))
ALL_ITEMS = ITEMS + OPTIONAL_ITEMS
# The items that state a choice in every profile; the others may be `inherit`.
EXPLICIT = ("keys.enter", "keys.enter_last", "keys.display", "keys.function", "keys.shortcuts")

VOICE_TERMS = "voice.terms"
TOKENS_MOTION = "tokens.json"
# What `inherit` gives: the value this skill uses without a profile, and the file that states it.
# VOICE_TERMS marks an operation whose word the project settles in voice.terms of tokens.json.
DEFAULTS = {
    "keys.enter": ("none", "the browser's own behaviour"),
    "keys.enter_last": ("none", "the browser's own behaviour"),
    "keys.display": ("none", "references/interaction.md"),
    "keys.function": ([], "references/interaction.md"),
    "keys.shortcuts": ([], "references/interaction.md"),
    "words.create": (VOICE_TERMS, "references/ui-copy.md, The operation vocabulary"),
    "words.save": ("保存", "references/interaction.md, Editing"),
    "words.delete": ("削除", "references/ui-copy.md, Button labels"),
    "words.new": (VOICE_TERMS, "references/ui-copy.md, The operation vocabulary"),
    "words.lookup": (VOICE_TERMS, "references/ui-copy.md, The operation vocabulary"),
    "words.search": ("検索", "references/real-screens.md, Form, sign-up and sign-in"),
    "words.clear": ("クリア", "references/real-screens.md, Business package: entry"),
    "words.cancel": ("キャンセル", "references/interaction.md, Editing"),
    "required_mark": ("text", "references/real-screens.md, Form, sign-up and sign-in"),
    "confirm.register": ("never", "references/interaction.md, Destructive and bulk actions"),
    "confirm.sentence": ("none", "references/ui-copy.md, Button labels"),
    "confirm.buttons": ([OPERATION, "キャンセル"], "references/ui-copy.md, Button labels"),
    "messages.error": ("field", "references/interaction.md, Feedback"),
    "messages.result": ("toast", "references/interaction.md, Feedback"),
    "messages.duration_ms": (5000, "references/interaction.md, Feedback"),
    "messages.max": (1, "references/interaction.md, Feedback"),
    "waiting.block": ("button", "references/interaction.md, Feedback"),
    "waiting.delay_ms": (200, "references/interaction.md, Feedback"),
    "motion": (TOKENS_MOTION, "references/tokens-format.md, motion"),
}

PROFILE_KEYS = {
    "id": str, "version": int, "name": str, "summary": str, "keys": dict, "words": dict,
    "required_mark": str, "confirm": dict, "messages": dict, "waiting": dict, "products": dict,
    "evidence": list, "from": dict,
}

CONVENTIONS_INTRO = ("Written by `scripts/patterns/resolve.py` from `meta.profile` and `meta.profile_product` of "
                     "`tokens.json` (`references/profiles.md`). Change those and run it again; an edit here is overwritten.")
CONVENTIONS_NONE = "none"
KEY_CELL = re.compile(r"^(?P<keys>\S+) (?P<label>.+) \((?P<action>[a-z-]+)\)$")


class ProfileError(Exception):
    """A profile or a product that tokens.json names and profiles/ does not hold."""


def profile_files(directory=PROFILE_DIR):
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.endswith(".json"))


def load_profiles(directory=PROFILE_DIR):
    """Every profile, keyed by id. A file that does not parse is skipped here; validate.py reports it."""
    profiles = {}
    for name in profile_files(directory):
        try:
            with open(os.path.join(directory, name), encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict) and isinstance(doc.get("id"), str):
            profiles[doc["id"]] = doc
    return profiles


def get(doc, path):
    """The value at a dotted path, or None when a segment is missing."""
    node = doc
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def key_text(entries, name):
    """A list of keys as the Conventions table prints it: `F12 登録 (register), F9 削除 (delete)`."""
    if not entries:
        return "none"
    return ", ".join(f"{e[name]} {e['label']} ({e['action']})" for e in entries)


def cell(item, value):
    """One value as the Conventions table prints it."""
    if item == "keys.function":
        return key_text(value, "key")
    if item == "keys.shortcuts":
        return key_text(value, "keys")
    if item in ("confirm.buttons", "confirm.close_buttons"):
        return ", ".join(value)
    if item == "motion" and isinstance(value, dict):
        return ", ".join(f"{step} {value[step]}" for step in MOTION_STEPS)
    return str(value)


def resolve(profile, product=None):
    """The conventions of one profile and product: [{"item", "value", "text", "from"}] in the order of ITEMS.

    A product's `set` replaces the profile's value, and `inherit` takes the value of DEFAULTS.
    """
    override = (profile.get("products") or {}).get(product, {}) if product else {}
    rows = []
    for item in ITEMS:
        if item in (override.get("set") or {}):
            value, source, refs = override["set"][item], f"{profile['id']}, product {product}", (override.get("from") or {}).get(item)
        else:
            value, source, refs = get(profile, item), profile["id"], (profile.get("from") or {}).get(item)
        if value is None or value == INHERIT:
            value, where = DEFAULTS[item]
            source = f"{INHERIT}: {where}"
        elif refs:
            source += f" [{', '.join(refs)}]"
        rows.append({"item": item, "value": value, "text": cell(item, value), "from": source})
    for item in OPTIONAL_ITEMS:
        if item in (override.get("set") or {}):
            value, source, refs = override["set"][item], f"{profile['id']}, product {product}", (override.get("from") or {}).get(item)
        else:
            value, source, refs = get(profile, item), profile["id"], (profile.get("from") or {}).get(item)
        if value is None or value == INHERIT:
            continue
        if refs:
            source += f" [{', '.join(refs)}]"
        rows.append({"item": item, "value": value, "text": cell(item, value), "from": source})
    return rows


DESKTOP_SOURCE = "desktop: references/desktop.md, When the surface is desktop (this skill's choice)"
STATUS_BAR = "status-bar"


def desktop_rows(rows, help_listed):
    """The rows of a desktop window's Conventions table: F1 ヘルプ only where the command set holds help, and a result in the status bar.

    A result the profile leaves at the default `toast` shows in the status bar (references/desktop.md); every
    other row stays as resolve returned it.
    """
    out = []
    for row in rows:
        row = dict(row)
        if row["item"] == "keys.function" and not help_listed:
            row["value"] = [e for e in row["value"] if e["action"] != "help"]
            row["text"] = cell(row["item"], row["value"])
        elif row["item"] == "messages.result" and row["value"] == "toast":
            row.update(value=STATUS_BAR, text=STATUS_BAR, **{"from": DESKTOP_SOURCE})
        out.append(row)
    return out


def defaults():
    """The conventions of a build with no profile."""
    return [{"item": item, "value": DEFAULTS[item][0], "text": cell(item, DEFAULTS[item][0]),
             "from": f"{INHERIT}: {DEFAULTS[item][1]}"} for item in ITEMS]


def read_tokens(tokens_path):
    """(profile id, product id) of a tokens.json; (None, None) when the file or the fields are missing."""
    try:
        with open(tokens_path, encoding="utf-8") as handle:
            meta = (json.load(handle) or {}).get("meta") or {}
    except (OSError, ValueError, AttributeError):
        return None, None
    return meta.get("profile") or None, meta.get("profile_product") or None


def for_tokens(tokens_path, directory=PROFILE_DIR):
    """(profile id, product id, rows) for a tokens.json; rows is None when it names no profile."""
    pid, product = read_tokens(tokens_path)
    if not pid:
        return None, None, None
    profiles = load_profiles(directory)
    if pid not in profiles:
        raise ProfileError(f"meta.profile `{pid}` has no file under profiles/; run validate_tokens.py")
    if product and product not in (profiles[pid].get("products") or {}):
        raise ProfileError(f"meta.profile_product `{product}` is not a product of `{pid}`; run validate_tokens.py")
    return pid, product, resolve(profiles[pid], product)


def table(pid, product, rows):
    """The `## Conventions` section of a brief, as lines."""
    lines = ["## Conventions", "", CONVENTIONS_INTRO, ""]
    if rows is None:
        return lines + [CONVENTIONS_NONE, ""]
    lines += [f"Profile: {pid}; product: {product or 'none'}", "", "| Item | Value | From |", "|---|---|---|"]
    lines += [f"| {r['item']} | {r['text']} | {r['from']} |" for r in rows]
    return lines + [""]


def parse_table(lines):
    """{item: value text} read back from the lines of a `## Conventions` section; None when it holds `none`."""
    found = {}
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.strip().startswith("|") and len(cells) == 3 and cells[0] in ALL_ITEMS:
            found[cells[0]] = cells[1]
    return found or None


def parse_keys(text):
    """[(keys, label, action)] from a `keys.function` or `keys.shortcuts` cell."""
    if not text or text == "none":
        return []
    out = []
    for part in text.split(", "):
        m = KEY_CELL.match(part.strip())
        if m:
            out.append((m.group("keys"), m.group("label"), m.group("action")))
    return out
