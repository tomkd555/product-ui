# product-ui

product-ui is a Claude Code plugin for building web screens that look like they come from a real product. It settles the design tokens and the wording before it writes any markup. It then composes each screen from the regions that production screens of the same kind contain, and builds each container from a pattern taken from the design systems of real products. Scripts then check the output, and an independent reviewer agent renders the screen in Chrome and reviews it.

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

After a manual install, the skill still runs every step of its pipeline. The agents are named without the `product-ui:` prefix: `product-ui:review-design-lead` becomes `review-design-lead`. The one piece a manual install leaves out is the hook that checks text size after each Write or Edit.

### Requirements

- **Python 3.9 or later** for the check scripts
- **Node 22 or later and Chrome** to render the screen for the review. If either is missing, the reviewer agent reads the files the skill wrote, without rendering them.
- **textlint**, optional, to lint the sentences in the UI copy. `assets/textlintrc.ui.json` needs `textlint`, `textlint-rule-preset-smarthr` and `@textlint-ja/textlint-rule-preset-ai-writing`.
- **A POSIX `sh`** to launch the hook. Claude Code provides `sh` on Windows through Git Bash.

## Usage

Describe the screen in plain words. The skill picks a mode and names it in the first line of its reply.

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
| Palette, font pairing, visual style, chart type, UX rule or per-stack rule | No mode: the answer comes from the lookup data |

## How it works

The skill runs these steps in order:

| Step | What the step does |
|---|---|
| 0 Intake | Detects the stack, then asks at most four questions: one each about the surface, the reference design system and the screen structure (object-oriented, OOUI, or task-oriented), and one about the user groups and the brand |
| 1 Tokens | Writes `tokens.json` with every value for colour, type, spacing, radius, shadow and motion, the writing style (文体) and the verb the UI uses for each action. Presets exist for the Digital Agency Design System (デジタル庁デザインシステム) and SmartHR |
| 2 Token check | `validate_tokens.py` checks the tokens, then `generate_theme.py` writes `theme.css` |
| 3 Build | Writes `ui-brief.md` first, with one composition plan per screen. Scripts pick each section's pattern and write its skeleton. The screen is then built with shadcn/ui on Tailwind v4, or with the preset's components |
| 4 Output checks | Scripts flag default-looking styling, check the UI copy, find strings a product would never ship and check each container against its pattern |
| 5 Review | `review-design-lead` renders the screen at 1280px and 375px, measures it and compares the composition with the brief. `shippable-text-auditor` then reads the built text for such strings that the scripts cannot match by pattern |
| 6 Hand-over | Reports what was produced, which warnings were accepted and why, and what remains open |

### Rules

- **Real screens are the benchmark.** `references/real-screens.md` records what production screens of each kind contain: their regions, the sizes they use and the strings they show.
- **A string exists only if a product writer could defend it.** The skill deletes explanatory captions, helper text placed under every field and notes that justify a number.
- **Every visible choice has a source.** The skill records where each colour, typeface and logo came from. Proof on a screen, such as figures, testimonials and customer logos, comes from the Proof section of `ui-brief.md`.
- **Text is 14px or more, with one exception.** Body text is 16px. The exception is a short run of Latin-only text, which may go down to 12px. A hook checks the size after every Write or Edit of a screen or stylesheet file.

`plugins/product-ui/skills/product-ui/SKILL.md` describes the full pipeline.

## Companion skills

The skill hands some work to companion skills that are published separately:

- landing-page layout: [`hallmark`](https://github.com/Nutlope/hallmark)
- interface polish and English copy: the [`interfaces` plugin](https://github.com/jakubkrehel/skills)
- the sentences in the UI copy, alongside textlint: [`prose-lint`](https://github.com/tomkd555/prose-lint)
- motion: the skills in [emilkowalski/skills](https://github.com/emilkowalski/skills)

Where a companion skill is not installed, the skill does that work in the main session and says so.

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
