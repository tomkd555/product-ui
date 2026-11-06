# Real screens

Source of record for what real production screens of each kind show: their regions in reading order, the sizes they use and the strings they print. Read it at Step 3 of `SKILL.md`, before the composition plan in `references/composition.md` is written, and when a reviewer asks what a screen of this kind normally shows. The evidence is `research/20261106-real-screens/report.md`: 192 production screens captured signed out at 1280px and 375px.

## How to use it

1. Choose the kind from the table below by what the request asks for. The kind settles the job class of the composition plan (`references/composition.md`).
2. Choose the variant. Each kind's Variants list names the forms production screens of the kind take, and a row pooled over the kind mixes them. Where the variant's line and a pooled row disagree, the variant decides: a status page takes the regions its variant names, with no chart and no time-range control, and a sign-in card takes the account-form figures.
3. List the regions in the Composition section of `ui-brief.md`, the shell first. Every built screen has its h1: the page title is built even where its row says `some`, and on a service status page the h1 is the status headline.
4. Build every region marked `always` (nine in ten real screens or more) and every region marked `usual` (more than half). A region is left out when the request rules it out, when the product has nothing for it to hold (a record shown whole on one page has no sub-view tabs), or when its content would be a fact about the business that the request does not give: a testimonial, a customer logo, a usage figure, a plan's sales line, the plan to recommend. The brief's Omitted line names the region with that reason. `some` marks a region on half or fewer; build it when the request asks for what it holds.
5. Fill each region the way production screens are filled. Navigation takes the product's objects (the brief's Structure table), the sibling screens the request names or implies, and the screens every product of the kind has: the sections of a settings area (プロフィール, 通知, セキュリティ), and on a public body's site よくある質問 and お問い合わせ. Each is a link to its route, and the brief lists the ones the request left unnamed as assumed. Where none of these applies, the header holds the product name and the account control alone. A collection takes a full page of sample records, and a record its whole thread and history. A footer on a public screen takes the links every product has (利用規約, プライバシーポリシー, ヘルプ). Names, titles, messages, dates and amounts are sample data, invented for a mock. A comparison table or an FAQ is built from what the request states: the plans, the prices, the trial. The rows "Text on the page" and "Links, buttons and inputs" under Every screen give the volume production screens reach. Reach it with what production screens of the kind link and list: in a row, each label, assignee and count is a link or a filter. A fact the request does not give stays out, whatever the volume, and a back-office record or a form of a few fields stays below the figures.
6. Take sizes from the kind's Values table and the shell sizes from Every screen: a text size at the step of the tokens' type scale nearest the figure, a distance at the nearest multiple of the spacing unit (`spacing.base_px`). Where two roles land on one type step, both keep it and the higher role takes the heavier weight. A Japanese screen takes the JA figure where a row gives one for its variant. A real text size under 14px is built at 14px; 12px stays only for a Latin-only run of at most 24 characters (`references/ban-list.md`), written "Latin-short 12px".
7. The Wording rows show what production screens print. The strings a build prints follow `voice` in `tokens.json` and `references/ui-copy.md`; where the two differ in form (「新しいイシュー」 against the button form), the voice rules decide.
8. A reference preset named at intake (`references/dads.md`, `references/smarthr.md`) keeps its components' own conventions where they differ from the record, such as the requirement badge on a デジタル庁デザインシステム field, and its own type scale: a size takes the preset's utility nearest the figure.

| The request asks for | Kind | Job class |
|---|---|---|
| A list or table of records in a tool a team works in: issues, tickets, orders, members | Collection: work tools | `lookup` |
| Search results or a catalogue a visitor browses: jobs, products, places | Collection: consumer search results | `lookup` |
| One record with its properties, its thread or its history | Single record | `record` |
| A form: an application, an inquiry, a sign-up, a sign-in, a search form | Form, sign-up and sign-in | `enter` |
| A dashboard, an analytics overview, a status page, a quote page | Monitoring | `monitor` |
| A pricing page | Pricing page | `decide` |
| A landing or marketing page | Landing page | `decide`, on the `lp` surface |
| A screen of a Japanese public service | Public service (Japanese), then the kind of its variant; an application or inquiry form takes the Form kind's Japanese application form | the variant's |

No capture shows a settings screen, which sits behind a sign-in. It takes the shell of the product's collection kind, Work tools for a tool a team works in and Consumer for a service a visitor browses, with that kind's shell values (header, navigation, control heights). A record inside a work tool takes the tool's shell values in the same way. The Form kind gives the field block alone (labels, inputs, gaps, the action), and the settings sections are listed in a navigation beside the fields; the job class is `enter`.

## Every screen

