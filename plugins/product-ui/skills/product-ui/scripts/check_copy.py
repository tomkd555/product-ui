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

Prose-shaped strings get C1 (as a warning), C2, C9, C10, C12 and C15's click here /
lorem ipsum pattern here, and belong to textlint for the rest. C11 reads buttons,
labels, errors, placeholders, tooltips and navigation items. --emit-prose writes the Japanese
ones out one per line for that run. C17 reads the element text inside a navigation
block, and runs only where tokens.json sets meta.structure to "ooui"; C18 and C19
read the same mark. C21 runs only where tokens.json carries a meta.name.

Script files (.ts, .js, .mjs) outside the catalog directories are read too, through
ts_strings.py: the entries keyed title, label, text and the like, and any string with
Japanese characters. So are the string literals in the script of a .tsx, .jsx, .vue,
.svelte or .astro file. C10 skips script and catalog files that hold sample data
(a path segment or file stem such as mock, sample, fixture, seed, data). C22 to C25, C31 and C32 are warnings on wording, C29 on filler in an
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
import html
import json
import os
import re
import sys
import unicodedata

from ts_strings import (catalog_entries, component_entries, kind_from_key, line_of,
                        looks_like_copy, script_entries)

MARKUP_EXT = {".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
COMPONENT_EXT = {".jsx", ".tsx", ".vue", ".svelte", ".astro"}
CATALOG_EXT = {".json", ".ts"}
SCRIPT_EXT = {".ts", ".js", ".mjs"}
SCRIPT_SKIP = re.compile(r"\.d\.ts$|\.config\.", re.IGNORECASE)
CATALOG_DIRS = {"locales", "locale", "i18n", "messages", "lang"}

EXCLUDE_DIRS = {"node_modules", "dist", "build", ".next", ".git", ".svelte-kit", "coverage", "vendor"}
EXCLUDE_FILE = re.compile(r"\.(test|spec|min)\.", re.IGNORECASE)

# Consent, statute and regulated copy keeps the register it was drafted in.
# See "The carve-out" in references/ui-copy.md.
CARVE_OUT = {"legal", "terms", "privacy", "policy"}

# C6 allows machine-facing precision on these surfaces.
PRECISION_DIRS = {"admin", "debug", "audit", "devtools"}

# C11 allows an exclamation mark where the copy is promotional.
PROMOTIONAL_DIRS = {"marketing", "landing", "lp"}

# C10 skips script and catalog files that hold sample data.
SAMPLE_NAMES = {"mock", "mocks", "sample", "samples", "fixture", "fixtures", "seed", "data"}

JAPANESE = re.compile(r"[぀-ヿ一-鿿]")

# --- classification -------------------------------------------------------

TAG_KIND = {
    "button": "button", "a": "link", "label": "label",
    "h1": "heading", "h2": "heading", "h3": "heading",
    "h4": "heading", "h5": "heading", "h6": "heading",
    "th": "label",
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
    "TableHead": "label",
}

LABEL_KINDS = {"button", "label", "heading", "error", "tooltip", "placeholder", "link"}

# One <svg>...</svg> up to its own closing tag. prepare_markup shrinks each to `<svg/>`, so the
# leading icon of TEXT_ELEMENT is a self-closing tag and cannot run past a later </svg>.
SVG_BLOCK = re.compile(r"<svg\b[^<>]*>(?s:.*?)</svg\s*>")
TEXT_ELEMENT = re.compile(
    r"<(?P<tag>[A-Za-z][A-Za-z0-9]*)(?P<attrs>[^<>]*)>"
    r"(?:\s*<[A-Za-z][^<>]*/>)*"  # a leading icon child
    r"(?P<text>[^<>{}]+)"
    r"(?P<hidden>(?:<span\b[^<>]*(?:sr-only|visually-hidden)[^<>]*>[^<>]*</span>)*)"  # text read aloud only
    r"</",
)
INLINE_TAGS = {"span", "b", "strong", "em", "i", "small", "mark", "sub", "sup", "abbr"}
# Text between two `<` of script code (`i<n`, a generic) is code, not copy.
SCRIPT_TEXT = re.compile(r"=>|\)\s*\{|;\s*\n|\s=\s")
HEADING = re.compile(r"<(?P<tag>h[1-6])\b[^<>]*>(?P<inner>(?s:.{0,2000}?))</(?P=tag)\s*>", re.IGNORECASE)
TAG = re.compile(r"<[^<>]*>")
# A paragraph whose text runs across inline children (a link, an emphasis) is read as one sentence.
PARAGRAPH = re.compile(r"<(?P<tag>p|li|dd)\b[^<>]*>(?P<inner>(?s:.{0,2000}?))</(?P=tag)\s*>", re.IGNORECASE)
PARAGRAPH_CHILD = re.compile(r"</?(?:a|br|code|kbd|" + "|".join(sorted(INLINE_TAGS)) + r")\b[^<>]*>", re.IGNORECASE)
ATTR_TEXT = re.compile(
    r"(?<![\w-])(?P<name>aria-label|placeholder|title|alt)\s*=\s*[\"'](?P<text>[^\"']+)[\"']",
)
ATTR_KIND = {"aria-label": "aria", "placeholder": "placeholder",
             "title": "tooltip", "alt": "alt"}
ARIA_LABEL = re.compile(r"(?<![\w-])aria-label\s*=\s*[\"'](?P<text>[^\"']+)[\"']")
DISCLOSURE = re.compile(r"(?<![\w-])aria-(?:expanded|controls)\b")
LABEL_FOR = re.compile(r"(?<![\w-])(?:for|htmlFor)\s*=\s*[\"'](?P<id>[^\"']+)[\"']")
OPTION_CONTROL = re.compile(r"<(?P<tag>input|Checkbox|RadioGroupItem|Switch)\b(?P<attrs>[^<>]*)>")
OPTION_TYPE = re.compile(r"type\s*=\s*[\"'](?:checkbox|radio)[\"']")
ELEMENT_ID = re.compile(r"(?<![\w-])id\s*=\s*[\"'](?P<id>[^\"']+)[\"']")
BLOCK_EDGE = re.compile(
    r"</?(?:p|li|div|dd|dt|td|th|tr|ul|ol|section|article|nav|header|footer|main|form|table|h[1-6])\b",
    re.IGNORECASE)

# Blanked before extraction. A .vue file keeps its <template>: that is its markup.
HIDDEN_BLOCKS = [re.compile(pattern, re.DOTALL) for pattern in (
    r"<script\b.*?</script\s*>", r"<style\b.*?</style\s*>", r"<head(?=[\s>]).*?</head\s*>",
    r"<(?:noscript|title)(?=[\s>]).*?</(?:noscript|title)\s*>")]
TEMPLATE_BLOCK = re.compile(r"<template(?=[\s>]).*?</template\s*>", re.DOTALL)

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

# A // after a scheme (https://), a word or inside an attribute value (href="//cdn") stays.
COMMENT = re.compile(r"/\*.*?\*/|(?<![:\w\"'=])//[^\n]*|<!--.*?-->", re.DOTALL)

# Containers whose headings the reader does not meet on the screen (C20); prepare_markup blanks `<template>` outside .vue files.
EXCLUDED_TAGS = {"nav", "header", "footer", "aside", "menu", "dialog"}
EXCLUDED_ROLES = re.compile(r"role\s*=\s*[\"'](?:navigation|menu|dialog|alertdialog|tabpanel)[\"']")
ARIA_HIDDEN = re.compile(r"aria-hidden\s*=\s*(?:[\"']true[\"']|\{\s*true\s*\})")
CLASS_ATTR = re.compile(r"(?:class|className)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|\{`([^`]*)`\})")
HIDDEN_CLASS = re.compile(r"hidden|[\w-]+:hidden|d-none|d-\w+-none|sr-only|slick-cloned|swiper-slide-duplicate")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
             "source", "track", "wbr"}
