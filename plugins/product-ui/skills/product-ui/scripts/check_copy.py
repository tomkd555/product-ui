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

Prose-shaped strings get C1, C2, C9, C10, C11, C12 and C15's click here / lorem ipsum
pattern here, and belong to textlint for the rest. --emit-prose writes the Japanese
ones out one per line for that run. C17 reads the element text inside a navigation
block, and runs only where tokens.json sets meta.structure to "ooui"; C18 and C19
read the same mark. C21 runs only where tokens.json carries a meta.name.

Script files (.ts, .js, .mjs) outside the catalog directories are read too, through
ts_strings.py: the entries keyed title, label, text and the like, and any string with
Japanese characters. C22 to C25, C28, C31 and C32 are warnings on wording, C29 on filler in an
error and C30 on the case of an English button or heading against voice.case; C26 runs where
voice.lang is "ja"; C27 is an error: a testimonial, a customer count, a "No.1" or (on
an lp surface) a figure or rating passes only when the brief's `## Proof` section holds
it. The brief is ui-brief.md beside tokens.json unless --brief names another file.

C33 to C36 read the label forms the pattern library fixes (references/patterns.md): C33 a
collection heading ending in 一覧, C34 a column header of 状況 or 状態 alone, C35 an empty
state's title in another form than the pattern's, and C36 a label the label register lists
(assets/label_register.ja.md, then label-register.md beside tokens.json, which the project grows).

CLI:
    python check_copy.py <path>... [--tokens tokens.json] [--brief ui-brief.md]
                         [--emit-prose out.md] [--json]

A finding ruled on and kept is silenced from the markup itself:
    product-ui: ignore C13 <reason>        the line before, or the same line
    product-ui: ignore-file C12 <reason>   anywhere in the file
A form with no reason is reported as C0 and silences nothing. Catalogs (.json)
carry no comments; voice.allow covers a catalog term for C10, a catalog label
for C13 and a navigation item for C17, and a catalog string for C18, C19 and C21;
a catalog string any other check reports is rewritten.

