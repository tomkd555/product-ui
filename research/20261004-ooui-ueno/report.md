# Manabu Ueno's OOUI — scan (as of 2026-10-04)

Purpose: gather what Ueno and Sociomedia state about object-oriented UI (OOUI), as material for adding OOUI to the product-ui skill as a selectable design approach.

Scope: Ueno's and Sociomedia's own texts, the publisher's page of 『オブジェクト指向UIデザイン』 (2020), practitioner articles in Japanese, and one academic comparison. Assumptions: the reader maintains product-ui; "selectable" means the skill applies OOUI when a setting or an intake answer asks for it. Materials: none supplied.

## Question analysis

- Decision: the product-ui maintainer decides which OOUI rules enter the skill, at which pipeline step they apply, and under which conditions the skill offers OOUI or a task-oriented structure.
- Question type: descriptive, with a prescriptive tail (what the sources allow the skill to encode).
- Presuppositions: OOUI is concrete enough to write as steps and checks — verify (SQ2). OOUI suits only part of the screens the skill builds, so a choice is needed — verify (SQ3).
- Useless answer: a history of OOUI and a list of its praised benefits, with no rule the skill could apply or check.

Sub-questions:

1. How does Ueno define OOUI, and which principles sit at its core?
2. How does the book define the design procedure, at a grain a procedure and checks can carry?
3. Which screens suit a task-oriented structure, and what do adopters report as difficulties?
4. How much quantitative evidence backs the claimed effect, and has OOUI already been written into an agent skill?

## Answer

OOUI, as Ueno and Sociomedia define it, designs a UI starting from objects (things, nouns) and rests on four principles: objects are perceivable and directly manipulable, objects embody their own properties and state, the operation order is object selection then action selection, and all objects cooperate to compose the UI [S1]. The book fixes a three-step procedure — object extraction, views and navigation, layout patterns — and the surrounding texts give rules concrete enough for a skill: an object test, a collection view and a single view per object, noun-form root navigation, and actions placed on the object [S1][S2][S3]. Ueno's own text names two exceptions where a task-based GUI is tolerated: a limited object that needs no selection (the ATM) and a self-contained procedure offered as a fixed input flow [S1]; this is the condition a "selectable" switch can key on. The effect claim (screen count down to one fifth to one twentieth) is the vendor's experience figure with one origin [S1]. Confidence: medium — the sources agree and no falsifier search reversed the direction, while the core texts share one origin (Sociomedia), the object test, the layout step and the iteration statement rest on grade C notes, and the book body was left unread.

Mechanism: Sociomedia's argument is that a task carried into a GUI becomes a modal procedure that hides the object the user came for, while an object shown up front lets the user pick the target and then the action in any order, so one collection view and one single view serve every task on that object and the screen count falls [S1]. A 1990 doctoral study supports the direction and locates the cause: the object-oriented interface was easier to use, and the command order tested alone showed no inherent difference, so the benefit comes from visible objects and their properties [S8]. The answer rests on one assumption: the screen manages a set of same-kind objects that the user chooses among. Where that fails, the sources themselves point to a task-oriented flow [S1][S6][S7].

Reading for the decision (inference of this scan, beyond what the sources state): the encodable core is (a) an object list in the brief, each object passing the three-part test, (b) a collection view and a single view per main object, (c) root navigation in noun form, (d) verbs only as actions on a selected object. Items (c) and (d) are mechanically checkable on labels; (a) and (b) need a reviewer. Ueno's statement that the method resists reduction to mechanical rules [S5] argues for keeping the judgment calls with the independent review.

## Findings

### SQ1 — Definition and core principles

- Definition: 「オブジェクト（もの、名詞）を起点としてUIを設計すること」 [S1].
- Four principles, as listed on the book page: perceivable and directly manipulable objects; objects embody their properties and state; object selection then action selection; all objects cooperate to compose the UI [S1]. The operation order is one of four.
- The same order appears in Sociomedia's 2016 and 2020 texts [S1].
- Contrast: in a task-oriented UI the object is enclosed in the task and hidden from outside; OOUI puts the object in front [S1] (single source).
- Modeless operation is presented as a consequence: fewer steps and screen transitions [S1] (single source).
- Falsifier: searched for a Ueno definition by a criterion other than the operation order, and for conditional endorsement of task-oriented UI. Came back: the definition carries four principles, and Sociomedia's 2016 text tolerates task-based GUI in named exceptions. It refines the answer and leaves its direction unchanged.

### SQ2 — Procedure at the grain of steps and checks