TAG_TOKEN = re.compile(r"<(?P<close>/?)(?P<tag>[A-Za-z][A-Za-z0-9.:_-]*)(?P<attrs>(?:[^<>\"']|\"[^\"<>]*\"|'[^'<>]*')*?)(?P<self>/?)>")

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
                 offset=0, testimonial=False, name=None, hidden=False, option=False,
                 disclosure=False, alone=None):
        self.text = text.strip()
        self.kind = kind
        self.path = path
        self.line = line
        self.key = key
        self.nav = nav
        self.offset = offset
        self.testimonial = testimonial
        self.name = (name or self.text).strip()  # the accessible name: aria-label, else the text read aloud
        self.hidden = hidden          # inside a container the reader does not meet (C20)
        self.option = option          # a label that names no text field: a checkbox or radio option, a table header (C14)
        self.disclosure = disclosure  # a button that opens or closes a panel (C14)
        self.alone = alone            # a link that is all the text of its block (C5)
        self.sample = False           # from a sample-data file (C10)

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


def blank(match):
    """The match as spaces, newlines kept: offsets and lines stay those of the file."""
    return re.sub(r"[^\n]", " ", match.group(0))


def prepare_markup(body, path):
    """`body` with head, title, script, style, noscript, template and comments blanked, each svg as `<svg/>`."""
    for pattern in HIDDEN_BLOCKS:
        body = pattern.sub(blank, body)
    body = SVG_BLOCK.sub(lambda m: "<svg/>" + re.sub(r"[^\n]", " ", m.group(0)[6:]), body)
    if not path.lower().endswith(".vue"):
        body = TEMPLATE_BLOCK.sub(blank, body)
    return COMMENT.sub(blank, body)


