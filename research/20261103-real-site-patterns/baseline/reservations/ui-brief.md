# UI brief: 美容室の予約管理

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: 受付スタッフが今日と明日の予約を時刻順に確かめて来店の準備をし、来店したお客様をその場で受付する。
- Surface: saas   (saas = a product screen behind a login; lp = a public landing page)
- Structure: ooui   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: none   (`none` by default: no logo, letter tile, product name or company name is drawn unless the user specified it)
- Tokens: tokens.json
- Theme: theme.css
- Built files: src/main.tsx, src/pages/reservations-page.tsx, src/components/app-header.tsx, src/components/reservation-table.tsx, src/components/reservation-detail.tsx, src/components/status-badge.tsx, src/components/ui/button.tsx, src/components/ui/badge.tsx, src/components/ui/table.tsx, src/lib/reservations.ts, src/lib/utils.ts, src/data/data.json; built output dist/   (Step 5)
- Controls: wired (an in-memory store seeded from src/data/data.json; 受付 changes the record's status in the page; there is no server) (Step 5)

## Composition

### 予約 `/`

- Job class: lookup
- Reader: 受付スタッフ, daily, intermediate
- Dominant element: 今日の予約の表（時刻とお客様名の列）, because the day's arrivals and their check-in are what the reader comes for
- Second: 明日の予約の表, read for preparation (menus and staff)
- Reading order: 見出し「予約」→ 今日の見出しと件数 → 今日の表の時刻・お客様名 → 行の「受付」ボタン → 明日の見出しと表 → それ以降の日の表
- Density: dense rows behind an overview (the day headings with their counts are the overview; one row per reservation)
- Archetype: list-detail (choosing a お客様名 opens the 予約 single view in a pane beside the list at 1024px and wider, and in place of the list below that)
- Grouping: page heading: distance; each day: heading on the ground and distance; each day's table: region (one bordered surface); the single view: region (one bordered surface beside the list); header bar: rule (one bottom border)
- Constant with the product's other screens: header bar with the navigation, button and badge forms, type scale, table form
- Decided for this screen: the today table as the dominant element (time column at text-lg bold), list-detail, day groups in date order, the 受付 action in the row for today's 確定 reservations only
- Omitted: KPI tiles (a lookup screen; the counts sit in the day headings), a staff filter and a search box (twelve rows over three days read in one scroll), a calendar view, 予約の新規作成 (no form exists for it in this request, so the button is left out rather than shown doing nothing), 予約の変更とキャンセル操作 (not part of the reader's job here)
- Tile row: none

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none.

| Item | Text as shown | Source |
|---|---|---|

## States

- Collection `予約（日ごと）`: empty state for a day with no reservation: 「この日の予約はありません」 under the day heading; the whole list empty: 「予約はありません」
- Collection `予約の単体ビュー`: nothing chosen shows no pane (the list takes the full width); a number in the URL that matches no record shows no pane
- Fetch: none. The records come from src/data/data.json, bundled at build time, so there is no loading or error state
- Form: none. 受付 is a single button; it is shown only on today's 確定 rows and changes the status to 来店済み

## Sample data

- Supplied by: the user (benchmark data.json, twelve records over 2026-11-04 to 2026-11-06; today is fixed at 2026-11-04 by the request)
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
| 予約 | 日時（時刻）, お客様名, メニュー, 担当スタッフ, ステータス | 受付（当日・確定のみ） | お客様, 担当スタッフ (no views of their own in this request) | `/` (day groups) | `/?reservation=<予約番号>` (pane beside the list) |

Task flows kept as a sequence, each with the condition that admits it: none

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
