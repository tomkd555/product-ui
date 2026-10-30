# SQ1: What makes a whole screen read as designed (collector report, 2026-10-07)

Collector: a Sonnet research agent with WebSearch and WebFetch. Quotes marked † were read from the fetched document; unmarked quotes came back through a summarising fetch tool and were re-checked against the page only where the report says so.

## Answer

A screen reads as designed when a person chose the rank of its parts and the viewer can recover that rank in under a second. Visual hierarchy means "guiding the eye on the page so that it attends to different design elements in the order of their importance" (S6). Contrast is "the irregularity in a design that communicates information or makes elements stand out" (S2). When every part is equally prominent, that signal is gone. Few's dashboard case states the result: "everything in this dashboard is visually prominent and vying for your attention, nothing in particular grabs your attention. When this happens the dashboard has failed" (S5). NN/g gives the same mechanism for similarity ("same-color buttons will be perceived as sharing the same level of importance", S8) and for content ("every extra unit of information in an interface competes with the relevant units", S10). Uniform spacing removes the second code, proximity, which tells the viewer what belongs together (S9, S29, S2, S24).

Sameness helps in the parts that users learn once and reuse. Jakob's Law, the Digital Agency layout guidance, Material's canonical layouts and the GOV.UK page templates all support a small, fixed set of layouts and conventions (S32, S30, S26, S27). Sameness hurts when the content, purpose and density of a screen are left out of the decision. Müller calls templates "content agnostic. And that is the problem" (S19). Few says the arrangement must fit "the way it's used" (S5). The MIT notes combine both views: "if your design is mostly regular, the elements that you do want to highlight will stand out better" (S2). The working position is a regular base and deliberate, ranked exceptions.

Where the evidence ends: the empirical papers (S13, S14, S15) study first impressions of whole websites; perceived visual complexity and category typicality drive appeal in them. No source tests "equal-weight tiles" or product screens directly, so applying them to product screens is inference. The sources on AI-made screens at whole-page level (S22 to S24) are risk analyses and practitioner blogs about landing pages.

## A composition plan the sources justify

1. Purpose and reader task: one sentence names the screen's job (monitor, enter data, look up or compare, decide). S5, S29, S36.
2. Dominant element, then second, then the rest. S28 ("no more than one primary action and 3 secondary actions per page"), S25 ("Order content by relative importance"), S5, S1 ("Insufficient Contrast", "Dominant Secondary Elements").
3. Reading order: three to five stops; leading and top positions carry the highest rank. S25, S29, S5, S11.
4. Which visual variables carry the rank and how many steps: "multiplicative scaling, not additive" (S2); "Don't compose without a scale" (S18); only as many heading levels as needed (S18).
5. Grouping method: proximity first, a filled region second, rules last. S29, S25, S2.
6. Density class by task and user: monitoring = one screen at a glance (S5); data entry = one thing per page or a single column (S27, S33); lookup or compare = dense rows behind an overview (S36, S34).
7. Layout archetype from a short list: list-detail, supporting pane, feed, single-column question page, dashboard. S26, S27, S29.
8. Constants and variables across the product: constants are chrome, navigation, tokens, scale steps, control forms (S32, S30, S2); variables are the dominant element, the archetype, the density and the group sizes (S19, S5). Bringhurst: variations "can and should add life to the page, but the main text should also return after each variation precisely on beat" (S18).
9. Spacing scale with three or more distinct steps for within-group, between-group and between-section gaps. S29, S9, S24 ("Equal gaps everywhere make it hard to tell what belongs together").
10. Omissions: what is cut so the remaining parts keep their relative visibility. S10, S2.

## Cold-read questions the sources justify

