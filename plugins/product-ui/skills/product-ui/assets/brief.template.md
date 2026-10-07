# UI brief: {{meta.name}}

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: {{purpose}}
- Surface: {{meta.surface}}   (saas = a product screen behind a login; lp = a public landing page)
- Structure: {{meta.structure}}   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Tokens: {{tokens_path}}
- Theme: {{theme_path}}
- Built files: {{built_files}}   (Step 5)
- Controls: {{wired|mock}} (wired: every control reaches its destination; mock: links and buttons are placeholders) (Step 5)

## Composition

One block per screen, from `references/composition.md`. With two or more screens, head each block `### {{screen}} \`{{route}}\`` (a parameter as `:id`, a tab as `?tab=…`); `check_render.py --plan` reads the Job class of the block whose route matches the Built files line.

- Job class: {{monitor|enter|lookup|decide}}
- Reader: {{role from meta.users}}, {{frequency}}, {{expertise}}
- Dominant element: {{element}}, because {{why it is the purpose}}
- Second: {{element}}
- Reading order: {{stop 1}} → {{stop 2}} → {{stop 3}}{{ → stop 4 → stop 5}}
- Density: {{one screen | one column | dense rows behind an overview | the comparison first}}
- Archetype: {{list-detail|supporting-pane|feed|single-column|dashboard}}
- Grouping: {{section: distance | region | rule}}, one entry per section
- Constant with the product's other screens: {{shell, navigation, controls, scale, …}}
- Decided for this screen: {{dominant element, archetype, density, group sizes}}
- Omitted: {{what was cut, and why the rest is more visible for it}}
- Tile row: {{none | the tiles, the monitored quantity and comparison of each, and the dominant tile}}

## What the reviewer judges

`check_render.py` measures contrast, token discipline, overflow, hit areas, input labels, heading levels, nested enclosures, spacing steps, emphasis levels and equal tile rows before any auditor starts. The reviewer judges the rest:

- the cold-read questions below, from the screenshot, before the dump is read
- overlap and alignment
- whether interactive elements do what they look like they do, when the controls are wired
- reflow at 375px
- the dark theme, when `tokens.json` declares `color_dark`
- the copy questions and the reader-fit questions below

## Cold-read questions, answered from the screenshot

1. Name the element the eye lands on first. Is it the dominant element above?
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
3. Is each heading specific to this screen? 「概要」「詳細」「設定」「情報」 pass every rule and carry nothing.
4. Is the copy true? Untrue copy includes 「削除したファイルは復元できません」 on a file the trash can restore, a dialog understating what it deletes, and a count that differs from the rows shown.
5. Is one object called by one name throughout, including names not yet in `voice.terms` in `tokens.json`?
6. Is the empty state's action the right next action for a reader who cannot perform it yet?
7. Does the register the tokens settle (敬体 or 常体) suit this audience? 敬体 on an internal operations screen and 常体 on a public form are the mismatches to look for.

## Reader-fit questions, answered against the running page and `meta.users`

1. Which recorded user group does this screen serve, and does the screen show it: the dense form and the frequent action within one click for a daily intermediate or expert reader, fewer options and a guided path for a first-time or occasional one?
2. For each structural choice (the density, the guidance text, the actions one click away), which recorded fact in `meta.users` justifies it? A choice with no recorded fact behind it is a finding.
3. Does each label predict what lies behind it, in words the recorded group uses (`meta.users[].job` and `voice.terms` are the evidence)? A label that names the feature, the computation or the product where the object or the reader's task belongs is a finding.

## Structure

Keep this section when Structure is ooui; delete it for task and unset.

| Object | Key properties | Actions | Related objects | Collection view | Single view |
|---|---|---|---|---|---|
| {{object}} | {{properties}} | {{actions}} | {{related objects}} | {{path or screen}} | {{path or screen}} |

Task flows kept as a sequence, each with the condition that admits it: {{flows, or none}}

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
