# SQ3: How the user's role, task and frequency shape a screen (collector report, 2026-10-07)

Collector: a Sonnet research agent with WebSearch and WebFetch. Rows E6 and E7 were unused placeholders in the collector's numbering and are omitted.

## Answer

The sources agree that a screen's structure follows from the context of use: who the user is, what job they are doing, how often, and in what setting (E1, E2, E3). Frequency and expertise decide how much the screen asks the user to remember. A frequent user spreads the learning cost over many sessions and wants density, accelerators and the common action close to hand (E8, E10, E12). An infrequent or first-time user needs few options and visible guidance (E9, E13, E17). A viewer who glances at numbers needs a few measures chosen for the job, with context, on one screen (E16, E17, E19). Guidance that helps novices can degrade performance for experts, which is the cognitive-load mechanism that makes one uniform structure a poor fit for mixed audiences (E23). The sources also fix the method: record observed facts about users, tasks and environments before choosing layout (E3, E14). No source opened reports a controlled comparison of role-differentiated screens against one uniform screen, so the mechanism rests on cognitive-load theory, standards text and practitioner consensus.

## Intake facts the sources justify recording

| Fact | What to record | Source IDs |
|---|---|---|
| User group / role | Who the users are, and which of them differ in characteristics, tasks or environments; each differing subset is its own user group | E1, E2, E3 |
| Goal and task as a job | The outcome the user wants, stated as the circumstance in which they need it | E1, E26, E3 |
| Frequency of use | Daily or continuous, periodic, or a one-time first use | E1, E8, E10, E27 |
| Expertise and learning path | Domain and tool expertise today, and whether the user will stay a beginner or settle into an intermediate | E4, E5, E23, E9 |
| Screen type needed | Monitor, analyse, enter or edit data, look up a record, or decide | E15, E16, E17, E19 |
| Environment | Device, place, interruptions, shared screen, organisational context | E1, E3 |
| Resources | Equipment and software the user already works with | E1, E29 |
| Stakes of error | Harm from use and cost of mistakes | E1 |
| User vocabulary | The words the user already uses for objects and actions | E8, E19 |
| Evidence basis | Whether each fact was observed, reported by a stakeholder, or assumed | E14, E30 |

## Rules the sources support

1. Settle users, goals and tasks, resources and environment before choosing layout, and record each as an observed fact. [E1, E2, E3, E14]
2. Two audiences that differ in task, expertise or environment get separate structure decisions. [E1, E21]
3. A daily operator gets the dense table, several items visible at once, plain visual styling, shortcuts, and the frequent action within one click. [E8, E10, E12, E11, E27 (single blog for the styling detail)]
4. A first-time or infrequent user gets a few primary options, explanatory text and a guided path, removable once the user is familiar. [E9, E4, E13, E23, E1]
5. When frequency or expertise is unknown, target the intermediate. [E4, E5, E8] (Cooper via secondary)
6. A viewer who glances at numbers gets a single-screen display of the few measures their job needs, each with comparison context, with the one item needing attention marked. [E15, E16, E19, E18]
7. Monitoring, analysis and data entry are different screen types. [E16, E17] (Few as relayed)
8. Keep one underlying structure and vary its depth through progressive disclosure and layered interfaces. [E9, E13, E8]
9. Offer user-controlled personalisation and role-based personalisation; keep automatic per-user adaptation out. [E24, E13, E10]
10. Take labels, objects and word order from the user's own vocabulary. [E8, E19]
11. State the task as a job tied to a circumstance. [E26] (inference from purchase-decision research)
12. Derive environment-driven choices (screen size, hit area, shared-screen legibility) from the recorded environment. [E1] (inference)
13. In review, ask of each structural choice which recorded fact justifies it; a choice with no recorded fact is unjustified. [E1, E3] (inference)

## Evidence table

