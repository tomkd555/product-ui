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

The skeletons of the six patterns from business packages (entry.slip, master.form,
collection.conditions, action.function-keys, feedback.confirm, feedback.message) also carry the
conventions of the brief's Conventions section, read from the tokens.json beside the brief: the
keys, the words, the required mark, the confirmation sentence and the form and time of a message,
with the attributes references/profiles.md lists (data-enter, data-key, data-action, data-confirm,
data-message, data-guard). On `shadcn` they are written on the parts of the kit (scripts/kit.py).

Stacks: `shadcn` writes React (TSX) on the shadcn/ui components; `html` writes static HTML
with {{label}} placeholders; `dads`, `smarthr` and `astryx` write a Markdown note naming the
preset's component and the attributes each slot takes. Without --stack the stack comes from
tokens.json beside the brief: `stack.base` smarthr-ui gives smarthr, `stack.base` astryx gives
astryx, `meta.reference` digital-agency-design-system gives dads, `stack.renderer` html or
server-templates gives html, and anything else gives shadcn.

CLI:
    python scaffold.py <ui-brief.md> [--stack shadcn|html|dads|smarthr|astryx] [--out DIR] [--json]

--out defaults to `scaffold/` beside the brief. The same brief writes the same bytes.

Exit codes: 0 = written, 1 = the brief is out of date or a section cannot be resolved.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import conventions  # noqa: E402
import kit  # noqa: E402
import library  # noqa: E402
import resolve  # noqa: E402

command_set = resolve.command_set

UI_IMPORT = {"Table": "table", "TableHeader": "table", "TableBody": "table", "TableRow": "table",
             "TableHead": "table", "TableCell": "table", "Badge": "badge",
             "Card": "card", "CardHeader": "card", "CardTitle": "card", "CardContent": "card", "Button": "button"}


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


class Cond:
    """`empty` when the collection holds no item, `filled` otherwise; the parts around it stay in both cases."""
    def __init__(self, empty, filled):
        self.empty, self.filled = empty, filled


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
        Note(f"after a search or filter that matched nothing: 該当する{obj}はありません。 with the search and the filters kept above it, and no create button"),
        Note("optional slot action: the action that adds the first one, first use only"),
    ])


