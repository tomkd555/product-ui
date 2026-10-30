# UI copy

Source of record for checks C1 through C32, implemented by `scripts/check_copy.py`; change this file first when a check or a threshold changes. Read the rules at Step 3 before writing any string a user will see, and again when a check fails.

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
- Markup props: the `title`, `heading`, `subtitle`, `description`, `label`, `text`, `message`, `caption`, `emptyText` and `helperText` attributes of a capitalised component (`title` and `heading` read as a heading, `label` as a label, the rest as prose), and the first string argument of `toast(`, `toast.success(` and `toast.error(` (prose)
- Message catalogs: `.json` and `.ts` files under a directory named `locales`, `locale`, `i18n`, `messages` or `lang`
- Script files: `.ts`, `.js` and `.mjs` files outside those directories, so guide text, FAQ answers and sample data in `src/data/` are judged. A `key: "text"` entry whose key ends in `title`, `heading`, `label`, `description`, `text`, `message`, `body`, `caption`, `subtitle`, `question`, `answer`, `placeholder`, `button` or `cta` is classified by its key as a catalog entry is; any other string literal is `prose` when it holds Japanese characters. A line carrying `console.`, `logger.` or `throw` is skipped, and so are `*.d.ts` and `*.config.*` files

`scripts/ts_strings.py` holds this extraction for script and catalog files, and `check_shippable_text.py` reads them through it as well.

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

`prose` runs C1, C2, C9, C10, C11, C12, C15's `click here` / `lorem ipsum` pattern, C22, C23, C24, C25 and C27. textlint takes the remaining checks of Japanese prose; `--emit-prose` writes the Japanese strings out for it. English prose gets no further check: the English rules below apply while writing and at the Step 5 review.

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

A button names its operation, so its label is the verb's plain form (終止形). A サ変 verb keeps the noun alone, the shortest name of the operation (C3, C4).

| | |
|---|---|
| Write | 「保存」「アップロード」「閉じる」 |
| Replace | 「保存する」「アップロードします」「アップロードを行う」 |

A destructive action takes the same plain form: 「削除」, as SmartHR writes the execute button (research E79 (ui-defaults)). C4 reports 「削除する」 like any other サ変 + する label.

A confirmation dialog repeats the verb of the action that opened it: 「削除」 opens a dialog whose primary action is 「削除」. Its title is 「{対象}の削除」 (research E79 (ui-defaults)), as in 「report.pdf の削除」, so the reader confirms the right file. A permanent deletion gets one sentence: 「削除したファイルは復元できません」.

### Status labels

A status badge is a noun phrase that names the progress of the task or the action asked of the reader (SmartHR, research E82 (ui-defaults)). A state in progress takes 「○○中」: 「依頼準備中」「入力中」「回答中」 (research E83 (ui-defaults)). A badge that only announces novelty or liveness (`New`, `Live`, 「新着」) names neither; S18 reports it when it pulses.

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
- No `click here`, no bare `here`, and no bare `Learn more`: a link names what it opens (C15)
- No full stop at the end of a heading, label, button or single-sentence tooltip. A question mark is allowed
- An error says what happened and what to do next, in words that leave the reader blameless: `File must be 10 MB or smaller`
- No `oops`, `uh-oh`, `sorry` or humour in an error, and no `invalid`, `illegal` or `forbidden` (C16)
- A confirmation dialog repeats the verb on its primary button (`Delete file`) and its heading names what the action affects. C13 reports an `OK` button; C15 reports `Yes` and an `Are you sure?` heading
- No `e.g.`, `i.e.` or `etc.`: they do not survive translation
- Second person throughout; never mix `you`/`your` with `me`/`my` on one screen

The product decides the case convention, recorded in `voice.case`, and whether to use negative contractions (`don't`, `can't`). C30 reads the case of English buttons and headings of two words or more against `voice.case`. No check reads the button's verb and word count, the final full stop, `e.g.`/`i.e.`/`etc.`, second person or contractions; apply them while writing, and the Step 5 reviewer checks them.

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

**Check.** A `button` string matching `^[一-鿿]{2,4}する$`, destructive or not. 「関する」「対する」 carry one kanji and do not match; a button of the matching shape is a サ変 verb in practice.

