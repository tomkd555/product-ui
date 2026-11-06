# Composition

Source of record for the composition plan a screen gets before any markup, for the shell, for the container rule, for the KPI tile rule (its slots are the pattern `measure.tile.kpi`, `references/patterns.md`), and for the measured checks in `scripts/render/check_render.py` listed under "Measured type and spacing" and "What the checks cover". Read it at Step 3 of `SKILL.md` before the first element is placed, and when one of these, S11 or C18 to C21 fires.

## What it settles

A screen reads as designed when a viewer recovers the rank of its parts at a glance: what it is for, what dominates, in what order it is read, and what belongs together. The element-level checks (colours, fonts, string existence, text size) leave that rank unsettled, and a screen of equal panels passes every one of them. "If everything is contrasted, then nothing stands out" (Nielsen Norman Group); "because everything in this dashboard is visually prominent and vying for your attention, nothing in particular grabs your attention. When this happens the dashboard has failed" (Stephen Few).

Three mechanisms carry the rank, and each has a check or a reviewer question:

| Mechanism | Carried by | Where it is judged |
|---|---|---|
| Emphasis | size, weight and position in steps a viewer can tell apart; one dominant element | R14; cold-read questions 1 to 4 |
| Grouping | distance first, a filled region second, a rule last; the enclosures production screens of the kind draw | R12, R13, S11; cold-read question 5 |
| Density | the job the screen does for its reader: monitor, enter, look up, decide, work on one record | the plan's job class; R15; cold-read question 8 |

Sameness is right in what users learn once and reuse: the shell, the navigation, the tokens, the control forms, the regions a screen of its kind carries, and the choice among a short list of layout archetypes. Sameness is the defect when it replaces the decision about this screen's content: the same tile row and the same panel grid on every screen, whoever reads it and whatever the job.

## The plan

Write one plan per screen into the Composition section of `ui-brief.md` (`assets/brief.template.md`) before any markup. The reviewer in Step 5 conforms the rendered screen to it.

| Decision | Write | Source |
|---|---|---|
| Purpose | one phrase: what the reader gets from this screen | Few |
| Kind | the section of `references/real-screens.md` the screen follows | `references/real-screens.md` |
| Regions | the regions of that kind this screen carries, in reading order, the shell first: every region marked `always` or `usual`, and each one left out named under Omissions with the reason | `references/real-screens.md` |
| Job class | `monitor` (glance at measures), `enter` (give the product data), `lookup` (find or compare records), `decide` (choose between options), `record` (read one record and act on it) | Few; Shneiderman 1996; GOV.UK |
| Reader | the group from `meta.users` this screen serves, with its frequency and expertise | ISO 9241-11 |
| Dominant element | the one element the eye lands on first after the page title, and why it is the purpose; then the second. The page title is the largest text on production screens that have one (12 of 12 forms, 14 of 18 records), so the dominant element leads by area, position or weight. On a `monitor` screen it is the summary: the headline figure, or the tile row as a whole, with the main chart under it | NN/g hierarchy; Polaris; `references/real-screens.md` |
| Reading order | three to five stops, top and leading edge first | Apple HIG; SmartHR 視線誘導 |
| Density | from the job class: `monitor` puts the summary and the main chart in the first viewport, and the rows continue below it (the page runs past the first viewport on 13 of 15 production monitoring screens); `enter` is one column with one question group per step; `lookup` is dense rows behind a filter; `decide` puts the comparison first; `record` puts the title and the state first and the properties beside the body (a right rail on 13 of 18 production record screens) | Few; GOV.UK; NN/g forms; Shneiderman 1996; `references/real-screens.md` |
| Archetype | `list-detail`, `supporting-pane`, `feed`, `single-column`, `dashboard`; `single-column` covers a full-width table or list whose record opens on its own route | Material canonical layouts; GOV.UK layout |
| Grouping | for each section, the cue that separates it from its neighbours: distance, region, rule, in that order of preference | SmartHR ビジュアルグルーピング; NN/g common region |
| Constants and variables | what this screen shares with the product's other screens (shell, navigation, controls, scale) and what it decides for itself (dominant element, archetype, density, group sizes) | NN/g Jakob's Law; DADS layout; Müller |
| Omissions | each region or control of the kind that is left out, with the reason the request gives; then what else was left out so the rest keeps its visibility | NN/g heuristic 8 |
| Lead content (`lp` only) | what the reader sees first: the product itself, named, in place of a stock illustration or an abstract claim; a headline that a competitor could carry unchanged fails the swap test (research T15, T22) | research/20261030-ai-tells-ui/report.md T15, T22 |

