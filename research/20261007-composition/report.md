# Screen composition for product-ui: scan (as of 2026-10-07)

Purpose: gather the design theory behind what makes a whole screen read as designed, as material for a product-ui revision in which each screen is composed (its job, its reader, its dominant element, its reading order, its containers) before it is built. The user's examples of the defect were card-shaped sections, screens that ignore who uses them, and labels that name the feature or the computation.

Scope: standards bodies and peer-reviewed work where they exist (ISO 9241-11, JIS Z 8530, Palmer 1992/2002, Tuch 2012, Reinecke 2013, Kalyuga 2007, Findlater 2004, Sarikaya 2019, Bach 2022, Furnas 1987), established practitioner bodies and design systems (Nielsen Norman Group, Stephen Few, Mullet and Sano via course notes, Apple, Material, GOV.UK, Shopify Polaris, Microsoft, デジタル庁デザインシステム, SmartHR Design System), and opinion pieces on the look of AI-generated screens, graded C. Materials: the latest build the skill produced (`hansya_Portal_V3`) as the specimen of the defect.

## Question analysis

- Decision: the product-ui maintainer decides which composition decisions the skill records before markup, which of them a script can measure, and which questions a cold reader answers from a screenshot.
- Question type: descriptive, with a prescriptive tail (what the sources allow the skill to encode).
- Presuppositions: the whole-screen defect has a theory behind it that element-level checks cannot carry (verified by SQ1); cards, user fit and labels are consequences of one missing decision (verified by SQ2 to SQ4, which each point back to the rank and the reader).
- Useless answer: a list of design maxims with no rule the skill could apply, measure or ask.

Sub-questions:

1. What makes a whole screen read as designed, and where does sameness help or hurt? (`evidence/sq1-whole-screen-composition.md`)
2. When is a card the right container, and when is a table, a list or whitespace better? (`evidence/sq2-containers-cards.md`)
3. How should the user's role, task and frequency shape a screen? (`evidence/sq3-user-fit.md`)
4. How should labels be chosen and tested? (`evidence/sq4-labelling.md`)

## Answer

A screen reads as designed when a viewer recovers the rank of its parts at a glance: what it is for, what dominates, in what order it is read, and what belongs together. The rank is carried by emphasis (size, weight, position in steps a viewer can tell apart), by grouping (distance first, a filled region second, a rule last) and by a density that follows the screen's job (monitor, enter, look up, decide) and its reader's frequency and expertise. Element-level checks leave that rank unsettled, and a screen of equal panels passes every one of them [SQ1 S5, S6, S8, S10]. Sameness is right in what users learn once (the shell, the navigation, the tokens, the control forms, a short list of layout archetypes) and wrong where it replaces the decision about this screen's content [SQ1 S19, S26, S27, S30, S32].

The three symptoms follow. A card is one unit in a browsed heterogeneous set; a card around every section, a nested card or a card standing in for a table row compensates for a hierarchy the layout has not made [SQ2 S1, S3, S4, S5, S11]. A KPI tile earns its place by a monitored quantity, a comparison and a rank among its neighbours, on a monitoring screen [SQ2 S14, S16, S7]. The user's role, frequency and expertise set the density and the guidance, and the facts are recorded as observed, reported or assumed, with the intermediate as the default [SQ3 E1, E8, E9, E12, E23, E30]. A label predicts what lies behind it in the reader's own words; generic words and feature names carry no scent, and a word the generator picked is a guess until tested [SQ4 S1, S3, S15, S18, S25].

Confidence: medium. The practitioner bodies and design systems agree, the standards fix the context-of-use vocabulary, and the perception literature supplies the mechanism (common region, expertise reversal, first impressions from complexity and typicality). No controlled study tests a row of equal tiles against a ranked row, or role-differentiated screens against one uniform screen, so those two claims rest on mechanism and consensus. Mullet and Sano, Tufte, Few's books, Cooper and Furnas were read through secondary copies.

Reading for the decision (inference of this scan): the encodable core is (a) a composition plan per screen written before markup, with the job class, the reader, the dominant element, the reading order, the density, the archetype, the grouping cue per section and the tile row; (b) `meta.users` in `tokens.json` with a validator; (c) measured checks for nested enclosures, spacing steps, emphasis levels and equal tile rows from the rendered DOM; (d) source checks for nested cards and for generic, feature-shaped, duplicated and product-named labels; (e) eight cold-read questions and three reader-fit questions for the independent reviewer. The judgement calls (whether the dominant element is the purpose, whether a label predicts its destination for this reader) stay with the reviewer.

## Findings

### SQ1: the whole screen

