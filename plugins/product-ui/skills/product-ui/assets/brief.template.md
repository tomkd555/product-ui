# UI brief — {{meta.name}}

Written by product-ui Step 5. This is the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: {{purpose}}
- Surface: {{meta.surface}}   (saas = a product screen behind a login; lp = a public landing page)
- Tokens: {{tokens_path}}
- Theme: {{theme_path}}
- Built files: {{built_files}}
- Controls: {{wired|mock}} (wired: every control reaches its destination; mock: links and buttons are placeholders)

## What the reviewer judges

Everything the scripts cannot: overlap and alignment, whether anything guides the eye, whether interactive elements do what they look like they do (when the controls are wired), reflow at 375px, the dark theme when `tokens.json` declares `color_dark`, and the copy questions below. Contrast, token discipline, overflow, hit areas, input labels and heading levels are measured by `check_render.py` before any auditor starts.

## Copy questions, answered against the running page

1. Does each button label name what the button actually does? 「保存」 on a control that publishes, 「送信」 on one that only validates, passes every script.
2. Does each error state a cause the reader can act on, rather than a plausible one?
3. Is each heading specific to this screen? 「概要」「詳細」「設定」「情報」 pass every rule and carry nothing.
4. Is the copy true — 「削除したファイルは復元できません」 on a file the trash can restore, a dialog understating what it deletes, a count that does not match the rows shown?
5. Is one object called by one name throughout, including names not yet in `voice.terms` in `tokens.json`?
6. Is the empty state's action the right next action for a reader who cannot perform it yet?
7. Does the register the tokens settle (敬体 or 常体) suit this audience — 敬体 on an internal operations screen, 常体 on a public form?
