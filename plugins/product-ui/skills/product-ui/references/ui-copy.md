# UI copy

Source of record for checks C1 through C21, implemented by `scripts/check_copy.py`; change this file first when a check or a threshold changes. Read the rules at Step 3 before writing any string a user will see, and again when a check fails.

## What is actually being judged

None of the checks in `slop-checklist.md` reads a word. Words fail in three ways a script can decide:

1. **A form the project already settled**: 敬体 or 常体, the shape of a button label, the word for an operation. `tokens.json` holds it under `voice`, so a diff decides.
2. **A phrase that carries no information**: 「エラーが発生しました」, `Something went wrong`, a bare 「こちら」. Closed sets, so a pattern decides.
3. **A grammatical shape that marks unedited generation**: 「〜することができます」, 「〜を行う」, a form label written as a sentence.

The rest needs the rendered page and a reader: Step 5 (Out of reach for this script).

## Where the Japanese rules come from

DADS leaves the wording of buttons, labels and error messages to each project, so a DADS project takes its wording rules from this file.

| Source | What it settles here |
|---|---|
| 文化審議会「[公用文作成の考え方](https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/93650001_01.html)」（建議、令和4年1月7日） | The citable authority for 表記 and 用語 when the client is public-sector |
| 文化審議会「敬語の指針」 | 二重敬語 and 「させていただく」 |
| wordrabbit UXライティングガイド | One of the 長音 conventions `voice.katakana_choon` offers |
| JTF日本語標準スタイルガイド | 全角・半角, 長音符 (the conventions differ between guides: see `voice.katakana_choon`) |

The button and label forms, the operation vocabulary, the punctuation and the error-message structure are this skill's own rules. Further reading: the SmartHR Design System's writing guidelines, https://smarthr.design/products/contents/.

## Scope

`scripts/check_copy.py` reads:

- Markup: `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`
- Message catalogs: `.json` and `.ts` files under a directory named `locales`, `locale`, `i18n`, `messages` or `lang`

Excluded: `node_modules/`, `dist/`, `build/`, `.next/`, `.git/`, `.svelte-kit/`, `coverage/`, `*.test.*`, `*.spec.*`, `*.min.*`, and any path segment named `legal`, `terms`, `privacy` or `policy` (the carve-out).

### Every string is classified before any rule runs

A rule that fits a button ruins a paragraph, so each string is sorted into one of eight kinds, and only that kind's checks run on it.

| Kind | Recognised by |
|---|---|
| `button` | `<button>`, `<Button>`, `<AlertDialogAction>`, `<AlertDialogCancel>`, `<MenuItem>`, `<DropdownMenuItem>`, `role="button"`, a catalog key segment `button` / `btn` / `action` / `cta` |
| `label` | `<label>`, `<Label>`, `<FormLabel>`, `aria-label=`, `alt=`, a key segment `label` / `field` |
| `heading` | `<h1>`–`<h6>`, `<CardTitle>`, `<DialogTitle>`, `<AlertDialogTitle>`, `<SheetTitle>`, `<DrawerTitle>`, a key segment `title` / `heading` |
| `link` | `<a>`, `<Link>`, `<NavLink>`, a key segment `link` |
| `error` | `<FormMessage>`, `<AlertTitle>`, `role="alert"`, a key segment `error` / `err` / `invalid` / `failed` |
| `tooltip` | `title=` on an element, `<TooltipContent>`, a key segment `tooltip` / `hint` |
| `placeholder` | `placeholder=`, a key segment `placeholder` |
| `prose` | everything else: descriptions, help text, empty-state bodies, notification mail |

A catalog key is split on `.`, `_`, `-` and `/`, and the first segment equal to one of the words above decides the kind; where no segment is equal to one, a key containing one of the words decides it. Both passes try the words in this order: `error`, `err`, `invalid`, `failed`, `button`, `btn`, `action`, `cta`, `label`, `field`, `title`, `heading`, `tooltip`, `hint`, `placeholder`, `link`.

`prose` runs C1, C2, C9, C10, C12 and C15's `click here` / `lorem ipsum` pattern. Its remaining checks belong to textlint; `--emit-prose` writes those strings out for it.