| | Work tools | Consumer | Record | Form | Monitoring | Public (ja) | Pricing | Landing |
|---|---|---|---|---|---|---|---|---|
| Screens | 14 | 27 (JA 18, EN 9) | 18 | 12 | 15 | 25 | 24 | 25 (JA 13, EN 12) |
| Text on the page, characters | 3264 (2523-4230) | 3868 (2955-7316) | 5876 (2602-11460) | 823 (628-962) | 1619 (1307-6963) | 1909 (1270-3319) | 5600 (4805-8194) | 4184 (2523-4879) |
| Links, buttons and inputs | 222 (131-264) | 166 (113-227) | 178 (62-216) | 32 (21-53) | 232 (105-259) | 65 (37-116) | 119 (75-152) | 140 (97-161) |
| Page height, in viewports of 1200px | 2.1 (1.9-2.3) | 5.2 (3.3-8.7) | 4.2 (2.2-6.9) | 1.1 (1.0-1.3) | 2.8 (1.9-5.9) | 3.1 (1.5-5.0) | 7.8 (6.3-10.0) | 8.0 (6.4-11.2) |
| Logo or name in the header, leading edge | 14 of 14 | 27 of 27 | 18 of 18 | 12 of 12 (position not counted) | 15 of 15 (centred on 1) | 25 of 25 (centred on 1) | 24 of 24 | 25 of 25 (centred on 2) |
| Trailing end of the header | sign in, sign up: 14 of 14 | log in, register | sign in, sign up | 0-1 links on account screens | subscribe on 6 of 7 status pages, else one sign-up, log-in or other action | language switch 16 of 25, login 7 of 25 | 1-3 actions: log in, trial, contact | login 23 of 25, filled button 21 of 25 |
| Header height, px | 52 (44-68) | JA 91 (60-300), EN 70 (36-230) | 64.5 (22-108) | 102 (60-171), the header's bottom edge | one bar of 48-80 on 11 of 15 | 120 (50-205); DADS 80 | about 64-117 | JA 100 (60-172), EN 70 (56-128) |
| Header nav items | 0 on 7 of 14, 3-6 on 7 of 14 | 5 (0-11) | 3.5 (0-12) | JA 7, non-JA 1 | status pages 1, data screens 6 | 6.5 (3-8), bar on 16 of 25 | 9 (JA domestic 11) | JA 6, EN 5 |
| Sidebar or rail | left, 7 of 14, 282px | leading column 14 of 27, 180-320px | right rail 13 of 18, 320px | 2 of 12 | 6 of 15, 304px | 4 of 25, 292.5px | 2 of 24 | |
| Footer | 7 of 14 | 27 of 27 | 13 of 18 | 10 of 12 | 13 of 15 | 22 of 25 | 24 of 24 | 25 of 25 |
| Card around every section | 0 of 14 | 4 of 27 | 4 of 18 | 1 of 12 | 6 of 15 | 7 of 25 | 0 of 24 | 0 of 25 |
| Filled buttons in the first viewport | 1 (0-2) | JA 1 (0-5), EN 0 (0-2) | 1 (0-3) | 1 (0-3) | 1 (0-3) | 0 (0-3) | 2 (1-6) | 2 (JA 0-8, EN 1-2) |
| Body text, px | 14 (12-18.38) | 14 (12-16.8) | 14 (11.2-16) | 16 (12.8-19) | 14 (12-24) | 14 (12.46-17) | 14; JA-text 16 | paragraphs JA 15.5, EN-text 15 |
| Page title, px | 20 (18-30), on 6 of 14 | JA 25, EN 29.4 | 27 (13.3-40) | 28 (JA 20) | 20 | 24 (14.4-45) | 48 | hero JA 57, EN-text 64 |
| Section heading, px | 12.13, sidebar groups only | JA 16, EN 22 | 18 | 20 | 16 | 18.29; DADS 26-32 | 39 | JA 40, EN 38.7 |
| Secondary text, px | 13.46 | JA 12, EN 14 | 14 | helper 14, legal 13.5 | 12 | 14 | unit line 14; JA-text 16 | ※ footnote 10 |
| Button height, px | 32; create 34 | JA 32, EN 40 | 32 (22-46) | primary 46 (36-52) | 32 (26-44) | primary 42 (24-50) | plan CTA 44 | hero CTA JA 70, EN 41.5 |
| Input height, px | 33.5 (28-50) | JA 33, EN 29.5 | 32.5 | 34 (JA 31.5, non-JA 48) | 32 (28-40) | 40; selects 31 | input on 5 of 24 | |

Build each value at the step of the tokens' type scale or spacing scale nearest the kind's median. Text sizes follow step 4. A visible box inset in a visible box shows on 19% of the 192 screens and three boxes deep on 1% (`references/composition.md`, Containers).

The three volume rows give the median and the quartiles at 1280px; the renderer counts at most 300 controls on a page.

The ground is white on 146 of the 192 screens, another light colour on 29 and dark on 17. On a light ground the most common text has a lightness of 29% at the median (under 25% on 57 screens, 25 to 40% on 73) and a chroma of 0.002. A screen is built on a light ground unless the request asks for a dark interface.

The most common text of a screen sets its line height at 1.5 times its size at the median on Japanese screens (1.45 to 1.62 on the middle half, n=79) and at 1.43 on English ones (1.33 to 1.5, n=101).

A chromatic fill paints a control on 132 of the 192 screens, and on 32 of those the fill matches a Tailwind default. The most common corner radius of a screen's containers is 0px on 74 of the 155 screens that draw one, 4 to 8px on 41 and 10 to 12px on 17. A build takes a radius of 4 to 8px unless the brand sets another.

Link text takes a chromatic colour in the page body on 119 of the 177 screens with links there: 16 of the 20 record screens, 11 of the 13 form and account screens, 43 of the 64 list and search screens. The colour is a blue on 119 of the 134 screens that colour a link. In the top band a link is chromatic on 73 of 148 screens, and in the foot on 66 of 160. Chromatic text outside links and controls, such as a state word, a signed change, a price or a required mark, is on 116 of the 192. A build colours its text the same way:

- A link in a sentence, beside a field, among the properties of a record or under a list (`すべて見る`) takes `text-primary` where `color.primary` reaches 4.5:1 on the ground (`python {SKILL_DIR}/scripts/colour.py contrast`), and an underline in the text colour otherwise.
- Navigation items, row titles and footer links take the text colour.
- A state word and a signed change take the status colour as text (`destructive`, `success`, `warning`) where it reaches 4.5:1 on the ground, and the word or the sign still carries the state.

At 375px the same screens set a control at 29px on its shorter side at the median (26px at 1280px) and the page title at 28px (32px at 1280px).

Every capture is signed out. Behind a sign-in, the trailing end of the header holds the signed-in user's menu in place of sign in and sign up. A footer belongs to the public screens the record shows; a signed-in work screen is built with none unless the request shows one, whatever the footer's mark in the kind's Anatomy.

The captures show each screen at rest, with data. The empty, loading and error states of a collection and the validation state of a form lie outside this record; the States section of `assets/brief.template.md` settles them.