def excluded_open(tag, attrs):
    """True when an opening tag starts a container the reader does not meet on screen."""
    if tag in EXCLUDED_TAGS or EXCLUDED_ROLES.search(attrs) or ARIA_HIDDEN.search(attrs):
        return True
    klass = CLASS_ATTR.search(attrs)
    if klass:
        tokens = (klass.group(1) or klass.group(2) or klass.group(3) or "").split()
        if any(HIDDEN_CLASS.fullmatch(token) for token in tokens):
            return True
        attrs = attrs[:klass.start()] + attrs[klass.end():]
    attrs = re.sub(r"\"[^\"]*\"|'[^']*'", '""', attrs)
    return bool(re.search(r"(?<![\w-])hidden(?![\w-])(?!\s*=\s*\{\s*false)", attrs))


def container_flags(body, offsets):
    """Map each offset to (inside an excluded container, inside a button), in one pass over the tags."""
    wanted = sorted(set(offsets))
    flags, stack, bad, button, index = {}, [], 0, 0, 0
    for token in TAG_TOKEN.finditer(body):
        while index < len(wanted) and wanted[index] < token.start():
            flags[wanted[index]] = (bad > 0, button > 0)
            index += 1
        tag = token.group("tag").lower()
        if token.group("close"):
            if any(entry[0] == tag for entry in stack):
                while stack:
                    name, was_bad, was_button = stack.pop()
                    bad, button = bad - was_bad, button - was_button
                    if name == tag:
                        break
        elif not token.group("self") and tag not in VOID_TAGS:
            attrs = token.group("attrs")
            is_bad = excluded_open(tag, attrs)
            is_button = tag == "button" or bool(re.search(r"role\s*=\s*[\"']button[\"']", attrs))
            stack.append((tag, is_bad, is_button))
            bad, button = bad + is_bad, button + is_button
    for offset in wanted[index:]:
        flags[offset] = (bad > 0, button > 0)
    return flags


