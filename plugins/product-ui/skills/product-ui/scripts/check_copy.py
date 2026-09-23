#!/usr/bin/env python3
"""product-ui: deterministic (non-LLM) checks on the words in an interface.

Standard library only. Reads the strings a user will see out of markup and message
catalogs, sorts each one into a kind (button, label, heading, error, tooltip,
placeholder, link, prose), and runs the checks that belong to that kind. The source
of record for these rules is references/ui-copy.md; change that file first when a
check or a threshold changes.

Errors mean the string contradicts something the project settled in tokens.json under
`voice`, or carries no information. Warnings mean it departs from what the skill
recommends and a reason may exist.

Prose-shaped strings get C1, C2, C9, C10, C12 and C15's click here / lorem ipsum
pattern here, and belong to textlint for the rest. --emit-prose writes the Japanese
ones out one per line for that run.

CLI:
    python check_copy.py <path>... [--tokens tokens.json] [--emit-prose out.md] [--json]

A finding ruled on and kept is silenced from the markup itself:
    product-ui: ignore C13 <reason>        the line before, or the same line
    product-ui: ignore-file C12 <reason>   anywhere in the file
A form with no reason is reported as C0 and silences nothing. Catalogs (.json)
carry no comments; voice.allow covers a catalog term for C10 and a catalog label
for C13, and a catalog string any other check reports is rewritten.

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors).
"""

import argparse
import json
import os
import re
import sys
import unicodedata