1. Name the element the eye lands on first. Is it the screen's purpose? (S6, S5, S28)
2. Blur or squint at the image. Count the distinct levels of emphasis that survive; under three is a finding. (S7, S2)
3. List the first four things you look at, in order. Does that order match a task someone would do here? (S25, S29, S11)
4. Count the elements of equal size, weight and fill. Say why each one earns that equality. (S5, S8, S24)
5. Point at the groups. Which cue separates them? Are gaps between groups visibly larger than gaps within them? (S9, S29, S2)
6. Does the screen contain a run of identical tiles followed by identical panels? Would reordering them change meaning? (S19, S24)
7. Name the screen's job in one phrase. Does the density fit that job? (S5, S33, S34)
8. Does the screen fit one of the layout archetypes? Which pane or region is primary? (S26, S27)
9. Is there a clear difference in size, value or position between the primary and secondary controls? (S28, S2)
10. Cover the labels. Could this be the screen of a different product, or a different screen of the same product? (S19, S21)
11. Which things are identical to the product's other screens, and which differ? Does that split follow the constants-and-variables rule? (S32, S18)
12. Is anything present whose removal would raise the visibility of the rest? (S10)

## Rules the sources support

1. Name one dominant element per screen, the element that carries the screen's purpose. [S5, S6, S28]
2. Use at least three visibly distinct levels of emphasis. [S5, S7, S8]
3. Make rank differences sharp: multiplicative size steps and redundant coding for the dominant element. [S2] (single source)
4. Draw sizes from a fixed scale. Add heading levels only as needed. [S18]
5. Place highest-ranked content at the top and leading edge, and treat reading order as a design decision. [S25, S29, S11]
6. Express relatedness through distance first, a filled region second, and a rule last. [S29, S2, S25, S9]
7. Use at least three spacing steps mapped to within-group, between-group and between-section. [S9, S29, S24 (opinion)]
8. Limit primary actions to one per page, with a small number of secondary actions. [S28] (single source)
9. Let every extra element prove its worth. [S10, S2]
10. Pick density by the screen's task and the user's expertise. [S5, S33, S34, S36, S35 (opinion)]
11. Start data-entry flows with one thing per page or a single column. [S27, S33]
12. Choose the layout from a short list of archetypes and fill it with the screen's own content. [S26, S27, S29]
13. Keep chrome, navigation, tokens and control forms constant across screens. [S32, S30, S2]
14. Vary composition (dominant element, archetype, density, group sizes) with the content. [S19, S5, S18]
15. Treat a grid as a tool that still needs judgment: "The grid system is an aid, not a guarantee" (S17). [S17, S37; S17 is secondary]
16. Tufte's density principle, "the greatest number of ideas in the shortest time with the least ink in the smallest space", makes density acceptable when structure carries it. [S16, S35 (opinion)]
17. Cap total visual complexity, because complexity shapes first impressions within 50 ms. [S13, S14] (inference from website homepage studies)

## Evidence table

