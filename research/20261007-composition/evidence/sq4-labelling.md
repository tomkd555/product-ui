# SQ4: Labelling and information scent (collector report, 2026-10-07)

Collector: a Sonnet research agent with WebSearch and WebFetch. Quotes marked "as returned" came back through a summarising fetch tool; the Microsoft pages (raw markdown) and the 公用文作成の考え方 PDF were read directly.

## Answer

Labels work when a user can predict from the label alone what lies behind it, and that prediction depends on the label carrying words the user already owns. Furnas et al. found that two people pick the same word for the same thing with probability below 0.20. A word chosen by the designer, or by a model, is therefore a guess unless it was taken from user data and tested [S1, S2]. Information-scent theory explains why generic labels fail: users judge a link or heading from its label alone, so "More", "Overview" or "Details" give no cue about the destination [S3, S4]. Style guides from Microsoft, Shopify, GOV.UK and SmartHR agree on the replacement: name the object or the user's task in the user's words, and leave feature names, product names and internal vocabulary out of headings [S15, S18, S21, S25, S26]. The sources that give a testing method (NN/g, the Information Architecture books, Donna Spencer) use user vocabulary, search logs and card sorts as inputs, and tree tests as the check. NN/g warns that card-sort category names are not final labels [S9, S10, S11, S12].

## Rules the sources support

### (a) Checkable on the label text alone

1. A label made only of a generic word fails the scent test: 概要, 詳細, 情報, 管理, 各種, 一覧, その他, Overview, Details, Information, More, Learn more. [S3, S6, S25; the list is inference]
2. A label suffixed 「機能」, prefixed 「各種」, or shaped "<noun>管理 / management" describes a feature or an umbrella. [S15, S18, S25; the patterns are inference, no source names them]
3. A heading or label that repeats the product or brand name. [S19 (single source); S22 lists "hub", "portal", "one-stop shop" as empty metaphors]
4. Two headings on one page with identical text; one destination with two labels. [S13, S17, S22]
5. The first two words carry the information. [S6, S15; S34 grade C]
6. Headings at the same level share one grammatical form. [S16, S13]
7. Button labels contain a verb and an object; bare "OK", "送信", "実行", "Submit" are flagged, with Save, Close, Cancel, OK allowed. [S20; S28]
8. Words on a glossary of internal terms and buzzwords. [S21, S22, S26]

### (b) Needing a reader or a test

9. Source labels from users' own text: search logs, support tickets, interviews. [S11, S12, S21]
10. Name the object or the user's task; in an OOUI the root navigation items are the nouns. [S15, S29, S30]
11. A label must predict its destination; test by asking a reader what each label leads to. [S3, S4, S28]
12. Treat any single chosen word as a hypothesis; agreement is below 0.20. [S1, S2]
13. Check labels with a tree test; card-sort names are input only. [S9, S10]
14. Keep consistency of style, granularity and audience across a labelling system. [S13, S14]
15. Domain jargon is acceptable when the named audience uses it. [S8, S23, S27, S36]
16. Established conventions beat novelty for standard destinations. [S13, S32]

## Evidence table

