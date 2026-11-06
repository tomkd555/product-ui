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
                                 is classified by key, and a `label` beside `href` is
                                 a link; any other string literal is
                                 prose when it holds Japanese characters. A line with
                                 console., logger. or throw is skipped.

    component_entries(body, path)  the script of a .tsx, .jsx, .vue, .svelte or .astro
                                 file, read as script_entries does, with a key taken
                                 from an assignment too and a sentence in English
                                 counted as prose.

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
QUOTE = re.compile(r"[\"'`]")
# A `label` in an object that also holds one of these is the text of a link.
LINK_KEY = re.compile(r"\bhref\b|\bto\s*:\s*[\"'`]/")


def _quoted_end(body, start):
    """The index of the quote that closes the string opening at start on its own line, or None."""
    quote, i, n = body[start], start + 1, len(body)
    while i < n and body[i] != "\n":
        if body[i] == quote:
            return i
        i += 2 if body[i] == "\\" else 1
    return None


def _template_end(body, start):
    """The index of the backtick that closes the template literal opening at start, or None."""
    i, n = start + 1, len(body)
    while i < n:
        if body[i] == "`":
            return i
        if body[i] == "\\":
            i += 2
        elif body.startswith("${", i):
            i = _expression_end(body, i + 2)
            if i is None:
                return None
            i += 1
        else:
            i += 1
    return None


def _expression_end(body, i):
    """The index of the brace that closes a `${` whose expression starts at i, or None."""
    depth, n = 0, len(body)
    while i < n:
        ch = body[i]
        if ch == "}":
            if depth == 0:
                return i
            depth -= 1
        elif ch == "{":
            depth += 1
        elif ch == "`":
            i = _template_end(body, i)
            if i is None:
                return None
        elif ch in "\"'":
            i = _quoted_end(body, i) or i
        i += 1
    return None


def literals(body):
    """Yield (start, inner) for each string literal of the body.

    A quoted string ends on its own line. A template literal ends at its own backtick:
    the braces, strings and templates inside its `${ }` parts belong to it.
    """
    i = 0
    while True:
        found = QUOTE.search(body, i)
        if not found:
            return
        start = found.start()
        end = _template_end(body, start) if body[start] == "`" else _quoted_end(body, start)
        if end is None:
            i = start + 1
        else:
            yield start, body[start + 1:end]
            i = end + 1


def _object_around(body, start, end):
    """The object literal a value sits in, from its opening brace to the next closing one; "" outside one."""
    left = body.rfind("{", max(0, start - 300), start)
    right = body.find("}", end, end + 300)
    if left < 0 or right < 0 or "}" in body[left:start]:
        return ""
    return body[left:right + 1]
KEY_BEFORE = re.compile(r"(?P<key>[A-Za-z_][\w.\-]*)[\"']?\s*:\s*$")
ASSIGN_BEFORE = re.compile(r"(?P<key>[A-Za-z_][\w.\-]*)\s*=\s*[\[(]?\s*$")
SKIP_LINE =re.compile(r"console\.|logger\.|\bthrow\b|^\s*import\b|^\s*export\b[^\n]*\bfrom\b")
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


def reads_as_sentence(text):
    """A literal with a space that starts with a capital or ends in punctuation; a class list does not."""
    return bool(re.search(r"\s", text)) and (text[:1].isupper() or text[-1:] in ".!?")


