# Composition

Source of record for the composition plan a screen gets before any markup, for the container rule, for the KPI tile rule, and for the measured checks R12 to R15 in `scripts/render/check_render.py`. Read it at Step 3 of `SKILL.md` before the first element is placed, and when R12 to R15, S11 or C18 to C21 fire.

## What it settles

A screen reads as designed when a viewer recovers the rank of its parts at a glance: what it is for, what dominates, in what order it is read, and what belongs together. The element-level checks (colours, fonts, string existence, text size) leave that rank unsettled, and a screen of equal panels passes every one of them. "If everything is contrasted, then nothing stands out" (Nielsen Norman Group); "because everything in this dashboard is visually prominent and vying for your attention, nothing in particular grabs your attention. When this happens the dashboard has failed" (Stephen Few).

Three mechanisms carry the rank, and each has a check or a reviewer question:

| Mechanism | Carried by | Where it is judged |
|---|---|---|
| Emphasis | size, weight and position in steps a viewer can tell apart; one dominant element | R14; cold-read questions 1 to 4 |
| Grouping | distance first, a filled region second, a rule last; one enclosure level | R12, R13, S11; cold-read question 5 |
| Density | the job the screen does for its reader: monitor, enter, look up, decide | the plan's job class; R15; cold-read question 8 |

Sameness is right in what users learn once and reuse: the shell, the navigation, the tokens, the control forms, and the choice among a short list of layout archetypes. Sameness is the defect when it replaces the decision about this screen's content: the same tile row and the same panel grid on every screen, whoever reads it and whatever the job.

## The plan

Write one plan per screen into the Composition section of `ui-brief.md` (`assets/brief.template.md`) before any markup. The reviewer in Step 5 conforms the rendered screen to it.

| Decision | Write | Source |
|---|---|---|
| Purpose | one phrase: what the reader gets from this screen | Few |
| Job class | `monitor` (glance at measures), `enter` (give the product data), `lookup` (find or compare records), `decide` (choose between options) | Few; Shneiderman 1996; GOV.UK |
| Reader | the group from `meta.users` this screen serves, with its frequency and expertise | ISO 9241-11 |
| Dominant element | the one element the eye lands on first, and why it is the purpose; then the second | NN/g hierarchy; Polaris |
| Reading order | three to five stops, top and leading edge first | Apple HIG; SmartHR 視線誘導 |
| Density | from the job class: `monitor` is one screen with no scrolling at 1280; `enter` is one column with one question group per step; `lookup` is dense rows behind an overview or a filter; `decide` puts the comparison first | Few; GOV.UK; NN/g forms; Shneiderman 1996 |
| Archetype | `list-detail`, `supporting-pane`, `feed`, `single-column`, `dashboard` | Material canonical layouts; GOV.UK layout |
| Grouping | for each section, the cue that separates it from its neighbours: distance, region, rule, in that order of preference | SmartHR ビジュアルグルーピング; NN/g common region |
| Constants and variables | what this screen shares with the product's other screens (shell, navigation, controls, scale) and what it decides for itself (dominant element, archetype, density, group sizes) | NN/g Jakob's Law; DADS layout; Müller |
| Omissions | what was left out so the rest keeps its visibility | NN/g heuristic 8 |

A frequent reader with intermediate or expert knowledge gets the dense form and the frequent action within one click; a first-time or occasional reader gets fewer options and a guided path. Where `meta.users` records nothing for a screen, design for the intermediate. Aids written for a novice slow an expert down (the expertise reversal effect), so guidance is placed where the novice finds it and the expert passes it.

## Containers

| The content is | Container | Reason |
|---|---|---|
| A set of homogeneous records the reader scans or compares | a table; a list when the reader scans by name | "Cards are also a poor choice when users need to compare between multiple options" (NN/g); 「データの比較や分析には、カード形式よりも行と列を使ったテーブルのほうが適しています」 (DADS) |
| One conceptual unit in a browsed set of heterogeneous items, or an object recognised by its image | a card | NN/g; DADS; Material |
| A section of the page | a heading and distance on the page ground | SmartHR; NN/g common region |
| A section that distance cannot separate, or that holds sub-groups | one region: a filled or bordered panel | SmartHR; NN/g |
| Two groups that still read as one | a rule, as the last resort | 「罫線は余白や矩形でグループを表現できない場合の最終手段として使います」 (SmartHR) |

One enclosure level. The page ground is the outer level, and a panel on it is the inner one; a chart or a table inside a panel is that one level. A panel inside a panel is S11 in `scripts/check_slop.py` and R12 at review. A `<dialog>` is its own surface and starts a new level.

A card that stands in for a table row, a panel around a single paragraph, or a border drawn where a larger gap would have grouped the same content compensates for a hierarchy the layout has not made.

## KPI tiles

A tile exists when all three hold:

1. its value is a quantity the reader monitors (a count, a rate, an amount); a category, a name or a date is a line in a list or a cell in a table;
2. it carries one comparison (a target, the previous period, a rank), because "quarter-to-date sales total $736,502 without any context means little" (Few);
3. the row has a dominant tile, by size or by position, because "not all data are equally important" (Few).

A tile row belongs to a `monitor` screen. An `enter` or `lookup` screen carries none by default; one that needs a figure puts it in the heading or the filter bar. When a row exists, its tiles share one layout, because card dashboards tested well only with high consistency (Baymard). R15 reports a row of three or more equal numeric tiles on any screen whose plan is other than `monitor`.

## Spacing and emphasis

- At least three spacing steps in use: within a group, between groups, between sections. Equal gaps everywhere erase proximity as a signal. R13 reports under three distinct gap values.
- At least three emphasis levels visible in the text of the main region: the dominant element, the headings, the body. R14 reports under three distinct size-and-weight pairs. The steps come from `typography.scale` in `tokens.json`; the plan decides which element gets the top step.
- "If your design is mostly regular, the elements that you do want to highlight will stand out better" (MIT 6.831, after Mullet and Sano): one scale, one radius per role, and the exceptions placed on purpose.

## What the checks cover

| Rule | Check | Left to the reviewer |
|---|---|---|
| One enclosure level | S11 (source), R12 (rendered) | whether the one region is the right cue |
| Three spacing steps | R13 | whether the steps map to within, between and section |
| Three emphasis levels | R14 | whether the dominant element is the purpose |
| A tile row on `monitor` only | R15 (needs `--plan`) | whether each tile is a monitored quantity with a comparison |
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