def build(pattern, rows, obj, section=None):
    """The skeleton tree for one section: (root, needs_items). `section` is the section's name in the brief."""
    pid = pattern["id"]
    one = lambda s: (fields_of(rows, s) or [None])[0]  # noqa: E731
    labels = pattern.get("labels") or {}
    if pid == "process.closing":
        cols = [("name", one("name"))] + ([("status", one("status"))] if one("status") else []) + \
               [("property", f) for f in fields_of(rows, "property")]
        head = El("TableRow", [], [El("TableHead", [], [Text(f)], html="th") for _, f in cols], html="tr")
        cells = []
        for sid, f in cols:
            if sid == "name":
                cells.append(El("TableCell", [("data-pattern-slot", "name"), ("data-pattern-field", f), ("class", "font-semibold")],
                                [Field(f)], html="td"))
            elif sid == "status":
                cells.append(El("TableCell", [], [badge(f, "status")], html="td"))
            else:
                cells.append(El("TableCell", [("data-pattern-slot", "property"), ("data-pattern-field", f)], [Field(f)], html="td"))
        body = El("TableBody", [], [Loop(El("TableRow", [], cells, html="tr"))], html="tbody")
        return El("section", [("data-pattern", pid), ("class", "space-y-4")], [
            Note("where the closing is the whole page, the heading below is the page title: make it the h1 and keep the attribute"),
            El("h2", [("data-pattern-slot", "heading"), ("class", "text-xl font-semibold")], [Text(section or obj)]),
            El("div", [("data-pattern-slot", "period"), ("class", "flex flex-wrap items-end gap-4")],
               [Note("the period or the closing date this run closes, as a labelled control")]),
            Note("optional slot blocker: what stands in the way of the closing, with its count and a link to the list of those records"),
            Cond(empty_state(obj), El("Table", [], [El("TableHeader", [], [head], html="thead"), body], html="table")),
            Note("align number columns to the end with tabular-nums; a closed target shows its state as a status word"),
            El("div", [("class", "flex flex-wrap gap-2")], [
                El("Button", [("data-pattern-slot", "run"), ("type", "button")],
                   [Note("the closing's own word (締切, 仮締め); it opens the confirmation (feedback.confirm), whose message states "
                         "what the closing covers and whether it can be released")], html="button"),
                Note("optional slot release: the release of a closing (締切の取消, 仮締め解除), on a closed period, for the roles that may run it")]),
        ]), True
    if pid == "process.import":
        mapped = [("key", one("key"))] + [("mapping", f) for f in fields_of(rows, "mapping")]
        head = El("TableRow", [], [El("TableHead", [], [Text(labels["file_column"])], html="th"),
                                   El("TableHead", [], [Text(labels["field"].replace("{object}", obj))], html="th")], html="tr")
        pairs = [El("TableRow", [], [
            El("TableCell", [], [Note("the column of the file that fills this field; one that matches the field by name is chosen for the reader")], html="td"),
            El("TableCell", [("data-pattern-slot", sid), ("data-pattern-field", f)], [Text(f)], html="td")], html="tr") for sid, f in mapped]
        return El("form", [("data-pattern", pid), ("class", "space-y-6")], [
            Note("where the import is the whole page, the heading below is the page title: make it the h1 and keep the attribute"),
            El("h2", [("data-pattern-slot", "heading"), ("class", "text-xl font-semibold")], [Text(section or obj)]),
            Note("optional slot step: the steps of the import as an indicator, where they span screens"),
            El("div", [("data-pattern-slot", "file")], [Note("the file input under its label, with the formats it takes")]),
            Note("optional slot setting: whether the first row names the columns, the row where the data starts, the character code, the delimiter"),
            Note("optional slot preview: the first rows of the file as they will be read"),
            El("Table", [], [El("TableHeader", [], [head], html="thead"), El("TableBody", [], pairs, html="tbody")], html="table"),
            Note("the first field above is the key: a row whose key is already stored is the record the next control decides about"),
            El("div", [("data-pattern-slot", "existing")],
               [Note("what happens to a record whose key is already stored: left as it is, or updated; as a labelled choice")]),
            Note("optional slot on-error: whether a row in error is skipped or stops the import"),
            El("Button", [("data-pattern-slot", "run"), ("type", "submit")], [Note("the importing word (インポート, 読み込む)")], html="button"),
            Note("optional slots after the run: result (the rows read, added, updated and in error), error (per row in error: its number, the field and the reason)"),
        ]), False
    if pid == "approval.request":
        return El("section", [("data-pattern", pid), ("class", "space-y-4")], [
            Note("optional slot heading: %s, as an h2 where the page holds other sections" % labels["heading"]),
            El("ol", [("data-pattern-slot", "route"), ("class", "space-y-2")],
               [Note("the steps of the route in order: who handles each, its state and when it was handled; the current step is marked")]),
            El("div", [("data-pattern-slot", "comment")], [Note("a labelled textarea for the approver's comment")]),
            El("div", [("class", "flex flex-wrap gap-2")], [
                El("Button", [("data-pattern-slot", "approve"), ("type", "button")], [Text(labels["approve"])], html="button"),
                El("Button", [("data-pattern-slot", "reject"), ("type", "button"), ("variant", "outline")], [Text(labels["reject"])], html="button"),
                Note("optional slot send-back: %s, with the step it returns to where the route allows a choice" % labels["send_back"]),
                Note("optional slot other: 保留 and 委任 where the product has them, two at most")]),
            Note("optional slot withdraw: %s, on the applicant's view while the next approver has not handled the request" % labels["withdraw"]),
            Note("the words follow the product (否認, 差戻し, 引戻し, 回収): one word each, settled in voice.terms"),
        ]), False
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
            Note("where this collection is the whole page, the heading below is the page title: make it the h1 and keep the attribute"),
            El("h2", [("data-pattern-slot", "heading"), ("class", "text-xl font-semibold")], [Text(obj)]),
            Note("optional slots, in this order: actions (3 at most), filter, count"),
            Cond(empty_state(obj), El("Table", [], [El("TableHeader", [], [head], html="thead"), body], html="table")),
            Note("align number columns to the end with tabular-nums; optional slots: row-action (3 at most), pagination (past 50 rows)"),
            Note("the name is a link where the build holds the record's single view, and plain text for a sub object or a view outside the build"),
        ]), True
    if pid == "record.header":
        keys = fields_of(rows, "key-fields")
        title = El("div", [("class", "flex flex-wrap items-center gap-3")],
                   [slot("title", one("title"), "h1", "text-2xl font-semibold")] +
                   ([badge(one("status"), "status")] if one("status") else []))
        kids = [Note("optional slot back: a link whose text is the title of the page it returns to"), title]
        if fields_of(rows, "rating"):
            kids.append(El("p", [("class", "flex gap-2 text-sm")], [slot("rating", f) for f in fields_of(rows, "rating")]))
        if one("price"):
            kids.append(slot("price", one("price"), "p", "text-2xl font-bold tabular-nums"))
        kids += [slot("offer", f, "p", "text-sm") for f in fields_of(rows, "offer")]
        if keys:
            kids.append(El("dl", [("class", "flex flex-wrap gap-x-8 gap-y-2")], [
                El("div", [], [El("dt", [("class", "text-sm text-muted-foreground")], [Text(k)]),
                               slot("key-fields", k, "dd")]) for k in keys]))
        kids.append(Note("optional slots: primary-action (one, verb + noun) and secondary-actions, in the title's row on a "
                         "work tool's record and under the price on a product page; pagination"))
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
            El("div", [("class", "flex gap-4 py-3")], [
                El("dt", [("data-pattern-slot", "key"), ("class", "w-32 shrink-0 text-muted-foreground")], [Text(f)]),
                slot("value", f, "dd", "min-w-0 flex-1")]) for f in fields_of(rows, "value")]), False
    if pid == "record.activity":
        entry = El("li", [("class", "space-y-1 py-3")], [
            El("p", [("class", "flex flex-wrap gap-x-3 text-sm text-muted-foreground")], [
                El("a", [("data-pattern-slot", "actor"), ("href", Expr("href(item)", "#"))],
                   [Note("who acted; a span where the build holds no view of the person")]),
                El("time", [("data-pattern-slot", "time")],
                   [Note("when: a relative phrase with the full time in title, or a date and time")])]),
            El("p", [("data-pattern-slot", "event")], [Note("what happened; a change names the property and both values")]),
            Note("optional slot body: the text of a comment")])
        return El("section", [("data-pattern", pid), ("class", "space-y-3")], [
            Note("optional slot heading: 履歴 or the object's own word, as an h2 where the page holds other sections"),
            El("ol", [("class", "divide-y divide-border")], [Loop(entry)])]), True
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
        if one("price"):
            head.append(slot("price", one("price"), "p", "text-3xl font-semibold tabular-nums"))
        kids += [El("CardHeader", [], head, html="header"),
                 El("CardContent", [], [El("dl", [("class", "space-y-1")], [
                     El("div", [("class", "flex gap-2")], [El("dt", [("class", "text-muted-foreground")], [Text(f)]),
                                                         slot("content", f, "dd")]) for f in fields_of(rows, "content")])], html="div"),
                 Note("optional slot sub: links or up to two function buttons; none when the whole card is a link")]
        return El("div", [("class", "grid gap-6 sm:grid-cols-2 lg:grid-cols-3")],
                  [Loop(El("Card", [("data-pattern", pid)], kids, html="article"))]), True
    if pid == "commerce.product-item":
        kids = [slot("image", one("image"), "div", "aspect-square rounded-md bg-muted", children=[]),
                El("h3", [("class", "line-clamp-2")], [
                    El("a", [("data-pattern-slot", "title"), ("data-pattern-field", one("title")), ("href", Expr("href(item)", "#"))],
                       [Field(one("title"))])]),
                slot("price", one("price"), "p", "text-xl font-bold tabular-nums")]
        kids += [slot("offer", f, "p", "text-sm") for f in fields_of(rows, "offer")]
        kids.append(El("p", [("class", "flex gap-2 text-sm")], [slot("rating", f) for f in fields_of(rows, "rating")]))
        if one("variations"):
            kids.append(slot("variations", one("variations"), "p", "text-sm text-muted-foreground"))
        kids += [slot("attributes", f, "p", "text-sm") for f in fields_of(rows, "attributes")]
        if one("status"):
            kids.append(badge(one("status"), "status"))
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


CONVENTION_PATTERNS = ("entry.slip", "master.form", "collection.conditions", "action.function-keys",
                       "feedback.confirm", "feedback.message")
KIT = {"FormField": "@/components/form-field", "LineGrid": "@/components/line-grid",
       "FunctionKey": "@/components/function-keys", "FunctionKeys": "@/components/function-keys",
       "ConfirmDialog": "@/components/confirm-dialog", "Messages": "@/components/message-bar",
       "useMessages": "@/components/message-bar", "Input": "@/components/ui/input", "Button": "@/components/ui/button",
       "TableCell": "@/components/ui/table", "useEnterKeys": "@/lib/keys", "useKeyButtons": "@/lib/keys",
       "useSubmitGuard": "@/lib/submit-guard", "useRef": "react", "ReactNode": "react",
       "ShellApi": "@/components/document-shell"}
