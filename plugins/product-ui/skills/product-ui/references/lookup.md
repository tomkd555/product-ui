# Lookup: palettes, pairings, styles, charts, UX rules, per-stack rules

`scripts/lookup/search.py` searches the data under `data/`, which came from the ui-ux-pro-max skill and was adapted to this plugin: colour palettes, font pairings, visual styles, chart types, UX guidelines, and implementation rules per stack. It answers one question at a time; the answer feeds Step 1 (tokens) or Step 3 (build) of `SKILL.md`, and the Step 4 checks still apply to whatever it returned.

- **Font sizes**: the CSV recommendations below 14px were raised to 14px (`text-sm`), and to 12px where the row says the size is for a Latin-only label. `references/ban-list.md` holds the minimum: 14px, 12px for a Latin-only run of at most 24 characters. Sizes in `pt` (mobile rows) are unchanged.
- **Output vocabulary**: colour rows print `oklch(...)` and the `tokens.json` key they fill (`color.primary`, `color.primary_foreground`, `color.accent` painted by the `brand-accent` utility, and so on); MASTER.md uses `--color-primary-foreground` and `--color-brand-accent`. Secondary and Ring have no slot and are not printed.
- **This plugin's rows**: row 75 of `typography.csv` (Japanese Government, Noto Sans JP) and row 162 of `colors.csv` (Government & Public Sector, Digital Agency DADS), both describing the DADS preset in `references/dads.md`.

Run the script with `python` on Windows (`python3` elsewhere); `{SKILL_DIR}` is this skill's directory.

## Design system in one call

```bash
python {SKILL_DIR}/scripts/lookup/search.py "<product type> <industry> <keywords>" --design-system [-p "Project Name"] [-f markdown] [--surface saas|lp|desktop] [--lang ja]
```

Returns one block built from the product, style, color, landing and typography data: the product category, a palette, a font pairing, the anti-patterns `data/ui-reasoning.csv` lists for that category, and a pre-delivery checklist. With `--surface lp` the block also holds a landing-page pattern, a style and key effects. With `--surface desktop` the product match leans to the productivity, editor and office tool types (`Productivity Tool`, `Notes & Writing App`, `Developer Tool / IDE`, `Scanner & Document Manager`, `Photo Editor & Filters`, `Short Video Editor`): the query takes the words `productivity editor document tool`, and those rows come first. The block's typography is left unused on `desktop`: Step 1 writes the face `references/desktop.md` fixes. Combine product, industry, tone and density in the query (`"entertainment social vibrant content-dense"`).

- `--surface {saas,lp,desktop}` selects the kind of screen. An application screen (an issue list, a dashboard, a ticket view, a settings page, a sign-up form) uses `--surface saas`, the default. A landing page uses `--surface lp`. An application in its own window (`references/desktop.md`) uses `--surface desktop`: it ranks the productivity and editor product types first, and its typography block names the window's fixed faces, Segoe UI Variable and Yu Gothic UI.
- `--lang ja` limits the font pairing to rows whose heading or body family is listed in `assets/ja_families.json`, ranked by the query; a query that matches none of them takes the best-ranked Japanese row. With `--domain typography` it filters the results the same way.
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

The CSVs give hex values from Tailwind's default palette. The design-system output converts them to oklch and prints the `tokens.json` key each fills. `background`, `foreground`, `muted` and `border` take the primary hue and cap chroma at 0.012 (rule 1 in `references/tokens-format.md`). `background` is printed as `oklch(100% 0 0)` and `foreground` at a lightness of 30% or under, as production screens set them (`references/real-screens.md`, Every screen); `muted` and `border` keep the CSV lightness; `muted_foreground` is derived from `foreground` at lightness 52%.

- A primary or accent that lies within ΔE_OK 0.02 of an entry in `assets/default_colours.json` is marked with the Tailwind step it equals. T20 warns on it unless its `meta.provenance` starts with `brand:`, `reference:` or `user:`: keep the lookup's colour with a ruling in the hand-over, or take the printed value; the output prints the value for `tokens.json` beside it: the same hue and chroma at the nearest darker lightness that matches no default and, for the primary, keeps 4.5:1 under the On Primary text. `--domain color` prints the same value in `Primary note` and `Accent note`.
- The ground is light unless the request asks for a dark interface: production screens set a white ground on 146 of 192 and a dark one on 17 (`references/real-screens.md`, Every screen). A row whose ground is dark is printed for a light screen: a white ground, text at 25%, `muted` at 96% and `border` at 90%, at the row's hue.
- `color.primary` paints the filled buttons and the links. Where the lookup's Primary has a lightness under 30%, it reads as text beside the foreground: take the Accent/CTA as `color.primary` and derive the neutrals at that hue (rule 1 of "Deriving the colours"). `color.accent` then takes a second hue derived from the new primary, recorded as `derived:` in `meta.provenance`, as the example in `references/tokens-format.md` does. Production screens paint a control with a chromatic fill on 132 of 192.
- On `desktop`, `color.primary` also meets 3:1 against `muted`: the selected tab's 3px bar sits on the tab row, which takes `muted` (`references/desktop.md`, Look). Where the chosen colour fails, lower its lightness in steps of 0.05 until it passes (in the dark theme, where `muted` is the darker of the two, raise it instead). Check the pair with `python {SKILL_DIR}/scripts/colour.py contrast "<primary>" "<muted>"`.
- The pattern and style blocks of `--surface lp` are candidates the Step 4 checks still judge. The sections of a landing or pricing page and their order come from `references/real-screens.md`.
- The accent row is a candidate hue for `color.accent`, painted by the `brand-accent` utility; the CTA colour is also a candidate for `color.primary`. An accent that reaches 4.5:1 with neither `foreground` nor white carries no text: it paints graphics that need 3:1 against the ground (a rating's stars, an icon, a rule), and a filled surface under text takes the lightness that reaches 4.5:1 with its text.

## Per-stack rules

```bash
python {SKILL_DIR}/scripts/lookup/search.py "<keyword>" --stack <stack>
```

Stacks: `angular`, `astro`, `avalonia`, `flutter`, `html-tailwind`, `javafx`, `jetpack-compose`, `laravel`, `nextjs`, `nuxt-ui`, `nuxtjs`, `react-native`, `react`, `shadcn`, `svelte`, `swiftui`, `threejs`, `uno`, `uwp`, `vue`, `winui`, `wpf` (one CSV each under `data/stacks/`).

## When a result does not fit

A result fits when its product type or its keywords name the product's field (会計, 物流, a shop) or its kind of screen. Re-run with different keywords (`"playful neon"` → `"vibrant dark"` → `"content-first minimal"`), or with the field's own words, when the first row names another field.

- **Japanese pairings**: the data holds two, and `--lang ja` returns them whatever the query. Noto Sans JP in both slots is the pairing to take for an application screen: it is the family production Japanese screens name most often (22 of the 69 that name a Japanese family). The row's mood words describe where the row came from and bind nothing.
- **Font pairings**: `--domain typography` marks a pairing whose heading or body family is on the T5 forbidden list with a `Rejected` field, and `--design-system` takes the next pairing that passes.
- **Effects**: where a style's effects name glass or backdrop blur, gradient text or a purple gradient, the output names the check that warns on it (S13, S12, S3). The web stack this skill builds with is settled in `references/stack-defaults.md`, and it takes precedence over a stack result from the lookup.
