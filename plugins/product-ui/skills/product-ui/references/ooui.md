# Object-oriented UI (OOUI)

Source of record for the screen structure the skill builds when `meta.structure` in `tokens.json` is `ooui`. The method is that of 上野学 and ソシオメディア in 『オブジェクト指向UIデザイン──使いやすいソフトウェアの原理』 (技術評論社, 2020; the revised edition of 2026 keeps the text). IBM's OVID, Sophia Prater's object mapping and the page patterns of enterprise design systems supply the parts the book's public record leaves open: the states of an object, the classes of its properties and the place of each action. Checks C17 and C19 in `references/ui-copy.md` are the mechanical part; the structure questions in `assets/brief.template.md` carry the rest to the Step 5 reviewer.

Read it at Step 0 for the structure question, at Step 3 before any layout or navigation exists, and when C17 fires. `references/interaction.md` settles how the views behave once they exist.

## What it settles

OOUI designs a screen from objects: the things the user came for, each named by a noun. The book's publisher page lists four principles.

1. The user can perceive each object and act on it directly.
2. An object shows its own properties and state.
3. The user selects the object first and the action second.
4. All objects work together to compose the interface.

A screen built around a task fixes the order of work and hides the object inside it. With the objects in front, one collection view and one single view serve every task on an object, so the product needs fewer screens and the user chooses the order.

## Choosing the structure

Step 0 records the answer in `meta.structure`; the request usually points to one of the two.

| `meta.structure` | Fits when | Typical screens |
|---|---|---|
| `ooui` | The product manages sets of same-kind objects, and the user chooses which one to act on | An admin console, a SaaS workspace, a CRM, an inventory, a ticket tracker; a catalogue or search results a visitor browses and saves (a job board, a shop, a property search) |
| `task` | The object is fixed and needs no selection, or the screen is a self-contained procedure offered as a fixed input flow | An ATM-style terminal, sign-up, checkout, an application form, an onboarding flow, a landing page, a monitoring screen of one fixed subject, a settings screen, the entry screen of one business document asked for by itself (受注伝票の入力) |

The two `task` conditions are the exceptions ソシオメディア names for a task-oriented UI. Practitioners add two more: a user who must be led to one goal with certainty, and an operation that must run without a mistake, as in an emergency.

One product can hold both: an `ooui` application keeps a task flow for a case in the `task` row, such as its sign-up. A request for a collection and the form that adds to it (an expense list and a new claim) is `ooui`: the form is the create view of the object, and its 入力, 確認 and 完了 steps are a task flow the brief names. Name each such flow in `ui-brief.md` so the reviewer reads it as intended.

When `meta.structure` is `task`, the screen follows the order of the procedure, C17 stays off, and the rest of this file is skipped.

## The three steps

Work through these before writing markup, in any order the work needs: when a later step exposes a gap in an earlier one, go back and settle it there. The object table is a check on the screens as well as their source: a finished screen is compared with it (the structure questions), and a mismatch is settled in the table first.

### Step 1: Extract the objects

Start from the tasks the reader does most often (`meta.users[].job`, the request, the existing screens): OVID takes the most frequent tasks first, because they name the most concrete objects. List the nouns in them. A noun is an object when it passes all three tests:

- it is a countable noun (顧客, 請求書, プロジェクト),
- the product manages it as a set of the same kind,
- its instances share the same actions.

A word that fails is an action (登録, 検索), which acts on an object; a value (金額, 期日), which is a property of one; or a screen name (一覧, 詳細), which is a view of one. A verb that only looks (確認, 表示, 閲覧, 参照, 照会) is none of these: showing the object does it, so it adds no action. Where the domain uses the same word for a step that changes the record (受注確認 as accepting an order, 承認前の確認 as a sign-off), it is an action with a state behind it; the request's wording and the object's states decide which.

Look for the objects the tasks imply and leave unnamed: the 明細 of a 請求書, the 添付ファイル of a 申請, the 履歴 of a 契約. A property that holds several values, or a part with a state of its own, is such an object, and one missed here sends the later steps back. The objects are the user's: they follow what the user counts and chooses, and they may differ from the tables and classes behind the screen.