TYPE_ONLY = ("ReactNode", "ShellApi")
RESULT_PHRASE = {"toast": "a toast", "bar": "a bar at the top of the content", "near-control": "a line beside the control",
                 "status-bar": "the window's status bar, through the shell's notify",
                 "new-entry": "no message: the form empties and the focus returns to its first field"}


def js(text):
    """A string as a JavaScript literal."""
    return json.dumps(text, ensure_ascii=False)


def word_of(values, operation, fallback):
    """The word the conventions give an operation; the fallback where the project settles it in voice.terms."""
    word = values.get(f"words.{operation}")
    return fallback if word in (None, conventions.VOICE_TERMS) else word


def screen_title(result):
    """The screen's name in the brief, which heads an entry screen: its heading up to the route."""
    return result["screen"].split(" `")[0].strip() or result["object"]


def number_lines(stack, pad, number):
    """The number of a slip, which the system assigns: shown as text beside the fields the reader enters."""
    if stack == "shadcn":
        return [f'{pad}<div data-pattern-slot="number" data-pattern-field="{number}" className="space-y-1">',
                f'{pad}  <p className="text-sm font-bold">{number}</p>',
                f'{pad}  <p className="tabular-nums">{{String(item[{js(number)}] ?? "")}}</p>', f"{pad}</div>",
                f"{pad}{{/* the system assigns the number; where the reader types it, make it a field of the header */}}"]
    return [f'{pad}<div data-pattern-slot="number" data-pattern-field="{number}" class="space-y-1">',
            f'{pad}  <p class="text-sm font-bold">{number}</p>', f'{pad}  <p class="tabular-nums">{{{{{number}}}}}</p>', f"{pad}</div>",
            f"{pad}<!-- the system assigns the number; where the reader types it, make it a field of the header -->"]


def register_words(values):
    """(the word of a registration on a new record, the word on an existing one); the two are equal in most families."""
    save = word_of(values, "save", "保存")
    return word_of(values, "create", save), save


def shortcut(values, action):
    """The shortcut of the conventions that runs an action, as {"keys", "label"}, or None."""
    return next((k for k in values.get("keys.shortcuts") or [] if k["action"] == action), None)


def head_lines(result, pattern, stack):
    lines = [f"product-ui scaffold: {pattern['id']} for section {result['section']} ({result['screen']}).",
             f"Slots, their order and their limits: patterns/{pattern['id']}.json and the Slots table in ui-brief.md.",
             "The keys, the words, the required mark and the messages: the Conventions section of ui-brief.md.",
             "Bind the values, fill the notes, and keep every data- attribute."]
    if stack == "shadcn":
        return ["// " + line for line in lines]
    return ["<!-- " + lines[0]] + ["     " + line for line in lines[1:-1]] + ["     " + lines[-1] + " -->"]


def import_lines(names):
    """The import statements of a TSX skeleton for the kit parts and components it names."""
    modules = {}
    for name in names:
        modules.setdefault(KIT[name], []).append(name)
    out = []
    for module in sorted(modules, key=lambda m: (m != "react", m)):
        listed = ", ".join(("type " + n) if n in TYPE_ONLY else n for n in sorted(modules[module], key=str.lower))
        out.append(f'import {{ {listed} }} from "{module}"')
    return out


def field_jsx(pad, slot_name, label, required, mark, source="item", change="onField", field=True, errors=True):
    """One labelled field on the kit's FormField."""
    attrs = [f'data-pattern-slot="{slot_name}"'] + ([f'data-pattern-field="{label}"'] if field else []) + [f"label={js(label)}"]
    if required:
        attrs += ["required", f'requiredMark="{mark}"']
    if errors:
        attrs.append(f"error={{errors[{js(label)}]}}")
    return [f"{pad}<FormField {' '.join(attrs)}>",
            f"{pad}  {{(control) => <Input {{...control}} name={js(label)} value={{String({source}[{js(label)}] ?? \"\")}} "
            f"onChange={{(event) => {change}({js(label)}, event.target.value)}} />}}",
            f"{pad}</FormField>"]


def mark_html(mark):
    if mark == "asterisk":
        return ' <span data-required-mark="asterisk" class="text-destructive"><span aria-hidden="true">*</span><span class="sr-only">必須</span></span>'
    return ' <span data-required-mark="text" class="text-destructive">必須</span>'


def field_html(pad, slot_name, label, required, mark, field=True):
    attr = f' data-pattern-field="{label}"' if field else ""
    return [f'{pad}<div data-pattern-slot="{slot_name}"{attr} class="space-y-1.5">',
            f'{pad}  <label for="f-{label}" class="flex items-center gap-2 text-sm font-medium">{label}{mark_html(mark) if required else ""}</label>',
            f'{pad}  <input id="f-{label}" name="{label}" value="{{{{{label}}}}}"{" required" if required else ""}>',
            f"{pad}</div>"]


def entry_hooks(values, name):
    """(imports, hook lines, form attributes, closing notes) that carry keys.enter and keys.enter_last into an entry form."""
    enter, last = values["keys.enter"], values["keys.enter_last"]
    if enter == "next-field":
        return (["useRef", "useEnterKeys", "useKeyButtons"],
                ["  const form = useRef<HTMLFormElement>(null)",
                 f'  useEnterKeys(form, {{ enter: "{enter}", enterLast: "{last}" }}, onRegister)',
                 "  useKeyButtons()"],
                'ref={form} data-pattern="%s" data-enter="next-field" noValidate' % name,
                "onSubmit={(event) => event.preventDefault()}")
    return (["useKeyButtons"], ["  useKeyButtons()"], 'data-pattern="%s" noValidate' % name,
            "onSubmit={(event) => {\n        event.preventDefault()\n        onRegister()\n      }}")


