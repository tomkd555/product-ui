#!/usr/bin/env python3
"""product-ui: the one rule that reads user-visible strings out of script and catalog files.

Standard library only. check_copy.py imports it today and check_shippable_text.py
after it, so both scripts read a catalog or a data file through the same rule.
The source of record for the scope is references/ui-copy.md.

Two readers:
    catalog_entries(body, path)  .json and .ts files under a catalog directory: every
                                 string that reads as copy, with its dotted key.
    script_entries(body)         .ts, .js and .mjs files elsewhere: a `key: "text"`
                                 entry whose key names a UI kind (title, label, ...)
                                 is classified by key; any other string literal is
                                 prose when it holds Japanese characters. A line with
                                 console., logger. or throw is skipped.

Each entry is Entry(text, kind, key, line, offset): the offset is the character index
of the string's first character in the body, the key is None for a bare literal.

Run `python ts_strings.py` for the module's own check.
"""

import json
import re
from collections import namedtuple

Entry = namedtuple("Entry", "text kind key line offset")

JAPANESE = re.compile(r"[぀-ヿ一-鿿]")

# Ordered: the first segment that matches decides the kind.
KEY_KIND = [
    ("error", "error"), ("err", "error"), ("invalid", "error"), ("failed", "error"),
    ("button", "button"), ("btn", "button"), ("action", "button"), ("cta", "button"),
    ("label", "label"), ("field", "label"),
    ("title", "heading"), ("heading", "heading"),
    ("tooltip", "tooltip"), ("hint", "tooltip"),
    ("placeholder", "placeholder"),
    ("link", "link"),
]

# A script entry whose key ends in one of these words is copy, classified by KEY_KIND.
UI_KEYS = {"title", "heading", "label", "description", "text", "message", "body", "caption",
           "subtitle", "question", "answer", "placeholder", "button", "cta"}

TS_ENTRY = re.compile(r"[\"']?(?P<key>[A-Za-z0-9_.\-]+)[\"']?\s*:\s*[\"'](?P<text>[^\"']+)[\"']")

# A // straight after a scheme (https://) is a URL, and stays.
COMMENT = re.compile(r"/\*.*?\*/|(?<![A-Za-z]:)//[^\n]*|<!--.*?-->", re.DOTALL)
LITERAL = re.compile(
    r"\"(?P<d>(?:[^\"\\\n]|\\.)*)\"|'(?P<s>(?:[^'\\\n]|\\.)*)'"
    r"|`(?P<t>(?:[^`\\$]|\\.|\$(?!\{))*)`")
KEY_BEFORE = re.compile(r"(?P<key>[A-Za-z_][\w.\-]*)[\"']?\s*:\s*$")
SKIP_LINE = re.compile(r"console\.|logger\.|\bthrow\b|^\s*import\b|^\s*export\b[^\n]*\bfrom\b")
WORD = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+")


def line_of(body, index):
    return body.count("\n", 0, index) + 1


def kind_from_key(key):
    for segment in re.split(r"[._\-/]", key.lower()):
        for needle, kind in KEY_KIND:
            if needle == segment:
                return kind
    for needle, kind in KEY_KIND:
        if needle in key.lower():
            return kind
    return "prose"


def looks_like_copy(text):
    """Keep sentences and labels; filter out expressions, class lists and other markup."""
    text = text.strip()
    if not text or text.startswith("{") or text.startswith("$"):
        return False
    if JAPANESE.search(text):
        return True
    # A plain word is a label — "OK" and "Submit" are exactly what C13 and C15 look for.
    if re.fullmatch(r"[A-Za-z]+", text):
        return True
    # Anything else that reads as one identifier or path is markup.
    return bool(re.search(r"[A-Za-z]{2,}", text)) and not re.fullmatch(r"[\w\-./:#]+", text)


def _walk(node, prefix, body, found):
    if isinstance(node, dict):
        for key, value in node.items():
            _walk(value, f"{prefix}.{key}" if prefix else key, body, found)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk(value, f"{prefix}.{index}", body, found)
    elif isinstance(node, str) and looks_like_copy(node):
        offset = body.find(json.dumps(node, ensure_ascii=False)[1:-1])
        found.append(Entry(node, kind_from_key(prefix), prefix,
                           line_of(body, offset) if offset >= 0 else 1, max(offset, 0)))


def catalog_entries(body, path):
    """Entries of a message catalog: .json by structure, .ts by `key: "text"` pairs."""
    found = []
    if path.endswith(".json"):
        try:
            doc = json.loads(body)
        except json.JSONDecodeError:
            return found
        _walk(doc, "", body, found)
        return found
    for match in TS_ENTRY.finditer(body):
        text = match.group("text")
        if looks_like_copy(text):
            found.append(Entry(text, kind_from_key(match.group("key")), match.group("key"),
                               line_of(body, match.start()), match.start("text")))
    return found


def script_entries(body):
    """Entries of a script file that is no catalog; see the module docstring."""
    body = COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), body)
    lines = body.split("\n")
    found = []
    for match in LITERAL.finditer(body):
        group = next(name for name in "dst" if match.group(name) is not None)
        inner = match.group(group)
        number = line_of(body, match.start())
        if SKIP_LINE.search(lines[number - 1]):
            continue
        text = re.sub(r"\\(.)", lambda m: " " if m.group(1) == "n" else m.group(1), inner)
        key = None
        before = KEY_BEFORE.search(body[max(0, match.start() - 60):match.start()])
        if before and (WORD.findall(before.group("key")) or [""])[-1].lower() in UI_KEYS:
            if not looks_like_copy(text):
                continue
            key = before.group("key")
            kind = kind_from_key(key)
        elif JAPANESE.search(text):
            kind = "prose"
        else:
            continue
        found.append(Entry(text, kind, key, number, match.start() + 1))
    return found


def self_check():
    """Assert the rule on a small sample; raise AssertionError on a mismatch."""
    body = ('export const A = [\n'
            '  { title: "概要", emptyText: "Nothing here", topic: "残価設定", cls: "px-4 py-2" },\n'
            '  { question: \'どうなりますか。\' },\n'
            '];\n'
            'console.log("ログ");\n'
            '// title: "コメント"\n'
            'throw new Error("失敗しました");\n')
    got = [(e.text, e.kind, e.key, e.line) for e in script_entries(body)]
    assert got == [("概要", "heading", "title", 2), ("Nothing here", "prose", "emptyText", 2),
                   ("残価設定", "prose", None, 2), ("どうなりますか。", "prose", "question", 3)], got
    first = script_entries(body)[0]
    assert body[first.offset:first.offset + 2] == "概要"
    long = "/* " + "x" * 300 + " */\n" + body
    assert long[script_entries(long)[0].offset:][:2] == "概要"
    catalog = catalog_entries('{"form": {"label": "名前"}}', "ja.json")
    assert [(e.text, e.kind, e.key, e.line) for e in catalog] == [("名前", "label", "form.label", 1)]


if __name__ == "__main__":
    self_check()
    print("PASS")
