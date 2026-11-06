# product-ui

One Claude Code plugin for web interfaces that read as a real product. It settles the design tokens and the wording before any markup exists, records who uses the product and composes each screen before building it from the regions production screens of its kind carry (its shell, its job, its dominant element, its reading order, its containers), decides whether each user-visible string should be on the screen at all, keeps every text at 14px or more (12px for a short Latin-only run), builds each container from a pattern drawn from production design systems, checks the output with deterministic scripts, and hands the rendered screen to an independent reviewer.

Seven ideas carry it:

- **Real screens are the standard.** `references/real-screens.md` records what production screens of eight kinds carry (work-tool and consumer collections, single records, forms, monitoring, Japanese public services, pricing and landing pages): their regions in reading order, the sizes they use and the strings they print. A screen is built with every region its kind always or usually shows, inside the product's shell: a header with the logo or the product name, the navigation, the create action, row links and pagination. The thresholds of the checks are set from measurements of the same 192 screens.
- **The screen is composed before it is built.** `tokens.json` records the user groups (role, frequency, expertise, job), and `ui-brief.md` records, before any markup, what each screen is for, what dominates, in what order it is read and which container each section gets. A container goes where production screens of the kind draw one, and a section is otherwise a heading on the page ground; records sit in a table or a list with rules between rows; a KPI tile row belongs to a monitoring screen. Scripts measure nested enclosures, spacing steps, emphasis levels, equal tile rows and generic or feature-shaped labels, and the reviewer answers eight cold-read questions from the screenshot before reading its parts.
- **Each container carries what its pattern names.** What a list row, a table, a card, a record's header, a status or an empty state shows comes from one of eleven patterns under `patterns/`, each drawn from what Polaris, GOV.UK, Primer, Carbon, DADS, SmartHR, Salesforce, Stripe, Baymard and NN/g publish about that component, with its sources. The brief ranks each object's properties by the reader's job; `resolve.py` picks the pattern for each section from a decision table and fills its slots from that ranking, `scaffold.py` writes the skeleton, and the same brief gives the same patterns and skeletons on every run. `check_pattern.py` (PT0–PT7) and the rendered review (R42–R48) report a container that drops a required slot, passes a limit, or shows a field the plan does not hold.
- **Tokens before markup.** Every colour, type, spacing, radius, shadow and motion value lands in `tokens.json` first, together with the 文体, the shape of a button label and the word for each operation. The implementation reads only those variables, and a script asks whether it did.
- **A string exists only if a product writer could defend it.** Explanatory captions, helper text under every field, self-describing screens, notes defending a number and placeholder filler are deleted. A ban list names each one, a script (ST1–ST10) catches what a pattern can settle, and an auditor agent reads the built text cold for the rest.
- **Every visible choice has a source.** Colours, type and the logo record where they came from (`meta.provenance`, `meta.logo`), the header shows the logo file or the product name as text and no logo mark is invented, a palette equal to the second set of AI defaults (cream and terracotta, near-black and acid green) with no recorded source fails, and one equal to a Tailwind default raises a warning to rule on. Proof on a screen (figures, testimonials, customer logos) comes from the brief's Proof section or stays off the screen, and a control that only shows a toast fails. The brief records each collection's empty, loading and error state before markup, and every warning from the scripts gets a ruling in the hand-over.
- **Text is 14px or more.** Body text is 16px, and a Latin-only run of at most 24 characters may go to 12px. The minimum is this plugin's own rule: production screens go below it on 168 of 192, and `references/real-screens.md` gives, for each role, the size they use and the size to build with. A script resolves each text run's size through the stylesheets, a PostToolUse hook in the plugin install runs it after every Write or Edit of a screen or stylesheet file, and the rendered review measures the computed size.

## Usage

Describe the screen in an ordinary request; the skill picks the mode and states it in its first line.

```
Build a settings page for notification preferences in our Next.js app
このダッシュボードの注釈と小さい文字を消して
Suggest a palette and font pairing for a B2B invoicing tool
```

| Request | Mode |
|---|---|
| Build, redesign or polish a screen, page, dashboard or component | STANDARD; DEEP when you say "thorough" or name two or more screens |
| One local change to an existing screen with tokens in place | LIGHT |
| Strip annotations, captions, helper text and small text from a screen that already has them | REMOVE |
| Palette, font pairing, visual style, chart type, UX rule or per-stack rule | answered from the lookup (`references/lookup.md`) |

## Install

```
/plugin marketplace add tomkd555/product-ui
/plugin install product-ui@product-ui
```

