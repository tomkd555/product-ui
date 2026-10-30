# UI brief: 販社ポータル V3

Written at product-ui Step 3 before the rebuild of every screen on the branch `feat/compose-v3`, and completed at Step 5: the plan `review-design-lead` conforms each screen to. One Composition block per screen. The shared parts are in `src/components/ui.tsx`: `Section` (a heading on the ground, no enclosure), `Figure` (`size="hero"` for the one dominant quantity of a `monitor` screen, `size="small"` beside it), `FigureRow`, and the styles `.count-filters` (filter buttons that carry a count) and `.facts` (key facts under a title). `Card` stays for a browsed unit recognised by image (the vehicle cards), the comparison tray and a dialog; everywhere else a section sits on the page ground.

## Screen

- Purpose, one sentence: a Honda dealership's staff raise the use of ホンダファイナンス products and exchange with HFC, from one portal that shows them their distance to target, the contracts to act on, the figures to quote and the notices to read.
- Surface: saas
- Structure: ooui
- Tokens: C:/Mycode/ClaudeCode/hansya_Portal_V3-compose/src/tokens.json
- Theme: C:/Mycode/ClaudeCode/hansya_Portal_V3-compose/src/theme.css
- Built files: index.html#/contracts?as=manager
- Controls: wired

## Readers (`meta.users`)

| Group | Frequency | Expertise | Job |
|---|---|---|---|
| 営業スタッフ | daily | intermediate | see this month's distance to the personal target and the contracts near 満期, and decide which customers to call today |
| 店長 | daily | intermediate | see the store's ペネトレーション against target and which products and staff are behind |
| エリアマネージャー | weekly | expert | compare the stores, and check the low ones and the open inquiries |

Every group is daily or weekly and intermediate or expert, so every screen takes the dense form: tables, the frequent action within one click, help behind the `?` icon, guidance in `使い方ガイド` only.

## Composition

Rules that hold on every block: one `hero` figure at most, and only on a `monitor` screen; a `lookup` or `enter` screen shows its counts as `.count-filters` buttons or as a `.facts` line under the title; a section is a `Section` on the ground; a table keeps its hairlines and sits in its section without a panel; spacing uses the three steps the shell gives (within a list 0, between a heading and its content 0.75rem, between sections 2.5rem); the label of a figure names the measure in the reader's words and the scope or period goes in the kicker or the compare line.

### ホーム `/`

- Job class: monitor
- Reader: 営業スタッフ, daily, intermediate; 店長 and エリアマネージャー see the store or area figure in place of the personal one
- Dominant element: `Figure size="hero"`: for 営業スタッフ 「マイ目標まで」 with the value 「あと N件」; for 店長 and エリアマネージャー 「今月のホンダファイナンスペネトレーション」 with the gap to the target on the compare line
- Second: the 要対応 list
- Reading order: hero figure → its compare line → 要対応 → 未読のお知らせ
- Density: one screen at 1280 with no scrolling; at most three rows per list
- Archetype: dashboard as a single column with a supporting pane for the notices from 1024px (`.home-grid`)
- Grouping: distance; rows divided by hairlines (`.rows`); no region
- Constant: the shell, the navigation, the `Updated` line, the help icon
- Decided here: the dominant figure, the two-to-one pane, 「要対応」 as the list's heading with its count
- Omitted: the two KPI tiles, the two panels
- Tile row: none

### 契約 `/contracts`

- Job class: lookup
- Reader: 営業スタッフ daily; 店長 and エリアマネージャー with the extra columns
- Dominant element: the table 契約の一覧, ordered by 満期, with 要対応 marked
- Second: the `.count-filters` bar above it: 「すべて N」「意向未確認 N」「乗り換え N」「3か月以内 N」, each a filter the spec's KPIs applied
- Reading order: filter bar → table → the chart 24か月以内の満期の月別件数 (managers) below
- Density: dense rows, paged at 50
- Archetype: single-column; a row opens the contract page
- Grouping: distance; the filter controls and the count buttons in one row; no region
- Constant: the shell, the table style, the pager
- Decided here: counts as filter buttons; the chart last
- Omitted: the four KPI tiles; the panel around the table
- Tile row: none