def option_ids(body):
    """The ids of the checkbox and radio controls in `body`."""
    found = set()
    for control in OPTION_CONTROL.finditer(body):
        attrs = control.group("attrs")
        if control.group("tag") == "input" and not OPTION_TYPE.search(attrs):
            continue
        ident = ELEMENT_ID.search(attrs)
        if ident:
            found.add(ident.group("id"))
    return found


def alone_in_block(body, start, end):
    """True when the element at body[start:end] is all the text of its nearest block."""
    before = body[max(0, start - 1500):start]
    edges = list(BLOCK_EDGE.finditer(before))
    if edges:
        cut = before.find(">", edges[-1].end())
        before = before[cut + 1:] if cut >= 0 else ""
    after_at = body.find(">", end) + 1
    after = body[after_at:after_at + 1500]
    edge = BLOCK_EDGE.search(after)
    after = after[:edge.start()] if edge else after
    return not html.unescape(TAG.sub("", before + after)).strip()


def heading_text(inner):
    """The text content of a heading, its inline children included."""
    return " ".join(html.unescape(TAG.sub("", inner)).split())


def read_headings(body):
    """(headings, starts): the (start, end, tag, text, content offset) of each heading with no
    script expression in it, and the start of every tag read."""
    found, starts = [], set()
    for match in HEADING.finditer(body):
        if "{" in match.group("inner"):
            continue
        starts.add(match.start())
        text = heading_text(match.group("inner"))
        found.append((match.start(), match.end(), match.group("tag").lower(), text, match.start("inner")))
    return found, starts


def extract_markup(body, path):
    body = prepare_markup(body, path)
    found = []
    spans = nav_spans(body)
    quotes = nav_spans(body, TESTIMONIAL_OPEN, skip_breadcrumb=False)
    options = option_ids(body)

    def in_nav(index):
        return any(start <= index < end for start, end in spans)

    def in_quote(index):
        return any(start <= index < end for start, end in quotes)

    headings, read = read_headings(body)
    heading_spans = [(head[0], head[1]) for head in headings]
    paragraphs = []
    for match in PARAGRAPH.finditer(body):
        inner = match.group("inner")
        if "<" not in inner or "{" in inner or TAG.search(PARAGRAPH_CHILD.sub("", inner)):
            continue
        text = heading_text(inner)
        # The sentence is the paragraph's own text: a paragraph that only wraps a link is that link.
        if looks_like_copy(text) and TAG.sub("", re.sub(r"(?s)<a\b.*?</a\s*>", "", inner)).strip():
            paragraphs.append((match.start(), match.end(), text, match.start("inner")))
    heading_spans += [(start, end) for start, end, _, _ in paragraphs]

    def heading_child(match):
        """An inline element inside a heading or a paragraph read above: its text is part of that string."""
        return match.group("tag").lower() in INLINE_TAGS and any(
            start < match.start() < end for start, end in heading_spans)

    elements = [match for match in TEXT_ELEMENT.finditer(body)
                if match.start() not in read and looks_like_copy(match.group("text"))
                and not SCRIPT_TEXT.search(match.group("text")) and not heading_child(match)]
    flags = container_flags(body, [head[0] for head in headings] + [
        match.start() for match in elements
        if (COMPONENT_KIND.get(match.group("tag")) or TAG_KIND.get(match.group("tag").lower()))
        in ("heading", "label")])

    for start, _, _, text, offset in headings:
        if looks_like_copy(text):
            found.append(Str(text, "heading", path, line_of(body, start), nav=in_nav(start),
                             offset=offset, testimonial=in_quote(start), hidden=flags[start][0]))

    for start, _, text, offset in paragraphs:
        found.append(Str(text, "prose", path, line_of(body, start), nav=in_nav(start),
                         offset=offset, testimonial=in_quote(start)))

    for match in elements:
        text = match.group("text")
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
        hidden, in_button = flags.get(match.start(), (False, False))
        option = tag.lower() in ("th", "tablehead")
        if kind == "label":
            if in_button:
                kind = "button"
            else:
                target = LABEL_FOR.search(attrs)
                option = option or bool(target and target.group("id") in options) or any(
                    control.group("tag") == "input" and OPTION_TYPE.search(control.group("attrs"))
                    for control in OPTION_CONTROL.finditer(body, match.start(), match.end()))
        aria = ARIA_LABEL.search(attrs)
        name = aria.group("text") if aria else " ".join(
            (text + " " + TAG.sub(" ", match.group("hidden"))).split())
        alone = None
        if kind == "link" and text.strip() in C5_BARE:
            alone = alone_in_block(body, match.start(), match.end())
        found.append(Str(text, kind, path, line_of(body, match.start()),
                         nav=in_nav(match.start()), offset=match.start("text"),
                         testimonial=in_quote(match.start()), name=name, hidden=hidden,
                         option=option, alone=alone,
                         disclosure=kind == "button" and bool(DISCLOSURE.search(attrs))))

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


