# Object-oriented UI (OOUI)

Source of record for the screen structure the skill builds when `meta.structure` in `tokens.json` is `ooui`, following the method of 上野学 and ソシオメディア in 『オブジェクト指向UIデザイン──使いやすいソフトウェアの原理』 (技術評論社, 2020). Check C17 in `references/ui-copy.md` is the mechanical part; the five structure questions in `assets/brief.template.md` carry the rest to the Step 5 reviewer.

Read it at Step 0 for the structure question, at Step 3 before any layout or navigation exists, and when C17 fires.

## What it settles

OOUI designs a screen from objects: the things the user came for, each named by a noun. The book's publisher page lists four principles.

1. The user can perceive each object and act on it directly.
2. An object shows its own properties and state.
3. The user selects the object first and the action second.
4. All objects work together to compose the interface.

A screen built around a task fixes the order of work and hides the object inside it. With the objects in front, one list and one detail view serve every task on an object, so the product needs fewer screens and the user chooses the order.

## Choosing the structure

Step 0 records the answer in `meta.structure`; the request usually points to one of the two.

| `meta.structure` | Fits when | Typical screens |
|---|---|---|
| `ooui` | The product manages sets of same-kind objects, and the user chooses which one to act on | An admin console, a SaaS workspace, a CRM, an inventory, a ticket tracker |
| `task` | The object is fixed and needs no selection, or the screen is a self-contained procedure offered as a fixed input flow | An ATM-style terminal, sign-up, checkout, an application form, an onboarding flow, a landing page |

The two `task` conditions are the exceptions ソシオメディア names for a task-based GUI. Practitioners add two more: a user who must be led to one goal with certainty, and an operation that must run without a mistake, as in an emergency.

One product can hold both: an `ooui` application keeps a task flow for a case in the `task` row, such as its sign-up. Name each such flow in `ui-brief.md` so the reviewer reads it as intended.

When `meta.structure` is `task`, the screen follows the order of the procedure, C17 stays off, and the rest of this file is skipped.

## The three steps

Work through these before writing markup, in any order the work needs: when a later step exposes a gap in an earlier one, go back and settle it there.

### Step 1 — Extract the objects

List the nouns in the request, the existing screens and the data model. A noun is an object when it passes all three tests:

- it is a countable noun (顧客, 請求書, プロジェクト),
- the product manages it as a set of the same kind,
- its instances share the same actions.

A word that fails is an operation (登録, 検索), which acts on an object; a value (金額, 期日), which is an attribute of one; or a screen name (一覧, 詳細), which is a view of one.

For each object, write down its name, key attributes, actions and the objects it refers to. One object keeps one name across the product; settle a competing pair in `voice.terms`. The objects the user comes to the product for are the main objects.

### Step 2 — Views and navigation

- Each main object gets a collection view, showing the set with the key attributes, and a single view, showing one object with the rest of its attributes.
- Choosing an object in the collection view opens its single view.
- Root navigation lists the main objects, each as a noun. C17 reports an item that names an operation.
- An action sits on the object it acts on: in the row or in the single view, after the object is selected. Creation sits at the collection, as 「新規」 above the list. Editing turns the single view into a form.
- A reference between objects becomes a link between views: the single view of a 顧客 shows the collection of that customer's 請求書.
- The object-then-action order holds across the whole application.

### Step 3 — Layout patterns

Map each view onto a component from `references/components.md` or the preset's component reference. The mapping is this skill's own.

| View | Layout |
|---|---|
| Collection | A table for attribute comparison, a list for scanning by name, a card grid for objects recognised by image |
| Single, beside its collection | A two-pane master and detail layout at desktop width, a separate page at 375px |
| Single, on its own | A page with the object's name as the heading and its actions beside the heading |
| Create and edit | The single view as a form, in the same pane or page |

## What the checks cover

上野学 treats design as judgement past mechanical rules, so one check is scripted and the rest goes to a reader of the rendered screen.

- C17 in `check_copy.py`, an error, reports a navigation item ending in an unambiguous operation word. 「申請」「承認」「顧客管理」 and the like go to the reviewer.
- C10 checks one name per object for the names in `voice.terms`.
- The five structure questions in `assets/brief.template.md` carry each rule above to the reviewer: noun navigation (1), a collection and a single view joined by selection (2), each action on its object after selection (3), one name and one set of key attributes per object (4), and every sequence a flow the `task` row admits (5).

## Sources

| Source | What it settles here |
|---|---|
| ソシオメディア、上野学、藤井幸多『[オブジェクト指向UIデザイン](https://gihyo.jp/book/2020/978-4-297-11351-3)』（技術評論社、2020年） | The four principles and the three steps |
| 上野学「[OOUI – オブジェクトベースのUIモデリング](https://www.sociomedia.co.jp/7279)」（2016年） | The two conditions under which a task-based GUI is tolerated |
| 上野学「[OOUI の目当て](https://www.sociomedia.co.jp/8740)」（2019年） | Noun-form navigation, the collection and single views, the edit form in the single view, the object-then-action order |
| uenitty「[Design process of OOUI](https://speakerdeck.com/uenitty/design-process-of-ooui)」（2020年） | The three tests for an object |
| yiio による同書の読書記録（[note](https://note.com/yiio/n/n646b6a031626)、2021年） | References between objects drawn as links between views |
| nextbeat design の記事（[note](https://note.com/nextbeat_design/n/nbbb7efcedee0)、2021年） | The two practitioner conditions for a task flow |
| 上野学「[オブジェクト指向デザインの道具論](https://ekrits.jp/2020/10/3914/)」（2020年） | Design as judgement past mechanical rules |