def foot_actions(values, stack, pad):
    """The registration button of an entry form whose conventions show no function keys; the function-key row holds it otherwise."""
    if values["keys.display"] != "none":
        return [pad + ("{/* the registration runs by its function key and by its button in the row (action.function-keys) */}"
                       if stack == "shadcn" else "<!-- the registration runs by its function key and by its button in the row (action.function-keys) -->")], []
    create, word = register_words(values)
    block = values["waiting.block"]
    key = shortcut(values, "register")
    marks = 'type="submit" data-action="register"' + (f' data-key="{key["keys"]}"' if key else "")
    if stack == "shadcn":
        attrs = marks + (' data-guard="button"' if block == "button" else "") + (" disabled={register.busy}" if block != "none" else "")
        label = word if create == word else f"{{mode === \"create\" ? {js(create)} : {js(word)}}}"
        out = [f'{pad}<div className="flex gap-2">', f"{pad}  <Button {attrs}>{label}</Button>", f"{pad}</div>"]
        if block == "screen":
            out.append(f'{pad}{{register.busy && <div data-guard="screen" aria-busy="true" className="fixed inset-0 z-50 bg-background/60" />}}')
        return out, ["Button"]
    attrs = marks + (' data-guard="button"' if block == "button" else "")
    out = [f'{pad}<div class="flex gap-2">', f"{pad}  <button {attrs}>{create}</button>", f"{pad}</div>"]
    if create != word:
        out.insert(1, f"{pad}  <!-- {create} on a new record, {word} on an existing one -->")
    if block == "screen":
        out.append(f'{pad}<!-- while the registration runs: <div data-guard="screen" aria-busy="true" class="fixed inset-0 z-50 bg-background/60"></div> -->')
    return out, []


def error_summary(values, stack, pad):
    """The summary above an entry form whose conventions show an input error at the top as well as beside its field."""
    if values["messages.error"] != "top-and-field":
        return []
    if stack == "shadcn":
        return [f"{pad}{{Object.values(errors).some(Boolean) && (",
                f'{pad}  <p role="alert" data-message="error" tabIndex={{-1}} className="rounded-md border border-destructive px-4 py-3 text-sm text-destructive">',
                f"{pad}    入力内容を確認してください。", f"{pad}  </p>", f"{pad})}}",
                f"{pad}{{/* on a registration with errors, move the focus to this summary; each error also shows beside its field */}}"]
    return [f"{pad}<!-- when the registration finds errors, above the fields and with the focus on it: -->",
            f'{pad}<p role="alert" data-message="error" tabindex="-1" class="rounded-md border border-destructive px-4 py-3 text-sm text-destructive">入力内容を確認してください。</p>']