- "If everything is contrasted, then nothing stands out" (NN/g); "nothing in particular grabs your attention. When this happens the dashboard has failed" (Few) [S6, S5].
- Contrast is meaningful irregularity on a regular base; multiplicative scaling; white space for grouping [S2, after Mullet and Sano].
- Density by job: one screen for monitoring [S5]; one thing per page or one column for entry [S27, S33]; overview first, details on demand for lookup [S36].
- Sameness helps in conventions and canonical layouts [S32, S30, S26, S27]; "templates are content agnostic. And that is the problem" [S19, grade C].
- First impressions form in under a second from complexity and typicality [S13, S14]; the transfer to product screens is inference.
- An LLM "can probabilistically default to the same familiar patterns" [S22, preprint].
- Falsifier: no source shows equal-weight tiles easier to use than a ranked hierarchy; the regular-base nuance [S2] is the strongest counter and is adopted.

### SQ2: containers

- Cards for heterogeneous browsed items; lists and tables for scanning and comparison [S1, S4, S6, S9].
- Distance first, rectangle second, rule last; no Base on Base [S5, S10, S11].
- Common region is an automatic grouping cue; competing cues weaken the group [S2, S12].
- "Cards are often used to compensate for poor information hierarchy or content design" [S3].
- A figure without context "means little"; "not all data are equally important" [S14]; tiled dashboards are a genre [S16]; card dashboards need consistency [S7].
- Falsifier: cards help on mobile touch targets and for browsing [S18, S1, S7]; the rule keeps those cases.

### SQ3: user fit

- Context of use and user group [E1, E2, E3]; frequency raises the wish for density and shortcuts [E12, E8]; progressive disclosure and layers serve both ends [E9, E13]; expertise reversal [E23].
- Role-based differentiation is sanctioned; automatic adaptation tested worse than static menus [E10, E24]; fictional personas cannot be verified [E30].
- Falsifier: consistency arguments constrain the chrome and leave the content decision open [E29]; one small study found frequent and infrequent users met mostly the same issues [E28].

### SQ4: labelling

- Agreement on one word is below 0.20 [S1, S2]; generic labels have low scent and scent depends on the audience's vocabulary [S3, S5].
- "Don't talk about products, features, or commands in headings" [S15]; "Most features don't need an official, branded name" [S18]; 「管理者」は指す範囲が明確ではない [S25].
- Tree tests check labels; card-sort names are input [S9, S10]; one term per concept and consistent navigation labels [S13, S17].
- Falsifier: conventions (Settings, Home) and specialist jargon for the recorded audience are correct [S32, S8, S27, S36]; no source names 「〜機能」「各種」「〜管理」, so those patterns stay warnings.

## What entered the skill

| Finding | Where it landed |
|---|---|
| Composition plan before markup | `references/composition.md`; `assets/brief.template.md` Composition section; `SKILL.md` Step 3 and Principle 6 |
| Container rule, one enclosure level | `composition.md`; `ban-list.md` "Enclosures are default OFF"; S11 in `check_slop.py`; R12 in `check_render.py`; `.section` in the portal shell |
| KPI tile rule | `composition.md`; `ban-list.md`; R15 with `--plan` |
| Three spacing steps, three emphasis levels | R13, R14; `ban-list.md` "Equal weight is default OFF" |
| User groups | `meta.users` with T18 in `validate_tokens.py`; the Users intake question; the reader-fit questions for P3 |
| Labels | C18 to C21 in `check_copy.py`; `ban-list.md` "A label names the object or the reader's task"; reader-fit question 3 |
| Cold read | eight questions in the brief, answered by P2 from the screenshot before the dump |

## Specimen

`before/` holds the original 販社ポータル V3 home and market captures, their measurements and the independent review of the home (BLOCK on the equal tiles). `after-v3/` holds the 27 captures of the rebuilt mock on branch `feat/compose-v3`, the measurements (no R12 to R15 finding), three independent reviews (all CONCERNS, none CRITICAL) and `after-v3/report.md`.

## Not covered

- The book texts of Mullet and Sano, Tufte, Few, Cooper, Beyer and Holtzblatt, Rosenfeld and Morville (4th ed.) and Furnas et al. were read through secondary copies or earlier editions.
- No controlled comparison of equal-weight tiles against a ranked row, or of role-differentiated screens against one uniform screen, surfaced; a research-team run with a literature search in the HCI venues would settle whether one exists.
- Material 3, Shopify Polaris card pages and Atlassian layout guidance did not load; Material is cited through its M2 pages and the Android Developers mirror.
- No Japanese academic text on 画面全体の構成 by a credible author surfaced.
- The thresholds in R13 to R15 (three steps, three levels, three tiles, 40% of the viewport) are this skill's own, set from grade B guidance, and await calibration on real screens.
- This report reflects what these searches surfaced, which differs from the balance of informed opinion.