### 契約 single `/contracts/:id`

- Job class: enter (the intention) with lookup of the contract's facts
- Reader: 営業スタッフ daily
- Dominant element: the title line's state: 満期 「2027年1月・あと3か月」 and 要対応, with the two actions beside it
- Second: 満期の意向 form
- Reading order: title and state → 満期までの日程 → 満期の意向 → 契約 and お客様 facts → 早期一括返済のシミュレーション
- Density: one column of sections; the facts as `<dl>` in two columns from 1024px
- Archetype: single-column page
- Grouping: distance between sections; the form fields within one section; no panel
- Constant: the shell, the form parts, the confirm dialog
- Decided here: the state in the title line, the dates before the form, the facts as definition lists
- Omitted: the five cards
- Tile row: none

### 車種 `/vehicles`

- Job class: lookup (browse)
- Reader: 営業スタッフ daily, beside a customer
- Dominant element: the category tabs with the vehicle cards (a browsed set recognised by image, the one place `Card` stays) or the table or the scatter under 表示
- Second: the comparison tray (a fixed region, kept)
- Reading order: tabs → view switch → cards → tray
- Density: a grid of cards at 1280, one column at 375
- Archetype: feed
- Grouping: the cards as units; the tray as a region
- Constant: the shell, the card component
- Decided here: the four market KPIs leave this screen; the header gets the link 「市場動向で登録台数を見る」
- Omitted: the KPI tiles
- Tile row: none

### 車種 single `/vehicles/:id`

- Job class: lookup (shown to the customer)
- Reader: 営業スタッフ with a customer; the switch スタッフ向けの情報を表示 adds the staff columns
- Dominant element: the car in its chosen colour (ボディーカラー) with the name and the price range beside it
- Second: タイプと価格 table
- Reading order: title with category marks → colour and image → `.facts` line (登録台数 and 前年比, 価格帯, 主な競合, 掲載車種 of the category) → タイプと価格 → 競合との比較 → 諸元の比較 → おすすめの選び方 → セールストーク (staff) → メーカーサイト
- Density: one column of sections; tables full width
- Archetype: single-column page
- Grouping: distance; the colour buttons in one group; no panel
- Constant: the shell, the comparison tray
- Decided here: the four KPI tiles become the `.facts` line under the title; the image comes first
- Omitted: the tiles; the cards around each table
- Tile row: none

### 市場動向 `/market`

- Job class: lookup (compare)
- Reader: 店長 and エリアマネージャー weekly; 営業スタッフ for a segment
- Dominant element: on セグメント, the segment's Hondaシェア as a `Figure size="small"` pair with 最大の競合 and the mark, above the bar chart; on 全国, the chart メーカー別シェアの推移 with the line 全国のHondaシェア in its heading's count; on 都道府県, the table; on 季節性, the chart
- Second: the table under each chart
- Reading order: tabs → segment control → share figure → chart → table → source line → HFC comments
- Density: dense tables; the comments as a collapsed list
- Archetype: single-column with tabs
- Grouping: distance; the source line directly under its table; no panel
- Constant: the shell, the tabs, the chart frame
- Decided here: the four KPI tiles leave; 「登録台数トップのHonda車」 moves into the 全国 tab's table (the top row is already there)
- Omitted: the tiles; the nine cards
- Tile row: none

### 見積り `/estimates`

- Job class: lookup
- Reader: 営業スタッフ daily
- Dominant element: the table of saved estimates with 見積りを作る as the primary action in the header
- Reading order: primary action → table
- Density: dense rows
- Archetype: single-column
- Grouping: distance; no panel
- Omitted: the panel
- Tile row: none

### 見積り single `/estimates/new`, `/estimates/:id`