**Allowed.** Nothing mechanical. A destructive button reads 「削除」, as SmartHR writes it (research E79 (ui-defaults)).

**On the threshold.** The pattern takes two to four kanji before 「する」. A label of that shape that is not a サ変 verb takes `ignore C4` with the reason.

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

**Check.** Project-wide, every kind including `prose`: both forms of one of the 12 pairs in `assets/voice_terms.ja.json` (ユーザ/ユーザー, サーバ/サーバー, ブラウザ/ブラウザー and the rest) anywhere in the scanned files. The short form counts only where no katakana follows it, so 「ユーザビリティ」 beside 「ユーザー」 passes.

**Why.** The three Japanese authorities give three conventions, so the defect is inconsistency inside one product. The message names the form `voice.katakana_choon` implies.

### C10: 用語辞書違反 (error)

**Check.** Every kind: any key of `voice.terms` in a string. The message carries the key's value as the replacement. With no `tokens.json` found, C10 is skipped and reported once as a warning saying so.

**Allowed.** A term in `voice.allow`. A project where 「消去」 names an operation distinct from 「削除」 lists it there, or removes the row from `voice.terms`.

**Why.** The copy equivalent of S1: the project settled the word, and the check asks whether the implementation used it.

### C11: 「！」の乱用 (warning)

**Check.** `!` or `！` in any string, `prose` included, outside a catalog key containing `success` or `toast`.

**Allowed.** A path segment named `marketing`, `landing` or `lp`. A success toast written in markup carries no key, so it takes `ignore C11` with the reason.

**Why.** 「！」 raises the pitch: right for a success toast, alarm in an error or an ordinary label.

### C12: 敬体と常体の混在 (warning)

**Check.** Per file, the strings carrying Japanese hold both a 敬体 ending (`です` / `ます` / `ました` / `ません` / `でした` before `。` or `！`) and a 常体 ending (`である` / `であった` / `だった` or `だ`).

**Allowed.** Strings ending in a noun, such as labels and log entries, match neither form, so a file holding only those passes.

### C13: 汎用ボタンラベル (warning)

**Check.** A `button` string that is exactly `OK` (or `Ok`, or the full-width `ＯＫ`), `確認`, `送信`, `実行`, `はい`, `いいえ`, `進む` or `完了`.

**Allowed.** Anything in `voice.allow`. `キャンセル`, `閉じる`, `戻る`, `次へ`, `保存` pass: they name their action already.

**On the threshold.** 「確認」 and 「完了」 are legitimate step names in a wizard, hence a warning; a wizard keeps them with `ignore C13` and the reason.

### C14: 文字数超過 (warning)

**Check.** Counted in 全角 characters, a wide, full-width or ambiguous-width character counting 1 and a narrow one 0.5: a `button` past 8, a `label` past 12, a `tooltip` past 80.

**Why.** The figures are a starting point with no design system behind them, hence warnings. A domain noun such as 「適格請求書発行事業者登録番号」 exceeds them legitimately.

### C15: 英語の空文言 (error)

**Check.** `button`, `link` or `heading` text that is exactly `here`, `read this`, `submit`, `confirm`, `yes`, `no` or `learn more` after case and trailing punctuation and symbols are stripped, or that begins `Are you sure`. `click here` and `lorem ipsum` are reported wherever they appear, prose included.

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

**Check.** Runs where `tokens.json` was found and `meta.name` holds 2 or more characters. A `heading` or `label` string that contains `meta.name` and is longer than it. A string equal to the name passes only where the `- Brand area:` line of the brief's `## Screen` section lists the product name; the check does not read the brief, and R24 in `scripts/render/check_render.py` reports the rendered name elsewhere. With no `tokens.json` found, C21 is skipped and C10's warning says so once.

**Allowed.** Anything in `voice.allow`.

**Why.** The Microsoft guidance quoted under C19 covers products as well as features: "In most cases, don't talk about products, features, or commands in headings". The reader already knows which product they are in. A brand element appears on a screen only where the brief's `Brand area` line lists it.