MARKUP_EXT = {".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
CATALOG_EXT = {".json", ".ts"}
CATALOG_DIRS = {"locales", "locale", "i18n", "messages", "lang"}

EXCLUDE_DIRS = {"node_modules", "dist", "build", ".next", ".git", ".svelte-kit", "coverage"}
EXCLUDE_FILE = re.compile(r"\.(test|spec|min)\.", re.IGNORECASE)

# Consent, statute and regulated copy keeps the register it was drafted in.
# See "The carve-out" in references/ui-copy.md.
CARVE_OUT = {"legal", "terms", "privacy", "policy"}

# C6 allows machine-facing precision on these surfaces.
PRECISION_DIRS = {"admin", "debug", "audit", "devtools"}

# C11 allows an exclamation mark where the copy is promotional.
PROMOTIONAL_DIRS = {"marketing", "landing", "lp"}

JAPANESE = re.compile(r"[぀-ヿ一-鿿]")

# --- classification -------------------------------------------------------

TAG_KIND = {
    "button": "button", "a": "link", "label": "label",
    "h1": "heading", "h2": "heading", "h3": "heading",
    "h4": "heading", "h5": "heading", "h6": "heading",
}

COMPONENT_KIND = {
    "Button": "button", "AlertDialogAction": "button", "AlertDialogCancel": "button",
    "MenuItem": "button", "DropdownMenuItem": "button",
    "Label": "label", "FormLabel": "label",
    "CardTitle": "heading", "DialogTitle": "heading", "AlertDialogTitle": "heading",
    "SheetTitle": "heading", "DrawerTitle": "heading",
    "FormMessage": "error", "AlertTitle": "error",
    "TooltipContent": "tooltip",
    "Link": "link", "NavLink": "link",
}

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

LABEL_KINDS = {"button", "label", "heading", "error", "tooltip", "placeholder", "link"}

TEXT_ELEMENT = re.compile(
    r"<(?P<tag>[A-Za-z][A-Za-z0-9]*)(?P<attrs>[^<>]*)>(?P<text>[^<>{}]+)</",
)
ATTR_TEXT = re.compile(
    r"\b(?P<name>aria-label|placeholder|title|alt)\s*=\s*[\"'](?P<text>[^\"']+)[\"']",
)
ATTR_KIND = {"aria-label": "label", "placeholder": "placeholder",
             "title": "tooltip", "alt": "label"}

TS_ENTRY = re.compile(r"[\"']?(?P<key>[A-Za-z0-9_.\-]+)[\"']?\s*:\s*[\"'](?P<text>[^\"']+)[\"']")

DESTRUCTIVE = re.compile(r"destructive|danger|delete|destroy|remove", re.IGNORECASE)

COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*|<!--.*?-->", re.DOTALL)


SUPPRESS = re.compile(r"product-ui:\s*ignore(?P<file>-file)?\s+(?P<id>[SC]\d+)(?P<rest>[^\n]*)")


def parse_suppressions(text):
    """Return (by_line, by_file, bare): line->ids, ids, and lines of reason-less forms."""
    by_line, by_file, bare = {}, set(), []
    for match in SUPPRESS.finditer(text):
        line = line_of(text, match.start())
        reason = re.sub(r"(\*/\}?|-->)\s*$", "", match.group("rest")).strip()
        if not reason:
            bare.append(line)
            continue
        check_id = match.group("id")
        if match.group("file"):
            by_file.add(check_id)
        else:
            by_line.setdefault(line, set()).add(check_id)
            by_line.setdefault(line + 1, set()).add(check_id)
    return by_line, by_file, bare


class Report:
    def __init__(self):
        self.findings = []
        self.suppress = {}  # path -> (by_line, by_file)

    def add(self, severity, check_id, path, line, message):
        by_line, by_file = self.suppress.get(path, ({}, set()))
        if check_id in by_file or check_id in by_line.get(line, ()):
            return
        self.findings.append({
            "severity": severity,
            "id": check_id,
            "file": path,
            "line": line,
            "message": message,
        })

    @property
    def errors(self):
        return [f for f in self.findings if f["severity"] == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f["severity"] == "WARN"]


class Str:
    """One string a user will see, with everything the checks need to judge it."""

    def __init__(self, text, kind, path, line, key=None, destructive=False):
        self.text = text.strip()
        self.kind = kind
        self.path = path
        self.line = line
        self.key = key
        self.destructive = destructive

    @property
    def japanese(self):
        return bool(JAPANESE.search(self.text))


# --- extraction -----------------------------------------------------------

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


def extract_markup(body, path):
    found = []
    for match in TEXT_ELEMENT.finditer(body):
        text = match.group("text")
        if not looks_like_copy(text):
            continue
        tag = match.group("tag")
        attrs = match.group("attrs")
        kind = COMPONENT_KIND.get(tag) or TAG_KIND.get(tag.lower())
        if kind is None:
            if re.search(r"role\s*=\s*[\"']button[\"']", attrs):
                kind = "button"
            elif re.search(r"role\s*=\s*[\"']alert[\"']", attrs):
                kind = "error"
            else:
                kind = "prose"
        found.append(Str(text, kind, path, line_of(body, match.start()),
                         destructive=bool(DESTRUCTIVE.search(attrs))))

    for match in ATTR_TEXT.finditer(body):
        text = match.group("text")
        if not looks_like_copy(text):
            continue
        found.append(Str(text, ATTR_KIND[match.group("name")], path,
                         line_of(body, match.start())))
    return found


def walk_catalog(node, path, prefix, body, found):
    if isinstance(node, dict):
        for key, value in node.items():
            walk_catalog(value, path, f"{prefix}.{key}" if prefix else key, body, found)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            walk_catalog(value, path, f"{prefix}.{index}", body, found)
    elif isinstance(node, str) and looks_like_copy(node):
        line = 1
        quoted = json.dumps(node, ensure_ascii=False)[1:-1]
        at = body.find(quoted)
        if at >= 0:
            line = line_of(body, at)
        found.append(Str(node, kind_from_key(prefix), path, line, key=prefix,
                         destructive=bool(DESTRUCTIVE.search(prefix))))


def extract_catalog(body, path):
    found = []
    if path.endswith(".json"):
        try:
            doc = json.loads(body)
        except json.JSONDecodeError:
            return found
        walk_catalog(doc, path, "", body, found)
        return found

    for match in TS_ENTRY.finditer(body):
        text = match.group("text")
        if not looks_like_copy(text):
            continue
        key = match.group("key")
        found.append(Str(text, kind_from_key(key), path, line_of(body, match.start()),
                         key=key, destructive=bool(DESTRUCTIVE.search(key))))
    return found


def is_catalog(path):
    parts = {part.lower() for part in path.replace("\\", "/").split("/")}
    return bool(parts & CATALOG_DIRS)


def collect(roots):
    """Return (files, strings, suppress). A file under the carve-out is skipped entirely."""
    files, strings, suppress = [], [], {}
    targets = []
    for root in roots:
        if os.path.isfile(root):
            targets.append(root)
            continue
        for base, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            targets.extend(os.path.join(base, name) for name in names)

    for path in dict.fromkeys(targets):
        norm = path.replace("\\", "/")
        segments = {part.lower() for part in norm.split("/")}
        if segments & CARVE_OUT or EXCLUDE_FILE.search(os.path.basename(path)):
            continue
        ext = os.path.splitext(path)[1].lower()
        catalog = ext in CATALOG_EXT and is_catalog(norm)
        if ext not in MARKUP_EXT and not catalog:
            continue
        try:
            with open(path, encoding="utf-8") as handle:
                body = handle.read()
        except (OSError, UnicodeDecodeError):
            continue
        files.append(path)
        by_line, by_file, bare = parse_suppressions(body)
        suppress[path] = (by_line, by_file)
        for line in bare:
            strings.append(Str("", "suppression", path, line))
        if catalog:
            strings.extend(extract_catalog(body, path))
        else:
            strings.extend(extract_markup(COMMENT.sub("", body), path))
    return files, strings, suppress


# --- checks ---------------------------------------------------------------

C1 = re.compile(r"することができ(る|ます|ません)|を行(う|い|います|った|って)|を実行(する|します)")
C2 = re.compile(r"ご[぀-ヿ一-鿿]{1,8}いただけますよう"
                r"|させていただ"
                r"|お[぀-ヿ一-鿿]{1,8}になられ"
                r"|ご[一-鿿]{1,8}してください")  # kanji only: 「ご自身で設定してください」 passes
C3 = re.compile(r"(ます|ました)$")
C4 = re.compile(r"^[一-鿿]{2,4}する$")
C5_BARE = {"こちら", "詳しくはこちら", "こちらから", "こちらをご覧ください", "こちらをクリック"}
C6 = re.compile(r"エラーが発生しました|に失敗しました|不正な|無効な")
C6_SOFT = re.compile(r"できませんでした")
C6_FIX = re.compile(r"[てで]ください|お試し|確認|もう一度|やり直")
C7 = re.compile(r"(してください|を入力|を選択|をご入力|をご選択)$")
C8 = re.compile(r"[。、]$")
C11 = re.compile(r"[!！]")
C12_POLITE = re.compile(r"(です|ます|ました|ません|でした)[。！]")
# 「保存しました。」 ends in した。 without being 常体, so だ。 only counts where the
# preceding character cannot be part of a 敬体 ending.
C12_PLAIN = re.compile(r"(である|であった|だった)[。！]|(?<![んまた])だ[。！]")
C13 = {"OK", "Ok", "ＯＫ", "確認", "送信", "実行", "はい", "いいえ", "進む", "完了"}
C15_PATTERN = re.compile(r"click here|lorem ipsum", re.IGNORECASE)
C15_EXACT = {"here", "read this", "submit", "confirm", "yes", "no", "learn more"}
C15_ALLOWED = {"save", "cancel", "close", "back", "next", "skip", "done"}
C16 = re.compile(r"\b(oops|uh-oh|whoops|sorry|invalid|illegal|forbidden|prohibited|you forgot)\b",
                 re.IGNORECASE)
C16_VAGUE = re.compile(r"something went wrong", re.IGNORECASE)
C16_FIX = re.compile(r"\b(try|refresh|reload|retry|contact|check)\b", re.IGNORECASE)

BUDGET = {"button": 8, "label": 12, "tooltip": 80}


def width(text):
    """Length in 全角 units: a wide character counts 1, a narrow one 0.5."""
    total = 0.0
    for char in text:
        total += 1.0 if unicodedata.east_asian_width(char) in "WFA" else 0.5
    return total


def in_dirs(path, names):
    return bool({p.lower() for p in path.replace("\\", "/").split("/")} & names)


def check_string(item, voice, rep):
    text = item.text
    allow = set(voice.get("allow") or [])

    if C1.search(text):
        rep.add("ERROR", "C1", item.path, item.line,
                f"冗長な言い回し: {text!r}. 「することができます」→「できます」、「〜を行う」→「〜する」")
    if C2.search(text):
        rep.add("ERROR", "C2", item.path, item.line,
                f"敬語が過剰: {text!r}. 「確認してください」の形まで下げる")

    for term, replacement in (voice.get("terms") or {}).items():
        if term in allow:
            continue
        if term in text:
            rep.add("ERROR", "C10", item.path, item.line,
                    f"用語辞書にない語 {term!r} が {text!r} に出る。この製品では {replacement!r} を使う")

    if C15_PATTERN.search(text):
        rep.add("ERROR", "C15", item.path, item.line, f"empty label: {text!r}")

    if item.kind not in LABEL_KINDS:
        return

    if item.kind == "button" and C3.search(text):
        rep.add("ERROR", "C3", item.path, item.line,
                f"ボタンラベルが丁寧形: {text!r}. 動詞の終止形で書く")

    if item.kind == "button" and C4.match(text) and not item.destructive:
        rep.add("WARN", "C4", item.path, item.line,
                f"サ変動詞の「する」: {text!r} → {text[:-2]!r}. 破壊的な操作だけ「する」を残す")

    if item.kind == "link":
        if text in C5_BARE:
            rep.add("ERROR", "C5", item.path, item.line,
                    f"リンクの文言が {text!r} だけで、移動先が分からない")
        elif "こちら" in text:
            rep.add("WARN", "C5", item.path, item.line,
                    f"文中の「こちら」: {text!r}. 移動先が分かる言葉に置き換えられないか")

    if item.kind == "error" and not in_dirs(item.path, PRECISION_DIRS):
        if C6.search(text):
            rep.add("ERROR", "C6", item.path, item.line,
                    f"利用者に何も伝えないエラー: {text!r}. 事象・原因・対処を書く")
        elif C6_SOFT.search(text) and not C6_FIX.search(text):
            rep.add("ERROR", "C6", item.path, item.line,
                    f"対処が書かれていないエラー: {text!r}")

    if item.kind == "label" and C7.search(text):
        rep.add("ERROR", "C7", item.path, item.line,
                f"ラベルが文になっている: {text!r}. 項目名だけを書く")

    if item.kind in ("button", "label", "heading") and C8.search(text):
        rep.add("ERROR", "C8", item.path, item.line,
                f"{item.kind} の末尾に句読点: {text!r}")

    if C11.search(text) and not in_dirs(item.path, PROMOTIONAL_DIRS):
        key = (item.key or "").lower()
        if "success" not in key and "toast" not in key:
            rep.add("WARN", "C11", item.path, item.line,
                    f"感嘆符: {text!r}. 成功を伝えるトーストだけに使う")

    if item.kind == "button" and text in C13 and text not in allow:
        rep.add("WARN", "C13", item.path, item.line,
                f"何をするか分からないボタン: {text!r}. 操作の名前をそのまま書く")

    budget = BUDGET.get(item.kind)
    if budget and width(text) > budget:
        rep.add("WARN", "C14", item.path, item.line,
                f"{item.kind} が {width(text):g} 全角で、目安の {budget} を超える: {text!r}")

    lowered = text.lower().rstrip(".!?")
    if item.kind in ("button", "link", "heading") and not C15_PATTERN.search(text):
        if lowered.startswith("are you sure") or (
                lowered in C15_EXACT and lowered not in C15_ALLOWED):
            rep.add("ERROR", "C15", item.path, item.line,
                    f"empty label: {text!r}. Name what the action does")

    if item.kind == "error" and not in_dirs(item.path, PRECISION_DIRS):
        found = C16.search(text)
        if found:
            rep.add("ERROR", "C16", item.path, item.line,
                    f"word to keep out of errors {found.group(0)!r}: {text!r}")
        elif C16_VAGUE.search(text) and not C16_FIX.search(text):
            rep.add("ERROR", "C16", item.path, item.line,
                    f"error with no next step: {text!r}")


def check_register(strings, rep):
    """C12 — 敬体 and 常体 in one file."""
    by_file = {}
    for item in strings:
        by_file.setdefault(item.path, []).append(item)
    for path, items in by_file.items():
        polite = [i for i in items if C12_POLITE.search(i.text)]
        plain = [i for i in items if C12_PLAIN.search(i.text)]
        if polite and plain:
            rep.add("WARN", "C12", path, plain[0].line,
                    f"敬体と常体が混ざる: {polite[0].text!r} と {plain[0].text!r}")


def check_choon(strings, pairs, preferred, rep):
    """C9 — both forms of a 長音 pair present anywhere in the project."""
    seen = {}
    for item in strings:
        for short, long in pairs:
            for form in (short, long):
                # 「ユーザ」 is a substring of 「ユーザー」, so the short form only
                # counts where the next character is not the 長音 mark.
                for found in re.finditer(re.escape(form), item.text):
                    tail = item.text[found.end():found.end() + 1]
                    if form == short and tail == "ー":
                        continue
                    seen.setdefault((short, long), {}).setdefault(form, item)
    for (short, long), forms in seen.items():
        if len(forms) == 2:
            item = forms[short]
            # wordrabbit drops the 長音 from a word of five characters or more,
            # counted with the 長音; every other setting keeps it.
            pick = short if preferred == "wordrabbit" and len(long) >= 5 else long
            rep.add("ERROR", "C9", item.path, item.line,
                    f"表記ゆれ: {short!r} と {long!r} が同じプロジェクトに出る。"
                    f"katakana_choon={preferred!r} なら {pick!r} に揃える")


# --- driver ---------------------------------------------------------------

def find_tokens(roots):
    base = os.path.commonpath([os.path.abspath(r) for r in roots])
    if os.path.isfile(base):
        base = os.path.dirname(base)
    for _ in range(4):
        candidate = os.path.join(base, "tokens.json")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(base)
        if parent == base:
            break
        base = parent
    return None


def load_voice(path):
    if not path or not os.path.isfile(path):
        return {}, None
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle).get("voice") or {}, path
    except (OSError, json.JSONDecodeError):
        return {}, None