def extract_component_script(body, path):
    return [entry_str(entry, path) for entry in component_entries(body, path)]


def is_catalog(path):
    parts = {part.lower() for part in path.replace("\\", "/").split("/")}
    return bool(parts & CATALOG_DIRS)


def collect(roots):
    """Return (files, strings, suppress). A file under the carve-out is skipped entirely."""
    files, strings, suppress = [], [], {}
    targets, base_of = [], {}
    for root in roots:
        if os.path.isfile(root):
            targets.append(root)
            # The sample-data test reads a file together with its folder: src/data/order.ts is data/order.ts.
            base_of.setdefault(root, os.path.dirname(os.path.dirname(os.path.abspath(root))))
            continue
        # A folder named by a relative path keeps its own name in that test: src/data is data/.
        parent = os.path.dirname(os.path.normpath(root))
        top = parent if parent and not os.path.isabs(root) else root
        for base, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for name in names:
                targets.append(os.path.join(base, name))
                base_of.setdefault(targets[-1], top)

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
            read = extract_catalog(body, path)
        elif script:
            read = extract_script(body, path)
        else:
            read = extract_markup(body, path)
            if ext in COMPONENT_EXT:
                # A literal the markup rules already read on the same line is not read twice.
                lines = {}
                for item in read:
                    lines.setdefault(item.line, []).append(item.text)
                read += [item for item in extract_component_script(body, path)
                         if not any(item.text == text or (item.text in text and len(text) <= len(item.text) + 6)
                                    for text in lines.get(item.line, ()))]
        if ext in SCRIPT_EXT | CATALOG_EXT:
            rel = os.path.relpath(path, base_of.get(path, ".")).replace("\\", "/").lower().split("/")
            if set(rel[:-1]) & SAMPLE_NAMES or os.path.splitext(rel[-1])[0] in SAMPLE_NAMES:
                for item in read:
                    item.sample = True
        strings.extend(read)
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
C5_NAMED = re.compile(r".+[はも]こちら$")  # 「ログインはこちら」 names its destination
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
C15_EXACT = {"here", "read this", "submit", "confirm", "yes", "no"}
C15_BARE_MORE = {"learn more", "詳しく見る", "もっと見る"}
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
# An item that opens a collection by a browsing verb names its object: 「求人を探す」, 「データベースから探す」.
C17_BROWSE = re.compile(r"(を|から|で)(探す|さがす|見る|みる|調べる|知る|読む)$")

# C18: a label that names nothing. Compared on the lower-cased trimmed text.
C18 = {"概要", "詳細", "情報", "管理", "各種", "overview", "details", "information"}
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

BUDGET = {"button": 16, "label": 12, "tooltip": 80}


INTERPOLATION = re.compile(r"\$\{[^{}]*\}")