**On the threshold.** The comparison is a case-sensitive substring match. The alt text of a logo, 「◯◯ ロゴ」, contains the name and is longer than it, so it takes a `voice.allow` entry or `ignore C21` with the reason.

### C22: English stock word (warning)

**Check.** Every string, whatever its kind: a word of `assets/stock_words.json` under `english_stock` (`seamless`, `elevate`, `unlock`, `empower`, `transform`, `powerful`, `robust`, `intuitive`, `end-to-end`, `AI-driven`, and the buzzword phrases below), with an `s`, `es`, `d`, `ed`, `ing` or `ly` ending allowed, compared case-insensitively on whole words. One finding for each word and string.

**Added phrases.** The marketing-buzzword list of impeccable (`BUZZWORDS` in `crates/detect/src/regex_matchers.rs`, Apache-2.0, pbakaus/impeccable at commit df3a4abe) adds these to the same list, written as impeccable writes them: `streamline your`, `supercharge your`, `unleash your`, `unleash the power`, `leverage the power`, `best-in-class`, `industry-leading`, `world-class`, `enterprise-grade`, `next-generation`, `cutting-edge`, `revolutionize`, `game-changer`, `game changing`, `mission-critical`, `best of breed`, `future-proof`, `future proof`, `harness the power`, `trusted by leading`, `trusted by the world`, `drive engagement`, `drive growth`, `drive results`. The rest of impeccable's list (`empower your`, `transform your business`, `seamless experience`, `seamlessly integrate`, `built for the modern`) is already covered by `empower`, `transform`, `seamless` and the `for modern` template. Difference: impeccable counts every phrase on the page in one finding, and this check reports one finding for each phrase and string, as for the earlier words.

**Allowed.** Nothing mechanical. A string where the word names a real operation (`Transform` in a data tool) takes `ignore C22` and the reason.

**Why.** Five publishers name these words as the vocabulary of generated benefit copy (research T13: `report.md` section 6). Co-occurrence carries more signal than one word, and the list ages as models move to a second set, so the words live in the dated data file and the check is a warning. The style-guide rule beneath it: Microsoft says to omit unnecessary adverbs (research E95 (ui-defaults)).

### C23: Japanese stock word or headline template (warning)

**Check.** Every string: a word of `japanese_stock` (`革新的`, `最先端`, `ワンストップ`, `シームレス`, `最適なソリューション`) or a pattern of `headline_templates` (`次世代`, `あなたの課題を解決`, `for modern`, `The modern platform for`, `Streamline your workflow`, and the others in the file). One finding for each string, naming every hit.

**Allowed.** Nothing mechanical; `ignore C23` with the reason.

