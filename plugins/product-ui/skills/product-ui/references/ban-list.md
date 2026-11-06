# The ban list

This file is the source of record for the generation-time bans and for checks ST1 through ST10. `scripts/check_shippable_text.py` implements the checks written here; change this file first when a check or a threshold changes.

## Why the rules are written as bans

A named ban with a reason changes the next generation; positive advice leaves it as it was. "A subtitle that describes the screen is banned; production application screens carry none" works where "write good copy" does nothing. Each ban below states what production screens show, counted on the corpus in `research/20261106-real-screens/report.md`; `references/real-screens.md` holds the same record per kind of screen. A ban read before the string is written suppresses it, while a ban applied afterwards meets a sentence that already has a defence ready, so generation time is the primary defence and the checks in Part 2 are the net underneath it.

---

## Part 1: Generation-time bans

### Helper text is default OFF

Helper text is valid only when it carries what the label cannot: a format, a limit, a consequence, or a legal requirement. 「PNGまたはJPEG、10MBまで」 under a file field ships. 「表示名を入力してください」 under a label reading 「表示名」 is deleted.

**Why.** Helper text under every field trains the reader to skip all of it, including the one line that carried a constraint. On production forms, 17 of 27 question groups carry no helper line, and each line that exists states a format, a limit, an example or a consequence. It sits between the label and the control on 5 of 6 forms that have one.

### Captions under charts, tables and cards are default OFF

The title names the data and the data shows itself. A caption ships only when it carries something the picture cannot show: the source, the unit, the collection period, an exclusion.

**Why.** 「月次の売上推移を示しています」 under a chart titled 月次売上 is the chart's title written twice. On production monitoring screens, 9 of 15 show no caption, and each of the 6 that do states a period, a source, a time or a scope.

### Legends are default OFF

Valid only where an encoding is ambiguous: multiple series in one colour family, a scale whose direction is unclear. A legend explaining that red means unhandled explains a convention the badge already carries.

**Why.** A legend for a self-evident encoding says the reader could not be trusted to read the screen. On production monitoring screens, 5 of 8 charted screens carry no legend, and a definition sits behind an info icon or a glossary link beside its label on 8 of 15.

### Author's notes never ship

A note about the method (what was left undone, what a number does not measure, the hypothesis behind a p-value, why a parameter was set as it was) is the author's working note and stays in the author's notebook. 「季節変動は補正していない」「しきい値はこの期間に合わせて選んでいない」「この値は訪問者数ではなく、セッション数に対する割合」 each answer an accusation nobody on the screen has made.

**Why.** A reader who did not suspect the number now does, and a denial reassures nobody who did. Microsoft's rule is "Emphasize what users can accomplish—not what they can't" ([Office Add-ins writing guidelines](https://learn.microsoft.com/office/dev/add-ins/design/voice-guidelines)); [Material Design, Writing](https://m1.material.io/style/writing.html) and Kiterlin's [anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing) say the same. A product states what a figure is, once, where the reader who wants it will look, and leaves the method to a help page.

#### Where a real product puts each kind of explanation