Exit codes: 0 = PASS (no errors; warnings are allowed), 1 = FAIL (one or more errors).
"""

import argparse
import json
import os
import re
import sys
import unicodedata

from ts_strings import catalog_entries, kind_from_key, line_of, looks_like_copy, script_entries

MARKUP_EXT = {".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
CATALOG_EXT = {".json", ".ts"}
SCRIPT_EXT = {".ts", ".js", ".mjs"}
SCRIPT_SKIP = re.compile(r"\.d\.ts$|\.config\.", re.IGNORECASE)
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

LABEL_KINDS = {"button", "label", "heading", "error", "tooltip", "placeholder", "link"}

TEXT_ELEMENT = re.compile(
    r"<(?P<tag>[A-Za-z][A-Za-z0-9]*)(?P<attrs>[^<>]*)>"
    r"(?:\s*<[A-Za-z][^<>]*/>|\s*<svg\b[^<>]*>(?s:.*?)</svg>)*"  # a leading icon child
    r"(?P<text>[^<>{}]+)</",
)
ATTR_TEXT = re.compile(
    r"\b(?P<name>aria-label|placeholder|title|alt)\s*=\s*[\"'](?P<text>[^\"']+)[\"']",
)
ATTR_KIND = {"aria-label": "label", "placeholder": "placeholder",
             "title": "tooltip", "alt": "label"}

# A capitalised component's text props, and the first string a toast call shows.
PROP = re.compile(
    r"(?<![\w-])(?P<name>title|heading|subtitle|description|label|text|message|caption"
    r"|emptyText|helperText)\s*=\s*"
    r"(?:\"(?P<d>[^\"]*)\"|'(?P<s>[^']*)'|\{\s*(?:\"(?P<jd>[^\"]*)\"|'(?P<js>[^']*)')\s*\})")
PROP_KIND = {"title": "heading", "heading": "heading", "label": "label"}
TOAST = re.compile(r"\btoast(?:\.(?:success|error))?\(\s*(?:\"(?P<d>[^\"]*)\"|'(?P<s>[^']*)'|`(?P<t>[^`$]*)`)")

# C27 reads the text inside these blocks as a testimonial.
TESTIMONIAL_OPEN = re.compile(
    r"<(?P<tag>blockquote)\b[^<>]*>"
    r"|<(?P<role>[A-Za-z][A-Za-z0-9]*)\b[^<>]*(?:class|className|id|data-[\w-]+)\s*=\s*[\"'{][^<>]*testimonial[^<>]*>",
    re.IGNORECASE)

# A // straight after a scheme (https://) is a URL, and stays.
COMMENT = re.compile(r"/\*.*?\*/|(?<![A-Za-z]:)//[^\n]*|<!--.*?-->", re.DOTALL)

# C17 reads the element text inside these blocks as navigation items.
NAV_OPEN = re.compile(
    r"<(?P<tag>nav|NavigationMenu|SidebarMenu)\b[^<>]*>"
    r"|<(?P<role>[A-Za-z][A-Za-z0-9]*)\b[^<>]*role\s*=\s*[\"']navigation[\"'][^<>]*>",
)
NAV_KEYS = {"nav", "navigation", "sidebar"}
# A search field inside the navigation keeps its placeholder and its tooltip.
NAV_SKIP_KINDS = {"placeholder", "tooltip"}
# A breadcrumb names where the reader is, and its last item may be a task.
BREADCRUMB = re.compile(r"breadcrumb|パンくず", re.IGNORECASE)


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

    def __init__(self, text, kind, path, line, key=None, nav=False,
                 offset=0, testimonial=False):
        self.text = text.strip()
        self.kind = kind
        self.path = path
        self.line = line
        self.key = key
        self.nav = nav
        self.offset = offset
        self.testimonial = testimonial

    @property
    def japanese(self):
        return bool(JAPANESE.search(self.text))


# --- extraction -----------------------------------------------------------

def nav_key(key):
    return bool(set(re.split(r"[._\-/]", key.lower())) & NAV_KEYS)


def nav_spans(body, opener=NAV_OPEN, skip_breadcrumb=True):
    """Spans of the blocks `opener` opens, each closed at the tag that pairs with its opening one."""
    spans = []
    for match in opener.finditer(body):
        if match.group(0).endswith("/>"):
            continue
        tag = match.group("tag") or match.group("role")
        depth, end = 0, len(body)
        for step in re.finditer(rf"<(/?){tag}\b", body[match.start():]):
            depth += -1 if step.group(1) else 1
            if depth == 0:
                end = match.start() + step.end()
                break
        # The breadcrumb mark sits on the block's own tag or on its first child's.
        if not skip_breadcrumb or not BREADCRUMB.search(
                "".join(body[match.start():end].split(">", 2)[:2])):
            spans.append((match.start(), end))
    return spans


def tag_end(body, start):
    """Index of the `>` that closes the tag whose attributes begin at `start`."""
    depth, quote = 0, None
    for index in range(start, len(body)):
        char = body[index]
        if quote:
            quote = None if char == quote else quote
        elif depth == 0 and char in "\"'":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == ">" and depth <= 0:
            return index
    return len(body)


def component_props(body, path):
    """Strs for the text props of capitalised components, and the offsets of their `title`s."""
    found, titles, seen = [], set(), set()
    for tag in re.finditer(r"<[A-Z][A-Za-z0-9.]*", body):
        for prop in PROP.finditer(body, tag.end(), tag_end(body, tag.end())):
            at = prop.start("name")
            text = next((prop.group(g) for g in ("d", "s", "jd", "js") if prop.group(g) is not None), "")
            if at in seen or not looks_like_copy(text):
                continue
            seen.add(at)
            if prop.group("name") == "title":
                titles.add(at)
            found.append(Str(text, PROP_KIND.get(prop.group("name"), "prose"), path,
                             line_of(body, at), offset=at))
    return found, titles


def extract_markup(body, path):
    found = []
    spans = nav_spans(body)
    quotes = nav_spans(body, TESTIMONIAL_OPEN, skip_breadcrumb=False)

    def in_nav(index):
        return any(start <= index < end for start, end in spans)

    def in_quote(index):
        return any(start <= index < end for start, end in quotes)

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
                         nav=in_nav(match.start()), offset=match.start("text"),
                         testimonial=in_quote(match.start())))

    props, titles = component_props(body, path)
    found.extend(props)
    for match in ATTR_TEXT.finditer(body):
        text = match.group("text")
        if not looks_like_copy(text) or match.start() in titles:
            continue
        found.append(Str(text, ATTR_KIND[match.group("name")], path,
                         line_of(body, match.start()), offset=match.start("text")))

    for match in TOAST.finditer(body):
        text = match.group("d") or match.group("s") or match.group("t") or ""
        if looks_like_copy(text):
            found.append(Str(text, "prose", path, line_of(body, match.start()),
                             offset=match.start()))
    return found


def entry_str(entry, path):
    """The Str for one ts_strings entry; the key decides the navigation mark."""
    key = entry.key or ""
    return Str(entry.text, entry.kind, path, entry.line, key=entry.key,
               nav=bool(key) and nav_key(key) and entry.kind not in NAV_SKIP_KINDS,
               offset=entry.offset, testimonial="testimonial" in key.lower())


def extract_catalog(body, path):
    return [entry_str(entry, path) for entry in catalog_entries(body, path)]


def extract_script(body, path):
    return [entry_str(entry, path) for entry in script_entries(body)]


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
        script = ext in SCRIPT_EXT and not catalog and not SCRIPT_SKIP.search(os.path.basename(path))
        if ext not in MARKUP_EXT and not catalog and not script:
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
        elif script:
            strings.extend(extract_script(body, path))
        else:
            # Each comment keeps its newlines, so a finding's line matches the file.
            strings.extend(extract_markup(
                COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), body), path))
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
C12_PLAIN = re.compile(r"(である|であった|だった|だ)[。！]")
C13 = {"OK", "Ok", "ＯＫ", "確認", "送信", "実行", "はい", "いいえ", "進む", "完了"}
C15_PATTERN = re.compile(r"click here|lorem ipsum", re.IGNORECASE)
C15_EXACT = {"here", "read this", "submit", "confirm", "yes", "no", "learn more"}
C16 = re.compile(r"\b(oops|uh-oh|whoops|sorry|invalid|illegal|forbidden|prohibited|you forgot)\b",
                 re.IGNORECASE)
C16_VAGUE = re.compile(r"something went wrong", re.IGNORECASE)
C16_FIX = re.compile(r"\b(try|refresh|reload|retry|contact|check)\b", re.IGNORECASE)
C29_PLEASE = re.compile(r"\bplease\b", re.IGNORECASE)
C29_BARE = {"this field is required", "required"}
JA_CHAR = re.compile(r"[぀-ヿ一-鿿]")
C17_JA = re.compile(r"^新規|(する|します|を[^を]{1,8})$"
                    r"|.(登録|作成|追加|編集|変更|削除|照会|入力|検索|出力|発行|送信)$")
C17_EN = re.compile(r"^(create|add|edit|register|delete|remove|search)\s+\S", re.IGNORECASE)

# C18: a label that names nothing. Compared on the lower-cased trimmed text.
C18 = {"概要", "詳細", "情報", "管理", "各種", "その他",
       "overview", "details", "information", "more", "dashboard"}
# C19: a label shaped like a feature. The class is kanji, hiragana, katakana and the 長音 mark.
C19_JA = re.compile(r"^[一-鿿ぁ-んァ-ヶー]{1,8}管理$")
C19_EN = re.compile(r"\b\w+ management$", re.IGNORECASE)
C33_JA = re.compile(r"一覧(画面)?$")
C33_EN = re.compile(r"\s+list$", re.IGNORECASE)
C34_HEADER = re.compile(r"<(?P<tag>th|TableHead)\b[^<>]*>\s*(?P<text>状況|状態)\s*</(?P=tag)>")
C35_JA = re.compile(r"^(該当する)?\S.*はありません。$")
C35_EN = re.compile(r"^No\s.+(\syet)?\.$|^No\s.+\smatch(es)?\s.+\.$")
REGISTER_FILE = "label_register.ja.md"
PROJECT_REGISTER = "label-register.md"

BUDGET = {"button": 8, "label": 12, "tooltip": 80}


def width(text):
    """Length in 全角 units: a wide character counts 1, a narrow one 0.5."""
    total = 0.0
    for char in text:
        total += 1.0 if unicodedata.east_asian_width(char) in "WFA" else 0.5
    return total


def in_dirs(path, names):
    return bool({p.lower() for p in path.replace("\\", "/").split("/")} & names)


def feature_shape(text):
    """The C19 pattern a text matches, or None."""
    if text.endswith("機能"):
        return "ends with 機能"
    if text.startswith("各種"):
        return "starts with 各種"
    if C19_JA.match(text):
        return "an object name followed by 管理"
    if C19_EN.search(text):
        return "an object name followed by 'management'"
    return None


def check_string(item, voice, structure, rep, name=None):
    text = item.text
    allow = set(voice.get("allow") or [])

    if structure == "ooui" and item.nav and text not in allow and (
            C17_JA.search(text) or C17_EN.search(text)):
        rep.add("ERROR", "C17", item.path, item.line,
                f"ナビゲーション項目がタスクの名前になっている: {text!r}. "
                "オブジェクトの名前を書き、アクションはそのオブジェクトのビューに移す")

    labelled = item.kind in ("heading", "label") or item.nav
    if labelled and text.lower() in C18 and text not in allow:
        rep.add("WARN", "C18", item.path, item.line,
                f"generic label {text!r}; name the object or the task it governs")
    elif (item.kind == "heading" or item.nav) and text not in allow:
        shape = feature_shape(text)
        if shape:
            rep.add("WARN", "C19", item.path, item.line,
                    f"feature-shaped label {text!r} ({shape}); name the object or the task it governs")
    if (name and item.kind in ("heading", "label") and name in text and len(text) > len(name)
            and text not in allow):
        rep.add("WARN", "C21", item.path, item.line,
                f"product name {name!r} inside {item.kind} {text!r}; the name appears only where "
                "the brief's `Brand area` lists it, so name the object or the task here")

    if item.kind == "heading" and text not in allow and (C33_JA.search(text) or C33_EN.search(text)):
        rep.add("WARN", "C33", item.path, item.line,
                f"collection heading {text!r} names the view; name the object, or the subset shown "
                "(references/patterns.md, labels)")

    if C1.search(text):
        rep.add("ERROR", "C1", item.path, item.line,
                f"冗長な言い回し: {text!r}. 「することができます」→「できます」、「〜を行う」「〜を実行する」→「〜する」")
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

    if C11.search(text) and not in_dirs(item.path, PROMOTIONAL_DIRS):
        key = (item.key or "").lower()
        if "success" not in key and "toast" not in key:
            rep.add("WARN", "C11", item.path, item.line,
                    f"感嘆符: {text!r}. 成功を伝えるトーストだけに使う")

    check_case(item, voice, name, rep)

    if item.kind not in LABEL_KINDS:
        return

    if item.kind == "button" and C3.search(text):
        rep.add("ERROR", "C3", item.path, item.line,
                f"ボタンラベルが丁寧形: {text!r}. 動詞の終止形で書く")

    if item.kind == "button" and C4.match(text):
        rep.add("WARN", "C4", item.path, item.line,
                f"サ変動詞の「する」: {text!r} → {text[:-2]!r}")

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

    if item.kind == "button" and text in C13 and text not in allow:
        rep.add("WARN", "C13", item.path, item.line,
                f"何をするか分からないボタン: {text!r}. 操作の名前をそのまま書く")

    budget = BUDGET.get(item.kind)
    if budget and width(text) > budget:
        rep.add("WARN", "C14", item.path, item.line,
                f"{item.kind} が {width(text):g} 全角で、目安の {budget} を超える: {text!r}")

    lowered = re.sub(r"\W+$", "", text.lower())
    if item.kind in ("button", "link", "heading") and not C15_PATTERN.search(text):
        if lowered.startswith("are you sure") or lowered in C15_EXACT:
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

    if item.kind == "error" and not in_dirs(item.path, PRECISION_DIRS):
        if C29_PLEASE.search(text) or text.lower() in C29_BARE:
            rep.add("WARN", "C29", item.path, item.line,
                    f"filler in error {text!r}; drop \"please\" and the bare \"required\", say what to enter")


def check_case(item, voice, name, rep):
    """C30 - an English button or heading of two or more words against voice.case."""
    case = voice.get("case")
    text = item.text
    if case not in ("sentence", "title") or item.kind not in ("button", "heading") or JA_CHAR.search(text):
        return
    words = text.split()
    if len(words) < 2:
        return
    terms = voice.get("terms") or {}
    known = {w.lower() for phrase in [name or "", *terms, *terms.values(), *(voice.get("allow") or [])]
             for w in phrase.split()}
    for word in words[1:] if case == "sentence" else words:
        bare = word.strip(".,:;!?()\"'")
        if not bare.isalpha() or bare.lower() in known:
            continue
        if (case == "sentence" and bare[0].isupper() and not bare.isupper()) or (
                case == "title" and bare.islower() and len(bare) >= 5):
            rep.add("WARN", "C30", item.path, item.line,
                    f"{item.kind} {text!r} breaks voice.case {case!r} at {bare!r}")
            return


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


def check_headings(strings, rep):
    """C20 - the same heading text twice in one file."""
    first = {}
    for item in sorted((i for i in strings if i.kind == "heading"), key=lambda i: i.line):
        key = (item.path, item.text)
        if key not in first:
            first[key] = item.line
        else:
            rep.add("WARN", "C20", item.path, item.line,
                    f"duplicate heading {item.text!r}, first at line {first[key]}; "
                    "one name for two places makes the reader unsure which one they are on")


def check_choon(strings, pairs, preferred, rep):
    """C9 — both forms of a 長音 pair present anywhere in the project."""
    seen = {}
    for item in strings:
        for short, long in pairs:
            for form in (short, long):
                # 「ユーザ」 is a substring of 「ユーザー」 and 「ユーザビリティ」, so the
                # short form only counts where no katakana follows it.
                for found in re.finditer(re.escape(form), item.text):
                    tail = item.text[found.end():found.end() + 1]
                    if form == short and re.match(r"[ァ-ヶー]", tail):
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


# --- C22 to C28 --------------------------------------------------------------

_STOCK = {}


def stock():
    """The compiled word lists of assets/stock_words.json; empty when the file cannot be read."""
    if _STOCK:
        return _STOCK
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(here, "..", "assets", "stock_words.json"), encoding="utf-8") as handle:
            raw = json.load(handle)
        flags = re.IGNORECASE
        proof = raw["proof"]
        _STOCK.update(
            english=[(w, re.compile(rf"\b{re.escape(w)}(?:s|es|d|ed|ing|ly)?\b", flags))
                     for w in raw["english_stock"]["words"]],
            ja_words=raw["japanese_stock"]["words"],
            templates=[re.compile(p, flags) for p in raw["headline_templates"]["patterns"]],
            np_en=[re.compile(p, flags) for p in raw["negative_parallelism"]["english"]],
            np_ja=raw["negative_parallelism"]["japanese"],
            triad_chars=raw["triad"]["max_chars"], triad_part=raw["triad"]["max_part_chars"],
            theater=re.compile(r"\b(\w+)\s+theater\b", flags),
            theater_heads=set(raw["theater"]["dismissive_heads"]),
            not_a=re.compile(raw["aphoristic_cadence"]["not_a"]),
            rebuttal=re.compile(raw["aphoristic_cadence"]["short_rebuttal"]),
            aphorisms_per_file=raw["aphoristic_cadence"]["min_per_file"],
            assertions=[re.compile(p, flags) for p in proof["assertions"]],
            figure=re.compile(proof["figure"]), rating=re.compile(proof["rating"]),
            marketing=re.compile("|".join(re.escape(w) for w in proof["marketing_words"]), flags),
            jobs=re.compile("|".join(re.escape(w) for w in proof["job_titles"]), flags))
    except (OSError, ValueError, KeyError, re.error):
        _STOCK.clear()
    return _STOCK


TESTIMONIAL_QUOTE = re.compile(
    r"[「\"“『].{4,}?[」\"”』]\s*(?:[—―–－]|\s-)\s*(?P<name>\S.*)$")
LATIN_PERSON = re.compile(r"[A-Z][a-z]+ [A-Z][a-z]+,\s*\S")
FIGURE_UNIT = re.compile(r"\s*(?:\+|%|％|[A-Za-z]+|[社名倍])")
NAME_HONORIFIC = re.compile(r"(?P<name>[^\s様さん]{1,10}(?:\s[^\s様さん]{1,10})?)(?:様|さん)")
TRIAD_SENTENCES = re.compile(r"(?<=[。！？])|(?<=[.!?])\s+")
TRIAD_EN = re.compile(r"[^,.。]{2,24}, [^,.。]{2,24}, (?:and )?[^,.。]{2,24}\.?")
TRIAD_JA = re.compile(r"[^、。]{1,16}、[^、。]{1,16}、そして[^、。]{1,16}。?")


def squash(text):
    return re.sub(r"(?<=\d),(?=\d)|\s", "", text).lower()


def is_triad(text, words):
    if len(text) > words["triad_chars"]:
        return False
    parts = [p.strip() for p in TRIAD_SENTENCES.split(text) if p.strip()]
    if len(parts) == 3 and all(len(p) <= words["triad_part"] for p in parts):
        return True
    return bool(TRIAD_EN.fullmatch(text) or TRIAD_JA.fullmatch(text))


def check_wording(item, rep, lp):
    """C22 to C25: stock vocabulary, headline templates, negative parallelism and triads."""
    words = stock()
    if not words:
        return
    text = item.text
    for word, pattern in words["english"]:
        if pattern.search(text):
            rep.add("WARN", "C22", item.path, item.line,
                    f"stock word {word!r} in {text!r}; say what the product does in the words of its field")
    hits = [w for w in words["ja_words"] if w in text]
    hits += [m.group(0) for m in (t.search(text) for t in words["templates"]) if m]
    if hits:
        rep.add("WARN", "C23", item.path, item.line,
                f"決まり文句 {', '.join(map(repr, hits))} が {text!r} に出る。"
                "この製品だけに当てはまる言葉で書く")
    if any(p.search(text) for p in words["np_en"]) or (
            (item.kind == "heading" or lp) and any(p in text for p in words["np_ja"])):
        rep.add("WARN", "C24", item.path, item.line,
                f"negative parallelism in {text!r}; state what the product is")
    for found in words["theater"].finditer(text):
        if found.group(1).lower() in words["theater_heads"]:
            rep.add("WARN", "C32", item.path, item.line,
                    f"{found.group(0)!r} in {text!r} dismisses the practice as a show; say what it does or does not do")
            break
    if item.kind in ("heading", "prose") and is_triad(text, words):
        rep.add("WARN", "C25", item.path, item.line,
                f"three short clauses in {text!r}; keep the one that carries the claim")


def check_aphorisms(strings, rep):
    """C31: three or more "Not a X. Y." or "X. Just Y." constructions in the strings of one file.

    Each string is read alone, so a construction never spans two elements. The two patterns can match the same
    sentence pair ("Not a tool. Just a platform."); such overlapping matches count once.
    """
    words = stock()
    if not words:
        return
    by_file = {}
    for item in strings:
        by_file.setdefault(item.path, []).append(item)
    for path, items in by_file.items():
        found = []
        for item in items:
            spans = sorted(m.span() for pattern in (words["not_a"], words["rebuttal"]) for m in pattern.finditer(item.text))
            merged = []
            for start, end in spans:
                if merged and start < merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], end)
                else:
                    merged.append([start, end])
            found += [(item, start, end) for start, end in merged]
        if len(found) < words["aphorisms_per_file"]:
            continue
        item, start, end = found[0]
        rep.add("WARN", "C31", path, item.line,
                f"{len(found)} aphoristic constructions in this file, the first {item.text[start:end][:80]!r}; "
                "state what the product is and does")


def check_latin(item, voice, name, rep):
    """C26: a Latin-only button, label, heading, link or navigation string on a Japanese screen."""
    if str(voice.get("lang") or "").lower() != "ja":
        return
    text = item.text
    if not (item.kind in ("button", "label", "heading", "link") or item.nav):
        return
    if JAPANESE.search(text) or not re.search(r"[A-Za-z]{2,}", text):
        return
    letters = re.sub(r"[^A-Za-z]", "", text)
    if letters.isupper() and len(letters) <= 4:
        return
    terms = voice.get("terms") or {}
    known = {w.lower() for w in [*terms, *terms.values(), *(voice.get("allow") or [])]}
    name_words = {w.lower() for w in re.findall(r"[A-Za-z]+", name or "")}
    if text.lower() in known or {w.lower() for w in re.findall(r"[A-Za-z]+", text)} <= name_words:
        return
    rep.add("WARN", "C26", item.path, item.line,
            f"{item.kind} {text!r} is Latin letters only on a Japanese screen; write it in Japanese "
            "or list it in voice.terms or voice.allow")


def proof_evidence(item, lp):
    """What the brief's Proof section must hold for this string to stand; [] when it is no proof."""
    words = stock()
    if not words:
        return []
    text = item.text
    found = []
    quote = TESTIMONIAL_QUOTE.search(text)
    if quote and (item.testimonial or NAME_HONORIFIC.search(quote.group("name"))
                  or words["jobs"].search(quote.group("name")) or LATIN_PERSON.search(quote.group("name"))
                  or re.search(r"氏", quote.group("name"))):
        found.append(quote.group("name"))
    elif item.testimonial:
        honorific = NAME_HONORIFIC.search(text)
        if honorific and words["jobs"].search(text):
            found.append(honorific.group("name"))
    for pattern in words["assertions"]:
        match = pattern.search(text)
        if match:
            figure = match.groupdict().get("figure")
            if figure:
                unit = FIGURE_UNIT.match(text, match.end("figure"))
                figure += unit.group(0) if unit else ""
            found.append(figure or match.group(0))
    if lp:
        figure = words["figure"].search(text)
        if figure and words["marketing"].search(text):
            found.append(figure.group(0))
        rating = words["rating"].search(text)
        if rating:
            found.append(rating.group(0))
    return found