**Why.** Two Japanese publishers list the buzzwords (research T14), and four name the headline that fits any company (research T15). The competitor-swap test (would the line still read true under a competitor's logo?) stays with the reviewer. The style-guide rules beneath it: Microsoft on unnecessary words (research E95 (ui-defaults)) and GOV.UK on filler such as "please note" (research E92 (ui-defaults)). Japanese tell lists carry weak evidence: a practitioner test confirmed 1 of 148 popular claims and 403 readers detected AI text poorly (research E112, E119 (ui-defaults)). So 「を実現」 left the list as a plain product verb phrase.

### C24: negative parallelism (warning)

**Check.** English in any string: `not just/only/merely ... but`, `it's not ..., it's`, `isn't just/only/merely`. Japanese `ではなく` in a heading, or in any string where the surface is `lp`.

**Allowed.** `ignore C24` with the reason. A Japanese body string on a `saas` surface passes: 「〜ではなく〜」 is ordinary there.

**Why.** Publishers call "It's not X, it's Y" the most commonly identified generated-text tell (research T17), with false positives reported; hence a warning. Japanese tell lists carry weak evidence (research E112, E119 (ui-defaults)).

### C25: triad (warning)

**Check.** A heading or prose string of at most 60 characters made of three sentences of at most 24 characters each (`Save time. Work smarter. Scale faster.`, 「時間を節約。成長を加速。効率を改善。」), or three comma clauses (`Save time, work smarter, scale faster`; 「A、B、そしてC」).

**Allowed.** `ignore C25` with the reason; a list of three real items (`Name, email, phone`) is the misfire to suppress.

**Why.** Wikipedia's cleanup guide and a landing-page review name the rule of three (research T16). Japanese tell lists carry weak evidence (research E112, E119 (ui-defaults)).

### C26: Latin-only label on a Japanese screen (warning)

**Check.** Runs where `voice.lang` is `ja`. A string of kind `button`, `label`, `heading` or `link`, or a navigation item, made of Latin letters with no Japanese character and two or more letters.

**Allowed.** An all-capital acronym of four letters or fewer (`OK`, `API`); a key or value of `voice.terms`; anything in `voice.allow`; a string whose words all belong to `meta.name`.

**Why.** English labels such as `LOGIN` on a screen written from a Japanese brief mark an unedited first draft (research T24).

### C27: proof the brief does not hold (error)

**Check.** A proof-shaped string passes only when the `## Proof` section of `ui-brief.md` holds the same figure or name (compared with spaces and commas removed, case-insensitively). The brief is the `ui-brief.md` beside `tokens.json`, or the file `--brief PATH` names. No brief counts as an empty Proof section, so every proof-shaped string fails. On any surface:

- a testimonial: a quotation followed by a dash and a name, or (inside a `<blockquote>`, an element named `testimonial`, or a catalog or data key containing `testimonial`) a name with `様` or `さん` and a job title
- `trusted by`, `loved by`, `used by` or `relied on by` followed by a figure
- `No.1`, `ナンバーワン`, `業界初`, `導入社数`, `導入実績`

On an `lp` surface also:

- a figure with `+`, `%`, `x`, `×`, `倍`, `社` or `名以上` in a string that holds a marketing word (the list under `proof` in the data file)
- a rating out of 5 (`4.8/5`, `out of 5`, `★★★`)

**Allowed.** Whatever the Proof section holds with its source. Nothing else: the message says to take the string from the brief or delete it.

**Why.** Fake testimonials, placeholder customer logos and precise figures with no source harm the reader whether or not anyone suspects generation: fake-review cues lower trust and purchase intent (research T19). The brief is where the person who owns the product states what is true.

### C28: the same call to action three times (warning)

**Check.** On an `lp` surface, a `button` or `link` text that occurs three or more times in one file. One finding, at the third occurrence.

**Allowed.** `ignore-file C28` with the reason.

**Why.** The same call in every section is a listed tell of an unedited landing page (research T20); C13 and C18 cover only part of it.

**The `lp` surface** in C24, C27 and C28 is `meta.surface` of the `tokens.json` the script finds; with no surface there, a path segment named `marketing`, `landing` or `lp` (the order `check_shippable_text.py` uses).

### C29: English error filler (warning)

**Check.** An `error` string that contains the word `please`, or that equals `This field is required` or `Required` after trimming and case folding. `invalid` stays with C16.

**Allowed.** A path segment named `admin`, `debug`, `audit` or `devtools`, as for C6 and C16. No Japanese counterpart exists: the run found no source for one.

**Why.** GOV.UK names `This field is required` among the generic messages to avoid (research E91 (ui-defaults)) and says there is usually no need to say "please" (research E92 (ui-defaults)). Atlassian: "Avoid using “please” and “sorry”" (research E98 (ui-defaults)).

### C30: case of English buttons and headings (warning)

**Check.** Runs where `voice.case` is `sentence` or `title`; `null` skips it. A `button` or `heading` string of two or more words with no Japanese character. Under `sentence`: a word after the first that starts with a capital letter. Under `title`: a lower-case word of five or more letters. Words of `meta.name`, of `voice.terms` (keys and values) and of `voice.allow`, and all-capital acronyms, pass. One finding for each string.

**Allowed.** The words above; `ignore C30` with the reason.

**Why.** GOV.UK writes button text in sentence case (research E89 (ui-defaults)); Microsoft applies sentence-style capitalisation to UI labels (research E94 (ui-defaults)); Apple writes title case. The project's `voice.case` decides which.

**On the threshold.** The five-letter limit under `title` is this skill's own choice: it leaves short articles, conjunctions and prepositions alone without a word list.

### C31: aphoristic cadence (warning)

**Check.** Each string is searched alone, so a construction never spans two elements, for two shapes of impeccable's `aphoristic-cadence` (`NOT_A_RE` and `SHORT_REBUTTAL_RE` in `crates/detect/src/regex_matchers.rs`, df3a4abe): `Not a` or `Not an`, a lower-case word and up to 40 more characters, a full stop or `!`, then a capitalised sentence of up to 60 characters ending in a full stop or `!` ("Not a feature. A platform."); and a capitalised sentence of 5 to 81 characters ending in a full stop or `!`, then `No` or `Just` and a lower-case clause of 3 to 61 characters ending in a full stop or `!` ("Built for teams. Just results."). The two shapes can match one pair ("Not a tool. Just a platform."); a pair inside one string counts once. The finding comes at 3 or more constructions in the file, at the line of the first one, and is a warning. Two constructions pass.

**Allowed.** `ignore C31` on the line of the first construction, or `ignore-file C31`, with the reason. Japanese strings carry no capital letters and pass. impeccable reads the text of a whole page, joined; this check counts the constructions of each string and adds them over a whole file, so a file of several screens counts them together.

**Why.** Three or more sections that land on a short rebuttal read as one cadence, and once is fine (impeccable's rule text). The check is a warning for the reason C22 is.

### C32: theater framing (warning)

**Check.** Every string: a word of `assets/stock_words.json` under `theater.dismissive_heads` (`security`, `compliance`, `growth`, `hiring`, `process`, `trust` and the others in the file) followed by `theater`, case-insensitively on whole words. One finding for each string. The list is closed on purpose, as in impeccable's `theater-slop-phrase` (`THEATER_DISMISSIVE_HEADS` in `crates/core/src/checks/html_patterns.rs`, df3a4abe): any other word before `theater` names a building, a stage or a war zone ("the official theater", "Southern Theater Command") and passes. impeccable reads the page text once; this check reads each string.

**Allowed.** `ignore C32` with the reason, where the string quotes the phrase.

**Why.** Calling a practice "theater" is a recurring tic of generated copy; say plainly what the thing does or does not do (impeccable's rule text).

## Suppressing a misfire

The same two forms as `slop-checklist.md`, read by `check_copy.py`:

| Form | Where | Silences |
|---|---|---|
| `product-ui: ignore C13 <reason>` | the line before the string, or the same line | that ID on that line. For the per-string checks: C1–C8, C10, C11, C13–C19, C21–C27, C29, C30, C32 |
| `product-ui: ignore-file C12 <reason>` | anywhere in a scanned file | that ID for the whole file. For the per-file checks C9, C12, C20, C28 and C31, and for any per-string check the file legitimately repeats |

A form with no reason is reported as **C0 (warning)** and suppresses nothing. Message catalogs (`.json`) carry no comments; there `voice.allow` covers C10 (a listed term), C13 (a listed label), C17 (a listed navigation item) and C18, C19, C21 and C26 (a listed string), and a catalog string any other check reports is rewritten.

Suppress only a misfire, where the check read the string wrong. A string read correctly is rewritten or deleted; preferring it is no reason to silence the check.

## Rules left to the reviewer

These two would fire on correct copy, and a check that fires on good copy teaches its reader to skip the output. A reviewer applies them by hand.

| Rule | Reason |
|---|---|
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

## Measured on the rendered page

`scripts/render/check_render.py` measures these at Step 5, ported from impeccable 4.8.0 (Apache-2.0; see `THIRD_PARTY_NOTICES.md`).

- **R38: all-caps body.** A WARNING for `text-transform: uppercase` on 80 or more characters of an element's own text outside headings and their descendants. Keep uppercase for short labels. Source: impeccable `all-caps-body`. Not ported: nothing known.
- **R40: the same text repeated in one container.** A WARNING when the same text (4 to 48 characters, with a Latin letter) is rendered at 3 or more structurally different spots inside one card. Japanese-only text is outside this check. Say it once, where it matters most. Source: impeccable `repeated-container-text`. Not ported: the full paint test (`is_visible` is simplified).
