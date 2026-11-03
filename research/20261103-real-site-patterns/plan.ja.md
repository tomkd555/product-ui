# 計画: 実在サイトのコンポーネントを標本にして画面を組む

時点: 2026-11-03。対象: `tomkd555/product-ui`（product-ui 1.2.0）。スキルのルートを `S = plugins/product-ui/skills/product-ui`、エージェントの置き場を `A = plugins/product-ui/agents` と書く。

## 結論

- **足りないもの**: 現行の product-ui は、画面から削る規則（ban-list と S・C・ST・R の検査）と、画面の構成（役割、支配要素、読む順序、容器の種類）を決める仕組みを持つ。容器の中に何を載せるか（スロット）と、どの実例に倣うかを決める仕組みは持たない。そのため、名前と数字が 1 つずつしかないカードもすべての検査を通る。文言を削る規則が強く働くほど、カードはかえって空になる。
- **方針**: 実在のデザインシステムとサイトから採ったコンポーネントの「標本」と、それを抽象化した「パターン」をスキルに持たせる。パターンは、スロットの一覧、順序、上限、ラベルの形、出典を記録する。brief の各セクションにパターン ID を書き、パターンの選択と骨組みの生成はスクリプトが受け持つ。出力がパターンに従っているかは検査で確かめる。この計画でいう「学習」は、採取、抽象化、パターン集への登録の 3 工程を指す。モデルの再学習は含めない。
- **関連リポジトリの結論**: コンポーネントの情報内容を構造化データとして取り出す公開ツールは見つからなかった。情報内容とは、どの項目をどの順で載せ、どう名付けるかのことである。見つかった抽出ツールと DESIGN.md 集は、色、文字、余白、角丸を扱うものだった。このため、記録の形式は senlindesign/proof に、採取の部品は product-ui 自身の `cdp.js` に、模範例と台帳の運用は prose-lint に倣う。
- **段階**: Phase 0〜6 の 7 段階で進める（基準線、パターンの書式と初期パターン、選択と骨組み、準拠の検査、ラベル、採取ツールと領域パック、較正）。Phase 3 を終えた時点で、情報のないカードが機械的に止まる。
- **オーナーが決めること**: D1〜D5 の 5 件（採取してよい対象、残す標本の範囲、準拠検査の強さ、最初の領域パック、prose-lint との接続）。

## 1. 現状の診断

### 1.1 決まっているものと決まっていないもの

| 決定 | 現行で決める場所 | 状態 |
|---|---|---|
| 色、文字、余白、角丸、影、動き | `tokens.json` → `theme.css`（T1〜T22） | 決まる |
| 文体、操作の語 | `tokens.json` の `voice`（C1〜C32） | 決まる |
| 利用者のグループ | `meta.users`（T18） | 決まる |
| 画面の役割、支配要素、読む順序、密度、容器の種類 | `ui-brief.md` の Composition と `S/references/composition.md`（R12〜R15） | 決まる |
| 文言が存在してよいか | `S/references/ban-list.md`（ST1〜ST10） | 決まる |
| **容器の中身**: 一覧の 1 行、カード、詳細の見出し領域に載せる項目と、その順序、強弱、操作の数 | 決める場所がない。`S/references/components.md` にある例は shadcn のフォームとセクションの 2 つで、`composition.md` が決めるのは容器の種類まで | **未決** |
| **ラベルの正解形**: コレクションの見出し、列見出し、状態の語彙、空状態の文 | C18〜C21 が検出するのは禁止形（汎用語、機能名、重複、製品名）だけ | **禁止形のみ** |
| **倣う実例** | `meta.reference` が扱うのは DADS と SmartHR の 2 つ。それ以外の製品は「スクリーンショットと説明文から」（SKILL.md Step 1）で、構造を取り出す道具はない | **手作業** |
| **選択の再現性** | 部品は生成時に判断して選ぶ。同じ brief から同じ部品が出る保証はない | **非決定的** |

### 1.2 情報のないカードがすべての検査を通る理由

例として、見出し「今月の売上」、数値「¥1,234,000」、キャプション「前月比で推移を確認できます」というカードが 4 枚並ぶ画面を考える。

- S11 と R12 は、カードが入れ子になっていなければ通す。R15 は、plan の job class が `monitor` なら通す。
- ST 系の検査はキャプションを削らせる。削るとカードには見出しと数字だけが残り、検査はすべて通る。
- 「タイルは比較を 1 つ持つ」という規則は `composition.md` にあるが、判定は Step 5 のレビュアーの読み取りに任されている。機械の検査はない。
- 一覧の行が名前だけでも、載せるべき項目の基準がないので検出できない。

現行の検査が問うのは「載っているものが悪いか」で、「載るべきものが載っているか」は問わない。今回の改善では後者を、パターンという外部の基準によって問えるようにする。

### 1.3 流用できる既存の部品

