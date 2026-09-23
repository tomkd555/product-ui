# product-ui

One Claude Code plugin for web interfaces that read as a real product. It settles the design tokens and the wording before any markup exists, decides whether each user-visible string should be on the screen at all, keeps every text at 14px or more (12px for a short Latin-only run), checks the output with deterministic scripts, and hands the rendered screen to an independent reviewer.

Three ideas carry it:

- **Tokens before markup.** Every colour, type, spacing, radius, shadow and motion value — and the 文体, the shape of a button label and the word for each operation — lands in `tokens.json` first; the implementation reads only those variables, and a script asks whether it did.
- **A string exists only if a product writer could defend it.** Explanatory captions, helper text under every field, self-describing screens, notes defending a number and placeholder filler do not ship. A ban list names each one, a script (ST1–ST10) catches what a pattern can settle, and an auditor agent reads the built text cold for the rest.
- **Nothing below the minimum size.** Body text 16px, minimum 14px, 12px only for a Latin-only run of at most 24 characters. The checker resolves each text run's size through the stylesheets and the cascade (`references/ban-list.md` lists what it leaves to the rendered review), a PostToolUse hook in the plugin install runs it after every write and reports errors back to Claude, and the rendered review measures the computed size.

## When to use it

| Request | Mode |
|---|---|
| Build, redesign or polish a screen, page, dashboard or component | STANDARD, or DEEP for a whole surface |
| One local change to an existing screen with tokens in place | LIGHT |
| Strip annotations, captions, helper text and small text from a screen that already has them | REMOVE |
| Palette, font pairing, visual style, chart type, UX rule or per-stack rule | the lookup (`references/lookup.md`) |

## Usage

Describe the screen in an ordinary request; the skill picks the mode and states it in its first line.

```
Build a settings page for notification preferences in our Next.js app
このダッシュボードの注釈と小さい文字を消して
Suggest a palette and font pairing for a B2B invoicing tool
```

The first two start STANDARD and REMOVE; the third is answered from the lookup. Say "thorough" or name several screens for DEEP.

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

Python 3.9 or later is required for the check scripts; the commands in the skill say `python`, which is `python3` on macOS and Linux. Node 22 or later and a Chrome install are required for the rendered review (Step 5), which starts headless Chrome on debugging port 9333 (`CDP_PORT` overrides it) and stops the Chrome it started when each capture ends; on Windows it first stops any `chrome.exe` running with `--remote-debugging-port` set to that port, which is one left over from an interrupted run; without them the skill says `Step 5 skipped` and answers the review questions against the built files. textlint is optional; `assets/textlintrc.ui.json` needs `textlint`, `textlint-rule-preset-smarthr` and `@textlint-ja/textlint-rule-preset-ai-writing`. The hook is a Python script launched through a POSIX `sh`, which Claude Code provides on Windows through Git Bash.

## What runs

| Step | What | Passes when |
|---|---|---|
| 0 Intake | Stack detection; at most three questions | — |
| 1 Tokens | `tokens.json`, colours derived, `voice` settled; presets for デジタル庁デザインシステム and SmartHR | — |
| 2 Token check | `validate_tokens.py` (T1–T17), then `generate_theme.py` writes `theme.css` with a `--text-*` scale that starts at 12px | exit 0 |
| 3 Build | shadcn/ui on Tailwind v4 (`references/components.md`), or the preset's components; `references/ban-list.md` and `references/ui-copy.md` read before any string | — |
| 4 Output checks | `check_slop.py` (S1–S10), `check_copy.py` (C1–C16), `check_shippable_text.py` (ST1–ST10), textlint on the prose strings | all three scripts exit 0, every warning ruled on |
| 5 Review | `review-design-lead` renders at 1280 and 375px and measures the screen with `check_render.py` (R1–R11, R7 is the size minimum); `shippable-text-auditor` reads the built text cold | every finding ruled on |
| 6 Hand-over | What was produced, what was kept under an allowance, what is open | — |

Outside the pipeline, `hooks/ui_text_lint.py` runs `check_shippable_text.py --checks ST7,ST8,ST10` after every Write or Edit of a `.html`, `.htm`, `.css`, `.scss`, `.jsx`, `.tsx`, `.vue`, `.svelte` or `.astro` file. The write has already happened when the hook runs; an error is reported back to Claude with the fix, up to three times per file.

