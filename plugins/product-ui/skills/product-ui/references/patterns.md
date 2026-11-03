# Patterns

Source of record for the pattern library under `patterns/`, its decision table `patterns/index.json`, the `## Objects`, `- Sections:` and `## Slots` parts of `ui-brief.md`, the scripts under `scripts/patterns/`, check_pattern.py (PT0 to PT7), and R42 to R48 in `scripts/render/check_render.py`; `references/ui-copy.md` holds the label checks C33 to C36 that read the patterns' label forms. Read it at Step 3 of `SKILL.md`, after the composition plan has settled each section's container and before any markup, and when one of these checks fires.

## What it settles

`references/composition.md` settles which container a section gets: a table, a list, a card, a heading on the ground. A container chosen right can still carry nothing the reader needs: a card of a title and one number passes every element check, and deleting the filler around it makes it emptier. A pattern settles what the container carries: its slots (the object's name, its state, its key properties, its actions), their order, their limits, and the words of its labels. Each pattern is drawn from what production design systems and research publish about that component, and names its sources.

The design systems agree on five rules, and the patterns encode them:

1. Every item carries one human-readable identifier: the object's own name, never a generated ID (SmartHR, NN/g, Primer, DADS, Salesforce).
2. An item carries a small, fixed set of key properties, chosen for what the reader identifies or decides by (Salesforce, HubSpot, Baymard, SmartHR).
3. An item links to its single view; an item that is a link as a whole holds no other control (SmartHR, DADS, Carbon).
4. Actions are capped, and an action on a row also exists in the single view (Polaris, SmartHR, DADS).
5. A collection's heading names the object, or the subset shown, never the view (Polaris, SmartHR).

## The library

| Pattern | For | Required slots |
|---|---|---|
| `collection.row.resource` | a list the reader scans by name | name, info (1 to 3) |
| `collection.table.index` | records the reader compares by property | heading, name (first column), property (1 or more) |
| `record.header` | the top of one record's single view | title |
| `record.body.two-column` | the body of one record's single view | primary |
| `record.summary-list` | one record's fields as key and value | key, value |
| `task.list` | the tasks of a procedure and their states | task, status |
| `browse.card` | one unit of a set of unlike items, or an object known by its image | title, content (1 to 3) |
| `commerce.product-item` | a product in a shop's listing | image, title, price, rating, attributes (1 to 3) |
| `status.badge` | a record's state as one word | label |
| `state.empty` | a collection that holds nothing | title |
| `measure.tile.kpi` | a monitored quantity on a `monitor` screen | label, value, comparison |

`status.badge` and `state.empty` are used inside the others. Run `python {SKILL_DIR}/scripts/patterns/validate.py` after any change to a file under `patterns/`.

## The pattern format

One JSON file per pattern, named by its id (`patterns/collection.row.resource.json`).

| Field | Holds |
|---|---|
| `id` | dotted lower case: the family, then the form |
| `version` | a whole number, raised when a slot or a rule changes |
| `kind` | `collection-row`, `collection-table`, `record-header`, `record-body`, `record-fields`, `task-list`, `card`, `product-item`, `badge`, `empty-state` or `tile`. The kinds `collection-row`, `task-list`, `card`, `product-item`, `tile` and `badge` describe one item, and every item carries `data-pattern`; the others describe a block, which carries it once |
| `summary` | what the pattern is for, one sentence |
| `not_for` | where it does not belong, and what goes there instead |
| `slots` | the slots in reading order (below) |
| `rules` | each `{"rule": …, "from": […]}`; `from` names evidence ids of this pattern, or `product-ui` for a rule of this skill's own |
| `labels` | the word forms the pattern fixes: `collection_heading`, `empty`, `empty_filtered`, `status_header` and the like, with `{object}` for the object's name |
| `uses` | the patterns it holds inside (`status.badge`, `state.empty`) |
| `maps_to` | the component each stack draws it with: `shadcn`, `html`, `dads`, `smarthr`; `null` where the stack has none |
| `evidence` | each `{"id", "source", "url", "says"}`: a page that was read, and what it says, paraphrased |
| `evidence_status` | `documented` (the sources state it), `cross-specimen` (two or more captured specimens show it), `inferred` (this skill's reading) |

A slot is `{"id", "takes", "required", "min", "max", …}`. `max` defaults to 1, and `null` means no limit. `takes` names what the slot holds:

| `takes` | Filled from |
|---|---|
| `identifier`, `status`, `image` | the object's row in `## Objects`: the Identifier, Status and Image columns |
| `property` | the object's Key properties, in rank order, up to the slot's `max` |
| `price`, `rating`, `variations` | a Key property tagged `[price]`, `[rating]` or `[variations]` |
| `action`, `label`, `text`, `link`, `control`, `count`, `measure`, `comparison`, `section` | written on the screen |

Other slot fields: `emphasis: 1` (the slot is the strongest text of its item, R42), `link: "single-view"` (the slot or the item opens the record), `same_across_items` (every item shows the same fields, R43), `label_of` (the slot holds the label of another slot's values), `when` (the condition for an optional slot), `column` and `align_numbers` (tables).

## Choosing a pattern

The brief says what each section holds; the decision table says which pattern that is. Nothing in between is chosen by taste.

### The brief

`## Objects`, one row per object the screens show:

| Column | Holds |
|---|---|
| Object | the object's name, as `voice.terms` and the navigation call it |
| Identifier | the property a reader knows one record by |
| Status | the property that holds its state, or `none` |
| Image | the property that holds its image, `placeholder` when the image is not yet supplied, or `none` |
| Key properties, ranked | the other properties, highest rank first; tag a property `[price]`, `[rating]` or `[variations]` where a pattern asks for one |
| Job they serve | the reader from `meta.users` and the job the ranking serves |

The rank is the decision: it comes from the reader's job, and it decides which properties a row, a card or a header shows when the slot takes fewer than all of them.

In each Composition block, a `- Sections:` list, one line per section:

```
- Sections:
  - 請求書: content records; object 請求書; compare yes
```

| Key | Values |
|---|---|
| `content` | `records` (a set of same-kind records), `record-header`, `record-detail` and `record-fields` (one record's header, body and fields), `items` (unlike items browsed), `products`, `measures`, `tasks`, `form`, `prose` |
| `object` | a row of `## Objects`; needed for every content but `measures`, `form` and `prose` |
| `compare` | `yes` when the reader compares the records by property, `no` when the reader finds one by name; needed for `records` and `products` |
| `media` | `no` drops an optional image slot |
| `pattern` | written by `resolve.py` |

### The decision table

`patterns/index.json` holds one row per case. A row matches a section when each key it sets (`content`, `job`, `compare`) equals the section's; a key the row leaves out matches anything. The job is the block's `- Job class:`.

| content | job | compare | pattern |
|---|---|---|---|
| records | any | yes | `collection.table.index` |
| records | any | no | `collection.row.resource` |
| record-header | any | any | `record.header` |
| record-detail | any | any | `record.body.two-column` |
| record-fields | any | any | `record.summary-list` |
| items | any | any | `browse.card` |
| products | any | yes | `collection.table.index` |
| products | any | no | `commerce.product-item` |
| measures | monitor | any | `measure.tile.kpi` |
| measures | enter, lookup, decide | any | none: the figure sits in the heading or the filter bar |
| tasks | any | any | `task.list` |
| form | any | any | none: `references/components.md` |
| prose | any | any | none: running text on the page ground |

`validate.py` (PV7) proves that every combination of content, job and compare meets exactly one row.

### resolve.py

```bash
python {SKILL_DIR}/scripts/patterns/resolve.py ui-brief.md
```

For each section it finds the row, writes `pattern <id>` (or `pattern none`) into the section's line, and writes the `## Slots` table after the Composition section: for each slot, the property it shows and where that came from (Identifier, Status, Image, Key property 3, a tag). A required slot the screen fills by hand is listed as `(on the screen)`. Slots are filled in the pattern's order, and property slots take the ranked properties from the top, so a header that shows four takes the first four.

A section the brief does not settle stops the run with the question that settles it, and nothing is guessed: `compare` missing on records, an object with no row, a required slot with nothing to show (a product with no `[price]`, a pattern needing an Image the object lacks). Ask the user that one question when the brief cannot answer it.

The same brief writes the same file. `--check` writes nothing and fails when the brief differs from what a run would write.

### scaffold.py

```bash
python {SKILL_DIR}/scripts/patterns/scaffold.py ui-brief.md [--stack shadcn|html|dads|smarthr]
```

Writes one skeleton per section with a pattern, under `scaffold/` beside the brief, numbered in the brief's order. The stack comes from `tokens.json` unless `--stack` names it. Each skeleton holds the slots in order, filled with the Slots table's properties, the collection's empty state with the pattern's words (「請求書はありません。」), and a note at each optional slot. `shadcn` writes TSX on the shadcn/ui components, `html` writes static HTML, `dads` and `smarthr` write a note naming the preset's component and the attributes each slot takes. The same brief writes the same bytes. It refuses a brief `resolve.py --check` would fail.

The build moves each skeleton into the screen, binds the record's keys, writes the words and keeps three attributes:

| Attribute | On |
|---|---|
| `data-pattern="<id>"` | each item of an item pattern; the block of a block pattern |
| `data-pattern-slot="<slot>"` | each slot |
| `data-pattern-field="<property>"` | each slot that shows a property of the object, with the property's name from `## Objects` |

An element that is a slot of one pattern and the root of another (a status badge inside a row) carries both `data-pattern-slot` and `data-pattern`: the slot belongs to the outer pattern, and the slots inside it to the inner one.

A slot is added or removed in the brief first: change the Objects ranking or the section, and run `resolve.py` again.

## Conformance: PT0 to PT7 and R42 to R48

### check_pattern.py, on the source (Step 4)

```bash
python {SKILL_DIR}/scripts/check_pattern.py <path> --json
```

It reads the markup files (`.html`, `.htm`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`) for the three attributes, outside `node_modules`, the build output and `scaffold/`. A slot belongs to the nearest `data-pattern` element around it. The brief is `ui-brief.md` beside the nearest `tokens.json`, or `--brief`; it is resolved in memory as `resolve.py` resolves it, and a brief that cannot be resolved leaves PT2's plan half, PT6 and PT7 unread, with the reason in the output.

| ID | Severity | Check |
|---|---|---|
| PT0 | warning | a suppression with no reason; it silences nothing |
| PT1 | error | an element missing a required slot of its pattern, a slot appearing fewer times than its `min`, or a slot name the pattern does not have |
| PT2 | error | a `data-pattern` id with no file under `patterns/`, or one no section of the brief resolves to (a pattern another resolved pattern `uses` passes) |
| PT3 | warning | slots out of the pattern's order: the first slot that comes after one the pattern puts later |
| PT4 | error | a slot appearing more times than its `max`: more than three properties in a row, a fourth table action, a third function button on a card |
| PT5 | error | a link that wraps every slot of its item holds another link or button |
| PT6 | warning | a slot shows a property (`data-pattern-field`) that no Slots row of its pattern assigns, or a Slots row's property no slot shows |
| PT7 | warning | a pattern the brief resolves that no element carries: the section was built without its skeleton |

Silence a misfire in the file, as `product-ui: ignore PT3 <reason>` on the line before or the same line, or `product-ui: ignore-file PT6 <reason>`; name the reason in the hand-over. A PT1, PT2, PT4 or PT5 the check read rightly is fixed, not silenced.

### R42 to R48, on the rendered page (Step 5)

`cdp.js` writes each `data-pattern` element with the slots it owns into the dump (`patterns`), and each enclosure's `inPattern` and `hasField`. `check_render.py` reads the library to know each pattern's slots. All seven are WARNINGs until the calibration (`research/20261103-real-site-patterns`) shows which hold on real sites well enough to be errors.

| ID | Check |
|---|---|
| R42 | in an item, the slot marked `emphasis: 1` (the name, the title, the value) is outweighed by another data slot: a larger size, or the same size at a heavier weight. Headings, keys and controls are not compared |
| R43 | items of one pattern under one parent show different sets of fields; an item without a value keeps its slot, blank |
| R44 | in a table pattern, a cell slot holding a number is not aligned to the end, or lacks `tabular-nums` |
| R45 | in a table pattern, a cell holds only a placeholder (`-`, `—`, `x`, `×`, `N/A`) |
| R46 | an item renders a required slot empty, or does not render it at all |
| R47 | an enclosure inside `<main>`, 120 by 48px or larger, that sits in no `data-pattern` element and holds no form control, on a page that carries patterns |
| R48 | a `status.badge` whose word is outside `voice.status` of `tokens.json` (`--tokens`); skipped without it |

A dump without `patterns` (an older capture) and a page with no `data-pattern` element skip all seven.

## Validation: PV1 to PV8

`scripts/patterns/validate.py`. Errors stop `resolve.py` and `scaffold.py` from reading the library rightly; the warning marks a pattern nothing reaches.

| ID | Severity | Check |
|---|---|---|
| PV1 | error | a file is not one JSON object, a field is missing or of the wrong type, `kind` or a `maps_to` stack is outside its set |
| PV2 | error | an id is not dotted lower case, differs from the file name, or is used twice |
| PV3 | error | a slot: no id, a duplicate id, `takes` outside its set, `required` not a boolean, `min` or `max` out of range, a required slot with `min: 0`; a pattern with no slot or no required slot |
| PV4 | error | `uses` names a pattern with no file |
| PV5 | error | no evidence, an entry without `id`, `source`, `url` (https) or `says`, `evidence_status` outside its set, a rule whose `from` names neither an evidence id of the pattern nor `product-ui` |
| PV6 | error | a table row's `content` or `job` is outside its set, its `pattern` has no file, or a row without a pattern says nothing in `say` |
| PV7 | error | a combination of content, job and compare that no row admits, or that two rows admit |
| PV8 | warning | a pattern no row selects and no pattern uses |

## Adding a pattern

1. Read the component's page in two or more production design systems or research bodies, and write what each says about the component's content into `evidence`, with the URL.
2. Write the slots in reading order, the limits the sources set, and the rules, each pointing at the evidence it rests on. A rule no source states is `from: ["product-ui"]`.
3. Add a row to `patterns/index.json` when the pattern is chosen by content, or name it in another pattern's `uses`.
4. Run `validate.py`; then `resolve.py` and `scaffold.py` on a brief that reaches it.

A source whose terms forbid automated use or AI training stays out of `evidence`, even when its content is quoted elsewhere.