| The explanation is… | Where it goes | Never | Seen in |
|---|---|---|---|
| The definition of a metric: what the number is | An info icon beside the label, opening a tooltip of one sentence in the present tense | A `<dl>` of definitions under the chart | Power BI: [Help tooltips](https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-help-tooltips) "appear when a consumer selects the **Help tooltip** icon in the visual header" ([Tooltips overview](https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-tooltips-overview)) |
| The state of the data: sampled, thresholded, estimated, awaiting more data | A status indicator, icon or badge, with a fixed noun-phrase label and a link for the mechanism | A sentence narrating what the pipeline did or did not do | GA4: the [data quality indicator](https://support.google.com/analytics/answer/12856703) at the top of a report, with the status "Thresholding applied"; Optimizely: the [Results page](https://support.optimizely.com/hc/en-us/articles/4410284017421-Optimizely-Experiment-Results-page) "displays that more visitors are needed" |
| Statistical uncertainty | The interval drawn on the chart, or a status: winning, losing, inconclusive | Prose about the hypothesis, the p-value or the false-positive rate | Optimizely: on the [Results page](https://support.optimizely.com/hc/en-us/articles/4410284017421-Optimizely-Experiment-Results-page), "statistical significance" is a link to the help centre |
| How the method works | A help-centre page reached by a link naming the page, such as 「有意差の計算方法」 or "How significance is calculated" (C15 reports a bare "Learn more"; a bare 「詳しく見る」 fails for the same reason) | Inline | Optimizely and GA4 link out |
| A fact about the data: the source, the period, an exclusion, a break in the series, an axis that does not start at zero | One line under the chart, stated as a fact: 「出典：アクセス解析ログ、2026年1月〜8月」 | A paragraph; a note attached to the title | [Datawrapper Academy](https://www.datawrapper.de/academy/annotate-tab): notes "clarify any abnormalities about your data" and "appear below the chart"; [Eurostat](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Tutorial:Guidelines_for_notes_and_footnotes): notes are "restricted to the maximum extent", and "Footnotes should not be attached to the chart or table title" |
| A legal disclaimer | Fixed wording, in the footer or directly under each result card | The author's own paraphrase | Any product whose statute or regulator fixes the wording, quoted verbatim |

The legal row is the only one where a negation ships, and there it is the statute's wording, under `ui-copy.md`'s carve-out. The definition row is a tooltip, so a chart needing three definitions gets three info icons; a legend block of definitions means this placement was skipped.

### The UI never describes itself

「この画面では各種指標を確認できます」 / "This dashboard lets you review your metrics." Banned outright on a screen a person operates. Screens are for using.

**Why.** The sentence exists only because the generator needed something under the heading. A real product has data there: 0 of 14 work-tool collections and 13 of 15 monitoring screens carry no sentence describing the screen.

**Where production screens say what something does.** The entry page of a public service states the service in one sentence near its top (10 of 25 Japanese public-service screens: 「このサイトでは、…を検索することができます。」), and a card or menu entry on a portal carries one line saying what the entry opens. Both describe a destination the reader has yet to choose. They belong to those kinds of screen (`references/real-screens.md`, Public service) and stay off the others.

### Copy never describes the layout

No 下の / 上記の / 以下のフォーム / below / above pointing at another element. "Enter your email below": if the input is below, saying so adds nothing.

**Why.** It is false on the next viewport width, and it survives no reordering, no responsive collapse, and no screen reader.

### Tutorial prose never ships inline

Onboarding lives in a dismissible surface (a tour, a first-run panel, a help page) or nowhere. 「まず名前を入力してください。次に…」 baked into the layout is documentation pasted into a screen.

**Why.** Inline instructions are permanent: every user reads them on every visit after the first, when they are already noise. Non-Japanese production forms carry none (0 of 7).

**The form filled a few times a year.** Japanese public-service and delivery forms print one instruction line or numbered steps between the title and the fields (4 of 5: Hello Work, 国税庁 invoice site, 気象庁, 日本郵便). A form of that kind, for a reader recorded as occasional or first-time, carries the same single line or step list above its fields; it stays out of every screen operated daily.

### No text below the minimum size

| Text | Standard | Minimum |
|---|---|---|
| Running text and UI text: labels, table cells, buttons, helper lines, captions that survived the bans above | 16px | 14px |
| A Latin-only run of at most 24 visible characters: a unit, a timestamp, a code, a badge | none | 12px |

Nothing is set below the minimum, in any unit, in any stylesheet, at any breakpoint other than print. A string that only fits at 11px is a string the screen has no room for; delete it. `typography.scale.base_px` in `tokens.json` is 16 to 18.

This minimum is this skill's own rule. Production screens go below it: 168 of 192 set some visible text under 14px, most often footers, navigation, metadata lines and badges at 12px, and the most common text size on a screen is 14px at the median. `references/real-screens.md` therefore gives two sizes for each role, the one production screens use and the one to build with, and a dense screen builds its rows, cells and labels at 14px.

**Why.** The Digital Agency Design System's Tailwind plugin starts its standard text utilities (`text-std-*`) at 16px, and its smallest utility of any group is 14px; Yahoo! JAPAN measured 16–19px as the readable range for Japanese and saw early abandonment fall by up to 23% at 17px. 漢字 lose their strokes at sizes where Latin letters still read, so the Latin allowance excludes any run holding a CJK character. Sources: `@digital-go-jp/tailwind-theme-plugin` 2.0.0, `dist/v4.css` (MIT); techblog.yahoo.co.jp/entry/2023052430423559/.

### Let each element do exactly one job

A label labels, an example demonstrates, a placeholder shows a shape, an error says what to do. No element does double duty: a placeholder standing in for the label, a label carrying the instruction, a heading carrying the summary. A search field is the measured case of its own: on production screens it carries a placeholder naming what it searches and an accessible name, with no visible label (10 of 10 work-tool collections).

**Why.** Double duty is how one slot ends up carrying two strings that say the same thing.

### Never invent prose to fill a slot

When the brief gives no real content for a slot, leave a labelled blank in a comment and ask the user exactly one question.

**Why.** Filler survives into the build, gets read as intent, and is defended in review; every explanatory caption in a generated screen started as a slot nobody had content for.

### A card around every section is default OFF

A panel, card or bordered box appears where production screens of the kind draw one: `references/real-screens.md` names the enclosed regions of each kind, and the container table is in `references/composition.md`. Everywhere else a section is a heading and distance on the page ground. One panel inside another is ordinary on production screens (15 to 19%); a third level is what they rarely show (1%), and R12 reports it. A `Card` opened directly inside a `Card` is S11 in `check_slop.py`.

**Why.** An enclosure is a strong grouping cue, so every box asserts a relation the reader has to resolve, and a box around every section leaves no box meaning anything. A card around every section shows on 0 of 14 work-tool collections, 1 of 12 forms, 7 of 25 Japanese public-service screens and 6 of 15 monitoring screens. SmartHR's design system treats a rule as 「余白や矩形でグループを表現できない場合の最終手段」 and places no `Base` on a `Base`; Nielsen Norman Group's common-region article adds a border only where whitespace cannot group; GOV.UK's review panel found that "cards are often used to compensate for poor information hierarchy or content design".

### A KPI tile row is default OFF

A row of tiles appears on a `monitor` screen in the composition plan, with a monitored quantity in each tile and its comparison where it has one. An `enter`, `lookup` or `record` screen carries none; a figure it needs goes in the heading or the filter bar. A category, a name or a date is a line in a list, never a tile (R15 at review).

**Why.** Stephen Few: a figure "without any context means little"; a row of four equal tiles on every screen is the layout a generator reaches for when no decision about the screen's job has been made. On production screens a tile row shows on 3 of 15 monitoring screens and on none of the collections, forms and public-service screens counted; a count sits in the title line, the list header or the filter bar on 7 of 7 work-tool collections that show one.

### Equal weight is default OFF

Every screen names one dominant element in its composition plan and gives it the lead in area, position or weight; the page title keeps the largest size, as on production screens, except on a monitoring screen, where the headline figure is the largest text. Text in the main region shows at least three emphasis levels (R14) and the layout uses at least three spacing steps (R13).

**Why.** "If everything is contrasted, then nothing stands out" (Nielsen Norman Group); when every panel weighs the same, the reader has to read the whole screen to find what it is for.

### Proof comes from the brief

A figure, a testimonial, a customer logo or a claim of rank on a screen appears only where the `## Proof` section of `ui-brief.md` lists it with its source. The rest is deleted, and no placeholder stands in for it (C27 in `check_copy.py` owns the check).

**Why.** An invented proof harms the reader whether or not they suspect that a generator wrote the page (research T19, `research/20261030-ai-tells-ui/report.md`).

### A label names the object or the reader's task

A heading, a navigation item or a KPI label names the object it governs or the outcome the reader gets, in the reader's words. A label that names the feature (「ユーザー管理機能」), the computation (「掲載車種内シェアが最大のセグメント」) or the product is rewritten, and so is a heading that is only a generic noun (「概要」「詳細」「情報」「管理」) (C18 to C21 in `check_copy.py`; the reader-fit questions in the brief for the rest). As a tab or a navigation item beside named siblings, `Overview`, `Details`, 「詳細」 and 「その他」 are ordinary on production screens and pass.

**Why.** Two people choose the same word for one thing with probability under 0.20 (Furnas et al., 1987), so a word the generator picked predicts nothing until it is the reader's own; a generic label carries no information scent (Nielsen Norman Group). Microsoft's style guide: "In most cases, don't talk about products, features, or commands in headings."

---

## Part 2: Checks

An **error** means a pattern settles it mechanically: the string describes the interface, describes the layout, or is filler. A **warning** means a tendency, which is all the evidence supports. Only errors stop the pipeline.

### Scope

The script takes one or more paths, each a file or a directory (`check_shippable_text.py src index.html`). It exits 2 when no path holds a file in scope. `tokens.json` and the theme stylesheet are looked up from the first path.

Files matching `.html`, `.htm`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`; `.css` and `.scss` for ST10 only, read as plain CSS.

ST1 to ST6, ST8 and ST9 also read the string literals of `.ts`, `.js` and `.mjs` files and the catalog files (`.json` and `.ts` under `locales`, `locale`, `i18n`, `messages` or `lang`), so guide and FAQ prose kept in data files is judged. `scripts/ts_strings.py` holds the one extraction rule, shared with `check_copy.py`. Each string becomes a segment whose source is the last segment of its key, lower-cased, where that is `label`, `aria-label`, a helper prop (`helpertext`, `helptext`, `hint`, `description`, `caption`, `subtitle`) or a tooltip source (`title`, `tooltip`); any other key gives the string's kind. ST6 runs on the file's strings joined in order. ST7 and ST10 judge rendered and declared sizes, so they skip script and catalog files. A script file with no user-visible string is not counted as scanned. `*.d.ts`, `*.config.*`, `*.min.*`, `*.test.*` and `*.spec.*` are excluded.

The PostToolUse hook (`hooks/ui_text_lint.py`) keeps its markup and stylesheet extensions. It runs in every project after every write, and the strings of a data file are judged at Step 4.

Excluded: `node_modules/`, `dist/`, `build/`, `.next/`, `out/`, `.svelte-kit/`, `.git/`, `coverage/`, `fixtures/`, `*.min.*`, `*.test.*`, `*.spec.*`.

Inside a file, these are out of scope:

- The contents of `<script>`, `<style>`, `<code>`, `<pre>`, `<noscript>`, `<title>` and every comment, and a JSX expression that is only `{…}`.
- For ST7, the contents of a `<template>`, which a browser leaves unrendered, except in a `.vue` file, where every `<template>` is markup.

`<title>`, `<noscript>` and `<template>` are matched in lower case only, so a JSX component such as `<Title>` is read as markup; `<script>`, `<style>`, `<code>` and `<pre>` are matched in any case. A `//` opens a comment only where nothing precedes it that makes it part of a value (a scheme, a word character, a quote or an `=`), so `href="//cdn.example.com"` survives with the rest of its line.

Two kinds of string are read: text between tags, and the value of a text-carrying attribute or prop (`label`, `placeholder`, `description`, `helperText`, `helpText`, `hint`, `title`, `aria-label`, `alt`, `caption`, `subtitle`, `legend`, `tooltip`).

### The surface

ST3 asks whether the file sits on a promotional surface. In order of precedence:

1. `--surface lp|saas` on the command line.
2. `meta.surface` in the nearest `tokens.json`, looked for in the first path's directory (a file's own directory) and then up to three directories above it. `lp` means a landing page and `saas` an application, the two values `validate_tokens.py` accepts; the auditor agent takes the same two values.
3. The path, the weakest signal: a segment named `marketing`, `landing` or `lp`, or a file name containing `landing` or `hero`.

### ST1: the screen describing itself (error)

**Check.** In any visible string: `(この|本)(画面|ページ|ダッシュボード|タブ|セクション|アプリ|サービス|機能)(では|から|で|には)`, a string opening with `ここでは`, and `(This|The) (page|screen|dashboard|view|section|tab|app) (lets|allows|enables|shows|displays|helps)`.

**Allowed.** Nothing. A screen has no legitimate reason to introduce itself to the person already on it.

**Why.** This is the most recognisable mark of a generated screen, and the one case where the pattern and the defect coincide exactly.

### ST2: an instruction that points at the layout (error)

**Check.** A Japanese positional phrase, `(下記|上記|以下|左記|右記|下|上|右|左)の(フォーム|入力欄|ボタン|欄|メニュー|タブ|カード|リンク|チェックボックス|プルダウン)`, in a string that also carries an instruction (`ください`, `入力`, `選択`, `押`, `クリック`, `タップ`, `参照`, `ご覧`). In English, an instruction verb followed by a UI noun and then `below` or `above`, the bare form `the <noun> below/above`, or an instruction verb whose sentence ends on `below` or `above` ("Enter your email below").

**Allowed.** The positional word without a UI noun: 「以下の条件」「上記の合計金額」 point at content and pass. The nouns that name content as readily as chrome (項目, 一覧, 表, リスト) are left off the list, so 「以下の項目をご確認のうえ、送信してください」 and 「下記の一覧に誤りがあれば修正してください」 pass; a confirmation screen says these about its own data.

**Why.** Requiring both the position and the UI noun keeps this off ordinary content pages, where 「以下の」 opens a perfectly good list.

### ST3: the capability explainer (warning)

**Check.** A short single-sentence string (80 characters or fewer after collapsing whitespace, carrying at most one 。 and at most one full stop) ending `できます`, `出来ます`, `が表示されます` or `をご覧いただけます` (with the trailing 。 optional in each) or opening `You can`, `You'll be able to` or `You are able to`, and standing in the subtitle position: it is the next visible string after a heading (`h1`, `h2`, `h3`, or a component whose name ends in `Heading` or `Title`, or a script entry whose key names a heading), with no other visible string between them. A visible string is element text or a rendered prop such as `label`, `description` or `caption`. The values of `alt`, `title`, `tooltip` and `aria-label` are left out of that sequence.

**Allowed.**

- A capability sentence anywhere but the subtitle position: under a service or menu entry, in a list of sign-up benefits, beside a field.
- Empty-state text, recognised by `empty`, `EmptyState`, `no-data`, `nodata`, `zero`, `no-results`, `not-found`, `cannot`, `空`, `ありません`, `ございません` or `0件` within 200 characters of the string; it legitimately says what becomes possible.
- Any string in a file on a landing-page surface, as settled under The surface; the script cannot tell the hero from the rest of the page.
- A `title` or `tooltip` attribute or prop, whose whole job is stating what a control does: 「Ctrl+S でも保存できます」 passes. `alt` text is never a candidate.
- A string that already raised ST1: ST1 reports it and ST3 stays silent.

**Why.** The length bound separates a caption from a paragraph: a documentation paragraph ends in 「できます」 constantly, while a 20-character grey line under a heading is this skill's business. A capability sentence is ordinary on real Japanese screens, which carry one under a menu entry, in a list of sign-up benefits and beside a field (23 of 57 application and public-service screens); as a subtitle under a heading it is rare (3 of 54 non-landing Japanese screens). It is a warning because the allowance list cannot be completed mechanically; a confirmation dialog and a line of reassurance microcopy both end in 「できます」 with every right to. Calibrated on `research/20261106-real-screens`.

### ST4: helper text restating its label (warning)

**Check.** Helper text (a `helperText`, `helpText`, `hint`, `description`, `caption` or `subtitle` value, or an element whose class holds the whole token `help`, `hint`, `description`, `caption`, `form-text` or `field-note`, alone or as a BEM element suffix such as `field__hint`) whose character-bigram overlap with the nearest label reaches 0.6. Nearest means nearest in either direction within 600 characters, because a section description above its label is as real a case as helper text below one. A helper or a label with no word character has no text to restate and is skipped.

**Allowed.** Helper text carrying a constraint token: a digit, `半角`, `全角`, `文字`, `以内`, `以上`, `以下`, `必須`, `任意`, `形式`, `拡張子`, `桁`, `バイト`, `@`, or the English `format`, `max`, `min`, `maximum`, `minimum`, `required`, `optional`, `characters`, `digits`, `must`, `at least`, `up to`, `MB`, `KB`.

**On the threshold.** Overlap is the trigger and a constraint token is the exemption. A missing constraint token alone is too weak a signal: a legitimate consequence line (「保存すると担当者に通知が届きます」) carries none. Restatement in different words belongs to the auditor, which can see that 「登録に使うアドレス」 restates 「メールアドレス」 without sharing a character with it. A class token such as `has-text-caption` or `js-job-show-description-toggle` names a style or a script hook and marks no helper; matching whole tokens leaves 0 of 54 non-landing Japanese screens with a hit. Calibrated on `research/20261106-real-screens`.

### ST5: a legend for the self-evident (warning)

**Check.** `(色|アイコン|マーク|バッジ|印|ラベル)` followed within 20 characters by `示します`, `表します` or `意味します`; and in English a colour word followed within 30 characters by `means`, `indicates`, `shows` or `denotes`. A leading `※` or `注:` is common and optional.

**Allowed.** Nothing mechanical. An ambiguous encoding needs its legend, so this is a warning and the reason for keeping one gets stated.

**Why.** A sentence explaining what a colour means is a sentence saying the colour did not mean it.

### ST6: inline tutorial prose (warning)

**Check.** Per file. The visible text carries `まず`, `最初に` or `はじめに` together with `してください` or `して下さい`, and also carries `次に`, `その後`, `続いて` or `最後に`. In English, `First,` together with `Then`.

**Allowed.** A file carrying a recognisable wizard or stepper, where the steps are the interface. The signals are read from markup only: `stepper`, `wizard`, `role="tablist"`, `aria-current="step"`, an `<ol>`, a `<Step>` or `<Steps>` component, or `step` or `steps` as a whole quoted value. Onboarding prose is where the word "steps" appears in visible text, so counting it would switch the check off on the files it exists for.

**Why.** File-level, because the defect is a sequence of instructions spread across the layout, which no single string reveals.

### ST7: text below the minimum size (error)

**Check.** Resolve the size every visible run actually gets, then report any run under 14px, unless the run holds no CJK character, is at most 24 visible characters, and is at least 12px.

Resolution follows the cascade as far as a stylesheet can be read without a browser.

- **Stylesheets read**: every `<style>` block in the file, every `<link rel="stylesheet" href>` that resolves to a local file, the nearest `theme.css` or `tokens.css` (beneath the scanned path, then up to four directories above), and any `.css` named on the command line.
- **`@media`**: a block whose only media type is `print` is skipped; every other block is read as if unconditional, because a size under a width query is still a size a reader gets.
- **Selectors**: a type, `.class`, `#id`, compounds of those, and descendant chains matched against the element's ancestors. The markup is walked with a stack of computed sizes.
- **Precedence**, highest first:
  1. an inline `style` (or a JSX `style={{fontSize}}`) marked `!important`;
  2. a matching stylesheet rule marked `!important`;
  3. the inline `style`;
  4. an SVG `font-size` attribute;
  5. a Tailwind size class (the last one in source order when more than one is present; variant prefixes such as `md:` are not read);
  6. the matching stylesheet rules by the higher specificity counted as (ids, classes, types), then the later one in source order;
  7. inheritance.
- **Root**: 16px unless an `html` or `:root` rule (alone or in a grouped selector such as `html, body`) declares a px size, which `rem` then uses.
- **Units**: `px`; `rem`; `em` and `%` against the parent; `pt` at 4/3; the keywords `xx-small` 9, `x-small` 10, `small` 13, `medium` 16, `large` 18, `x-large` 24, `xx-large` 32, `smaller` ×0.83, `larger` ×1.2; `var(--x)` when `--x` is declared literally on `:root`, on `html` or in `@theme`; `clamp()`, `min()` and `max()` as the smallest px literal inside.
- **Tailwind**: `text-xs` 12, `text-sm` 14, `text-base` 16, `text-lg` 18, `text-xl` 20, `text-2xl` 24, `text-3xl` 30, `text-4xl` 36, `text-5xl` 48, `text-6xl` 60, `text-7xl` 72, `text-8xl` 96, `text-9xl` 128 and `text-[N(px|rem|pt)]`, with a `--text-*` declaration in the found theme overriding the default.
- **SVG**: a `<text font-size="N">` counts.
- **Unresolved**: a `var()` whose property is undeclared resolves to its fallback when it carries one. A run whose nearest declared size is an undeclared `var()` with no fallback, a `clamp()` with no px literal, or a rule in a stylesheet that could not be opened inherits its parent's size and is not reported as unresolved.

What counts as text is settled in the Scope section above.

The finding names the resolved size and where it came from (`inline`, the selector, the Tailwind class, or `inherited from <tag.class>`), so the fix lands on the declaration itself.

With `--dom <dump.json>`, the same rule runs over the computed `fontSize` of every entry in a `cdp.js` dump's `text` array, and the source is reported as `rendered`. That mode sees what the stylesheet reader cannot: a size set from JavaScript, a `transform: scale()`, a `zoom`.

In `--dom` mode only rendered text counts, by the test `scripts/render/visibility.py` holds (`rendered`), which `check_render.py` R7 shares. An entry is skipped when its font size is 1px or less (icon fonts hide labels at 0px), when its class holds `sr-only` or the shorter side of its rect is 1px or less, when its rect lies wholly left of 0, right of the dump's viewport width or above 0, when its `effOpacity` is 0.05 or less, or when its `consent` flag is true. A dump that lacks `effOpacity` or `consent` reads as visible.

**Allowed.** Only the Latin-short case in the check itself. A dense table does not defend 13px Japanese; it gets 14px and fewer columns.

**Why.** A `.note { font-size: 11px }` rule in a stylesheet is where most small text is born, and a check that reads only the element never sees it. The Latin-short allowance is the one case where 12px reads, and its length bound keeps it from becoming a caption. Of 15,825 runs the check reports on 192 real screens at 1280px, 7.6% are text no reader sees: off-screen (693), opacity 0 (287), 1px or `sr-only` (118), 0px (112) and consent banners (39). The size and the Latin-short bound are the product owner's rule, and the dump test removes only the text that is not drawn. Calibrated on `research/20261106-real-screens`.

### ST10: a size below the minimum declared in a stylesheet (error and warning)

**Check.** In a `.css` or `.scss` file or a `<style>` block, outside `@media print`, a `font-size` declaration that resolves to a literal under 12px is an error; 12px to under 14px is a warning naming the Latin-short allowance. `rem` resolves against 16px, `pt` at 4/3, and the absolute keywords as ST7 lists them. `smaller`, `larger`, a `var()`, a percentage, an `em` and a `clamp()` with no px literal need a parent, so ST10 passes them to ST7, which judges them where they land. A file that raises the root (`html { font-size: 18px }`) can draw a warning here that ST7 clears; the ST7 result settles it, and one declaration is reported once, at its own line.

**Allowed.** Nothing mechanical for the error. A warning is kept only when every element the rule reaches is a Latin-short run, and the hand-over says so.

**Why.** ST7 catches the size where text is; this catches it where it is written, so a stylesheet written before any markup exists, or a rule nothing uses yet, is reported at the moment of writing, which is where the PostToolUse hook runs. A declaration under 12px has no legitimate reader on any screen.

### ST8: placeholder filler (error)

**Check.** In any visible string: `説明テキスト`, `ダミーテキスト`, `サンプルテキスト`, `テキストが入ります`, `ここにテキスト`, `lorem ipsum`, `Description goes here`, `Placeholder text`, and a string opening `TODO:` or `TODO：`.

**Allowed.** Nothing. A `placeholder` attribute holding a real example (`yamada@example.com`) passes.

**Why.** Filler reaches production because it looks deliberate in a screenshot. C15 (`references/ui-copy.md`) also reports `lorem ipsum`; each script runs on its own, so both report it.

### ST9: a note defending the method (warning)

**Check.** In any visible string, method vocabulary together with a negation:

- Japanese method vocabulary: `検定|仮説|p値|有意|偽陽性|信頼区間|記述統計|標準誤差|パラメータ|パラメーター|補正|調整|推定|集計|標本|サンプル|ベンチマーク|閾値|しきい値|最適化|統計`
- Japanese negation: `[てで]いない|[てで]いません|[てで]いなかった|ではない|ではなく|ではありません|しない|しません|せず`
- English method vocabulary: `test|tested|hypothesis|p-value|significan\w*|false positive|confidence interval|parameter|tuned|fitted|adjusted|optimi[sz]ed|sample|benchmark|model|statistic`, each noun except `hypothesis` also in the plural
- English negation: `not|never|without|n't|un(tested|adjusted|tuned|fitted)`, and `no` only directly before `significance`, `test`, `adjustment`, `correction` or `hypothesis`

The negation branch skips a string inside an element whose class or id holds `cookie`, `consent`, `privacy` or `gdpr` (a script entry whose key holds one), because a notice states what it does not collect.

Also, with no negation at all, a string longer than ten visible characters carrying test vocabulary (`p値|偽陽性|信頼区間|記述統計|有意水準|帰無|対立仮説|検定統計量|[tTχ]検定|カイ二乗検定`, or `hypothesis|p-value|false positive|confidence interval|null hypothesis|descriptive statistic`) because 「p値」 is a column heading and 「AとBの差がゼロという仮説のもとでのp値」 is the author explaining it. 「仮説」 and 「検定」 alone are outside this list, because 「仮説検証」 is marketing copy and 「検定」 is an examination.

**Allowed.** Empty-state text, recognised as ST3 recognises it. Nothing else mechanically: a data-fact note can carry a negation legitimately (an exclusion), so this is a warning, and a kept note is restated in the positive where one exists (「集計対象は支払いが完了した注文だけです」 for 「未払いの注文は集計していない」), with the reason in the hand-over.

**Why.** Negation alone is everywhere in good copy (「削除したファイルは復元できません」), and method words alone are column headings. Together, in a caption, they are the author telling the reader what was not done. A data-fact exclusion note (Yahoo! Finance's 「分割後の調整が未反映の目標株価は表示していません」) is the one real hit left on 1 of 54 non-landing Japanese screens. Calibrated on `research/20261106-real-screens`.

---

## Out of reach for this script

ST7 in source mode misses a size set from JavaScript, a `transform: scale()` or a `zoom` on an ancestor, and a rule behind a selector the resolver skips (any selector outside the forms under Selectors: a pseudo-class such as `:hover`, `:first-child` or `:nth-child`, a pseudo-element, `*`, an attribute selector, and the `>`, `+` and `~` combinators). ST10 still reports such a declaration at its own line when it is under the minimum; the element it lands on is seen only by ST7's `--dom` mode, which `review-design-lead`'s `check_render.py` R7 also covers at review time.

The `shippable-text-auditor` agent judges the following on the built screen, since each needs a reader who can tell what a sentence means:

- A self-describing screen phrased in a way the ST1 patterns do not carry. 「各種指標をまとめてご覧いただける場所です」 says the same thing and matches nothing.
- A label describing the feature where the action should be named: 「ユーザー管理機能」 on the control that opens the user list.
- Helper text that restates its label in meaning through different words, which ST4's bigram overlap cannot see.
- A caption stating what is already visible on the chart, the table or the card above it.
- Whether a legend's encoding is ambiguous, which is the only question that decides ST5.
- Whether an empty state's next-action sentence repeats what its button already says; a sentence reporting the emptiness alone stands.
- A definitions legend under a chart written without a negation. 「購入まで進んだセッションの、全セッションに対する割合」 is a tooltip's sentence sitting in a `<dl>`, and only a reader can tell it from a data-fact note.
