# Lookup — palettes, pairings, styles, charts, UX rules, per-stack rules

The data under `data/` (162 colour palettes, 75 font pairings, 84 visual styles, 25 chart types, 99 UX guidelines, and implementation rules for 22 stacks) came from the ui-ux-pro-max skill and is searched by `scripts/lookup/search.py`. It is a lookup, not a pipeline: the answer feeds Step 1 (tokens) or Step 3 (build) of `SKILL.md`, and the checks in Step 4 still apply to whatever it returned. In particular, a font size the data suggests is subject to the minimum in `references/ban-list.md` — 14px, 12px for a Latin-only run of at most 24 characters — because the CSVs are third-party data kept verbatim and rows in `typography.csv` and `styles.csv` carry 10px and 11px. Two rows are this plugin's own additions: row 75 of `typography.csv` (Japanese Government, Noto Sans JP) and row 162 of `colors.csv` (Government & Public Sector, Digital Agency DADS), both describing the DADS preset in `references/dads.md`.

Run the script with `python` on Windows (`python3` elsewhere); `{SKILL_DIR}` is this skill's directory.

## Design system in one call

```bash
python {SKILL_DIR}/scripts/lookup/search.py "<product type> <industry> <keywords>" --design-system [-p "Project Name"] [-f markdown]
```

Returns one block built from the product, style, color, landing and typography data: the product category, a landing-page pattern, a style, a palette, a font pairing, key effects, the anti-patterns `data/ui-reasoning.csv` lists for that category, and a pre-delivery checklist. Combine product, industry, tone and density in the query (`"entertainment social vibrant content-dense"`, not `"app"`). `--persist` writes it to `design-system/<project-slug>/MASTER.md`, where the slug is the `-p` name (or the query) lower-cased with spaces turned into hyphens; `--page "dashboard"` adds `design-system/<project-slug>/pages/dashboard.md`, a page override that inherits from the master.

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

## Per-stack rules

```bash
python {SKILL_DIR}/scripts/lookup/search.py "<keyword>" --stack <stack>
```

Stacks: `angular`, `astro`, `avalonia`, `flutter`, `html-tailwind`, `javafx`, `jetpack-compose`, `laravel`, `nextjs`, `nuxt-ui`, `nuxtjs`, `react-native`, `react`, `shadcn`, `svelte`, `swiftui`, `threejs`, `uno`, `uwp`, `vue`, `winui`, `wpf` — one CSV each under `data/stacks/`.

## When a result does not fit

Re-run with different keywords (`"playful neon"` → `"vibrant dark"` → `"content-first minimal"`) rather than editing the data. The web stack this skill builds with is settled in `references/stack-defaults.md`; a stack result from the lookup does not override it.