Without the plugin system, copy the skill and the agents by hand:

```
git clone https://github.com/tomkd555/product-ui
cp -r product-ui/plugins/product-ui/skills/product-ui ~/.claude/skills/
cp product-ui/plugins/product-ui/THIRD_PARTY_NOTICES.md product-ui/plugins/product-ui/LICENSE ~/.claude/skills/product-ui/
cp product-ui/plugins/product-ui/agents/*.md ~/.claude/agents/
```

A manual install runs every step, with the agents under their bare names (`review-design-lead` and so on); the write hook is the one piece it leaves out.

Requirements:

- **Python 3.9 or later** for the check scripts. The commands in the skill say `python`, which is `python3` on macOS and Linux.
- **Node 22 or later and a Chrome install** for the rendered review (Step 5). Each capture starts its own headless Chrome on a free debugging port (`CDP_PORT` fixes the port) and closes it when the capture ends. Without Node or Chrome the skill says `Step 5 skipped` and answers the review questions against the built files.
- **textlint**, optional. `assets/textlintrc.ui.json` needs `textlint`, `textlint-rule-preset-smarthr` and `@textlint-ja/textlint-rule-preset-ai-writing`.
- **A POSIX `sh`** to launch the hook, a Python script. Claude Code provides `sh` on Windows through Git Bash.

## What runs

