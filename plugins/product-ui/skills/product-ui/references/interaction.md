# Interaction

Source of record for how a collection, a record and a form behave once they are on the screen: what each control does, which state each part falls back to, what precedes a destructive action, and which sample records test the layout. `references/real-screens.md` records what a screen shows at rest; this file records what happens after a click. Read it at Step 3 of `SKILL.md`, before the brief's Controls line, States section and Sample data section are written, and when one of the interaction questions in `assets/brief.template.md` fails.

The evidence is `research/20261113-production-ui-ooui/report.md` and the screens of business tools captured for it (`corpus/anatomy_business_collection.json`, `corpus/anatomy_business_record.json`: issue trackers, project tools and SAP's list pages, signed out).

## What it settles

A built screen passes every check at rest and still reads as a mock when its filter filters nothing, its count disagrees with its rows and every record is tidy. "Screens that have been generated with AI typically use mock data", and mock data "masks the hardest UX problems": empty states, error flows and permission rules (UX Collective). Vercel's guidelines ask for the opposite on every screen: "All states designed. Empty, sparse, dense, & error states", and layouts that "handle short, average, & very long content". Three plans in the brief carry this:

| Plan | Written in | Settled by |
|---|---|---|
| Which controls work in this build, and on what | the `Controls` line | "Controls that work" |
| The state each collection, fetch and form falls back to | `## States` | "States" |
| The records that test the layout | `## Sample data` | "Sample data that tests the layout" |

## Controls that work

A control that changes what this page shows works in the build, on the sample data: the search field, the filters and their presets, the sort, the pagination, the tabs, the selection, a section that expands, an edit in place, the validation of a form. A screen whose filter row is decoration reports an effect it does not have (principle 2 of `SKILL.md`).

| The control | In the build |
|---|---|
| Changes the view of the data on this page (search, filter, preset, sort, page, tab) | Works on the sample data, and the record count follows it |
| Changes a record in place (a status changed, a field edited, a reply added, a setting saved) | Changes the page's own state, kept in the browser's storage where the reader would expect it after a reload (saved settings); the brief's `Controls` line names the part a server would do |
| Sends data away (submit, save on a form page, delete, add to cart) | Moves to the state the brief names, by the page's own navigation: 完了 at its URL, the collection without the record, the cart count raised. A 完了 state names the result and links to the step that follows it (the new record, the collection, the page the reader came from). The brief's `Controls` line names the route a server would receive. A form that posts to a route no server answers ends on an error page |
| Would open a view outside this build | Left off the screen: no link, button or navigation item points at a view the build lacks, and an object without a view is named as plain text. The hand-over lists what was left off. An empty state whose create form is outside the build shows its message alone. A file name links to a file the build holds, and is plain text otherwise. R10 reports an `<a>` whose route the brief's screens lack; a button or a menu item that navigates by script is the builder's to check |

The view's state lives in the URL: the search text, the filters or the preset, the sort, the page, the open tab and the open record are query parameters or path segments, so a reload and a shared link restore the view ("Deep-link everything. Filters, tabs, pagination, expanded panels", Vercel). The state URLs the brief names for review (`?state=empty`) sit beside them.

## Collections

What the collection screens of business tools show, counted on 14 captured screens, and how a build behaves. `references/real-screens.md` (Collection: work tools) gives the regions and sizes.

| Part | On real screens | In a build |
|---|---|---|
| Record count | 14 of 14: `(1-25/4780)` beside the pager, `Open 18,545 / Closed 240,329` on the state tabs, `Sales Orders (20)` in the table title | A number with the object noun or 件. It counts the rows the current filter gives, and it changes when the filter does |
| Search | 12 of 14 | A field that narrows the rows by the identifying properties. Reference by name stayed accurate as the number of objects grew, where reference by place fell away (Jones and Dumais, 1986) |
| Filters | Controls on 10 of 14; the applied filter visible on 11 of 14, as the filter row itself, the active tab or the name of the saved query | Each active filter is visible above the rows with a way to clear it. Baymard counts sites without such an overview as failing its practice |
| Presets | Named queries or views on 8 of 14 (`Open issues`, 未完了) | The presets the tasks give (`references/ooui.md`, Tasks), as tabs or a list of saved filters; each carries its count where the reader triages by it |
| Sort | 10 of 14: column headers on tables, one dropdown on issue lists | The current order is visible, on the header or in the control. Where the table folds into list items at 375px, a 並び替え select takes the headers' place. A consumer catalogue offers price, rating, best-selling and newest (Baymard's four) |
| Pagination | 10 of 14, numbered pages on 9; a page-size choice on 3 | Numbered pages under the rows with the range and the total. A list of more than a page of records paginates; Polaris recommends it above 50 items in a table, and consumer results hold 25 a page at the median |
| Row link | The identifier, the title or both | The identifying property links to the single view |
| Selection and bulk actions | A checkbox per row on 4 of 14; bulk actions in view on 2 | Built where a task acts on many records at once. The bar appears with the selection, states how many are selected, and offers to extend the selection to every record the filter gives (HubSpot's `Select all`) |
| Row actions | 6 of 14, in the trailing column or a row menu | The frequent, reversible ones; the rest wait in the single view |
| Status | Plain text or an icon on 8 of 14; a coloured dot or chip with the word on the rest | The state's word always; the colour is added to it (`patterns/status.badge.json`) |
| Empty cell | Blank on the Redmine, SAP and OpenProject tables captured; a dash on Bugzilla | A table cell with no value stays blank (`patterns/collection.table.index.json`); a record's property list prints a word for it (Records, below). In a row folded into a list item at 375px, a label whose value is empty is left out with it |
| Numbers | | Amounts and counts right-aligned in their column, in tabular figures (`font-variant-numeric: tabular-nums`), with the unit in the header or on the value, in the form the domain prints (賃料 in 万円 on a rental site, 円 on an order). Digits group by three with a half-width comma (`1,280,000円`) |
| Dates and times | | On a Japanese screen a date reads `2026/11/13` with the month and day zero-padded, and a time reads `15:35` on the 24-hour clock, with seconds where the record keeps them. One formatter serves the whole build, so a date reads the same in a table cell, a record's property list and a history entry. SmartHR writes the Japanese date as `2025/01/01` and the time as `hh:mm:ss`, where `ss` may be left off |

Views can be kept per person or shared: Linear saves display options "as personal preferences or as the default display options on that page for your workspace", and Airtable separates personal views from locked ones. A build offers saved views only where the request asks for them; the presets above cover the tasks.

## Records

Counted on 4 captured record screens of business tools, with the 18 records of `references/real-screens.md`.

| Part | On real screens | In a build |
|---|---|---|
| Title block | The identifier beside the title; the status as a coloured badge on 3 of 4 | The identifying property, the title and the state's word together, above everything else |
| Way back | A path to the collection on 2 of 4 | A breadcrumb or a link to the collection above the title. It returns to the view the reader left: the search, the filters, the sort and the page they came from |
| Properties | Label and value pairs in a right rail on 2 of 4, in a grid under the title on 2 of 4; empty values printed (`-`, `None yet`, なし) on 4 of 4 | An empty property keeps its row and prints a dash or the object's word for it (未設定, なし) |
| Links to other objects | 4 of 4: people, referenced records, versions, filtered lists | Each value that names another object links to that object (`references/ooui.md`, Step 2) |
| Related lists | A section on 4 of 4 | A heading with the related noun and its count, the rows, and an add action where the reader may add one. A list with no rows keeps its heading and says so in one line |
| Activity | 4 of 4: a chronological thread, each entry with its author, its time and its body, comments mixed with change events | The history of the record under its body: who did what, and when (`content history`, the `record.activity` pattern) |
| Previous and next record | 0 of 4 | Left out unless the request asks for it |

### Editing

| The edit | Form | Source |
|---|---|---|
| One field that changes often, outside a form (a status, an assignee, a due date) | In place: the value becomes its control, and the change saves when confirmed | Atlassian: inline edit "on screens where information needs to be updated often, such as a work item page" |
| A longer text | In place, staying in edit mode until 保存 or キャンセル, so unfinished work is neither saved nor lost by a stray click | Atlassian |
| Several fields together | The single view turns into a form, one edit mode at a time on the page; 保存 and キャンセル at the form's foot | Primer; SAP Fiori elements |
| A short task that needs an answer before the reader goes on | A dialog, with one dismissing button beside its action (キャンセル) and the header's × named 閉じる | SmartHR |
| A task whose content would scroll inside a dialog | A page of its own, with the way back | SmartHR |

A form warns before the reader leaves it with unsaved changes (Vercel).

## Destructive and bulk actions

The step before an action follows what the action destroys.

| The action | Before it | After it |
|---|---|---|
| A part of a form the reader has not saved yet (a 明細 row being entered) | Nothing | The part goes at once; a toast offers 元に戻す where it held input |
| Reversible (archive, a status change, removal from a list) | Nothing: "破壊的な操作であっても、操作後に元に戻せる場合は、処理前の確認は必要ありません" (SmartHR) | A toast that names what happened and offers 元に戻す |
| Irreversible deletion of one record | A dialog titled with what is deleted (`{対象}の削除`: the record's own name, as `references/ui-copy.md` writes the title) that shows which record goes and that it cannot be restored; the confirming button on the right, in the destructive style, labelled 削除 | The reader is at the collection, and a toast names the record |
| Deletion that takes other records with it (a customer with its orders, a workspace) | The dialog also lists what else goes, and asks for the record's name typed (Carbon) | As above |
| An everyday change to many records | A step that states how many records change and what happens to them: many targets raise the risk of a wrong selection (SmartHR) | A toast with the count |
| A registration, under a profile that asks first (`confirm.register always` in the brief's Conventions section) | A dialog titled with the object and the operation (「受注伝票の登録」) whose body is the profile's sentence (「登録します。よろしいですか？」), as 奉行Jシリーズ and 弥生販売 ask | The result in the form `messages` gives |

Bulk operations in production carry limits (1000 work items in Jira Cloud, 100 records for some HubSpot actions); a mock states none unless the request does.

## Feedback

- A toast carries a message that is momentary and can be missed without harm: the result of an action that worked. One toast shows at a time, for about 5 seconds. A failure the reader has to act on shows where it happened, and stays. Products differ here (a kintone notification stays until it is closed, a SAPUI5 toast closes after 3000 ms), so under a profile the form, the time and the number of result messages follow the `messages` rows of the brief's Conventions section (`references/profiles.md`, `patterns/feedback.message.json`); the figures of this line are what `inherit` gives.
- A form shows each error beside its field in words that say how to put it right, and on submit the focus moves to the first error. The submit control stays enabled, so that an incomplete form answers with its errors ("Don't pre-disable submit", Vercel). Validation runs when a field loses focus and again on submit.
- An operation that sends data runs once per press: while it runs, the control that started it takes no second click, and it is free again when the run ends (TERASOLUNA: a clicked button cannot be clicked again until the screen is redrawn). A second press that registers a second record is a defect. `useSubmitGuard` of the kit does this, and the control carries `data-guard="button"`. Where a dialog asks before the registration, the guard is on the dialog's confirming button, as `ConfirmDialog` of the kit carries it: a guard on the control that opens the dialog leaves the registration itself open to a second press.
- After a registration on an entry screen of a business package (a `slip` or a `master` section): on a new record the form empties for the next one and the focus returns to its first field (freee会計: 「[登録]をクリックすると、入力した内容が保存され、新規作成画面となります。」); on an existing record the record stays on the screen. The result message shows as the brief's Conventions section says.
- A placeholder never stands in for a label: "placeholders in form fields often hurt usability more than help it" (Nielsen Norman Group).
- A disabled control states its reason in text beside it. A tooltip on a disabled control reaches no keyboard or touch user. On `desktop`, `references/desktop.md` replaces this rule for a ribbon, quick access or file view command: the condition stays in its tooltip, and the command stays focusable (`aria-disabled`), so the tooltip shows on focus.
- A region that loads shows the shape of its content: a skeleton with the rows and columns of the table it becomes, so nothing shifts when the data arrives. Without an indicator "users may think a process has silently failed" (Primer). Where the wait is real, the indicator appears after about 200 ms and stays at least about 400 ms, so a fast answer does not flicker (Vercel).
- A change that is likely to succeed shows at once and is reconciled when the server answers; on failure the page restores the earlier value and says so (Vercel).

## Keys

The reader of a business package enters data without leaving the keyboard, and each family of products has its own keys. A screen built under a profile follows the `keys` rows of the brief's Conventions section (`references/profiles.md`); a screen without a profile keeps the browser's keys.

| Key | Under a profile that sets it | Without a profile |
|---|---|---|
| Enter in a field of an entry form | Moves to the next field, and Shift+Enter to the previous one (`keys.enter next-field`; 弥生会計, 弥生販売). A `textarea`, a button and an open list keep their own Enter, and an Enter that settles an input-method conversion moves nothing | Submits the form |
| Enter in the last field | Registers where the product does (`keys.enter_last register`; 奉行Jシリーズ), and stays otherwise | Submits the form |
| A function key | Runs the button that shows it in the row of function keys (`patterns/action.function-keys.json`; PCA 会計シリーズ shows them together at the foot of the screen). The browser's own action for that key is stopped | The browser's own action |
| A shortcut (Ctrl+F, Ctrl+Insert) | Runs the control that carries it | The browser's own action |

- Every key is also a control. An operation never depends on a key alone: a browser may keep a key for itself, and a touch device has none.
- The keys rest while a dialog is open, and the dialog's own buttons take Enter and Escape.
- Tab keeps its order under every profile, so a reader who does not know the product's keys loses nothing.
- An entry form opens with the focus on the first field the reader fills (intra-mart, 入力フォーム).
- `lib/keys.ts` of the kit carries these out (`useEnterKeys`, `useKeyButtons`), and R49 and R50 measure them on the rendered page.

## States

Every collection, fetch and form has its states in the brief, and a mock gives each a URL. A collection that is full by its nature (the seven days of a week, the lines of a confirmed order) has no empty state, and the brief's States section says so. A depiction of the product on a landing page (the table inside a hero's product window) is an illustration with no states of its own; at 375px it shows the columns that fit and leaves the others out, with no cell cut at its edge.

| State | Shows | Differs from |
|---|---|---|
| Empty | That the collection holds nothing yet, and the action that adds the first record (`patterns/state.empty.json`) | No results: here there is nothing to filter |
| No results | That the current search or filter matched nothing (「該当する{オブジェクト名}はありません。」, with 「別の条件を試してください。」), under the search and the filters, which stay in place for the reader to change. Where several filters can be active at once, one control clears them all | Empty: the records exist |
| Error | That the data could not be loaded, the cause the reader can act on, and a retry | Empty: Primer keeps a failure visibly apart from a feature that is empty by its nature |
| Loading | The skeleton of the content | |
| Sparse and dense | The same layout with one record and with a full page | |
| The main action is closed (在庫切れ, 締切後, a record in its last state) | In the action's place, the state in words and the step the reader still has (お気に入りに追加, 再入荷の予定 where the shop states one) | |
| No permission | The record without the actions the reader's role lacks; a whole view the role cannot open says so and links back | |
| Not found | Inside the shell: that the page does not exist, and a link to the collection. A mistyped or outdated address falls here; no control of the build leads to it | A blank page |

A mock that reads local sample data builds the empty and the no-results state of each collection, the validation state of each form and the not-found screen. A state URL shows the state as an operation would leave it: the validation state has the focus on the first field with an error. The loading and error states of a fetch are built where the brief names a fetch.

## Sample data that tests the layout

Tidy records hide what production data does to a layout. The sample data of a collection includes, somewhere on its first page:

- the longest name the domain produces (a company name with its legal form and a division, a product name with its model number), and the shortest;
- a record with each optional property empty;
- an amount of zero where the domain has one (a draft, a free item; a shop's price has none), one of seven digits or more, and a negative one where the domain has refunds or corrections;
- each state of the object at least once, in the mix a product in use has: most records in the common states, a few in the rare ones;
- a date in the past where a due date exists, and a record changed today;
- on a shop, ratings on most products with counts from one digit to four, and a product or two with none yet.

The record a single view opens by default (the brief's Entry or Captures) is one in mid-life: past its first state, with several entries in its history, rows in each related list and one optional property empty. A record created a minute ago shows a title and an empty page, where production records hold 5876 characters at the median (`references/real-screens.md`, Every screen).

Each slot settles what long text does: a title in a list wraps, a cell in a dense grid ends in an ellipsis with the full text in `title`, a description clamps to its lines (`references/patterns.md` gives each pattern's limits). Formats follow the locale of the interface and stay the same across the screen: an amount with its separator and currency (`¥1,280,000` or `1,280,000円`), a date in one form (`2026/11/13`), a recent time as a relative phrase with the full time in `title`, a count with its unit (件).

## Consumer search and purchase

Baymard Institute's benchmarks count the share of large shops that miss each practice it recommends. A catalogue, a product page or a cart built here meets them:

| Part | Practice | Sites that miss it |
|---|---|---|
| Search | Autocomplete under the field | Present on 80%; fully right on 19% |
| Sort | Price, user rating, best-selling and newest | 68% of desktop sites lack one |
| Filters | The applied filters in an overview above the results | 20% |
| List item | The variations of a product (colour, size) in one item | 42% |
| Path | A breadcrumb to the category | None on 23% |
| Product images | Enough resolution to inspect the product | 25% |
| Cart | Quantity changed and an item removed in the row; the order total with shipping before checkout | 86% make the quantity or the removal hard |
| Checkout | Guest checkout as the leading option; validation in the field | 47%; 31% |

The figures are Baymard's own, of shops in the US and Europe. What the Japanese majors show is in `references/real-screens.md` (Collection: consumer search results, Japanese shops): the price as the largest text of an item, the shipping beside it, points and the review count under it, and a sort select whose orders include the price both ways and the reviews. A price shown to consumers in Japan is the tax-inclusive price (総額表示), printed as `98,800円` or `98,800円（税込）` ([国税庁 No.6902](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6902.htm)).

## What the checks cover

The scripts read a screen at rest. The interaction questions in `assets/brief.template.md` carry this file to the Step 5 reviewer and to the author's own run of the built screen: each is answered by operating the screen (`cdp.js` takes an expression to run before the dump) or by opening a state's URL.

## Sources

| Source | What it settles here |
|---|---|
| Vercel, [Web Interface Guidelines](https://vercel.com/design/guidelines) | Every state designed; content of any length; deep links; errors beside fields and focus on the first; submit left enabled; the loading delays; optimistic updates; a confirmation or an undo |
| A. Paschal, [What makes generated UI worth keeping](https://uxdesign.cc/what-makes-generated-ui-worth-keeping-96b44ade04a1), UX Collective | Mock data hides empty states, error flows and permission rules |
| SmartHR Design System [削除ダイアログ](https://smarthr.design/products/design-patterns/delete-dialog/), [ワンクッション必要な操作](https://smarthr.design/products/design-patterns/confirmation-step/), [モーダルなUI](https://smarthr.design/products/design-patterns/modal-ui/) | No confirmation where an action can be undone; the delete dialog; a step before a change to many; dialog or page |
| SmartHR Design System [数字・数えの表記](https://smarthr.design/products/contents/idiomatic-usage/count/) | The Japanese date form `2025/01/01`; time as `hh:mm:ss` with `ss` optional; a half-width comma every three digits |
| IBM Carbon, [Common actions](https://carbondesignsystem.com/patterns/common-actions/) | The typed name before a deletion with wide effect; the return to the list |
| Atlassian Design System, [Inline edit](https://atlassian.design/components/inline-edit/usage) | When a field is edited in place |
| GitHub Primer, [Empty states](https://primer.style/ui-patterns/empty-states), [Loading](https://primer.style/ui-patterns/loading/), [Saving](https://primer.style/product/ui-patterns/saving/) | Empty apart from failed; the loading indicator; one edit mode at a time |
| Shopify, [Index table](https://shopify.dev/docs/api/app-home/latest/patterns/compositions/index-table.md), [Polaris index table](https://raw.githubusercontent.com/Shopify/polaris/main/polaris.shopify.com/content/components/tables/index-table.mdx), [Alerts](https://shopify.dev/docs/apps/design/user-experience/alerts) | Checkboxes for bulk selection; pagination; numeric cells right-aligned; toasts for momentary messages |
| Linear, [Display options](https://linear.app/docs/display-options.md), [Undo](https://linear.app/changelog/undo-actions); Airtable, [Views](https://support.airtable.com/articles/5189551686-getting-started-with-airtable-views) | Views saved per person or shared; undo across operations |
| HubSpot, [Bulk edit records](https://knowledge.hubspot.com/records/bulk-edit-records); Atlassian, [Edit multiple work items](https://support.atlassian.com/jira-software-cloud/docs/edit-multiple-issues-at-the-same-time/) | Selection extended to every record of the view; limits on bulk operations |
| W. P. Jones and S. T. Dumais, [The spatial metaphor for user interfaces](https://doi.org/10.1145/5401.5405), ACM TOIS 4(1) (1986) | Reference by name against reference by place as objects grow |
| Baymard Institute, [autocomplete](https://baymard.com/blog/autocomplete-design), [product lists and filtering](https://baymard.com/blog/current-state-product-list-and-filtering), [breadcrumbs](https://baymard.com/blog/ecommerce-breadcrumbs), [cart](https://baymard.com/checkout-usability/benchmark/step-type/cart), [checkout](https://baymard.com/blog/ecommerce-checkout-usability), [image resolution](https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom) | The consumer practices and the share of sites that miss each |
| Nielsen Norman Group, [Placeholders in Form Fields Are Harmful](https://www.nngroup.com/articles/form-design-placeholders/) | A label outside the field |
| 弥生, [弥生会計の環境設定](https://support.yayoi-kk.co.jp/subcontents.html?page_id=18326), [弥生販売のショートカットキー一覧](https://support.yayoi-kk.co.jp/subcontents.html?page_id=22523); OBC 奉行Jシリーズ, [部門を登録する](https://www.obc.co.jp/bugyo-j/jseries/quick/quick-op/04), [定型取引を呼び出して使用する](https://www.obc.co.jp/bugyo-j/jseries/quick/quick-op/16); PCA 会計シリーズ, [ボタン、メニューバー、キーなどの操作](https://pca.jp/area_support/manual/acc/a_Common/Button_menu_key.html) | Enter between fields; the function keys and their row; the question before a registration |
| TERASOLUNA Server Framework for Java, [二重送信防止](https://terasolunaorg.github.io/guideline/current/ja/ArchitectureInDetail/WebApplicationDetail/DoubleSubmitProtection.html) | One run per press of a control that sends data |
| intra-mart Accel Platform, [UIデザインガイドライン(PC版)](https://document.intra-mart.jp/library/iap/public/im_ui/im_design_guideline_pc/texts/contents_area/input_form.html) | The focus on the first field of a form |

The counts of business tools come from signed-out captures of issue trackers, project tools and SAP's demo list pages; edit controls are mostly hidden from a signed-out reader, so the editing table rests on the design systems. The toast timing is this skill's own default.