For each object, write into the brief's Structure table:

| Entry | Holds |
|---|---|
| Name | One noun, kept across the product; settle a competing pair in `voice.terms` |
| Properties | In three classes: what identifies a record (the name or number a reader knows it by), what describes it (status, dates, amounts, owner), and the related objects it contains (明細, コメント, 添付ファイル). The `## Objects` table ranks the first two by the reader's job |
| States | The states a record moves through (下書き, 申請中, 承認済み, 差戻し), in order, with the word the screen prints for each (`references/ui-copy.md`, Status labels) |
| Actions | For each state, the actions a reader may take on a record in it: 申請中 allows 取り下げ, 下書き allows 編集 and 削除. An action a state excludes is left off the screen in that state. Each state short of the last offers the action that moves the record on: 差戻し allows 再申請, 確認待ち allows 確認. A state the product computes from the record's figures (達成, 期限切れ) has no action of its own |
| Relations | Each related object with its multiplicity: one (a 受注 has one 取引先) or many (a 取引先 has many 受注) |

The objects the user comes to the product for are the main objects. The split has no fixed rule and follows the product's area of concern; an object that lives inside another's single view (明細 inside 受注) is a sub object and gets no collection view of its own.

### Step 2: Views and navigation

- Each main object gets a collection view, showing the set with the key properties, and a single view, showing one object with the rest of its properties.
- Choosing an object in the collection view opens its single view.
- A relation becomes a call between views. From a single view, a relation to many shows a collection of the related objects (the single view of a 取引先 shows that customer's 受注), and a relation to one is a link to that object's single view.
- Every mention of an object whose single view the build holds is a link to that view: a 取引先 name in a 受注 row, an 担当者 in a property list. An object printed as plain text in one view and as a record in another is a broken object. An object whose single view is outside the build is plain text in every view, or a link to the collection filtered by it where the collection holds that filter (an 担当者 in a row opens the rows of that 担当者).
- One object looks the same wherever it appears: the same name, the same identifier, the same status words, the key properties in the same rank. Where one list holds two kinds of object, each row shows its kind.
- Root navigation lists the main objects and nothing else, each as its bare noun. A shop's header band of categories (冷蔵庫, 洗濯機) is a row of filtering groups over the one product collection, and each links to that collection with the filter applied. Where the request names no top page, `/` opens the collection of the first main object. In an application, a suffix that names a function or a view (管理, 一覧, 登録, 編集, 閲覧, 参照) is left off the object's name. C17 reports an item that names a task and C19 the `<noun>管理` shape; the other suffixes stay with the builder, because production screens print them: of 92 Japanese screens, 20 hold a navigation item ending in 一覧, most of them public and marketing sites (`research/20261106-real-screens/data/words.csv`).
- An action sits on the object it acts on: in the row or in the single view, after the object is selected. Creation sits at the collection, above the list, labelled as `references/ui-copy.md` gives a page's primary action (「受注を登録」, 「経費申請を作成」). Editing turns the single view into a form.
- A collection and the single view its rows open are built together, unless the intake's Structure answer leaves the record out (`SKILL.md`, Step 0). A view that stays outside the build keeps its row in the brief's Structure table and gets no control on the screen: a collection without its single view shows its rows without links, 「新規」 waits for the create form, and the navigation lists the objects whose collection the build holds. The `Built files` line lists what this build holds, and the hand-over lists the controls left off.
- The object-then-action order holds across the whole application.

### Tasks

A task the request names (「未出荷の受注を確認する」, 「月末に請求書を送る」) gets no entry of its own in the navigation. It lands on its object, in one of the six places the book names:

| Place | The task becomes |
|---|---|
| Content | a property the views show (出荷予定日 in the row) |
| Display form | the layout of the collection for that work: a table to compare, a calendar by date, a board by state |
| Action | an action on the object (出荷を手配), offered in the states that allow it |
| Initial value | the default of a filter or a form field (担当者 preset to the reader) |
| Template | a new object started from a copy or a pattern (前回の申請をコピー) |
| Filtering group | a named preset of the collection (未出荷, 今日出荷, 自分の担当), as tabs or saved filters above the rows |

Where several tasks work on one object, the one collection view serves them all and switches by preset. Check the plain list against each task the reader has: a task that needs a property or an order the list lacks gets it in that task's preset. A list of items waiting for the reader (承認待ち, 未処理) is such a preset: SAP's worklist is a variant of the list page.

### Step 3: Layout patterns

Map each view onto a component from `references/components.md` or the preset's component reference, after the composition plan in `references/composition.md` has settled the screen's dominant element, reading order and density. The conditions come from the design systems named under Sources; the mapping is this skill's own.

| View | Layout | When |
|---|---|---|
| Collection | A table | The reader compares objects by their properties |
| Collection | A list | The reader scans by name, or the screen is narrow: a table needs width, and at 375px its rows fold into list items, each with the name and the properties the reader decides by. The fold is CSS on the one table: each row becomes a block, each cell prints its header from a `data-label` attribute, and the columns the reader does not decide by are hidden; a second markup for the list is left out |
| Collection | A card grid | Objects recognised by image and browsed (the container rule in `references/composition.md`) |
| Single, beside its collection | The Master-Detail pattern in two panes at desktop width, a separate page at 375px | The request says the reader moves through many records in a row; a page of its own is the default |
| Single, on its own, one column | A page with the object's name as the heading and its properties in sections | The properties stand in parallel |
| Single, on its own, two columns | The body in the main column, the properties in a rail | Main and secondary information differ greatly in amount and importance |
| Create and edit | The single view as a form, in the same pane or page | |

| Action | Place |
|---|---|
| Create | The trailing end of the collection's title row |
| An action on one row, frequent and reversible | The trailing column of the row; that column stays in view when the table scrolls sideways |
| An action on many records | A bar that appears with the selection, above the rows; built only where a task acts on many records at once |
| Actions on one object | Beside the title of the single view: the main one as a button, the others in one menu |
| Save and cancel | With the form: in display mode the actions sit by the title, and in edit or create mode the form's own foot holds 保存 and キャンセル |
| Delete | In the single view's menu. After a deletion the reader is back at the collection. `references/interaction.md` settles the confirmation |

## What the checks cover

上野学 treats design as judgement past mechanical rules, so the label checks are scripted and the rest goes to a reader of the rendered screen.

- C17 in `check_copy.py`, an error, reports a navigation item ending in an unambiguous action word; C19, a warning, reports the `<noun>管理` shape. 「申請」「承認」 and the like go to the reviewer.
- C10 checks one name per object for the names in `voice.terms`.
- The structure questions in `assets/brief.template.md` carry each rule above to the reviewer: noun navigation (1), a collection and a single view joined by selection (2), each action on its object after selection (3), one name and one set of key properties per object (4), every sequence a flow the `task` row admits (5), every mention of an object a link to its single view (6), each state's word and actions as the table gives them (7), and each task landed on its object (8).

## Sources

| Source | What it settles here |
|---|---|
| ソシオメディア、上野学、藤井幸多『[オブジェクト指向UIデザイン](https://gihyo.jp/book/2020/978-4-297-11351-3)』（技術評論社、2020年; [改訂新版](https://gihyo.jp/book/2026/978-4-297-15716-6)、2026年） | The four principles and the three steps |
| 上野学「[OOUI – オブジェクトベースのUIモデリング](https://www.sociomedia.co.jp/7279)」（2016年） | The two conditions under which a task-oriented UI is tolerated |
| 上野学「[OOUI の目当て](https://www.sociomedia.co.jp/8740)」（2019年） | Noun-form navigation, the collection and single views, the edit form in the single view, the object-then-action order |
| uenitty「[Design process of OOUI](https://speakerdeck.com/uenitty/design-process-of-ooui)」（2020年） | The three tests for an object |
| uenitty「[Practice of OOUI design](https://speakerdeck.com/uenitty/practice-of-ooui-design)」（2020年） | Verbs that only look are no action; the call from a single view by multiplicity; the collection switched by task with no task entry; the split of main objects by area of concern |
| 同書の読書記録（[silloi-books](https://scrapbox.io/silloi-books/%E3%82%AA%E3%83%96%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E6%8C%87%E5%90%91UI%E3%83%87%E3%82%B6%E3%82%A4%E3%83%B3%E3%80%80%E4%BD%BF%E3%81%84%E3%82%84%E3%81%99%E3%81%84%E3%82%BD%E3%83%95%E3%83%88%E3%82%A6%E3%82%A7%E3%82%A2%E3%81%AE%E5%8E%9F%E7%90%86)、[leony](https://note.com/leony/n/na16e133aa2ac)、[yiio](https://note.com/yiio/n/n646b6a031626)） | The six places a task goes; multiplicity on main objects; navigation of objects alone, with no suffix; relations drawn as links between views |
| しもしも の演習記録（[note](https://note.com/shimo_shimo/n/nfcbab539de40)、2020年） | An implicit object missed at extraction sends later steps back |
| UXの電球「[OOUI をチームに浸透させる](https://uxman2020.substack.com/p/one-way-to-permeates-ooui-to-your-designers)」（2023年） | The object model as a check on finished screens; objects kept apart from table design |
| D. Roberts et al., [OVID tutorial](https://www.chi1997.chistatic.hosting.acm.org/proceedings/tutorial/djr.html), CHI 97 | The most frequent tasks first; views per object; states and the interactions each allows |
| S. V. Prater, [OOUX: A Foundation for Interaction Design](https://alistapart.com/article/ooux-a-foundation-for-interaction-design/) and [UX for Lizard Brains](https://alistapart.com/article/ux-for-lizard-brains), A List Apart | Object elements (core content, metadata, nested objects); the shapeshifting, masked and broken object |
| SmartHR Design System [ページレイアウト](https://smarthr.design/products/design-patterns/page-layout/), [共通設定](https://smarthr.design/products/design-patterns/main-admin-core-features/), [テーブル](https://smarthr.design/products/design-patterns/smarthr-table/), [一括操作](https://smarthr.design/products/design-patterns/table-bulk-action/) | The conditions for a table, a list, one column and two columns; actions beside the title with the rest in a menu; row actions in the trailing column; the bulk-action area |
| SAP, Fiori elements [floorplans](https://github.com/SAP-docs/sapui5/blob/main/docs/06_SAP_Fiori_Elements/standard-floorplans-797c323.md) and [actions on the object page](https://github.com/SAP-docs/sapui5/blob/main/docs/06_SAP_Fiori_Elements/displaying-actions-on-the-object-page-f65e8b1.md) | The list page with the object page; the worklist as a variant; actions by the title in display mode and at the foot in edit mode |
| Shopify Polaris, [Page](https://raw.githubusercontent.com/Shopify/polaris/main/polaris.shopify.com/content/components/layout-and-structure/page.mdx) and [Resource list](https://raw.githubusercontent.com/Shopify/polaris/main/polaris.shopify.com/content/components/lists/resource-list.mdx) | The list's job of finding an object and reaching its page; one primary action, the others secondary |
| IBM Carbon, [Common actions](https://carbondesignsystem.com/patterns/common-actions/) | The return to the list after a deletion |
| nextbeat design の記事（[note](https://note.com/nextbeat_design/n/nbbb7efcedee0)、2021年） | The two practitioner conditions for a task flow |
| 上野学「[オブジェクト指向デザインの道具論](https://ekrits.jp/2020/10/3914/)」（2020年） | Design as judgement past mechanical rules |

The rules taken from the book's chapters on views, navigation and tasks rest on readers' notes and the slides of a talk; the book's own pages on its layout patterns were out of reach (`research/20261113-production-ui-ooui/report.md`). No controlled study compares object-first with task-first business screens.
