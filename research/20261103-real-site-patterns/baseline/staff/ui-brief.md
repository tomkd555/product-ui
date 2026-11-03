# UI brief: 社内ポータル

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: 社員が同僚を名前や部署で探し、その人の所属と内線番号・メールアドレスを確かめる。
- Surface: saas   (saas = a product screen behind a login; lp = a public landing page)
- Structure: ooui   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: none   (`none` by default: no logo, letter tile, product name or company name is drawn unless the user specified it)
- Tokens: tokens.json
- Theme: theme.css
- Built files: src/App.tsx, src/main.tsx, src/index.css, src/components/app-shell.tsx, src/components/staff-directory.tsx, src/components/employee-detail.tsx, src/components/ui/*.tsx, src/lib/*.ts   (Step 5)
- Controls: wired (the search field, the 部署 select, the row links, the close and back buttons and the clear-filter button all work client-side; each メールアドレス is a mailto link) (Step 5)

## Composition

### 社員名簿 `/`

- Job class: lookup
- Reader: 社員, occasional, intermediate
- Dominant element: the search field, because the reader arrives with a colleague's name in mind and an occasional reader gets one obvious way in
- Second: the result table (氏名, 部署, 役職, 内線番号, メールアドレス), which answers the question for most lookups without opening anything
- Reading order: heading 社員名簿 → search field → 部署 select → table rows → the selected 社員's pane (勤務地, 社員番号 and the contact lines)
- Density: dense rows behind a filter; all 15 社員 on one screen at 1280, no pagination
- Archetype: list-detail. At 1024px and wider the selected 社員 opens in a pane beside the table (`/?employee=<社員番号>`); under 1024px the pane replaces the table, with a back button
- Grouping: heading and filter bar: distance on the page ground; table: one region (surface fill with a border); selected 社員: one region beside the table; nothing nested
- Constant with the product's other screens: top bar with the navigation, page width, type scale, control forms
- Decided for this screen: the search field at the top step of the filter bar (taller, wider); a two-pane layout once a 社員 is chosen; 役職, 内線番号 and メールアドレス hidden from the table under 768px, where the pane carries them
- Omitted: photos and initial tiles (no photos exist, and a letter tile would only decorate), KPI tiles, an org chart, sorting, pagination, a result count (15 rows show at once)
- Tile row: none

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none.

| Item | Text as shown | Source |
|---|---|---|

The screen shows no proof. Every value on it is a record from `src/data/data.json`.

## States

- Collection `社員`: when the search and the 部署 select match nobody, the table body shows 「該当する社員はいません」 and a 「絞り込みを解除」 button that resets both
- Selection: an `employee` parameter that matches no 社員 shows the table with no pane
- Fetch: none; the records are bundled from `src/data/data.json`, so no loading or error state exists
- Form `検索`: a search field and a select, filtering as the reader types or chooses; no validation runs

## Sample data

- Supplied by: the user (`data.json` from the request), copied to `src/data/data.json`; all 15 records render
- Mock data varies names, dates and amounts, and carries no statistic the reader did not ask for.

## What the reviewer judges

`check_render.py` measures contrast, token discipline, overflow, clipped text, hit areas, input labels, text under the minimum size, heading levels, console errors, links without a destination, the viewport width, nested enclosures, spacing steps, emphasis levels and equal tile rows before any auditor starts. The reviewer judges the rest:

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

| Object | Key properties | Actions | Related objects | Collection view | Single view |
|---|---|---|---|---|---|
| 社員 | 氏名, 部署, 役職, 内線番号, メールアドレス (勤務地 and 社員番号 in the single view) | 検索, 部署で絞り込み, 開く, メールを送る (mailto) | 部署, 勤務地 | `/` (table) | `/?employee=<社員番号>` (pane beside the table; its own view under 1024px) |

部署 and 勤務地 are properties shared by many 社員 and have no views of their own in this build.

Task flows kept as a sequence, each with the condition that admits it: none

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
