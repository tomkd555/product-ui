#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) validation of the profiles under profiles/.

Standard library only. Checks every profile file: its fields, the set each value is drawn from,
its sources and its products. The source of record for these rules is references/profiles.md;
change that file first when a rule changes.

An error means a profile cannot be used: patterns/resolve.py would write a Conventions table the
build and the checks read wrongly.

CLI:
    python validate.py [<profiles dir>] [--json]

Exit codes: 0 = PASS (no errors), 1 = FAIL (one or more errors).
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conventions  # noqa: E402

ID = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
MS = re.compile(r"^\d+ms$")
# As the kit's lib/keys.ts writes a pressed key: the modifiers in the order Ctrl, Shift, Alt, then a capital, a digit or a named key.
SHORTCUT = re.compile(r"^(?=.+\+)(?:Ctrl\+)?(?:Shift\+)?(?:Alt\+)?(?:[A-Z0-9]|F(?:[1-9]|1[0-2])|Enter|Insert|Delete|Home|End|PageUp|PageDown|"
                      r"ArrowUp|ArrowDown|ArrowLeft|ArrowRight|Escape|Tab|Backspace)$")
TABLE_BREAKERS = ("|", "\n")
LABEL_BREAKERS = ("|", "\n", ",", "(", ")")
SURU = ("する", "します")

SETS = {
    "keys.enter": conventions.ENTER,
    "keys.enter_last": conventions.ENTER_LAST,
    "keys.display": conventions.DISPLAY,
    "required_mark": conventions.REQUIRED_MARK,
    "confirm.register": conventions.CONFIRM_REGISTER,
    "messages.error": conventions.MESSAGE_ERROR,
    "messages.result": conventions.MESSAGE_RESULT,
    "waiting.block": conventions.WAITING_BLOCK,
    "keys.keytips": conventions.KEYTIPS,
    "confirm.close": conventions.CONFIRM_CLOSE,
}


class Report:
    def __init__(self):
        self.errors = []

    def error(self, check_id, path, message):
        self.errors.append({"id": check_id, "path": path, "message": message})


def plain(text, breakers):
    return isinstance(text, str) and bool(text.strip()) and not any(b in text for b in breakers)


def check_keys(item, value, where, rep):
    """PFV3 and PFV4 on a `keys.function` or `keys.shortcuts` list."""
    function = item == "keys.function"
    name, actions = ("key", conventions.ACTIONS) if function else ("keys", conventions.SHORTCUT_ACTIONS)
    if not isinstance(value, list):
        rep.error("PFV3", where, "a list of keys, each an object; write [] for none")
        return
    seen = set()
    for i, entry in enumerate(value):
        at = f"{where}[{i}]"
        if not isinstance(entry, dict):
            rep.error("PFV3", at, f"an object with `{name}`, `label` and `action`")
            continue
        key = entry.get(name)
        if not isinstance(key, str):
            rep.error("PFV3", at, f"`{name}` is a string, found {key!r}")
            continue
        if function and key not in conventions.FUNCTION_KEYS:
            rep.error("PFV3", at, f"`key` is one of F1 to F12, found {key!r}")
        if not function and not SHORTCUT.match(key):
            rep.error("PFV3", at, f"`keys` is a combination as the kit writes it, such as Ctrl+Enter, Ctrl+Shift+N or Shift+F8, found {key!r}")
        if key in seen:
            rep.error("PFV3", at, f"{key} appears twice")
        seen.add(key)
        if not plain(entry.get("label"), LABEL_BREAKERS):
            rep.error("PFV3", at, "`label` is a non-empty word without `|`, a comma or a parenthesis")
        elif entry["label"].endswith(SURU):
            rep.error("PFV4", at, f"the label `{entry['label']}` ends in する or します; a button names its operation "
                      "by the noun or the plain form (references/ui-copy.md, Button labels)")
        if entry.get("action") not in actions:
            rep.error("PFV3", at, f"`action` is one of {', '.join(actions)}, found {entry.get('action')!r}")