| # | Claim | Source | URL | Published | Grade | Verbatim quote |
|---|---|---|---|---|---|---|
| S1 | Two people rarely choose the same word | Furnas, Landauer, Gomez, Dumais, CACM 30(11) (abstract via note page) | https://honnef.co/notes/references/furnasvocabularyproblemhumansystem1987 | 1987-11 | A (secondary copy) | "In every case two people favored the same term with probability <0.20." |
| S2 | Single-word access fails 80-90% | Same paper (abstract via UIPedia) | https://scrapbox.io/UIPedia/George_Furnas:_The_vocabulary_problem_in_human-system_communication | 1987-11 | A (secondary copy) | "the popular approach in which access is via one designer's favorite single word will result in 80-90 percent failure rates in many common situations." |
| S3 | Generic labels have low scent | Budiu, NN/g, Information Scent | https://www.nngroup.com/articles/information-scent/ | 2020-02-02 | B | "a label (such as More or Learn more) has low information scent … it's hard to guess what the link may lead to." (as returned) |
| S4 | Definition of scent | Budiu, NN/g | https://www.nngroup.com/articles/information-scent/ | 2020-02-02 | B | "the user's imperfect estimate of the value that the source will deliver to the user, derived from a representation of the source." |
| S5 | Scent depends on the audience's vocabulary | Budiu, NN/g | https://www.nngroup.com/articles/information-scent/ | 2020-02-02 | B | "it may still miss the mark and have low information scent if it contains words that are not easily understood by the target audience." (as returned) |
| S6 | Specific, front-loaded headings | Loranger and Nielsen, NN/g, Microcontent | https://www.nngroup.com/articles/microcontent-how-to-write-headlines-page-titles-and-subject-lines/ | 2017-01-29 | B | "useful headings are specific"; "Avoid broad and generic headings." (as returned) |
| S7 | Heuristic 2 | NN/g, 10 Usability Heuristics | https://www.nngroup.com/articles/ten-usability-heuristics/ | rev. 2024-01-30 | B | "The design should speak the users' language." |
| S8 | Jargon is fine for a specialist group | Loranger, NN/g, Plain Language Is for Everyone, Even Experts | https://www.nngroup.com/articles/plain-language-experts/ | 2017-10-08 | B | "Jargon is helpful, however, when it communicates a concept clearly understood by specialized user groups." (as returned) |
| S9 | Card-sort names are not final labels | Tankala and Sherwin, NN/g | https://www.nngroup.com/articles/card-sorting-definition/ | 2024-02-02 | B | "Category names they come up with will not necessarily be your final labels." (as returned) |
| S10 | Tree-test directness measures label clarity | Laubheimer, NN/g, tree testing | https://www.nngroup.com/articles/tree-testing/ | 2023-08-06 | B | directness gives insight into "the clarity or ambiguity of your category labels" (as returned) |
| S11 | Users are the best label source | Rosenfeld and Morville, IA for the WWW (1st ed.), 5.4.1 | https://files.znu.edu.ua/files/comp.books/books/information_architecture_for_WWW/infoarch/ch05_04.htm | 1998 | B | "if you can, it's the best source of labeling there is." |
| S12 | Search logs show users' labels | Same, 5.4.1 | same | 1998 | B | "Query analysis is a great way to understand the types of labels your site's users typically use" |
| S13 | Navigation labels need consistency | Same, 5.3 | https://files.znu.edu.ua/files/comp.books/books/information_architecture_for_WWW/infoarch/ch05_03.htm | 1998 | B | "using the label Main, on one page, Main Page on another, and Home elsewhere will surely destroy the familiarity." |
| S14 | A labelling system needs planning | Same, 5.2 | https://files.znu.edu.ua/files/comp.books/books/information_architecture_for_WWW/infoarch/ch05_02.htm | 1998 | B | "labeling systems, like any other, require planning to succeed." |
| S15 | Headings name what customers achieve | Microsoft Writing Style Guide, Headings | https://learn.microsoft.com/en-us/style-guide/scannable-content/headings | 2018-07-24 | B | "In most cases, don't talk about products, features, or commands in headings. Concentrate on what customers can achieve or what they need to know." |
| S16 | Parallel headings | Microsoft, Headings | same | 2018-07-24 | B | "Use parallel sentence structure for all headings at the same level." |
| S17 | One term per concept | Microsoft, Use simple words, concise sentences | https://learn.microsoft.com/en-us/style-guide/word-choice/use-simple-words-concise-sentences | 2018-01-19 | B | "Use one term consistently to represent one concept." |
| S18 | Descriptive, merchant-language names | Shopify Polaris, Naming (archived source) | https://raw.githubusercontent.com/Shopify/polaris-react-archive/main/polaris.shopify.com/content/content/naming.mdx | undated | B | "Most features don't need an official, branded name" (as returned) |
| S19 | Product name stays out of built-in feature names | Shopify Polaris, Naming | same | undated | B | Don't: Shopify Analytics, Shopify Discounts (as returned) |
| S20 | Button and link labels start with a verb | Apple HIG, Writing | https://developer.apple.com/tutorials/data/design/human-interface-guidelines/writing.json | undated | B | "When labeling buttons and links, it's almost always best to use a verb." |
| S21 | Use users' words; check search terms | GOV.UK, Clear language | https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/ | undated | B | "Use the language that users: will be familiar with, use themselves" (as returned) |
| S22 | Unique, descriptive, front-loaded titles | GOV.UK, A to Z style guide | https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/ | undated | B | "Page titles should: be 65 characters or less, be unique, clear and descriptive, be frontloaded" (as returned) |
| S23 | Plain language and specialist terms | plainlanguage.gov, Word suggestions (archived) | https://cybercemetery.unt.edu/oilspill/20121014022836mp_/http://www.plainlanguage.gov/howto/wordsuggestions/index.cfm | 2012 archive | B | "Plain language does not ban jargon and other specialist terms. But you need to understand your readers" (as returned) |
| S24 | Headings and labels describe topic or purpose | W3C, WCAG 2.2 Understanding SC 2.4.6 | https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html | WCAG 2.2 | A | "A word, or even a single character, may suffice if it provides an appropriate cue" (as returned) |
| S25 | SmartHR avoids 「管理者」 | SmartHR Design System 用字用語 | https://smarthr.design/products/contents/idiomatic-usage/usage/ | undated | B | 「管理者」という呼称は、その言葉が指す範囲が明確ではないため、できるだけ使用しません。 (as returned) |
| S26 | SmartHR on dictionary words and internal terms | SmartHR Design System 基本的な考え方 | https://smarthr.design/products/contents/writing-style/ | undated | B | 「社内用語・専門用語・独自の用語など、ユーザーに伝わらない可能性がある言葉は避けましょう。」 (as returned) |
| S27 | Technical terms and loanwords | 文化審議会「公用文作成の考え方」 pp. 5-6 | https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/pdf/93731901_01.pdf | 2022-01-07 | A | 「専門家同士であれば、難しい用語や詳しいデータをそのまま用いることによって正確な伝え合いが可能となる。しかし、専門的な知識を特に持たない人に対してはそのままでは伝わらない。」 |
| S28 | Headings represent their content; button labels | デジタル庁デザインシステム heading, button | https://design.digital.go.jp/dads/components/heading/ ; https://design.digital.go.jp/dads/components/button/ | undated | B | 「内容を的確に表す」 (fragment) |
| S29 | OOUI is noun first | 上野学, OOUI introduction in 15 min | https://speakerdeck.com/uenitty/ooui-introduction-in-15-min-lt | 2020-10-26 | C | 「名詞 → 動詞」 |
| S30 | Navigation starts from objects | mrsekut, Scrapbox note | https://scrapbox.io/mrsekut-p/OOUI%E8%A8%AD%E8%A8%88%E3%81%AE%E6%B5%81%E3%82%8C | undated | C | 「まず最初にオブジェクトを見せる。その後に、タスクを選択させる」 |
| S31 | Clever names must convey the benefit | Krug, Don't Make Me Think (Kindle highlights) | https://notes.elie.net/zdata/kindle/Krug-Dont+Make+Me+Think | undated | C | "Clever is good, but only if the cleverness helps convey—not obscure—the benefit." |
| S32 | Convention beats novelty | Nielsen, NN/g, Jakob's Law | https://www.nngroup.com/videos/jakobs-law-internet-ux/ | 2017-08-18 | B | "users prefer your site to work the same way as all the other sites they already know." |
| S33 | Org-centred labels in practice | Lowe, Palantir | https://www.palantir.net/blog/improving-task-completion-through-tree-testing | 2019-09-04 | C | "frequently they use labels that are understood by the organization but not by the audience" (as returned) |
| S34 | First two words decide | Nielsen, uxtigers.com | https://www.uxtigers.com/post/information-foraging | undated | C | "Users judge a link on roughly the first 2 words of the label" (as returned) |
| S35 | Use words users already use | yosuke777, Zenn (READYFOR) | https://zenn.dev/readyfor_blog/articles/1fde03dd5795c2 | 2023-12-03 | C | 「ユーザーがよく使う言葉を採用する」 (as returned) |
| S36 | Shopify allows jargon merchants say | Shopify Polaris, Content fundamentals | https://raw.githubusercontent.com/Shopify/polaris-react-archive/main/polaris.shopify.com/content/content/fundamentals.mdx | undated | B | "Some jargon is okay, as long as it's what actual merchants say." (as returned) |

## Falsifier results

- Convention beats specificity for standard destinations [S13, S32]: Settings, Profile, Sign in, Home stay. The rules target content-level labels (a KPI title, a section heading, a column) where no convention supplies the meaning.
- Specialist jargon can be the right label [S8, S23, S27, S36], which limits the rule to "use the audience's words".
- A short label can be enough [S24].
- Users' own words can mislead [S9, S1]: "the user's word" is a distribution and a test is still required.
- No verified source on legal terms in UI labels.
- No NN/g or standards-body source on dashboard titles.

## Gaps

- Furnas et al., Pirolli and Card 1999, Chi et al. 2001 not opened; secondary copies used.
- IA 4th edition chapter returned 403; the 1998 first-edition mirror was used.
- Spencer's Card Sorting and Optimal Workshop pages not opened.
- Krug reached only through Kindle highlights.
- Atlassian, Material 3 and Apple on "use words people know" not confirmed.
- Shopify Polaris actionable-language page and 18F guide failed to load.
- No credible Japanese article was found that names 「〜機能」「各種」「管理」 as labels to avoid; rule 2 is inference.