def script_entries(body, embedded=False):
    """Entries of a script file that is no catalog; see the module docstring.

    `embedded` reads the script of a component file (.tsx, .jsx, .vue, .svelte, .astro):
    a `name = "text"` assignment is keyed like `name: "text"`, a key that KEY_KIND
    recognises (nameError) is a UI key when the literal reads as copy, a literal in the value position of a markup
    attribute is left to the markup rules, and a literal with no Japanese character is
    copy only when it reads as a sentence.
    """
    body = COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), body)
    lines = body.split("\n")
    found = []
    for start, inner in literals(body):
        number = line_of(body, start)
        if SKIP_LINE.search(lines[number - 1]):
            continue
        if embedded and re.search(r"[\w\-]=$", body[max(0, start - 2):start]):
            continue
        text = re.sub(r"\\(.)", lambda m: " " if m.group(1) == "n" else m.group(1), inner)
        key = None
        window = body[max(0, start - 60):start]
        before = KEY_BEFORE.search(window) or (ASSIGN_BEFORE.search(window) if embedded else None)
        if before and ((WORD.findall(before.group("key")) or [""])[-1].lower() in UI_KEYS
                       or (embedded and kind_from_key(before.group("key")) != "prose"
                           and (JAPANESE.search(text) or reads_as_sentence(text)))):
            if not (looks_like_copy(text) or (embedded and JAPANESE.search(text))):
                continue
            key = before.group("key")
            kind = kind_from_key(key)
            if kind == "label" and LINK_KEY.search(_object_around(body, start, start + len(inner) + 2)):
                kind = "link"
        elif JAPANESE.search(text) or (embedded and reads_as_sentence(text)):
            kind = "prose"
        else:
            continue
        found.append(Entry(text, kind, key, number, start + 1))
    return found


SCRIPT_BLOCK = re.compile(r"(<script\b[^<>]*>)(.*?)(</script>)", re.DOTALL | re.IGNORECASE)


def component_entries(body, path):
    """Entries of the script part of a .tsx, .jsx, .vue, .svelte or .astro file.

    A .tsx or .jsx file is script throughout. Elsewhere only the `<script>` blocks are
    read: everything outside them is blanked, so offsets and lines match the file.
    """
    if not path.lower().endswith((".vue", ".svelte", ".astro")):
        return script_entries(body, embedded=True)
    masked = re.sub(r"[^\n]", " ", body)
    for block in SCRIPT_BLOCK.finditer(body):
        start, end = block.span(2)
        masked = masked[:start] + body[start:end] + masked[end:]
    return script_entries(masked, embedded=True)


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
    tsx = ('const nameError = "名前を入力してください";\n'
           'const cls = "px-4 flex";\n'
           'const msg = ok ? "Saved the file." : "x";\n'
           '<Input placeholder="メール" className="a b" />\n')
    got = [(e.text, e.kind, e.key) for e in component_entries(tsx, "A.tsx")]
    assert got == [("名前を入力してください", "error", "nameError"),
                   ("Saved the file.", "prose", None)], got
    vue = '<template><p>"あ"</p></template>\n<script>\nconst a = ["いろは"];\n</script>\n'
    got = [(e.text, e.line) for e in component_entries(vue, "A.vue")]
    assert got == [("いろは", 3)], got
    nested = ("const a = `${(yen / 10000).toLocaleString('ja-JP', { maximumFractionDigits: 2 })}万円`\n"
              "}\n"
              "const b = `${yen}円`\n"
              "function age(n) {\n"
              "  return n === 0 ? '新築' : `築${n}年`\n")
    got = [(e.text, e.line) for e in script_entries(nested)]
    assert got == [("${(yen / 10000).toLocaleString('ja-JP', { maximumFractionDigits: 2 })}万円", 1),
                   ("${yen}円", 3), ("新築", 5), ("築${n}年", 5)], got
    links = ('const FOOTER = [{ label: "利用規約", href: "/terms" }, { to: "/help", label: "ヘルプ" }]\n'
             'const FIELDS = [{ name: "mail", label: "メールアドレス" }]\n')
    got = [(e.text, e.kind) for e in script_entries(links)]
    assert got == [("利用規約", "link"), ("ヘルプ", "link"), ("メールアドレス", "label")], got
    catalog = catalog_entries('{"form": {"label": "名前"}}', "ja.json")
    assert [(e.text, e.kind, e.key, e.line) for e in catalog] == [("名前", "label", "form.label", 1)]


if __name__ == "__main__":
    self_check()
    print("PASS")
