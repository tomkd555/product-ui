# UI copy

This file is the source of record for checks C1 through C16. `scripts/check_copy.py` implements the rules written here; change this file first when a check or a threshold changes.

It also carries the material Step 3 works from. Read the rules before writing any string a user will see, and again when a check fails.

## What is actually being judged

A screen can pass every check in `slop-checklist.md` and still be unusable, because none of those checks reads a word. The words fail in a way that is separable from taste:

1. **A form the project already settled** — 敬体 or 常体, the shape of a button label, which word this product uses for an operation. `tokens.json` holds the answer under `voice`, so a diff decides it.
2. **A phrase that carries no information** — 「エラーが発生しました」, `Something went wrong`, a bare 「こちら」. These are closed sets, so a pattern decides them.
3. **A grammatical shape that marks unedited generation** — 「〜することができます」, 「〜を行う」, a form label written as a sentence.

Everything past that — whether the label names what the button actually does, whether the heading is specific to this screen — needs the rendered page and a reader. Step 5 takes it.

## Where the Japanese rules come from

A project on the Digital Agency Design System takes its wording rules from this file: DADS publishes its visual foundations and components, and the wording of buttons, labels and error messages is left to each project.

| Source | What it settles here |
|---|---|
| 文化審議会「[公用文作成の考え方](https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/93650001_01.html)」（建議、令和4年1月7日） | The citable authority for 表記 and 用語 when the client is public-sector |
| 文化審議会「敬語の指針」 | 二重敬語 and 「させていただく」 |
| wordrabbit UXライティングガイド | One of the 長音 conventions `voice.katakana_choon` offers |
| JTF日本語標準スタイルガイド | 全角・半角, 長音符 (the conventions differ between guides — see `voice.katakana_choon`) |

The button and label forms, the operation vocabulary, the punctuation and the error-message structure below are this skill's own rules. For further reading on Japanese product writing, the SmartHR Design System publishes its writing guidelines at https://smarthr.design/products/contents/.

English rules come from Shopify Polaris, GOV.UK, Material 3, Atlassian and IBM Carbon, kept to what all of them agree on. `interfaces:better-writing` holds the rest; route there and keep this section to the consensus.

## Scope

`scripts/check_copy.py` reads:

- Markup: `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`
- Message catalogs: `.json` and `.ts` files under a directory named `locales`, `locale`, `i18n`, `messages` or `lang`

Excluded: `node_modules/`, `dist/`, `build/`, `.next/`, `.git/`, `.svelte-kit/`, `coverage/`, `*.test.*`, `*.spec.*`, `*.min.*`, and any path segment named `legal`, `terms`, `privacy` or `policy` — see the carve-out below.

### Every string is classified before any rule runs

A rule that fits a button ruins a paragraph. Each string is sorted into one of eight kinds first, and only the checks belonging to that kind run against it.

| Kind | Recognised by |
|---|---|
| `button` | `<button>`, `<Button>`, `<AlertDialogAction>`, `<AlertDialogCancel>`, `<MenuItem>`, `<DropdownMenuItem>`, `role="button"`, a catalog key segment `button` / `btn` / `action` / `cta` |
| `label` | `<label>`, `<Label>`, `<FormLabel>`, `aria-label=`, `alt=`, a key segment `label` / `field` |
| `heading` | `<h1>`–`<h6>`, `<CardTitle>`, `<DialogTitle>`, `<AlertDialogTitle>`, `<SheetTitle>`, `<DrawerTitle>`, a key segment `title` / `heading` |
| `link` | `<a>`, `<Link>`, `<NavLink>`, a key segment `link` |
| `error` | `<FormMessage>`, `<AlertTitle>`, `role="alert"`, a key segment `error` / `err` / `invalid` / `failed` |
| `tooltip` | `title=` on an element, `<TooltipContent>`, a key segment `tooltip` / `hint` |
| `placeholder` | `placeholder=`, a key segment `placeholder` |
| `prose` | everything else — descriptions, help text, empty-state bodies, notification mail |

