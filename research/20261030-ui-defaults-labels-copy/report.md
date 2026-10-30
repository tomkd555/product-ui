# Which default values, font sizes, labels and wording do highly rated web screens use, and which of them make a screen or its text read as AI-made

As of 2026-10-30. Tier: DEEP.

## Answer

Highly rated design systems publish ranges that product-ui can take as defaults. Spacing steps sit on a 4px base in Tailwind, on 8px in Atlassian and on 5px in GOV.UK [E1, E16, E10]. Carbon builds its scale from multiples of 2, 4 and 8px, and Primer lists base sizes of 2px and 4px [E13, E15]. Body text is 16px in DADS and SmartHR, the 2 Japanese systems, and 14px in Carbon's productive set and in Atlassian's default body token [E21, E62, E67, E71]. DADS allows 14px only as an exception and in principle permits nothing smaller [E47]. DADS and SmartHR set body text for reading at a line height of 1.5 or more, and DADS sets letter spacing of 0 to 2% [E48, E64, E50]. WCAG's AAA criterion 1.4.8 gives 80 characters, or 40 for CJK text, as the maximum line width [E73].

Tailwind and shadcn/ui defaults sit inside most of these ranges: a 4px spacing unit, `text-base` at 16px on a 24px line, and a 36px default button [E1, E54, E34]. Two defaults fall outside them. shadcn's base radius of 0.625rem (10px) is above the 6px of Primer and the 4px of Fluent [E7, E14, E19], and `text-sm` at 14px on a 20px line gives 1.43, below the 1.5 that DADS recommends for body text in reading content (lead's computation from [E55, E48]).

For labels, Japanese and English guides agree that a button names its action [E76, E89]. SmartHR drops 「する」 from the label, as in 「追加」, and DADS and SmartHR both reject 「こちら」 as link text [E77, E81, E86]. GOV.UK and Microsoft write labels in sentence case [E89, E94], while Apple's HIG buttons page, found during verification, asks for title-style capitalisation such as "Add to Cart". GOV.UK and Atlassian leave "please" out of general content and error messages [E92, E98].

The AI tells collected for values, layout and labels all rest on grade C commentary from 2026 [E99, E100, E101, E102, E105, E108]. These sources name a radius of about 0.5rem on everything, shadows at about 0.1 opacity, wide tracking on uppercase eyebrows, oversized hero text, a 3-column icon grid, a stock section order and a "Get Started" gradient button [E99, E100, E101, E102, E105, E108]. Apart from a radius of "around half a rem", none of them gives a spacing or size value that marks AI output, and none reports a measurement [E99, E100]. For text, the grade A evidence on Japanese readers points away from tell lists. 403 Japanese participants had limited ability to tell AI-written text from human text [E119], and their comments suggested that they relied mainly on surface impressions [E121]. A Hiroshima University bachelor's thesis, reported by Fyve, found that 1 of 148 popular 「AIらしさ」 claims matched measurement [E112].

The plan therefore has its firmest footing where it takes default values from the design systems and wording rules from the style guides, and weaker footing where it bans specific values as signs of AI (lead's inference). A controlled study of how readers react to a uniform radius, shadow or type size, with content held constant, would change this.

## Findings

### 1. Setting values

The spacing base unit is 4px in Tailwind CSS v4.3, which sets `--spacing` to 0.25rem [E1]. IBM Carbon's first 5 spacing tokens are 2, 4, 8, 12 and 16px [E13], and Primer has base-size tokens of 2px and 4px [E15]. Atlassian builds its spacing scale on an 8px unit, with `space.100` at 8px, `space.150` at 12px and `space.200` at 16px [E16, E17]. GOV.UK uses steps of 5px: its static scale runs 0, 5, 10, 15, 20, 25, 30, 40, 50 and 60px [E10, E41]. DADS observes that a style guide's spacing scale usually holds about 3 to 5 values [E20]. The previous run recorded `p-6` among the classes of AI-made screens (ai-tells-ui E15). No source in this run ties a particular spacing value to AI output.

Corner radius differs most between the frameworks and the design systems. Tailwind's radius scale runs from `xs` at 0.125rem to `4xl` at 2rem, with `lg` at 0.5rem and `2xl` at 1rem [E2]. shadcn/ui sets `--radius` to 0.625rem and derives `radius-sm` as 0.6 times and `radius-md` as 0.8 times that value, with `radius-lg` equal to it [E7, E8]. At a 16px root this gives 6, 8 and 10px (lead's computation from [E7, E8]). Primer's radius tokens are 3px, 6px and 12px, with 6px as the default [E14]. Fluent 2 sets 4px as the default radius for rectangles and 2px for shapes smaller than 32px [E18, E19].