- `S/scripts/render/cdp.js`: 任意の URL を headless Chrome で描画し、DOM と計算済みスタイルのほか、`boxes`、`gaps`、`repeatGroups`（繰り返す兄弟要素の群）を書き出す。採取ツールの土台にする。
- `S/scripts/render/check_render.py`: dump を測る。パターン準拠の描画検査（R42 以降）はここに足す。
- `S/assets/brief.template.md` と `check_render.py --plan`: 機械が brief を読む経路がすでにあり、Job class の読み取りに使っている。パターン ID も同じ経路で読める。
- `S/references/ooui.md` のオブジェクト表（Key properties、Actions）: パターンのスロットに割り当てる項目の出どころにする。
- `S/scripts/lookup/`（ui-ux-pro-max 由来）: 検索の仕組みは流用できる。中身は配色とスタイルが中心で、コンポーネントの中身は持たない。

## 2. 関連リポジトリの調査

### 2.1 作者のリポジトリ: prose-lint

prose-lint は文章について、今回コンポーネントについてしたいことを先に実現している。

| prose-lint の仕組み | product-ui で対応させるもの |
|---|---|
| `references/exemplars-japanese.md`: 機関や賞が良い文章と認めた 18 段落を原文のまま引き、何を取るか（文の始め方と終わり方、語の選び方、つなぎ方）を注記する | パターンの標本: 実在のコンポーネントを出典付きで記録し、何を取るか（スロット、順序、強弱、ラベルの形）を注記する |
| 文体（`business`、`paper` など）を最初に決める。呼び出し元のスキルは `style=<name>` で渡せる | 領域パック（業務 SaaS、EC、予約など）を Step 0 で決め、パターン選択の入力にする |
| register: Pattern、Instead、Why の 3 列の表に、却下した言い回しを 1 行ずつ足す | ラベル台帳: 却下した UI ラベルを同じ 3 列で足し、`check_copy.py` が読む |
| 翻訳調の 13 行は、人が書いた 83 文書で測ってから採用した | 新しい検査は実在サイトの標本で誤検出率を測り、それから error にする |
| 新しい文脈で起動した読み手のエージェントが、模範例と照らして読む | Step 5 のレビュアーに標本を渡し、「この部品は標本の何に倣ったか」を問う |

接続の候補: product-ui の Step 4 は、文章の形をした文言を `copy-prose.md` に書き出し、textlint にかけている。この工程を prose-lint に `style=business` で渡す形にする（置き換えるか併用するかは D5）。UI ラベルのような短い語は prose-lint の対象外なので、ラベルの検査は product-ui に置く。

### 2.2 外部のリポジトリとツール

「中身」の列は、部品が載せる項目、その順序、名付け方を記録しているかを示す。