def holds(proof, evidence):
    """True when the squashed proof text holds the evidence; a figure only as a whole number."""
    needle = squash(evidence)
    if needle[:1].isdigit():
        return bool(re.search(r"(?<![\d.])" + re.escape(needle) + r"(?!\d)", proof))
    return needle.replace(",", "") in proof.replace(",", "")


def check_proof(item, proof, lp, rep):
    """C27 - a proof-shaped string the brief's Proof section does not hold."""
    evidence = proof_evidence(item, lp)
    missing = [e for e in evidence if not holds(proof, e)]
    if missing:
        rep.add("ERROR", "C27", item.path, item.line,
                f"根拠のない実績・数値・声 {missing[0]!r}: {item.text!r}. "
                "ブリーフの Proof にある内容を使うか、この文言を削除する")


def check_repeats(strings, lp_of, rep):
    """C28 - the same button or link text three times in one lp file."""
    counts = {}
    for item in sorted((i for i in strings if i.kind in ("button", "link")), key=lambda i: i.line):
        if not lp_of(item.path):
            continue
        key = (item.path, item.text)
        counts[key] = counts.get(key, 0) + 1
        if counts[key] == 3:
            rep.add("WARN", "C28", item.path, item.line,
                    f"{item.text!r} is the call to action 3 times in this file; "
                    "name what each section's action does")