A frequent reader with intermediate or expert knowledge gets the dense form and the frequent action within one click; a first-time or occasional reader gets fewer options and a guided path. Where `meta.users` records nothing for a screen, design for the intermediate. Aids written for a novice slow an expert down (the expertise reversal effect), so guidance is placed where the novice finds it and the expert passes it.

## The shell

A screen ships inside its product. A logo or the product name sits at the leading edge of the header on every production screen of every kind counted, so a built screen carries the same parts. `references/real-screens.md` gives their sizes per kind under "Every screen".

| Part | Holds | Where |
|---|---|---|
| Header | the logo file, or the product name as text when `meta.logo` is null, linking to the product's top | full width; 52px at the median on work tools, 64px on record screens, taller on consumer and public screens |
| Navigation | the product's sibling screens, the current one marked | links in the header (3 to 6 on work tools), or a left sidebar (282px at the median on work tools, on 7 of 14) |
| Account controls | the signed-in user's menu, or sign in and sign up on a public screen | the trailing end of the header |
| Footer | legal links and copyright | every consumer, pricing and landing screen; one line on 7 of 14 work-tool collections |

A sign-in or sign-up form is the exception production screens show: its header holds the logo or the name and at most one link, with no product navigation. Behind a sign-in, the account controls are the signed-in user's menu, and the screen is built with no footer unless the request shows one. Navigation lists the product's objects and the sibling screens the request names or implies; a request that implies none leaves the header with the product name and the account controls.