def skeleton_slip(name, result, pattern, fields, values, stack):
    rows, obj = result["slots"], result["object"]
    one = lambda s: (fields_of(rows, s) or [None])[0]  # noqa: E731
    number, status, item = one("number"), one("status"), one("line-item")
    header, line_fields, totals = fields_of(rows, "header-field"), fields_of(rows, "line-field"), fields_of(rows, "total")
    auto, required, mark = set(resolve.names(fields.get("auto"))), set(resolve.names(fields.get("required"))), values["required_mark"]
    insert, remove, add = shortcut(values, "row-insert"), shortcut(values, "row-delete"), shortcut(values, "row-new")
    add_key = f' data-key="{add["keys"]}"' if add else ""
    if stack == "html":
        out = head_lines(result, pattern, stack)
        enter = ' data-enter="next-field"' if values["keys.enter"] == "next-field" else ""
        out += [f'<form data-pattern="{pattern["id"]}"{enter} novalidate class="space-y-6">',
                "  <!-- where this slip is the whole page, the heading below is the page title: make it the h1 and keep the attribute -->",
                f'  <h2 data-pattern-slot="heading" class="text-xl font-semibold">{screen_title(result)}</h2>']
        out += error_summary(values, stack, "  ") + ['  <div class="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">']
        out += number_lines(stack, "    ", number)
        if status:
            out += field_html("    ", "status", status, status in required, mark)
        for f in header:
            out += field_html("    ", "header-field", f, f in required, mark)
        out += ["  </div>",
                "  <!-- the control of each field follows its value: a date, a number aligned to the end, a select, a code with its lookup -->",
                '  <table class="w-full">', "    <thead>", "      <tr>"]
        end = ' class="text-right"'
        out += [f'        <th{end if f in auto else ""}>{f}{mark_html(mark) if f in required else ""}</th>' for f in [item] + line_fields]
        out += ['        <th><span class="sr-only">行の操作</span></th>', "      </tr>", "    </thead>", "    <tbody>", "      <!-- one per line -->", "      <tr>",
                f'        <td data-pattern-slot="line-item" data-pattern-field="{item}"><input aria-label="{item}" name="{item}" value="{{{{{item}}}}}"{" required" if item in required else ""}></td>']
        for f in line_fields:
            if f in auto:
                out.append(f'        <td data-pattern-slot="line-field" data-pattern-field="{f}" data-auto="true">{{{{{f}}}}}</td>')
            else:
                out.append(f'        <td data-pattern-slot="line-field" data-pattern-field="{f}"><input aria-label="{f}" name="{f}" value="{{{{{f}}}}}"{" required" if f in required else ""}></td>')
        out.append("        <td>")
        if insert:
            out.append(f'          <button type="button" data-pattern-slot="line-action" data-key="{insert["keys"]}">{insert["label"]}</button>')
        key = f' data-key="{remove["keys"]}"' if remove else ""
        out += [f'          <button type="button" data-pattern-slot="line-action"{key}>{remove["label"] if remove else pattern["labels"]["line_remove"]}</button>',
                "        </td>", "      </tr>", "    </tbody>", "  </table>",
                f'  <button type="button" data-pattern-slot="line-action"{add_key}>{add["label"] if add else pattern["labels"]["line_add"]}</button>',
                '  <dl class="ml-auto w-full max-w-xs space-y-1">']
        for n, t in enumerate(totals):
            weight = " font-semibold" if n == len(totals) - 1 else ""
            out += [f'    <div class="flex justify-between gap-4{weight}">', f'      <dt class="text-muted-foreground">{t}</dt>',
                    f'      <dd data-pattern-slot="total" class="tabular-nums">{{{{{t}}}}}</dd>', "    </div>"]
        out.append("  </dl>")
        out += foot_actions(values, stack, "  ")[0]
        out.append("</form>")
        if values["keys.enter"] == "next-field":
            out.append("<!-- Enter moves to the next field and Shift+Enter to the previous one; in the last field it "
                       + ("registers" if values["keys.enter_last"] == "register" else "stays")
                       + " (Conventions, keys.enter and keys.enter_last). On this stack the key handling is written by hand. -->")
        return "\n".join(out + [""])
    imports, hooks, form_attrs, submit = entry_hooks(values, pattern["id"])
    foot, foot_imports = foot_actions(values, stack, "      ")
    guard = values["keys.display"] == "none" and values["waiting.block"] != "none"
    if guard:
        hooks = ["  const register = useSubmitGuard(onRegister)"] + [h.replace(", onRegister)", ", register.run)") for h in hooks]
        submit = submit.replace("onRegister()", "void register.run()")
        imports = imports + ["useSubmitGuard"]
    out = head_lines(result, pattern, stack) + import_lines(["FormField", "LineGrid", "Input", "TableCell"] + imports + foot_imports)
    out += ["", "type Item = Record<string, unknown>", "type Errors = Record<string, string | undefined>", "",
            f"export function {name}({{", "  item,", "  lines,", "  totals,", "  errors = {},", "  onField,", "  onLines,", "  blankLine,", "  onRegister,",
            "}: {", "  item: Item", "  lines: Item[]", "  totals: Item", "  errors?: Errors",
            "  onField: (name: string, value: string) => void", "  onLines: (lines: Item[]) => void", "  blankLine: () => Item",
            "  onRegister: () => void" + (" | Promise<void>" if guard else ""), "}) {"] + hooks
    if values["keys.display"] == "none" and len(set(register_words(values))) == 2:
        out[out.index("  onRegister,")] = "  onRegister,\n  mode,"
        out[out.index("  errors?: Errors")] = '  errors?: Errors\n  mode: "create" | "edit"'
    out += ["  return (", f'    <form {form_attrs} className="space-y-6" {submit}>',
            "      {/* where this slip is the whole page, the heading below is the page title: make it the h1 and keep the attribute */}",
            f'      <h2 data-pattern-slot="heading" className="text-xl font-semibold">{screen_title(result)}</h2>']
    out += error_summary(values, stack, "      ") + ['      <div className="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">']
    out += number_lines(stack, "        ", number)
    if status:
        out += field_jsx("        ", "status", status, status in required, mark)
    for f in header:
        out += field_jsx("        ", "header-field", f, f in required, mark)
    out += ["      </div>",
            "      {/* the control of each field follows its value: a date, a number aligned to the end, a select, a code with its lookup */}",
            "      <LineGrid", "        lines={lines}", "        onChange={onLines}", "        blank={blankLine}", "        columns={["]
    for f in [item] + line_fields:
        flags = "" if f not in required else ", required: true"
        out.append(f"          {{ label: {js(f)}{flags} }},")
    out.append("        ]}")
    if insert:
        out.append(f"        insert={{{{ keys: {js(insert['keys'])}, label: {js(insert['label'])} }}}}")
    if remove:
        out.append(f"        remove={{{{ keys: {js(remove['keys'])}, label: {js(remove['label'])} }}}}")
    if add:
        out.append(f"        add={{{{ keys: {js(add['keys'])}, label: {js(add['label'])} }}}}")
    out += [f'        requiredMark="{mark}"', "      >", "        {(line, set) => (", "          <>",
            f'            <TableCell data-pattern-slot="line-item" data-pattern-field="{item}" className="py-0.5">',
            f"              <Input className=\"h-8\" aria-label={js(item)}{' required' if item in required else ''} value={{String(line[{js(item)}] ?? \"\")}} "
            f"onChange={{(event) => set({{ [{js(item)}]: event.target.value }})}} />",
            "            </TableCell>"]
    for f in line_fields:
        if f in auto:
            out += [f'            <TableCell data-pattern-slot="line-field" data-pattern-field="{f}" data-auto="true" className="py-0.5">',
                    f"              {{String(line[{js(f)}] ?? \"\")}}", "            </TableCell>"]
        else:
            out += [f'            <TableCell data-pattern-slot="line-field" data-pattern-field="{f}" className="py-0.5">',
                    f"              <Input className=\"h-8\" aria-label={js(f)}{' required' if f in required else ''} value={{String(line[{js(f)}] ?? \"\")}} "
                    f"onChange={{(event) => set({{ [{js(f)}]: event.target.value }})}} />",
                    "            </TableCell>"]
    out += ["          </>", "        )}", "      </LineGrid>",
            "      {/* a column of numbers takes numeric: true, and its cell or its input text-right tabular-nums */}",
            "      {/* before the registration, leave out the lines the reader left empty */}",
            '      <dl className="ml-auto w-full max-w-xs space-y-1">']
    for n, t in enumerate(totals):
        weight = " font-semibold" if n == len(totals) - 1 else ""
        out += [f'        <div className="flex justify-between gap-4{weight}">', f'          <dt className="text-muted-foreground">{t}</dt>',
                f'          <dd data-pattern-slot="total" className="tabular-nums">{{String(totals[{js(t)}] ?? "")}}</dd>', "        </div>"]
    out += ["      </dl>"] + foot + ["    </form>", "  )", "}", ""]
    return "\n".join(out)


