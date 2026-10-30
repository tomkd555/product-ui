# 上野学氏は OOUI をどう定義し、どの原則（オブジェクト優先、「名詞→動詞」の操作順、タスク指向 UI との対比、モードレス）を中核に置いているか？

## Evidence
| Claim | Publisher | URL | Published | Grade | Quote | Corroboration |
|---|---|---|---|---|---|---|
| OOUI is defined as designing a UI starting from objects (things, nouns). Sociomedia's own definition. | Sociomedia (gihyo.jp book page, book by Ueno/Sociomedia) | https://gihyo.jp/book/2020/978-4-297-11351-3 | 2020-06-05 | B | オブジェクト指向ユーザーインターフェース（OOUI）とは、オブジェクト（もの、名詞）を起点としてUIを設計すること。 | corroborated (same wording on sociomedia.co.jp/10046; same author/publisher, so one origin plus the publisher's page) |
| Same definition on Sociomedia's own site, with task (verb)-origin UI as the contrast and a claim of better usability and development efficiency. | Sociomedia | https://www.sociomedia.co.jp/10046 | 2020-06-05 | B | オブジェクト（もの、名詞）を起点としてUIを設計すること | single_source (self-published by the author's firm; paraphrase of the contrast via WebFetch, only the definition string is verbatim) |
| Four principles of OOUI listed: objects perceivable and directly manipulable; objects embody their own properties and state; operation order is object selection then action selection; all objects cooperate to compose the UI. | Sociomedia / Gihyo | https://gihyo.jp/book/2020/978-4-297-11351-3 | 2020-06-05 | B | オブジェクト選択→アクション選択の操作順序 | single_source (the other three principle strings come from the same page via WebFetch; also listed in a WebSearch result summary, not independently opened) |
| Operation order: user selects the object first, then the action on it (noun then verb). | Sociomedia | https://www.sociomedia.co.jp/10241 | 2020-10-20 | B | オブジェクト選択 → アクション選択の操作順序 | corroborated (gihyo.jp page and sociomedia.co.jp/7279 state the same order) |
| 2016 Sociomedia article states the same order: object first, then action. | Sociomedia | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | ユーザーはまずオブジェクト（対象物）を選び、次にそのオブジェクトに対するアクションを選びます | corroborated (same author/firm as other rows; consistency over 2016 to 2020 is the point) |
| Contrast with task-oriented UI: in task-oriented UI the object the user wants is enclosed in the task and not visible; OOUI puts the object in front. | Sociomedia | https://www.sociomedia.co.jp/10241 | 2020-10-20 | B | タスク指向UIではユーザーの目当てであるオブジェクトがタスクの中に閉じ込められていて外から見えません。オブジェクト指向UIではオブジェクトを前面に出します。 | single_source |
| Modeless is presented as a consequence of object-first design: fewer steps and screen transitions, whole operation becomes modeless. | Sociomedia | https://www.sociomedia.co.jp/10241 | 2020-10-20 | B | 作業手順や画面遷移が減り、操作全体がモードレスになります。 | single_source |
| Task-oriented UI reverses the sequence (task first, then target object) and is described as modal; object-based design as modeless. | Sociomedia | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | no quote | single_source (WebFetch paraphrase only) |
| The 2020 gihyo page states a benefit: fewer screens, higher work efficiency, better development efficiency and extensibility versus task-origin UI. | Sociomedia / Gihyo | https://gihyo.jp/book/2020/978-4-297-11351-3 | 2020-06-05 | B | タスク（やること、動詞）を起点としたUIに比べて、画面数が減って作業効率が高まり、また開発効率や拡張性も向上する | single_source |
| Ueno also authored 『モードレスデザイン 意味空間の創造』, tying modeless to his wider work. | WebSearch result summary (booklive/booklog listings, not opened) | https://booklive.jp/focus/author/a_id/53607 | unknown | C | no quote | single_source |

## Falsifier
| Query | What came back | Does it change the answer |
|---|---|---|
| 上野学 オブジェクト指向UI タスク指向UI 使い分け 向いている 場合 例外 (plus fetch of sociomedia.co.jp/7279) | Sociomedia's 2016 page lists conditions where task-oriented UI is acceptable: limited or predetermined objects (ATM example: account selection merged with card insertion), self-contained input procedures, and cases where limiting user behaviour helps reach the goal (WebFetch paraphrase, no verbatim quote). Search results from secondary blogs (nextbeat design note, Zenn, idealump) repeat that public procedure services, internet banking and ATMs suit task-oriented UI (C grade, summarised, not opened). No Ueno statement defining OOUI by a criterion other than object-first/noun-then-verb was found; the fourth principle set (perceivable objects, state embodiment, cooperation) adds criteria beyond the order. | Partly. Conditional endorsement of task-oriented UI exists in Ueno's own Sociomedia text (exceptions for ATM-like cases). The definition also rests on four principles, with operation order as one of them, not the sole criterion. |

## Search log
| Query | Facet | Sources adopted |
|---|---|---|
| 上野学 OOUI オブジェクト指向UI とは 定義 名詞 動詞 タスク指向 | definition | sociomedia.co.jp/10046, gihyo.jp book page |
| オブジェクト指向UI ソシオメディア 上野学 モードレス オブジェクト 先に選ぶ | definition/practice | sociomedia.co.jp/10241, 7279, booklive listing |
| 上野学 オブジェクト指向UI タスク指向UI 使い分け 向いている 場合 例外 | falsifier | sociomedia.co.jp/7279 (fetched); secondary blogs seen, not adopted |
| Manabu Ueno object-oriented UI Sociomedia definition (allowed_domains sociomedia.co.jp, gihyo.jp, ooui.jp) | definition (primary sweep) | no new source beyond above sociomedia pages |

## Gaps
- Data facet: no figures or scale found (book sales, adoption counts). Not searched beyond the four queries; a query on sales or adopter case counts would settle it.
- Practice facet: no practitioner reports opened. Secondary blogs (Zenn, note.com, Yahoo! Japan Tech Blog, Qiita) appeared in results but were not fetched; they are C grade.
- Quotes from WebFetch were requested as verbatim but the tool mixed paraphrase in; only strings in Japanese quotation form are recorded as quotes. Pages were not re-checked against raw text.
- The falsifier's exception conditions (ATM etc.) have no verbatim quote; verify on https://www.sociomedia.co.jp/7279 directly.
- The book 『オブジェクト指向UIデザイン』 (Gihyo, 2020) itself was not read; its definitions of levels (レベル0 to 3) and the 'mode' treatment were not checked.
- No scholarly source; sub-question is a definitional one, so none was sought.
- Independent origins: effectively 1 (Sociomedia, with Gihyo as publisher of its book). Floor of 2 independent sources is unmet; only secondary blogs (not adopted) echo it.