def rendered_length_text(text):
    """`text` with each `${...}` of a template literal as two full-width characters, the width a short value renders at."""
    return INTERPOLATION.sub("〇〇", text)


def width(text):
    """Length in 全角 units, white space collapsed: a wide character counts 1, a narrow one 0.5."""
    total = 0.0
    for char in " ".join(rendered_length_text(text).split()):
        total += 1.0 if unicodedata.east_asian_width(char) in "WFA" else 0.5
    return total


def in_dirs(path, names):
    return bool({p.lower() for p in path.replace("\\", "/").split("/")} & names)


def feature_shape(text):
    """The C19 pattern a text matches, or None."""
    if len(text) > 2 and text.endswith("機能"):
        return "ends with 機能"
    if C19_JA.match(text):
        return "an object name followed by 管理"
    if C19_EN.search(text):
        return "an object name followed by 'management'"
    return None


C1_ERROR_KINDS = {"button", "label", "heading", "link", "tooltip", "placeholder", "error"}
C11_KINDS = {"button", "label", "error", "placeholder", "tooltip"}


def check_string(item, voice, structure, rep, name=None, lp=False):
    text = item.text
    allow = set(voice.get("allow") or [])

    if structure == "ooui" and item.nav and text not in allow and not C17_BROWSE.search(text) and (
            C17_JA.search(text) or C17_EN.search(text)):
        rep.add("ERROR", "C17", item.path, item.line,
                f"ナビゲーション項目がタスクの名前になっている: {text!r}. "
                "オブジェクトの名前を書き、アクションはそのオブジェクトのビューに移す")

    if item.kind == "heading" and text.lower() in C18 and text not in allow:
        rep.add("WARN", "C18", item.path, item.line,
                f"generic label {text!r}; name the object or the task it governs")
    elif (item.kind == "heading" or item.nav) and text not in allow and not lp:
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
        rep.add("ERROR" if item.kind in C1_ERROR_KINDS else "WARN", "C1", item.path, item.line,
                f"冗長な言い回し: {text!r}. 「することができます」→「できます」、「〜を行う」「〜を実行する」→「〜する」")
    if C2.search(text):
        rep.add("ERROR", "C2", item.path, item.line,
                f"敬語が過剰: {text!r}. 「確認してください」の形まで下げる")

    for term, replacement in (voice.get("terms") or {}).items():
        if term in allow or item.sample:
            continue
        if term in text:
            rep.add("ERROR", "C10", item.path, item.line,
                    f"用語辞書にない語 {term!r} が {text!r} に出る。この製品では {replacement!r} を使う")

    if C15_PATTERN.search(text) or C15_PATTERN.search(item.name):
        rep.add("ERROR", "C15", item.path, item.line, f"empty label: {text!r}")

    if (item.kind in C11_KINDS or item.nav) and not lp:
        bare = text
        for term in [name, *allow]:
            bare = bare.replace(term, "") if term else bare
        key = (item.key or "").lower()
        if C11.search(bare) and "success" not in key and "toast" not in key:
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

    if item.kind == "link" and (text in C5_BARE or not C5_NAMED.search(text)):
        if text in C5_BARE and item.alone is not False:
            rep.add("ERROR", "C5", item.path, item.line,
                    f"リンクの文言が {text!r} だけで、移動先が分からない")
        elif text in C5_BARE:
            rep.add("WARN", "C5", item.path, item.line,
                    f"文中の「こちら」: {text!r}. 移動先が分かる言葉に言い換えられないか")
        elif "こちら" in text:
            rep.add("WARN", "C5", item.path, item.line,
                    f"文中の「こちら」: {text!r}. 移動先が分かる言葉に言い換えられないか")

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
        rep.add("WARN" if item.kind == "heading" else "ERROR", "C8", item.path, item.line,
                f"{item.kind} の末尾に句読点: {text!r}")

    if item.kind == "button" and text in C13 and text not in allow:
        rep.add("WARN", "C13", item.path, item.line,
                f"何をするか分からないボタン: {text!r}. 操作の名前をそのまま書く")

    budget = BUDGET.get(item.kind)
    if budget and width(text) > budget and not item.option and not item.disclosure:
        rep.add("WARN", "C14", item.path, item.line,
                f"{item.kind} が {width(text):g} 全角で、目安の {budget} を超える: {text!r}")

    lowered = re.sub(r"\W+$", "", item.name.lower())
    if item.kind in ("button", "link", "heading") and not C15_PATTERN.search(item.name):
        if lowered.startswith("are you sure") or lowered in C15_EXACT:
            rep.add("ERROR", "C15", item.path, item.line,
                    f"empty label: {item.name!r}. Name what the action does")
        elif lowered in C15_BARE_MORE:
            rep.add("WARN", "C15", item.path, item.line,
                    f"link text {item.name!r} names no target; say what it opens")

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
    """C20 - the same heading text twice in one file, outside the containers that stay out of sight."""
    first = {}
    for item in sorted((i for i in strings if i.kind == "heading" and not i.hidden), key=lambda i: i.line):
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
        english, japanese = raw["english_stock"], raw["japanese_stock"]
        bare = set(english.get("bare_stem", []))
        _STOCK.update(
            english=[(w, re.compile(
                rf"\b{re.escape(w)}(?:{'' if w in bare else 's|es|'}d|ed|ing|ly)?\b", flags))
                     for w in english["words"]],
            english_per_file=english.get("min_distinct_per_file", 3),
            english_per_string=english.get("min_distinct_per_string", 2),
            ja_words=japanese["words"],
            ja_exempt=japanese.get("exempt_before", {}),
            ja_per_file=japanese.get("min_distinct_per_file_outside_headings", 2),
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
TRIAD_SENTENCES = re.compile(
    r"(?<=[。！？])|(?<!\bInc\.)(?<!\bCo\.)(?<!\bLtd\.)(?<!\bCorp\.)(?<!\bNo\.)(?<!\bVol\.)(?<!\betc\.)(?<=[.!?])\s+",
    re.IGNORECASE)
TRIAD_NOT = re.compile(r"©|®|\(c\)|all rights reserved", re.IGNORECASE)
TRIAD_PREDICATE = re.compile(r"(です|ます|ました|ません|た|る|い)[。！？]?$")
TRIAD_EN = re.compile(r"[^,.。]{2,24}, [^,.。]{2,24}, (?:and )?[^,.。]{2,24}\.?")
TRIAD_JA = re.compile(r"[^、。]{1,16}、[^、。]{1,16}、そして[^、。]{1,16}。?")


def squash(text):
    return re.sub(r"(?<=\d),(?=\d)|\s", "", text).lower()


def is_triad(text, words):
    if len(rendered_length_text(text)) > words["triad_chars"] or TRIAD_NOT.search(text):
        return False
    parts = [p.strip() for p in TRIAD_SENTENCES.split(text) if p and p.strip()]
    if len(parts) == 3 and all(len(p) <= words["triad_part"] for p in parts) and not (
            JAPANESE.search(text) and any(TRIAD_PREDICATE.search(p) for p in parts)):
        return True
    return bool(TRIAD_EN.fullmatch(text) or TRIAD_JA.fullmatch(text))


# C31 and C32 are adapted from impeccable (Apache-2.0, pbakaus/impeccable @ df3a4abe); THIRD_PARTY_NOTICES.md lists the changes.
def check_wording(item, rep, lp):
    """C24, C25 and C32: negative parallelism, triads and theater framing, read string by string."""
    words = stock()
    if not words:
        return
    text = item.text
    if any(p.search(text) for p in words["np_en"]) or (
            (item.kind == "heading" or lp) and any(p in text for p in words["np_ja"])):
        rep.add("WARN", "C24", item.path, item.line,
                f"negative parallelism in {text!r}; state what the product is")
    for found in words["theater"].finditer(text):
        if found.group(1).lower() in words["theater_heads"]:
            rep.add("WARN", "C32", item.path, item.line,
                    f"{found.group(0)!r} in {text!r} dismisses the practice as a show; say what it does or does not do")
            break
    if item.kind in ("heading", "prose") and not item.sample and is_triad(text, words):
        rep.add("WARN", "C25", item.path, item.line,
                f"three short clauses in {text!r}; keep the one that carries the claim")


def ja_stock_hits(text, words):
    """The Japanese stock words in `text`; 「ワンストップ特例」 and the like are no hit."""
    hits = []
    for word in words["ja_words"]:
        exempt = tuple(words["ja_exempt"].get(word, ()))
        at = text.find(word)
        while at >= 0:
            if not (exempt and text.startswith(exempt, at + len(word))):
                hits.append(word)
                break
            at = text.find(word, at + 1)
    return hits


def check_stock(strings, rep):
    """C22 and C23: stock words and headline templates, judged over the file.

    C22 reports once per file, at 3 or more distinct English stock words in the file or 2 or more in
    one string. C23 reports a string of kind heading that holds a Japanese stock word or a headline
    template, and a string of another kind that holds a Japanese stock word where the file holds 2 or
    more distinct words and templates.
    """
    words = stock()
    if not words:
        return
    by_file = {}
    for item in strings:
        text = item.text
        english = [w for w, pattern in words["english"] if pattern.search(text)]
        ja = ja_stock_hits(text, words)
        templates = [m.group(0) for m in (t.search(text) for t in words["templates"]) if m]
        if english or ja or templates:
            by_file.setdefault(item.path, []).append((item, english, ja, templates))
    for path, found in by_file.items():
        distinct_english = {w for _, english, _, _ in found for w in english}
        crowded = next((entry for entry in found if len(entry[1]) >= words["english_per_string"]), None)
        if crowded or len(distinct_english) >= words["english_per_file"]:
            item, english = (crowded or next(entry for entry in found if entry[1]))[:2]
            rep.add("WARN", "C22", path, item.line,
                    f"stock words {', '.join(map(repr, sorted(distinct_english)))} in this file, "
                    f"the first in {item.text!r}; say what the product does in the words of its field")
        distinct_ja = {h for _, _, ja, templates in found for h in [*ja, *templates]}
        for item, _, ja, templates in found:
            hits = [*ja, *templates] if item.kind == "heading" else (
                ja if len(distinct_ja) >= words["ja_per_file"] else [])
            if hits:
                rep.add("WARN", "C23", item.path, item.line,
                        f"決まり文句 {', '.join(map(repr, hits))} が {item.text!r} に出る。"
                        "この製品だけに当てはまる言葉で書く")


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


# The name of a language written in that language, as a language picker lists it.
LANGUAGE_NAMES = {"english", "deutsch", "français", "español", "italiano", "português", "nederlands",
                  "bahasa indonesia", "tiếng việt"}


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
    if (letters.isupper() and len(letters) <= 4) or text.strip().lower() in LANGUAGE_NAMES:
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
        check_string(item, voice, structure, rep, name, lp_of(item.path))
        check_wording(item, rep, lp_of(item.path))
        check_latin(item, voice, name, rep)
        check_proof(item, proof, lp_of(item.path), rep)
    check_stock(strings, rep)
    check_aphorisms(strings, rep)
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

    # Sentences reach textlint: prose and error messages, with the strings of sample-data files left out.
    prose = [s for s in strings if s.kind in ("prose", "error") and s.japanese and not s.sample]
    prose_lines = []
    if args.emit_prose:
        with open(args.emit_prose, "w", encoding="utf-8", newline="\n") as handle:
            for number, item in enumerate(prose, start=1):
                handle.write(rendered_length_text(item.text).replace("\n", " ") + "\n")
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