A catalog key is split on `.`, `_`, `-` and `/`, and the first segment equal to one of the words above decides the kind; where no segment is equal to one, a key containing one of the words decides it. Both passes try the words in this order: `error`, `err`, `invalid`, `failed`, `button`, `btn`, `action`, `cta`, `label`, `field`, `title`, `heading`, `tooltip`, `hint`, `placeholder`, `link`.

`prose` runs C1, C2, C9, C10, C12 and C15's `click here` / `lorem ipsum` pattern. Its remaining checks belong to textlint; `--emit-prose` writes those strings out for it.

## The carve-out

Do not rewrite, and do not report against, four kinds of string:

- Legal, regulated and consent copy — 利用規約, プライバシーポリシー, 特定商取引法に基づく表記, 金融商品の説明
- A verbatim quotation or a phrase a statute fixes
- An established product term, even a clumsy one, and a proper noun
- A term the business defines, where a translation would hide which word the specification names

Flag a concern about one of these and leave the decision to the user. An automated copy pass that edits a consent screen causes a larger problem than the one it fixes.

## Japanese rules

### Button labels

A button names the operation it performs, so its label is the verb in its plain form (終止形). A サ変 verb — a noun carrying 「する」 — keeps the noun alone: that is the shortest name the operation has, and it leaves the 「する」 form free to mark a destructive action.

| | |
|---|---|
| Write | 「保存」「アップロード」「閉じる」 |
| Replace | 「保存する」「アップロードします」「アップロードを行う」 |

The one exception is a destructive action, where the fuller 「削除する」 makes the weight of the operation visible. `check_copy.py` recognises it from an attribute on the element, or a catalog key, containing `destructive`, `danger`, `delete`, `destroy` or `remove` — `variant="destructive"` and `className="danger"` are the usual forms.

A confirmation dialog repeats the verb of the action that opened it: 「削除」 opens a dialog whose primary action is 「削除する」. Its heading names the object that disappears — 「report.pdf を削除しますか？」 — so the reader confirms the right file. When the deletion is permanent, one sentence says so: 「削除したファイルは復元できません」.

### Form labels

A label is the name of the item. The instruction, where one is needed, goes into help text.

| | |
|---|---|
| Write | 「表示名」「ファイル名」 |
| Replace | 「表示名を入力してください」「ファイル名をご入力ください」 |

Help text names the format or the limit: 「PNGまたはJPEG、10MBまで」. Whether help text appears at all belongs to `references/ban-list.md`.

### Notes, captions and legends

A note that survives `references/ban-list.md` says what the figure is, in the surface's register, and stops. 「購入まで進んだセッションを、全セッション数で割った値です」 is a tooltip's sentence. A note that says what the figure is not, what was not done, or what the reader should not conclude — 「セッション数ではない」「季節変動は補正していない」「ボットのアクセスは除いていない」 — is the author's notebook, and ban-list.md's ST9 reports the ones carrying a method word. A data-fact note under a chart states the fact in the positive: 「集計対象は支払いが完了した注文だけです」. The one negation that ships is a statute's own wording, under the carve-out.

### Error messages

An error message tells the reader what happened, why, and what to do next. When the space holds a single sentence, keep the one that says what to do: the reader can act on it alone.

| | |
|---|---|
| Replace | 「エラーが発生しました」「アップロードに失敗しました」「不正なファイル形式です」 |
| Write | 「ファイルが10MBを超えているため、アップロードできませんでした。10MB以下のファイルを選んでください」 |
| Replace | 「10MBを超えるファイルは使えません。」 |
| Write | 「10MB以下のファイルを選んでください。」 |

The error states what the product accepts. 「間違っています」「失敗しました」 put the fault on the reader and leave the fix unsaid.

### Register and 敬語

敬体 (です・ます) by default. The project records its choice in `voice.register`, and one surface keeps one register.

「〜してください」 is the polite request this file recommends. C2 reports the polite form stacked past what the sentence needs.

| | |
|---|---|
| Write | 「ファイル名を確認してください。」「設定を保存しました。」 |
| Replace | 「ファイル名をご確認いただけますようお願いいたします。」「設定を保存させていただきました。」 |

### Words and characters