def load_proof(path):
    """The squashed `## Proof` section of the brief at `path`; empty when there is none."""
    if not path or not os.path.isfile(path):
        return ""
    try:
        with open(path, encoding="utf-8") as handle:
            body = handle.read()
    except (OSError, UnicodeDecodeError):
        return ""
    section = re.search(r"^##[ \t]*Proof\b[^\n]*\n(.*?)(?=^##[ \t]|\Z)", body, re.MULTILINE | re.DOTALL)
    return squash(re.sub(r"<!--.*?-->", "", section.group(1), flags=re.DOTALL)) if section else ""


def token_surface(path):
    """meta.surface of the tokens.json at `path`, lower-cased, or None."""
    try:
        with open(path, encoding="utf-8") as handle:
            surface = (json.load(handle).get("meta") or {}).get("surface")
    except (OSError, TypeError, AttributeError, json.JSONDecodeError):
        return None
    return surface.lower() if isinstance(surface, str) else None


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


def load_tokens(path):
    """Return (voice, meta.structure, meta.name, path); path is None when no file was read."""
    if not path or not os.path.isfile(path):
        return {}, None, None, None
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}, None, None, None
    meta = doc.get("meta") or {}
    return doc.get("voice") or {}, meta.get("structure"), meta.get("name"), path