def load_choon_pairs():
    here = os.path.dirname(os.path.abspath(__file__))
    seed = os.path.join(here, "..", "assets", "voice_terms.ja.json")
    try:
        with open(seed, encoding="utf-8") as handle:
            return [tuple(pair) for pair in json.load(handle).get("choon_pairs", [])]
    except (OSError, json.JSONDecodeError, ValueError):
        return []


def run(roots, tokens_path):
    if isinstance(roots, str):
        roots = [roots]
    rep = Report()
    files, strings, rep.suppress = collect(roots)
    voice, tokens_used = load_voice(tokens_path or find_tokens(roots))

    for item in [s for s in strings if s.kind == "suppression"]:
        rep.findings.append({"severity": "WARN", "id": "C0", "file": item.path, "line": item.line,
                             "message": "suppression carries no reason, so it suppresses nothing"})
    strings = [s for s in strings if s.kind != "suppression"]
    for item in strings:
        check_string(item, voice, rep)
    check_register([s for s in strings if s.japanese], rep)
    check_choon(strings, load_choon_pairs(), voice.get("katakana_choon", "jtf"), rep)

    if not tokens_used:
        rep.add("WARN", "C10", roots[0], 0,
                "tokens.json が見つからず、用語辞書の検査 (C10) を飛ばした")
    return rep, files, strings, tokens_used