- Job class: decide (which plan to propose) with enter (the conditions)
- Reader: 営業スタッフ beside a customer, on a tablet as well
- Dominant element: the chosen product's 月々のお支払い額 (月額料金 for 楽まる) as a `Figure size="hero"` at the top of the result pane, with 実質年率 and the campaign on its compare line
- Second: プランの比較 table
- Reading order: conditions (left pane) → hero payment (right pane) → プランの比較 → 下取り → actions
- Density: a supporting pane from 1024px: the form in one column on the left, the result on the right; stacked at 375
- Archetype: supporting-pane
- Grouping: distance between form groups; the result pane as one section; no panel
- Constant: the form parts, the customer-facing view (お客様向けに表示) which keeps one card per compared plan because the customer browses them side by side
- Decided here: the payment as the dominant figure; the comparison table replaces the per-product cards in the staff view
- Omitted: the six cards of the staff view
- Tile row: none (the hero stands alone; `decide` admits the one figure the decision turns on)

### 金利・キャンペーン `/rates`

- Job class: lookup
- Reader: 営業スタッフ daily
- Dominant element: the table 商品別の実質年率
- Second: the list 実施中のキャンペーン with the heading count 「実施中のキャンペーン N件」 and the filter 14日以内に終了 as a `.count-filters` button with its count
- Reading order: rates table → campaigns → the campaign pane beside the list
- Density: dense
- Archetype: list-detail (the campaign pane)
- Grouping: distance; no panel
- Omitted: the two KPI tiles
- Tile row: none

### お知らせ `/notices`

- Job class: lookup
- Reader: every group, daily
- Dominant element: the list, unread titles bold, 要対応 marked
- Second: the filter row: 種別, 既読状態, and the `.count-filters` buttons 「対象のお客様がいる N」「まもなく終了 N」「要対応 N」
- Reading order: filters → list → the notice pane
- Density: dense rows
- Archetype: list-detail
- Grouping: distance; rows by hairlines; the pane as the detail
- Omitted: the two KPI tiles; the panels
- Tile row: none

### 問い合わせ `/inquiries`

- Job class: lookup
- Reader: 営業スタッフ and 店長 daily
- Dominant element: the list ordered by last update, unread subjects bold
- Second: the state filter as `.count-filters`: 「回答待ち N」「回答あり N」「解決済み N」, and 問い合わせを追加 as the primary action
- Reading order: primary action → state filters → list → pane
- Density: dense rows
- Archetype: list-detail; the form and the inquiry as the pane
- Grouping: distance; no panel
- Omitted: the two KPI tiles; the panels
- Tile row: none

### よくあるご質問・資料 `/library`

- Job class: lookup
- Reader: 営業スタッフ occasional on this screen
- Dominant element: the search field 質問と資料を検索, full width under the title
- Second: the tabs よくあるご質問（N件） and 資料（N件）
- Reading order: search → tabs → topic groups or document table
- Density: a list of questions grouped by topic; the documents as a table
- Archetype: single-column
- Grouping: distance; a question opens in place
- Omitted: the panels
- Tile row: none

### 販売店 `/stores`

- Job class: lookup (compare)
- Reader: 店長 and エリアマネージャー weekly; 営業スタッフ sees the own store's row and the link to its 実績
- Dominant element: for managers the bar chart 販売店の達成率; for an advisor the table
- Second: the table 販売店一覧 with 全販売店 first and the own store marked
- Reading order: period filter → chart → table
- Density: dense
- Archetype: single-column
- Grouping: distance
- Decided here: the four manager KPIs become a `.facts` line under the title (エリア達成率 with 前月比; 販売店数 and 営業スタッフ数); the highest and lowest store are read off the chart
- Omitted: the tiles; the panels
- Tile row: none

### 販売店 single, tab 実績 `/stores/:id`, `/stores/all`

