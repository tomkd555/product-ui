# OOUI が向かない画面や業務はどれで、上野氏と実務者はタスク指向 UI を選ぶ条件と OOUI 導入時の課題をどう述べているか？

## Evidence
| Claim | Publisher | URL | Published | Grade | Quote | Corroboration |
|---|---|---|---|---|---|---|
| Sociomedia (Ueno's firm) states task-based GUI is tolerated as an exception when the target object is limited and needs no selection, as with an ATM | Sociomedia | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | タスクベースの GUI が例外的に許容されるのは、ATM のように対象オブジェクトが限定的で選択の必要がない場合 | corroborated (sevendex, nextbeat state the same ATM condition) |
| Sociomedia estimates about 80% of business applications are task-based (estimate, not measured) | Sociomedia | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | 世の業務アプリケーションのおよそ8割はタスクベースのUI構成になっていると思われます | single_source |
| Sociomedia argues task procedures are modal and become harder to use when carried into a GUI | Sociomedia | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | タスクベースの操作手順はモーダルであり、これを GUI に持ち込むと使いにくくなります | single_source |
| Sociomedia advises against turning tasks into wizards; define the information objects the task needs instead | Sociomedia | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | タスクを手順化してウィザードにするのではなく、タスクに必要な情報オブジェクトを定義 | single_source |
| Sociomedia (2016) names adoption barrier: few texts explain the method and designers and programmers understand it little | Sociomedia | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | その手法について正面から解説した文献は少なく、デザイナーやプログラマーの間ではあまり理解されていない | single_source |
| Practitioner (sevendex): OOUI does not fit when the object is single, since there is nothing to compare (ATM account example) | Sevendex | https://sevendex.com/post/3676/ | 2020-12-17 (updated 2025-05-02) | C | オブジェクトが単一な場合は比べるものがなく、そもそもルールが作れません。 | corroborated |
| Practitioner (sevendex): task-oriented UI helps when the user has not yet decided what to do (travel-planning example) | Sevendex | https://sevendex.com/post/3676/ | 2020-12-17 (updated 2025-05-02) | C | ユーザーのしたい事が決まっていない場合は、タスク指向UIでユーザーに行動を当ててあげる事が有効です。 | single_source |
| Practitioner (nextbeat design): task-oriented UI fits when the operation target is always fixed | nextbeat design (note) | https://note.com/nextbeat_design/n/nbbb7efcedee0 | 2021-11-12 | C | ユーザーが行う操作の対象が常に一定である時 | corroborated (ATM-type condition matches Sociomedia) |
| nextbeat design: task-oriented UI fits when users must be guided reliably to a specific goal | nextbeat design (note) | https://note.com/nextbeat_design/n/nbbb7efcedee0 | 2021-11-12 | C | ユーザーを特定のゴールまで確実に誘導したい時 | single_source |
| nextbeat design: task-oriented UI fits when a specific operation must be done without mistakes, e.g. emergencies | nextbeat design (note) | https://note.com/nextbeat_design/n/nbbb7efcedee0 | 2021-11-12 | C | 緊急時など、特定の操作をミスなく行う必要がある時 | single_source |
| nextbeat design reports adoption pitfall: the author first equated task-oriented UI with bad usability; a paradigm must be chosen by user context | nextbeat design (note) | https://note.com/nextbeat_design/n/nbbb7efcedee0 | 2021-11-12 | C | タスク指向UIは悪ではない | single_source |
| Sociomedia/gihyo book page frames design as trade-off and says simplifying is difficult (no limit conditions stated on this page) | gihyo.jp | https://gihyo.jp/book/pickup/2020/0034 | 2020-06-25 | B | no quote | single_source |

## Falsifier
| Query | What came back | Does it change the answer |
|---|---|---|
| OOUI すべての業務アプリに適用できる タスク指向UIは不要 上野学 | No source found claiming OOUI applies to every app or that task-oriented UI has no place. Search snippets (not opened as pages) say not all apps suit OOUI and recommend per-case choice; fetched pages (Sociomedia 7279, sevendex, nextbeat) name exception conditions. Sociomedia calls the task-to-object conversion "半ば機械的" in a snippet only. | No |

## Search log
| Query | Facet | Sources adopted |
|---|---|---|
| OOUI 向かない 画面 タスク指向UI ウィザード 上野学 使い分け | definition | sevendex (via fetch) |
| オブジェクト指向UI 導入 課題 難しい 実務 ATM 券売機 タスク指向 | practice | none adopted from snippets (Gaji-Labo, freee posts seen, not opened) |
| OOUI すべての業務アプリに適用できる タスク指向UIは不要 上野学 | falsifier | nextbeat, sociomedia 10046 (fetched) |
| object-oriented UI limitations when task-based UI is better wizard one-time procedure | data | none (patents, generic results) |
| オブジェクト指向UI タスク指向 向いていない 使い分け ATM 初心者 ウィザード (allowed: sociomedia.co.jp, gihyo.jp) | definition, primary sweep | sociomedia 7279, gihyo pickup |
| Fetch sociomedia.co.jp/10046 | definition | opened; book promotion page (2020-06-05), no limit statements found |

## Gaps
- No quote found from Ueno or the book on "one-time procedure", "ticket machine", or "beginner routine task" specifically; the web search summary attributing "simple tasks can use a guided wizard" to Sociomedia was not confirmed on any opened page. The book itself (gihyo 2020; revised edition 2026) is the likely source; not read.
- The "適材適所" statement appeared only in a search summary; unverified on an opened page.
- Adoption challenges from practitioners (Gaji-Labo, freee Developers Hub, sevendex adoption detail) were seen in results but not fetched.
- Sociomedia 80% figure is an author estimate; floor of 2 independent sources is met only for the ATM condition (Sociomedia, sevendex, nextbeat).
- No scholarly query was run.
