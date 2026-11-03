# UI brief: サポート窓口

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: サポート担当者が未対応の問い合わせを受付の古い順に開き、その場で返信する。
- Surface: saas   (saas = a product screen behind a login; lp = a public landing page)
- Structure: ooui   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: none   (`none` by default: no logo, letter tile, product name or company name is drawn unless the user specified it)
- Tokens: tokens.json
- Theme: theme.css
- Built files: src/main.tsx, src/pages/inbox-page.tsx, src/components/app-header.tsx, src/components/inquiry-table.tsx, src/components/inquiry-detail.tsx, src/components/reply-form.tsx, src/components/status-badge.tsx, src/components/ui/button.tsx, src/components/ui/badge.tsx, src/components/ui/table.tsx, src/components/ui/tabs.tsx, src/components/ui/textarea.tsx, src/components/ui/label.tsx, src/lib/inquiries.ts, src/lib/utils.ts, src/data/data.json; built output dist/   (Step 5)
- Controls: wired (an in-memory store seeded from src/data/data.json; 返信 records the reply in the page and moves the inquiry to 返信待ち; there is no server) (Step 5)

## Composition

### 問い合わせ `/`

- Job class: lookup
- Reader: サポート担当者, daily, expert
- Dominant element: 未対応の問い合わせの表、受付の古い順, because the oldest unanswered inquiry is the one the reader opens next
- Second: 開いた問い合わせの単体ビューと返信欄
- Reading order: 見出し「問い合わせ」→ ステータスの切り替え（未対応と件数）→ 表の先頭行の件名 → 単体ビューの件名と属性 → 返信欄と「返信」ボタン
- Density: dense rows behind a filter (the status tabs with their counts are the filter; one row per inquiry)
- Archetype: list-detail (choosing a 件名 opens the 問い合わせ single view in a pane beside the list at 1024px and wider, and in place of the list below that)
- Grouping: page heading and status tabs: distance; the table: region (one bordered surface); the single view: region (one bordered surface beside the list); inside the single view, attributes and reply: distance and one rule; header bar: rule (one bottom border)
- Constant with the product's other screens: header bar with the navigation, button, badge, tab and form-field forms, type scale, table form
- Decided for this screen: the 未対応 tab open by default, rows sorted by 受付日時 ascending with a toggle on the column header, list-detail, the reply form in the single view
- Omitted: KPI tiles (a lookup screen; the counts sit on the status tabs), search and category filter (twelve inquiries fit one screen), 担当者の割り当てとステータスの手動変更 (not part of the reader's job here), the inquiry body and the message thread (data.json carries no body; see the TODO in src/components/inquiry-detail.tsx), 新規作成 (inquiries arrive from customers; the reader does not create them)
- Tile row: none

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none.

| Item | Text as shown | Source |
|---|---|---|

## States

- Collection `問い合わせ（ステータスごと）`: empty state per tab: 「未対応の問い合わせはありません」 and the same form for each status; 「すべて」 empty: 「問い合わせはありません」
- Collection `問い合わせの単体ビュー`: nothing chosen shows no pane (the list takes the full width); a number in the URL that matches no record shows no pane
- Fetch: none. The records come from src/data/data.json, bundled at build time, so there is no loading or error state
- Form `返信`: validation on submit; an empty reply shows 「返信を入力してください。」 under the field (role="alert", aria-invalid, aria-describedby); after a valid submit the reply appears under the 「返信」 heading in the single view, the field clears and the status becomes 返信待ち

## Sample data

- Supplied by: the user (benchmark data.json, twelve records received 2026-11-01 to 2026-11-03; today is fixed at 2026-11-03 by the request)
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
| 問い合わせ | 件名, お客様, 受付日時, ステータス, 担当者 | 返信（単体ビューで） | お客様, 担当者 (no views of their own in this request) | `/` (status tabs) | `/?inquiry=<問い合わせ番号>` (pane beside the list) |

Task flows kept as a sequence, each with the condition that admits it: none

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