## Collection: work tools

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Global header | Logo; search field (8 of 14) or icon (4 of 14); 3-6 nav links (7 of 14) | Dark or brand fill on 5 of 14, else white with a 1px rule | 14 of 14, always |
| Left sidebar | Section nav of 9-30 items | 282px (237-412); content 26px (14-49) to its right | 7 of 14, some |
| Page title | The collection's plural noun or the saved query's name | 20px (18-30) | 6 of 14, some |
| Search or filter field | The active query or a placeholder, which names the field on 10 of 10 | Top of the content column | 10 of 14, usual |
| Filter, sort and view row | Field dropdowns; view tabs or a state switch (7 of 14); a sort control (4 of 14) or sortable headers (7 of 14) | Directly above the rows | 14 of 14, always |
| Result count | A number and a noun | List header, beside the title or in the pager | 7 of 14, some |
| Column headers | One noun per column, 5 columns (5-10) | A 1px rule under the row | 8 of 14, usual |
| Rows | Title in the text colour (12 of 14); a second line (12 of 14); right-aligned time or counts (10 of 14); chips (8 of 14); avatars (8 of 14) | First row at y 254 (141-467); a 1px rule between rows on 12 of 14 | 14 of 14, always |
| Pagination | Previous, page numbers, Next; the forums load on scroll | Centred under the last row | 8 of 14, usual |
| Footer | One line of legal links | Page end | 7 of 14, some |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Row title | 16px (13-18.38, n=14) | 16px; 14px in a one-line grid |
| Second line and cells | 13.46px (12-14, n=14) | 14px |
| Chip and badge text | 12px (11.6-13.93, n=9) | 14px (Latin-short 12px) |
| Row pitch | 71px (35-135, n=13); one-line grids 35-37, two-line rows 60-92 | 71px; 35-37px for one-line grids |
| Records in the first 1200px | 12.5 (8-29, n=14) | 9-21 |
| Content column | 950px beside a sidebar (814-995, n=7); 1233px as the only column (1088-1280, n=7) | 950px; 1233px |

### Wording

- Create action: `New` and the object noun on 4 of 5; 新しい and the noun in Japanese. `New issue` [GitHub Issues]; `新しいイシュー` [Codeberg Issues]; `Create Task` [Phabricator (Maniphest)]
- Filter labels: a bare field noun on a dropdown. `Author` [GitHub Issues]; `ラベル` [Codeberg Issues]; `担当者` [Codeberg Issues]
- Sort and view: the current order, or view tabs. `Newest` [GitHub Issues]; `Sort: Trending` [Hugging Face Models]; `Latest / Top` [Obsidian Forum]
- Search placeholder: a verb and its object. `Search runs` [GitHub Actions]; `Filter by name` [Hugging Face Models]; `イシューを検索…` [Codeberg Issues]
- Count: a number and a plural noun. `5967 results` [GitHub Issues]; `Tasks (100)` [Phabricator (Maniphest)]; `1 - 50 of many` [Chromium Issue Tracker]
- Row metadata: id, actor, verb and relative time, or the category on forums. `microsoft/vscode#346430 · jruales opened 5m ago` [GitHub Issues]; `#15154 markfqs が 2時間前に作成` [Codeberg Issues]; `Help and Support` [rclone Forum]

### Variants

- Issue-tracker list: a search field and a filter bar over two-line records at 60-86px pitch, then numbered pages. GitHub Issues, GitHub Actions, Codeberg Issues, Phabricator (Maniphest).
- Forum topic table: category pills and Latest/Top tabs over a Topic, Replies, Views, Activity table at 70-92px pitch, loaded on scroll. Python Discourse, Discourse Meta, rclone Forum, Mozilla Discourse, Obsidian Forum.
- Dense data grid: 5-10 sortable columns at full width; one-line rows of 35-37px put 21-29 records in the first 1200px. Bugzilla, Chromium Issue Tracker; GitLab CI/CD Pipelines with stacked cells.
- Catalogue: a facet sidebar beside one bordered card per item, or a 4-column card grid. Hugging Face Models, Hugging Face Spaces.

### Rare on real screens

Row of 3 or more equal statistic tiles 0 of 14; subtitle describing the screen 0 of 14; helper text under form fields 0 of 14; icon in a tinted square above a heading 0 of 14; card around every section 0 of 14; legend or caption 0 of 14; hero heading over the first viewport 0 of 14; bulk-select checkboxes 1 of 14.

## Collection: consumer search results

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Global header | Logo; search field (JA 14 of 18, EN 7 of 9); log in and register; 0-11 section links | Full width | 27 of 27, always |
| Breadcrumb | Path links of 12-13px | Above the title | 10 of 27, some |
| Page title | The query or subject with の検索結果 or 一覧, or the subject alone | JA y 190, bold on 14 of 16; EN y 137 | 22 of 27, usual |
| Filter region | Facet groups under bare-noun labels: checkboxes, price ranges, もっと見る | Left column on 10 of 19, right on 5 of 19, a bar above the list on 4 of 19 | 19 of 27, usual |
| Result count | The total, often with the shown range; the number larger or bolder | Above the first result, in the title or in the toolbar | 20 of 27, usual |
| Sort control | A dropdown showing the current order, or order tabs | Trailing end of the toolbar, or a tab row above the list | 19 of 27, usual |
| Results | Title link, 1-3 metadata lines; image on 20 of 27; save control on 15 of 27; price on 10 of 27 | Rules between results on 11 of 27, distance alone on 12 of 27, a box each on 4 of 27 | 27 of 27, always |
| Pagination or load more | Numbered pages, a next-N link or Load more | Below the last result; repeated above on 4 of 27 | 23 of 27, usual |
| Footer | Link columns and copyright | Full width | 27 of 27, always |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Item title | JA 16.8px (13.91-24, n=18) at 700; EN 15.96px (12-18, n=9) at 400 | JA 16.8px bold; EN 15.96px |
| Metadata line | JA 12px (11.5-14, n=17); EN 14px (9.33-16, n=9) | 14px |
| Count numeral | JA 16px (13-30, n=14), bold on 11 of 14; EN 12px (12-14.4, n=5) | JA 16px bold; EN 14px (Latin-short 12px) |
| Item pitch | row lists 188.5px (20-654, n=20); image grids 279px (140-679, n=7) | 188.5px; 279px |
| Items in the first 1200px | JA 3 (1-21, n=18); EN 10 (0-30, n=9) | JA 3; EN 10 |
| Results per page | 25 (3-50, n=27) | 25 |
| Grid columns | 4 (2-6, n=7) | 4 |
| Filter column; right rail | 239px (180-300, n=8); JA 300px (230-360, n=8) | 239px; 300px |
| Result column | JA 764px (532-1035, n=18); EN 890px (596-1258, n=9) | JA 764px; EN 890px |