The AI tells for radius concern uniformity. A 2026-06 devtake.dev article names "Border radius around half a rem on everything" as part of the AI front-end signature [E99]. Noqta writes that one identical exaggerated radius on cards, buttons, inputs, badges and images flattens hierarchy [E102]; the previous run cited the same publisher and the classes `rounded-2xl` and `rounded-3xl` (ai-tells-ui E11, E15).

Shadow values follow the same pattern. Tailwind's `shadow-sm` has two layers, `0 1px 3px` and `0 1px 2px -1px`, each in black at 0.1 alpha [E5]. DADS assigns drop shadows Style 1 to 8 by elevation level [E26]. devtake.dev names "Box shadows at roughly 0.1 opacity" as an AI trait [E99], and a 2026-07 Substack post names soft grey shadows on floating cards [E109]. The 0.1 alpha that these sources name as a tell is the alpha of Tailwind's own default shadow, so the tell is the framework default applied to every surface (lead's inference from [E5, E99]).

Line height in the design systems depends on the script and the density. Tailwind's `leading` scale runs from `tight` at 1.25 through `normal` at 1.5 to `loose` at 2 [E3]. GOV.UK gives every point on its type scale a line height that is a multiple of 5px [E11]. DADS lists 150% as the minimum for body text on general websites [E25], pairs 18px with 160% and 16px or 17px with 170% in its standard bold styles [E23], and uses 120% for 14px text in its dense styles for admin screens [E24]. WCAG's success criterion 1.4.8 asks for line spacing of at least space-and-a-half within paragraphs [E74].

Letter spacing is positive in Japanese and small in Latin systems. Tailwind's `tracking` scale runs from `tighter` at -0.05em to `widest` at 0.1em [E4]. DADS sets 0, 1% or 2% depending on the font size [E22]. Carbon sets 0.16px on 14px body text and 0.32px on 12px labels [E68, E69]. Noqta names wide tracking on uppercase labels and eyebrow text, "auto-applied everywhere", as one of 4 overused AI patterns [E101]. No source in this run names tight tracking on headings as an AI tell.

Colour roles were collected only for shadcn/ui, which pairs each background token with a foreground token, as in `primary` and `primary-foreground` [E9]. No source in this run gives the number of colours in a highly rated palette. The previous run found that shadcn/ui's default primary is a neutral and that the purple gradient comes from the model's habits (ai-tells-ui E16).

For the web as a whole, the latest CSS figures come from the 2022 Web Almanac [E27, E30]. Font sizes were set in px in 71% of declarations and em in 15% [E27]. Line heights were px in 49% and unitless numbers in 35% [E28]. The 2025 edition has no CSS chapter [E30].

### 2. Screen design defaults

Maximum widths vary with the purpose of the page. GOV.UK sets its default maximum page width at 1020px [E40]. Tailwind's `max-w` scale runs from `max-w-3xs` at 256px to `max-w-7xl` at 1280px [E32], with `max-w-2xl` at 672px and `max-w-3xl` at 768px [E33].

Breakpoints and grids differ between web and platform systems. Tailwind's default breakpoints are 640, 768, 1024, 1280 and 1536px, applied mobile-first [E31]. Carbon's 2x grid uses 4 columns from 320px, 8 from 672px and 16 from 1056px and from 1584px, with a 16px gutter [E37]. Android's window size classes, which Material 3 uses, set Compact below 600dp, Expanded from 840dp to under 1200dp and Large from 1200dp to under 1600dp [E42, E43].

Density is explicit in the systems built for data-heavy screens. Carbon offers data-table rows at 24, 32, 40, 48 and 64px [E38], with 14px text and 16px cell padding on each side [E39]. DADS has dense text styles for admin screens, such as 14px at 130% or 120% [E53].

Component sizes are published as numbers in shadcn/ui and as names in the design systems. shadcn/ui's default button is `h-9` (36px) with `px-4 py-2`; `sm` is `h-8` with `px-3`, `lg` is `h-10` with `px-6`, and the icon button is `size-9` [E34, E35]. Its sidebar is 16rem wide, 18rem on mobile and 3rem when collapsed to icons [E36]. SmartHR offers 2 button sizes, normal and small, the small one for saving space [E44]. Primer offers small, medium and large, with large reserved for emphasis and used sparingly [E45].

Page structure appeared in one design-system rule. DADS places 「OK」, 「完了」 and 「次へ」 at the right and 「キャンセル」, 「中止」 and 「戻る」 at the left on desktop [E88]. The AI tells for page structure come from 2026 commentary [E99, E103, E105]. Superdesign names the stock order of hero, logos, 3 features, testimonial, pricing and CTA [E105], devtake.dev names a 3-column feature grid with an icon per card [E99], and Noqta names pulsing "Live" or "New" pill badges on features that are neither [E103]. The previous run recorded the same section order from other publishers (ai-tells-ui E6, E13). No source gives a container width, section padding or gap value as a sign of AI.

### 3. Font sizes

Body text is 16px or larger in the Japanese systems and in GOV.UK [E21, E62, E12]. DADS sets 16 CSS px or more as the reference for body and UI text [E21, E46]. SmartHR sets its base at 16px [E62]. GOV.UK sets body text at 19px on a 25px line on large screens, and its small body text at 16px on a 20px line [E12, E59]. Carbon's productive set and Atlassian's default body token use 14px [E67, E71]. Carbon's productive set has a 14px base and its expressive set a 16px base [E67]. Atlassian's `font.body` is 14px on a 20px line [E71], and Atlassian names Body L as the default size for long-form content [E70]. Apple's defaults are 17pt on iOS and iPadOS and 13pt on macOS [E72]. Tailwind's `text-base` is 16px on a 24px line [E54].

The size ramps step by ratios that grow with the size. Tailwind's steps are 12, 14, 16, 18, 20, 24 and 30px, and `text-6xl` is 60px with a line height of 1 [E55, E56, E57, E58]. The ratio between neighbouring Tailwind steps rises from 1.11 to 1.25 (lead's computation from [E55, E56, E57]). SmartHR's tokens are 10.67, 12, 13.71, 16, 19.2, 24 and 32px [E63], which equal 16 × 6/n for n from 9 down to 3 (lead's computation from [E63]). GOV.UK's large-screen scale includes 16, 19 and 24px [E59]. DADS sets display sizes at 48, 57 and 64px, each at 140% line height [E51].

