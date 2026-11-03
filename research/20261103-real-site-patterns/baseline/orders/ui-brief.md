# UI brief: 通販マイページ 注文履歴

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: 購入者が、注文した商品がいつ届くか、届いたかを注文ごとに確かめる。
- Surface: saas   (saas = a product screen behind a login; lp = a public landing page)
- Structure: ooui   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: none   (`none` by default: no logo, letter tile, product name or company name is drawn unless the user specified it)
- Tokens: tokens.json
- Theme: theme.css
- Built files: src/main.tsx, src/App.tsx, src/pages/OrdersPage.tsx, src/lib/utils.ts, src/lib/format.ts, src/data/orders.json   (Step 5 skipped: baseline run)
- Controls: wired (the screen carries no control; nothing is shown that does nothing)

## Composition

### 注文履歴 `/`

- Job class: lookup
- Reader: 購入者, occasional, novice
- Dominant element: each order's 配送状況 line (準備中 / 発送済み / 配達済み / キャンセル済み, with its icon), because the reader opens the screen to learn whether the item has arrived
- Second: the お届け予定日 under it, with the weekday, which answers when the item arrives
- Reading order: heading 注文履歴 → newest order's 配送状況 → its お届け予定日 → its 商品 → 注文日, 注文番号, 数量, 合計金額 → the next order
- Density: dense rows behind an overview: one list of all 8 orders, newest order first, no filter (eight rows need none, and an occasional novice reader gets no control to learn)
- Archetype: single-column
- Grouping: heading to list: distance; order to order: rule (each row holds three lines and a property list, so distance alone would run the rows together); delivery block to property list inside a row: distance
- Constant with the product's other screens: page ground, centred column, heading scale, body type, the 配送状況 wording from the data
- Decided for this screen: dominant 配送状況 line, single-column archetype, newest first, the property list beside the delivery block at desktop and under it at 375px
- Omitted: マイページ navigation and breadcrumb (no destination screen exists in this request), order actions such as 詳細・キャンセル・再購入 (no destination or behaviour exists), a period filter and search (eight orders), product images (the data carries none), a tile row; the delivery line keeps its visibility for it
- Tile row: none

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none.

| Item | Text as shown | Source |
|---|---|---|
| Order records (注文番号, 注文日, 商品, 数量, 合計金額, 配送状況, お届け予定日) | the 8 rows as recorded | data.json supplied by the user (bench orders) |

No testimonial, customer logo, rating or claim is shown.

## States

- Collection `注文`: empty state 「注文はまだありません。」 in place of the list; no next action, since no shopping screen exists in this request
- Fetch: none. The records are bundled from data.json, so there is no loading or error state
- Form: none
- Order without お届け予定日 (キャンセル済み): the お届け予定日 line is left out of that row

## Sample data

- Supplied by: the user (data.json, 8 orders, today 2026-11-03)
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
| 注文 | 配送状況, お届け予定日, 商品, 注文日 (also 注文番号, 数量, 合計金額) | none on this screen | 商品 | `/` 注文履歴 | not in this request: each row already shows every property the data holds, so no row opens one |

Task flows kept as a sequence, each with the condition that admits it: none

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
