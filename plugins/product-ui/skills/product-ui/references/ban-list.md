# The ban list

This file is the source of record for the generation-time bans and for checks ST1 through ST10. `scripts/check_shippable_text.py` implements the checks written here; change this file first when a check or a threshold changes.

## Why the rules are written as bans

The design premise is that a named ban with a reason changes the next generation, and positive advice leaves it as it was. "Use nice spacing" changes no output. "Inter is banned; it is what gets picked when no choice is made" changes the next generation immediately. So every rule below is a named ban with a one-line reason.

The same argument settles when to read the rules. A ban read before the string is written suppresses it; a ban applied afterwards meets a sentence that already exists and has a defence ready. Generation time is the primary defence, and the checks in Part 2 are the net underneath it.

---

## Part 1 — Generation-time bans

### Helper text is default OFF

Helper text is a device, valid only when it carries what the label cannot: a format, a limit, a consequence, or a legal requirement. 「PNGまたはJPEG、10MBまで」 under a file field ships. 「表示名を入力してください」 under a label reading 「表示名」 is deleted.

**Why.** Helper text under every field trains the reader to skip all of it, including the one line that carried a constraint.

### Captions under charts, tables and cards are default OFF

The title names the data and the data shows itself. A caption ships only when it carries something not derivable from the picture: the source, the unit, the collection period, an exclusion.

**Why.** 「月次の売上推移を示しています」 under a chart titled 月次売上 is the chart's title written twice.

### Legends are default OFF

Valid only where an encoding is genuinely ambiguous — several series in one colour family, a scale whose direction is not obvious. A legend explaining that red means unhandled is explaining a convention the badge already carries.

**Why.** A legend for a self-evident encoding says the reader could not be trusted to read the screen.

### Author's notes never ship

A note that speaks about the method — what was not done, what a number is not, the hypothesis behind a p-value, why a parameter was set the way it was — is the author's working note, and it stays in the author's notebook. 「季節変動は補正していない」「しきい値はこの期間に合わせて選んでいない」「この値は訪問者数ではなく、セッション数に対する割合」 each answer an accusation nobody on the screen has made.

**Why.** A reader who did not suspect the number now does, and a reader who did is not reassured by a denial. Microsoft's rule for interface text is "Emphasize what users can accomplish—not what they can't" ([Office Add-ins writing guidelines](https://learn.microsoft.com/office/dev/add-ins/design/voice-guidelines)); Material's is "Present information in a positive light: it's reassuring" ([Material Design, Writing](https://m1.material.io/style/writing.html)); the same point about prose appears in Kiterlin's [anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing), which lists "Explaining what the paper does **not** do instead of what it **does**" as the mark of defensive writing. A product states what a figure is, once, where the reader who wants it will look, and leaves the method to a help page.

#### Where a real product puts each kind of explanation

Analytics and experimentation products agree on where each kind of explanation goes:

| The explanation is… | Where it goes | Never | Seen in |
|---|---|---|---|
| The definition of a metric — what the number is | An info icon beside the label, opening a tooltip of one sentence in the present tense | A `<dl>` of definitions under the chart | Power BI: [Help tooltips](https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-help-tooltips) "appear when a consumer selects the **Help tooltip** icon in the visual header" ([Tooltips overview](https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-tooltips-overview)) |
| The state of the data — sampled, thresholded, estimated, awaiting more data | A status indicator, icon or badge, with a fixed noun-phrase label and a link for the mechanism | A sentence narrating what the pipeline did or did not do | GA4: the [data quality indicator](https://support.google.com/analytics/answer/12856703) at the top of a report, with the status "Thresholding applied"; Optimizely: the [Results page](https://support.optimizely.com/hc/en-us/articles/4410284017421-Optimizely-Experiment-Results-page) "displays that more visitors are needed" |
| Statistical uncertainty | The interval drawn on the chart, or a status — winning, losing, inconclusive | Prose about the hypothesis, the p-value or the false-positive rate | Optimizely: on the [Results page](https://support.optimizely.com/hc/en-us/articles/4410284017421-Optimizely-Experiment-Results-page), "statistical significance" is a link to the help centre |
| How the method works | A help-centre page reached by 「詳しく見る」 or a link naming the page, such as "How significance is calculated" (C15 reports a bare "Learn more") | Inline | Optimizely and GA4 link out |
| A fact about the data — the source, the period, an exclusion, a break in the series, an axis that does not start at zero | One line under the chart, stated as a fact: 「出典：アクセス解析ログ、2026年1月〜8月」 | A paragraph; a note attached to the title | [Datawrapper Academy](https://www.datawrapper.de/academy/annotate-tab): notes "clarify any abnormalities about your data" and "appear below the chart"; [Eurostat](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Tutorial:Guidelines_for_notes_and_footnotes): notes are "restricted to the maximum extent", and "Footnotes should not be attached to the chart or table title" |
| A legal disclaimer | Fixed wording, in the footer or directly under each result card | The author's own paraphrase | Any product whose statute or regulator fixes the wording, quoted verbatim |

Two consequences for the build. The legal row is the only one where a negation ships, and there it is the statute's wording, under `ui-copy.md`'s carve-out. The definition row is a tooltip, so a chart needing three definitions gets three info icons — a legend block of definitions is the sign that this placement was skipped.

Sources are linked in the table and the paragraph above.

### The UI never describes itself

「この画面では各種指標を確認できます」 / "This dashboard lets you review your metrics." Banned outright. Screens are for using.

**Why.** The sentence exists only because the generator needed something to put in the space under the heading. A real product has data there.

### Copy never describes the layout

No 下の / 上記の / 以下のフォーム / below / above pointing at another element. "Enter your email below" — if the input is below, you don't need to say so.

**Why.** It is false on the next viewport width, and it survives no reordering, no responsive collapse, and no screen reader.

### Tutorial prose never ships inline

Onboarding lives in a dismissible surface — a tour, a first-run panel, a help page — or nowhere. 「まず名前を入力してください。次に…」 baked into the layout is documentation someone pasted into a screen.

**Why.** Inline instructions are permanent, and they are read by every user on every visit after the first, when they are already noise.

### No text below the minimum size

| Text | Standard | Minimum |
|---|---|---|
| Running text and UI text — labels, table cells, buttons, helper lines, captions that survived the bans above | 16px | 14px |
| A Latin-only run of at most 24 visible characters — a unit, a timestamp, a code, a badge | — | 12px |

Nothing is set below the minimum, in any unit, in any stylesheet, at any breakpoint other than print. A string that only fits at 11px is a string the screen has no room for, and the honest move is to delete it. `typography.scale.base_px` in `tokens.json` is 16 to 18.

**Why.** The Digital Agency Design System's Tailwind plugin starts its standard text utilities (`text-std-*`) at 16px, and its smallest utility of any group is 14px; Yahoo! JAPAN measured 16–19px as the readable range for Japanese and saw early abandonment fall by up to 23% at 17px. 漢字 lose their strokes at sizes where Latin letters still read, so the Latin allowance does not extend to a run holding a single CJK character. Sources: `@digital-go-jp/tailwind-theme-plugin` 1.0.1, `dist/v4.css` (MIT); techblog.yahoo.co.jp/entry/2023052430423559/.

### Let each element do exactly one job

A label labels, an example demonstrates, a placeholder shows a shape, an error says what to do. Nothing quietly does double duty — a placeholder standing in for the label, a label carrying the instruction, a heading carrying the summary.

**Why.** Doubled duty is how one slot ends up carrying two strings that say the same thing.

### Never invent prose to fill a slot

When the brief gives no real content for a slot, leave a labelled blank in a comment and ask the user exactly one question. Filler survives into the build, gets read as intent, and is defended in review.

**Why.** Every explanatory caption in a generated screen started as a slot nobody had content for.

---

## Part 2 — Checks

An **error** means a pattern settles it mechanically: the string is describing the interface, describing the layout, or is filler. A **warning** means a tendency, which is all the evidence supports. Only errors stop the pipeline.

### Scope

Files matching `.html`, `.htm`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`; `.css` and `.scss` for ST10 only, read as plain CSS.

Excluded: `node_modules/`, `dist/`, `build/`, `.next/`, `out/`, `.svelte-kit/`, `.git/`, `coverage/`, `fixtures/`, `*.min.*`, `*.test.*`, `*.spec.*`. Inside a file, the contents of `<script>`, `<style>`, `<code>`, `<pre>`, `<noscript>`, `<title>` and every comment are out of scope, and so is a JSX expression that is only `{…}`. ST7 also skips the contents of a `<template>`, which a browser leaves unrendered, everywhere except in a `.vue` file, where every `<template>` is markup. `<title>`, `<noscript>` and `<template>` are matched in lower case only, so a JSX component such as `<Title>` is read as markup; `<script>`, `<style>`, `<code>` and `<pre>` are matched in any case. A `//` opens a comment only where nothing precedes it that makes it part of a value — a scheme, a word character, a quote or an `=` — so `href="//cdn.example.com"` survives with the rest of its line.

Two kinds of string are read: text between tags, and the value of a text-carrying attribute or prop — `label`, `placeholder`, `description`, `helperText`, `helpText`, `hint`, `title`, `aria-label`, `alt`, `caption`, `subtitle`, `legend`, `tooltip`.

### The surface

ST3 asks whether the file sits on a promotional surface. The answer comes from `meta.surface` in the nearest `tokens.json`, looked for in the scanned directory (a scanned file's own directory) and then up to three directories above it; `lp` means a landing page, and anything else means an application (`validate_tokens.py` accepts only `saas` and `lp`); the auditor agent takes the same distinction as `landing` or `application`. `--surface lp|app` on the command line beats the file. Where neither is available the path decides, which is the weakest of the three: a segment named `marketing`, `landing` or `lp`, or a file name containing `landing` or `hero`.

### ST1 — the screen describing itself (error)

**Check.** In any visible string: `(この|本)(画面|ページ|ダッシュボード|タブ|セクション|アプリ|サービス|機能)(では|から|で|には)`, a string opening with `ここでは`, and `(This|The) (page|screen|dashboard|view|section|tab|app) (lets|allows|enables|shows|displays|helps)`.

**Allowed.** Nothing. A screen has no legitimate reason to introduce itself to the person already on it.

**Why.** This is the single most recognisable mark of a generated screen, and it is the one case where the pattern and the defect coincide exactly.

### ST2 — an instruction that points at the layout (error)

**Check.** A Japanese positional phrase — `(下記|上記|以下|左記|右記|下|上|右|左)の(フォーム|入力欄|ボタン|欄|メニュー|タブ|カード|リンク|チェックボックス|プルダウン)` — in a string that also carries an instruction (`ください`, `入力`, `選択`, `押`, `クリック`, `タップ`, `参照`, `ご覧`). In English, an instruction verb followed by a UI noun and then `below` or `above`, or the bare form `the <noun> below/above`.

**Allowed.** The positional word without a UI noun. 「以下の条件」「上記の合計金額」 point at content and pass. The nouns that name content as readily as chrome are out of the list as well — 項目, 一覧, 表, リスト — so 「以下の項目をご確認のうえ、送信してください」 and 「下記の一覧に誤りがあれば修正してください」 both pass. Those are what a confirmation screen says, and it says it about the data on the screen. Only the unambiguous chrome nouns remain.

**Why.** Requiring both the position and the UI noun is what keeps this off ordinary content pages, where 「以下の」 opens a perfectly good list.

### ST3 — the capability explainer (warning)

**Check.** A short single-sentence string (80 characters or fewer after collapsing whitespace, carrying at most one 。 and at most one full stop) ending `できます`, `出来ます`, `が表示されます` or `をご覧いただけます` — with the trailing 。 optional in each — or opening `You can`, `You'll be able to` or `You are able to`.

**Allowed.** Empty-state text — recognised by `empty`, `EmptyState`, `no-data`, `nodata`, `空`, `ありません`, `ございません` or `0件` within 200 characters of the string — which legitimately says what becomes possible. Hero copy on a landing-page surface, as the surface is settled above. A `title` or `tooltip` attribute or prop, where stating what a control does is the whole job of the string: 「Ctrl+S でも保存できます」 passes. A string that already raised ST1 is not reported twice.

**Why.** The length bound is what separates a caption from a paragraph. A body paragraph on a documentation page ends in 「できます」 constantly and falls outside the length bound; a 20-character grey line under a card is this skill's business. This is a warning because the allowance list cannot be completed mechanically — a confirmation dialog and a line of reassurance microcopy both end in 「できます」 with every right to — and only mechanical certainty stops the pipeline. 

### ST4 — helper text restating its label (warning)

**Check.** Helper text — a `helperText`, `helpText`, `hint`, `description`, `caption` or `subtitle` value, or an element whose class contains `help`, `hint`, `description`, `caption`, `form-text` or `field-note` — whose character-bigram overlap with the nearest label reaches 0.6. Nearest means nearest in either direction within 600 characters, because a section description sitting above its label is as real a case as helper text sitting below one.

**Allowed.** Helper text carrying a constraint token: a digit, `半角`, `全角`, `文字`, `以内`, `以上`, `以下`, `必須`, `任意`, `形式`, `拡張子`, `桁`, `バイト`, `@`, or the English `format`, `max`, `min`, `maximum`, `minimum`, `required`, `optional`, `characters`, `digits`, `must`, `at least`, `up to`, `MB`, `KB`.

**On the threshold.** Bigram overlap is the trigger, and a constraint token exempts the string. The absence of a constraint token is too weak a signal on its own: a legitimate consequence line ("保存すると担当者に通知が届きます") carries none and is exactly what helper text is for. Overlap alone is the mechanical part; the rest belongs to the auditor, which can see that 「登録に使うアドレス」 restates 「メールアドレス」 without sharing a character with it.

### ST5 — a legend for the self-evident (warning)

**Check.** `(色|アイコン|マーク|バッジ|印|ラベル)` followed within 20 characters by `示します`, `表します` or `意味します`; and in English a colour word followed within 30 characters by `means`, `indicates`, `shows` or `denotes`. A leading `※` or `注:` is common but not required.

**Allowed.** Nothing mechanical. A genuinely ambiguous encoding needs its legend, so this is a warning and the reason for keeping one gets stated.

**Why.** A sentence explaining what a colour means is a sentence saying the colour did not mean it.

### ST6 — inline tutorial prose (warning)

**Check.** Per file. The visible text carries `まず`, `最初に` or `はじめに` together with `してください` or `して下さい`, and also carries `次に`, `その後`, `続いて` or `最後に`. In English, `First,` together with `Then`.

**Allowed.** A file carrying a recognisable wizard or stepper. The signals are markup only — `stepper`, `wizard`, `role="tablist"`, `aria-current="step"`, an `<ol>`, a `<Step>` or `<Steps>` component, or `steps` as a whole quoted value. There the steps are the interface. The signals are read from markup alone, because onboarding prose is where the word "steps" appears in visible text, and counting it would switch the check off on the files it exists for.

**Why.** File-level, because the defect is a sequence of instructions spread across the layout, which no single string reveals.

### ST7 — text below the minimum size (error)

**Check.** Resolve the size every visible run actually gets, then report any run under 14px, unless the run holds no CJK character, is at most 24 visible characters, and is at least 12px.

Resolution follows the cascade as far as a stylesheet can be read without a browser. Stylesheets are every `<style>` block in the file, every `<link rel="stylesheet" href>` that resolves to a local file, the nearest `theme.css` or `tokens.css` (beneath the scanned path, then up to four directories above), and any `.css` named on the command line. A `@media` block whose only media type is `print` is skipped; every other `@media` block is read as if unconditional, because a size that appears only under a width query is still a size a reader gets. Supported selectors are a type, `.class`, `#id`, compounds of those, and descendant chains matched against the element's ancestors. The markup is walked with a stack of computed sizes. Precedence, highest first: an inline `style` (or a JSX `style={{fontSize}}`) marked `!important`; a matching stylesheet rule marked `!important`; the inline `style`; an SVG `font-size` attribute; a Tailwind size class (the last one in source order when several are present; variant prefixes such as `md:` are not read); the matching stylesheet rules by the higher specificity counted as (ids, classes, types), then the later one in source order; inheritance. The root is 16px unless an `html` or `:root` rule (alone or in a grouped selector such as `html, body`) declares a px size, which `rem` then uses. Units: `px`; `rem`; `em` and `%` against the parent; `pt` at 4/3; the keywords `xx-small` 9, `x-small` 10, `small` 13, `medium` 16, `large` 18, `x-large` 24, `xx-large` 32, `smaller` ×0.83, `larger` ×1.2; `var(--x)` when `--x` is declared literally on `:root`, on `html` or in `@theme`; `clamp()`, `min()` and `max()` as the smallest px literal inside. Tailwind classes resolve as `text-xs` 12, `text-sm` 14, `text-base` 16, `text-lg` 18, `text-xl` 20, `text-2xl` 24, `text-3xl` 30, `text-4xl` 36, `text-5xl` 48, `text-6xl` 60, `text-7xl` 72, `text-8xl` 96, `text-9xl` 128 and `text-[N(px|rem|pt)]`, with a `--text-*` declaration in the found theme overriding the default. An SVG `<text font-size="N">` counts. A `var()` whose property is undeclared resolves to its fallback when it carries one. A run whose nearest declared size is an undeclared `var()` with no fallback, a `clamp()` with no px literal, or a rule in a stylesheet that could not be opened inherits its parent's size and is not reported as unresolved. What counts as text is settled in the Scope section above.

The finding names the resolved size and where it came from — `inline`, the selector, the Tailwind class, or `inherited from <tag.class>` — so the fix lands on the declaration itself.

With `--dom <dump.json>`, the same rule runs over the computed `fontSize` of every entry in a `cdp.js` dump's `text` array, and the source is reported as `rendered`. That mode sees what the stylesheet reader cannot: a size set from JavaScript, a `transform: scale()`, a `zoom`.

**Allowed.** Only the Latin-short case in the check itself. A dense table does not defend 13px Japanese; it gets 14px and fewer columns.

**Why.** Resolving the cascade is what makes the ban above enforceable: a `.note { font-size: 11px }` rule in a stylesheet is where most small text is born, and a check that reads only the element never sees it. The Latin-short allowance is the one case where 12px reads, and it is bounded by length so it cannot become a caption. ST10 follows ST7 directly because the two size checks are read together.

### ST10 — a size below the minimum declared in a stylesheet (error and warning)

**Check.** In a `.css` or `.scss` file or a `<style>` block, outside `@media print`, a `font-size` declaration that resolves to a literal under 12px is an error; 12px to under 14px is a warning naming the Latin-short allowance. `rem` resolves against 16px, `pt` at 4/3, and the absolute keywords as ST7 lists them; `smaller` and `larger`, a `var()`, a percentage, an `em` and a `clamp()` with no px literal need a parent and are not judged here — ST7 judges them where they land. A file that raises the root (`html { font-size: 18px }`) can draw a warning here that ST7 clears; the ST7 result settles it, and one declaration is reported once, at its own line.

**Allowed.** Nothing mechanical for the error. A warning is kept only when every element the rule reaches is a Latin-short run, and the hand-over says so.

**Why.** ST7 catches the size where text is; this catches it where it is written, so a stylesheet written before any markup exists — or a rule nothing uses yet — is reported at the moment of writing, which is where the PostToolUse hook runs. A declaration under 12px has no legitimate reader on any screen, so the error needs no allowance.

### ST8 — placeholder filler (error)

**Check.** In any visible string: `説明テキスト`, `ダミーテキスト`, `サンプルテキスト`, `テキストが入ります`, `ここにテキスト`, `lorem ipsum`, `Description goes here`, `Placeholder text`, and a string opening `TODO:` or `TODO：`.

**Allowed.** Nothing. A `placeholder` attribute holding a real example (`yamada@example.com`) passes.

**Why.** Filler reaches production because it looks deliberate in a screenshot. `lorem ipsum` is also reported by C15 (`references/ui-copy.md`); each script runs on its own, so both report it.

### ST9 — a note defending the method (warning)

**Check.** In any visible string, method vocabulary together with a negation. Japanese method vocabulary: `検定|仮説|p値|有意|偽陽性|信頼区間|記述統計|標準誤差|パラメータ|パラメーター|補正|調整|推定|集計|標本|サンプル|ベンチマーク|閾値|しきい値|最適化|統計`; Japanese negation: `[てで]いない|[てで]いません|[てで]いなかった|ではない|ではなく|ではありません|しない|しません|せず`. English method vocabulary: `test|tested|hypothesis|p-value|significan\w*|false positive|confidence interval|parameter|tuned|fitted|adjusted|optimi[sz]ed|sample|benchmark|model|statistic`, each noun except `hypothesis` also in the plural; English negation: `not|never|without|n't|un(tested|adjusted|tuned|fitted)`, and `no` only directly before `significance`, `test`, `adjustment`, `correction` or `hypothesis`. Also, with no negation at all, a string longer than ten visible characters carrying test vocabulary — `検定|仮説|p値|偽陽性|信頼区間|記述統計|有意水準|帰無`, or `hypothesis|p-value|false positive|confidence interval|null hypothesis|descriptive statistic` — because 「p値」 is a column heading and 「AとBの差がゼロという仮説のもとでのp値」 is the author explaining it.

**Allowed.** Empty-state text, recognised as ST3 recognises it. Nothing else mechanically: a data-fact note can carry a negation legitimately (an exclusion), so this is a warning, and a kept note is restated in the positive where one exists — 「集計対象は支払いが完了した注文だけです」 for 「未払いの注文は集計していない」 — with the reason in the hand-over.

**Why.** The combination is what makes the check precise. Negation alone is everywhere in good copy (「削除したファイルは復元できません」), and method words alone are column headings. Together, in a caption, they are the author telling the reader what was not done.

---

## Out of reach for this script

A size set from JavaScript, a `transform: scale()` or a `zoom` on an ancestor, and a rule behind a selector the resolver does not read (`:nth-child`, `:not()`, attribute selectors, and the `>`, `+` and `~` combinators, which are skipped outright) are not seen by ST7 in source mode. ST10 still reports such a declaration at its own line when it is under the minimum; the element it lands on is seen only by ST7's `--dom` mode, which `review-design-lead`'s `check_render.py` R7 also covers at review time.

The `shippable-text-auditor` agent judges these on the built screen. Every one of them needs a reader who can tell what a sentence means, which no pattern can.

- A self-describing screen phrased in a way the ST1 patterns do not carry. 「各種指標をまとめてご覧いただける場所です」 says the same thing and matches nothing.
- A label describing the feature where the action should be named — 「ユーザー管理機能」 on the control that opens the user list.
- Helper text that restates its label in meaning through different words, which ST4's bigram overlap cannot see.
- A caption stating what is already visible on the chart, the table or the card above it.
- Whether a legend's encoding is genuinely ambiguous, which is the only question that decides ST5.
- Whether an empty state's sentence names a next action or merely reports the emptiness.
- A definitions legend under a chart written without a negation. 「購入まで進んだセッションの、全セッションに対する割合」 is a tooltip's sentence sitting in a `<dl>`, and only a reader can tell it from a data-fact note.