The minimum size differs between systems. DADS permits 14px only in exceptional cases and in principle no size below it [E47]. SmartHR has 10.67px and 12px tokens but tells designers to avoid its small and extra-small sizes for paragraphs unless the layout leaves no other choice [E63, E65]. Carbon's `label-01` is 12px on a 16px line [E69], and Tailwind's `text-xs` is 12px [E55]. Apple's minimums are 11pt on iOS and 10pt on macOS [E72].

Japanese text gets more line height and positive letter spacing. DADS recommends at least 1.5 for body text [E48]. Its standard styles set 18px at 160% and 16px or 17px at 170% or 175%, each with 2% letter spacing [E49]. DADS describes 170% as a line height chosen to reduce the psychological load of reading [E52]. SmartHR sets paragraph line height at 1.5 and the line height of labels such as buttons at 1 [E64, E66]. Tailwind's `text-sm` pairs 14px with a 20px line, a ratio of 1.43, below the 1.5 that DADS recommends for body text in reading content (lead's computation from [E55, E48]).

Line length has one published limit and two Japanese studies behind it. WCAG's success criterion 1.4.8 says lines should not exceed 80 characters, or 40 for CJK text [E73]. At 16px, Tailwind's `max-w-2xl` of 672px holds 42 full-width characters, close to the CJK limit (lead's computation from [E33, E73]). In a 2017 eye-movement study, breaking Japanese lines only between bunsetsu gave faster reading than the conventional layout at line lengths of 5 to 40 characters [E115]. A 2016 study with 10 Japanese readers of scrolling text found reading performance highest at character sizes of 0.6 to 1.0 degrees of visual angle [E114].

The AI tells for font size have no values behind them. devtake.dev names "Oversized hero text over vague copy" [E100], without a size. The previous run recorded broken mixing of Japanese and Latin typefaces as a trait of AI first drafts (ai-tells-ui E118, E119) and a rendered check for tiny text in one open-source checker (ai-tells-ui E105). No source in this run names small grey text, a flat size hierarchy or a particular hero size as a sign of AI. Across the web, the 2025 Web Almanac reports px as the font-size unit on 67% of desktop sites and gives no median size [E75].

### 4. Labels

Japanese button labels in SmartHR use the terminal form of a verb [E76]. For a sa-hen noun, SmartHR drops 「する」 and gives 「追加」 and 「削除」 as correct and 「追加する」 and 「削除する」 as incorrect [E77, E78]. A dialog title takes the form 「{対象}の{アクション}」 and its confirming button 「{アクション}」 [E79]. Description text ends in a verb and avoids noun endings [E80]. SmartHR writes the press of a button as 「押す」 and avoids 「クリック」 and 「タップ」, and writes data extraction as 「書き出す」 in place of 「エクスポート」 or 「出力」 [E84, E85].

Link text has the clearest agreement in Japanese. SmartHR tells writers to avoid 「こちら」 and to name the destination [E81]. DADS says that link text of 「ここ」 or 「こちら」 alone cannot be understood on its own by screen-reader users [E86]. Where a repeated phrase such as 「もっと詳しく」 cannot be avoided, DADS tells writers to tell the links apart with an `aria-label` [E87].

Status labels in SmartHR convey the progress of a task or the action requested of the user [E82]. In-progress states take the form ○○中, as in 依頼準備中, 入力中 and 回答中 [E83]. Noqta names pulsing "Live" or "New" badges on features that are neither as an AI tell [E103].

GOV.UK and Microsoft use sentence case. Apple's HIG buttons page, found during verification, uses title-style capitalisation for button labels. GOV.UK writes button text in sentence case and describes the action the button performs [E89], and uses "Save and continue" where the service saves the user's answers [E90]. The Microsoft Writing Style Guide applies sentence-style capitalisation to button names, headings and titles [E93, E94]. For errors, GOV.UK lists generic messages such as "This field is required" as ones to avoid [E91] and says there is usually no need for "please" [E92]. Atlassian writes error titles in sentence case, keeps them to 3 or 4 words where possible, and leaves out "please" and "sorry" [E96, E97, E98].

The AI tells in labels are few and from commentary. 925Studios describes the default AI landing page with a gradient button labelled "Get Started" [E108]. The previous run recorded the same CTA repeated in every section and English labels such as 「LOGIN」 on Japanese screens (ai-tells-ui E120, E123). No source in this run names Title Case, 「詳細はこちら」 or 「今すぐ始める」 as a sign of AI.

The effect of wording on task success has thin evidence in this run. Google researchers found that 3 visual variants of one error message improved both comprehension and resolution over the original [E116]. In a 2016 eye-tracking study of web-form errors, messages placed far from the field drew fewer saccades and fixations, while completion time and error-correction time did not differ significantly [E117, E118]. No experiment on button-label wording was found.

### 5. Slop text

The style guides already carry rules that remove filler. Microsoft tells writers to omit unnecessary adverbs [E95]. GOV.UK says there is usually no need for "please" or "please note" [E92]. SmartHR requires description text to end in a verb [E80].

The English tells collected in 2026 extend the previous run's list [E104, E106, E107]. Superdesign names the mad-lib headline "The AI-powered [X] for modern [Y]" and benefit triads such as "Save time. Work smarter. Scale faster." [E107, E106]. Noqta cites "Build the future of work" and "Scale without limits" as headlines as generic as a purple gradient [E104]. Wikipedia's guide states that LLMs overuse the rule of three [E111] and gives a word group for the GPT-5 era, from mid-2025 to mid-2026, that includes "emphasizing", "enhance" and "highlighting" [E110]. The previous run holds the older stock words and Wikipedia's advice that many such words together carry more signal than one (ai-tells-ui E14, E19, E21, E32).

The Japanese evidence weighs against fixed tell lists. A Hiroshima University bachelor's thesis, not peer reviewed and reported by Fyve, compared 148 popular claims about 「AIらしさ」 with measurement and found that 1 of them matched [E112]. The same report says noun-ending sentences were far more frequent in human text than in AI text [E113]. Fyve sells AI advisory services, and the thesis itself was not read in this run. A peer-reviewed study in PLOS ONE gives grade A support in the same direction. 403 Japanese participants judged public-comment texts written by humans and by 7 LLMs, and their ability to tell them apart was limited [E119]. Texts from the newer o1 model were judged human-written more often than GPT-4o texts and raised the participants' confidence [E120]. Their free-text comments suggested that they judged mainly from surface impressions such as phrasing, word endings, conjunctions and punctuation [E121]. The previous run's Japanese tells, such as the buzzwords 「革新的」 and 「シームレス」 and residue such as 「これにより」, come from single practitioners (ai-tells-ui E113, E124).

Copy performance gives one measured comparison. In a 2025 A/B study of Meta ads in Canada, copy written by humans beat AI-generated copy on cost per result in 9 of 12 cases and on click-through rate in 5 of 12 [E122]. The 2 authors are practitioners at an agency, which gains from the finding [E122]. The readers of those ads did not know who wrote them, so this effect needs no attribution to AI (lead's inference from [E122]).

### 6. The hypotheses

H1, the user's view, holds for the design systems and the style guides, which publish measurable ranges and rules [E1, E21, E47, E76, E89]. It holds weakly for AI tells in values and labels, which rest on grade C commentary with no measured values [E99, E100, E108]. It finds no support for award-recognised sites, because no values for them were found.

H2 has partial support. Tailwind and shadcn/ui put body text at 16px and spacing on 4px, inside the design-system ranges [E54, E1, E21, E13]. The tells name uniform application: the same radius and the same 0.1-alpha shadow on every surface, and wide tracking applied everywhere [E99, E101, E102]. The shadow alpha in the tell equals Tailwind's default [E5, E99]. Hierarchy and per-element choice therefore separate good output from AI-made output in these sources, while a range check alone does not (lead's inference).

H3 has support within the design systems. Carbon splits a productive 14px set from an expressive 16px set [E67], DADS keeps dense styles for admin screens [E24], and Atlassian uses 14px for body text and Body L for long-form content [E70, E71]. The values of award-recognised marketing sites were not found, so the gap between them and product systems is unmeasured.

H4 has grade A support for Japanese readers [E119, E121] and grade C support from the thesis report [E112, E113]. The ad-copy study shows that generic AI copy can cost performance without any attribution [E122].

### 7. Tables by area

Grades: A for official design-system pages of public bodies, W3C and peer-reviewed studies; B for vendor and framework documentation, Wikipedia and other studies; C for blogs, agencies and reports of unpublished work. A row takes the grade of its strongest item for the design-system column and gives the AI-tell grade separately. "None found" means the collectors found no source.

#### Area 1: setting values

| Item | Highly rated design systems | Tailwind / shadcn/ui default | AI tell | Grade |
|---|---|---|---|---|
| Spacing base | Carbon multiples of 2, 4 and 8 (2, 4, 8, 12, 16); Primer 2px and 4px steps; 8px Atlassian; 5px GOV.UK (5 to 60); DADS: 3 to 5 values per scale [E13, E15, E16, E10, E20] | 0.25rem (4px) [E1] | `p-6` everywhere (ai-tells-ui E15); no new source | A; tell C |
| Corner radius | Primer 3, 6 (default), 12px; Fluent 4px, 2px under 32px [E14, E18, E19] | Tailwind 0.125 to 2rem; shadcn 0.625rem (10px), sm 0.6x, md 0.8x [E2, E7, E8] | one identical radius on everything; about 0.5rem everywhere [E102, E99] | B; tell C |
| Shadow | DADS Style 1 to 8 by elevation [E26] | `shadow-sm`: 2 layers at 0.1 alpha [E5] | 0.1-opacity shadow on every card; soft grey shadows on floating cards [E99, E109] | A; tell C |
| Line height | DADS body 150% minimum, 160 to 175%; dense 120 to 130%; SmartHR 1.5, labels 1; GOV.UK multiples of 5px; WCAG 1.5 [E25, E23, E24, E64, E66, E11, E74] | `leading` 1.25 to 2 [E3] | none found | A |
| Letter spacing | DADS 0 to 2%; Carbon 0.16px at 14px, 0.32px at 12px [E22, E68, E69] | `tracking` -0.05em to 0.1em [E4] | wide tracking on uppercase eyebrows everywhere [E101] | A; tell C |
| Colour roles | not collected | background and foreground pairs [E9] | purple gradients (ai-tells-ui E1, E16) | B |
| Web baseline | Web Almanac 2022: font-size in px 71%; line-height unitless 35% [E27, E28] | | | A |

#### Area 2: screen design defaults

| Item | Highly rated design systems | Tailwind / shadcn/ui default | AI tell | Grade |
|---|---|---|---|---|
| Maximum width | GOV.UK 1020px [E40] | `max-w-3xs` 256px to `max-w-7xl` 1280px [E32] | none found with a value | A |
| Breakpoints and grid | Carbon 320, 672, 1056, 1584px with 4, 8, 16, 16 columns and 16px gutter; Android Compact under 600dp, Expanded 840dp, Large 1200dp [E37, E42] | 640, 768, 1024, 1280, 1536px [E31] | none found | A |
| Density | Carbon rows 24 to 64px, 14px text, 16px cell padding; DADS dense 14px at 120 to 130% [E38, E39, E53] | none collected | none found | A |
| Buttons | SmartHR 2 sizes; Primer 3 sizes, large used sparingly [E44, E45] | `h-9` (36px) `px-4 py-2`; `sm` `h-8`; `lg` `h-10` [E34, E35] | gradient "Get Started" button [E108] | A; tell C |
| Side navigation | none collected | 16rem, 18rem on mobile, 3rem collapsed [E36] | none found | B |
| Page structure | DADS: OK, 完了, 次へ at right; キャンセル, 戻る at left [E88] | none collected | stock section order; 3-column icon grid; pulsing badges [E105, E99, E103] | A; tell C |

#### Area 3: font sizes

| Item | Highly rated design systems | Tailwind / shadcn/ui default | AI tell | Grade |
|---|---|---|---|---|
| Body size | DADS 16px or more; SmartHR 16px; GOV.UK 19px on large screens; Carbon 14px productive, 16px expressive; Atlassian 14px; Apple 17pt iOS, 13pt macOS [E21, E62, E59, E67, E71, E72] | `text-base` 16px on 24px [E54] | oversized hero text over vague copy, no size given [E100] | A; tell C |
| Ramp | SmartHR 10.67 to 32px; GOV.UK 16, 19, 24px; DADS display 48, 57, 64px at 140% [E63, E59, E51] | 12, 14, 16, 18, 20, 24, 30px, then 60px at line height 1 [E55, E56, E57, E58] | none found | A |
| Minimum | DADS 14px by exception, nothing smaller; SmartHR avoids S and XS for paragraphs; Carbon labels 12px; Apple 11pt iOS, 10pt macOS [E47, E65, E69, E72] | `text-xs` 12px [E55] | tiny text checked by one checker (ai-tells-ui E105) | A |
| Japanese text | line height 150% or more, 170% for reading; letter spacing 0 to 2% [E48, E52, E50] | `text-sm` 14px on 20px (1.43) [E55] | broken Japanese and Latin mixing (ai-tells-ui E118) | A |
| Line length | WCAG 80 characters, 40 for CJK; bunsetsu line breaks read faster at 5 to 40 characters [E73, E115] | `max-w-2xl` 672px [E33] | none found | A |

#### Area 4: labels

| Item | Highly rated design systems | Tailwind / shadcn/ui default | AI tell | Grade |
|---|---|---|---|---|
| Japanese buttons | terminal-form verb, 「追加」 without 「する」; dialog 「{対象}の{アクション}」 [E76, E77, E79] | none | English labels such as 「LOGIN」 on Japanese screens (ai-tells-ui E123) | C as recorded; tell C |
| English buttons | sentence case in GOV.UK and Microsoft, names the action, "Save and continue" [E89, E90, E94]; Apple HIG uses title-style capitalisation | none | gradient "Get Started" [E108] | A; tell C |
| Link text | avoid 「こちら」; `aria-label` for repeated 「もっと詳しく」 [E81, E86, E87] | none | none found | A |
| Status | progress or requested action; ○○中 [E82, E83] | none | pulsing "Live" or "New" badges [E103] | C; tell C |
| Errors | no generic "This field is required"; no "please"; titles of 3 or 4 words [E91, E92, E97] | none | none found | A |
| Effect on tasks | visual variants of an error message improve comprehension and resolution; placement changes fixations [E116, E117] | | | A |

#### Area 5: slop text

| Item | Highly rated design systems and guides | Tailwind / shadcn/ui default | AI tell | Grade |
|---|---|---|---|---|
| Filler rules | omit unnecessary adverbs; no "please"; descriptions end in a verb [E95, E92, E80] | none | | B |
| Headlines | none collected | none | "The AI-powered [X] for modern [Y]"; "Build the future of work" [E107, E104] | tell C |
| Triads | none collected | none | "Save time. Work smarter. Scale faster."; rule of three [E106, E111] | tell B |
| Word lists | none collected | none | GPT-5-era words such as "enhance" and "highlighting" [E110] | tell B |
| Japanese markers | none collected | none | 1 of 148 popular claims matched measurement; noun endings more frequent in human text [E112, E113] | tell C, opposing |
| Japanese readers | none collected | none | detection limited; comments suggest surface cues [E119, E121] | A |
| Copy performance | none collected | none | human copy beat AI copy on cost per result in 9 of 12 ad tests [E122] | B |

## Disagreements and limits

The design systems disagree on 4 values the plan must choose:

- Spacing base: 4px in Tailwind, 8px in Atlassian and 5px in GOV.UK, with Carbon building on multiples of 2, 4 and 8px [E1, E16, E10, E13].
- Body size: 14px in Carbon's productive set and Atlassian, 16px in DADS, SmartHR and Tailwind, 19px in GOV.UK on large screens [E67, E71, E21, E62, E54, E59]. The difference follows the purpose: dense product screens use 14px, public services and reading text use 16px or more.
- Minimum size: DADS permits nothing below 14px as a rule, while SmartHR, Carbon and Tailwind have 12px or smaller tokens [E47, E63, E69, E55]. SmartHR limits its small sizes in paragraphs [E65].
- Radius: shadcn/ui's 10px default is larger than Primer's 6px and Fluent's 4px [E7, E14, E19].

English guides also differ on capitalisation. GOV.UK and Microsoft use sentence case [E89, E94], and Apple's HIG buttons page, found during verification, uses title-style capitalisation.

The Japanese evidence on AI-written prose conflicts. The previous run's markers, such as 「これにより」 and buzzword lists, come from practitioners (ai-tells-ui E124, E113). Fyve's report of a bachelor's thesis finds most popular claims unconfirmed [E112, E113]. The thesis is unpublished, and Fyve sells AI services. The ad-copy study comes from agency practitioners who gain from a result in favour of human copywriters [E122].

The collectors could not reach several sources:

- Award-recognised sites: no values were found for Awwwards, CSS Design Awards, the Webby Awards, Good Design Award or Web グランプリ. The layout collector did not search them.
- Material 3, Apple HIG beyond its default and minimum sizes, Shopify Polaris and Fluent 2 typography: the pages were rendered by JavaScript or returned thin content. Polaris and Material 3 contributed no item.
- DADS layout pages were unreachable for the layout collector, so DADS widths and grids are missing.
- The 2025 Web Almanac has no CSS chapter, so the web-wide CSS figures date from 2022 [E30, E27].
- No source gives the number of colours in a highly rated palette.
- No source ties a spacing value, container width, hero size, tight heading tracking, muted grey text, Title Case or 「詳細はこちら」 to AI output.
- No experiment on button-label wording, no Japanese study of the effect of font size or line spacing on reading speed, and no Japanese study of AI-written ad or UI copy was found. English line-length studies returned HTTP 403, and the academic search service returned HTTP 429.
- SmartHR's writing rules carry grade C in the labelling collection, while SmartHR's typography pages carry grade A. Both come from SmartHR's own design-system site.
- To keep the run under 10 agents, as the user's instructions require, 15 claims were verified where the DEEP tier sets 25.

What would change the Answer: measured token values from award-recognised sites; a controlled study that varies radius, shadow or type size with content held constant and measures attribution to AI or trust; or an experiment on Japanese button and link wording and task success.

Sources, the gaps and the search log: `sources.md`.
