# Profiles

Source of record for the profiles under `profiles/`, the scripts under `scripts/profiles/` (PFV1 to PFV7), `meta.profile` and `meta.profile_product` of `tokens.json` (T24), the `## Conventions` section of `ui-brief.md`, `scripts/check_profile.py` (PF0 to PF7), and R49 to R51 in `scripts/render/check_render.py`. Read it at Step 0 of `SKILL.md` when the request names a business package or asks for a screen of one, at Step 3 before the keys, the words and the messages of a screen are built, and when one of these checks fires.

The evidence is `research/20261120-jp-business-packages/report.md`: the manuals, help pages and design guidelines that vendors of business packages publish. The evidence of `ms-office` is `research/20261121-office-desktop-conventions/report.md` and the measurement in `research/20261121-office-window-measure/measured.md`.

## What a profile settles

Business packages differ in what a key does, which word names an operation and how a message behaves. In 弥生販売 F9 deletes the slip on the screen, and in OBC's 奉行Jシリーズ F9 opens a journal entry for editing. SmartHR names the creating operation 追加 where intra-mart names it 登録. A kintone notification stays until it is closed, and a SAPUI5 toast closes after 3000 ms. A screen proposed to people who work in one of these products reads as theirs when it keeps those conventions, and no rule of taste recovers them: they are facts of each product.

A profile records the conventions of one family of products: the products whose keys and words follow one scheme. It holds data only, and every value that departs from this skill's own default names the page it was read on. Two layers stay apart:

| Layer | Settles | Recorded in |
|---|---|---|
| Conventions | keys, words, the required mark, the confirmation step, messages, waiting | `meta.profile`, a file of `profiles/` |
| Look | colours, type, components | `meta.reference`, a preset (`references/dads.md`, `references/smarthr.md`, `references/astryx.md`) |

A build may take a profile with any preset or with none. The vendors of the Japanese core packages publish no design system, so a screen under `jp-core` takes its look from the request or the lookup, as any screen without a preset does.

## The profiles

| Profile | Family | Products with a table of their own | Read on |
|---|---|---|---|
| `jp-core` | 国産の基幹パッケージ: sales and accounting packages that began on the desktop | `yayoi-hanbai` (弥生販売), `bugyo-j` (奉行Jシリーズ) | the manuals of 弥生販売, 弥生会計, 奉行Jシリーズ and PCA 会計シリーズ; TERASOLUNA's guideline for the double-submit guard |
| `jp-cloud-accounting` | 国産のクラウド会計: accounting services that run in the browser. The family's values are freee会計's | `yayoi-kaikei-next` (弥生会計 Next) | freee ヘルプセンター; the shortcut list of 弥生会計 Next |
| `smarthr` | SmartHR, and products that follow its design system | | SmartHR Design System |
| `kintone` | kintone and its customisations | | cybozu developer network |
| `intra-mart` | Business systems built on intra-mart Accel Platform | | UIデザインガイドライン(PC版) |
| `sap-fiori` | Applications on SAPUI5 | | the SAPUI5 documentation and the OpenUI5 source on GitHub |
| `salesforce-lightning` | Applications on the Lightning platform | | Lightning Web Components Developer Guide, an archived copy |
| `dynamics-365` | Model-driven applications of Dynamics 365 and Power Apps | | Microsoft Learn; Fluent 2 |
| `ms-office` | The document window of Word, Excel and PowerPoint for Windows, the profile of the `desktop` surface (`references/desktop.md`) | `word`, `excel`, `powerpoint` | Microsoft サポート's keyboard pages for Word, PowerPoint and Excel; the Win32 guidelines on keyboard and dialog boxes; the window of Microsoft 365 read through UI Automation |

A product has a table of its own where its manual gives values that differ inside the family. 奉行クラウド, SMILE, OBIC7, GLOVIA and SuperStream-NX keep their manuals behind a sign-in, so they stay outside the products the profiles cover: a request that names one of the five takes `jp-core` with no product, and the hand-over says that the product's own keys were not read. The help pages of マネーフォワード クラウド refused the fetch, so it stays outside as well, and a request that names it takes no profile.