| Step | What | Passes when |
|---|---|---|
| 0 Intake | Stack detection; at most four questions, in this order: the surface, the reference system, the screen structure (OOUI or task-oriented), the user groups and the brand (colour, typeface, logo) | none |
| 1 Tokens | `tokens.json`, colours derived, `voice` settled, `meta.users` and `meta.provenance` recorded; presets for デジタル庁デザインシステム and SmartHR | none |
| 2 Token check | `validate_tokens.py` (T1–T23: provenance, default colours, tinted neutrals, a Japanese face on Japanese screens, status words), then `generate_theme.py` writes `theme.css` with the type ramp and spacing unit computed from the tokens | exit 0, every warning ruled on |
| 3 Build | `ui-brief.md` first, with one composition plan per screen (its kind and regions from `references/real-screens.md`), the Objects table and each screen's Sections, and the Proof, States and Sample data sections; `scripts/patterns/resolve.py` picks each section's pattern and writes the Slots table, `scaffold.py` writes a skeleton per section; then shadcn/ui on Tailwind v4, or the preset's components; under the OOUI structure, the objects, views and navigation settled first; the ban list and the copy rules read before any string | none |
| 4 Output checks | `check_slop.py` (S1–S37: default palette classes, gradient text, glass, motion, template chrome, missing states, toast-only actions, pulsing New badges), `check_copy.py` (C1–C36: stock vocabulary, proof-shaped strings checked against the brief, English error filler and case, the label forms the patterns fix, the label register), `check_shippable_text.py` (ST1–ST10), `check_pattern.py` (PT0–PT7: each container against its pattern and the brief's Slots table), textlint and, when installed, prose-lint on the prose strings | all four scripts exit 0, every warning ruled on |
| 5 Review | `review-design-lead` renders at 1280 and 375px, measures the screen with `check_render.py` (R1–R48) and reads the composition cold against the brief; `shippable-text-auditor` reads the built text cold | every finding ruled on |
| 6 Hand-over | What was produced, what was kept under an allowance, what is open | none |

Outside the pipeline, `hooks/ui_text_lint.py` runs `check_shippable_text.py --checks ST7,ST8,ST10` after every Write or Edit of a `.html`, `.htm`, `.css`, `.scss`, `.jsx`, `.tsx`, `.vue`, `.svelte` or `.astro` file. The write has already happened when the hook runs; an error is reported back to Claude with the fix, up to three times per file.

## Contents

Paths are relative to `plugins/product-ui/`.

| Path | Holds |
|---|---|
| `skills/product-ui/SKILL.md` | The pipeline with its gates, the modes, the routing table, the hook |
| `skills/product-ui/references/` | `real-screens.md` (what production screens of each kind carry: regions, sizes, wording); `composition.md` (the composition plan, the shell, the container rule, the KPI tile rule, R4, R12–R15, R21, R22, R30, R32, R34–R37, R39, and the conditions of R1, R3, R5–R8, R10 and R19); `ban-list.md` (the bans, the size minimum, ST1–ST10); `ui-copy.md` (Japanese UI copy, the label forms, C1–C36, R23, R24, R38, R40, R48); `patterns.md` (the pattern format, the decision table, the brief's Objects, Sections and Slots, PV1–PV8, PT0–PT7, R42–R48); `ooui.md` (the object-oriented screen structure); `tokens-format.md` (T1–T23); `slop-checklist.md` (S1–S37, R16–R20, R25–R29, R31, R33, R41); `steering.md` (named adjustments of an existing screen); `stack-defaults.md`; `components.md`; `lookup.md`; the two preset mappings (`dads.md`, `smarthr.md`) and `dads-components.md` |
| `skills/product-ui/patterns/` | The eleven pattern files and `index.json`, the decision table |
| `skills/product-ui/scripts/` | `validate_tokens.py`, `generate_theme.py`, `check_slop.py`, `check_copy.py`, `check_shippable_text.py`, `check_pattern.py`, `lookup/search.py`; `patterns/validate.py`, `patterns/resolve.py`, `patterns/scaffold.py`; `harvest/specimen.py` and `harvest/compare.py`, which capture a component's structure from a permitted live page and compare it with a pattern; `render/cdp.js`, the headless-Chrome renderer, `render/check_render.py`, which measures its dumps, and `render/visibility.py`, the test both use for text a reader can see |
| `skills/product-ui/data/` | The lookup CSVs: palettes, pairings, styles, charts, UX rules, per-stack rules; `LICENSE.ui-ux-pro-max.txt` |
| `skills/product-ui/assets/` | The theme template, three example `tokens.json` files, the 長音 pair list C9 reads (`voice_terms.ja.json`), the brief template, the textlint config, the label register C36 reads (`label_register.ja.md`) |
| `agents/` | `review-design-lead`, `review-design-auditor`, `review-verifier`, `shippable-text-auditor` |
| `hooks/` | `ui_text_lint.py` and its `hooks.json` registration |

A citation of the form `research/<folder>` in the references names the maintainer's research notes, which are kept outside this repository.

## Companion skills

The routing table names skills published separately:

- landing-page layout: [`hallmark`](https://github.com/Nutlope/hallmark)
- interface polish and English copy: the [`interfaces` plugin](https://github.com/jakubkrehel/skills)
- the prose-shaped strings, besides textlint: [`prose-lint`](https://github.com/tomkd555/prose-lint), with `style=business`
- motion: `emil-design-eng`, `apple-design`, `find-animation-opportunities`, `improve-animations` and `review-animations`, in [emilkowalski/skills](https://github.com/emilkowalski/skills)

Where one is not installed, the skill does that row's work in the main session and says so.

## License

MIT, except the material below, which keeps its own licence (MIT or Apache-2.0).

product-ui is an independent project with no affiliation to or endorsement from the Digital Agency (デジタル庁) or SmartHR, Inc.; each preset uses the named system's token values published under the MIT licence ([tailwind-theme-plugin](https://github.com/digital-go-jp/tailwind-theme-plugin); [smarthr-ui](https://github.com/kufu/smarthr-ui)).

Paths in this list are relative to `plugins/product-ui/skills/product-ui/`.

- `data/` and `scripts/lookup/` come from [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), MIT, Copyright (c) 2024 Next Level Builder, in `data/LICENSE.ui-ux-pro-max.txt`, and are adapted to this plugin. Two rows are this plugin's own additions: row 75 of `data/typography.csv` and row 162 of `data/colors.csv`, which describe the DADS preset.
- The component patterns in `references/components.md` follow the examples in the [shadcn/ui documentation](https://ui.shadcn.com/docs), MIT, Copyright (c) 2023 shadcn.
- The `Button.tsx` excerpt in `references/dads-components.md` is from [design-system-example-components-react](https://github.com/digital-go-jp/design-system-example-components-react), MIT, Copyright (c) 2025 デジタル庁.
- `references/steering.md`, the detector rules S19 to S37, C31, C32 and R25 to R41, and the extensions of S3, S18, C22, T20, R4, R20 and R21 are adapted from [impeccable](https://github.com/pbakaus/impeccable), Apache-2.0, Copyright 2025 Paul Bakaus.
- The DADS token values come from [tailwind-theme-plugin](https://github.com/digital-go-jp/tailwind-theme-plugin), MIT, Copyright (c) 2023 デジタル庁, and the SmartHR token values from [smarthr-ui](https://github.com/kufu/smarthr-ui), MIT, Copyright 2018 SmartHR.

[`plugins/product-ui/THIRD_PARTY_NOTICES.md`](plugins/product-ui/THIRD_PARTY_NOTICES.md) holds the full licence text for each of these, and `plugins/product-ui/LICENSE` repeats this repository's licence, so both travel with an installed plugin; the manual install above copies both into the skill's directory.
