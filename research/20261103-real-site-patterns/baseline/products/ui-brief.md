# UI brief: 家電通販 電気ケトル一覧

Written at product-ui Step 3, before any markup, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: 購入者が、予算内の電気ケトルを容量と評価で比べて 1 台に絞る。
- Surface: saas   (saas = a product screen behind a login; lp = a public landing page)
- Structure: ooui   (ooui = objects first, `references/ooui.md`; task = the order of a procedure; unset = `tokens.json` carries no `meta.structure`)
- Brand area: none   (`none` by default: no logo, letter tile, product name or company name is drawn unless the user specified it)
- Tokens: tokens.json
- Theme: theme.css
- Built files: src/main.tsx, src/App.tsx, src/pages/KettlesPage.tsx, src/components/ui/table.tsx, src/components/ui/native-select.tsx, src/components/ui/label.tsx, src/components/ui/button.tsx, src/lib/utils.ts, src/lib/format.ts, src/data/products.json   (Step 5 skipped: baseline run)
- Controls: wired (価格 filters the rows, 並び順 reorders them, 価格の条件を外す resets 価格; nothing else is clickable)

## Composition

### 電気ケトル `/`

- Job class: decide
- Reader: 購入者, occasional, novice
- Dominant element: the comparison table, with 価格, 容量 and 評価 in aligned columns row by row, because comparing those three within a budget is the purpose
- Second: the 価格 filter, which cuts the set to the reader's budget
- Reading order: heading 電気ケトル and the count → 価格 and 並び順 → a row's 商品名 → its 価格 → its 容量 and 評価 (with レビュー件数)
- Density: the comparison first: all 12 products in one table with no pagination; at 375px the table becomes a list with the same properties per product
- Archetype: single-column
- Grouping: heading and filter bar to table: distance; product to product: rule (table rows); image slot to name: distance
- Constant with the product's other screens: page ground, centred column, heading scale, body type, select and button forms
- Decided for this screen: table as the dominant element, 評価の高い順 as the starting order, price filter steps at 5,000円 and 10,000円, the list form at 375px
- Omitted: category navigation and breadcrumb, the product single view, カートに入れる and お気に入り (no destination screen or behaviour exists in this request), product images (none exist yet; an empty slot is kept), colour swatches (カラー is shown as text), a tile row; the three compared columns keep their visibility for it
- Tile row: none

## Proof

Every figure, testimonial, customer logo and claim the screen shows, with its source. `check_copy.py` (C27) reads this section; a proof-shaped string whose figure or name is not here fails. Empty means the screen shows none.

| Item | Text as shown | Source |
|---|---|---|
| Product records (商品名, 価格, 評価, レビュー件数, 容量, カラー) | the 12 products as recorded, e.g. 4.2 and 312件 for ケトル ミニマル 0.8L | data.json supplied by the user (bench products) |

No testimonial, customer logo, rank or claim is shown.

## States

- Collection `商品`: empty state, reachable only through the 価格 filter: 「条件に合う電気ケトルはありません。」 with the button 「価格の条件を外す」, which sets 価格 back to すべての価格
- Fetch: none. The records are bundled from data.json, so there is no loading or error state
- Form: none. 価格 and 並び順 are selects with fixed options, so there is nothing to validate
- Image slot: each product keeps an empty square where its image will go (the request asks for the space to stay empty)

## Sample data

- Supplied by: the user (data.json, 12 products)
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
| 商品 (電気ケトル) | 商品名, 価格, 容量, 評価, レビュー件数 (also カラー) | none on this screen; filtering and ordering act on the collection | none in this request | `/` 電気ケトル | not in this request: each row shows every property the data holds, so no row opens one |

Task flows kept as a sequence, each with the condition that admits it: none

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