def check_value(item, value, where, rep):
    """PFV3 and PFV4 on one item's value."""
    if value is None:
        rep.error("PFV1", where, "missing")
        return
    if item in ("keys.function", "keys.shortcuts"):
        check_keys(item, value, where, rep)
        return
    if value == conventions.INHERIT:
        if item in conventions.EXPLICIT:
            rep.error("PFV3", where, "a profile states this choice: write its value in place of `inherit`")
        return
    if item in SETS:
        if value not in SETS[item]:
            rep.error("PFV3", where, f"one of {', '.join(SETS[item])}"
                      + ("" if item in conventions.EXPLICIT else f" or {conventions.INHERIT}") + f", found {value!r}")
    elif item.startswith("words."):
        if not plain(value, LABEL_BREAKERS):
            rep.error("PFV3", where, "a non-empty word without `|`, a comma or a parenthesis, or `inherit`")
        elif value.endswith(SURU):
            rep.error("PFV4", where, f"`{value}` ends in する or します; a button names its operation by the noun "
                      "or the plain form (references/ui-copy.md, Button labels)")
    elif item == "confirm.sentence":
        if not plain(value, TABLE_BREAKERS) or conventions.OPERATION not in value:
            rep.error("PFV3", where, f"a sentence that holds {conventions.OPERATION}, or `inherit`")
    elif item == "confirm.buttons":
        if not (isinstance(value, list) and len(value) == 2 and all(plain(v, LABEL_BREAKERS) for v in value)):
            rep.error("PFV3", where, "two words, the confirming one first, or `inherit`")
        elif any(v.endswith(SURU) for v in value):
            rep.error("PFV4", where, "a button label ends in する or します (references/ui-copy.md, Button labels)")
    elif item == "confirm.close_sentence":
        if not plain(value, TABLE_BREAKERS):
            rep.error("PFV3", where, "a sentence without `|`, or `inherit`")
    elif item == "confirm.close_buttons":
        if not (isinstance(value, list) and len(value) == 3 and all(plain(v, LABEL_BREAKERS) for v in value)):
            rep.error("PFV3", where, "three words: the saving one, the one that goes on without saving, the cancelling one; or `inherit`")
        elif any(v.endswith(SURU) for v in value):
            rep.error("PFV4", where, "a button label ends in する or します (references/ui-copy.md, Button labels)")
    elif item == "messages.duration_ms":
        if value != conventions.UNTIL_CLOSED and not (isinstance(value, int) and not isinstance(value, bool) and value > 0):
            rep.error("PFV3", where, f"a whole number of milliseconds, `{conventions.UNTIL_CLOSED}` or `inherit`, found {value!r}")
    elif item == "messages.max":
        if not (isinstance(value, int) and not isinstance(value, bool) and value >= 1):
            rep.error("PFV3", where, f"a whole number of 1 or more, or `inherit`, found {value!r}")
    elif item == "waiting.delay_ms":
        if not (isinstance(value, int) and not isinstance(value, bool) and value >= 0):
            rep.error("PFV3", where, f"a whole number of milliseconds, or `inherit`, found {value!r}")
    elif item == "motion":
        if not (isinstance(value, dict) and set(value) == set(conventions.MOTION_STEPS)
                and all(isinstance(v, str) and MS.match(v) for v in value.values())):
            rep.error("PFV3", where, "`inherit`, or an object with fast, base and slow, each written in ms")


def check_sources(item, value, refs, evidence_ids, where, rep):
    """PFV6: a value that differs from what `inherit` gives names the evidence it rests on."""
    same = value is None or value == conventions.INHERIT or value == conventions.DEFAULTS.get(item, (None,))[0]
    if same and refs is None:
        return
    if not isinstance(refs, list) or (not refs and not same):
        rep.error("PFV6", where, f"`from` names no evidence for `{item}`")
        return
    for ref in refs:
        if ref not in evidence_ids:
            rep.error("PFV6", where, f"`from` names `{ref}`; the evidence of this profile holds no entry with that id")