### Wording

- Page title: JA the query with の検索結果 or 一覧; EN the category or a search heading. `iphone の検索結果` [メルカリ]; `ノートパソコン 製品一覧` [価格.com]; `Sofas & sectionals` [IKEA]
- Count: JA a number with 件, often with the range; EN the range and the total. `1～20 件を表示 ／ 全 5604 件` [食べログ]; `714,896 件` [Yahoo!ショッピング]; `Results 1 – 20 of 11,858` [Wikipedia]
- Sort: JA an order ending in 順; EN a noun phrase. `おすすめ順` [Yahoo!ショッピング]; `価格の安い順` [メルカリ]; `Best match` [IKEA]
- Filter labels: bare nouns under a panel title. `絞り込み` [メルカリ]; `予算` [食べログ]; `Filters` [Eventbrite]
- Metadata: facts joined by a slash, a bar or a dot. `西武新宿駅 347m / 日本料理、しゃぶしゃぶ、居酒屋` [食べログ]; `15時間前` [Zenn]; `Today • 11:00 PM` [Eventbrite]

### Variants

- Row list: one full-width row per result, a thumbnail on the leading side on 9 of 14. connpass, Qiita, クックパッド, 食べログ, ランサーズ, 楽天市場, Wikipedia, Hacker News, Steam, Open Library, Eventbrite, Lobsters.
- Image tile grid: 2-6 columns of image-first tiles, grouped by the image's rounded corners and the gaps. Zenn, メルカリ, note, Yahoo!ショッピング, IKEA, Rotten Tomatoes.
- Comparison table: records as rows, attributes as 5-12 columns. 価格.com, Yahoo!乗換案内, MusicBrainz.
- Large record block: a 566-654px block per result with photos, attributes and an in-row action. Wantedly, SUUMO.

### Rare on real screens

Row of 3 or more equal statistic tiles 0 of 27; icon in a tinted square above a heading 0 of 27; hero heading over the first viewport 0 of 27; helper text under most form fields 0 of 27; gradient or glass 2 of 27; visible label on the header search field 0 of 21.

## Single record

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Global header | Logo, search field, 0-12 nav links, sign in; a second band on 10 of 18 | Full width | 18 of 18, always |
| Context line | Breadcrumb, owner / project path, or category eyebrow | 12-14px, 20-45px above the title | 13 of 18, usual |
| Title block | The record's name; id, version or ticker beside it (10 of 18); a status badge (4 of 18); one meta line | y 142.5 (47-525); the largest text on 14 of 18 | 18 of 18, always |
| Record actions | 1-3 controls: collect, buy, use; export, print, copy; edit, share | Trailing end of the title row on 9 of 18, top of the rail on 4 of 18 | 17 of 18, always |
| Sub-view tabs | 2-12 tabs (median 6) splitting the record | A 40-58px row under the title | 10 of 18, usual |
| Property list | Label and value pairs; an empty field shows a placeholder | Main column on 10 of 18, rail on 7 of 18 | 17 of 18, always |
| Record body | Description, README, steps or the first comment | Main column | 10 of 18 in the first 1200px, usual |
| Child-record list | Files, comments, markets, tags or contents | Below the properties | 12 of 18 in the first 1200px, usual |
| Right rail | Properties under small headings, install fields, related records | 320px (250-394) beside a 594-872px main column | 13 of 18, usual |
| Footer | Link columns, legal links | Full width | 13 of 18, usual |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Property label; value | 14px (11-18.7, n=17); 14px (12-32, n=17); JA 16 and 18 | 14px |
| Label set apart by | a lighter grey on 9 of 17; a colon on 7 of 17, on 0 of 3 Japanese-UI screens | grey label; colon on English side-by-side rows |
| Property row pitch | side by side 32px (20-43, n=13); stacked 80px (52-120, n=7) | 32px; 80px |
| Property rows in the first 1200px | 7.5 (0-15, n=18) | 7.5 |
| Child-record rows | 43px pitch (28-125, n=10), 13.8px text | 43px; 14px |
| Main column as the only column | 972px (789-1074, n=5) | 972px |

### Wording

- Page title: the record's own name; the id or version follows in a lighter run on 10 of 18. `requests 2.34.2` [PyPI]; `serde v1.0.229` [crates.io]; `トヨタ自動車(株)` [Yahoo!ファイナンス]
- Status badge: one word or a short noun phrase. `Merged` [GitHub Pull Requests]; `Resolved` [Apache JIRA]; `検証済み` [GitLab Repository]
- Primary action: what the reader does with the record. `Want to Read` [Goodreads]; `カートに入れる` [Steam]; `Use this dataset` [Hugging Face Datasets]; `pip install requests` [PyPI]
- Property labels: the field's name; English side-by-side labels end in a colon. `Type:` [Jira]; `資料種別` [国立国会図書館サーチ]; `前日終値` [Yahoo!ファイナンス]; `Content type` [Docker Hub]
- Empty values: a placeholder word, or one sentence for an empty list. `None yet` [GitHub Pull Requests]; `Unassigned` [Apache JIRA]; `最近見た銘柄はありません` [Yahoo!ファイナンス]

### Variants

- Record with a right rail: the body in a 594-872px main column, properties in a 250-394px rail; Jira, Apache JIRA and GitLab Repository add an app sidebar. GitHub Pull Requests, Jira, Apache JIRA, Hugging Face Datasets, PyPI, Docker Hub, crates.io, GitLab Repository, 国立国会図書館サーチ.
- Quote page: a 32-48px price as the largest text with a red or green change, then a chart and a label/value grid. CoinMarketCap coin detail, Yahoo Finance quote, Yahoo!ファイナンス.
- Media-led product page: a cover or photo leads; the title, rating and a filled collect or buy action sit beside it. Goodreads, Steam, Open Food Facts.
- Single-column record sheet: one 972-1074px column of stacked fields or ruled sections, history below. 国税庁法人番号公表サイト, Bugzilla Bug Detail, Hacker News.

### Rare on real screens