| # | Claim | Source | URL | Published | Grade | Verbatim quote |
|---|---|---|---|---|---|---|
| S1 | Named pitfalls per chapter; "uniform weight" is not among them | Mullet and Sano, Designing Visual Interfaces (table of contents via GUIdebook) | https://guidebookgallery.org/books/designingvisualinterfaces/ | 1995 | B | "Haphazard Layout," "False Structure," "Excessive Display Density"; "Insufficient Contrast"; "Dominant Secondary Elements"; "Random Window Sizes and Layouts," "Inconsistent Visual Language"; "Unwarranted Innovation" |
| S2 | Contrast is meaningful difference; regularity makes exceptions stand out; white space groups | MIT 6.831 Lecture 11 notes, citing Mullet and Sano | https://groups.csail.mit.edu/graphics/classes/6.831/lectures/L11.pdf | 2004 | B | †"Contrast is the irregularity in a design that communicates information or makes elements stand out." †"if your design is mostly regular, the elements that you do want to highlight will stand out better." †"Use white space for grouping, instead of lines." †"Multiplicative scaling, not additive" |
| S3 | Review of the book | Kolli, SIGCHI Bulletin 28(2) | https://homepages.cwi.nl/~steven/sigchi/bulletin/1996.2/book-review.html | 1996-04 | B | "reduction, regularisation, alignment, optical adjustment, repetition, selection, refinement, generalisation." |
| S4 | Foreword | Nielsen, foreword to Mullet and Sano | https://www.nngroup.com/articles/foreword-visual-design/ | 1994-05-01 | B | "Good graphic design can significantly improve the communicative value of the interface, leading to increased usability." |
| S5 | Everything prominent produces no focus; arrangement follows importance and use; dashboard definition | Few, Perceptual Edge, Common Pitfalls in Dashboard Design | https://www.perceptualedge.com/articles/Whitepapers/Common_Pitfalls.pdf | 2006-02 | B | †"because everything in this dashboard is visually prominent and vying for your attention, nothing in particular grabs your attention. When this happens the dashboard has failed." †"all the data is equally bold and colorful, leaving us with a wash of sameness and no clue where to focus." †"The most important data ought to be prominent." †"A dashboard is a visual display of the most important information needed to achieve one or more objectives; consolidated and arranged on a single screen so the information can be monitored at a glance." |
| S6 | Visual hierarchy, scale, balance, contrast defined | NN/g, Visual Design Principles | https://www.nngroup.com/articles/principles-visual-design/ | 2020-03-01 | B | "Guiding the eye on the page so that it attends to different design elements in the order of their importance." |
| S7 | Squint test | NN/g, Visual Hierarchy in UX | https://www.nngroup.com/articles/visual-hierarchy-ux-definition/ | 2021-01-17 | B | "In design school, we are taught to squint or apply a slight blur to the design to get an idea of the conveyed groupings and hierarchy." |
| S8 | Same appearance reads as same importance | NN/g, Similarity Principle | https://www.nngroup.com/articles/gestalt-similarity/ | 2020-09-06 | B | "same-color buttons will be perceived as sharing the same level of importance" |
| S9 | Proximity groups | NN/g, Proximity Principle | https://www.nngroup.com/articles/gestalt-proximity/ | 2020-08-02 | B | "Items close together are likely to be perceived as part of the same group" |
| S10 | Extra information competes | NN/g, 10 Usability Heuristics | https://www.nngroup.com/articles/ten-usability-heuristics/ | rev. 2024-01-30 | B | "Every extra unit of information in an interface competes with the relevant units of information and diminishes their relative visibility." |
| S11 | Scanning depends on layout | NN/g, Text Scanning Patterns | https://nngroup.com/articles/text-scanning-patterns-eyetracking/ | 2019-08-25 | B | "How people read on the web is highly contingent upon: Their task, … The page layout, The type of page content" |
| S12 | F-pattern | NN/g, F-Shaped Pattern | https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/ | 2006-04-16 | B | "The first two paragraphs must state the most important information." |
| S13 | Complexity and prototypicality shape first impressions | Tuch et al., IJHCS 70(11) | https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/38315.pdf | 2012 | A | †"Overall, websites with low VC and high PT were perceived as highly appealing." †"people prefered novel designs only as long as the novelty did not affect prototypicality" (Hekkert et al., cited) |
| S14 | Complexity and colorfulness predict appeal | Reinecke et al., CHI 2013 | https://kgajos.seas.harvard.edu/papers/reinecke13aesthetics.pdf | 2013-04 | A | †"Users make lasting judgments about a website's appeal within a split second of seeing it for the first time." |
| S15 | Judgments in 50 ms | Lindgaard et al. 2006 via websiteoptimization.com | https://www.websiteoptimization.com/speed/tweak/blink/ | 2006-01-17 | C (secondary of A) | "Web users form first impressions of web pages in as little as 50 milliseconds" |
| S16 | Tufte on arrangement and density | Tufte, Envisioning Information via course notes | https://faculty.cc.gatech.edu/~stasko/7450/16/Notes/tufte.pdf ; https://publish.uwo.ca/~pazner/180/lecture4.html | 1990 (book) | C (secondary) | "it is not how much information there is, but rather how effectively it is arranged" (p. 50); "Clutter and confusion are failures of design, not attributes of information" (p. 51) |
| S17 | Grid is a tool | Müller-Brockmann via Goodreads | https://www.goodreads.com/work/quotes/341206 | 1981 (book) | C (secondary) | "The grid system is an aid, not a guarantee." |
| S18 | Scale, rhythm, heading levels | Bringhurst, The Elements of Typographic Style (PDF copy) | https://literature.wolkersdorfer.info/literature/The%20Elements%20of%20Typographic%20Style.pdf | edition unstated | B | †"3.1.1 Don't compose without a scale." †"4.2.2 Use as many levels of headings as you need: no more and no fewer." |
| S19 | Templates carry no design decisions | Müller, Medium, Why Do All Websites Look the Same? | https://borism.medium.com/on-the-visual-weariness-of-the-web-8af1c969ce73 | 2018-09-15 | C | †"Templates are not designs. Rather, they are rules for combining related data types." †"templates are content agnostic. And that is the problem." |
| S20 | Layout homogenization measured | Goree et al. via The Conversation | https://theconversation.com/yes-websites-really-are-starting-to-look-more-similar-136484 | 2020-05-06 | B | "Layout differences decreased the most, declining over 30% in that time frame" |
| S21 | Convergence has causes and benefits | Ström-Awn, The inevitable same-ification of the internet | https://mattstromawn.com/writing/sameification/ | undated | C | "Deviations from a learned routine lead to user errors." |
| S22 | LLM defaults flatten design | Shin et al., Interrogating Design Homogenization in Web Vibe Coding, arXiv 2603.13036 | https://arxiv.org/pdf/2603.13036 | 2026-03-13 | preprint | †"[the LLM] can probabilistically default to the same familiar patterns—generic layouts, standard component libraries, and a clean, but non-distinctive, professional veneer." †"The models justified a minimalist layout (right) as a cultural preference, thereby overriding the preference for high information density in Japanese web design" |
| S23 | Uniform spacing and radius as a tell | 925Studios, AI Slop Web Design | https://www.925studios.co/blog/ai-slop-web-design-guide | 2026-03-19 | C | "AI-built sites tend to use identical padding, identical border radius, and identical card heights throughout." |
| S24 | Layout tells in AI output | impeccable.style, slop catalog | https://impeccable.style/slop | undated | C | "Repeated icon, heading, and text cards give every point the same weight." "Equal gaps everywhere make it hard to tell what belongs together." |
| S25 | Order by importance, group, disclose progressively | Apple HIG, Layout | https://developer.apple.com/design/human-interface-guidelines/layout | undated | B | †"Order content by relative importance. … place the most important items near the top and leading side of the window or display." |
| S26 | Canonical layouts | Android Developers, Canonical layouts | https://developer.android.com/develop/adaptive-apps/guides/canonical-layouts | 2026-09-22 | B | "the primary display area occupies about two-thirds of the app window" |
| S27 | Layout and one thing per page | GOV.UK Design System layout; question pages; Design Notes | https://design-system.service.gov.uk/styles/layout ; https://design-system.service.gov.uk/patterns/question-pages/ ; https://designnotes.blog.gov.uk/2015/07/03/one-thing-per-page/ | 2015-07-03 (blog) | B | "Asking just one question per question page helps users understand what you're asking them to do" |
| S28 | Page actions | Shopify Polaris, Page | https://shopify.dev/docs/api/app-home/polaris-web-components/structure/page | undated | B | "Include no more than one primary action and 3 secondary actions per page." |
| S29 | Japanese design-pattern guidance | SmartHR Design System (視線誘導, 視覚的グルーピング, ページレイアウト, 余白の取り方) | https://smarthr.design/products/design-patterns/visual-guidance/ ; …/visual-grouping/ ; …/page-layout/ ; …/spacing-layout-pattern/ | undated | B | 「優先度が高い情報は、上部に配置する」「ユーザーの利用目的に沿って、オブジェクトの関係性や重要度を表すように設計してください」「関連の深い要素同士ほど近接させ、関連の薄い要素とはそれよりも大きな距離を取ることで要素のまとまりを示します。」「罫線は余白や矩形でグループを表現できない場合の最終手段」 |
| S30 | Layout consistency | デジタル庁 デザインシステム レイアウト | https://design.digital.go.jp/dads/foundations/layout/ | 2024-07-31 | B | 「一貫性のあるレイアウトは、学習効率を高め、ページの閲覧やサイト内の回遊を促進し、ユーザー体験を向上させます。」 |
| S31 | Views placed to reflect the interaction layer | 上野学, design process of OOUI; gihyo.jp book message | https://speakerdeck.com/uenitty/design-process-of-ooui ; https://gihyo.jp/book/2026/978-4-297-15716-6/content/message | 2020-09-30 | B/C | 「インタラクション層を反映するようにビューを配置して、ユーザーが実際に目にする画面を構成する」 |
| S32 | Jakob's Law | NN/g video; Laws of UX | https://www.nngroup.com/videos/jakobs-law-internet-ux/ ; https://lawsofux.com/jakobs-law/ | 2017-08-18 | B | "users prefer your site to work the same way as all the other sites they already know." |
| S33 | Forms use a single column | NN/g, Website Forms Usability | https://www.nngroup.com/articles/web-form-design/ | 2016-05-01 | B | "Multiple columns interrupt the vertical momentum of moving down the form." |
| S34 | Density depends on audience | Ström-Awn, UI Density | https://mattstromawn.com/writing/ui-density/ | undated | C | "UI density is the value a user gets from the interface divided by the time and space the interface occupies." |
| S35 | Density and clarity | Davis, WebdesignerDepot | https://webdesignerdepot.com/density-vs-clarity-the-core-tension-in-modern-ui-design/ | 2026-01-26 | C | "Clarity comes from meaningful structure, not from emptiness." |
| S36 | Overview first | Shneiderman, The Eyes Have It | https://drum.lib.umd.edu/items/155a868e-fb83-4115-9899-9187ea8c0498/full | 1996 | A | "Overview first, zoom and filter, then details-on-demand." |
| S37 | Grid achieves alignment and balance | MIT 6.813/6.831 Spring 2017, Layout | https://web.mit.edu/6.813/www/sp17/classes/14-layout/ | 2017 | B | "Establish a hierarchy of importance among items in the design" |