def skeleton_master(name, result, pattern, fields, values, stack):
    rows, obj = result["slots"], result["object"]
    one = lambda s: (fields_of(rows, s) or [None])[0]  # noqa: E731
    ident, status, shown = one("name"), one("status"), fields_of(rows, "field")
    required, mark = set(resolve.names(fields.get("required"))), values["required_mark"]
    grouped = [(g, [p for p in props if p in shown]) for g, props in resolve.groups(fields.get("groups"))] or [(None, shown)]
    lead = [("name", ident)] + ([("status", status)] if status else [])
    html = stack == "html"
    cls = "class" if html else "className"
    body = []
    for n, (group, props) in enumerate(grouped):
        pad = " " * ((2 if html else 6) + (2 if group else 0))
        if group:
            body += [f'{pad[:-2]}<fieldset {cls}="space-y-4">',
                     f'{pad}<legend data-pattern-slot="group" {cls}="text-base font-semibold">{group}</legend>']
        body.append(f'{pad}<div {cls}="grid gap-x-6 gap-y-4 sm:grid-cols-2">')
        for slot_name, label in (lead if n == 0 else []) + [("field", p) for p in props]:
            body += (field_html(pad + "  ", slot_name, label, label in required, mark) if html
                     else field_jsx(pad + "  ", slot_name, label, label in required, mark))
        body.append(f"{pad}</div>")
        if group:
            body.append(f"{pad[:-2]}</fieldset>")
    note = "where this form is the whole page, the heading below is the page title: make it the h1 and keep the attribute"
    if html:
        enter = ' data-enter="next-field"' if values["keys.enter"] == "next-field" else ""
        out = head_lines(result, pattern, stack) + [
            f'<form data-pattern="{pattern["id"]}"{enter} novalidate class="space-y-8">', f"  <!-- {note} -->",
            f'  <h2 data-pattern-slot="heading" class="text-xl font-semibold">{screen_title(result)}</h2>'] + error_summary(values, stack, "  ") + body
        out += foot_actions(values, stack, "  ")[0] + ["</form>"]
        if values["keys.enter"] == "next-field":
            out.append("<!-- Enter moves to the next field and Shift+Enter to the previous one; in the last field it "
                       + ("registers" if values["keys.enter_last"] == "register" else "stays")
                       + " (Conventions, keys.enter and keys.enter_last). On this stack the key handling is written by hand. -->")
        return "\n".join(out + [""])
    imports, hooks, form_attrs, submit = entry_hooks(values, pattern["id"])
    foot, foot_imports = foot_actions(values, stack, "      ")
    guard = values["keys.display"] == "none" and values["waiting.block"] != "none"
    if guard:
        hooks = ["  const register = useSubmitGuard(onRegister)"] + [h.replace(", onRegister)", ", register.run)") for h in hooks]
        submit = submit.replace("onRegister()", "void register.run()")
        imports = imports + ["useSubmitGuard"]
    out = head_lines(result, pattern, stack) + import_lines(["FormField", "Input"] + imports + foot_imports)
    out += ["", "type Item = Record<string, unknown>", "type Errors = Record<string, string | undefined>", "",
            f"export function {name}({{", "  item,", "  errors = {},", "  onField,", "  onRegister,", "}: {", "  item: Item", "  errors?: Errors",
            "  onField: (name: string, value: string) => void", "  onRegister: () => void" + (" | Promise<void>" if guard else ""), "}) {"] + hooks
    if values["keys.display"] == "none" and len(set(register_words(values))) == 2:
        out[out.index("  onRegister,")] = "  onRegister,\n  mode,"
        out[out.index("  errors?: Errors")] = '  errors?: Errors\n  mode: "create" | "edit"'
    out += ["  return (", f'    <form {form_attrs} className="space-y-8" {submit}>', f"      {{/* {note} */}}",
            f'      <h2 data-pattern-slot="heading" className="text-xl font-semibold">{screen_title(result)}</h2>'] + error_summary(values, stack, "      ") + body
    out += ["      {/* the control of each field follows its value: a date, a number aligned to the end, a select, a code with its lookup */}"]
    out += foot + ["    </form>", "  )", "}", ""]
    return "\n".join(out)


def skeleton_conditions(name, result, pattern, fields, values, stack):
    listed = fields_of(result["slots"], "condition")
    search, clear = word_of(values, "search", pattern["labels"]["search"]), word_of(values, "clear", pattern["labels"]["clear"])
    key = shortcut(values, "search")
    key_attr = f' data-key="{key["keys"]}"' if key else ""
    if stack == "html":
        out = head_lines(result, pattern, stack) + [
            f'<form data-pattern="{pattern["id"]}" role="search" class="flex flex-wrap items-end gap-x-4 gap-y-3">']
        for c in listed:
            out += field_html("  ", "condition", c, False, "text", field=False)
        out += [f'  <button type="submit" data-pattern-slot="search" data-action="search"{key_attr}>{search}</button>',
                f'  <button type="button" data-pattern-slot="clear" data-action="clear">{clear}</button>', "</form>"]
        return "\n".join(out + [""])
    out = head_lines(result, pattern, stack) + import_lines(["FormField", "Input", "Button"])
    out += ["", f"export function {name}({{", "  values,", "  onChange,", "  onSearch,", "  onClear,", "}: {",
            "  values: Record<string, string>", "  onChange: (name: string, value: string) => void", "  onSearch: () => void",
            "  onClear: () => void", "}) {", "  return (", "    <form",
            f'      data-pattern="{pattern["id"]}"', '      role="search"', '      className="flex flex-wrap items-end gap-x-4 gap-y-3"',
            "      onSubmit={(event) => {", "        event.preventDefault()", "        onSearch()", "      }}", "    >"]
    for c in listed:
        out += field_jsx("      ", "condition", c, False, "text", source="values", change="onChange", field=False, errors=False)
    out += [f'      <Button type="submit" data-pattern-slot="search" data-action="search"{key_attr}>', f"        {search}", "      </Button>",
            '      <Button type="button" variant="outline" data-pattern-slot="clear" data-action="clear" onClick={onClear}>',
            f"        {clear}", "      </Button>", "    </form>", "  )", "}", ""]
    return "\n".join(out)


def skeleton_function_keys(name, result, pattern, fields, values, stack):
    listed = values.get("keys.function") or []
    block = values["waiting.block"]
    guard = block != "none"
    toolbar = values["keys.display"] == "toolbar"
    if stack == "html":
        cls = "flex flex-wrap gap-2 border-b border-border py-3" if toolbar else "sticky bottom-0 z-10 flex flex-wrap gap-2 border-t border-border bg-background py-3"
        out = head_lines(result, pattern, stack) + [f'<div data-pattern="{pattern["id"]}" role="toolbar" aria-label="ファンクションキー" class="{cls}">']
        for k in listed:
            extra = ' data-guard="button"' if block == "button" and k["action"] == "register" else ""
            out.append(f'  <button type="button" data-pattern-slot="key" data-key="{k["key"]}" data-action="{k["action"]}"{extra}>'
                       f'<kbd class="font-sans text-sm text-muted-foreground">{k["key"]}</kbd> {k["label"]}</button>')
        out += ["</div>", "<!-- each key runs its button, and the browser's own action for that key is stopped; on this stack the key handling is written by hand -->"]
        return "\n".join(out + [""])
    actions = []
    for k in listed:
        if k["action"] not in actions:
            actions.append(k["action"])
    guarded = guard and "register" in actions
    out = head_lines(result, pattern, stack) + import_lines(["FunctionKey", "FunctionKeys"] + (["useSubmitGuard"] if guarded else []))
    out += ["", f"export function {name}({{", "  on,", "}: {", "  on: {"]
    out += [f"    {a}: () => void" + (" | Promise<void>" if guarded and a == "register" else "") for a in actions]
    out += ["  }", "}) {"] + (["  const register = useSubmitGuard(on.register)"] if guarded else [])
    out += ["  return (", f'    <FunctionKeys data-pattern="{pattern["id"]}"' + (' className="static border-t-0 border-b"' if toolbar else "") + ">"]
    for k in listed:
        if guarded and k["action"] == "register":
            handler = (' data-guard="button"' if block == "button" else "") + " disabled={register.busy} onClick={() => void register.run()}"
        else:
            handler = f" onClick={{on.{k['action']}}}"
        out += [f'      <FunctionKey data-pattern-slot="key" keyName="{k["key"]}" data-action="{k["action"]}"{handler}>',
                f"        {k['label']}", "      </FunctionKey>"]
    if guarded and block == "screen":
        out.append('      {register.busy && <div data-guard="screen" aria-busy="true" className="fixed inset-0 z-50 bg-background/60" />}')
    out += ["    </FunctionKeys>", "  )", "}", ""]
    return "\n".join(out)