Row of 3 or more equal statistic tiles on the record 0 of 18; subtitle describing the screen 0 of 18; helper text under form fields 0 of 18; icon in a tinted square above a heading 0 of 18; chart legend 0 of 18; hero heading over the first viewport 0 of 18; negated method or data note 1 of 18.

## Form, sign-up and sign-in

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Site header | Logo; a utility row and nav bar on Japanese service sites | Full width | 12 of 12, always |
| Page title | The task: an object with 検索 or 作成, or an English verb phrase; a slogan on 2 of 12 | y 199 (69-481); left-aligned with the form on 9 of 12; the largest text on 12 of 12 | 12 of 12, always |
| Intro or instruction | How-to lines or steps on Japanese public and service forms, a tagline, an appeal | Between the title and the first field, 1-4 lines | 6 of 12, some |
| Field block | Labelled question groups (median 2); labels above the control on 9 of 10; one column on 7 of 10 | Under the title or intro | 10 of 12, usual |
| Primary action | One filled button in the form on 7 of 12 | Below the last field; full column width on 6 of 11 | 11 of 12, always |
| Secondary paths and legal line | Other flow, recovery, another method, help, terms or CAPTCHA | 16-40px below the action | 10 of 12, usual |
| Footer | Policy, contact, accessibility links | Page end | 10 of 12, usual |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Field label | 15.7px (12-20, n=10), bold on 8 of 10 | 15.7px bold |
| Helper; legal line | 14px (10-16, n=6); 13.5px (12-16, n=6) | 14px |
| Input width; action width | 448px (63-892, n=9); 330px (144-460, n=11) | 448px; full column width |
| Form column | narrow 444px (330-460) or wide 960px (680-1088), n=12 | 444px for account forms; 960px for lookups |
| Gaps: title to field, label to input, between fields, field to action | 32px (16-73, n=6), 5px (5-31, n=5), 24px (10-49, n=6), 27px (16-40, n=6) | 32, 5, 24, 27px |

An account form (sign-in, sign-up) takes these figures: a column of 444px (330-460), inputs of 48px, a primary action of 46px at the column's full width, and a header that holds the logo and at most one link. The distance from one field to the next follows from the label, the gaps above and the input. A Japanese account form takes the column and the header from this line and its input and action heights from the list below: inputs of 40px, an action of 44px, the spacing step above the measured 42px. The JA figures in the tables of this section come from search and tracking forms and stay with them.

Japanese account forms, from a supplement of 22 sign-in and sign-up pages of Japanese products (`urls_supplement.jsonl` in the research folder):

- Sizes: text inputs of 40px (21-52, n=20); a primary action of 42px (35-56, n=20).
- Page title: 「ログイン」 alone on 7 of 16, with the service's name on 4. `マネーフォワード IDでログイン` [マネーフォワード ID]; `Qiita にログイン` [Qiita]
- Primary action of a sign-in: 「ログイン」 on 12 of 18, 「ログインする」 on 2; a form of two steps reads 「次へ」 or 「続ける」 on 3. A sign-up reads `登録する` [Qiita].
- Password recovery: a link by the password field on 16 pages, worded with 忘れ on 12. `パスワードを忘れた方` [note]; `パスワードをお忘れの方` [SmartHR]; `パスワードを忘れた場合` [Qiita]
- Path to sign-up: 「新規登録」 or 「新規会員登録」 on 9 of 15, with はこちら on 3. `新規登録はこちら` [ニコニコ]; `新規会員登録` [さくらインターネット]
- Identity providers: buttons on 15 of 22, at 40 to 52px. A Google button reads 「Googleでログイン」 on 7 of 12, and `Googleで登録` on a sign-up [Qiita, note].

Japanese application and inquiry forms, from a second supplement of forms that public bodies, universities and companies serve (`urls_forms.jsonl` in the research folder; 18 measured at 1280px, 24 at 375px):

- Fields: 10 (8-12) on one page. Text inputs of 33.5px (26-42) and 464px wide (384-654), in a column of about 650px (581-720).
- Label: 16px (14-16), bold on 9 of 18. It sits beside its field, in a label column, on 14 of 18 at 1280px, and above its field on 16 of 24 at 375px.
- Required mark: 「必須」 by the label on 11 of 18, in a chromatic colour or on a chromatic fill; 「任意」 on 1 and an asterisk on 1.
- Page title: 27px (20-36, n=16), the form's name. `ご意見・お問い合わせメールフォーム` [船橋市]; `リモート消費生活相談申込フォーム` [札幌市]; `資料請求フォーム` [国際工科専門職大学]
- Primary action: it opens the confirmation step on 14 of the 15 forms with an action, and its text says so. `入力内容を確認する` [船橋市]; `確認画面へ` [美馬市, 東急ストア]; `送信確認` [調布市, 札幌市]; `同意して確認画面に進む` [サカタのタネ]. It is 47px high and 184px wide at the median, narrower than the column.
- Also on the page: consent to the handling of personal information on 6 of 18, an example value after 例 on 6, and the steps 入力, 確認 and 完了 as an indicator on 3.
- Volume: 902 characters (631-1485) and 42 links, buttons and inputs (30-51).

### Wording

- Page title: JA an object noun ending in 検索; EN a verb phrase in sentence case. `過去の気象データ検索` [過去の気象データ検索]; `送り状番号検索` [荷物お問い合わせシステム]; `Create account` [Wikipedia create account]
- Field label: the item's noun on 6 of 10 forms, an instruction on 4 of 10. `Username` [Wikipedia create account]; `お問い合わせ番号` [郵便追跡サービス]; `Enter your email address` [login.gov create account]
- Helper: a format, limit, example or consequence. `Avoid using your real name.` [Wikipedia create account]; `全角50文字以内` [ハローワークインターネットサービス]; `例（書留,ゆうパック） ： 12345678901` [郵便追跡サービス]
- Primary action: JA the operation noun on 6 of 7; EN a verb and object of at most 3 words. `検索` [適格請求書発行事業者公表サイト]; `追跡スタート` [郵便追跡サービス]; `Continue with Google` [Vercel sign-up]
- Secondary action: JA a clear on 4 of 5; EN another method or Cancel. `入力内容をクリア` [荷物お問い合わせシステム]; `Show other options` [Vercel sign-up]; `Cancel` [login.gov create account]