def load_choon_pairs():
    here = os.path.dirname(os.path.abspath(__file__))
    seed = os.path.join(here, "..", "assets", "voice_terms.ja.json")
    try:
        with open(seed, encoding="utf-8") as handle:
            return [tuple(pair) for pair in json.load(handle).get("choon_pairs", [])]
    except (OSError, json.JSONDecodeError, ValueError):
        return []


def check_column_headers(files, rep):
    """C34 - a column header of 状況 or 状態 alone."""
    for path in files:
        if os.path.splitext(path)[1].lower() not in MARKUP_EXT:
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            body = handle.read()
        for m in C34_HEADER.finditer(body):
            rep.add("WARN", "C34", path, line_of(body, m.start()),
                    f"column header {m.group('text')!r} alone; head a status column ステータス, "
                    "or 〇〇状況 when the table has several (SmartHR, よくあるテーブル)")


def check_empty_states(files, rep):
    """C35 - an empty state's title in another form than the pattern's."""
    import check_pattern  # the element scanner the pattern checks share
    for path in files:
        if os.path.splitext(path)[1].lower() not in MARKUP_EXT:
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            body = handle.read()
        if "state.empty" not in body:
            continue
        els = check_pattern.scan(body)
        roots = [e for e in els if e["pattern"]]
        for el in els:
            own = check_pattern.owner(el, roots) if el["slot"] == "title" else None
            if not own or own["pattern"] != "state.empty":
                continue
            inner = body[el["open_end"]:el["end"]]
            inner = re.sub(r"</?[A-Za-z][^<>]*>", "", inner)
            if "{" in inner or not inner.strip():
                continue
            text = inner.strip()
            if not (C35_JA.match(text) or C35_EN.match(text)):
                rep.add("WARN", "C35", path, line_of(body, el["start"]),
                        f"empty state {text!r}; before first use 「{{object}}はありません。」, "
                        "after a filter 「該当する{object}はありません。」 (references/patterns.md, state.empty)")