| 分類 | リポジトリ・ツール | 記録するもの | 中身 | product-ui での扱い |
|---|---|---|---|---|
| 記録形式 | [senlindesign/proof](https://github.com/senlindesign/proof)（MIT） | 実在ページ 410 件の調査から作った、節ごとの知識ファイル。パターンごとに When to use、Execution（各セルに何を載せるか）、Variants、When not to use、Evidence（倣ったサイト名）、Evidence status を持つ。19 件の golden set で結果を確かめる | あり。ただしランディングページの節に限る（README に "Not for: app screens and dashboards"） | **記録形式を取り入れる**。調査元の Mobbin は規約で AI での利用を制限しているので、proof のデータ自体は使わない |
| 採取 | [dembrandt](https://github.com/dembrandt/dembrandt)（MIT） | 計算済みスタイルから色、文字、余白とボタン等の見た目を取り、DTCG、DESIGN.md、Tailwind v4 `@theme` で出力する | なし | 採取には使わない。README の「規約が自動アクセスを認めるサイトか自分のサイトにだけ使う」「第三者のブランドの再現に使わない」は、採取の方針として取り入れる |
| 採取 | [designlang](https://github.com/Manavarya09/design-extract)（MIT） | ページを 30 項目の特徴ベクトルにしてコーパスと比べる（`dna`）。CTA の動詞一覧と `anatomy.tsx` も出す | 浅い。カードのスロットは heading、description、media、footer の真偽値だけ（`src/extractors/component-anatomy.js`） | 欠損値を null のまま残し、特徴の組に版番号を付ける規則を取り入れる |
| 書式 | [google-labs-code/design.md](https://github.com/google-labs-code/design.md)（Apache-2.0） | YAML のトークンと決まった節。CLI で lint、diff、export ができる | なし。component の属性は色、文字、角丸、余白、寸法 | パターンの書式には使えない |
| DESIGN.md 集 | [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)、[kzhrknt/awesome-design-md-jp](https://github.com/kzhrknt/awesome-design-md-jp)（610 サイト）、[plugin87/ux-ui-agent-skills](https://github.com/plugin87/ux-ui-agent-skills)（いずれも MIT） | 実在サイトのトークン | なし、または浅い | パターンの出典にはしない |
| 部品の索引 | [component.gallery](https://component.gallery/)、[Open UI component matrix](https://open-ui.org/research/component-matrix/) | 60 種の部品名と別名、95 のデザインシステムへのリンク | なし | 部品名をそろえるため、また各デザインシステムの anatomy の文書を探すための索引にする |
| コード集 | shadcn 系のレジストリ、[21st.dev Magic MCP](https://github.com/21st-dev/magic-mcp) | shadcn 系の部品のコード | なし | **使わない**。出力が互いに似る原因そのものである |
| 有料の参照 | [Refero MCP](https://doc.refero.design/mcp/tools)、[Mobbin MCP](https://docs.mobbin.com/mcp/features) | 画面の画像、タグ、説明文 | 一部（タグと文章） | 使う場合も brief を書くときの参照にとどめ、保存しない。Mobbin の規約（2026-05-16 施行）は、生成 AI の学習、評価、索引作成と派生物の作成に自動ツールを使うことを禁じている |
| データセット | [WebUI](https://uimodeling.github.io)（40 万ページ。アクセシビリティツリーと計算済みスタイルを含む） | 研究向けの利用条件 | 構造を取り出せる | 較正の候補。利用条件を確かめてから使う |
| データセット | [Web Data Commons schema.org Table Corpus](https://webdatacommons.org/structureddata/schemaorgtables/) | サイトが公開する実体の項目と出現率（例: Product の `name` が 99%、`offers` が 87%） | 項目の事前分布として使える | 領域パックで「この対象の行には普通何が載るか」を決める根拠の一つ。研究目的という条件がある |
| データセット・変換 | WebSight、Design2Code、screenshot-to-code | 合成ページ、評価用データ、画像からのコード生成 | なし | **使わない**。WebSight は LLM が生成したページの見た目そのものである |

まとめると次の 4 点になる。

1. 部品の中身を構造化して持つ公開ツールはない。そこは product-ui が自作する。
2. 記録の形は proof に倣う。
3. 採取は `cdp.js` を拡張して実現し、新しい外部ツールは入れない。
4. 情報源は、許可が明確な範囲に限る（D1）。

### 2.3 デザインシステムが決めている部品の中身

公開されているデザインシステムの文書は、部品の中身について次の 5 点で一致する。どれも `composition.md` にはまだ書かれていない。

| 規則 | 出典 |
|---|---|
| 1. 各項目は、人が読める主識別子（そのオブジェクトの名前）を 1 つ必ず持つ。機械が振った ID は主識別子にしない | SmartHR「よくあるリスト」（オブジェクト名は必須）、NN/g "Data Tables"（先頭列は人が読める識別子）、Primer DataTable（row header）、DADS カード（タイトルは必須）、Salesforce compact layout（先頭の項目を太字で上に出す） |
| 2. 主要な属性を少数、固定の組で持つ。選ぶ基準は、利用者が識別や判断に使う属性である | Salesforce highlights panel は最大 7、HubSpot data highlights は 4、Baymard の商品一覧は必須 5 項目に分類固有の 1〜3 項目、SmartHR は全行で同じ種類と数の項目 |
| 3. 項目は詳細へのリンクにする。項目全体がリンクなら、その中に別の操作を置かない | SmartHR、DADS リソースリストとカード、Carbon の clickable tile |
| 4. 操作の数に上限を置く。行に出す操作は詳細画面にも置く | Polaris（shortcut actions）、SmartHR（テーブルの操作は 3 つまで）、DADS（カードの機能ボタンは 2 つまで） |
| 5. コレクションの見出しは対象の名前にし、表示形式の名前は入れない。部分集合を出すときは部分集合を名指す | Polaris（"Orders"、"Popular products this week"）、SmartHR（「一覧」を付けない） |

各システムの具体的なスロットは付録 A にまとめた。上限の数（7、4 など）は各システムの慣例である。中身を埋めた部品と空の部品を比べた統制実験は見つからなかった。

## 3. 設計

### 3.1 標本とパターンの二層

- **標本（specimen）**: 実在のコンポーネント 1 件の記録。出典 URL、取得日、ビューポート幅、セレクタ、スロットの並び（役割と値の型）、強弱の段位（項目の中での相対順位）、ラベルの形を持つ。画像と本文はリポジトリに入れない（D2）。
- **パターン（pattern）**: 同じ種類の標本 2 件以上、またはデザインシステムの文書の明記から抽象化した仕様。スロット、必須か任意か、順序、上限、強弱、ラベルの形、適用条件、使わない場面、出典、Evidence status を持つ。Evidence status は `documented`（文書に明記）、`cross-specimen`（複数の標本から推論）、`inferred`（このスキルの推論）の 3 段で、proof の形式に倣う。

生成が読むのはパターンだけで、標本は根拠として残す。標本から見た目の値（色、フォント、px）を写すことはない。

### 3.2 パターンの書式

`S/patterns/<id>.yaml` に 1 パターンずつ置く。例を示す。

```yaml
id: collection.row.resource        # 名前で探す一覧の 1 行
version: 1
kind: collection-row
fits:
  content: homogeneous-records
  job: [lookup, monitor]
  compare_by_property: false       # 属性を横に並べて比べるなら collection.table.index
not_for: 属性を列で比べる一覧
slots:
  - id: media
    required: false
    when: 画像が 1 件を選ぶ助けになる対象に限る
  - id: name
    required: true
    role: identifier               # オブジェクト表の主識別子
    emphasis: 1                    # 行の中で最も強い
    link: single-view
  - id: info
    required: true
    count: 1..3                    # 全行で同じ種類と数
    source: object.key_properties  # brief の順位の上位から入れる
    label_form: "{label}：{value}" # 値だけでは意味が曖昧なときに限る
  - id: trailing
    required: false
    accepts: [status, count, time]
  - id: action
    required: false
    max: 1
    only_if: 行に詳細画面がない
rules:
  - 行全体がリンクなら、行の中に操作を置かない
  - 並べ替えや絞り込みに使った属性は、行に出す
labels:
  collection_heading: object-name  # 「一覧」を付けない。部分集合なら部分集合を名指す
  empty: "{object}はありません。"
  empty_filtered: "該当する{object}はありません。"
evidence:
  - SmartHR よくあるリスト: https://smarthr.design/products/design-patterns/smarthr-list/
  - Polaris ResourceItem: https://github.com/Shopify/polaris/tree/main/polaris.shopify.com/content/components/lists
  - DADS リソースリスト: https://design.digital.go.jp/dads/components/resource-list/
  - NN/g List Entries: https://www.nngroup.com/articles/list-entries/
evidence_status: documented
```

`S/patterns/index.yaml` は決定表として、内容の種類、job class、属性で比べるか、画像で識別するかの組み合わせからパターン ID を 1 つ引けるようにする。

### 3.3 選択を決定的にする

1. brief の Composition で、セクションごとに `内容:` と `対象:` を書く。`内容:` には下の語彙から 1 つ選び、`対象:` には OOUI 表のオブジェクトを書く。
   - 内容の語彙: `homogeneous-records`（同種の記録の集合）、`single-record`（1 件の記録）、`heterogeneous-items`（異種の項目を眺める）、`measures`（監視する量）、`tasks`（手続きの進み具合）、`form`（入力）、`products`（商品）
2. `S/scripts/patterns/resolve.py ui-brief.md` が決定表を引き、パターン ID を brief に書き込む。決定表で 1 つに決まらないときは推測で選ばず、足りない条件を示して止まる。止まったら Step 3 で利用者に 1 問だけ聞く。
3. 同じスクリプトが、オブジェクト表の Key properties をスロットに割り当て、その結果をスロット割当表として brief に書く。割り当ての規則は固定とする。主識別子は `name` に、状態の属性は `trailing` に入れ、残りは brief に書かれた順位の上位から `info` の上限まで入れる。順位は brief の作成時に、利用者の job を根拠にして書く。スクリプトはその順位を機械的に切るだけである。
4. `S/scripts/patterns/scaffold.py` がスタックごとの骨組みを出力する。各要素には `data-pattern="collection.row.resource"` や `data-slot="name"` を付ける。生成の役目は、骨組みのスロットにデータと文言を入れることに限る。スロットを足すか削るときは、先に brief を変える。

決定性が及ぶ範囲は、同じ brief から同じパターン ID、同じスロット割当、同じ骨組みが出るところまでとする。文言と見た目の値は従来どおり `voice` と tokens の層で決まる。ピクセル単位の同一性は目標にしない。

### 3.4 brief テンプレートの変更

Composition の各画面ブロックに `Sections` 行を足す。

```
- Sections:
  - {見出し}: 内容 {homogeneous-records|…}; 対象 {オブジェクト}; 比較 {yes|no}; パターン {id（resolve.py が書く）}
```

新しい節 `## Slots` にスロット割当表を置く。

| セクション | パターン | スロット | 割り当てる項目 | 根拠（`meta.users` の job） |
|---|---|---|---|---|

Step 5 のレビュアーには、内容の質問を 3 問足す。

1. 各コレクションの 1 項目を見て、利用者（`meta.users`）はその項目を開かずに、探している 1 件を見分けられるか。
2. 各スロットに入った項目は、スロット割当表の根拠と結び付いているか。結び付かない項目は削り、足りない項目は足す。
3. 各部品はどのパターンのどの出典に倣ったか。パターンから外れた点があれば、その理由は brief に書かれているか。

### 3.5 準拠の検査

ソースを読む検査は、新しいスクリプト `S/scripts/check_pattern.py` に置く。

| ID | 重さ | 検出するもの |
|---|---|---|
| PT1 | error | `data-pattern` の付いた要素に、パターンの必須スロット（`data-slot`）が欠けている |
| PT2 | error | 容器（カード、表、一覧の行、詳細の見出し領域）に `data-pattern` がない。または brief にない ID が付いている |
| PT3 | warning | スロットの順序がパターンと違う |
| PT4 | error | 上限を超えている（行の操作、カードの機能ボタン、`info` の数） |
| PT5 | error | 全体がリンクの項目の中に、別のリンクやボタンがある |
| PT6 | warning | スロット割当表にない項目がスロットに入っている |

描画を測る検査は `check_render.py` に足す。`cdp.js` の dump に `data-pattern` と `data-slot` を書き出すようにする。

| ID | 検出するもの |
|---|---|
| R42 | 項目の中で `name` スロットが最も強くない（文字サイズと太さの組で 1 位になっていない） |
| R43 | 同じコレクションの行どうしで、`info` の種類と数がそろっていない |
| R44 | 数値の列が右揃えになっていないか、等幅数字（`tabular-nums`）になっていない |
| R45 | 表の空セルに「-」「x」や絵文字が入っている（SmartHR の、入力できない項目の「-」は除く） |
| R46 | 描画された項目で、必須スロットの値が空になっている（空文字、プレースホルダー） |

しきい値と重さは Phase 6 の較正で確定させる（D3）。

### 3.6 ラベル

パターンの `labels` 節に、2.3 の出典にある正解形を持たせる。

- **コレクションの見出し**: 対象の名前（「請求書」）。「一覧」は付けない。部分集合を出すときは部分集合を名指す（「支払期日を過ぎた請求書」）。
- **列見出し**: オブジェクト表の属性名。1 列に 1 種類の値を入れる。状態の列は「ステータス」とし、状態の列が複数あるときは「〇〇状況」にする。「状況」「状態」だけの見出しは使わない（SmartHR「よくあるテーブル」）。
- **状態バッジ**: 1 語で書く（複雑な状態に限り 2 語）。形容詞か完了の形（「返金済み」）を使い、領域ごとに語彙を固定する。1 つの状態に 1 色を割り当て、リンクにはしない（Polaris Badge、GOV.UK Tag）。
- **ページの主操作**: 動詞と名詞で書く。ページの対象と同じ名詞は省ける（Polaris）。
- **空状態**: 初めて使うときは「{対象}はありません。」と、見出しに合う操作を出す。絞り込みの結果が空のときは「該当する{対象}はありません。」とし、作成ボタンは出さずに条件を残す（SmartHR、Stripe Apps、Atlassian、Primer）。
- **パンくず**: リンク先のページの見出しと同じ語を使う（Polaris）。

検査と設定:

| ID・項目 | 重さ | 内容 |
|---|---|---|
| `voice.status` | — | `tokens.json` に、オブジェクトごとの状態語彙の表を足す。形式は `validate_tokens.py` の T23 で検査する |
| C33 | warning | コレクションの見出しが「一覧」で終わる |
| C34 | error | 状態スロットのラベルが `voice.status` にない |
| C35 | warning | 列見出しが「状況」「状態」だけ |
| C36 | warning | 空状態の文がパターンの形（初回と絞り込み）に合わない |
| C37 | warning | ラベル台帳の行に一致した |

ラベル台帳は `S/assets/label_register.ja.md` に置き、prose-lint の register と同じく Pattern、Instead、Why の 3 列で書く。利用者が却下したラベルを 1 行ずつ足すと、次の検査から効く。

### 3.7 採取: 実在サイトから標本を作る

- `cdp.js` に `SPECIMEN=<selector>` を足す。指定した要素、または `repeatGroups` が見つけた繰り返しの兄弟群について、部分木を書き出す。書き出すのは、要素ごとの役割（見出し、本文、画像、ボタン、リンク）、値の型（日付、金額、件数、状態語、人名、ID の形、自由文）、文字サイズと太さの段位、余白の段数、並び順である。
- `S/scripts/harvest/abstract.py` が dump から標本 YAML の下書きを作る。値は相対値（項目の中での強弱の順位、余白の段数）で持ち、色、フォント、ブランドの値は持たない。本文は持たず、値の型だけを残す。列見出しのような短いラベルをラベルの形として残すかは D2 で決める。
- 同じ構造を示す標本が 2 件以上集まったら、パターン候補（`cross-specimen`）にする。人が承認してから `S/patterns/` に入れる。
- 採取の対象は次の順に広げる（D1）。
  1. 公開されたデザインシステムの文書とデモ（DADS、SmartHR、GOV.UK、Primer、Carbon、Polaris）。ライセンスと規約が明確で、引用と出典の記載で足りる。Polaris の文書の再利用条件は採取の前に確かめる
  2. 利用者自身のプロダクト
  3. OSS のアプリケーションのデモ
  4. 一般の商用サイト。規約が自動アクセスを認める範囲で、構造だけを採る
- 採取に使わないもの: Mobbin のような規約で AI での利用を禁じる集積、WebSight、shadcn 系のレジストリ。
- リポジトリに保存しないもの: スクリーンショット、ロゴ、画像、本文、ブランドの色と書体。スクリーンショットは gitignore したキャッシュに置き、リポジトリには SHA-256 だけを残す。

## 4. 段階

依存関係: Phase 0 → 1 → 2 → 3 の順に進める。Phase 4 は Phase 1 の後なら並行できる。Phase 5 は dump の拡張を共有するので Phase 3 の後に置く。Phase 6 は最後に置く。版は、Phase 1〜3 を 1.3.0、Phase 4〜6 を 1.4.0 とする。

### Phase 0: 基準線

- 作業: 中立な領域で、評価用の要求を 6 件作る。請求書の一覧と詳細、予約の一覧、社員名簿、EC の注文履歴、問い合わせの受信箱、商品の一覧とする。現行の 1.2.0 で生成し、描画と測定の結果を残す。
- 指標:
  - 項目あたりの埋まったスロット数
  - 主識別子を持つ項目の割合
  - 利用者の job に結び付く属性を 1 つ以上持つ項目の割合
  - C18〜C21 の件数
  - レビューの判定
- 置き場所: `research/20261103-real-site-patterns/baseline/`
- 合格条件: 6 件すべてで指標がそろう。

### Phase 1: パターンの書式と初期パターン

- 作業:
  - スキーマ `S/patterns/schema.json`
  - 付録 A の 10 種（`S/patterns/*.yaml`）
  - 決定表 `S/patterns/index.yaml`
  - 使い方と出典を書く `S/references/patterns.md`
  - `S/scripts/patterns/validate.py`（スキーマ、出典 URL の有無、ID の重複、決定表の網羅と曖昧さを検査する）
- `composition.md` の KPI タイルの規則を `measure.tile.kpi` パターンに移し、`composition.md` からはパターンを参照する。
- 合格条件: `validate.py` の検出が 0 件。決定表が、内容の種類と job class のすべての組み合わせについて、パターン ID を 1 つ返すか、質問を返す。

### Phase 2: 選択と骨組み

- 作業:
  - `resolve.py` と `scaffold.py` を作る。骨組みのスタックは vite-react（shadcn）と html の 2 つとし、DADS と SmartHR はそれぞれの部品名へ対応表で写す
  - brief テンプレートに `Sections` 行と `## Slots` 節を足す
  - OOUI 表に属性の順位の列を足す
  - SKILL.md Step 3 の手順を「brief → resolve → scaffold → 中身を入れる」に変える
- 合格条件: 同じ brief を 3 回通し、パターン ID、スロット割当、骨組みのハッシュが一致する。評価用の 6 件を骨組みから組める。

### Phase 3: 準拠の検査

- 作業:
  - `check_pattern.py`（PT1〜PT6）を作る
  - `cdp.js` が `data-pattern` と `data-slot` を書き出すようにする
  - `check_render.py` に R42〜R46 を足す
  - brief に内容の質問 3 問を足し、`A/review-design-auditor.md` の P3 にパターン準拠の観点を足す
  - SKILL.md の Step 4 と ID 表を更新する
- 合格条件: 1.2 節の例のカードが PT1 か R46 で止まる。評価用の 6 件で error が 0 件。

### Phase 4: ラベル

- 作業:
  - パターンの `labels` 節
  - `voice.status` と T23
  - C33〜C37 とラベル台帳
  - `S/references/ui-copy.md` に正解形の節を足す
  - prose-lint への受け渡し（D5）
- 合格条件: 評価用の 6 件で、C18〜C21 と C33〜C36 の件数が基準線より減る。台帳に 1 行足すと、次の検査からその行が効く。

### Phase 5: 採取ツールと領域パック

- 作業:
  - `cdp.js` の SPECIMEN モードと `harvest/abstract.py` を作る
  - 標本の台帳（`S/patterns/specimens/*.yaml`。出典、取得日、ハッシュを持つ）と承認の手順を作る
  - 最初の領域パックを 1 つ作る（D4）。その領域の実在サービスから標本を採り、パターンの変種、状態語彙、ラベル語彙を足す
  - Web Data Commons の項目出現率を項目選びの根拠に使うかは D1 で決める
- Step 0 の Reference の質問に「同じ領域で利用者が普段使うサービス」を足し、その答えで領域パックを選ぶ。
- 合格条件: 1 つの領域で、承認済みの標本が 20 件以上、パターンの変種が 5 件以上ある。

### Phase 6: 較正と検証

- 作業:
  - 新しい検査（PT、R42〜R46、C33〜C37）を採取済みの実在サイトの標本にかけ、誤検出率を測る。prose-lint が 83 文書で測った手順に倣う
  - 誤検出の多い検査は、warning に下げるか、しきい値を直す
  - 評価用の 6 件を新しい版で作り直し、Phase 0 の指標と比べる
  - 6 件を golden set として固定する（proof の 19 件に倣う）
- 合格条件（案）:
  - error にする検査は、実在サイトの標本での誤検出率が 5% 以下
  - 評価用の 6 件で、主識別子を持つ項目と、job に結び付く属性を持つ項目がどちらも 100%
  - レビューの判定に BLOCK がない

## 5. オーナーが決めること

| # | 決めること | 選択肢 | 計画の既定 |
|---|---|---|---|
| D1 | 採取してよい対象 | (a) 公開デザインシステムの文書とデモだけ<br>(b) (a) に、利用者自身のプロダクトと OSS アプリを加える<br>(c) (b) に、規約が自動アクセスを認める一般サイトを加える | (b) |
| D2 | リポジトリに残す標本の範囲 | (a) 構造と相対値だけ<br>(b) (a) に短いラベル（列見出し、状態語）を加える<br>(c) (b) にスクリーンショットを加える | (a)。(b) は出典ごとに判断する |
| D3 | 準拠検査の強さ | PT1、PT2、PT4、PT5 を最初から error にするか、較正まで warning にするか | Phase 6 の較正までは warning、その後 error |
| D4 | 最初の領域パック | 業務 SaaS（請求、顧客、案件）、EC（商品、注文）、予約・受付、公共の申請 | 利用者が選ぶ |
| D5 | prose-lint との接続 | (a) Step 4 の textlint を prose-lint（`style=business`）に置き換える<br>(b) 併用する<br>(c) 接続しない | (b) |

## 6. 扱わないことと限界

- モデルの再学習と fine-tuning は扱わない。
- スロットの上限（Salesforce の 7、HubSpot の 4 など）は各システムの慣例である。中身を埋めた部品と空の部品を比べた統制実験は見つからなかったので、上限の値は Phase 6 の較正で決める。
- Material 3 のガイドラインは JavaScript で描画され、読めなかった。スロット名（start、headline、supporting-text、trailing-supporting-text、end）だけを material-web の文書で確かめた。
- Salesforce の Dynamic Highlights Panel の項目数（12）は検索結果の抜粋でしか確かめられなかったので、計画では使っていない。
- Refero の規約の全文は読めなかった。

## 付録 A: 初期パターン 10 種

これとは別に、`composition.md` から KPI タイルの規則を `measure.tile.kpi` として移す。

| ID | 用途 | スロット（! は必須） | 主な規則 | 出典 |
|---|---|---|---|---|
| `collection.row.resource` | 名前で探す一覧の行 | media、name!、info（1〜3）!、trailing、action（1 つまで） | 行全体がリンクなら中に操作を置かない。全行で同じ属性を出す。並べ替えと絞り込みに使った属性を行に出す | SmartHR よくあるリスト、Polaris ResourceItem、DADS リソースリスト、NN/g List Entries |
| `collection.table.index` | 属性で比べる一覧 | 見出し、表の操作（3 つまで）、絞り込み、件数、見出し行、行、ページ送り。先頭列は name! で、詳細があればリンクにする | 1 列に 1 種類の値。数値は右揃え。空セルは空白。50 件を超えたらページ送り。表題にページの見出しを繰り返さない | Polaris IndexTable、Primer DataTable、SmartHR よくあるテーブル、Carbon Data table、NN/g Data Tables |
| `record.header` | 1 件の記録の見出し領域 | 戻る・パンくず、title!、状態バッジ、主要項目（4〜7）、主操作（1 つまで）、副操作、前後送り | 主要項目の先頭は名前。その記録に固有の操作を先に、複製や削除などの汎用操作を後に置く | Polaris Page、Primer PageHeader、Salesforce compact layout、HubSpot data highlights、Stripe Apps |
| `record.body.two-column` | 詳細の本文 | 主列（オブジェクトを定義する情報、2/3）、副列（状態、メタデータ、要約、1/3） | 節は重要な順に並べ、似た内容を 1 つにまとめる | Polaris resource details layout、Stripe Apps full-page |
| `record.summary-list` | 項目名と値の対 | key!、value!、action | 値がない行は、変更リンクの代わりに入力へのリンクを置く。表形式のデータには使わない | GOV.UK summary list、Stripe PropertyList、DADS 説明リスト |
| `task.list` | 手続きの進み具合 | タスク名（リンク、動詞から始める）!、hint、status! | 状態は「完了」「未完了」から始め、必要に応じて足す | GOV.UK task list、Complete multiple tasks |
| `browse.card` | 異種の項目を眺める | image、title!、label、content、sub-area（リンクか操作） | 機能ボタンは 2 つまで。カード全体がリンクなら中に操作を置かない。最初に知るべき内容を短く載せる | DADS カード、Fluent 2 Card、Carbon Tile、NN/g Cards |
| `commerce.product-item` | 商品一覧の項目 | thumbnail!、title!、price!（常に表示）、rating（平均と件数）!、variations!、分類固有の属性（1〜3） | 並べ替えと絞り込みに使った属性を項目に出す。項目に出した属性は絞り込める | Baymard（2023、2015、2019） |
| `status.badge` | 状態の表示 | label! | 1 語（複雑な状態に限り 2 語）。形容詞か完了の形。領域ごとに固定した語彙。1 つの状態に 1 色。リンクにしない | Polaris Badge、GOV.UK Tag |
| `state.empty` | 空状態 | title!、action（初回のみ）、description | 初回と絞り込み結果を分ける。絞り込み結果では作成ボタンを出さず、条件を残す | Stripe Apps empty state、SmartHR 空データ、Atlassian empty state、Primer Blankslate |

## 付録 B: 出典

デザインシステムと調査機関:

- Shopify Polaris: https://github.com/Shopify/polaris/tree/main/polaris.shopify.com/content （`components/lists/resource-list.mdx`、`resource-item.mdx`、`components/tables/index-table.mdx`、`components/layout-and-structure/page.mdx`、`components/feedback-indicators/badge.mdx`、`patterns/resource-details-layout`、`patterns/resource-index-layout`）
- GOV.UK Design System:
  - https://design-system.service.gov.uk/components/summary-list/
  - https://design-system.service.gov.uk/components/task-list/
  - https://design-system.service.gov.uk/patterns/complete-multiple-tasks/
  - https://design-system.service.gov.uk/components/tag/
- Primer:
  - https://primer.style/product/components/data-table/guidelines
  - https://primer.style/product/components/action-list/guidelines
  - https://primer.style/product/components/page-header/guidelines
  - https://primer.style/product/components/blankslate/guidelines
- IBM Carbon:
  - https://carbondesignsystem.com/components/data-table/usage/
  - https://carbondesignsystem.com/components/tile/usage/
- デジタル庁デザインシステム:
  - https://design.digital.go.jp/dads/components/card/usage/
  - https://design.digital.go.jp/dads/components/resource-list/
- SmartHR Design System:
  - https://smarthr.design/products/design-patterns/smarthr-list/
  - https://smarthr.design/products/design-patterns/smarthr-table/
  - https://smarthr.design/products/design-patterns/empty-data/
- Material Web: https://github.com/material-components/material-web/blob/main/docs/components/list.md
- Fluent 2: https://fluent2.microsoft.design/components/web/react/core/card/usage
- Atlassian:
  - https://atlassian.design/components/page-header/usage
  - https://atlassian.design/foundations/content/designing-messages/empty-state
- Salesforce:
  - https://trailhead.salesforce.com/content/learn/modules/lex_customization/lex_customization_compact_layouts
  - https://trailhead.salesforce.com/content/learn/modules/lex_migration_customization/lex_migration_customization_layouts_ui
- HubSpot: https://knowledge.hubspot.com/object-settings/create-cards-on-records
- Stripe Apps:
  - https://docs.stripe.com/stripe-apps/patterns/lists.md
  - https://docs.stripe.com/stripe-apps/patterns/full-page-apps.md
  - https://docs.stripe.com/stripe-apps/patterns/empty-state.md
- Baymard Institute:
  - https://baymard.com/blog/product-listing-information
  - https://baymard.com/blog/contextual-list-item-information
  - https://baymard.com/research-articles/have-filters-for-list-item-info
- Nielsen Norman Group:
  - https://www.nngroup.com/articles/list-entries/
  - https://www.nngroup.com/articles/data-tables/
  - https://www.nngroup.com/articles/comparison-tables/
  - https://www.nngroup.com/articles/first-2-words-a-signal-for-scanning/
  - https://www.nngroup.com/articles/information-foraging/
  - https://www.nngroup.com/articles/cards-component/

リポジトリとツール（2.2 の表の各行にもリンクを置いた）:

- prose-lint: https://github.com/tomkd555/prose-lint
- senlindesign/proof: https://github.com/senlindesign/proof
- dembrandt: https://github.com/dembrandt/dembrandt
- designlang: https://github.com/Manavarya09/design-extract
- google-labs-code/design.md: https://github.com/google-labs-code/design.md
- Mobbin の規約（2026-05-16 施行）: https://tostracker.app/document/mobbincom-tos
- Web Data Commons schema.org Table Corpus: https://webdatacommons.org/structureddata/schemaorgtables/
- WebUI: https://uimodeling.github.io