### Variants

- Focused account form: a 390-460px column as a centred card or beside a photo; inputs and the action at full width. Wikipedia create account, login.gov sign-in, login.gov create account, Cal.com, Vercel sign-up.
- Lookup by identifier: one identifier field or 10 numbered inputs under a format line; search beside clear on Japanese sites. 適格請求書発行事業者公表サイト, Find and update company information, 郵便追跡サービス, 荷物お問い合わせシステム.
- Application or inquiry form (Japanese): a label column beside about ten fields, 必須 marks, and an action that opens the confirmation step. 船橋市, 札幌市, 新潟市, 厚生労働省, 東急ストア, サカタのタネ.
- Multi-criteria search form: a ruled label/field table with 必須 and 任意 badges, or three selector columns. ハローワークインターネットサービス, 過去の気象データ検索.
- Donation or payment panel: frequency and amount tiles, with payment-method buttons as the submit. Wikimedia donation page.

### Rare on real screens

Row of 3 or more equal statistic tiles 0 of 12; icon in a tinted square above a heading 0 of 12; card around every section 1 of 12; legend or caption 0 of 12; hero heading over the first viewport 0 of 12; helper text below the input 0 of 10; asterisk required marker 0 of 10; 必須/任意 badges 1 of 10 (on Japanese application and inquiry forms a 必須 mark is usual, 11 of 18); glass 0 of 12; cookie banner 1 of 12.

## Monitoring

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Global header | Logo; up to 13 nav links; one subscribe or account action at the trailing end | One bar on 11 of 15 | 15 of 15, always |
| Local navigation | Tabs or a sidebar of sibling views | Under the header; tabs 28-48px, sidebars 296-312px | 9 of 15, usual |
| Summary block | Status pages: the overall state as a filled banner or headline. Data screens: a headline figure with a signed change, or a KPI row | First content block, top at y 165 (78-576) | 12 of 15, usual |
| Time-range control | A dropdown, range buttons, a stepper or a slider | Dropdown at the top right; 24-28px range buttons by the chart | 8 of 15, usual |
| Main chart | One time-series or bar chart, tick labels on both axes | Under the summary; ends inside the first 1200px on 7 of 7 | 8 of 15, usual |
| Repeated rows | Status components (name, state word, 90-day uptime strip on 4 of 7), table rows, breakdown lists or label/value stats | Top at y 575 (190-1096) | 15 of 15, always |
| Footer | Link columns, a link row or one Powered by line | Below the fold on 13 of 15 | 13 of 15, usual |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Row text | 16px (13.4-16, n=15); data rows 12-14px | 16px; 14px on data rows |
| Headline figure | 25.6px (16-48, n=6), the largest text on 3 of 3 quote pages | 25.6px |
| Row pitch | status pages 127.5px (70-190, n=7); data screens 36px (32-52, n=8) | 127.5px; 36px |
| Items fully in the first 1200px | 8 (4-18, n=15) | 8 |
| Chart plot | 700×340px (n=7) | 700×340px |
| Status page column | 850px (670-1153, n=7) | 850px |
| Statistic tiles | 0 (0-8, n=15); a tile row on 3 of 15: two analytics overviews and one market strip | a tile row on an analytics overview; none on the other variants |

### Wording

- Status headline: the overall state as a short sentence. `All Systems Operational` [GitHub Status]; `We’re currently experiencing issues` [OpenAI Status]; `Slack is up and running` [Slack System Status]
- Header action: verb first, 1-3 words. `Subscribe to updates` [OpenAI Status]; `Sign up` [Plausible Analytics public dashboard]; `ポートフォリオに追加` [Yahoo!ファイナンス]
- Range control: the current value. `Last 28 days` [Plausible Analytics public dashboard]; `Period: 1 week` [GitHub Insights Pulse]; `1日 1週 1カ月 6カ月 1年 2年` [Yahoo!ファイナンス]
- Change on a figure: a signed change in red or green with the period. `$76,192.00 ▼5.47% (24h)` [CoinMarketCap coin detail]; `344.17 -5.34 (-1.53%)` [Yahoo Finance quote]; `3,463 前日比 -70 (-1.98%)` [Yahoo!ファイナンス]
- Empty: one phrase stating that nothing is there. `No incidents reported today.` [npm Status]; `No recent incidents` [Cloudflare System Status]; `最近見た銘柄はありません` [Yahoo!ファイナンス]

### Variants

- Service status page: a centred column under a header with the logo and a subscribe action; the overall state, component rows, then past incidents. GitHub Status, npm Status, OpenAI Status, Cloudflare System Status, Vercel Status, Slack System Status, Atlassian Status.
- Analytics overview: statistic tiles above or beside one main chart, then breakdown lists or a table; a period control at the top right. Plausible Analytics public dashboard, GitHub Insights Pulse, CoinMarketCap.
- Quote or entity detail: the name over a 32-48px figure with a signed change, a chart with range buttons, a stats grid and a 297-344px rail. CoinMarketCap coin detail, Yahoo Finance quote, Yahoo!ファイナンス.
- Chart explorer: the chart fills the screen, changed by a query editor or by view tabs and a selection panel. Grafana Play Explore, Our World in Data Grapher.

1 of 15 screens is Japanese (Yahoo!ファイナンス): 14px body, 28px name, 48px price, 34px rows.

### Rare on real screens

Icon in a tinted square above a heading 0 of 15; hero heading over the first viewport 0 of 15; helper text under most form fields 0 of 15; decorative gradient or glass 0 of 15.