C17, C18 and C19 read a navigation mark:

- **Markup**: set on the text of an element inside `<nav>`, `<NavigationMenu>`, `<SidebarMenu>` or an element carrying `role="navigation"`. A block stays unmarked when its opening tag, or its first child's opening tag, carries `breadcrumb` or `パンくず`.
- **Catalogs**: set on a string whose key has a segment `nav`, `navigation` or `sidebar` (the full key path in a `.json` catalog, the entry's own key in a `.ts` one). A string of kind `placeholder` or `tooltip` stays unmarked.
- **Attributes**: `aria-label`, `placeholder`, `title` and `alt` strings stay unmarked.

A breadcrumb ending in 「編集」 and a search field inside the navigation therefore pass.

## The carve-out

Do not rewrite, and do not report against, four kinds of string:

- Legal, regulated and consent copy: 利用規約, プライバシーポリシー, 特定商取引法に基づく表記, 金融商品の説明
- A verbatim quotation or a phrase a statute fixes
- An established product term, even a clumsy one, and a proper noun
- A term the business defines, where a translation would hide which word the specification names

Flag a concern about one of these and leave the decision to the user: an automated copy pass that edits a consent screen causes a larger problem than the one it fixes.

## Japanese rules

### Button labels

A button names its operation, so its label is the verb's plain form (終止形). A サ変 verb keeps the noun alone, the shortest name of the operation, which leaves the 「する」 form to mark a destructive action (C3, C4).

| | |
|---|---|
| Write | 「保存」「アップロード」「閉じる」 |
| Replace | 「保存する」「アップロードします」「アップロードを行う」 |

A destructive action takes the fuller 「削除する」 to make its weight visible; C4 lists the markings the script reads, usually `variant="destructive"` or `className="danger"`.

A confirmation dialog repeats the verb of the action that opened it: 「削除」 opens a dialog whose primary action is 「削除する」. Its heading names the object that disappears (「report.pdf を削除しますか？」), so the reader confirms the right file. A permanent deletion gets one sentence: 「削除したファイルは復元できません」.

### Form labels

A label is the name of the item; an instruction goes into help text, or nowhere (C7).

| | |
|---|---|
| Write | 「表示名」「ファイル名」 |
| Replace | 「表示名を入力してください」「ファイル名をご入力ください」 |

Help text names the format or the limit: 「PNGまたはJPEG、10MBまで」. Whether help text appears at all belongs to `references/ban-list.md`.

### Notes, captions and legends

A note that survives `references/ban-list.md` says what the figure is, in the surface's register, and stops: 「購入まで進んだセッションを、全セッション数で割った値です」 is a tooltip's sentence. A note negating the figure, the method or a conclusion (「セッション数ではない」「季節変動は補正していない」「ボットのアクセスは除いていない」) records the author's working; ban-list.md's ST9 reports the ones carrying a method word. A data-fact note under a chart states the fact in the positive: 「集計対象は支払いが完了した注文だけです」. A negation ships only as a statute's own wording, under the carve-out.

### Error messages

An error message says what happened, why, and what to do next. With room for one sentence, keep the one that says what to do: the reader can act on it alone.

| | |
|---|---|
| Replace | 「エラーが発生しました」「アップロードに失敗しました」「不正なファイル形式です」 |
| Write | 「ファイルが10MBを超えているため、アップロードできませんでした。10MB以下のファイルを選んでください」 |
| Replace | 「10MBを超えるファイルは使えません。」 |
| Write | 「10MB以下のファイルを選んでください。」 |

The error states what the product accepts. 「間違っています」「失敗しました」 put the fault on the reader and leave the fix unsaid.

### Register and 敬語

敬体 (です・ます) by default; the project records its choice in `voice.register`, and one surface keeps one register. 「〜してください」 is the recommended polite request, and C2 reports the polite form stacked past what the sentence needs.

| | |
|---|---|
| Write | 「ファイル名を確認してください。」「設定を保存しました。」 |
| Replace | 「ファイル名をご確認いただけますようお願いいたします。」「設定を保存させていただきました。」 |

### Words and characters

- Use the short verb form: 「◯◯できます」 for 「◯◯することができます」, and 「アップロードする」 or 「アップロードしてください」 for 「アップロードを行う」「アップロードを実行する」 (C1)
- Keep the case particles: 「通知設定を保存します」 carries its 「を」. A phrase stripped of its particles reads as a compound noun
- Before writing a katakana loanword, check whether a word the reader already knows says the same thing, as 公用文作成の考え方 asks of public-sector text: the screen gives no help in working a loanword out
- Write kanji with the readings in the 常用漢字表: 「分かる」 for 「解る」
- Join half-width and full-width characters with no space: 「ZIP形式」 (JTF日本語標準スタイルガイド)
- Write katakana in full width

A heading, a label and a button name something, so they end without 「。」 (C8). A sentence ends with 「。」 wherever it appears, a one-sentence tooltip included. 「！」 is kept for a toast that reports success (C11).

### The operation vocabulary

One word per operation, across the whole product. Step 1 settles the words in `voice.terms`: each key is a word the product stops using, its value the word the product uses. Read the words on the existing screens, then settle one entry for every operation where two words compete.

C10 reports the keys, so a project whose business itself says 「サインイン」 leaves it out of `voice.terms`.

## English rules

This skill's own rules for English copy; route anything past them to `interfaces:better-writing`.

- Sentence case for buttons, headings, labels and menu items: `Upload file`
- A button label is a verb, or a verb and a noun, in three words or fewer
- No `click here`, no bare `here`, and no bare `Learn more`: a link names what it opens
- No full stop at the end of a heading, label, button or single-sentence tooltip. A question mark is allowed
- An error says what happened and what to do next, in words that leave the reader blameless: `File must be 10 MB or smaller`
- No `oops`, `uh-oh`, `sorry` or humour in an error, and no `invalid`, `illegal` or `forbidden`
- A confirmation dialog repeats the verb on its primary button (`Delete file`) and its heading names what the action affects. C13 reports an `OK` button; C15 reports `Yes` and an `Are you sure?` heading
- No `e.g.`, `i.e.` or `etc.`: they do not survive translation
- Second person throughout; never mix `you`/`your` with `me`/`my` on one screen

The product decides the case convention, recorded in `voice.case`, and whether to use negative contractions (`don't`, `can't`); no check reads the latter.

## Checks

An error means the string contradicts something the project settled or carries no information. A warning means it departs from this skill's recommendation and a reason may exist.

### C1: 冗長表現 (error)

**Check.** Every kind: `することができ(る|ます|ません)`, `を行(う|い|います|った|って)`, `を実行(する|します)`.

**Why.** Each wraps the verb in words that add no information, and they are the most common trace of unedited Japanese.

### C2: 過剰敬語 (error)

**Check.** Every kind: `ご[぀-ヿ一-鿿]{1,8}いただけますよう`, `させていただ`, `お[぀-ヿ一-鿿]{1,8}になられ`, `ご[一-鿿]{1,8}してください`. The last takes kanji alone between ご and してください, so 「ご確認してください」 is caught and 「ご自身で設定してください」 passes.

**Allowed.** The carve-out: consent and legal surfaces keep the register they were drafted in.

**Why.** Stacked 敬語 lengthens the sentence and adds nothing. 「ご〜してください」 applies a humble form to the reader's own action, a misuse under 文化審議会「敬語の指針」.

### C3: ボタンが丁寧形 (error)

**Check.** A `button` string ending `ます` or `ました`.

**Why.** 「アップロードします」 reads as a sentence the screen says to the user (Button labels).

### C4: サ変ボタンの「する」 (warning)

**Check.** A `button` string matching `^[一-鿿]{2,4}する$`. 「関する」「対する」 carry one kanji and do not match; a button of the matching shape is a サ変 verb in practice.

**Allowed.** An element marked destructive: an attribute on it, or its catalog key, containing `destructive`, `danger`, `delete`, `destroy` or `remove`.

**On the threshold.** A project that signals danger some other way sees this misfire. Add the marking to the element; it also tells assistive technology and the next reader that the action destroys data.

### C5: 「こちら」 (error / warning)

**Check.** Link text that is exactly `こちら`, `詳しくはこちら`, `こちらから`, `こちらをご覧ください` or `こちらをクリック`: error. `こちら` inside longer link text: warning.

**Why.** A screen reader reaches a link out of context, and there 「こちら」 names nothing.

### C6: プログラム目線のエラー (error)

**Check.** In an `error` string: `エラーが発生しました`, `に失敗しました`, `不正な`, `無効な`. Also `できませんでした` where the same string carries none of `てください` or `でください`, `お試し`, `確認`, `もう一度`, `やり直`: the phrase is fine once the fix follows it.

**Allowed.** A path segment named `admin`, `debug`, `audit` or `devtools`, where precision beats readability.

### C7: ラベルが文になっている (error)

**Check.** A `label` string ending `してください`, `を入力`, `を選択`, `をご入力` or `をご選択`; `を入力してください` is caught through `してください`.

### C8: ラベル末尾の句読点 (error)

**Check.** A `button`, `label` or `heading` string ending `。` or `、`.

**Allowed.** `tooltip` and `prose`. A string ending `？` or `?`.

**On the threshold.** A heading misclassified through an unusual component name misfires here; fix the classification table and keep the check.

### C9: 長音符の不統一 (error)

**Check.** Project-wide, every kind including `prose`: both forms of one of the 12 pairs in `assets/voice_terms.ja.json` (ユーザ/ユーザー, サーバ/サーバー, ブラウザ/ブラウザー and the rest) anywhere in the scanned files.

**Why.** The three Japanese authorities give three conventions, so the defect is inconsistency inside one product. The message names the form `voice.katakana_choon` implies.

### C10: 用語辞書違反 (error)

**Check.** Every kind: any key of `voice.terms` in a string. The message carries the key's value as the replacement. With no `tokens.json` found, C10 is skipped and reported once as a warning saying so.

**Allowed.** A term in `voice.allow`. A project where 「消去」 names an operation distinct from 「削除」 lists it there, or removes the row from `voice.terms`.

**Why.** The copy equivalent of S1: the project settled the word, and the check asks whether the implementation used it.

### C11: 「！」の乱用 (warning)

**Check.** `!` or `！` in any string other than `prose`, outside a catalog key containing `success` or `toast`.

**Allowed.** A path segment named `marketing`, `landing` or `lp`. A success toast written in markup carries no key, so it takes `ignore C11` with the reason.

**Why.** 「！」 raises the pitch: right for a success toast, alarm in an error or an ordinary label.

### C12: 敬体と常体の混在 (warning)

**Check.** Per file, the strings carrying Japanese hold both a 敬体 ending (`です` / `ます` / `ました` / `ません` / `でした` before `。` or `！`) and a 常体 ending (`である` / `であった` / `だった`, or `だ` where the preceding character is not part of a 敬体 form).

**Allowed.** Strings ending in a noun, such as labels and log entries, match neither form, so a file holding only those passes.

### C13: 汎用ボタンラベル (warning)

**Check.** A `button` string that is exactly `OK` (or `Ok`, or the full-width `ＯＫ`), `確認`, `送信`, `実行`, `はい`, `いいえ`, `進む` or `完了`.

**Allowed.** Anything in `voice.allow`. `キャンセル`, `閉じる`, `戻る`, `次へ`, `保存` pass: they name their action already.

**On the threshold.** 「確認」 and 「完了」 are legitimate step names in a wizard, hence a warning; a wizard keeps them with `ignore C13` and the reason.

### C14: 文字数超過 (warning)

**Check.** Counted in 全角 characters, a wide, full-width or ambiguous-width character counting 1 and a narrow one 0.5: a `button` past 8, a `label` past 12, a `tooltip` past 80.

**Why.** The figures are a starting point with no design system behind them, hence warnings. A domain noun such as 「適格請求書発行事業者登録番号」 exceeds them legitimately.

### C15: 英語の空文言 (error)

**Check.** `button`, `link` or `heading` text that is exactly `here`, `read this`, `submit`, `confirm`, `yes`, `no` or `learn more` after case and trailing punctuation are stripped, or that begins `Are you sure`. `click here` and `lorem ipsum` are reported wherever they appear, prose included.

**Allowed.** `Save`, `Cancel`, `Close`, `Back`, `Next`, `Skip`, `Done`: each names a complete action with no object.

### C16: 英語のエラー禁止語 (error)

**Check.** In an `error` string: `oops`, `uh-oh`, `whoops`, `sorry`, `invalid`, `illegal`, `forbidden`, `prohibited`, `you forgot`. Also `something went wrong` where the same string carries none of `try`, `refresh`, `reload`, `retry`, `contact`, `check`.

**Allowed.** A path segment named `admin`, `debug`, `audit` or `devtools`, as for C6.

**Why.** The [GOV.UK Design System](https://design-system.service.gov.uk/components/error-message/) names `forbidden`, `illegal`, `you forgot`, `prohibited`, `sorry`, `invalid` and `oops` among the words an error message avoids; `uh-oh`, `whoops` and a bare `something went wrong` are the same kind. `invalid` gives the reader nothing to act on.

### C17: ナビゲーション項目がタスク名 (error)

**Check.** Runs only when `meta.structure` in `tokens.json` is `ooui`, on every string marked as a navigation item, whatever its kind. Japanese: an item that starts with `新規`, ends with `する`, `します` or `を` followed by one to eight characters, or carries at least one character before a final `登録`, `作成`, `追加`, `編集`, `変更`, `削除`, `照会`, `入力`, `検索`, `出力`, `発行` or `送信`. English: an item that starts with `create`, `add`, `edit`, `register`, `delete`, `remove` or `search` followed by another word. With no `tokens.json` found, C17 is skipped, and C10's warning names C17 and C21 as well.

**Allowed.** Anything in `voice.allow`. An action noun away from the item's end: 「変更履歴」「登録情報」. The action noun alone: a bare 「検索」 opens a product-wide search.

**Why.** Under `references/ooui.md` the navigation lists objects, and an action sits on its object. 「顧客登録」「顧客検索」「顧客照会」 as three items are one object, 顧客, with three actions.

**On the threshold.** The list holds words that name an action and nothing else. 「申請」「承認」「注文」「予約」「管理」 name an object or a queue as often as an action, and `New` and `Update` open 「New arrivals」 and 「Update history」; those go to the reviewer through structure question 1 in the brief. A task flow the brief admits (`references/ooui.md`, Choosing the structure) keeps its navigation entry with `ignore C17` and the reason.

### C18: generic label (warning)

**Check.** A string of kind `heading` or `label`, or any string marked as a navigation item, whose trimmed text is exactly `概要`, `詳細`, `情報`, `管理`, `各種`, `その他`, `Overview`, `Details`, `Information`, `More` or `Dashboard`. English is compared case-insensitively. The message reads "generic label; name the object or the task it governs".

**Allowed.** Anything in `voice.allow`.

**Why.** A label is judged from its text alone: Nielsen Norman Group's [Information Scent: How Users Decide Where to Go Next](https://www.nngroup.com/articles/information-scent/) treats the words of a link as the cue a reader follows or skips, and `More` and `Learn more` are labels with low information scent. 「概要」 and 「詳細」 sit on every screen of a product and so tell the reader nothing about this one.

### C19: feature-shaped label (warning)

**Check.** A `heading` string or a navigation string that:

- ends with `機能`,
- starts with `各種`,
- matches `^[一-鿿ぁ-んァ-ヶー]{1,8}管理$` (one to eight kanji, hiragana, katakana or 長音 characters, then 管理), or
- in English matches `\b\w+ management$`, case-insensitively.

A string C18 already reports is reported once. The message names the pattern matched and asks for the object or the task.

**Allowed.** Anything in `voice.allow`. 機能 or 各種 away from its end or start: 「機能の一覧」. A lone `Management` passes; a lone `管理` is C18's.

**Why.** Microsoft's Writing Style Guide, [Headings](https://learn.microsoft.com/en-us/style-guide/scannable-content/headings), advises: "In most cases, don't talk about products, features, or commands in headings". Shopify Polaris, in its [Naming](https://raw.githubusercontent.com/Shopify/polaris-react-archive/main/polaris.shopify.com/content/content/naming.mdx) guidance, makes the same point from the product side: "Most features don't need an official, branded name". 「ユーザー管理機能」 names the feature the screen belongs to, where 「ユーザー」 or 「ユーザーを招待」 names the object or the task.

**On the threshold.** The 「機能」「各種」「管理」 patterns are this skill's inference from those sources, and no source names them. That is why C19 is a warning. A business whose own term is 「顧客管理」 lists it in `voice.allow`.

### C20: duplicate heading (warning)

**Check.** Per file, two or more `heading` strings with identical trimmed text. The finding is reported at the second and later occurrences.

**Allowed.** Nothing mechanical. A file whose repeat is intended, such as two tab panels that each open with the name of their tab, takes `ignore-file C20` and the reason.

**Why.** Rosenfeld and Morville, *Information Architecture for the World Wide Web*, ch. 5, put the cost of inconsistent labels this way: "using the label Main, on one page, Main Page on another, and Home elsewhere will surely destroy the familiarity". One label for one place is what keeps a screen familiar, and two headings with one name break the rule from the other side: the reader cannot tell which place they are in.

**On the threshold.** The source argues for one place under one label. Applying it to one label over two places is this skill's extension, which is why C20 is a warning.

### C21: product name in a heading or label (warning)

**Check.** Runs where `tokens.json` was found and `meta.name` holds 2 or more characters. A `heading` or `label` string that contains `meta.name` and is longer than it. A string equal to the name passes: it is a logo or a sidebar title. With no `tokens.json` found, C21 is skipped and C10's warning says so once.

**Allowed.** Anything in `voice.allow`.

**Why.** The Microsoft guidance quoted under C19 covers products as well as features: "In most cases, don't talk about products, features, or commands in headings". The reader already knows which product they are in, and the name in the logo and the title says it once.

**On the threshold.** The comparison is a case-sensitive substring match. The alt text of a logo, 「◯◯ ロゴ」, contains the name and is longer than it, so it takes a `voice.allow` entry or `ignore C21` with the reason.

## Suppressing a misfire

The same two forms as `slop-checklist.md`, read by `check_copy.py`:

| Form | Where | Silences |
|---|---|---|
| `product-ui: ignore C13 <reason>` | the line before the string, or the same line | that ID on that line. For the per-string checks: C1–C8, C10, C11, C13–C19, C21 |
| `product-ui: ignore-file C12 <reason>` | anywhere in a scanned file | that ID for the whole file. For the per-file checks C9, C12 and C20, and for any per-string check the file legitimately repeats |

A form with no reason is reported as **C0 (warning)** and suppresses nothing. Message catalogs (`.json`) carry no comments; there `voice.allow` covers C10 (a listed term), C13 (a listed label), C17 (a listed navigation item) and C18, C19 and C21 (a listed string), and a catalog string any other check reports is rewritten.

Suppress only a misfire, where the check read the string wrong. A string read correctly is rewritten or deleted; preferring it is no reason to silence the check.

## Rules left to the reviewer

These three would fire on correct copy, and a check that fires on good copy teaches its reader to skip the output. A reviewer applies them by hand.

| Rule | Reason |
|---|---|
| Title case in English buttons and headings | Needs a per-project list of proper nouns and acronyms to tell `Google Drive` from `Upload New File`. Add it once such a list exists |
| The [GOV.UK words to avoid](https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style#words-to-avoid) (`key`, `deploy`, `drive`, `portal`, `impact`, `land`) | Each carries an ordinary technical sense. The list stays available for public-sector work, applied by hand |
| Gerund headings (`Getting started`) | `Getting started` is common and correct |

## Out of reach for this script

Step 5, through `review-design-lead`, judges these against the rendered page:

- Whether the button label names what the button actually does. `保存` on a control that publishes passes every check here
- Whether the cause the error states is the real cause, and one the reader can act on
- Whether the heading is specific to this screen. 「設定」 passes every check and carries nothing; C18 reports 「概要」「詳細」「情報」
- Whether the copy is true (「削除したファイルは復元できません」 on a file the trash can restore, or a dialog understating what it deletes)
- Whether one object is called by one name throughout, when the names are not in `voice.terms` yet
- Whether the empty state's action is the right next action for a reader who cannot perform it
- Whether the register the tokens settle (敬体 or 常体) suits this audience: 敬体 on an internal operations screen, 常体 on a public form
