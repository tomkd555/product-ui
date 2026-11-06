# UI brief: {{meta.name}}

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: {{purpose}}
- Surface: {{meta.surface}}   (saas = an application screen a person operates, behind a login or public; lp = a marketing page)
- Structure: {{meta.structure}}   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: {{the logo file in the header | the product name as text in the header | none}}   (the header shows the product: the logo file when `meta.logo` names one, else the product name as text; a letter tile, a monogram or a drawn mark is never invented; `none` only for a fragment that sits inside another screen's shell)
- Tokens: {{tokens_path}}
- Theme: {{theme_path}}
- Built files: {{built_files}}   (listed for Step 4, completed at Step 5)
- Entry: {{the HTML file to render: `dist/index.html` for a bundler project}}   (Step 5)
- Controls: {{wired|mock}}, naming which are which when the screen has both (wired: every control reaches its destination; mock: a control whose destination is outside this build links to the route it will open, a form posts to its route, and no control reports an effect it does not have; a control that changes what the page shows from the page's own state, such as a reply added to the thread or a status changed in place, is named here with the part a server would do) (Step 5)

## Objects

One row per object the screens show, from `references/patterns.md`. `scripts/patterns/resolve.py` fills each section's slots from it. Rank the Key properties by the reader's job, highest first: the rank decides which ones a row, a card or a header shows. Tag a property `[price]`, `[rating]` or `[variations]` where a pattern asks for one.

| Object | Identifier | Status | Image | Key properties, ranked | Job they serve |
|---|---|---|---|---|---|
| {{object}} | {{the property a reader knows one record by}} | {{status property, or none}} | {{image property, placeholder, or none}} | {{property 1, property 2, …}} | {{role from meta.users}}: {{the job the ranking serves}} |

## Composition

One block per screen, from `references/composition.md`. With two or more screens, head each block `### {{screen}} \`{{route}}\`` (a parameter as `:id`, a tab as `?tab=…`); `check_render.py --plan` reads the Job class of the block whose route matches the Built files line.

- Kind: {{the section of `references/real-screens.md` this screen follows}}
- Regions: {{the regions of that kind this screen carries, in reading order, the shell first}}
- Job class: {{monitor|enter|lookup|decide|record}}
- Reader: {{role from meta.users}}, {{frequency}}, {{expertise}}   (the frequency of this screen where it differs from the product's; the device where the request reports one; on `lp`, the visitor the page addresses)
- Dominant element: {{the element the eye lands on first after the page title}}, because {{why it is the purpose}}
- Second: {{element}}
- Reading order: {{stop 1}} → {{stop 2}} → {{stop 3}}{{ → stop 4 → stop 5}}
- Density: {{the summary and the main chart in the first viewport | one column | dense rows behind a filter | the comparison first | the record first, its properties beside its body}}
- Archetype: {{list-detail|supporting-pane|feed|single-column|dashboard}}
- Grouping: {{section: distance | region | rule}}, one entry per section
- Constant with the product's other screens: {{shell, navigation, controls, scale, …}}
- Decided for this screen: {{dominant element, archetype, density, group sizes}}
- Omitted: {{each region or control of the kind that is left out, with the reason the request gives; then what else was cut, and why the rest is more visible for it}}
- Tile row: {{none | the tiles and the monitored quantity of each, with its comparison where it has one}}
- Sections: one line per section, in reading order; `resolve.py` adds `pattern <id>` (`references/patterns.md`)
  - {{section}}: content {{records|record-header|record-detail|record-fields|items|products|measures|tasks|form|prose}}; object {{a row of ## Objects}}; compare {{yes|no, for records and products}}
- Lead content (`lp` only): {{what the reader sees first: the product itself, named}}

## Slots

Written by `scripts/patterns/resolve.py` from the `- Sections:` lines and the `## Objects` table. Change those and run it again; an edit here is overwritten.

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none. Prices, plan terms and the other facts the request states about the product are content and stay out of this table.

| Item | Text as shown | Source |
|---|---|---|
| {{figure, testimonial, customer logo or claim}} | {{text}} | {{where it comes from}} |

## States

Per screen, the state each part falls back to. A collection, a fetch or a form without its entry here has no designed state. A state the default URL cannot reach names the URL that shows it.

- Collection `{{name}}`: empty state {{what the reader sees and the next action}}
- Fetch `{{name}}`: loading {{state}}; error {{state, with the cause the reader can act on}}   (a mock that reads local sample data writes `none: local sample data` and builds neither)
- Form `{{name}}`: validation {{when it runs, where the message sits}}

## Sample data

- Supplied by: {{the user | the project's fixtures | invented for this mock | none: the screen holds no records}}
- (Delete this line when the screen holds no records.) Mock data varies names, dates and amounts, and carries no statistic the reader did not ask for; a monitored figure keeps its comparison. Its order follows no formula: record numbers and update times interleave as in a product in use, and names are a mix a real team would have.
- Volume: {{the records, messages or rows the screen shows, against the volume production screens of the kind hold (`references/real-screens.md`, Every screen)}}

## What the reviewer judges

`check_render.py` measures contrast, token discipline, overflow, clipped text, hit areas, input labels, text under the minimum size, heading levels, console errors, links without a destination, the viewport width, nested enclosures, spacing steps, emphasis levels and equal tile rows before any auditor starts. The reviewer judges the rest:

- the cold-read questions below, from the screenshot, before the dump is read
- overlap and alignment
- whether interactive elements do what they look like they do, when the controls are wired
- reflow at 375px
- the dark theme, when `tokens.json` declares `color_dark`
- the copy questions and the reader-fit questions below

## Cold-read questions, answered from the screenshot

1. Name the element the eye lands on first after the page title. Is it the dominant element above?
2. Squint at the capture. Count the levels of emphasis that survive. Under three is a finding.
3. List the first four stops. Do they match the reading order above?
4. Count the equal-sized siblings in the top region. Why does each earn equality with the others?
5. Which cue separates the groups: distance, a region, a rule? Are the gaps between groups visibly larger than the gaps within them?
6. Is the screen a run of equal tiles followed by equal panels? Would reordering them change the meaning?
7. Cover the labels. Could this be another product, or another screen of this product? What here is specific to its content?
8. Does the density fit the job class above?

## Copy questions, answered against the running page

1. Does each button label name what the button actually does? 「保存」 on a control that publishes, 「送信」 on one that only validates, passes every script.
2. Does each error state the actual cause, in terms the reader can act on?
3. Does the page title name the object or the task of this screen, and each section heading its content?
4. Is the copy true? Untrue copy includes 「削除したファイルは復元できません」 on a file the trash can restore, a dialog understating what it deletes, and a count that differs from the rows shown.
5. Is one object called by one name throughout, including names not yet in `voice.terms` in `tokens.json`?
6. Is the empty state's action the right next action for a reader who cannot perform it yet?
7. Does the register the tokens settle (敬体 or 常体) suit this audience? 常体 on a public form is the mismatch to look for.

## Reader-fit questions, answered against the running page and `meta.users`

1. Which recorded user group does this screen serve, and does the screen show it: the dense form and the frequent action within one click for a daily intermediate or expert reader, fewer options and a guided path for a first-time or occasional one?
2. For each structural choice (the density, the guidance text, the actions one click away), which recorded fact in `meta.users` justifies it? A choice with no recorded fact behind it is a finding.
3. Does each label predict what lies behind it, in words the recorded group uses (`meta.users[].job` and `voice.terms` are the evidence)? A label that names the feature, the computation or the product where the object or the reader's task belongs is a finding.

## Content questions, answered against the running page and `## Slots`

1. Take one item of each collection. Can the reader recorded in `## Objects` tell the record they want from it without opening it?
2. Does each slot show the property the Slots table assigns it? A property shown with no row there, or a row with nothing on the screen, is a finding.
3. Which pattern and which of its sources does each component follow? Where the screen departs from its pattern, does the brief say why?

## Structure

Keep this section when Structure is ooui; delete it for task and unset.

Each object is a row of `## Objects`, which holds its properties.

| Object | Actions | Related objects | Collection view | Single view |
|---|---|---|---|---|
| {{object}} | {{actions}} | {{related objects}} | {{path or screen}} | {{path or screen}} |

Task flows kept as a sequence, each with the condition that admits it: {{flows, or none}}

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name, and the key properties `## Objects` ranks for it, in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