def main():
    parser = argparse.ArgumentParser(description="Check the words in a product-ui interface.")
    parser.add_argument("path", nargs="+", help="files or directories to check")
    parser.add_argument("--tokens", help="path to tokens.json (found automatically otherwise)")
    parser.add_argument("--emit-prose", help="write prose-shaped strings here for textlint")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    missing = [p for p in args.path if not os.path.exists(p)]
    if missing:
        print(f"FAIL: no such path: {', '.join(missing)}", file=sys.stderr)
        return 1

    rep, files, strings, tokens_used = run(args.path, args.tokens)

    prose = [s for s in strings if s.kind == "prose" and s.japanese]
    prose_lines = []
    if args.emit_prose:
        with open(args.emit_prose, "w", encoding="utf-8", newline="\n") as handle:
            for number, item in enumerate(prose, start=1):
                handle.write(item.text.replace("\n", " ") + "\n")
                prose_lines.append({"line": number, "file": item.path,
                                    "key": item.key, "source_line": item.line})

    status = "FAIL" if rep.errors else "PASS"

    if args.json:
        print(json.dumps({
            "status": status,
            "tokens": tokens_used,
            "files_checked": len(files),
            "strings_checked": len(strings),
            "error_count": len(rep.errors),
            "warning_count": len(rep.warnings),
            "findings": rep.findings,
            "prose_lines": prose_lines,
        }, indent=2, ensure_ascii=False))
    else:
        for item in rep.findings:
            print(f"{item['severity']:5} [{item['id']}] {item['file']}:{item['line']}: {item['message']}")
        print(f"{status}: {len(files)} file(s), {len(strings)} string(s), "
              f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