- The book's Chapter 2-6 names three basic steps: ステップ1 オブジェクトの抽出, ステップ2 ビューとナビゲーションの検討, ステップ3 レイアウトパターンの適用; Chapter 3 works through each, and 3-6 is titled 「タスクをどう扱うか」 [S1]. The steps map to model, interaction and presentation [S1][S2].
- Object test: expressible as a countable noun, manageable as a set of the same kind, carrying common actions [S2] (single source, grade C).
- Two view types: collection (a set of objects of one type, key attributes) and single (one object, more attributes) [S2][S3]. Selecting an object in a collection view shows its single view [S1].
- Root navigation items take noun form and follow the object-based syntax [S1]; verbs sit inside the object's screen or as action buttons [S4].
- The object-then-action syntax is kept across the whole application [S1].
- Create and update: pressing 変更 on an object or 新規 above the list turns the single-view pane into an edit form [S1] (single source).
- Layout: UI parts are chosen from a pattern collection by purpose [S3] (single source, grade C).
- The steps are iterated in any order [S2], and Ueno describes design as a round trip between whole and part [S1].
- Falsifier: searched for a statement that the procedure differs from three steps or resists fixing as rules. Came back: the three steps stand; the steps are iterated freely; in an interview Ueno says design needs abductive judgment beyond mechanical rules [S5]. It limits what a one-pass checklist can claim and leaves the three-step frame intact.

### SQ3 — Where task-oriented structure fits, and adoption difficulties

- Sociomedia's exceptions: a limited object needing no selection (ATM), and a self-contained procedure offered as a fixed input flow [S1].
- Sociomedia advises defining the information objects a task needs in place of turning the task into a wizard [S1] (single source).
- Sociomedia estimates that about 80% of business applications are task-based; the figure is the firm's impression from the hundreds of applications it has reviewed [S1] (single source, estimate).
- Practitioners add conditions for task-oriented UI: a single object [S6], a target that is always fixed [S7], a user who has yet to decide what to do [S6], reliable guidance to one goal [S7], and operations that must be done without mistakes, as in emergencies [S7] (grade C; the fixed-object condition is corroborated by S1).
- Adoption difficulties: in 2016 Sociomedia noted that texts explaining the method were scarce and that designers and programmers understood it little [S1]; one practitioner reports first treating task-oriented UI as bad and later choosing by user context [S7].
- Falsifier: searched for a claim that OOUI fits every business application and task-oriented UI has no place. Came back: no such claim; every opened page names exceptions. The answer stands.

### SQ4 — Effect evidence and prior art

- Sociomedia states that the screen count usually falls to one fifth to one twentieth; the page gives no dataset [S1] (single source, interested party).
- One reported case: a 12-screen system became a single-page application [S1] (single source).
- Selby's 1990 UCL thesis compared an object-oriented interface (Lisa) with a non-object-oriented one (TopView) and found the former easier to use; two experiments on command order alone found no inherent difference, and the thesis attributes the advantage to characteristics of objects [S8] (single source, 36 years old; no newer controlled study surfaced).
- Prior art: an agent skill `ooui-design` (AyatoAshihara/Scribo) lists six steps — extract objects, map relationships, design collection and single views, attach actions to objects, build navigation around object types, validate with a checklist [S9] (grade C, read through a listing page).
- The English-language sibling, OOUX, is taught as ORCA: objects, relationships, calls-to-action, attributes [S10].
- Falsifier: searched for controlled comparisons of noun-verb and verb-noun order and for quantitative refutations of OOUI. Came back: Selby's finding on command order (above) and practitioner caveats; no quantitative refutation. It moves the weight from operation order to visible objects and leaves the answer's direction unchanged.

## Sources

