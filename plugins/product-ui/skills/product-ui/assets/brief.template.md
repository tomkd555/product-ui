# UI brief — {{meta.name}}

Written by product-ui Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: {{purpose}}
- Surface: {{meta.surface}}   (saas = a product screen behind a login; lp = a public landing page)
- Structure: {{meta.structure}}   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Tokens: {{tokens_path}}
- Theme: {{theme_path}}
- Built files: {{built_files}}
- Controls: {{wired|mock}} (wired: every control reaches its destination; mock: links and buttons are placeholders)

## What the reviewer judges

`check_render.py` measures contrast, token discipline, overflow, hit areas, input labels and heading levels before any auditor starts. The reviewer judges the rest:

- overlap and alignment, and whether anything guides the eye
- whether interactive elements do what they look like they do, when the controls are wired
- reflow at 375px
- the dark theme, when `tokens.json` declares `color_dark`
- the copy questions below

## Copy questions, answered against the running page

1. Does each button label name what the button actually does? 「保存」 on a control that publishes, 「送信」 on one that only validates, passes every script.
2. Does each error state the actual cause, in terms the reader can act on?
3. Is each heading specific to this screen? 「概要」「詳細」「設定」「情報」 pass every rule and carry nothing.
4. Is the copy true — 「削除したファイルは復元できません」 on a file the trash can restore, a dialog understating what it deletes, a count that differs from the rows shown?
5. Is one object called by one name throughout, including names not yet in `voice.terms` in `tokens.json`?
6. Is the empty state's action the right next action for a reader who cannot perform it yet?
7. Does the register the tokens settle (敬体 or 常体) suit this audience — 敬体 on an internal operations screen, 常体 on a public form?

## Structure

Keep this section when Structure is ooui; delete it for task and unset.

| Object | Key attributes | Actions | Refers to | Collection view | Single view |
|---|---|---|---|---|---|
| {{object}} | {{attributes}} | {{actions}} | {{related objects}} | {{path or screen}} | {{path or screen}} |

Task flows kept as a sequence, each with the condition that admits it: {{flows, or none}}

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on — in the row or in the single view, after the object is chosen — with creation at the collection?
4. Does one object carry the same name and the same key attributes in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