| # | Claim | Source | URL | Published | Grade | Verbatim quote |
|---|---|---|---|---|---|---|
| E1 | Context of use; user group; usability covers regular and infrequent use | ISO 9241-11:2018 (SIST preview) | https://preview.sist.si/sist-preview/63500/33c267a5a7564f298f02bbd65721a181/ISO-9241-11-2018.pdf | 2018-03 | A | 3.1.15: "combination of users, goals and tasks, resources, and environment". 3.1.8: "subset of intended users who are differentiated from other intended users by characteristics of the users, tasks or environments that could influence usability". |
| E2 | JIS principle for users, tasks and environment | JIS Z 8530:2019 (preview) | https://webdesk.jsa.or.jp/preview/pre_jis_z_08530_000_000_2019_j_ed10_ch.pdf | 2019 | A | "4.2 ユーザー，タスク及び環境の明確な理解に基づく設計"; "6.2 利用状況の把握及び明示" |
| E3 | ISO 9241-210 principle 1 and rationale | NHS England Digital, quoting ISO 9241-210 | https://nhsd-proxy.openprescribing.net/blog/design-matters/2022/how-a-20-year-old-standard-is-still-relevant-today | 2022-03-08 | B | "The design is based upon an explicit understanding of users, tasks and environments" |
| E4 | Cooper: most users are intermediates | Naderi, MSDN blog, What Would Alan Cooper Do? | https://learn.microsoft.com/en-us/archive/blogs/nnaderi/what-would-alan-cooper-do | 2009-01-15 | C | "the vast majority of users of any software product can be categorized as intermediate users" |
| E5 | Cooper on beginners and persistent intermediacy | Atwood, Coding Horror, quoting About Face | https://blog.codinghorror.com/defending-perpetual-intermediacy/ | 2004-10-05 | C | "When people achieve an adequate level of experience and ability, they generally stay there forever." |
| E8 | Heuristics 2 and 7 | NN/g, 10 Usability Heuristics | https://www.nngroup.com/articles/ten-usability-heuristics/ | rev. 2024-01-30 | B | H2: "The design should speak the users' language." H7: "Shortcuts — hidden from novice users — may speed up the interaction for the expert user" |
| E9 | Progressive disclosure helps novices and experts | NN/g, Progressive Disclosure | https://www.nngroup.com/articles/progressive-disclosure/ | 2006-12-03 | B | "Initially, show users only a few of the most important options. Offer a larger set of specialized options upon request." |
| E10 | Accelerators and role-based personalisation | NN/g, Flexibility and Efficiency of Use | https://www.nngroup.com/articles/flexibility-efficiency-heuristic/ | 2020-11-22 | B | "Role-based personalization works well for enterprise tools." |
| E11 | Frequent users justify expert-oriented design | NN/g, Novice vs. Expert Users | https://www.nngroup.com/articles/novice-vs-expert-users/ | 2000-02-05 | B | "It is time to take expert user performance more seriously on the Web." |
| E12 | Frequent users need shortcuts; novices explanations | Shneiderman, Eight Golden Rules | https://me.konigi.com/blog/shneidermans-eight-golden-rules-interface-design ; https://www.cs.umd.edu/~ben/goldenrules.html | 2008; 2016 ed. | B | "As the frequency of use increases, so do the user's desires to reduce the number of interactions and to increase the pace of interaction." |
| E13 | Multi-layer interfaces | Shneiderman, Promoting Universal Usability with Multi-Layer Interface Design, ACM CUU 2003 | https://www.cs.umd.edu/~ben/ACM-CUU2003.pdf | 2003-11 | A | "multi-layer interface designs that enable first-time and novice users to begin with a limited set of features at layer 1" |
| E14 | Observe work in context | Holtzblatt, InContext Design | https://www.incontextdesign.com/dont-ask-your-customer-article/ | undated | B | "People know everything—everything—about what they do. They just can't tell you." |
| E15 | Dashboard defined for monitoring a job; dense, single screen | Few, Why Most Dashboards Fail | https://blogs.ischool.berkeley.edu/i247s13/files/2013/02/WhyMostDashboardsFail.pdf | 2007 | B | "This single-screen display of the most important information needed to do a job, designed for rapid monitoring" |
| E16 | Few's definition; audience-dependent design | Bach et al., Dashboard Design Patterns | https://arxiv.org/pdf/2205.00757 | 2022-08-24 | A | "Novice or casual users will likely need more guidance in the form of clear layout (e.g., stratified) and titles, little to no interaction, and generally less information" |
| E17 | Dashboards tailored to a person, group or function | UXmatters review of Information Dashboard Design | http://www.uxmatters.com/mt/archives/2007/04/book-review-information-dashboard-design.php | 2007-04-09 | C | "tailored specifically to the requirements of a given person, group, or function." |
| E18 | Dashboards serve time-sensitive monitoring | NN/g, dashboards article | https://www.nngroup.com/articles/dashboards-preattentive/ | 2017-06-18 | B | "consume fast, with a minimum of interaction or cognitive processing." |
| E19 | SmartHR principle: user time is finite; words first | SmartHR Design System デザイン原則 | https://smarthr.design/products/principles/ | undated | B | 「ユーザーの限りある業務時間をムダにしない、使い勝手のよいプロダクトを作ります。」 |
| E20 | Sociomedia object-first principle | ソシオメディア home page | https://www.sociomedia.co.jp/ | undated | B | 「オブジェクト（もの、名詞）を起点としてUIを設計すること。」 |
| E21 | Digital Agency: human-centred principle | デジタル庁 サービスデザイン | https://www.digital.go.jp/policies/servicedesign | 2026-07-09 | B | 「多様な利用者のニーズを効果的かつ効率的に達成できるよう利用者中心（人間中心）を原則とする」 |
| E22 | Digital Agency definition of 利用者視点 | デジタル庁 利用者視点導入ガイドブック | https://www.digital.go.jp/resources/user-centered-approach-guidebook | 2025-04-01 | B | 「実際の利用者の声や行動を起点として改善や改革を進めていく考え方やアプローチです。」 |
| E23 | Expertise reversal effect | Kalyuga, Educational Psychology Review 19 | https://www.uky.edu/~gmswan3/EDC608/Kalyuga2007_Article_ExpertiseReversalEffectAndItsI.pdf | 2007 | A | "designs and techniques that are effective with low-knowledge individuals can lose their effectiveness and even have negative consequences for more proficient learners" |
| E24 | Static menus beat adaptive menus; users preferred adaptable | Findlater and McGrenere, CHI 2004 | https://www.cs.ubc.ca/labs/edapt/papers/findlater2004.pdf | 2004-04 | A | "The static menu was found to be significantly faster than the adaptive menu... The majority of users preferred the adaptable menu overall." |
| E25 | KLM models expert routine tasks | Wikipedia, Keystroke-level model (citing Card, Moran and Newell 1980) | https://en.wikipedia.org/wiki/Keystroke-level_model | n/a | C | "predicts how long it will take an expert user to accomplish a routine task without errors" |
| E26 | Jobs to be done | HBS Working Knowledge, Christensen interview | https://www.library.hbs.edu/working-knowledge/clay-christensens-milkshake-marketing | 2011-02-14 | B | "The fact that you're 18 to 35 years old with a college degree does not cause you to buy a product." |
| E27 | Interfaces change with frequency of use | Hobday, blog | https://anthonyhobday.com/blog/20221222 | 2022-12-22 | C | "We get tired of expressive visual design if we see it every day." |
| E28 | Frequent and infrequent ERP users hit mostly the same issues | Derckx, Radboud University master's thesis | https://cs.ru.nl/masters-theses/2015/S_Derckx___A_research_on_usability_problems_of_frequent_and_infrequent_users.pdf | 2015-03-31 | C | "They mostly experience the same usability issues, however they occurred more often with the infrequent users" |
| E29 | Consistency heuristic and Jakob's Law | NN/g, Consistency and Standards | https://www.nngroup.com/articles/consistency-and-standards/ | 2021-01-10 | B | "Follow platform and industry conventions." |
| E30 | Personas cannot be verified | Chapman and Milham, HFES 2006 | https://quantuxbook.com/papers/Chapman-Milham-Personas-HFES2006-0139-0330.pdf | 2006 | A | "Personas cannot be adequately verified or falsified and therefore have no demonstrable validity." |

## Falsifier results

- Consistency (E29) constrains how the screen is built and leaves room to vary which content comes first.
- Automatic adaptation fails (E24, E13): static menus were faster than adaptive ones; Shneiderman reports that predictable interfaces are strongly preferred. This opposes system-driven per-user change and leaves design by recorded role intact.
- Layering has costs (E13): critics note that switching layers can overwhelm novices.
- Small differences by frequency (E28): one 7-participant ERP study found frequent and infrequent users met mostly the same issues, with infrequent users meeting them more often.
- Cooper's own claim (E4, E5): if most users in every role are intermediates, role differences are smaller than assumed.
- Personas (E30): fictional personas cannot be validated, which supports recording observed facts.
- No controlled study compares role-differentiated screens with one uniform screen.

## Gaps

- ISO 9241-210:2019 text (403); the principles come from the NHS blog.
- JIS Z 8530:2021 was not opened; only the 2019 preview's contents.
- Cooper, Beyer and Holtzblatt, Few's book, Card Moran and Newell, Christensen's book reached only through secondary sources.
- SmartHR has no found guidance on 従業員 versus 管理者 screens; freee yielded nothing usable.
- No NN/g article specifically on information density was found.