- Job class: monitor
- Reader: 店長 daily; エリアマネージャー weekly; 営業スタッフ for the own store
- Dominant element: `Figure size="hero"` ペネトレーション（全商品）, with the 95%信頼区間 on its compare line
- Second: three `Figure size="small"` in the same `FigureRow`: 前年同期 (or 前年同月), the lowest product named as its own label (「楽まる」 with the compare line 「最も低い商品」), and the contract count against target
- Reading order: period filter → figure row → 商品別のペネトレーション → ペネトレーションの月次推移 → 販売店の比較 (the verdict sentence and its one action first) → 月別の契約明細 → 支払方法の構成 → お客様属性別の商品構成 → the store trend (managers)
- Density: one dense screen with scrolling; each section a chart or a table
- Archetype: dashboard
- Grouping: distance; the verdict line as emphasised text, the analyst detail in a `<details>` (kept, a disclosure is a control)
- Constant: the shell, the tabs, the chart frame
- Decided here: the tile row becomes one hero with three small figures; the cards become sections
- Omitted: the six cards; the equal tiles
- Tile row: the FigureRow above, with the hero dominant

### 販売店 single, tab 目標 `/stores/:id?tab=targets`

- Job class: enter
- Reader: 店長 monthly; エリアマネージャー on 全販売店
- Dominant element: the allocation table with its editable スタンダード目標 inputs and the running total
- Second: the two actions 配分を確定して目標にする and 統計から再計算
- Reading order: `.facts` line (今月の契約件数 with 目標差 and 残りN日, 達成率 with 前月比, 到達した営業スタッフ or 目標未達の販売店 as a `.count-filters` button, エリア内順位) → table → actions → charts
- Density: one table, one column
- Archetype: single-column
- Grouping: distance
- Omitted: the four tiles; the panels
- Tile row: none

### 販売店 single, tab スタッフ `/stores/:id?tab=staff`

- Job class: lookup
- Dominant element: the staff table
- Omitted: the panel
- Tile row: none

### 販売店 single, tab RMコメント `/stores/:id?tab=rm`

- Job class: monitor with enter (the comment)
- Reader: 店長 and エリアマネージャー
- Dominant element: `Figure size="hero"` ペネトレーション（全商品）
- Second: three small figures (楽まる, 残クレ, 目標達成), each with the action 「コメント」 beside its label
- Reading order: header (対象期間, 最終同期, 担当RM) → figure row → 共有中の指標の推移 → RMとのコメント → コメントを追加
- Density: one screen with scrolling
- Archetype: dashboard
- Grouping: distance; comment threads as a list with hairlines
- Omitted: the tiles; the panels
- Tile row: the FigureRow, with the hero dominant

### スタッフ `/staff`

- Job class: lookup
- Reader: 店長 and エリアマネージャー
- Dominant element: the sortable table
- Second: `.facts` line (営業スタッフ N名 with 目標合計, 営業スタッフ平均の達成率 with 中央値) and the `.count-filters` button 「目標未達 N名」
- Reading order: facts and filter → table → 契約件数の分布
- Density: dense
- Archetype: single-column
- Grouping: distance
- Omitted: the four tiles; the panels
- Tile row: none

### スタッフ single `/staff/:id` (マイ目標 for the advisor, the advisor's page for managers)