A navigation item or a create action whose view lies outside the build links to its route (the brief's `Controls` line). A fragment that renders inside another screen's shell carries none of these parts, and its plan says `Brand area: none`.

## Containers

A container goes where production screens of the kind draw one. `references/real-screens.md` names the enclosed regions of each kind; the table gives the rule across kinds.

| The content is | Container | Reason |
|---|---|---|
| A set of homogeneous records the reader scans or compares | a table, or a list when the reader scans by name, with a 1px rule between rows | rules between rows on 12 of 14 production work-tool collections; "Cards are also a poor choice when users need to compare between multiple options" (NN/g); 「データの比較や分析には、カード形式よりも行と列を使ったテーブルのほうが適しています」 (DADS) |
| A result with an image or several lines of metadata, in a browsed set | a row set apart by a rule or by distance; a card where the reader recognises the record by its image in a grid | consumer results: rules on 11 of 27, distance alone on 12 of 27, a box each on 4 of 27; NN/g; DADS; Material |
| A plan on a pricing page | a card per plan, or one container split into plan columns by rules | `references/real-screens.md`, Pricing page, Variants |
| A breakdown, a chart or a component group on a monitoring screen | a panel | panels around the sections on 6 of 15 production monitoring screens |
| The properties of a record beside its body | a rail of label and value pairs under small headings | a right rail on 13 of 18 production record screens |
| A sign-in or sign-up form | one centred card, or a column beside a picture | `references/real-screens.md`, Form, Variants |
| A section of the page | a heading and distance on the page ground | a card around every section on 0 of 14 work-tool collections, 1 of 12 forms and 0 of 24 pricing pages; SmartHR; NN/g common region |
| Two groups that still read as one | a rule | 「罫線は余白や矩形でグループを表現できない場合の最終手段として使います」 (SmartHR) |

Nesting follows what production screens show. A visible box inset in a visible box shows on 19% of them (a table in a panel, a plan card on a tinted band, a field group in a form card), and three boxes deep on 1%. R12 reports the second level as a NOTE and the third as a WARNING; a `Card` opened directly inside a `Card` is S11 in `scripts/check_slop.py`. A fill as wide as `<main>` is the page ground, wherever it is painted, and a `<dialog>` is its own surface and starts a new level.

A card that stands in for a table row, a panel around a single paragraph, or a border drawn where a larger gap would have grouped the same content compensates for a hierarchy the layout has not made.

This table settles which container a section gets. What the container carries (the slots of a row, a table, a card, a record's header, and their order and limits) is settled by a pattern from the library in `references/patterns.md`, chosen from the section's content by `scripts/patterns/resolve.py`.

## KPI tiles

The tile is the pattern `measure.tile.kpi` (`patterns/measure.tile.kpi.json`): a label, the value, one comparison, and an optional link to the records the figure counts. A tile exists when both hold:

1. its value is a quantity the reader monitors (a count, a rate, an amount); a category, a name or a date is a line in a list or a cell in a table;
2. it carries its comparison where it has one (a target, the previous period, a rank), because "quarter-to-date sales total $736,502 without any context means little" (Few). The comparison is part of the figure, so a mock's sample data supplies it.

A tile row belongs to a `monitor` screen: production screens show one on 3 of 15 monitoring screens and on none of the collections, forms and record screens counted. An `enter`, `lookup` or `record` screen carries none; one that needs a figure puts it in the heading or the filter bar, where 7 of 7 production work-tool collections that show a count put it. When a row exists, its tiles share one layout, because card dashboards tested well only with high consistency (Baymard). R15 reports a row of three or more equal figure tiles (on screen, on one line, the first starting in the top 40% of the viewport; each at most 160px tall, with at most six text entries and no image, and a figure as its largest text) on any screen whose plan is other than `monitor`. Calibrated on `research/20261106-real-screens`.

## Spacing and emphasis

- At least three spacing steps in use: within a group, between groups, between sections. Equal gaps everywhere erase proximity as a signal. R13 reports under three distinct gap values.
- At least three emphasis levels visible in the text of the main region: the dominant element, the headings, the body. R14 reports under three distinct size-and-weight pairs. The steps come from `typography.scale` in `tokens.json`; the plan decides which element gets the top step.
- "If your design is mostly regular, the elements that you do want to highlight will stand out better" (MIT 6.831, after Mullet and Sano): one scale, one radius per role, and the exceptions placed on purpose.
- Reading text for Japanese carries the measure `max-w-[40em]`: 640px at 16px, which is 40 full-width characters, and 39 with 0.02em tracking. This measure and the line height of 1.5 are the build defaults (WCAG 1.4.8, research E73 (ui-defaults)). The checks report only what real screens rarely show: R21 below 1.4 times the size, R22 above 60 full-width characters or 120 other characters per rendered line.

## Measured type and spacing

These rules run on the rendered dump. The entries that name a source are ported from impeccable 4.8.0 (Apache-2.0; see `THIRD_PARTY_NOTICES.md`). The text rules R1, R4, R7, R19, R21, R22 and R35 count text a reader can see (`scripts/render/visibility.py`):

- type above 1px, in an element wider and taller than 1px that has no `sr-only` class;
- a rect that meets the page, between 0 and the viewport width and below the top edge;
- an effective opacity above 0.05;
- a place outside every consent banner.

- **R21: leading of reading text.** A WARNING for a p, li, dd or blockquote of 16 to 18px with 2 or more lines and 50 or more characters in its subtree, weight under 600, outside controls, headings, navigation and fixed layers, whose line height is under 1.4 times its size. Real screens set reading text at 1.4 and up; 1.5 stays the build default. Calibrated on `research/20261106-real-screens`.
- **R22: line length of reading text.** A WARNING for a p, li, dd, blockquote or td of 14px and up with 2 or more lines, outside controls, preformatted text and fixed layers, whose widest rendered line holds more than 60 full-width characters (text with CJK) or 120 characters (other text). Calibrated on `research/20261106-real-screens`.

- **R30: crushed letter spacing.** A WARNING below -0.07em (-0.09em from 40px) on an element with more than 10 characters of its own text and more than 20 in its subtree, unless the text is CJK (CJK letters at least half of the letters). Source: impeccable `extreme-negative-tracking`. Not ported: nothing known.
- **R32: text under an element.** A WARNING when an `elementFromPoint` grid over the text lines finds 30% of the points under an opaque box (a background alpha above 0.6 or a background image), or 45% under other text on a layered element. Only the first viewport is probed, and only rendered text: its box and every ancestor's are over 2px wide and tall, `clip` and `clip-path` are unset, the effective opacity is above 0.02, and the text rect is clipped by every overflow ancestor. A point counts when an element ahead of the text in the `elementsFromPoint` stack covers it. Source: impeccable `text-occlusion`. Not ported: the card-overhang and inline-leak forms and the mockup downgrade.
- **R34: cramped padding.** A WARNING when both the padding and the measured space between a bordered or filled box and its own text are under max(4px, 0.3em) above and below, or under max(8px, 0.5em) beside. Add 8px or more, ideally 12 to 16. Source: impeccable `cramped-padding`. Not ported: the form where a wrapper sits flush against the box.
- **R35: body text at the viewport edge.** A WARNING when the rendered text of a p or li (over 40 characters, over half the viewport wide) sits under 16px, or under 12px at 480px and below, from the left or right edge, measured against the layout width with scrollbars hidden. A list item counts its marker only when one is drawn. Navigation, filled, positioned, clipped, screen-reader-only and fixed-bar text is exempt. Under 768px the check is skipped when the page scrolls sideways or its viewport meta lacks `width=device-width`. Source: impeccable `body-text-viewport-edge`. Not ported: the animation and scroller exemptions. Calibrated on `research/20261106-real-screens`.
- **R36: heading crowded against the block above.** A WARNING when two or more h2 to h4 have under 75% of the space below them, and 12px less, above them, or an even gap (within 0.5px) under a block that ends in running prose (80 characters on 2 lines or more, smaller than the heading, at most 1.25 times the body text, across half the heading's width); the space below is between 6 and 160px. An empty spacer block counts as space, and an eyebrow label directly above the heading belongs to the heading. Exempt: small cards, headings with their own top edge, and a block above that separates the heading (a rule, a picture, a bottom border drawn alone, a heading). Source: impeccable `heading-rhythm`. Not ported: runs of like boxes (accordion rows, cards) in the walks, shadow-DOM content, run-in headings beyond `display: inline`, the unpainted-heading test, the image-band tiling detail and the dark canvas colour.
- **R37: justified text.** A WARNING for `text-align: justify` without `hyphens: auto` in a wrapping column of 45 or fewer characters per line. CJK, Thai and Arabic are exempt. Source: impeccable `justified-text`. Not ported: the text-extent measure for inline elements (the box width is used).
- **R39: wide letter spacing.** A WARNING above 0.05em on an element with more than 10 characters of its own text and more than 20 in its subtree; uppercase labels (typed or transformed), single-line controls and CJK are exempt. Source: impeccable `wide-tracking`. Not ported: nothing known.
- **R4: clipped text.** A WARNING for rendered text cut by the edge of its box (overflow hidden or clip, no ellipsis, no line clamp, opacity above 0.02, text colour not transparent). Ellipsis truncation and a line clamp shorten text on purpose and give no finding.
- **R4 also** reports text that overflows its box by 16px or more and meets another box, probed after scrolling to the element (12 probes at most, scroll position restored), for rendered text only: its rect is clipped by every overflow ancestor and the element itself answers `elementsFromPoint` inside its own box. Source: impeccable `text-overflow`. Not ported: the clipping-ancestor and viewport-edge harms.
- **R21 also** reports text under 1.25 times its size (more than 10 own and 80 subtree characters, 3 lines or more counted on the rect of its own text, outside headings and their descendants, controls and fixed layers, from 9px up and under 24px). Lead text of 20 to 23px from 1.15 over 3 lines or fewer, bold text of weight 600 and up over 2 lines or fewer, uppercase labels and pre, code and samp are exempt. An element the reading rule R21 (16 to 18px body text) already flags gets only that finding. Source: impeccable `tight-leading`. Not ported: line-clamped titles, items that each fit one line, monospace pre-wrap runs outside pre, code and samp, the strut-based line pitch and visually hidden text.

## What the checks cover

| Rule | Check | Left to the reviewer |
|---|---|---|
| Enclosure nesting | S11 (source), R12 (rendered: a NOTE for a drawn box of 64x64 or more inset 4px or more inside another such box, a WARNING for three deep) | whether each enclosure is one the kind's production screens draw |
| Three spacing steps | R13 | whether the steps map to within, between and section |
| Three emphasis levels | R14 | whether the dominant element is the purpose |
| A tile row on `monitor` only | R15 (needs `--plan`; in a brief with one block per screen, the block whose heading carries the captured route in backticks, as `### 契約 \`/contracts\``, supplies the job class) | whether each tile is a monitored quantity with a comparison |
| Contrast | R1 on rendered text with a letter or digit: CRITICAL under 2:1, WARNING for text of 40 or more letters or digits under 2.5:1, NOTE for every other pair under the WCAG threshold | whether a quiet label is quiet on purpose |
| Overflow | R3: WARNING when the root scrolls sideways (and, under 768px, the viewport meta holds `width=device-width`); NOTE for a desktop-only document and for a 100vw element beside a classic scrollbar | whether the wide content is the product's own |
| Controls | R5 a NOTE for a rendered control under 24px (a WARNING under 16px beside another small control); R6 a WARNING for a rendered input with no label, no placeholder and no search role; R10 and R23 a NOTE per capture for rendered links | whether a link name predicts its destination |
| Headings | R8 over rendered headings: a WARNING when no h1 and no h2 is rendered; a NOTE for an h1 count other than 1 or a skip of two levels | whether the hierarchy mirrors the content |
| Type | R7 on rendered text (CRITICAL, unchanged), R19 a NOTE on a `ja` page and a WARNING on a page whose `lang` is not `ja` | whether the small text carries anything the reader needs |
| Reader fit | T18 requires `meta.users` | which recorded fact justifies each structural choice |
| Labels | C18 to C21 | whether a label predicts its destination in the reader's words |

The eight cold-read questions in `assets/brief.template.md` carry the rest to P2 of the review, answered from the screenshot before the dump is read.

## Sources

| Source | What it settles here |
|---|---|
| S. Few, [Common Pitfalls in Dashboard Design](https://www.perceptualedge.com/articles/Whitepapers/Common_Pitfalls.pdf) (2006) | the dashboard as one screen; equal prominence as failure; a figure without a comparison; rank among measures |
| S. Few, [Effectively Communicating Numbers](https://www.perceptualedge.com/articles/Whitepapers/Communicating_Numbers.pdf) (2005) | tables for lookup and precise values |
| Nielsen Norman Group, [Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/) (2021) | "If everything is contrasted, then nothing stands out"; the squint test |
| Nielsen Norman Group, [10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | heuristic 8: every extra unit of information competes with the relevant ones |
| Nielsen Norman Group, [The Principle of Common Region](https://www.nngroup.com/articles/common-region/) (2020) and [Proximity Principle](https://www.nngroup.com/articles/gestalt-proximity/) (2020) | enclosure as a grouping cue; a border only when whitespace cannot group |
| Nielsen Norman Group, [Cards: UI-Component Definition](https://www.nngroup.com/articles/cards-component/) (2016) | cards for heterogeneous browsed items; lists and tables for scanning and comparison |
| Nielsen Norman Group, [Flexibility and Efficiency of Use](https://www.nngroup.com/articles/flexibility-efficiency-heuristic/) (2020) and [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) (2006) | role-based differentiation; guidance for the novice placed where the expert passes it |
| Nielsen Norman Group, [Website Forms Usability](https://www.nngroup.com/articles/web-form-design/) (2016) | one column for data entry |
| Nielsen Norman Group, [Jakob's Law](https://www.nngroup.com/videos/jakobs-law-internet-ux/) (2017) | sameness in conventions users learn once |
| MIT 6.831, [Lecture 11 notes](https://groups.csail.mit.edu/graphics/classes/6.831/lectures/L11.pdf) (2004), after K. Mullet and D. Sano, Designing Visual Interfaces (1995) | contrast as meaningful irregularity on a regular base; white space for grouping |
| S. E. Palmer, [Perceptual Grouping: It's Later Than You Think](https://palmerlab.berkeley.edu/pdf/Palmer.pdf), Current Directions in Psychological Science 11(3) (2002) | common region as a grouping principle |
| B. Shneiderman, [The Eyes Have It](https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf) (1996) | overview first, then zoom and filter, then details on demand |
| B. Shneiderman, [Eight Golden Rules](https://www.cs.umd.edu/~ben/goldenrules.html) | shortcuts for frequent users |
| S. Kalyuga, [Expertise Reversal Effect](https://www.uky.edu/~gmswan3/EDC608/Kalyuga2007_Article_ExpertiseReversalEffectAndItsI.pdf), Educational Psychology Review 19 (2007) | aids for novices degrade expert performance |
| ISO 9241-11:2018 ([preview](https://preview.sist.si/sist-preview/63500/33c267a5a7564f298f02bbd65721a181/ISO-9241-11-2018.pdf)) | user group, context of use |
| Baymard Institute, [cards dashboard layout](https://baymard.com/blog/cards-dashboard-layout) (2018) | card dashboards need consistent tiles |
| R. Sarikaya et al., [What Do We Talk About When We Talk About Dashboards?](https://tableau.com/sites/default/files/2023-01/DashboardsConspiracy_final.pdf), IEEE TVCG 25(1) (2019) | the tiled dashboard as a genre |
| デジタル庁デザインシステム [カード](https://design.digital.go.jp/dads/components/card/), [レイアウト](https://design.digital.go.jp/dads/foundations/layout/) | a card holds one subject; tables for comparison; consistent layouts aid learning |
| SmartHR Design System [ビジュアルグルーピング](https://smarthr.design/products/design-patterns/visual-grouping/), [視線誘導](https://smarthr.design/products/design-patterns/visual-guidance/), [Base](https://smarthr.design/products/components/base/) | distance, region, rule in that order; priority at the top; no Base on Base |
| Apple, [Human Interface Guidelines: Layout](https://developer.apple.com/design/human-interface-guidelines/layout) | order by importance; top and leading edge |
| Android Developers, [Canonical layouts](https://developer.android.com/develop/adaptive-apps/guides/canonical-layouts) | list-detail, supporting pane, feed |
| GOV.UK Design System, [Layout](https://design-system.service.gov.uk/styles/layout) and [One thing per page](https://designnotes.blog.gov.uk/2015/07/03/one-thing-per-page/) (2015) | two-thirds layouts; one question per page |
| GOV.UK Design System backlog, [Card #113](https://github.com/alphagov/govuk-design-system-backlog/issues/113) (2018) | cards as compensation for weak hierarchy |
| Shopify Polaris, [Page](https://shopify.dev/docs/api/app-home/polaris-web-components/structure/page) | one primary action per page |
| B. Müller, [Why Do All Websites Look the Same?](https://borism.medium.com/on-the-visual-weariness-of-the-web-8af1c969ce73) (2018) | templates carry no content decision (opinion) |

Mullet and Sano, Tufte and Few's books were read through secondary copies; no source tests a row of equal tiles against a ranked row directly. The thresholds in R13 to R15 are this skill's own, set from the grade B guidance above.