## Public service (Japanese)

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Header | Logo; at the top right a language switch (16 of 25), site search (10 of 25), help (8 of 25), 文字サイズ buttons (4 of 25) | One 80px row on DADS screens | 25 of 25, always |
| Global navigation | 3-8 items: functions with よくある質問, topic categories, or audiences | A filled band on 9 of 16, a text row on 7 of 16; 44-70px | 16 of 25, usual |
| Breadcrumb | Path links | Above the title | 7 of 25, some |
| Page title | The object or service; the count on result pages | Left-aligned at y 209 (51-497); an accent bar or tinted band on 6 of 15 | 15 of 25, usual |
| Site or screen description | このサイトでは… or …できます | Under the title on 3 of 25, else in the header or at the top | 10 of 25, some |
| Main working block | A search form panel, results under a query bar, a data table, record fields, or portal sections | Centred container; a sidebar on 4 of 25 | 25 of 25, always |
| Footer | Site-policy links, agency name, copyright | A grey or dark band | 22 of 25, usual |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Content container | 1120px (892-1280, n=25) | 1120px |
| Table and result-list text | 14px: tables 12.46-16 (n=4), result lists 14-16 (n=3) | 14px |
| Line height | 1.6 (1.2-2.0, n=22); DADS 1.7-2.0 | 1.6 |
| Data table rows | 27px (26-42, n=4); 26 rows in the first 1200px | 27px |
| Result items | 227px (204-257, n=3); 3 in the first 1200px | 227px |
| News rows | 38px (29-50, n=7), 16px text | 38px |
| Table columns | 6 (5-20, n=5) | 6 |

### Wording

- Page title: a noun phrase ending in 検索, 一覧, 情報 or 表示. `データセット一覧` [e-Stat 政府統計の総合窓口]; `検索結果 19,942 件` [国立国会図書館サーチ]; `地震情報` [気象庁 地震情報]
- Primary action: the bare サ変 noun (8 of 25) or the する form (6 of 25). `検索` [国税庁法人番号公表サイト]; `検索する` [ハローワークインターネットサービス]; `表示する` [国会会議録検索システム]
- Reset: クリア or 解除 on every search screen. `クリア` [国税庁法人番号公表サイト]; `すべてクリア` [国立国会図書館サーチ]; `検索条件を全てクリア` [過去の気象データ検索]
- Empty: a sentence naming the absent object. `現在、お知らせはありません。` [横浜市ホームページ]; `発表情報はありません` [川の防災情報]; `---` [気象庁 防災情報 警報・注意報]
- Section headings: the お知らせ family, and tasks as 〜から探す. `重要なお知らせ` [デジタル庁]; `新着・更新` [デジタル庁]; `市町村から探す` [川の防災情報]

### Variants

- Search entry form (Form): one form panel, a how-to link above the fields on 5 of 5, a 40-50px button with クリア. 国税庁法人番号公表サイト, ハローワークインターネットサービス, 国会会議録検索システム, 過去の気象データ検索, 適格請求書発行事業者公表サイト.
- Dense lookup (a collection kind): results under a query bar, count and filters, or full-width tables with a tinted header row. Among them e-Stat 政府統計の総合窓口, 国立国会図書館サーチ, e-Stat 統計データベース, 気象庁 地震情報.
- Record page (Single record): the record's name as the h1, key-value fields, print or export links. 国税庁法人番号公表サイト, 国立国会図書館サーチ, e-Gov 法令検索.
- Portal: a notice block or hero, then link tiles, topic cards, 〜から探す panels and news; DADS sites put 26-32px headings on a white ground. Among them デジタル庁, こども家庭庁, 東京都公式ホームページ, 横浜市ホームページ.

### Rare on real screens

Row of 3 or more equal statistic tiles 0 of 25; icon in a tinted square above a heading 0 of 25; hero over the first viewport 0 of 15 non-portal screens, 2 of 10 portals; gradient 1 of 25; glass 0 of 25; required or optional badges 1 of 25; dark theme 1 of 25; apology in a notice 1 of 25.

## Pricing page

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Global header | Logo; 6-14 nav items; 1-3 actions; a utility row above on 5 of 8 JA domestic pages | An announcement bar on 4 of 24 | 24 of 24, always |
| Title block | One title; a one-sentence subtitle on 13 of 24; hero art on 4 of 24 | y 168 (109-322); centred on 14 of 23 | 23 of 24, always |
| Controls above the plans | Billing toggle (11 of 24), segment tabs (7 of 24), currency (5 of 24) | Directly above the plans; 36-48px pill toggles | 15 of 24, usual |
| Plan row | 2-5 plans: name, one-line description, price with unit, CTA, features; one plan singled out on 16 of 23; top tier Custom on 11 of 23 | First plan name at y 536 (JA domestic 813, global 412); equal widths on 22 of 23 | 23 of 24, always |
| Note or link line | A tax note, a comparison link or a help prompt | One line under the plans | 16 of 23, usual |
| Proof band | Customer logos, a usage figure or a testimonial | Below the plans on 13 of 15 | 15 of 24, usual |
| Comparison table | A label column and 2-5 plan columns; labelled row groups on 16 of 18; check icons on 14 of 18 | Before the FAQ | 18 of 24, usual |
| FAQ | Billing, trial, plan change, payment, tax; an accordion on 18 of 21 | Near the end | 21 of 24, usual |
| Closing CTA band | A short heading and 1-3 buttons | Before the footer | 13 of 24, usual |
| Footer | Link columns, legal links, language | Full width | 24 of 24, always |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Plans in the row | 4 (2-5, n=23); JA domestic 3 | 4; JA domestic 3 |
| Plan name | 23.5px (14-36, n=22) | 23.5px |
| Price numeral | 29px (17-64, n=22); larger than the plan name on 13 of 22 | 29px |
| Unit line; feature lines | 14px (13-16.9, n=22; JA-text 16); 14px (13-16, n=23) | unit line 14px (JA 16px); feature lines 14px |
| Plan CTA | 44px (36-54, n=22); full column width on 16 of 23 | 44px at full width |
| Plan row | 1120px (878-1250, n=23), column pitch 304px (235-404, n=22) | 1120px; 304px |
| Comparison rows | 65 (21-119, n=18) at 54px pitch (44-74) | 54px |
| FAQ questions | 11 (3-32, n=21) | 11 |

### Wording

