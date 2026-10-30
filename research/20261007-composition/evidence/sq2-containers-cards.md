# SQ2: When a card is the right container (collector report, 2026-10-07)

Collector: a Sonnet research agent with WebSearch and WebFetch.

## Answer

A card is justified when the content is one conceptual unit (single subject, short, usually linked) and the unit sits in a collection of heterogeneous items that people browse. NN/g, Material, DADS and Baymard agree on this. Homogeneous records that need scanning, searching or comparison go in a list or table. Precise values go in a table (NN/g, DADS, Few). Relationships inside one screen are shown by proximity first, enclosure second, rules last (SmartHR, NN/g). The mechanism is perceptual: enclosure is a strong grouping cue (Palmer's common region), so each box asserts "these belong together" and takes visual weight. Many equal boxes dilute that signal and flatten hierarchy (NN/g visual hierarchy, Few pitfall #10). Nested boxes add noise without information (Tufte layering, SmartHR, GOV.UK panel). The sources split on one point: dashboards built from tiles are a recognised genre (Sarikaya 2019), and Baymard found card dashboards effective when cards were consistent. The defensible rule is "tiles earn their place by hierarchy, context and a real unit of content", with no general ban on tiles.

## Rules the sources support

1. Use a card for one conceptual unit: a few short, related pieces of information that act as a linked, short representation of a single subject. [S1, S3, S4, S9]
2. Use cards for collections of heterogeneous items that users browse. [S1, S7]
3. Use a list when items are homogeneous or users search or scan for a particular item. [S1]
4. Use a table when users compare options or attributes. [S1, S4, S6]
5. Use a table when the reader looks up individual values or needs precise values. [S6]
6. Group by proximity first; add a rectangle only when spatial layout prevents proximity grouping or when the group holds sub-groups; treat rules and borders as a last resort. [S5, S10]
7. Add a border or box only after asking whether whitespace alone could convey the grouping. [S10]
8. Do not nest enclosures; use spacing, type and dividers inside a surface. [S5, S11, S17]
9. An enclosure is a strong, automatic grouping cue, so box only content that is related. [S2] (inference)
10. Competing grouping cues weaken grouping. [S12] (inference when applied to UI)
11. Treat boxes, rules and decoration as non-data ink to be minimised; adjacent elements create "1 + 1 = 3" noise. [S13] (Tufte via secondary)
12. On an overview screen, create one dominant focal item; "if everything is contrasted, then nothing stands out". [S8, S14, S16]
13. Give every KPI context (target, history, comparison). [S14]
14. Fit a dashboard to a single screen; splitting the big picture into small separate pictures blocks comparison. [S14, S15, S19]
15. Follow overview first, then zoom and filter, then details on demand. [S15]
16. Treat a card as a smell when it compensates for weak information hierarchy or content design. [S3]
17. When cards are used, apply them with high consistency. [S7]
18. Make the whole card a single large tap target on touch screens. [S18]
19. Offer card-like containers as composable primitives. [S20] (single source)
20. Cards carry a recognisable AI-sameness signature: equal icon-heading-text grids, nested cards, uniform radii. [S21, S22, S23] (opinion)
21. Do not use cards as a substitute for table rows. [S24] (search snippet only)

## Evidence table

| # | Claim | Source | URL | Published | Grade | Verbatim quote |
|---|---|---|---|---|---|---|
| S1 | Cards suit heterogeneous browsing; lists beat cards for scanning and comparison | Laubheimer, NN/g, Cards: UI-Component Definition | https://www.nngroup.com/articles/cards-component/ | 2016-11-06 | B | "Cards work best for collections of heterogeneous items (i.e. not all the content is of the same basic type)." "Card layouts are less scannable than lists." "Cards are also a poor choice when users need to compare between multiple options, since cards often aren't structured in a predictable way from item to item." |
| S2 | Elements in the same bounded area group together | Palmer, Current Directions in Psychological Science 11(3) | https://palmerlab.berkeley.edu/pdf/Palmer.pdf | 2002-06 | A | "According to the principle of common region, elements that lie within the same bounded area tend to be grouped together, as the spots of a leopard are grouped within its contours (Palmer, 1992)." |
| S3 | Cards often compensate for weak hierarchy | GOV.UK Design System backlog #113, review-panel note | https://github.com/alphagov/govuk-design-system-backlog/issues/113 | 2018-02-15 | B | "There were concerns that cards are often used to compensate for poor information hierarchy or content design." |
| S4 | A card is a single-subject container; comparison goes to tables | デジタル庁デザインシステム カード | https://design.digital.go.jp/dads/components/card/ | undated | B | 「カードは、単一の主題に関するコンテンツをまとめて表示するコンテナとなるコンポーネント」「データの比較や分析には、カード形式よりも行と列を使ったテーブルのほうが適しています。」 |
| S5 | Grouping order: whitespace, rectangle, rules | SmartHR Design System ビジュアルグルーピング | https://smarthr.design/products/design-patterns/visual-grouping/ | undated | B | 「罫線は余白や矩形でグループを表現できない場合の最終手段として使います。」「大きな面積で領域を強く区切る意匠であるため、過度な使用は画面を冗長で複雑にします。」 |
| S6 | Tables serve lookup and precise values | Few, Effectively Communicating Numbers | https://www.perceptualedge.com/articles/Whitepapers/Communicating_Numbers.pdf | 2005-11 | B | "Tables work best when the display will be used to look up individual values or the quantitative values must be precise." |
| S7 | Card dashboards work when consistent | Baymard Institute, cards dashboard layout | https://baymard.com/blog/cards-dashboard-layout | 2018-08-08 | B | "a 'Cards' dashboard UI performed poorly when card content wasn't implemented with a very high level of consistency." |
| S8 | Hierarchy needs contrast limited to a few items | NN/g, visual hierarchy definition | https://www.nngroup.com/articles/visual-hierarchy-ux-definition/ | 2021-01-17 | B | "Grouping is usually conveyed implicitly through proximity and the use of white space or explicitly through enclosure." "If everything is contrasted, then nothing stands out." |
| S9 | Material defines a card as single-subject | Material Design 2, Cards | https://m2.material.io/design/components/cards.html | undated | B | "Cards contain content and actions about a single subject" |
| S10 | Add borders only when whitespace cannot group | NN/g, The Principle of Common Region | https://www.nngroup.com/articles/common-region/ | 2020 | B | "Items within a boundary are perceived as a group and assumed to share some common characteristic or functionality." |
| S11 | Nesting containers obscures layer order | SmartHR Design System Base | https://smarthr.design/products/components/base/ | undated | B | 「Baseの上にBaseを重ねることもレイヤー順序を把握しづらくさせます。Baseの上で矩形によるグルーピングをする場合は基本的に BaseColumn を使ってください。」 |
| S12 | Competing grouping cues reduce grouping strength | Montoro and Luna, Spanish Journal of Psychology 18 | https://www.cambridge.org/core/journals/spanish-journal-of-psychology/article/does-the-relative-strength-of-grouping-principles-modulate-the-interactions-between-them/5EECC917DB4843AE4255EE22EB3EB075 | 2015 | A | "the effect of conjoined competing principles was smaller than that of either principle operating alone." |
| S13 | Layering reduces noise; "1+1=3"; interior decoration is non-data ink | Tufte, Envisioning Information pp. 53, 62 via reader notes; Visual Display via Wikipedia | https://www.robnagler.com/2007/08/25/Envisioning-Information.html ; https://qahiccupps.blogspot.com/2018/08/tufte-envisioning-information.html ; https://en.wikipedia.org/wiki/Chartjunk | 1990 / 1983 | A via secondary | "The noise in 1 + 1 = 3 is directly proportional to the contrast in value (light/dark) between figure and ground." |
| S14 | Dashboard definition; fragmentation hurts; context required; equal prominence fails | Few, Common Pitfalls in Dashboard Design | https://www.perceptualedge.com/articles/Whitepapers/Common_Pitfalls.pdf | 2006-02 | B | "Splitting the big picture into a series of separate small pictures is a mistake when seeing the big picture is worthwhile." "To state that quarter-to-date sales total $736,502 without any context means little." "All of the data displayed on a dashboard ought to be important, but not all data are equally important." |
| S15 | Overview first | Shneiderman, The Eyes Have It | https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf | 1996 | A | "Overview first, zoom and filter, then details-on-demand" |
| S16 | Tiled layouts are a dashboard genre | Sarikaya et al., IEEE TVCG 25(1) | https://tableau.com/sites/default/files/2023-01/DashboardsConspiracy_final.pdf | 2019-01 | A | "the visual genre of dashboards (a visual data representation structured as a tiled layout of simple charts and/or large numbers …)" |
| S17 | Dashboard layouts group widgets by proximity or closure | Bach et al., Dashboard Design Patterns, IEEE TVCG 29(1) | https://ar5iv.labs.arxiv.org/html/2205.00757 | 2022 | A | "A layout needs to prioritize information, e.g., showing information in different sizes or places on each page" |
| S18 | Large clickable areas help touch users | UC Berkeley Digital Accessibility Program | https://dap.berkeley.edu/node/146 | undated | B | "A large clickable area benefits mobile users, touchscreen users, and users with tremors." |
| S19 | Dashboards are single-page, at-a-glance | NN/g, dashboards and preattentive attributes | https://www.nngroup.com/articles/dashboards-preattentive/ | 2017-06-18 | B | "Dashboards are collections of data visualizations, presented in a single-page view that imparts at-a-glance information on which users can act quickly." |
| S20 | Atlassian offers primitives and no fixed card component | Atlassian Design System, Box examples | https://atlassian.design/components/primitives/box/examples | undated | B | "Atlassian uses dozens of distinct card-like components across apps. Therefore, rather than providing a strict component, the Design System empowers you to build your own card components" |
| S21 | Nested and identical cards as AI tells | impeccable.style, The visible tells of AI design | https://impeccable.style/slop | undated | C | "Cards inside cards create visual noise and excessive depth." "Repeated icon, heading, and text cards give every point the same weight." |
| S22 | Equal stat-card grids as an AI-UI tell | Mondal, SaaSUI.Design | https://www.saasui.design/blog/saas-ui-looks-ai-generated | 2026-06-28 | C | "The fastest generated layout is a grid of equal cards, which flattens importance" |
| S23 | Bento grids as a cliché | May, Creative Boom | https://creativeboom.com/insight/10-trends-creatives-are-so-over-in-2026/ | 2026-04-21 | C | "the laziness it enables and the homogeneity it produces." |
| S24 | Material M2 usage rule on tables (search summary) | Material Design 2, Cards | https://m2.material.io/components/cards | undated | B (unverified wording) | "don't use a card as a substitute for a table row when dealing with tabular data" |
| S25 | Cards are good for browsing (practitioner) | Schenker, Webdesigner Depot | https://webdesignerdepot.com/2017/01/cards-vs-lists-how-they-impact-ux | 2017-01-12 | C | "They're great for letting users browse lots of information and for grouping items." |
| S26 | IBM Carbon tile scope | IBM Carbon, Tile usage | https://carbondesignsystem.com/components/tile/usage/ | undated | B | "Tiles are flexible containers for displaying a variety of content" |

## Falsifier results

- Baymard (S7): card dashboards can improve scannability when cards are consistent; the study concerns feature-entry dashboards and does not endorse four equal KPI tiles by default.
- Sarikaya 2019 and Bach 2022 describe tiled layouts; neither says tiles are optimal, and Bach's patterns include prioritisation by size and position.
- NN/g (S1) names dashboards and social aggregation as natural homes for cards (heterogeneous browsing).
- Touch targets (S18) support a card around a navigable entity, not around a static section.
- No source states that cards in general are harmful; every critical source targets inconsistency, equal weighting, nesting, or use on homogeneous or comparable data.

## Gaps

- Palmer 1992 original not opened (403); S2 is Palmer's 2002 summary.
- Wertheimer not opened as a primary source.
- Tufte primary texts not opened; quotes via secondary pages with page numbers.
- Few's books not opened; white papers used.
- Material 3 card pages JS-rendered; only one sentence retrieved.
- Shopify Polaris card pages failed to load.
- GOV.UK backlog #113 is open and unpublished; no final ruling text exists.
- SmartHR's Base page contained no "card" wording; its guidance runs through Base, BaseColumn and visual-grouping rules.