def skeleton_confirm(name, result, pattern, fields, values, stack):
    always = values["confirm.register"] == "always"
    sentence = values["confirm.sentence"] if values["confirm.sentence"] != "none" else None
    cancel = values["confirm.buttons"][1]
    (create, save), delete = register_words(values), word_of(values, "delete", "削除")
    said = lambda w: sentence.replace(conventions.OPERATION, w) if sentence else None  # noqa: E731
    agree = lambda w: values["confirm.buttons"][0].replace(conventions.OPERATION, w)  # noqa: E731
    if stack == "html":
        out = head_lines(result, pattern, stack)
        for operation, w in ([("register", create)] if always else []) + [("delete", delete)]:
            out += [f'<dialog data-pattern="{pattern["id"]}" data-confirm="{operation}">',
                    f'  <h2 data-pattern-slot="title">{{{{object}}}}の{w}</h2>']
            if said(w):
                out.append(f'  <p data-pattern-slot="message">{said(w)}</p>')
            if operation == "delete":
                out.append("  <!-- name the record that goes, and say that it cannot be restored -->")
            out += [f'  <button type="button" data-pattern-slot="cancel">{cancel}</button>',
                    f'  <button type="button" data-pattern-slot="confirm">{agree(w)}</button>', "</dialog>"]
        return "\n".join(out + [""])
    out = head_lines(result, pattern, stack) + import_lines(["ConfirmDialog", "ReactNode"])
    props = ["  open: boolean", "  onOpenChange: (open: boolean) => void"]
    if always:
        modes = create != save
        word = "${word}" if modes else save
        out += ["", "/** The step before a registration. `object` is the name of what is registered (受注伝票)"
                + (f"; `mode` gives the word: {create} on a new record, {save} on an existing one. */" if modes else ". */"),
                f"export function {name}Register({{", "  open,", "  onOpenChange,", "  object,"] + (["  mode,"] if modes else []) + [
                "  onConfirm,", "}: {"] + props + ["  object: string"] + (['  mode: "create" | "edit"'] if modes else []) + [
                "  onConfirm: () => void", "}) {"]
        out += [f'  const word = mode === "create" ? {js(create)} : {js(save)}'] if modes else []
        out += ["  return (", "    <ConfirmDialog", '      data-confirm="register"',
                "      open={open}", "      onOpenChange={onOpenChange}", f"      title={{`${{object}}の{word}`}}"]
        if said(save):
            out.append(f"      description={{`{said(word)}`}}" if modes else f"      description={js(said(save))}")
        label = agree(word)
        out += [f"      confirmLabel={{`{label}`}}" if modes and "${" in label else f"      confirmLabel={js(agree(save))}",
                f"      cancelLabel={js(cancel)}", "      onConfirm={onConfirm}", "    />", "  )", "}"]
    out += ["", "/**", " * The step before a deletion. `target` names the record that goes (受注伝票 SO-1042), and `consequence` says what the",
            " * reader loses: that the record cannot be restored, and what goes with it.", " */",
            f"export function {name}Delete({{", "  open,", "  onOpenChange,", "  target,", "  consequence,", "  onConfirm,", "}: {"] + props + [
            "  target: string", "  consequence: ReactNode", "  onConfirm: () => void", "}) {", "  return (", "    <ConfirmDialog",
            '      data-confirm="delete"', "      open={open}", "      onOpenChange={onOpenChange}", f"      title={{`${{target}}の{delete}`}}"]
    if said(delete):
        out += ["      description={", "        <>", f"          {said(delete)}", "          {consequence}", "        </>", "      }"]
    else:
        out.append("      description={consequence}")
    out += [f"      confirmLabel={js(agree(delete))}", f"      cancelLabel={js(cancel)}", "      destructive", "      onConfirm={onConfirm}", "    />", "  )", "}", ""]
    return "\n".join(out)


def skeleton_message(name, result, pattern, fields, values, stack):
    kind, duration, most = values["messages.result"], values["messages.duration_ms"], values["messages.max"]
    until = duration == conventions.UNTIL_CLOSED
    stays = "until it is closed" if until else f"for {duration} ms"
    rule = f"{RESULT_PHRASE[kind]}" + ("" if kind == "new-entry" else f", {stays}, {most} at a time")
    save = word_of(values, "save", "保存")
    example = f"{result['object'] or '{object}'}を{save}しました。"
    if stack == "html":
        out = head_lines(result, pattern, stack) + [f"<!-- the result of an operation: {rule} (Conventions, messages) -->"]
        if kind != "new-entry":
            out += [f'<div data-pattern="{pattern["id"]}" data-message="result" data-message-kind="{kind}" data-duration="{duration}" role="status">',
                    f'  <p data-pattern-slot="text">{example}</p>']
            if until:
                out.append(f'  <button type="button" data-pattern-slot="close">{pattern["labels"]["close"]}</button>')
            out.append("</div>")
        return "\n".join(out + [""])
    if kind == "status-bar":
        out = head_lines(result, pattern, stack) + import_lines(["ShellApi"])
        out += ["", "/**", f" * The messages of this screen: {rule} (Conventions, messages).",
                f" * After an operation ends, call `notify` of the shell's api: `notify({js(example)})`.", " */",
                f"export function {name}({{ notify }}: Pick<ShellApi, \"notify\">, text = {js(example)}) {{", "  notify(text)", "}"]
        return "\n".join(out + [""])
    placed = kind in ("bar", "near-control")
    out = head_lines(result, pattern, stack) + import_lines((["Messages"] if placed else []) + ["useMessages"])
    out += ["", "/**", f" * The messages of this screen: {rule} (Conventions, messages).",
            f" * After an operation ends, call `show`: `show({js(example)})`; an operation that can be taken back passes `undo`.", " */",
            f"export function use{name}() {{",
            f'  return useMessages({{ result: "{kind}", durationMs: {"null" if until else duration}, max: {most} }})', "}"]
    if placed:
        where = "at the top of the content" if kind == "bar" else "beside the control that ran the operation"
        out += ["", f"/** Place it {where}, with the `messages` and the `close` of the hook above. */",
                f"export function {name}({{ messages, onClose }}: {{ messages: ReturnType<typeof use{name}>[\"messages\"]; onClose: (id: number) => void }}) {{",
                f'  return <Messages messages={{messages}} kind="{kind}" durationMs={{{"null" if until else duration}}} onClose={{onClose}} />', "}"]
    return "\n".join(out + [""])