- Page title: JA domestic a bare label on 7 of 8; global a claim or slogan on 12 of 16. `料金プラン` [SmartHR]; `料金` [kintone]; `Pricing` [Linear]; `Predictable pricing, designed to scale` [Supabase]
- Plan names: a ladder of tier words, Enterprise last on 13 of 23. `フリー / プラス / ビジネス / エンタープライズ` [Notion]; `ライト コース / スタンダード コース / ワイド コース` [kintone]; `Hobby / Pro / Enterprise` [Vercel]
- Price unit: a smaller unit and billing basis by the numeral. `1ユーザー/月 (年額契約)` [LINE WORKS]; `per user / month` [Jira]; `カスタム料金` [Notion]
- Recommended marker: a short badge on 13 of 23. `おすすめ` [kintone]; `Recommended` [Notion]; `Most Popular` [Supabase]
- Plan CTA: start, trial or buy; a sales contact on 16 of 23. `無料で使ってみる` [マネーフォワード クラウド]; `Start free trial` [Jira]; `営業に問い合わせる` [Notion]; `Contact sales` [Linear]
- Feature lead-in: each higher plan restates the lower one, on 14 of 23. `プラスプランの全機能に加えて` [Notion]; `Everything in the Free Plan, plus:` [Supabase]; `All Hobby features, plus:` [Vercel]

### Variants

- Separate plan cards with gaps between. freee, マネーフォワード クラウド, LINE WORKS, Asana, Zendesk, Shopify.
- One container split into plan columns, the recommended column raised or tinted. Vercel, Supabase, Raycast, GitHub, Jira, Intercom, HubSpot CRM, Notion.
- Open columns on the page ground, separated by space or thin rules. Linear, Figma, Datadog.
- Plan table: the plans head the feature matrix. SmartHR, kintone, クラウドサイン, Mailchimp.

### Rare on real screens

Row of 3 or more equal statistic tiles 1 of 24; subtitle describing the screen 2 of 24; helper text under form fields 0 of 24; icon in a tinted square above a heading 1 of 24; card around every section 0 of 24; legend for table marks 0 of 18.

## Landing page

### Anatomy

| Region | Holds | Size and position | Shown on |
|---|---|---|---|
| Utility row or announcement bar | JA secondary links (7 of 13); EN a one-line announcement (3 of 12) | y 0, 20-40px | 11 of 25, some |
| Global header | Logo; 4-9 nav items; login; filled buttons: JA a document request with a contact or trial, EN one sign-up | Sticky | 25 of 25, always |
| Hero | Headline; sub-copy (JA 6 of 13, EN 12 of 12); 1-3 CTAs (22 of 25; JA 2, EN 1.5); product UI in the first 1200px (18 of 25) | Ends at y 600-900; JA text left, visual right on 12 of 13 | 25 of 25, always |
| Proof band | Customer logos with a claim line; JA adds share figures and badges | Under the hero, 120-300px | 12 of 25, some |
| Value and feature sections | A heading and a short lead over 3-4 equal cards (21 of 25), tabs or accordions (9 of 25), a bento or alternating rows (4 of 25 each) | JA on full-bleed tinted bands on 11 of 13 | 25 of 25, always |
| Customer stories | JA case-study cards under 導入事例; EN quotes with name and role | After the features | 19 of 25, usual |
| Repeated CTA band | One sentence and the hero's buttons | Between sections | JA 7 of 13, usual; EN 1 of 12, some |
| Pricing, FAQ, resources | 料金プラン, よくあるご質問, お役立ち資料 | Second half | pricing 10 of 25, FAQ 6 of 25, some; resources JA 10 of 13, usual |
| Closing CTA | A heading and 1-2 buttons; JA a phone number on 4 of 13 | Above the footer | 23 of 25, always |
| Footer | 4 or more link columns (21 of 25), legal links, copyright | Dark on JA 3 of 13, EN 7 of 12 | 25 of 25, always |

### Values

| Value | Real screens | Build with |
|---|---|---|
| Headline length | JA 15 characters (6-22, n=13); EN-text 51 characters, 8 words (22-73, n=8) | JA 15 characters; EN 8 words |
| Hero sub-copy | JA 37.5 characters (19-101, n=6) at 19px; EN-text 123 characters (61-192, n=8) at 17px | same |
| Sections below the hero | JA 9 (3-17, n=13); EN 6.5 (3-9, n=12) | JA 9; EN 6-7 |
| Heading block width | JA 1130px (1000-1216, n=11); EN-text 605px (500-1185, n=8) | JA 1130px; EN 605px |

### Wording

- Hero headline: JA a benefit statement, EN a positioning phrase; it names the product or category on 9 of 13 JA and 9 of 12 EN. `名刺データベースが、収益を最大化する` [Sansan]; `みんな、つかえる。` [kintone]; `The product development system for teams and agents` [Linear]
- Primary CTA: JA a free trial or a document download, 無料 on 9 of 13; EN sign up, start or download. `無料トライアル` [SmartHR]; `資料ダウンロード` [バクラク]; `Start free trial` [Plausible Analytics]
- CTA micro-copy: JA a tag above the button (7 of 13); EN a line under it (3 of 12). `＼ クレジットカード不要 ／` [freee]; `いつでも見られる！` [SmartHR]; `14 day free trial. No credit card required.` [Intercom]
- Proof line: JA an adoption count or share; EN a trust phrase. `利用企業数4,500社超` [カオナビ]; `Supported by the best.` [Tailwind CSS]; `Trusted by fast-growing companies worldwide` [Supabase]

### Variants

- JA conversion LP: a split hero with two tagged CTAs, a logo band, 8-17 sections, repeated CTA bands. SmartHR, マネーフォワード クラウド, Sansan, kintone, バクラク, カオナビ, ジョブカン, クラウドサイン, 楽楽精算.
- Product-led LP: a headline over 1-3 sentences and a large product visual, one line of logos, 3-9 capability sections. Linear, Vercel, Supabase, Plausible Analytics, Tailwind CSS, Raycast, GitHub Copilot, Datadog, Figma, Notion, BASE.
- Sign-up or letter in the hero: an email field with a start button, or a signed letter. Intercom, Asana, Basecamp.
- Portal or index page: audience tabs over card grids of products. freee, kintone.

### Rare on real screens

Icon in a tinted square above a heading 1 of 25; card around every section 0 of 25; chart legend 0 of 25; helper text under form fields 0 of 25; hero over an empty first viewport 2 of 25; subtitle describing the page 2 of 25; breadcrumb 1 of 25; hero carousel 2 of 25; autoplay video 0 of 25; video tour button 2 of 25; glass 2 of 25; gradient text 2 of 25.
