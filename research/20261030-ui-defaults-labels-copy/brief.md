# Brief: default values, font sizes, labels and copy in highly rated web screens, and the elements that make screens and their text read as AI-made

As of 2026-10-30. Tier: DEEP. Request language: ja.

## Decision

The main session, right after this run, writes the improvement plan for the product-ui skill
(C:\Mycode\ClaudeCode\product-ui\plugins\product-ui\skills\product-ui). For each of five areas it
sets a default value or range, a generation rule, and the check that enforces it:

1. setting values: the design-token values the skill ships (spacing base unit and scale,
   type-scale ratio, corner radius, shadow, line height, letter spacing, number of colours and
   their roles) in `assets/tokens_example*.json`, `assets/theme.template.css` and
   `data/typography.csv`, `data/styles.csv`;
2. screen design defaults: content and container widths, grid, density, component heights and
   paddings, navigation and page structure (`references/composition.md`, `components.md`,
   `stack-defaults.md`);
3. font sizes: body size, the size ramp, the minimum size, Japanese and Latin text, line length;
4. labelling: button, navigation, form-field, heading and status labels in Japanese and English
   (`references/ui-copy.md`);
5. slop text: filler copy that reads as AI-written, Japanese and English (`references/ban-list.md`,
   `slop-checklist.md`, `assets/stock_words.json`, `assets/voice_terms.ja.json`).

The plan needs, per area, the value ranges and conventions that highly rated sites and design
systems use, the framework defaults the skill starts from (Tailwind CSS, shadcn/ui), and the
elements readers take as signs of AI, each with the grade of its evidence.

## Question type

Descriptive (observed values and conventions; named AI tells), with an evaluative part (what
the studies say about the effect of size, line length and wording on reading and task success,
and about readers' reaction to AI-written text).

## Definition of "highly rated"

- Sites recognised by a named jury: Awwwards (Site of the Day, Site of the Year), CSS Design
  Awards, the Webby Awards, Good Design Award (Japan), Web グランプリ (Japan).
- Public design systems of organisations known for UI quality: GOV.UK Design System, デジタル庁
  デザインシステム (DADS), SmartHR Design System, Apple Human Interface Guidelines, Material
  Design 3, IBM Carbon, Shopify Polaris, GitHub Primer, Atlassian Design System; Microsoft
  Fluent 2 and other public Japanese design systems where they publish values.
- HTTP Archive's Web Almanac describes what is common across the web, the baseline that the
  highly rated sets are compared against; it is no measure of rating.

## Presuppositions

- Highly rated design systems publish numeric values that fall into ranges → verify in SQ1-SQ3.
- Award-recognised sites have measurable values → verify in SQ1-SQ3; award juries publish no
  token tables, so values come from the sites' CSS or third-party measurements where found.
- Content style guides agree on label conventions in Japanese and English → verify in SQ4.
- Elements of values, sizes, labels and copy make readers take a screen or text as AI-made,
  beyond the traits the previous run holds → verify in SQ5.
- Font size, line length and label wording change reading and task success → verify in SQ6.
- Readers react to AI-written text in Japanese as in English → verify in SQ6.
- The previous run's findings on visual traits, stock vocabulary and the attribution penalty
  hold → accept, because they were verified in that run; cite them by run and id.

## Sub-questions

- SQ1: What values do highly rated design systems and award-recognised sites use for design
  tokens: spacing base unit and scale steps, type-scale ratio, corner radius steps, shadow and
  elevation levels, line height, letter spacing, the number of colours and their roles; what are
  the defaults of Tailwind CSS v4 and shadcn/ui; and what does the Web Almanac report as common?
  Source: web
- SQ2: What screen-design defaults do the same sources set: content and container maximum widths,
  grid columns, gutters and breakpoints, density modes, heights and paddings of buttons, inputs
  and table rows, navigation patterns and page structure, for application screens and marketing
  pages, with the Tailwind and shadcn/ui defaults? Source: web
- SQ3: What font sizes do the same sources set: body size, the size ramp, the minimum size,
  Japanese text versus Latin text (font size, line height, letter spacing for Japanese), line
  length in characters; and what does the Web Almanac report? Source: web
- SQ4: What conventions do published content style guides set for button, navigation, form-field,
  heading and status labels, in Japanese (DADS, SmartHR, others) and English (GOV.UK, Material,
  Polaris, Primer, Atlassian, Apple, Microsoft): verb forms, case, length, and the words and
  phrases they discourage as filler? Source: web
- SQ5: Which elements of setting values, layout defaults, font sizes, labels and copy do
  designers, developers and readers name in 2023-2026 as making a screen or its text read as
  AI-made, beyond the previous run's traits? Source: web
- SQ6: What do published studies report on on-screen readability by font size, line length, line spacing and
  letter spacing (Japanese text included); on label and microcopy wording and task success; and
  on readers' detection of and reaction to AI-written text, Japanese readers and marketing or UI
  copy included? Source: academic

## Hypotheses

- H1 (the user's view): highly rated sites and design systems share measurable value ranges and
  wording conventions, and AI-made screens and text show identifiable elements in each of the
  5 areas; product-ui improves by adopting the ranges and avoiding the elements.
- H2: Tailwind and shadcn/ui defaults already sit inside the design-system ranges; the AI look in
  values comes from one unchosen default applied everywhere, so a range alone does not separate
  good output from AI-made output; hierarchy and per-product choice do.
- H3: award-recognised marketing sites and product design systems diverge (display sizes,
  density, widths); one default set cannot serve both, and award-site values would hurt task
  screens.
- H4: readers detect AI-written copy poorly; the harm of slop text comes from low information
  and generic wording, so plain-language rules from style guides carry more weight than lists of
  AI tells.

## Local materials

- C:\Mycode\ClaudeCode\product-ui\research\20261030-ai-tells-ui\report.md, sources.md,
  evidence.jsonl (previous run; its items are cited by id)
- C:\Mycode\ClaudeCode\product-ui\plugins\product-ui\skills\product-ui\ (SKILL.md, references,
  assets, data): read by the main session for the plan; collectors receive none of it.

## Notes

- Plan agreement skipped: this run is a subagent and cannot ask the user.
- Agent count: the user's CLAUDE.md keeps a workflow under 10 agents. This run launches 6
  collectors and at most 3 verifiers, so the verification cap is 15 claims where DEEP sets 25.
  The academic collector covers three topics in one sub-question (SQ6) for the same reason.
- Previous run's items are cited in the report as "ai-tells-ui E#"; this run's ids are its own.
- AI-tell evidence is restricted to 2023-2026; design-system values to current versions.