- Use the short verb form: 「◯◯できます」 for 「◯◯することができます」, and 「アップロードする」 or 「アップロードしてください」 for 「アップロードを行う」「アップロードを実行する」 (C1)
- Keep the case particles: 「通知設定を保存します」 carries its 「を」. A phrase stripped of its particles reads as a compound noun
- Before writing a katakana loanword, check whether a word the reader already knows says the same thing, as 公用文作成の考え方 asks of public-sector text. A reader who does not know the loanword has nothing on the screen to work it out from
- Write kanji with the readings in the 常用漢字表: 「分かる」 for 「解る」
- Join half-width and full-width characters with no space: 「ZIP形式」 (JTF日本語標準スタイルガイド)
- Write katakana in full width

A heading, a label and a button name something, so they end without 「。」 (C8). A sentence ends with 「。」 wherever it appears, a one-sentence tooltip included. 「！」 is kept for a toast that reports success (C11).

### The operation vocabulary

One word per operation, across the whole product. Step 1 settles the words in `voice.terms`: each key is a word the product stops using, and its value is the word the product uses. Settle one entry for every operation the screens offer where two words compete for it, reading the words already on the existing screens first.

The keys are what C10 reports. A project where 「サインイン」 is the word the business itself uses leaves it out of `voice.terms`, and the check then stays silent about it.

## English rules

Kept to what Polaris, GOV.UK, Material 3, Atlassian and Carbon all state. For anything past this, route to `interfaces:better-writing`.

- Sentence case for buttons, headings, labels and menu items — `Upload file`
- A button label is a verb, or a verb and a noun, in three words or fewer
- No `click here`, no bare `here`, and no bare `Learn more`: a link names what it opens
- No full stop at the end of a heading, label, button or single-sentence tooltip. A question mark is allowed
- An error says what happened and what to do next, in words that leave the reader blameless — `File must be 10 MB or smaller`
- No `oops`, `uh-oh`, `sorry` or humour in an error, and no `invalid`, `illegal` or `forbidden`
- A confirmation dialog repeats the verb on its primary button — `Delete file` — and its heading names what the action affects. C13 reports an `OK` button; C15 reports `Yes` and an `Are you sure?` heading
- No `e.g.`, `i.e.` or `etc.` — they do not survive translation
- Second person throughout; never mix `you`/`your` with `me`/`my` on one screen

Three sources dissent on points this list settles:

- **Apple** does not mandate sentence case. It says pick a case convention and hold to it. Do not cite Apple for sentence case
- **Mailchimp** uses title case for global navigation and for titles. This skill overrules it
- **GOV.UK** bans negative contractions (`don't`, `can't`) where Polaris, Atlassian and Carbon all want contractions. Settle it per product in `voice.case`'s neighbourhood and do not script it

## Checks

An error means the string contradicts something the project settled or carries no information. A warning means it departs from what this skill recommends and a reason may exist.

### C1 — 冗長表現 (error)

**Check.** `することができ(る|ます|ません)`, `を行(う|い|います|った|って)`, `を実行(する|します)`.

**Applies to.** Every kind.

**Why.** Each wraps the verb in words that add no information. They are the most common trace of Japanese written without editing.

### C2 — 過剰敬語 (error)

**Check.** `ご[぀-ヿ一-鿿]{1,8}いただけますよう`, `させていただ`, `お[぀-ヿ一-鿿]{1,8}になられ`, `ご[一-鿿]{1,8}してください`. The last pattern takes kanji alone between ご and してください, so 「ご確認してください」 is caught and 「ご自身で設定してください」 passes.

**Applies to.** Every kind.

**Allowed.** Anything under the carve-out — consent and legal surfaces keep the register they were drafted in.

**Why.** Stacked 敬語 lengthens the sentence and adds no information. 「ご〜してください」 applies a humble form to the reader's own action, which 文化審議会「敬語の指針」 treats as a misuse.

### C3 — ボタンが丁寧形 (error)

**Check.** A `button` string ending `ます` or `ました`.

**Why.** A button names the operation the user performs, so it takes the verb's plain form. 「アップロードします」 reads as a sentence the screen says to the user.

### C4 — サ変ボタンの「する」 (warning)

**Check.** A `button` string matching `^[一-鿿]{2,4}する$`. Two or more kanji before 「する」 is enough on its own — 「関する」「対する」 carry one kanji and do not match, and a button label of that shape is a サ変 verb in practice.

