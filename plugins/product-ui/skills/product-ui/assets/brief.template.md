# UI brief: {{meta.name}}

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: {{purpose}}
- Surface: {{meta.surface}}   (saas = an application screen a person operates, behind a login or public; lp = a marketing page; desktop = an application in its own window, built with Electron, `references/desktop.md`)
- Structure: {{meta.structure}}   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: {{the logo file in the header | the product name as text in the header | none}}   (the header shows the product: the logo file when `meta.logo` names one, else the product name as text; a letter tile, a monogram or a drawn mark is never invented; `none` only for a fragment that sits inside another screen's shell)
- Tokens: {{tokens_path}}
- Theme: {{theme_path}}
- Built files: {{built_files}}   (listed for Step 4, completed at Step 5)
- Entry: {{the HTML file to render: `dist/index.html` for a bundler project}}   (Step 5)
- Captures: {{each further screen and state the review renders, as a short name and its URL path: `detail /orders/SO-1042`, `empty /?state=empty`, `no-results /?q=zzz`, `invalid /expenses/new?state=invalid`; `none` for one screen with no state}}   (Step 5; the Entry is captured as the default)
- (desktop) Captures name a state of the window by its query: `file-new ?view=file&page=new`, `properties ?pane=properties`, `save-prompt ?prompt=save`. The review captures each at the two sizes of `## Window`.
- Controls: {{wired|mock}}, naming which are which when the screen has both (wired: every control reaches its destination; mock: every link and every control that opens a page leads to a view of this build, a view outside the build gets no control on the screen and is listed in the hand-over, a form's submit moves to the state the brief names for it, with the route a server would receive written here, and no control reports an effect it does not have; a control that changes the view of the data on this page, such as the search, a filter, a preset, the sort, the pagination or a tab, works on the sample data and keeps its state in the URL; a control that changes what the page shows from the page's own state, such as a reply added to the thread or a status changed in place, is named here with the part a server would do; `references/interaction.md`) (Step 5)

## Objects

One row per object the screens show, from `references/patterns.md`. `scripts/patterns/resolve.py` fills each section's slots from it. Rank the Key properties by the reader's job, highest first: the rank decides which ones a row, a card or a header shows. Tag a property `[price]`, `[rating]`, `[variations]` or `[offer]` where a pattern asks for one.

| Object | Identifier | Status | Image | Key properties, ranked | Job they serve |
|---|---|---|---|---|---|
| {{object}} | {{the property a reader knows one record by}} | {{status property, or none}} | {{image property, placeholder, or none}} | {{property 1, property 2, …}} | {{role from meta.users}}: {{the job the ranking serves}} |

## Composition

One block per screen, from `references/composition.md`. With two or more screens, head each block `### {{screen}} \`{{route}}\`` (a parameter as `:id`, a tab as `?tab=…`); `check_render.py --plan` reads the Job class of the block whose route matches the URL of each capture.

- Kind: {{the section of `references/real-screens.md` this screen follows; `desktop window` on `desktop`}}
- Regions: {{the regions of that kind this screen carries, in reading order, the shell first}}
- Job class: {{monitor|enter|lookup|decide|record}}
- Reader: {{role from meta.users}}, {{frequency}}, {{expertise}}   (the frequency of this screen where it differs from the product's; the device where the request reports one; on `lp`, the visitor the page addresses)
- Dominant element: {{the element the eye lands on first after the page title}}, because {{why it is the purpose}}
- Second: {{element}}
- Reading order: {{stop 1}} → {{stop 2}} → {{stop 3}}{{ → stop 4 → stop 5}}
- Density: {{the summary and the main chart in the first viewport | one column | dense rows behind a filter | the comparison first | the record first, its properties beside its body | `compact` on `desktop`}}
- Archetype: {{list-detail|supporting-pane|feed|single-column|dashboard}}
- Grouping: {{section: distance | region | rule}}, one entry per section
- Constant with the product's other screens: {{shell, navigation, controls, scale, …}}
- Decided for this screen: {{dominant element, archetype, density, group sizes}}
- Omitted: {{each region or control of the kind that is left out, with the reason the request gives; then what else was cut, and why the rest is more visible for it}}
- Tile row: {{none | the tiles and the monitored quantity of each, with its comparison where it has one}}
- (The Sections list below holds one line per section, in reading order; `resolve.py` adds `pattern <id>` to each, `references/patterns.md`.)
- Sections:
  - {{section}}: content {{records|record-header|record-detail|record-fields|history|items|products|measures|chart|tasks|slip|master|closing|import|approval|form|prose}}; show {{the properties of this section, where the ranking's first ones fit it badly}}; object {{a row of ## Objects}}; compare {{yes|no, for records and products}}
- (A `slip` section adds `lines {{the object of its lines}}; totals {{小計, 消費税, 合計}}; auto {{the line properties the screen computes}}; required {{the properties the reader has to fill}}`. A `master` section adds `groups {{group=property, property / group=property}}; required {{…}}`. A `records` section whose list sits under search conditions adds `conditions {{property, property}}`. `references/patterns.md` gives each key.)
- Lead content (`lp` only): {{what the reader sees first: the product itself, named}}

## Window

(desktop only; delete this section and the next three on `saas` and `lp`.) From `references/desktop.md`, The brief's desktop sections. `resolve.py` fills a row left out with the reference's value and adds the rows of the fixed regions.

| Item | Value |
|---|---|
| size | {{width}}x{{height}} |
| minimum | {{width}}x{{height}} |
| title | {file} - {{meta.name}} |
| left pane | {{title}} {{default width}} {{min}}-{{max}} {{open|closed}}, or none |
| right pane | {{title}} {{default width}} {{min}}-{{max}} {{open|closed}}, or none |
| document | {{what the document area holds}}; minimum width {{px}} |
| status bar | {{left items}} / {{right items}} |

## Commands

(desktop only.) One row per command of the application's own. The commands of the operations listed below are written by `resolve.py`.

| Tab | Group | Command | Size | Keys | Key tip | Enabled when | Runs |
|---|---|---|---|---|---|---|---|
| {{tab}} | {{group}} | {{command}} | {{large|small|menu|check}} | {{keys, or none}} | {{letter}} | {{the condition, or always}} | {{what it does}} |

- Operations: {{the profile's action names the application has: new, open, save, save-as, close, undo, redo, cut, copy, paste, select-all, delete, export, print, find, replace, zoom}}
- Collapse: {{the groups in the order they collapse as the window narrows}}

## File view

(desktop only.) One row per item that opens a page.

| Item | Page or action |
|---|---|
| {{新規|エクスポート|印刷|オプション}} | {{what the page holds}} |

## Command set

Written by `scripts/patterns/resolve.py` from `## Commands`, `## File view` and the profile (`references/desktop.md`). Change those and run it again; an edit here is overwritten.

## Slots

Written by `scripts/patterns/resolve.py` from the `- Sections:` lines and the `## Objects` table. Change those and run it again; an edit here is overwritten.

## Conventions

Written by `scripts/patterns/resolve.py` from `meta.profile` and `meta.profile_product` of `tokens.json` (`references/profiles.md`). Change those and run it again; an edit here is overwritten.

none

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none. Prices, plan terms and the other facts the request states about the product are content and stay out of this table.

| Item | Text as shown | Source |
|---|---|---|
| {{figure, testimonial, customer logo or claim}} | {{text}} | {{where it comes from}} |

## States

Per screen, the state each part falls back to. A collection, a fetch or a form without its entry here has no designed state. A state the default URL cannot reach names the URL that shows it.

- Collection `{{name}}`: empty state {{what the reader sees and the next action}}; no results {{what the reader sees when the search or filter matches nothing, and the control that clears it}}
- Fetch `{{name}}`: loading {{state}}; error {{state, with the cause the reader can act on}}   (a mock that reads local sample data writes `none: local sample data` and builds neither)
- Form `{{name}}`: validation {{when it runs, where the message sits}}

## Sample data

- Supplied by: {{the user | the project's fixtures | invented for this mock | none: the screen holds no records}}
- (Delete this line when the screen holds no records.) Mock data varies names, dates and amounts, and carries no statistic the reader did not ask for; a monitored figure keeps its comparison. Its order follows no formula: record numbers and update times interleave as in a product in use, and names are a mix a real team would have.
- Volume: {{the records, messages or rows the screen shows, against the volume production screens of the kind hold (`references/real-screens.md`, Every screen)}}
- Edge records: {{the records that test the layout, by name: the longest and the shortest name, a record with its optional properties empty, a zero and a seven-digit amount, each state of the object, a date past due, a record changed today (`references/interaction.md`)}}
- Formats: {{amount, date, relative time and count, one form each across the screen}}

## What the reviewer judges

`check_render.py` measures contrast, token discipline, overflow, clipped text, hit areas, input labels, text under the minimum size, heading levels, console errors, links without a destination, the viewport width, nested enclosures, spacing steps, emphasis levels and equal tile rows before any auditor starts. The reviewer judges the rest:

- the cold-read questions below, from the screenshot, before the dump is read
- overlap and alignment
- whether interactive elements do what they look like they do, when the controls are wired
- reflow at 375px
- the dark theme, when `tokens.json` declares `color_dark`
- the copy questions and the reader-fit questions below
- the conventions questions below, when `## Conventions` names a profile

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

## Interaction questions, answered by operating the running page and opening each state's URL

From `references/interaction.md`. A question about a part this screen lacks is answered `no such part`.

1. Type in the search field, change a filter, the sort and the page. Does the record count follow each change, does the URL change with it, and does a reload show the same view?
2. Does a filter that matches nothing show the no-results state, with the filter still visible and a control that clears it, and does that state differ from the empty state?
3. Does each count on the screen equal the records it counts under the current filter?
4. For each action that changes or sends data, on every route that offers it (the create form and the edit form each): does it end in the state the brief names, with no error page and no not-found screen, and for a destructive or bulk action is the step before it the one its row in "Destructive and bulk actions" gives? Follow each navigation item, each button that opens a page and one link of each kind: does every one end on a view of this build, with none on the not-found screen?
5. Submit each form empty. Does each error sit beside its field and say how to put it right, and does the focus move to the first error?
6. Find the longest value and the empty value among the edge records. Does the long one stay inside its slot at 1280px and at 375px, and is an empty property of a record printed as a word (未設定, なし) while an empty table cell stays blank?
7. Is each amount, date and count in the one format the brief gives it, with numbers that are compared in a column right-aligned?

## Conventions questions, answered by operating the running page with the keyboard

From `references/profiles.md`. Answered only when `## Conventions` names a profile; each row of that section is the expected answer.

1. Press Enter in the first field of each entry form, then in its last field. Does the focus move as `keys.enter` and `keys.enter_last` say, and does Enter in a text being converted by the input method only settle the conversion?
2. Press each key of `keys.function` and `keys.shortcuts`. Does each run the operation its row names, is each shown with the word of its row where `keys.display` says, and does the same operation run by a click?
3. Does each control that creates, saves, deletes, starts a new record, looks up or searches carry the word `words` gives it, on every screen?
4. Run the registration. Does the step before it, the form and the time of its result and the number of messages on the screen match `confirm` and `messages`? Press the registering control twice in a row: does one registration run?
5. Does the screen stay free of the product's name and logo whose conventions it follows?

## Window questions, answered by operating the running window

(desktop only.) From `references/desktop.md`; each answer is checked against `## Window` and `## Command set`.

1. Narrow the window to its minimum size. Do the groups collapse one at a time in the order of `- Collapse:`, does the tab row stand alone once every group is collapsed, and does the document keep its minimum width?
2. Press Alt. Do key tips show on ファイル, on each tab and on the quick access toolbar, does a tab's letter show its commands' key tips, and does Esc step back one level at a time?
3. Change the document and close the window. Does the save prompt show its sentence with 保存, 保存しない and キャンセル in that order, and does each button do what `references/desktop.md` says? Do 新規 and 開く ask the same?
4. Press F6 and Shift+F6. Does the focus move between the tab row, the document, each open pane and the status bar?
5. Does each command show its name and keys in its tooltip, and a disabled one the condition under which it runs?

## Content questions, answered against the running page and `## Slots`

1. Take one item of each collection. Can the reader recorded in `## Objects` tell the record they want from it without opening it?
2. Does each slot show the property the Slots table assigns it? A property shown with no row there, or a row with nothing on the screen, is a finding.
3. Which pattern and which of its sources does each component follow? Where the screen departs from its pattern, does the brief say why?

## Structure

Keep this section when Structure is ooui; delete it for task and unset.

Each object is a row of `## Objects`, which holds its properties. A sub object, shown inside another object's single view, writes `inside {{object}}` in both view columns.

| Object | States, in order | Actions, by state | Related objects (one or many) | Collection view | Single view |
|---|---|---|---|---|---|
| {{object}} | {{state 1 → state 2 → …, or none}} | {{state: actions; any state: actions}} | {{object (one), object (many)}} | {{path or screen}} | {{path or screen}} |

Tasks, each with the place it lands (`references/ooui.md`, Tasks): {{task → preset `name` on the collection | default of a filter or field | template | action on the object | property shown | display form}}

Task flows kept as a sequence, each with the condition that admits it: {{flows, or none}}

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name, and the key properties `## Objects` ranks for it, in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
6. Is every mention of an object whose single view the build holds, such as a name in a row or a value in a property list, a link to that view?
7. Does each record print the word of its state, and are the actions offered on it the ones the table gives that state?
8. Does each task above land in the place the table gives it, with no navigation item of its own?