| # | Source | URL | Published | Grade | Quote | Corroboration |
|---|---|---|---|---|---|---|
| S1 | 技術評論社, book page of 『オブジェクト指向UIデザイン』 (text by Sociomedia, Ueno, Fujii) | https://gihyo.jp/book/2020/978-4-297-11351-3 | 2020-06-05 | B | 「オブジェクト選択→アクション選択の操作順序」; 「ステップ1. オブジェクトの抽出」「ステップ2. ビューとナビゲーションの検討」「ステップ3. レイアウトパターンの適用」; 「通常、画面数は5〜20分の1に減ります。」 | steps corroborated by S2, S3; figure single_source |
| S1 | Sociomedia, book announcement | https://www.sociomedia.co.jp/10046 | 2020-06-05 | B | 「オブジェクト（もの、名詞）を起点としてUIを設計すること」 | same origin |
| S1 | Sociomedia, OOUI article | https://www.sociomedia.co.jp/10241 | 2020-10-20 | B | 「タスク指向UIではユーザーの目当てであるオブジェクトがタスクの中に閉じ込められていて外から見えません。」; 「作業手順や画面遷移が減り、操作全体がモードレスになります。」 | single_source |
| S1 | Sociomedia, task-based and object-based GUI article | https://www.sociomedia.co.jp/7279 | 2016-12-08 | B | 「タスクベースの GUI が例外的に許容されるのは、ATM のように対象オブジェクトが限定的で選択の必要がない場合…や、自己完結的な手続きを定型入力フローとして提供する場合です。」; 「世の業務アプリケーションのおよそ8割はタスクベースのUI構成になっていると思われます。」; 「タスクに必要な情報オブジェクトを定義」 | ATM condition corroborated by S6, S7; 8割 single_source |
| S1 | Sociomedia, 上野学「OOUI の目当て」 | https://www.sociomedia.co.jp/8740 | 2019-03-05 | B | 「するとナビゲーション項目は名詞形の表現になり、オブジェクトベースの操作構文に沿ったものになります。」; 「コレクションビューの中でユーザーがひとつのオブジェクトを選ぶと、その内容を表示するシングルビューが表示される」; 「シングルビュー部分のペインが編集用のフォームに変わるようにします。」; 「改善前に12画面もあったシステムが、合理的に作業の全体を把握できるシングルページアプリケーションになったのです。」 | noun navigation corroborated by S4; rest single_source |
| S1 | Sociomedia, OOUI consulting service page | https://www.sociomedia.co.jp/8653 | unknown | B | 「画面数は5〜20分の1に減ります。」 | single_source |
| S2 | Speaker Deck, uenitty, "Design process of OOUI" | https://speakerdeck.com/uenitty/design-process-of-ooui | 2020-09-30 | C | 「数えられる名詞として表せる・同種の集合として管理され得る・共通のアクションを持っている」; 「これらを順不同で繰り返し調整し、全体としてのまとまりを作り上げる」 | steps corroborated by S1, S3; object test single_source |
| S3 | note, yiio, reading notes on the book | https://note.com/yiio/n/n646b6a031626 | 2021-08-25 | C | 「用途に応じたUIパーツをパターン集から選び、配置していきます」 | view types corroborated by S2 |
| S4 | iret.media | https://iret.media/198776 | 2026-06-11 | C | 「「オブジェクトの画面内に配置する」「アクションボタンとして設置する」のがOOUIの鉄則です。」 | corroborated by S1 |
| S5 | ekrits, interview 上野学「オブジェクト指向デザインの道具論」 | https://ekrits.jp/2020/10/3914/ | 2020-10-28 | C | no quote | single_source |
| S6 | Sevendex | https://sevendex.com/post/3676/ | 2020-12-17 (updated 2025-05-02) | C | 「オブジェクトが単一な場合は比べるものがなく、そもそもルールが作れません。」 | corroborated by S1, S7 |
| S7 | note, nextbeat design | https://note.com/nextbeat_design/n/nbbb7efcedee0 | 2021-11-12 | C | 「ユーザーが行う操作の対象が常に一定である時」; 「ユーザーを特定のゴールまで確実に誘導したい時」 | fixed-object condition corroborated by S1, S6 |
| S8 | Selby, C. M. J., "An Investigation of Object-oriented Interfaces for Human Computer Interaction", PhD thesis, University College London | https://discovery.ucl.ac.uk/id/eprint/10107640/1/An_investigation_of_object-ori.pdf | 1990-08 | A | "These studies suggest there is no inherent difference between the two command sequences tested." | single_source |
| S9 | skills.lc listing of AyatoAshihara/Scribo `ooui-design` skill | https://skills.lc/AyatoAshihara/Scribo/ayatoashihara-scribo-github-skills-ooui-design-skill-md | unknown | C | "Use when designing information architecture, navigation, screen flows, or restructuring task-oriented UI into object-oriented patterns." | single_source |
| S10 | Sophia V. Prater, Medium | https://sophiavux.medium.com/in-the-approach-to-ooux-that-i-teach-we-call-the-process-orca-e226dfdd015a | unknown | C | "That stands for objects, relationships, calls-to-action, and attributes." | single_source |

## Re-fetch

| Figure | URL | Sentence returned | Outcome |
|---|---|---|---|
| Three-step procedure | https://gihyo.jp/book/2020/978-4-297-11351-3 | 「ステップ1. オブジェクトの抽出」「ステップ2. ビューとナビゲーションの検討」「ステップ3. レイアウトパターンの適用」 | confirmed |
| Exceptions tolerating task-based GUI | https://www.sociomedia.co.jp/7279 | 「タスクベースの GUI が例外的に許容されるのは、ATM のように対象オブジェクトが限定的で選択の必要がない場合（…）や、自己完結的な手続きを定型入力フローとして提供する場合です。」 | confirmed |
| Screen count 5〜20分の1 | https://www.sociomedia.co.jp/8653 | 「画面数は5〜20分の1に減ります。」 | confirmed |

The four sentences cited from https://www.sociomedia.co.jp/8740 were also fetched again and returned as quoted. The S8 sentences were read from the PDF's abstract page directly.

## Not covered

- The book body (Chapters 2, 3 and 3-6 「タスクをどう扱うか」) was left unread; the selection criteria for root navigation, the action-placement variants and the layout patterns rest on Ueno's 2019 blog post and grade C notes. Reading those chapters, or the 2026 revised edition the collector saw listed, would settle them.
- Core definitional claims share one origin (Sociomedia, with its publisher); the floor of two independent sources is unmet for SQ1.
- S5 (the ekrits interview) carries no quote, so the "resists mechanical rules" statement is a paraphrase.
- The effect figure has no dataset behind it, and the only controlled comparison dates from 1990 on desktop systems.
- The Scribo skill's SKILL.md was read through a listing page; its date and the quality of its output are unknown. Practitioner adoption reports from Gaji-Labo and freee appeared in results and were left unopened.
- A research-team run would add the book's own text, verified quotes, and a search for recent controlled studies.
- This report reflects what these searches surfaced, which differs from the balance of informed opinion.
