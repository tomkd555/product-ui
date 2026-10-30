# UI brief: 販社ポータル V3, ホーム

Written at product-ui Step 3, before the Home rebuild, and completed at Step 5: the plan `review-design-lead` conforms the screen to.

## Screen

- Purpose, one sentence: the signed-in reader sees how far they are from this month's target and what needs their action today.
- Surface: saas
- Structure: ooui
- Tokens: C:/Mycode/ClaudeCode/hansya_Portal_V3-compose/src/tokens.json
- Theme: C:/Mycode/ClaudeCode/hansya_Portal_V3-compose/src/theme.css
- Built files: index.html#/?as=advisor
- Controls: wired (every figure and row opens the list it counts; the sample accounts are `#/?as=advisor` and `#/?as=manager`)

## Composition

- Job class: monitor
- Reader: 営業スタッフ, daily, intermediate (`meta.users[0]`); the same screen serves 店長 (daily, intermediate) with the store figure in place of the personal one
- Dominant element: the one figure the reader acts on this month. For 営業スタッフ, 「マイ目標まで あと N件」. For 店長 and エリアマネージャー, 「今月のホンダファイナンスペネトレーション」 with the gap to the target on the line under it. It is the purpose: the portal exists to raise that figure.
- Second: the 要対応 list, the rows the reader opens next
- Reading order: the figure → its comparison line → 要対応 → 未読のお知らせ
- Density: one screen at 1280 with no scrolling; the two lists hold at most three rows each
- Archetype: dashboard, as a single column with a supporting pane for the notices from 1024px
- Grouping: hero figure separated from the lists by distance; 要対応 and 未読のお知らせ as two sections on the ground with a heading each; rows inside a list divided by hairlines; no region
- Constant with the product's other screens: the shell, the navigation, the `Updated` line, the help icon beside ペネトレーション, the type scale
- Decided for this screen: the dominant figure, sections on the ground in place of panels, the two-to-one supporting pane
- Omitted: the panel borders and shadows around the lists; the second KPI tile (the store's penetration, for an advisor, moves into the comparison line); the computation words in the figure's label
- Tile row: none

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

1. Does each button label name what the button actually does?
2. Does each error state the actual cause, in terms the reader can act on?
3. Is each heading specific to this screen?
4. Is the copy true?
5. Is one object called by one name throughout, including names not yet in `voice.terms` in `tokens.json`?
6. Is the empty state's action the right next action for a reader who cannot perform it yet?
7. Does the register the tokens settle (敬体) suit this audience?

## Reader-fit questions, answered against the running page and `meta.users`

1. Which recorded user group does this screen serve, and does the screen show it: the dense form and the frequent action within one click for a daily intermediate or expert reader, fewer options and a guided path for a first-time or occasional one?
2. For each structural choice (the density, the guidance text, the actions one click away), which recorded fact in `meta.users` justifies it? A choice with no recorded fact behind it is a finding.
3. Does each label predict what lies behind it, in words the recorded group uses (`meta.users[].job` and `voice.terms` are the evidence)? A label that names the feature, the computation or the product where the object or the reader's task belongs is a finding.

## Structure

| Object | Key properties | Actions | Related objects | Collection view | Single view |
|---|---|---|---|---|---|
| 契約 | 満期, 意向, 商品 | 意向を記録 | お客様, 販売店 | `#/contracts` | `#/contracts/:id` |
| 問い合わせ | 状態, 最終更新 | 返信 | お客様 | `#/inquiries` | `#/inquiries/:id` |
| お知らせ | 種別, 要対応, 公開日 | 既読にする | 対象のお客様 | `#/notices` | `#/notices/:id` |
| 販売店 | ペネトレーション, 目標差 | 目標を設定 | スタッフ, 契約 | `#/stores` | `#/stores/:id` |

Task flows kept as a sequence, each with the condition that admits it: none on this screen.

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
