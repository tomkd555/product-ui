#!/usr/bin/env python3
"""product-ui: write the skeleton of each resolved section, deterministically.

Standard library only. Reads ui-brief.md through resolve.py (the brief must be up to date:
run resolve.py first), and writes one file per section that has a pattern, in the order the
brief lists them. Each skeleton holds the pattern's slots in the pattern's order, filled with
the properties the Slots table assigns, and marks them with the attributes check_pattern.py
and check_render.py read:

    data-pattern="<id>"          on the item (row, card, tile, badge) or the block (table, header)
    data-pattern-slot="<slot>"   on each slot
    data-pattern-field="<label>" on a slot that shows a property of the object

The build fills the data and the words and keeps the attributes. A slot is added or removed in
the brief first. The source of record is references/patterns.md.

Stacks: `shadcn` writes React (TSX) on the shadcn/ui components; `html` writes static HTML
with {{label}} placeholders; `dads` and `smarthr` write a Markdown note naming the
preset's component and the attributes each slot takes. Without --stack the stack comes from
tokens.json beside the brief: `stack.base` smarthr-ui gives smarthr, `meta.reference`
digital-agency-design-system gives dads, `stack.renderer` html or server-templates gives html,
and anything else gives shadcn.

CLI:
    python scaffold.py <ui-brief.md> [--stack shadcn|html|dads|smarthr] [--out DIR] [--json]

--out defaults to `scaffold/` beside the brief. The same brief writes the same bytes.

Exit codes: 0 = written, 1 = the brief is out of date or a section cannot be resolved.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library  # noqa: E402
import resolve  # noqa: E402

UI_IMPORT = {"Table": "table", "TableHeader": "table", "TableBody": "table", "TableRow": "table",
             "TableHead": "table", "TableCell": "table", "Badge": "badge",
             "Card": "card", "CardHeader": "card", "CardTitle": "card", "CardContent": "card"}


class El:
    def __init__(self, tag, attrs=None, children=None, html=None):
        self.tag, self.html = tag, html or tag.lower()
        self.attrs = attrs or []
        self.children = children or []


class Field:
    def __init__(self, label):
        self.label = label


class Text:
    def __init__(self, text):
        self.text = text


class Note:
    def __init__(self, text):
        self.text = text


class Loop:
    """The child repeated once per item; in JSX it takes `key`."""
    def __init__(self, child):
        self.child = child


class Expr:
    def __init__(self, jsx, html):
        self.jsx, self.html = jsx, html


def slot(name, field=None, tag="span", cls=None, children=None, html=None, extra=None):
    attrs = [("data-pattern-slot", name)]
    if field == "placeholder":
        field = None
    if field:
        attrs.append(("data-pattern-field", field))
    if cls:
        attrs.append(("class", cls))
    attrs += extra or []
    return El(tag, attrs, children if children is not None else ([Field(field)] if field else []), html)


def badge(field, slot_name):
    inner = El("span", [("data-pattern-slot", "label")], [Field(field)])
    return El("span", [("data-pattern-slot", slot_name), ("data-pattern-field", field)],
              [El("Badge", [("data-pattern", "status.badge"), ("variant", "outline")], [inner], html="span")])


def fields_of(rows, slot_id):
    return [shows for sid, shows, _ in rows if sid == slot_id]


def empty_state(obj):
    return El("div", [("data-pattern", "state.empty"), ("class", "py-8")], [
        El("p", [("data-pattern-slot", "title"), ("class", "font-semibold")], [Text(f"{obj}はありません。")]),
        Note(f"after a filter that matched nothing: 該当する{obj}はありません。, the filters kept, no create button"),
        Note("optional slot action: the action that adds the first one, first use only"),
    ])


def build(pattern, rows, obj):
    """The skeleton tree for one section: (root, needs_items)."""
    pid = pattern["id"]
    one = lambda s: (fields_of(rows, s) or [None])[0]  # noqa: E731
    if pid == "collection.row.resource":
        parts = []
        if one("media"):
            parts.append(slot("media", one("media"), "div", "size-12 shrink-0 rounded-md bg-muted", children=[]))
        parts.append(slot("name", one("name"), cls="font-semibold"))
        parts += [slot("info", f, cls="text-muted-foreground") for f in fields_of(rows, "info")]
        if one("trailing"):
            parts.append(El("span", [("class", "ml-auto")], [badge(one("trailing"), "trailing")]))
        item = El("li", [("data-pattern", pid)], [
            El("a", [("href", Expr("href(item)", "#")), ("class", "flex flex-wrap items-baseline gap-x-4 gap-y-1 py-3")], parts)])
        return El("ul", [("class", "divide-y divide-border")], [Loop(item)]), True
    if pid == "collection.table.index":
        cols = [("name", one("name"))] + ([("status", one("status"))] if one("status") else []) + \
               [("property", f) for f in fields_of(rows, "property")]
        head = El("TableRow", [], [El("TableHead", [], [Text(f)], html="th") for _, f in cols], html="tr")
        cells = []
        for sid, f in cols:
            if sid == "name":
                cells.append(El("TableCell", [("data-pattern-slot", "name"), ("data-pattern-field", f), ("class", "font-semibold")],
                                [El("a", [("href", Expr("href(item)", "#"))], [Field(f)])], html="td"))
            elif sid == "status":
                cells.append(El("TableCell", [], [badge(f, "status")], html="td"))
            else:
                cells.append(El("TableCell", [("data-pattern-slot", "property"), ("data-pattern-field", f)], [Field(f)], html="td"))
        body = El("TableBody", [], [Loop(El("TableRow", [], cells, html="tr"))], html="tbody")
        return El("section", [("data-pattern", pid), ("class", "space-y-4")], [
            El("h2", [("data-pattern-slot", "heading"), ("class", "text-xl font-semibold")], [Text(obj)]),
            Note("optional slots, in this order: actions (3 at most), filter, count"),
            El("Table", [], [El("TableHeader", [], [head], html="thead"), body], html="table"),
            Note("align number columns to the end with tabular-nums; optional slots: row-action (3 at most), pagination (past 50 rows)"),
        ]), True
    if pid == "record.header":
        keys = fields_of(rows, "key-fields")
        title = El("div", [("class", "flex flex-wrap items-center gap-3")],
                   [slot("title", one("title"), "h1", "text-2xl font-semibold")] +
                   ([badge(one("status"), "status")] if one("status") else []))
        kids = [Note("optional slot back: a link whose text is the title of the page it returns to"), title]
        if keys:
            kids.append(El("dl", [("class", "flex flex-wrap gap-x-8 gap-y-2")], [
                El("div", [], [El("dt", [("class", "text-sm text-muted-foreground")], [Text(k)]),
                               slot("key-fields", k, "dd")]) for k in keys]))
        kids.append(Note("optional slots: primary-action (one, verb + noun), secondary-actions, pagination"))
        return El("header", [("data-pattern", pid), ("class", "space-y-3")], kids), False
    if pid == "record.body.two-column":
        return El("div", [("data-pattern", pid), ("class", "grid gap-8 lg:grid-cols-3")], [
            El("div", [("data-pattern-slot", "primary"), ("class", "space-y-8 lg:col-span-2")],
               [Note("the sections that define the object, most important first")]),
            El("aside", [("data-pattern-slot", "secondary"), ("class", "space-y-8")],
               [Note("optional: status, metadata, summaries")]),
        ]), False
    if pid == "record.summary-list":
        return El("dl", [("data-pattern", pid), ("class", "divide-y divide-border")], [
            El("div", [("class", "grid grid-cols-3 gap-4 py-3")], [
                El("dt", [("data-pattern-slot", "key"), ("class", "text-muted-foreground")], [Text(f)]),
                slot("value", f, "dd", "col-span-2")]) for f in fields_of(rows, "value")]), False
    if pid == "task.list":
        item = El("li", [("data-pattern", pid), ("class", "flex items-baseline justify-between gap-4 py-3")], [
            El("a", [("data-pattern-slot", "task"), ("data-pattern-field", one("task")), ("href", Expr("href(item)", "#"))],
               [Field(one("task"))]),
            Note("optional slot hint: one sentence, only with evidence"),
            badge(one("status"), "status")])
        return El("ol", [("class", "divide-y divide-border")], [Loop(item)]), True
    if pid == "browse.card":
        head = [slot("title", one("title"), "CardTitle", html="h3")]
        if one("label"):
            head.append(badge(one("label"), "label"))
        kids = []
        if one("image"):
            kids.append(slot("image", one("image"), "div", "aspect-video bg-muted", children=[]))
        kids += [El("CardHeader", [], head, html="header"),
                 El("CardContent", [], [El("dl", [("class", "space-y-1")], [
                     El("div", [("class", "flex gap-2")], [El("dt", [("class", "text-muted-foreground")], [Text(f)]),
                                                         slot("content", f, "dd")]) for f in fields_of(rows, "content")])], html="div"),
                 Note("optional slot sub: links or up to two function buttons; none when the whole card is a link")]
        return El("div", [("class", "grid gap-6 sm:grid-cols-2 lg:grid-cols-3")],
                  [Loop(El("Card", [("data-pattern", pid)], kids, html="article"))]), True
    if pid == "commerce.product-item":
        kids = [slot("image", one("image"), "div", "aspect-square rounded-md bg-muted", children=[]),
                El("h3", [("class", "font-semibold")], [
                    El("a", [("data-pattern-slot", "title"), ("data-pattern-field", one("title")), ("href", Expr("href(item)", "#"))],
                       [Field(one("title"))])]),
                slot("price", one("price"), "p", "text-lg font-semibold tabular-nums")]
        kids.append(El("p", [("class", "flex gap-2 text-sm")], [slot("rating", f) for f in fields_of(rows, "rating")]))
        if one("variations"):
            kids.append(slot("variations", one("variations"), "p", "text-sm text-muted-foreground"))
        kids += [slot("attributes", f, "p", "text-sm") for f in fields_of(rows, "attributes")]
        return El("div", [("class", "grid gap-6 sm:grid-cols-2 lg:grid-cols-4")],
                  [Loop(El("article", [("data-pattern", pid), ("class", "space-y-2")], kids))]), True
    if pid == "measure.tile.kpi":
        return El("div", [("data-pattern", pid), ("class", "space-y-1")], [
            El("p", [("data-pattern-slot", "label"), ("class", "text-sm text-muted-foreground")], [Note("the quantity, in the reader's words")]),
            El("p", [("data-pattern-slot", "value"), ("class", "text-3xl font-semibold tabular-nums")], [Note("the value")]),
            El("p", [("data-pattern-slot", "comparison"), ("class", "text-sm")], [Note("one comparison: a target, the previous period or a rank")]),
            Note("optional slot link: opens the records the figure counts"),
        ]), False
    if pid == "state.empty":
        return empty_state(obj or "{object}"), False
    if pid == "status.badge":
        return badge(one("label") or "{status}", "label"), False
    raise ValueError(f"no skeleton for {pid}")


def attr_jsx(name, value):
    if name == "class":
        name = "className"
    if isinstance(value, Expr):
        return f"{name}={{{value.jsx}}}"
    return f'{name}="{value}"'


def attr_html(name, value):
    return f'{name}="{value.html if isinstance(value, Expr) else value}"'


def emit(node, stack, depth, uses, key=False):
    pad = "  " * depth
    if isinstance(node, Text):
        return [pad + node.text]
    if isinstance(node, Field):
        return [pad + (f'{{String(item["{node.label}"] ?? "")}}' if stack == "shadcn" else f"{{{{{node.label}}}}}")]
    if isinstance(node, Note):
        return [pad + (f"{{/* {node.text} */}}" if stack == "shadcn" else f"<!-- {node.text} -->")]
    if isinstance(node, Loop):
        if stack == "shadcn":
            return [pad + "{items.map((item, i) => ("] + emit(node.child, stack, depth + 1, uses, key=True) + [pad + "))}"]
        return [pad + "<!-- one per item -->"] + emit(node.child, stack, depth, uses)
    tag = node.tag if stack == "shadcn" else node.html
    if stack == "shadcn" and tag in UI_IMPORT:
        uses.add(tag)
    attrs = [("key", Expr("i", "")) ] if key else []
    attrs += node.attrs
    rendered = " ".join((attr_jsx if stack == "shadcn" else attr_html)(n, v) for n, v in attrs
                        if not (stack == "html" and n in ("key", "variant")))
    open_tag = f"<{tag}{' ' + rendered if rendered else ''}>"
    inline = [c for c in node.children if isinstance(c, (Text, Field))]
    if not node.children:
        return [pad + open_tag + f"</{tag}>"]
    if len(node.children) == 1 and inline:
        return [pad + open_tag + emit(node.children[0], stack, 0, uses)[0] + f"</{tag}>"]
    out = [pad + open_tag]
    for child in node.children:
        out += emit(child, stack, depth + 1, uses)
    return out + [pad + f"</{tag}>"]


def component_name(n, pid):
    return f"S{n}" + "".join(part.capitalize() for part in re.split(r"[.-]", pid))


def render_shadcn(n, result, pattern, root, needs_items):
    uses = set()
    body = emit(root, "shadcn", 2, uses)
    name = component_name(n, pattern["id"])
    head = [f"// product-ui scaffold: {pattern['id']} for section {result['section']} ({result['screen']}).",
            f"// Slots, their order and their limits: patterns/{pattern['id']}.json and the Slots table in ui-brief.md.",
            "// Replace each item[\"…\"] with the record's own key, fill the notes, and keep every data-pattern attribute."]
    imports = {}
    for comp in sorted(uses):
        imports.setdefault(UI_IMPORT[comp], []).append(comp)
    head += [f'import {{ {", ".join(names)} }} from "@/components/ui/{mod}"' for mod, names in sorted(imports.items())]
    head += ["", "type Item = Record<string, unknown>", ""]
    if needs_items:
        sig = f"export function {name}({{ items, href }}: {{ items: Item[]; href: (item: Item) => string }}) {{"
        empty = ["  if (items.length === 0) {", "    return ("] + emit(empty_state(result["object"]), "shadcn", 3, uses) + ["    )", "  }"]
        imports_used = []
    else:
        sig = f"export function {name}({{ item }}: {{ item: Item }}) {{" if any(
            isinstance(c, Field) for c in walk(root)) else f"export function {name}() {{"
        empty = []
        imports_used = []
    del imports_used
    return "\n".join(head + [sig] + empty + ["  return ("] + body + ["  )", "}", ""])


def walk(node):
    yield node
    for child in getattr(node, "children", []) or ([node.child] if isinstance(node, Loop) else []):
        yield from walk(child)


def render_html(result, pattern, root, needs_items):
    lines = [f"<!-- product-ui scaffold: {pattern['id']} for section {result['section']} ({result['screen']}).",
             f"     Slots, their order and their limits: patterns/{pattern['id']}.json and the Slots table in ui-brief.md.",
             "     Replace each {{label}} with the record's value, fill the notes, and keep every data-pattern attribute. -->"]
    if needs_items:
        lines += ["<!-- when the collection is empty, in place of the list: -->"] + emit(empty_state(result["object"]), "html", 0, set())
    return "\n".join(lines + emit(root, "html", 0, set()) + [""])


def render_note(stack, result, pattern):
    comp = (pattern.get("maps_to") or {}).get(stack)
    lines = [f"# {result['section']} ({result['screen']}): {pattern['id']}", "",
             f"Component: {comp or 'none in the preset; build it from the preset primitives'}.",
             f"Put `data-pattern=\"{pattern['id']}\"` on "
             + ("each item." if pattern["kind"] in library.ITEM_KINDS else "the block."), "",
             "| Slot | Shows | Attributes |", "|---|---|---|"]
    for sid, shows, _ in result["slots"]:
        field = f' data-pattern-field="{shows}"' if not shows.startswith("(") and not shows.startswith("the label") else ""
        lines.append(f'| {sid} | {shows} | `data-pattern-slot="{sid}"{field}` |')
    return "\n".join(lines + [""])


def stack_from_tokens(brief):
    path = os.path.join(os.path.dirname(os.path.abspath(brief)), "tokens.json")
    try:
        with open(path, encoding="utf-8") as handle:
            tokens = json.load(handle)
    except (OSError, ValueError):
        return "shadcn"
    stack, meta = tokens.get("stack") or {}, tokens.get("meta") or {}
    if stack.get("base") == "smarthr-ui":
        return "smarthr"
    if meta.get("reference") == "digital-agency-design-system":
        return "dads"
    if stack.get("renderer") in ("html", "server-templates"):
        return "html"
    return "shadcn"


def main():
    parser = argparse.ArgumentParser(description="Write the skeleton of each resolved section of ui-brief.md.")
    parser.add_argument("brief", help="path to ui-brief.md")
    parser.add_argument("--stack", choices=library.STACKS)
    parser.add_argument("--out")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    try:
        with open(args.brief, encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError:
        print(f"FAIL: no such file: {args.brief}", file=sys.stderr)
        return 1
    patterns = library.load_library()
    try:
        new_lines, results = resolve.resolve(text.split("\n"), library.load_index(), patterns)
    except resolve.Stop as exc:
        print(f"FAIL: {exc}")
        return 1
    if "\n".join(new_lines) != text:
        print("FAIL: the brief is out of date; run resolve.py first")
        return 1
    stack = args.stack or stack_from_tokens(args.brief)
    out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.brief)), "scaffold")
    os.makedirs(out_dir, exist_ok=True)
    ext = {"shadcn": ".tsx", "html": ".html"}.get(stack, ".md")
    written = []
    n = 0
    for result in results:
        if not result["pattern"]:
            continue
        n += 1
        pattern = patterns[result["pattern"]]
        if stack in ("shadcn", "html"):
            root, needs_items = build(pattern, result["slots"], result["object"])
            body = (render_shadcn(n, result, pattern, root, needs_items) if stack == "shadcn"
                    else render_html(result, pattern, root, needs_items))
        else:
            body = render_note(stack, result, pattern)
        path = os.path.join(out_dir, f"{n:02d}-{pattern['id'].replace('.', '-')}{ext}")
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
        written.append({"section": result["section"], "screen": result["screen"], "pattern": pattern["id"], "file": path})
    if args.json:
        print(json.dumps({"status": "PASS", "stack": stack, "files": written}, ensure_ascii=False, indent=2))
    else:
        for w in written:
            print(f"{w['screen']} / {w['section']}: {w['pattern']} -> {w['file']}")
        print(f"PASS: {len(written)} file(s), stack {stack}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