## Contents

| Path | Holds |
|---|---|
| `plugins/product-ui/skills/product-ui/SKILL.md` | The pipeline, the modes, the routing table, the hook, the gates |
| `plugins/product-ui/skills/product-ui/references/` | `ban-list.md` (the bans, the size minimum, ST1–ST10); `ui-copy.md` (Japanese UI copy, C1–C16); `tokens-format.md` (T1–T17); `slop-checklist.md` (S1–S10); `stack-defaults.md`; `components.md`, which links the official shadcn/ui, Base UI and Tailwind documentation; `lookup.md`; the two preset mappings (`dads.md`, `smarthr.md`) and `dads-components.md` |
| `plugins/product-ui/skills/product-ui/scripts/` | `validate_tokens.py`, `generate_theme.py`, `check_slop.py`, `check_copy.py`, `check_shippable_text.py`, `lookup/search.py` |
| `plugins/product-ui/skills/product-ui/scripts/render/` | `cdp.js`, the headless-Chrome renderer, and `check_render.py`, which measures its dumps |
| `plugins/product-ui/skills/product-ui/data/` | The lookup CSVs: palettes, pairings, styles, charts, UX rules, 22 stacks; `LICENSE.ui-ux-pro-max.txt` |
| `plugins/product-ui/skills/product-ui/assets/` | The theme template, three example `tokens.json` files, the 長音 pair list C9 reads (`voice_terms.ja.json`), the brief template, the textlint config |
| `plugins/product-ui/agents/` | `review-design-lead`, `review-design-auditor`, `review-verifier`, `shippable-text-auditor` |
| `plugins/product-ui/hooks/` | `ui_text_lint.py` and its `hooks.json` registration |

## Companion skills

The routing table names skills published separately:

- landing-page structure: [`hallmark`](https://github.com/Nutlope/hallmark)
- interface polish and English copy: the [`interfaces` plugin](https://github.com/jakubkrehel/skills)
- motion: `emil-design-eng`, `apple-design`, `find-animation-opportunities`, `improve-animations` and `review-animations`, in [emilkowalski/skills](https://github.com/emilkowalski/skills)

Where one is not installed, the skill does that row's work in the main session and says so.

## License

MIT, except the material below.

product-ui is an independent project with no affiliation to or endorsement from the Digital Agency (デジタル庁) or SmartHR, Inc.; each preset uses the named system's token values published under the MIT licence ([tailwind-theme-plugin](https://github.com/digital-go-jp/tailwind-theme-plugin); [smarthr-ui](https://github.com/kufu/smarthr-ui)).

Paths in this list are relative to `plugins/product-ui/skills/product-ui/`.

- `data/` and `scripts/lookup/` come from [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), MIT, Copyright (c) 2024 Next Level Builder, in `data/LICENSE.ui-ux-pro-max.txt`. Two rows are this plugin's own additions: row 75 of `data/typography.csv` and row 162 of `data/colors.csv`, which describe the DADS preset.
- The component patterns in `references/components.md` follow the examples in the [shadcn/ui documentation](https://ui.shadcn.com/docs), MIT, Copyright (c) 2023 shadcn.
- The `Button.tsx` excerpt in `references/dads-components.md` is from [design-system-example-components-react](https://github.com/digital-go-jp/design-system-example-components-react), MIT, Copyright (c) 2025 デジタル庁.
- The DADS token values come from [tailwind-theme-plugin](https://github.com/digital-go-jp/tailwind-theme-plugin), MIT, Copyright (c) 2023 デジタル庁, and the SmartHR token values from [smarthr-ui](https://github.com/kufu/smarthr-ui), MIT, Copyright 2018 SmartHR.

[`plugins/product-ui/THIRD_PARTY_NOTICES.md`](plugins/product-ui/THIRD_PARTY_NOTICES.md) holds the full licence text for each of these, and `plugins/product-ui/LICENSE` repeats this repository's licence, so both travel with an installed plugin; the manual install above copies both into the skill's directory.