## Falsifier results

- Jakob's Law (S32) supports sameness in navigation, conventions and control behaviour and says nothing about equal weight inside a screen.
- Design-system layouts (S26, S27, S30) recommend a small set of standard layouts, each naming a primary region; they reduce the choice of archetype and leave the dominant element open.
- Prototypicality (S13) measures typicality within a site category; it does not measure repetition of one template across the screens of one product.
- Homogenization research (S20, S21) reports the trend and a learnability benefit, without judging outcome quality.
- Regularity inside a screen (S2) is the strongest nuance: a regular base makes the exceptions readable. The conclusion is a regular base with deliberate exceptions.
- No source shows that a screen of equal-weight tiles is easier to use than one with a ranked hierarchy.

## Gaps

- Mullet and Sano full text was lending-only; chapter and pitfall names come from a table of contents, sentences from course notes.
- Lindgaard 2006 primary text returned 403.
- Miniukovich and De Angeli were not opened.
- Goree et al. CHI 2021 full paper redirected; the authors' own summary was used.
- Tufte, Müller-Brockmann and Bringhurst reached through secondary copies or an unconfirmed edition.
- Atlassian layout guidance returned empty; Material 3 returned 404 and the Android Developers mirror was used.
- No Japanese academic text on 画面全体の構成 by a credible author surfaced.
- Only S22 is academic on AI-made screens, and it argues from risk analysis.