def load_register(tokens_used):
    """Rows (pattern, instead, why, source) of the shipped label register and the project's own."""
    paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", REGISTER_FILE)]
    if tokens_used:
        paths.append(os.path.join(os.path.dirname(os.path.abspath(tokens_used)), PROJECT_REGISTER))
    rows = []
    for path in paths:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line.startswith("|") or re.match(r"^\|\s*-{3,}", line):
                    continue
                cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip("|"))]
                if len(cells) < 3 or cells[0] in ("Pattern", ""):
                    continue
                try:
                    rows.append((re.compile(cells[0]), cells[1], cells[2], os.path.basename(path)))
                except re.error:
                    continue
    return rows


def check_label_register(strings, register, voice, rep):
    """C36 - a label the label register lists."""
    allow = set(voice.get("allow") or [])
    for item in strings:
        if item.kind not in LABEL_KINDS or item.text in allow:
            continue
        for pattern, instead, why, source in register:
            if pattern.search(item.text):
                rep.add("WARN", "C36", item.path, item.line,
                        f"{item.text!r} is in the label register ({source}): {instead} {why}")
                break


def run(roots, tokens_path, brief_path=None):
    if isinstance(roots, str):
        roots = [roots]
    rep = Report()
    files, strings, rep.suppress = collect(roots)
    voice, structure, name, tokens_used = load_tokens(tokens_path or find_tokens(roots))
    surface = token_surface(tokens_used) if tokens_used else None
    if not brief_path and tokens_used:
        brief_path = os.path.join(os.path.dirname(os.path.abspath(tokens_used)), "ui-brief.md")
    proof = load_proof(brief_path)

    def lp_of(path):
        return surface == "lp" if surface else in_dirs(path, PROMOTIONAL_DIRS)
    name = name.strip() if isinstance(name, str) and len(name.strip()) >= 2 else None

    for item in [s for s in strings if s.kind == "suppression"]:
        rep.findings.append({"severity": "WARN", "id": "C0", "file": item.path, "line": item.line,
                             "message": "suppression carries no reason, so it suppresses nothing"})
    strings = [s for s in strings if s.kind != "suppression"]
    for item in strings:
        check_string(item, voice, structure, rep, name)
        check_wording(item, rep, lp_of(item.path))
        check_latin(item, voice, name, rep)
        check_proof(item, proof, lp_of(item.path), rep)
    check_aphorisms(strings, rep)
    check_repeats(strings, lp_of, rep)
    check_headings(strings, rep)
    check_register([s for s in strings if s.japanese], rep)
    check_choon(strings, load_choon_pairs(), voice.get("katakana_choon", "jtf"), rep)
    check_column_headers(files, rep)
    check_empty_states(files, rep)
    check_label_register(strings, load_register(tokens_used), voice, rep)

    if not stock():
        rep.add("WARN", "C22", roots[0], 0,
                "assets/stock_words.json が読めず、C22 から C25、C27、C31、C32 の語彙の検査を飛ばした")
    if not tokens_used:
        rep.add("WARN", "C10", roots[0], 0,
                "tokens.json が見つからず、用語辞書の検査 (C10)、"
                "ナビゲーション項目の検査 (C17)、製品名の検査 (C21) を飛ばした")
    return rep, files, strings, tokens_used


def main():
    parser = argparse.ArgumentParser(description="Check the words in a product-ui interface.")
    parser.add_argument("path", nargs="+", help="files or directories to check")
    parser.add_argument("--tokens", help="path to tokens.json (found automatically otherwise)")
    parser.add_argument("--brief", help="path to ui-brief.md (ui-brief.md beside tokens.json otherwise)")
    parser.add_argument("--emit-prose", help="write prose-shaped strings here for textlint")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    missing = [p for p in args.path if not os.path.exists(p)]
    if missing:
        print(f"FAIL: no such path: {', '.join(missing)}", file=sys.stderr)
        return 1

    rep, files, strings, tokens_used = run(args.path, args.tokens, args.brief)

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