- Job class: monitor
- Reader: 営業スタッフ daily on the own page; 店長 on an advisor's page
- Dominant element: `Figure size="hero"` 今月の契約件数 with 目標差 on the compare line (and 前月N件 for a manager's view)
- Second: small figures in the same row: 翌月の達成予測 with its 予測範囲, 達成率が最も高い商品 with 店内N位, 安定度 with ばらつき; for a manager's view スタンダード目標 and 店内順位
- Reading order: figure row → tabs → 商品別の目標レンジ → 提案アドバイス (or the trend charts)
- Density: one screen with scrolling
- Archetype: dashboard
- Grouping: distance; tables in sections
- Omitted: the four tiles; the panels
- Tile row: the FigureRow, with the hero dominant

### Common: ログイン `/login`, アカウント・表示設定 `/settings`, 使い方ガイド `/guide`, 404

- Job class: enter (ログイン, 設定); lookup (ガイド)
- Dominant element: ログイン, the form in one card centred on the ground (a dialog-like surface, the one region); 設定, the first form section; ガイド, the four steps as an ordered list
- Reading order: title → sections in order
- Density: one column
- Archetype: single-column
- Grouping: distance; the settings as sections (アカウント, 表示, パスワードの変更) without panels
- Omitted: the panels on 設定 and ガイド
- Tile row: none

## What the reviewer judges

`check_render.py` measures contrast, token discipline, overflow, hit areas, input labels, heading levels, nested enclosures, spacing steps, emphasis levels and equal tile rows before any auditor starts. The reviewer judges the rest:

- the cold-read questions below, from the screenshot, before the dump is read
- overlap and alignment
- whether interactive elements do what they look like they do
- reflow at 375px
- the dark theme (`color_dark` is declared)
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

1. Which recorded user group does this screen serve, and does the screen show it: the dense form and the frequent action within one click for a daily intermediate or expert reader?
2. For each structural choice (the density, the guidance text, the actions one click away), which recorded fact in `meta.users` justifies it? A choice with no recorded fact behind it is a finding.
3. Does each label predict what lies behind it, in words the recorded group uses (`meta.users[].job` and `voice.terms` are the evidence)? A label that names the feature, the computation or the product where the object or the reader's task belongs is a finding.

## Structure

| Object | Key properties | Actions | Related objects | Collection view | Single view |
|---|---|---|---|---|---|
| 契約 | 契約番号, お客様, 商品と契約期間, 月々のお支払い額, 残価, 満期, 意向 | 意向を記録, 意向をクリア, 見積りを作る, ホンダファイナンスに問い合わせる | 見積り, お知らせ, 問い合わせ | `#/contracts` | `#/contracts/:id` |
| 車種 | 車種名, カテゴリー, タイプと価格, 寸法 | 見積りを作る, 比較に追加 | 市場動向, 見積り | `#/vehicles` | `#/vehicles/:id` |
| 市場動向 | メーカー, 車種, セグメント, 都道府県の登録台数 | none | 車種 | `#/market` | a Honda row opens its 車種 |
| 見積り | 番号, 保存日, お客様, 車種, 商品, 支払額 | 見積りを保存, 提案書を印刷, お客様向けに表示 | 契約, 車種, 金利・キャンペーン | `#/estimates` | `#/estimates/:id` |
| 金利・キャンペーン | 商品, 実質年率, 対象車種, 期間 | none | お知らせ, 契約 | `#/rates` | `#/rates/:id` |
| お知らせ | 番号, 種別, 件名, 配信日, 要対応, 既読 | 既読にする, 対応済みにする | 契約, 金利・キャンペーン | `#/notices` | `#/notices/:id` |
| 問い合わせ | 番号, 件名, 状態, 販売店, お客様 | 返信を送る, 解決済みにする, 問い合わせを再開 | 契約 | `#/inquiries` | `#/inquiries/:id` |
| よくあるご質問・資料 | 分類, 質問, 回答; 資料名, 種類, 配布区分 | 問い合わせを追加 | 問い合わせ | `#/library` | in place |
| 販売店 | 店名, 店長, ペネトレーション, 契約件数, スタンダード目標, 達成率 | 配分を確定して目標にする, 統計から再計算, コメントを送る | スタッフ, 契約, 市場動向 | `#/stores` | `#/stores/:id` |
| スタッフ | 氏名, 販売店, 役割, 実績, 目標 | none | 販売店, 契約 | `#/staff` | `#/staff/:id` |

Task flows kept as a sequence, each with the condition that admits it: ログイン (a self-contained procedure); the 見積り conditions form (a fixed input flow whose object, the estimate, is being created).

Structure questions, answered against the running page:

1. Does each root navigation item name an object from the table, as a noun?
2. Does each object in the table have its collection view and its single view, and does choosing an item in the collection open its single view?
3. Does each action sit on the object it acts on (in the row or in the single view, after the object is chosen), with creation at the collection?
4. Does one object carry the same name and the same key properties in every view that shows it?
5. Is every flow that runs as a fixed sequence one of the task flows named above?