**Allowed.** An element marked destructive — an attribute on it, or its catalog key, containing `destructive`, `danger`, `delete`, `destroy` or `remove`. There the fuller form is correct.

**Why.** The noun alone is the shortest name of the operation, and keeping 「する」 for destructive actions gives that form a meaning of its own.

**On the threshold.** This check depends on recognising the destructive marking, and a project that signals danger some other way sees it misfire. The fix is to add the marking to the element, which also tells assistive technology and the next reader that the action destroys data.

### C5 — 「こちら」 (error / warning)

**Check.** Link text that is exactly `こちら`, `詳しくはこちら`, `こちらから`, `こちらをご覧ください` or `こちらをクリック` — error. `こちら` inside a longer sentence — warning.

**Why.** Link text tells the reader what the destination holds. A screen reader reaches a link out of context, and there 「こちら」 names nothing.

### C6 — プログラム目線のエラー (error)

**Check.** In an `error` string: `エラーが発生しました`, `に失敗しました`, `不正な`, `無効な`. Also `できませんでした` where the same string carries none of `てください` or `でください`, `お試し`, `確認`, `もう一度`, `やり直` — the phrase is fine once the fix follows it.

**Allowed.** A path segment named `admin`, `debug`, `audit` or `devtools`, where precision beats readability.

### C7 — ラベルが文になっている (error)

**Check.** A `label` string ending `してください`, `を入力`, `を選択`, `をご入力` or `をご選択`; `を入力してください` ends in `してください` and is caught with it.

**Why.** A label names the item. The instruction belongs in help text, or nowhere.

### C8 — ラベル末尾の句読点 (error)

**Check.** A `button`, `label` or `heading` string ending `。` or `、`.

**Allowed.** `tooltip` and `prose`. A string ending `？` or `?`.

**On the threshold.** Punctuation in a heading is unambiguous, but a heading misclassified as such by an unusual component name will misfire. The fix belongs in the classification table above; the check stays as written.

### C9 — 長音符の不統一 (error)

**Check.** Project-wide. For each of the 12 pairs in `assets/voice_terms.ja.json` (ユーザ/ユーザー, サーバ/サーバー, ブラウザ/ブラウザー and the rest), both forms appearing anywhere in the scanned files. Every kind is read, `prose` included.

**Why.** The three Japanese authorities give three different conventions, so no single form is correct. Inconsistency inside one product is the defect. The message names the form `voice.katakana_choon` implies.

### C10 — 用語辞書違反 (error)

**Check.** Any key of `voice.terms` appearing in a string. The message carries that key's value as the replacement. When no `tokens.json` is found, C10 is skipped and reported once as a warning saying so.

**Applies to.** Every kind.

**Allowed.** A term listed in `voice.allow`. A project where 「消去」 names an operation distinct from 「削除」 puts it there, or removes the row from `voice.terms`.

**Why.** This is the copy equivalent of S1. The project settled the word; the check asks whether the implementation used it.

### C11 — 「！」の乱用 (warning)

**Check.** `!` or `！` in any string other than `prose`, outside a key containing `success` or `toast`.

**Allowed.** A path segment named `marketing`, `landing` or `lp`.

**Why.** 「！」 raises the pitch of a sentence. A toast reporting success carries that tone; in an error or an ordinary label it reads as alarm.

### C12 — 敬体と常体の混在 (warning)

**Check.** Per file, across the strings carrying Japanese. Both a 敬体 ending (`です` / `ます` / `ました` / `ません` / `でした` before `。` or `！`) and a 常体 ending (`である` / `であった` / `だった`, or `だ` where the preceding character is not part of a 敬体 form) present.

**Allowed.** Strings ending in a noun, such as labels and log entries, match neither form, so a file holding only those passes.

### C13 — 汎用ボタンラベル (warning)

**Check.** A `button` string that is exactly `OK` (or `Ok`, or the full-width `ＯＫ`), `確認`, `送信`, `実行`, `はい`, `いいえ`, `進む` or `完了`.

**Allowed.** Anything in `voice.allow`. `キャンセル`, `閉じる`, `戻る`, `次へ`, `保存` are not reported — they name their action already.

