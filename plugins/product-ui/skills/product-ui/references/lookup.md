# Lookup: palettes, pairings, styles, charts, UX rules, per-stack rules

`scripts/lookup/search.py` searches the data under `data/`, which came from the ui-ux-pro-max skill and was adapted to this plugin: colour palettes, font pairings, visual styles, chart types, UX guidelines, and implementation rules per stack. It answers one question at a time; the answer feeds Step 1 (tokens) or Step 3 (build) of `SKILL.md`, and the Step 4 checks still apply to whatever it returned.

- **Font sizes**: the CSV recommendations below 14px were raised to 14px (`text-sm`), and to 12px where the row says the size is for a Latin-only label. `references/ban-list.md` holds the minimum: 14px, 12px for a Latin-only run of at most 24 characters. Sizes in `pt` (mobile rows) are unchanged.
- **Output vocabulary**: colour rows print `oklch(...)` and the `tokens.json` key they fill (`color.primary`, `color.primary_foreground`, `color.accent` painted by the `brand-accent` utility, and so on); MASTER.md uses `--color-primary-foreground` and `--color-brand-accent`. Secondary and Ring have no slot and are not printed.
- **This plugin's rows**: row 75 of `typography.csv` (Japanese Government, Noto Sans JP) and row 162 of `colors.csv` (Government & Public Sector, Digital Agency DADS), both describing the DADS preset in `references/dads.md`.

Run the script with `python` on Windows (`python3` elsewhere); `{SKILL_DIR}` is this skill's directory.

## Design system in one call

```bash
python {SKILL_DIR}/scripts/lookup/search.py "<product type> <industry> <keywords>" --design-system [-p "Project Name"] [-f markdown]
```

Returns one block built from the product, style, color, landing and typography data: the product category, a landing-page pattern, a style, a palette, a font pairing, key effects, the anti-patterns `data/ui-reasoning.csv` lists for that category, and a pre-delivery checklist. Combine product, industry, tone and density in the query (`"entertainment social vibrant content-dense"`).

- `--persist` writes it to `design-system/<project-slug>/MASTER.md`, where the slug is the `-p` name (or the query) lower-cased with spaces turned into hyphens.
- `--page "dashboard"` adds `design-system/<project-slug>/pages/dashboard.md`, a page override that inherits from the master.

## One dimension at a time

```bash
python {SKILL_DIR}/scripts/lookup/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

| Domain | Use for | Example keywords |
|---|---|---|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI styles, colours, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairings | elegant, playful, professional, modern |
| `color` | Palettes by product type | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | Page structure, CTA strategies | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | Chart types, library choice | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading |
| `web` | Mobile app interface guidelines (iOS / Android / React Native), despite the keyword | accessibilityLabel, touch targets, safe areas, Dynamic Type |
| `icons` | Icon sets and usage | outline, filled, brand |

## Colours

The CSVs give hex values from Tailwind's default palette. The design-system output converts them to oklch and prints the `tokens.json` key each fills. `background`, `foreground`, `muted` and `border` keep the CSV lightness, take the primary hue and cap chroma at 0.012 (rule 1 in `references/tokens-format.md`); `muted_foreground` is derived from `foreground` at lightness 52%.

- A primary or accent that lies within ΔE_OK 0.02 of an entry in `assets/default_colours.json` is marked with the Tailwind step it equals. T20 rejects it unless its `meta.provenance` starts with `brand:`, `reference:` or `user:`; keep the hue and move lightness or chroma until the match clears.
- The accent row is a candidate hue for `color.accent`, painted by the `brand-accent` utility; the CTA colour is also a candidate for `color.primary`.

## Per-stack rules

```bash
python {SKILL_DIR}/scripts/lookup/search.py "<keyword>" --stack <stack>
```

Stacks: `angular`, `astro`, `avalonia`, `flutter`, `html-tailwind`, `javafx`, `jetpack-compose`, `laravel`, `nextjs`, `nuxt-ui`, `nuxtjs`, `react-native`, `react`, `shadcn`, `svelte`, `swiftui`, `threejs`, `uno`, `uwp`, `vue`, `winui`, `wpf` (one CSV each under `data/stacks/`).

## When a result does not fit

Re-run with different keywords (`"playful neon"` → `"vibrant dark"` → `"content-first minimal"`).

- **Font pairings**: `--domain typography` marks a pairing whose heading or body family is on the T5 forbidden list with a `Rejected` field, and `--design-system` takes the next pairing that passes.
- **Effects**: where a style's effects name glass or backdrop blur, gradient text, `transition: all` or a purple gradient, the output names the check that warns on it (S13, S12, S14, S3). The web stack this skill builds with is settled in `references/stack-defaults.md`, and it takes precedence over a stack result from the lookup.
