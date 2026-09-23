# SmartHR Design System and smarthr-ui

product-ui is an independent project with no affiliation to or endorsement from SmartHR, Inc.; this preset uses the token values published in `smarthr-ui` (https://github.com/kufu/smarthr-ui) under the MIT licence.

The design system SmartHR publishes at https://smarthr.design/, and `smarthr-ui`, the React component library
that implements it. `smarthr-ui` is MIT-licensed (© 2018 SmartHR). The content of smarthr.design is © SmartHR
under its own terms (https://smarthr.design/terms/), which reserve copyright and ask users to refrain from
redistributing it; the design system repository, `kufu/smarthr-design-system`, carries no licence file. This file is the source of record for the SmartHR route: read it in
Step 1 whenever `meta.reference` is `"smarthr"`, and in Step 3 before writing markup.

Choosing SmartHR replaces the usual token derivation, exactly as the DADS route does. The palette, the type
scale, the spacing scale and the components are already decided, so Step 1 maps the published values and no
screenshot reading takes place.

It also replaces most of Step 3. SmartHR ships an official Claude Code plugin holding a guide for each of its
components and design patterns (104 and 22 as of September 2026), so the components are documented in that plugin — install it and read
its guides.

## Resources

| What | Where |
|---|---|
| Design system site | https://smarthr.design/ |
| Component library | `smarthr-ui` on npm — https://github.com/kufu/smarthr-ui |
| Component gallery (Storybook) | https://story.smarthr-ui.dev |
| Design tokens | https://smarthr.design/products/design-tokens/ |
| Writing guidelines | https://smarthr.design/products/contents/ |
| Accessibility guidelines | https://smarthr.design/accessibility/guidelines/ |
| Design system repository | https://github.com/kufu/smarthr-design-system |
| Claude Code plugin | the `plugins/smarthr-design-system` directory of that repository |

Versions this file was written against, as of September 2026: `smarthr-ui` 99.2.0, plugin 0.6.0.

## The official plugin

```
/plugin marketplace add kufu/smarthr-design-system
/plugin install smarthr-design-system@smarthr-design-system
```

It carries two skills:

- `component-guidelines` — one guide per component, each holding the props and types generated from
  `smarthr-ui/metadata.json`, the Do and Don't drawn from `eslint-plugin-smarthr`, and a usage checklist. A
  `component-selector.md` maps a UI requirement onto the component that serves it.
- `design-pattern-guidelines` — page layout, table, list, wizard, delete dialog, empty data, feedback,
  permission settings and fifteen more.

Step 3 routes there for every component on this route. Where the plugin is not installed, tell the user the two
commands above; component APIs come from those guides alone — the props move between versions, and
each guide names the `smarthr-ui` version it was generated against.

## The stack

`smarthr-ui` is a React component library with `styled-components` as a peer dependency, and it ships its own
compiled stylesheet:

```tsx
import { createTheme, ThemeProvider, Button } from 'smarthr-ui'
import 'smarthr-ui/smarthr-ui.css'
```

Peer dependencies are `react`, `react-dom`, `react-intl` and `styled-components`. `createTheme()` takes
overrides for the colour, font-size, spacing, radius and shadow themes; calling it bare gives the published
defaults, which is what this route assumes.

Internally the library is built with Tailwind v3 under the `shr-` prefix, and `smarthr-ui.css` is that build,
already compiled. So the product's own Tailwind stays at v4 and `meta.stack.tailwind` stays `"4"`.

**The product never writes a `shr-` class.** Component styling arrives compiled in `smarthr-ui.css`; the
product's own layout uses the v4 utilities its `theme.css` generates. Authoring `shr-` utilities would mean
loading `smarthr-ui/smarthr-ui-preset` into a Tailwind v3 config, which is out of this skill's scope.

Import `smarthr-ui.css` after the Tailwind entry point. The library disables Tailwind's preflight and supplies
its own base layer — the body font, the margin resets, `text-spacing-trim` — and that layer has to land after
v4's preflight to survive it.

Set `meta.stack.base` to `smarthr-ui`: the component base on this route is the library itself.

## Token mapping

SmartHR ships hex, and rule T2 requires `oklch()`. These are the nine required keys of `tokens.json` and the optional `surface`, converted from the
published semantic tokens with the Oklab transform. Use them verbatim.

| `tokens.json` | SmartHR token | hex | oklch |
|---|---|---|---|
| `background` | `BACKGROUND` | `#f8f7f6` | `oklch(97.7% 0.002 68)` |
| `foreground` | `TEXT_BLACK` | `#23221e` | `oklch(25.2% 0.008 95)` |
| `surface` | `WHITE` | `#ffffff` | `oklch(100% 0 0)` |
| `primary` | `MAIN` | `#0077c7` | `oklch(55.7% 0.152 248)` |
| `primary_foreground` | `TEXT_WHITE` | `#ffffff` | `oklch(100% 0 0)` |
| `muted` | `HEAD` | `#edebe8` | `oklch(94.1% 0.005 78)` |
| `muted_foreground` | `TEXT_GREY` | `#706d65` | `oklch(53.5% 0.013 90)` |
| `border` | `BORDER` | `#d6d3d0` | `oklch(86.8% 0.005 68)` |
| `destructive` | `DANGER` | `#e01e5a` | `oklch(58.8% 0.222 11)` |
| `accent` | `BRAND` | `#00c4cc` | `oklch(74.6% 0.127 200)` |

Why these values:

- SmartHR separates the page ground from the panel ground: `BACKGROUND` `#f8f7f6` is the screen, and panels
  drawn with `Base` sit on `WHITE`. Both enter `tokens.json` — the screen as `background`, the panel as the
  optional `surface` key — so a panel the product builds itself lands on the same white the library's own
  components do. Text on either is `foreground`.
- `muted` takes `HEAD`. The neighbouring grey, `OVER_BACKGROUND` `#f2f1f0`, sits 1.8% in lightness away
  from `BACKGROUND`, which is too little to read as a distinct surface; `HEAD`, the table-header ground, is the
  one grey that separates.
- `accent` takes `BRAND` `#00c4cc`, the SmartHR blue. It is the only non-`MAIN` hue the system carries as an
  identity colour, and the Tailwind preset exposes it as `bg-brand`. It is light: text on top of it must be
  `foreground`.
- `WARNING_YELLOW` `#ffcc17` has no slot among these ten keys. It stays in the library, where the components that
  need it already paint it.

Everything else:

| Field | Value | Source |
|---|---|---|
| `radius.sm` / `md` / `lg` / `full` | `0.25rem` / `0.375rem` / `0.5rem` / `9999px` | `s` 4px, `m` 6px, `l` 8px, and the preset's `full` |
| `shadow.sm` / `md` / `lg` | `LAYER1/2/3`, with `rgba(3,3,2,0.3)` rewritten as `oklch(9.6% 0.005 107 / 0.3)` | `defaultShadow` |
| `typography.display.family` and `body.family` | `system-ui` | published as `font-family: system-ui, sans-serif` |
| `typography.scale.ratio` / `base_px` | `1.2` / `16` | see below |
| `spacing.base_px` / `steps` | `4` / `[1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 32]` | the char-relative scale at 16px per character |
| `motion` | product-ui's own default | SmartHR publishes no motion tokens |
| `color_dark` | omitted | SmartHR publishes no dark theme |
| `voice` | product-ui's own default | `references/ui-copy.md` — see below |

`scale.ratio` is an approximation. SmartHR's font sizes come from `6 / (6 + d)`, which gives 0.667, 0.75,
0.857, 1, 1.2, 1.5 and 2rem — a harmonic series, where each neighbouring pair sits at a different ratio (1.2,
1.25, 1.333 above the base). `1.2` is the closest single geometric ratio, and the `Text` component's `size`
prop sets the real sizes.

Spacing is char-relative: one unit is one character at the 16px base size, and the published tokens run
0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 3.5, 4 and 8 characters. Written as multiples of 4px, that is the
`steps` array above.

Four entries belong in `meta.defaults_applied` on this route, so each departure from the preset carries its reason:

- `"color_dark omitted — SmartHR publishes no dark theme"`
- `"motion left at the product-ui default — SmartHR publishes no motion tokens"`
- `"T5 warning accepted — system-ui is the font family smarthr-ui ships"`
- `"T10 warning accepted — SmartHR LAYER1/2/3 all use alpha 0.3, and only the offset and blur differ"`

`assets/tokens_example.smarthr.json` is this mapping written out in full.

## The font is a deliberate decision

T5 and S2 both treat `system-ui` as the mark of a font nobody chose. On this route it is a value copied from
the reference: `smarthr-ui` ships `font-family: system-ui, sans-serif` in its base layer, and the OS then
renders each language with its own UI font. T5 falls to a warning whenever `meta.reference` is set, which
covers it.

S2 reads the built output alone, so keep the family out of the markup and let
`smarthr-ui.css` set the body font. The one place the family is recorded is `tokens.json`; the next section
generates a `theme.css` that leaves it out.

## Wording

The `voice` block and the rules in `references/ui-copy.md` apply on this route as written; the project settles
its own `voice.terms` there.

For further reading, the design system publishes its writing style, its UI text guidance and its 用字用語 at
https://smarthr.design/products/contents/. The `preset-smarthr` textlint rules in Step 4 check 用字用語 against
that guidance.

## theme.css

The standard template writes the family in quotes — `"system-ui", ui-serif, serif` for `h1`–`h3` — and a
quoted `"system-ui"` is read as a font name, so headings would fall through to a serif. Generate from a project
copy of the template instead, through the generator's `--template` option:

1. Copy `assets/theme.template.css` beside `tokens.json` as `theme.template.css`.
2. In the copy, delete the `--font-display` and `--font-body` lines from the `@theme inline` block, and the two
   `font-family` declarations from the base layer.
3. Run `python {SKILL_DIR}/scripts/generate_theme.py tokens.json --template theme.template.css`.

Each regeneration reads the project copy, so `theme.css` is still never edited by hand. Load the two
stylesheets in this order:

```tsx
import './theme.css'
import 'smarthr-ui/smarthr-ui.css'
```

`check_slop.py` reads every `oklch()` literal out of the generated file, so S1 keeps working: a raw
`#0077c7` written into markup still fails, which is the intended outcome. Use the component or the utility
class.