**On the threshold.** 「確認」 and 「完了」 are legitimate as step names in a wizard, so this check is a warning; a wizard keeps them with `ignore C13` and the reason.

### C14 — 文字数超過 (warning)

**Check.** Counted in 全角 characters, a wide character counting 1 and a narrow one 0.5: a `button` past 8, a `label` past 12, a `tooltip` past 80.

**Why.** These figures are a starting point with no design system behind them, so they are warnings. A domain noun such as 「適格請求書発行事業者登録番号」 exceeds them legitimately.

### C15 — 英語の空文言 (error)

**Check.** `button`, `link` or `heading` text that is exactly `here`, `read this`, `submit`, `confirm`, `yes`, `no` or `learn more` after case and trailing punctuation are stripped, or that begins `Are you sure`. `click here` and `lorem ipsum` are reported wherever they appear, including in prose.

**Allowed.** `Save`, `Cancel`, `Close`, `Back`, `Next`, `Skip`, `Done` — each names a complete action with no object.

### C16 — 英語のエラー禁止語 (error)

**Check.** In an `error` string: `oops`, `uh-oh`, `whoops`, `sorry`, `invalid`, `illegal`, `forbidden`, `prohibited`, `you forgot`. Also `something went wrong` where the same string carries none of `try`, `refresh`, `reload`, `retry`, `contact`, `check`.

**Allowed.** A path segment named `admin`, `debug`, `audit` or `devtools`, as for C6.

**Why.** The [GOV.UK Design System](https://design-system.service.gov.uk/components/error-message/) names `forbidden`, `illegal`, `you forgot`, `prohibited`, `sorry`, `invalid` and `oops` among the words an error message avoids; `uh-oh`, `whoops` and a bare `something went wrong` are the same kind of wording. `invalid` in particular tells the reader nothing they can act on.

## Suppressing a misfire

The same two forms as `slop-checklist.md`, read by `check_copy.py`:

| Form | Where | Silences |
|---|---|---|
| `product-ui: ignore C13 <reason>` | the line before the string, or the same line | that ID on that line. For the per-string checks: C1–C8, C10, C11, C13–C16 |
| `product-ui: ignore-file C12 <reason>` | anywhere in a scanned file | that ID for the whole file. For the per-file checks C9 and C12, and for any per-string check the file legitimately repeats |

A form with no reason is reported as **C0 (warning)** and suppresses nothing. Message catalogs (`.json`) carry no comments. For them `voice.allow` does the work for C10 (a listed term) and C13 (a listed label); a catalog string any other check reports is rewritten.

Suppress only a misfire — the check read the string wrong. Where it read the string correctly, rewrite or delete the string; preferring it is no reason to silence the check.

## Rules left to the reviewer

Three rules would fire on correct copy, so a reviewer applies them by hand.

| Rule | Reason |
|---|---|
| Title case in English buttons and headings | Needs a per-project list of proper nouns and acronyms before it can tell `Google Drive` from `Upload New File`. Add it once such a list exists |
| The [GOV.UK words to avoid](https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style#words-to-avoid) (`key`, `deploy`, `drive`, `portal`, `impact`, `land`) | Every one of them carries an ordinary technical sense. The list stays available for public-sector work, applied by hand |
| Gerund headings (`Getting started`) | `Getting started` is common and correct, so a check would fire on correct copy |

A check that fires on good copy teaches its reader to skip the output, which costs more than the check returns.

## Out of reach for this script

Step 5 — the independent review through `review-design-lead` — judges these against the rendered page.

- Whether the button label names what the button actually does. `保存` on a control that publishes passes every check here
- Whether the cause the error states is the real cause, and one the reader can act on
- Whether the heading is specific to this screen. 「概要」「詳細」「設定」「情報」 pass every length and punctuation rule and carry nothing
- Whether the copy is true — 「削除したファイルは復元できません」 on a file the trash can restore, or a dialog understating what it deletes
- Whether one object is called by one name throughout, when the names are not in `voice.terms` yet
- Whether the empty state's action is the right next action for a reader who cannot perform it
- Whether the register the tokens settle (敬体 or 常体) suits this audience — 敬体 on an internal operations screen, 常体 on a public form