The profiles differ in how much their sources state. `jp-core` sets the keys, the words and the confirmation; `kintone`, `sap-fiori`, `salesforce-lightning` and `dynamics-365` set the messages and leave the words to `inherit`, since the pages read for them are developer documentation in English. `sap-fiori` rests on the SAPUI5 documentation and source, and its wait of 1000 ms on an issue of the UI5 Web Components repository that reports the Fiori guideline. `ms-office` sets the keys, the words of a document window and the save prompt, and leaves the messages to `inherit`; its words and its prompt come from the window of Microsoft 365, read through UI Automation, where Microsoft's pages print other words (the Excel page names the in-place save [保存], and the window prints 上書き保存).

Run `python {SKILL_DIR}/scripts/profiles/validate.py` after any change to a file under `profiles/`.

## The profile format

One JSON file per family, named by its id (`profiles/jp-core.json`).

| Field | Holds | Values |
|---|---|---|
| `id` | lower case joined by hyphens | |
| `version` | a whole number, raised when a value changes | |
| `name` | the family's name, as the intake question prints it | |
| `summary` | what marks the family, one sentence | |
| `keys.enter` | what Enter does in a field | `next-field` (Enter moves to the next field and Shift+Enter to the previous one), `none` |
| `keys.enter_last` | what Enter does in the last field | `register`, `none` |
| `keys.display` | where the function keys are shown | `bottom` (a row at the foot of the screen), `toolbar`, `tooltip` (in the tooltip of the command that carries the key, after its name), `none` |
| `keys.function` | the function keys | a list of `{"key", "label", "action"}`: `key` is F1 to F12, `action` is `register`, `delete`, `new`, `lookup`, `edit`, `recall`, `print` or `search`, or on a desktop window `save-as`, `help`, `next-region` or `keytips`; `[]` for none |
| `keys.shortcuts` | the other shortcuts | a list of `{"keys", "label", "action"}`: `keys` is written as the kit reads a pressed key: the modifiers in the order Ctrl, Shift, Alt, then a capital letter, a digit or a named key (`Ctrl+S`, `Ctrl+Shift+N`, `Shift+F8`, `Ctrl+Enter`), `action` is one of the function-key actions or `row-insert`, `row-delete`, `row-new` (the lines of a slip), or on a desktop window `undo`, `redo`, `cut`, `copy`, `paste`, `select-all`, `open`, `save`, `close`, `find`, `replace`, `ribbon` (collapse the command area) or `context-menu`; `[]` for none |
| `words` | the word of each operation: `create`, `save`, `delete`, `new`, `lookup`, `search`, `clear`, `cancel` | a word, or `inherit` |
| `required_mark` | how a required field is marked | `text` (「必須」 beside the label), `asterisk`, `inherit` |
| `confirm.register` | whether a message asks before a registration | `always`, `never`, `inherit` |
| `confirm.sentence` | the sentence of that message | a sentence holding `{操作}`, the place of the operation's word; `inherit` |
| `confirm.buttons` | the two buttons of that message, the confirming one first | two words (`{操作}` stands for the operation's word), or `inherit` |
| `messages.error` | where an input error shows | `field` (beside its field), `top-and-field` (a summary above the form as well), `inherit` |
| `messages.result` | how the result of an operation shows | `toast`, `bar` (a bar at the top of the content), `near-control` (beside the control that ran it), `new-entry` (the screen returns to an empty entry with no message), `inherit` |
| `messages.duration_ms` | how long a result message stays | a whole number of milliseconds, `until-closed`, `inherit` |
| `messages.max` | how many messages show at once | a whole number, `inherit` |
| `waiting.block` | what is blocked while an operation runs | `screen`, `button` (the control that started it), `none`, `inherit` |
| `waiting.delay_ms` | the wait before a progress indicator shows | a whole number of milliseconds, `inherit` |
| `motion` | the durations of motion | `{"fast", "base", "slow"}`, each in ms, or `inherit` |
| `products` | per product, the items whose value differs from the family's | `{"<product id>": {"name", "set": {"<item>": value}, "from": {"<item>": [evidence ids]}}}` |
| `evidence` | each `{"id", "source", "url", "says"}`: a page that was read, and what it says, paraphrased. A measurement the maintainer made of a product names its record with `measured` (a path under `research/`) in place of `url` | |
| `from` | per item, the evidence ids its value rests on | `{"keys.enter": ["yayoi-kaikei-env"]}` |

An item is named by its dotted path (`keys.enter`, `words.save`, `messages.duration_ms`). The five `keys` items state a choice in every profile; every other item may be `inherit`. A value that differs from what `inherit` gives names its evidence in `from`.

The items of a desktop window are optional: a profile that leaves them out is valid, and the Conventions table prints the ones a profile or its product sets, after the others.

| Field | Holds | Values |
|---|---|---|
| `keys.keytips` | whether Alt shows key tips on the ribbon (`references/desktop.md`, Keys) | `alt`, `none` |
| `words.save_as`, `words.undo`, `words.redo`, `words.cut`, `words.copy`, `words.paste`, `words.open`, `words.close`, `words.print`, `words.export`, `words.select_all`, `words.replace` | the word of each operation of a document window | a word |
| `confirm.close` | whether closing a changed document, and 新規 and 開く on one, asks to save it first | `always`, `never` |
| `confirm.close_sentence` | the sentence of that prompt | a sentence |
| `confirm.close_buttons` | its three buttons: the saving one, the one that goes on without saving, the cancelling one | three words |

## What `inherit` gives

`inherit` means this skill's own value, the one a build without a profile uses.

| Item | Value | Stated in |
|---|---|---|
| `words.save`, `words.cancel` | 「保存」, 「キャンセル」 | `references/interaction.md`, Editing |
| `words.delete` | 「削除」 | `references/ui-copy.md`, Button labels |
| `words.search` | 「検索」 | `references/real-screens.md`, Form, sign-up and sign-in |
| `words.create`, `words.new`, `words.lookup` | the project's own word, settled in `voice.terms` | `references/ui-copy.md`, The operation vocabulary |
| `words.clear` | クリア | `references/real-screens.md`, Business package: entry |
| `required_mark` | `text` | `references/real-screens.md`, Form, sign-up and sign-in: 「必須」 by the label on 11 of 18 Japanese forms |
| `confirm.register` | `never`: a step precedes only what cannot be undone or changes many records | `references/interaction.md`, Destructive and bulk actions |
| `confirm.sentence` | none: the dialog's title names the object and the operation | `references/ui-copy.md`, Button labels |
| `confirm.buttons` | the operation's word, then 「キャンセル」 | `references/ui-copy.md`, Button labels |
| `messages.error` | `field` | `references/interaction.md`, Feedback |
| `messages.result`, `messages.duration_ms`, `messages.max` | `toast`, 5000, 1 | `references/interaction.md`, Feedback |
| `waiting.block` | `button`: the control that started an operation takes no second click while it runs | `references/interaction.md`, Feedback |
| `waiting.delay_ms` | 200 | `references/interaction.md`, Feedback |
| `motion` | `motion.duration` of `tokens.json` | `references/tokens-format.md`, motion |

No Japanese vendor's material read for the research states a duration of motion, and the published figures (Carbon's 70 to 700 ms, Fluent's 250, 167 and 83 ms for Windows apps) belong to design systems, so every profile keeps `motion` at `inherit` until a source for its family is read. A profile that sets `motion` gives the values Step 1 writes into `motion.duration` of `tokens.json`.

## What every profile keeps

A profile changes the conventions listed above and nothing else. Three rules of this skill hold under every profile:

- Text is 14px or more (principle 5 of `SKILL.md`).
- A button names its operation by the noun or the plain form, without する (`references/ui-copy.md`, Button labels). `validate.py` (PFV4) refuses a profile word that ends in する or します.
- No text explains the method or the screen (`references/ban-list.md`). The function keys are controls with labels, and the screen carries no line that explains them.

The duration of a result message, the confirmation before a registration and the required mark follow the profile.

A built screen prints no product name and no logo of the product whose conventions it follows: the vendors set conditions on the use of their names and marks (OBC, Cybozu). The product's name lives in `tokens.json` and in the brief.

## Choosing a profile

Step 0 settles `meta.profile` and `meta.profile_product`:

| The request | `meta.profile` | `meta.profile_product` |
|---|---|---|
| names a product that has a table (弥生販売, 奉行Jシリーズ, 弥生会計 Next) | its family | the product |
| names a product or a platform of a family without a table of its own (PCA, 奉行クラウド, OBIC7; freee会計; SmartHR; kintone; intra-mart; SAP; Salesforce; Dynamics 365) | its family | `null` |
| asks for a screen of a Japanese core package without naming one (伝票入力, マスタメンテナンス, 「基幹システムの画面」) | asked in the Reference question, with `jp-core` first | `null` |
| asks for a desktop application (`meta.surface: desktop`) | `ms-office` | `word`, `excel` or `powerpoint` where the request names the product the application should work like, else `null` |
| anything else | `null` | `null` |

Under a profile, Step 1 writes into `voice.terms` one entry for each operation whose word differs from what `inherit` gives and does not contain that inherited word, so that C10 holds the screens to it: `{"保存": "登録"}` under `jp-core`. Under `ms-office` the words 上書き保存 and 名前を付けて保存 contain 保存, and the save prompt's button is 保存, so Step 1 writes no term for the save operation.

## The Conventions section

`scripts/patterns/resolve.py` reads `meta.profile` and `meta.profile_product` from the `tokens.json` beside the brief and writes the `## Conventions` section after `## Slots`: the profile, the product, and one row per item with its value and where the value came from. A product's value replaces the family's, and `inherit` is printed as the value it gives.

```
## Conventions

Profile: jp-core; product: yayoi-hanbai

| Item | Value | From |
|---|---|---|
| keys.enter | next-field | jp-core [yayoi-kaikei-env, yayoi-hanbai-keys] |
| keys.function | F2 新規作成 (new), F8 参照 (lookup), F9 削除 (delete), F12 登録 (register) | jp-core, product yayoi-hanbai [yayoi-hanbai-keys] |
| words.save | 登録 | jp-core [yayoi-hanbai-keys, bugyo-j-register] |
| messages.duration_ms | 5000 | inherit: references/interaction.md, Feedback |
```

The same brief and the same `tokens.json` write the same section. `resolve.py --check` compares it with the rest of the brief. With `meta.profile` at `null` the section holds the one line `none`, and a brief written before this section existed is left without it.

## What the build does with each item

`scripts/patterns/scaffold.py` writes the conventions into the skeletons of the six patterns from business packages, and the kit holds the code that carries them out (`references/components.md`, The kit). Each skeleton spells the values out (the keys, the words, the sentence, the times), so the build takes them with the skeleton and settles no key and no word of its own.

| Item | On the screen | Kit part | Attribute the checks read |
|---|---|---|---|
| `keys.enter`, `keys.enter_last` | Enter moves the focus to the next field of the entry form, Shift+Enter to the previous one; a `textarea` and a button keep their own Enter. In the last field Enter registers where the product does | `lib/keys.ts`, `useEnterKeys` | `data-enter="next-field"` on the form |
| `keys.function`, `keys.display` | A row of buttons, each showing its key and its word; the key runs the button, and the button works by click as well (`patterns/action.function-keys.json`). A key whose operation the screen lacks is left out (a deletion on a new record, a recall on a master), and an operation the section gives no key is a button after the keys with its word alone. Under `bottom` the shell lifts its toasts above the row | `components/function-keys.tsx`, `lib/keys.ts`, `components/app-shell.tsx` (`keysAtFoot`) | `data-key`, `data-action` on each button |
| the lines of a slip | Enter in the last field of the last line opens the next line and moves to its first field while that line holds a value; from an empty last line Enter goes on as `keys.enter_last` says, and the registration leaves the empty lines out. A key that the lines carry (`row-insert`, `row-delete`) runs for the line that holds the focus, and rests while the focus is outside the lines | `lib/keys.ts`, `components/line-grid.tsx` | `data-line-add` on the button that adds a line |
| after a registration | On a new record the form empties for the next one and the focus returns to its first field; on an existing record the record stays on the screen. The message of `messages.result` shows in both cases | | |
| `keys.shortcuts` | The combination runs the control that carries it: the registering button of a form without function keys (`Ctrl+Enter`, `Ctrl+S`), the search button of the conditions, and on the lines of a slip `row-insert`, `row-delete` and `row-new` | `lib/keys.ts`, `components/line-grid.tsx` | `data-key` on the control |
| `words` | The label of each control that runs the operation | | `data-action` on the control |
| `required_mark` | 「必須」 beside the label or the column header, or an asterisk with 「必須」 as its accessible name | `components/form-field.tsx`, `components/line-grid.tsx` | `data-required-mark`; in source the `requiredMark` the skeleton passes |
| `confirm` | Before a registration, a dialog whose title names the object and the operation (「受注伝票の登録」) and whose body is the sentence (`patterns/feedback.confirm.json`). The dialog before a deletion takes the same sentence with the deleting word | `components/confirm-dialog.tsx` | `data-confirm="register"` on the dialog |
| `messages` | The result of an operation as a toast, a bar or a line beside the control, for the time given, with the number shown at once capped (`patterns/feedback.message.json`); under `new-entry` the form empties and the focus returns to its first field | `components/message-bar.tsx` | `data-message`, `data-message-kind`, `data-duration`; in source the values `useMessages` takes |
| `messages.error` | Each error beside its field; under `top-and-field` also a summary above the form, which takes the focus when a registration finds errors | `components/form-field.tsx` | `data-message="error"` on the summary |
| `waiting.block` | Under `button` the control that started the operation takes no second click until the run ends; under `screen` a layer covers the screen for that time | `lib/submit-guard.ts` | `data-guard="button"` on the control; `data-guard="screen"` on the layer |
| `keys.keytips` | Alt and F10 show a key tip on ファイル, on each tab and on the quick access toolbar; a tab's letter shows its commands' key tips, and Esc goes back one step | the desktop kit's command table | `data-keytip` on each key tip |
| `confirm.close` | Closing the window, 新規 and 開く ask first while the document has unsaved changes, with the sentence and the three buttons in the order the profile gives (`references/desktop.md`, Save prompt) | the desktop kit's save prompt | `data-confirm="close"` on the dialog |
| `words.create`, `words.save` | Where a family separates the two (追加 and 更新 in SmartHR, 登録 and 更新 in intra-mart), the registering button and its confirmation take a `mode`: the creating word on a new record, the saving word on an existing one | | `data-action="register"` |

A browser keeps some keys for itself (F5 reloads, F11 fills the screen, and a browser may refuse to hand a key over). `lib/keys.ts` takes the keys the Conventions section lists and stops their default action; every one of them is also a button, so no operation depends on a key the browser kept. 弥生会計 Next, a browser product, documents such an exception for Safari.

The `html` stack takes the skeletons with the same attributes; the key handling is written by hand there, since the kit is React.

## Checks

### PFV1 to PFV7: `scripts/profiles/validate.py`

| ID | Check |
|---|---|
| PFV1 | a file that holds anything other than one JSON object, or a field or an item that is missing or of the wrong type |
| PFV2 | an id written in another form than lower case joined by hyphens, one that differs from the file name, or one used twice |
| PFV3 | a value outside the set its item draws from; a key listed twice; a word or a sentence holding `\|`, and a label holding a comma or a parenthesis, which the Conventions table cannot carry |
| PFV4 | a word or a key label that ends in する or します |
| PFV5 | no evidence, an entry without `id`, `source`, `url` (https) or `says`, or an evidence id used twice |
| PFV6 | a value that differs from what `inherit` gives with no evidence in `from`, or a `from` entry naming an id the evidence lacks |
| PFV7 | a product without a `name` or a `set`, or a `set` naming an item a profile does not have |

All seven are errors.

### T24: `scripts/validate_tokens.py`

`meta.profile` names no file under `profiles/`, `meta.profile_product` is set while `meta.profile` is `null`, or it names a product outside the profile's `products` (`references/tokens-format.md`).

### PF0 to PF7: `scripts/check_profile.py`, on the source (Step 4)

```bash
python {SKILL_DIR}/scripts/check_profile.py <paths> --json
```

It reads the `## Conventions` section of `ui-brief.md` beside the nearest `tokens.json` (`--brief` names another) and the markup and script files of the screen. A control whose text is computed is passed over: the checks compare literals. A brief whose section holds `none`, or that has no such section, gives no finding.

| ID | Check |
|---|---|
| PF0 | a suppression with no reason; it silences nothing |
| PF1 | a control marked `data-action` whose text is a literal that differs from the word the section gives the operation |
| PF2 | a function key or a shortcut: a `data-key` or a key of a `keys` list that the section lacks, one whose label or action differs from the section's, or the registering key of the section carried by no file of a screen that holds an entry form. A key whose operation the screen lacks is left out of the build (`patterns/action.function-keys.json`), and its absence is no finding |
| PF3 | `confirm.register` is `always`, a control registers (`data-action="register"`) and no `data-confirm="register"` is in the files; or it is `never` and one is |
| PF4 | a `data-required-mark` whose value differs from `required_mark` |
| PF5 | `keys.enter` is `next-field` and an entry form (`data-pattern="entry.slip"` or `master.form`) is in the files with no `data-enter="next-field"`; or it is `none` and one is |
| PF6 | a `data-message` whose kind differs from `messages.result`, or a `data-duration` that differs from `messages.duration_ms` |
| PF7 | `waiting.block` is `button`, and a control that registers (`data-action="register"`) lacks `data-guard="button"`: a second click reaches it while the first run is under way. Or it is `screen`, a control registers and no element carries `data-guard="screen"` |

PF1 to PF7 are errors. The checks read the attributes of elements: a note or an example inside a comment is passed over, and so is a key written as an expression. Silence a misfire in the file, as `product-ui: ignore PF1 <reason>` on the line before or the same line, or `product-ui: ignore-file PF2 <reason>`; name the reason in the hand-over. A finding on the screen as a whole (the registering key carried by no file, the missing confirmation, the missing layer) is silenced by `ignore-file` in any file of the screen.

### R49 to R51, on the rendered page (Step 5)

`cdp.js` takes `PROBE`, a list of `keys` and `messages`, and writes what it measured into the dump as `probes`, after the screenshot and the dump are taken. With `keys` it presses Enter and Shift+Enter in the first field of the entry form and then every key a control carries in `data-key`; the submit and the clicks are stopped before the page's own handlers, so no operation runs. With `messages` it records each `data-message` element with the time it stayed. `check_render.py` compares the probes with the Conventions section of the brief (`--plan`). All three are warnings, and a capture without `probes`, or a brief without conventions, skips them.

```bash
PROBE=keys DUMP={OUT}/keys-1280.json node {SKILL_DIR}/scripts/render/cdp.js http://127.0.0.1:<port>/orders/new 1280
PROBE=messages DUMP={OUT}/registered-1280.json node {SKILL_DIR}/scripts/render/cdp.js http://127.0.0.1:<port>/orders/new 1280 "<an expression that runs the registration>"
```

The second capture needs the expression that fills the required fields, runs the registration and answers its confirmation, so that the result message is on the screen when the probe starts.

| ID | Check |
|---|---|
| R49 | `keys.enter` is `next-field`, and Enter in the first field of the entry form left the focus where it was, moved it elsewhere than the next field, or submitted the form; or Shift+Enter did not bring it back |
| R50 | the registering key of the section carried by no control on a page that holds an entry form, or a key or a shortcut whose control did not run when it was pressed. Before it presses a key that the lines of a slip carry, the probe puts the focus in a line |
| R51 | a result message that stayed for a time other than `messages.duration_ms` (500 ms of tolerance), that closed by itself under `until-closed`, or whose form differs from `messages.result` |

## Adding a profile or a product

1. Read the manuals, help pages or guidelines the vendor publishes for the family, and write what each says into `evidence`, with the URL. A page behind a sign-in stays unread; where the user supplies the material, record in the entry that the user supplied it.
2. Write each item. A value the pages do not state is `inherit`.
3. Give a product its own table where its pages state a value that differs inside the family, with the evidence in the product's `from`.
4. Run `validate.py`; then `resolve.py` and `scaffold.py` on a brief whose `tokens.json` names the profile.

A product whose pages differ from a family in a few items joins it as a product; a product or a platform whose keys, words or messages follow a scheme of its own gets a profile.
