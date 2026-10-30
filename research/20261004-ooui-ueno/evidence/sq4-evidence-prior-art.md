# SQ4 — Effect evidence and prior art for encoding OOUI in an agent skill

Sub-question: OOUI の効果を示す定量的な証拠はどこまであり、OOUI を AI エージェントのスキルや手順に書いた先行例はあるか？

Falsifier: 対照実験が「名詞→動詞」の操作順そのものに効果がないと示している、または OOUI の効果を定量的に否定する研究がある。

As of: 2026-10-04. Collected in the main session under the collector's floors.

## Sources

| Claim | Publisher | URL | Published | Grade | Quote | Corroboration |
|---|---|---|---|---|---|---|
| Sociomedia states that applying OOUI usually cuts the screen count to one fifth to one twentieth. The figure is the firm's own consulting experience; the page gives no dataset. | Sociomedia (OOUI consulting service page) | https://www.sociomedia.co.jp/8653 | unknown | B (interested party) | 「画面数は5〜20分の1に減ります。設計はシンプルになり、開発工数は低減され、保守性も高まります。」 | single_source (the gihyo book page repeats the same origin) |
| The book's publisher page carries the same figure and lists the qualities said to improve: operation efficiency, learning efficiency, business efficiency, UI extensibility. | 技術評論社 (book page, text supplied by the authors) | https://gihyo.jp/book/2020/978-4-297-11351-3 | 2020-06-05 | B (same origin as Sociomedia) | 「通常、画面数は5〜20分の1に減ります。」 | same origin as row 1 |
| Ueno reports one redesign in which a 12-screen system became a single-page application after OOUI was applied. | Sociomedia, 上野学「OOUI の目当て」 | https://www.sociomedia.co.jp/8740 | 2019-03-05 | B (interested party) | 「改善前に12画面もあったシステムが、合理的に作業の全体を把握できるシングルページアプリケーションになったのです。」 | single_source (one case) |
| A UCL doctoral thesis compared user performance on an object-oriented interface (Apple Lisa) and a non-object-oriented one (IBM TopView) and found the object-oriented interface easier to use. | Selby, C. M. J., "An Investigation of Object-oriented Interfaces for Human Computer Interaction", PhD thesis, University College London | https://discovery.ucl.ac.uk/id/eprint/10107640/1/An_investigation_of_object-ori.pdf | 1990-08 | A (examined doctoral thesis; 36 years old, kept because no newer controlled study surfaced) | "It determines that object-oriented interfaces are easier to use and that the dimensions for classifying object-oriented interfaces have consequences for user performance." | single_source |
| The same thesis ran two experiments on command-sequence syntax alone and found no inherent difference between the two orders; it attributes the observed advantage to characteristics of the objects. | Selby 1990 (as above) | https://discovery.ucl.ac.uk/id/eprint/10107640/1/An_investigation_of_object-ori.pdf | 1990-08 | A | "These studies suggest there is no inherent difference between the two command sequences tested." | single_source |
| An agent skill for OOUI design already exists: it names six steps (extract objects, map relationships, design collection and single views, attach actions to objects, build navigation around object types, validate with a checklist). | skills.lc listing of AyatoAshihara/Scribo `ooui-design` SKILL.md | https://skills.lc/AyatoAshihara/Scribo/ayatoashihara-scribo-github-skills-ooui-design-skill-md | unknown | C | "Object-Oriented UI (OOUI) design specialist applying HIG principles. Use when designing information architecture, navigation, screen flows, or restructuring task-oriented UI into object-oriented patterns." | single_source |
| The English-language sibling method, OOUX, is taught as the ORCA process: objects, relationships, calls-to-action, attributes. | Sophia V. Prater (Medium) | https://sophiavux.medium.com/in-the-approach-to-ooux-that-i-teach-we-call-the-process-orca-e226dfdd015a | unknown | C | "we call the process ORCA. That stands for objects, relationships, calls-to-action, and attributes." | corroborated by ooux.com listing (same origin) |

## Falsifier

| Query | What came back | Changes the answer? |
|---|---|---|
| `object-oriented user interface usability study task-oriented comparison experiment noun-verb verb-noun` | Selby 1990: the whole object-oriented interface was easier to use, while the command order tested in isolation showed no inherent difference. | Partly. The effect belongs to visible objects and their properties; the operation order alone carries no measured effect. A skill rule should therefore require objects to be shown as lists and detail views, with the action order as a consequence. |
| `OOUI 批判 OR 限界 OR 疑問 効果 根拠 定量 検証 オブジェクト指向UI 本当に使いやすいのか` | Practitioner articles naming cases where task-oriented UI fits (a single object, an object the user need not choose, an object still undefined) and implementation drift toward the easier build. No quantitative study surfaced. | No. It confirms that the quantitative base is thin. |

## Search log

1. `オブジェクト指向UI OOUI 効果 事例 画面数 削減 ソシオメディア` — found the 5〜20分の1 figure (Sociomedia 8653, gihyo).
2. `object-oriented user interface usability study task-oriented comparison experiment noun-verb verb-noun` — found Selby 1990 (falsifier and academic supplement).
3. `OOUI Claude Code skill OR プロンプト OR 生成AI オブジェクト指向UI 設計 エージェント` — general design-skill articles only; none on OOUI.
4. `OOUX ORCA process Sophia Prater objects relationships CTAs attributes AI prompt` — ORCA definition.
5. `"OOUI" OR "オブジェクト指向UI" LLM OR ChatGPT OR Claude オブジェクト抽出 プロンプト UI生成 やってみた` — nothing relevant.
6. `OOUI 批判 OR 限界 OR 疑問 効果 根拠 定量 検証 オブジェクト指向UI 本当に使いやすいのか` — falsifier, see above.
7. `OOUI 生成AI UI設計 オブジェクト抽出 AIに任せる zenn OR qiita OR note 2025 OR 2026` — nothing relevant.
8. `github OOUI skill SKILL.md object-oriented UI design agent skill "OOUI"` — found the Scribo `ooui-design` skill.

Fetched: sociomedia.co.jp/8740, sociomedia.co.jp/8653, gihyo.jp book page, the UCL PDF (pages 1–6 read directly), skills.lc listing.

## Gaps

- The 5〜20分の1 figure has one origin (Sociomedia) and no published dataset; it is the vendor's experience claim.
- The only controlled comparison found dates from 1990 and compares desktop systems; nothing recent on web applications surfaced.
- The Scribo skill was read through a listing page; its SKILL.md on GitHub was left unopened, and its publication date is unknown.
- No published account of an LLM running Ueno's three-step process surfaced in Japanese or English.
