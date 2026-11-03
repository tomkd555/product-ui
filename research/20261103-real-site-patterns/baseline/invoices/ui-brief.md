# UI brief: 請求書発行サービス

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: 経理担当者が請求書ごとの入金状況を確かめ、支払期日を過ぎた請求書とその取引先を見つけて連絡先にたどり着く。
- Surface: saas   (saas = a product screen behind a login; lp = a public landing page)
- Structure: ooui   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: none   (`none` by default: no logo, letter tile, product name or company name is drawn unless the user specified it)
- Tokens: tokens.json
- Theme: theme.css
- Built files: src/App.tsx, src/main.tsx, src/index.css, src/pages/invoice-list.tsx, src/pages/invoice-detail.tsx, src/components/app-shell.tsx, src/components/status-badge.tsx, src/components/ui/*.tsx, src/lib/*.ts   (Step 5)
- Controls: wired (the status filter, the search field, the row links, the breadcrumb link and the clear-filter button all work client-side; no mock action is drawn: creation, payment recording and sending a reminder are left out because nothing backs them) (Step 5)

## Composition

### 請求書一覧 `/`

- Job class: lookup
- Reader: 経理担当者, daily, intermediate
- Dominant element: the invoice table, because the reader comes to read each invoice's status against its client, amount and due date
- Second: the status filter with a count per status, because 期日超過 is the set the reader acts on
- Reading order: page heading 請求書 → status filter (期日超過 and its count) → table rows (取引先, 請求金額, 支払期日, ステータス) → search field
- Density: dense rows behind a filter; all 12 records on one screen at 1280, no pagination
- Archetype: list-detail (the collection view; the single view is its own page)
- Grouping: heading and filter bar: distance on the page ground; table: one region (surface fill with a border), because rows need a common ground against the tinted page; nothing nested inside it
- Constant with the product's other screens: top bar with the object navigation, page width, type scale, status badge forms, amount and date formats
- Decided for this screen: the table dominates; status filter as a toggle group with counts; 発行日 and 担当者 hidden under 768px
- Omitted: KPI tiles (a lookup screen; the counts live in the filter bar), a 新規作成 button and row actions (nothing backs them), pagination (12 records), column sorting (the data already runs in due-date order)
- Tile row: none

### 請求書 `/invoices/:number`

- Job class: lookup
- Reader: 経理担当者, daily, intermediate
- Dominant element: the billed amount with its status and due date, because the reader opens one invoice to confirm whether it is paid and by when
- Second: 請求先 (the contact line), because contacting the client is the next step for an unpaid invoice
- Reading order: breadcrumb 請求書 → heading 請求書 INV-2026-0403 with status → 請求金額 and 支払期日 → 取引先 / 請求先 / 発行日 / 担当者 → 明細 table with 小計, 消費税, 合計
- Density: one column of facts, then the line-item table; one screen at 1280
- Archetype: single-column
- Grouping: summary (amount, due date, status): distance under the heading; facts list: distance; 明細: heading and one region (the table on the surface fill)
- Constant with the product's other screens: top bar, page width, type scale, status badge, amount and date formats
- Decided for this screen: the amount at the top step of the scale; facts as a two-column description list at desktop, one column at 375px
- Omitted: 入金を記録, PDF download, reminder mail (nothing backs them, so they are left out rather than drawn as mock controls); a payment history (no data)
- Tile row: none

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none.

| Item | Text as shown | Source |
|---|---|---|

The screens show no proof. Every figure on them (amounts, dates, counts per status) is a record from `src/data/data.json` or a count of those records.

## States

- Collection `請求書` (list): when the status filter and search match nothing, the table body shows 「該当する請求書はありません」 and a 「絞り込みを解除」 button that resets both
- Collection `明細` (detail): an invoice with no line items in the data shows 「明細はありません」 in place of the table
- Record lookup (detail): a number with no matching record shows the heading 「請求書が見つかりません」 and a link back to the list
- Fetch: none; the records are bundled from `src/data/data.json`, so no loading or error state exists
- Form `検索`: a search field only, filtering as the reader types; no validation runs

## Sample data

- Supplied by: the user (`data.json` from the request), copied to `src/data/data.json`; all 12 records render
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
| 請求書 | 請求書番号, 取引先, 請求金額, 支払期日, ステータス (担当者, 発行日 in the collection at desktop width) | 絞り込み, 検索, 開く | 取引先, 担当者, 明細 | `/` | `/invoices/:number` |

明細 is a part of one 請求書, shown inside its single view; 取引先 and 担当者 are related objects with no views in this build, so they appear as text, not links.

Task flows kept as a sequence, each with the condition that admits it: none

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