SKELETONS = {"entry.slip": skeleton_slip, "master.form": skeleton_master, "collection.conditions": skeleton_conditions,
             "action.function-keys": skeleton_function_keys, "feedback.confirm": skeleton_confirm,
             "feedback.message": skeleton_message}


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
    if isinstance(node, Cond):
        if stack == "shadcn":
            return ([pad + "{items.length === 0 ? ("] + emit(node.empty, stack, depth + 1, uses) + [pad + ") : ("]
                    + emit(node.filled, stack, depth + 1, uses) + [pad + ")}"])
        return ([pad + "<!-- when the collection is empty, in place of the table: -->"] + emit(node.empty, stack, depth, uses)
                + [pad + "<!-- otherwise: -->"] + emit(node.filled, stack, depth, uses))
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
    fields = any(isinstance(c, Field) for c in walk(root))
    head += ["", "type Item = Record<string, unknown>", ""] if needs_items or fields else [""]
    if needs_items:
        sig = f"export function {name}({{ items, href }}: {{ items: Item[]; href: (item: Item) => string }}) {{"
        if not any("href(item)" in line for line in body):
            sig = f"export function {name}({{ items }}: {{ items: Item[] }}) {{"
        if any(isinstance(c, Cond) for c in walk(root)) or pattern["id"] == "record.activity":
            empty = []  # the table shows its own empty state; a record's history holds its creation at least
        else:
            empty = (["  if (items.length === 0) {", "    return ("] + emit(empty_state(result["object"]), "shadcn", 3, uses)
                     + ["    )", "  }"])
        imports_used = []
    else:
        sig = f"export function {name}({{ item }}: {{ item: Item }}) {{" if fields else f"export function {name}() {{"
        empty = []
        imports_used = []
    del imports_used
    return "\n".join(head + [sig] + empty + ["  return ("] + body + ["  )", "}", ""])


def walk(node):
    yield node
    if isinstance(node, Cond):
        children = [node.empty, node.filled]
    else:
        children = getattr(node, "children", []) or ([node.child] if isinstance(node, Loop) else [])
    for child in children:
        yield from walk(child)


def render_html(result, pattern, root, needs_items):
    lines = [f"<!-- product-ui scaffold: {pattern['id']} for section {result['section']} ({result['screen']}).",
             f"     Slots, their order and their limits: patterns/{pattern['id']}.json and the Slots table in ui-brief.md.",
             "     Replace each {{label}} with the record's value, fill the notes, and keep every data-pattern attribute. -->"]
    if needs_items and not any(isinstance(c, Cond) for c in walk(root)) and pattern["id"] != "record.activity":
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


def read_tokens(brief):
    """The tokens.json beside a brief as a dict; None where it is missing or does not parse."""
    path = os.path.join(os.path.dirname(os.path.abspath(brief)), "tokens.json")
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


UI_IMPORT_LINE = re.compile(r'from "@/components/ui/([\w-]+)"')


def missing_ui(brief, files):
    """The shadcn/ui components the written skeletons import that the project lacks, in name order.

    The project is the nearest folder at or above the brief with a package.json; without one every imported
    component counts as missing.
    """
    used = sorted({name for path in files for name in UI_IMPORT_LINE.findall(open(path, encoding="utf-8").read())})
    project = os.path.dirname(os.path.abspath(brief))
    while not os.path.exists(os.path.join(project, "package.json")):
        parent = os.path.dirname(project)
        if parent == project:
            return used
        project = parent
    root = os.path.join(project, "src", "renderer", "src") if kit.is_electron_vite(project) else (
        os.path.join(project, "src") if os.path.isdir(os.path.join(project, "src")) else project)
    return [name for name in used if not os.path.exists(os.path.join(root, "components", "ui", name + ".tsx"))]


def stack_from_tokens(brief):
    tokens = read_tokens(brief)
    if tokens is None:
        return "shadcn"
    meta = tokens.get("meta") or {}
    stack = meta.get("stack") or {}
    if stack.get("base") == "smarthr-ui":
        return "smarthr"
    if stack.get("base") == "astryx":
        return "astryx"
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
        conv = resolve.load_conventions(args.brief)
        new_lines, results = resolve.resolve(text.split("\n"), library.load_index(), patterns, conv)
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
    # The section keys a conventions skeleton reads (lines, auto, required, groups), by screen and section.
    section_fields = {(b["screen"], s["name"]): s["fields"] for b in resolve.read_blocks(new_lines) for s in b["sections"]}
    for result in results:
        if not result["pattern"]:
            continue
        n += 1
        pattern = patterns[result["pattern"]]
        if stack in ("shadcn", "html") and pattern["id"] in SKELETONS:
            body = SKELETONS[pattern["id"]](component_name(n, pattern["id"]), result, pattern,
                                            section_fields.get((result["screen"], result["section"]), {}), conv["values"], stack)
        elif stack in ("shadcn", "html"):
            root, needs_items = build(pattern, result["slots"], result["object"], result["section"])
            body = (render_shadcn(n, result, pattern, root, needs_items) if stack == "shadcn"
                    else render_html(result, pattern, root, needs_items))
        else:
            body = render_note(stack, result, pattern)
        path = os.path.join(out_dir, f"{n:02d}-{pattern['id'].replace('.', '-')}{ext}")
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
        written.append({"section": result["section"], "screen": result["screen"], "pattern": pattern["id"], "file": path})
    if conv.get("surface") == "desktop":
        try:
            desktop_files = {"command-set.ts": command_set.command_set_ts(new_lines),
                             "window-spec.ts": command_set.window_spec_ts(new_lines, conv["values"], read_tokens(args.brief))}
        except command_set.CommandSetError as exc:
            print(f"FAIL: {exc}")
            return 1
        for name, body in desktop_files.items():
            path = os.path.join(out_dir, name)
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(body)
            written.append({"section": "Command set" if name.startswith("command") else "Window", "screen": "(window)",
                            "pattern": name, "file": path})
    needed = missing_ui(args.brief, [w["file"] for w in written if w["file"].endswith(".tsx")]) if stack == "shadcn" else []
    if args.json:
        print(json.dumps({"status": "PASS", "stack": stack, "files": written, "shadcn_add": needed}, ensure_ascii=False, indent=2))
    else:
        for w in written:
            print(f"{w['screen']} / {w['section']}: {w['pattern']} -> {w['file']}")
        if needed:
            print(f"next: npx shadcn@latest add {' '.join(needed)}")
        print(f"PASS: {len(written)} file(s), stack {stack}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # a cp932 or cp1252 console cannot print Japanese
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