def check_profile(name, doc, rep):
    """PFV1 to PFV7 on one profile file."""
    if not isinstance(doc, dict):
        rep.error("PFV1", name, "a profile file holds one JSON object")
        return
    for key, kind in conventions.PROFILE_KEYS.items():
        if key not in doc:
            rep.error("PFV1", name, f"missing field `{key}`")
        elif not isinstance(doc[key], kind) or (kind is int and isinstance(doc[key], bool)):
            rep.error("PFV1", name, f"`{key}` must be a {kind.__name__}")
    if "motion" not in doc:
        rep.error("PFV1", name, "missing field `motion`")
    pid = doc.get("id")
    if isinstance(pid, str):
        if not ID.match(pid):
            rep.error("PFV2", name, f"id `{pid}` must be lower case joined by hyphens (`jp-core`)")
        if name != pid + ".json":
            rep.error("PFV2", name, f"the file name must be the id: `{pid}.json`")
    for key in ("name", "summary"):
        if isinstance(doc.get(key), str) and not doc[key].strip():
            rep.error("PFV1", name, f"`{key}` is empty")

    evidence_ids = set()
    for i, ev in enumerate(doc.get("evidence") or []):
        where = f"{name} evidence[{i}]"
        if not isinstance(ev, dict):
            rep.error("PFV5", where, "an evidence entry is an object")
            continue
        for key in ("id", "source", "says"):
            if not isinstance(ev.get(key), str) or not ev.get(key).strip():
                rep.error("PFV5", where, f"missing `{key}`")
        # A measurement the maintainer made stands in for a page: `measured` names its record under research/.
        if isinstance(ev.get("measured"), str):
            if not ev["measured"].startswith("research/"):
                rep.error("PFV5", where, "`measured` names a file under research/")
        elif not isinstance(ev.get("url"), str) or not ev.get("url").strip():
            rep.error("PFV5", where, "missing `url` (or `measured` for a measurement)")
        elif not ev["url"].startswith("https://"):
            rep.error("PFV5", where, "the url starts with https://")
        if ev.get("id") in evidence_ids:
            rep.error("PFV5", where, f"evidence id `{ev.get('id')}` appears twice")
        evidence_ids.add(ev.get("id"))
    if not doc.get("evidence"):
        rep.error("PFV5", name, "a profile names at least one source")

    sources = doc.get("from") if isinstance(doc.get("from"), dict) else {}
    for item in sources:
        if item not in conventions.ALL_ITEMS:
            rep.error("PFV6", f"{name} from", f"`{item}` is outside the items of a profile")
    for item in conventions.ITEMS:
        value = conventions.get(doc, item)
        check_value(item, value, f"{name} {item}", rep)
        check_sources(item, value, sources.get(item), evidence_ids, f"{name} {item}", rep)
    for item in conventions.OPTIONAL_ITEMS:
        value = conventions.get(doc, item)
        if value is not None:
            check_value(item, value, f"{name} {item}", rep)
            check_sources(item, value, sources.get(item), evidence_ids, f"{name} {item}", rep)

    for product, entry in (doc.get("products") or {}).items():
        where = f"{name} products.{product}"
        if not ID.match(product):
            rep.error("PFV7", where, "a product id is lower case joined by hyphens (`yayoi-hanbai`)")
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str) or not entry.get("name", "").strip():
            rep.error("PFV7", where, "a product is an object with a `name`, a `set` and a `from`")
            continue
        changes = entry.get("set")
        if not isinstance(changes, dict):
            rep.error("PFV7", where, "`set` maps an item to the value this product gives it; write {} for none")
            continue
        refs = entry.get("from") if isinstance(entry.get("from"), dict) else {}
        for item, value in changes.items():
            if item not in conventions.ALL_ITEMS:
                rep.error("PFV7", f"{where}.set", f"`{item}` is outside the items of a profile")
                continue
            check_value(item, value, f"{where}.set.{item}", rep)
            check_sources(item, value, refs.get(item), evidence_ids, f"{where}.set.{item}", rep)


def validate(directory):
    rep = Report()
    seen = set()
    for name in conventions.profile_files(directory):
        try:
            with open(os.path.join(directory, name), encoding="utf-8") as handle:
                doc = json.load(handle)
        except ValueError as exc:
            rep.error("PFV1", name, f"not valid JSON: {exc}")
            continue
        check_profile(name, doc, rep)
        if isinstance(doc, dict) and isinstance(doc.get("id"), str):
            if doc["id"] in seen:
                rep.error("PFV2", name, f"id `{doc['id']}` is used by another file")
            seen.add(doc["id"])
    return rep, len(seen)


def main():
    parser = argparse.ArgumentParser(description="Validate the product-ui profiles.")
    parser.add_argument("dir", nargs="?", default=conventions.PROFILE_DIR, help="the profiles directory")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    if not os.path.isdir(args.dir):
        print(f"FAIL: no such directory: {args.dir}", file=sys.stderr)
        return 1
    rep, count = validate(args.dir)
    status = "FAIL" if rep.errors else "PASS"
    if args.json:
        print(json.dumps({"status": status, "profiles": count, "error_count": len(rep.errors), "errors": rep.errors},
                         indent=2, ensure_ascii=False))
    else:
        for item in rep.errors:
            print(f"ERROR [{item['id']}] {item['path']}: {item['message']}")
        print(f"{status}: {count} profile(s), {len(rep.errors)} error(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
