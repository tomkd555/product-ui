# SmartHR Design System and smarthr-ui

product-ui is an independent project with no affiliation to or endorsement from SmartHR, Inc.; this preset uses the token values published in `smarthr-ui` (https://github.com/kufu/smarthr-ui) under the MIT licence.

The design system SmartHR publishes at https://smarthr.design/, and `smarthr-ui`, the React component library that implements it. `smarthr-ui` is MIT-licensed (© 2018 SmartHR). The content of smarthr.design is © SmartHR under its own terms (https://smarthr.design/terms/), which reserve copyright and ask users to refrain from redistributing it; the design system repository, `kufu/smarthr-design-system`, carries no licence file. Read this file in Step 1 whenever `meta.reference` is `"smarthr"`, and in Step 3 before writing markup.

SmartHR has already settled the palette, the type scale, the spacing scale and the components, so Step 1 maps the published values and reads no screenshot. For the components, Step 3 reads SmartHR's official Claude Code plugin, which holds a guide for each of its components and design patterns.

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

Written against, as of September 2026: `smarthr-ui` 99.2.0, plugin 0.6.0.

## The official plugin

```
/plugin marketplace add kufu/smarthr-design-system
/plugin install smarthr-design-system@smarthr-design-system
```

It carries two skills:

- `component-guidelines` — one guide per component, each holding the props and types generated from `smarthr-ui/metadata.json`, the Do and Don't drawn from `eslint-plugin-smarthr`, and a usage checklist. A `component-selector.md` maps a UI requirement onto the component that serves it.
- `design-pattern-guidelines` — page layout, table, list, wizard, delete dialog, empty data, feedback, permission settings and the rest of the pattern guides.

Step 3 routes there for every component on this route. When the plugin is missing, give the user the two commands above. Component APIs come from those guides alone, because the props move between versions and each guide names the `smarthr-ui` version it was generated against.

## The stack

`smarthr-ui` is a React library with peer dependencies `react`, `react-dom`, `react-intl` and `styled-components`, and it ships its own compiled stylesheet:

```tsx
import { createTheme, ThemeProvider, Button } from 'smarthr-ui'
import 'smarthr-ui/smarthr-ui.css'
```

`createTheme()` takes overrides for the colour, font-size, spacing, radius and shadow themes; this route calls it bare, which gives the published defaults.

- **Tailwind stays at v4.** The library is built internally with Tailwind v3 under the `shr-` prefix, and `smarthr-ui.css` is that build, compiled. `meta.stack.tailwind` stays `"4"`.
- **The product never writes a `shr-` class.** Component styling arrives in `smarthr-ui.css`; the product's own layout uses the v4 utilities its `theme.css` generates. Authoring `shr-` utilities would need `smarthr-ui/smarthr-ui-preset` in a Tailwind v3 config, outside this skill's scope.
- **Import `smarthr-ui.css` after the Tailwind entry point.** The library disables Tailwind's preflight and supplies its own base layer (the body font, the margin resets, `text-spacing-trim`), which has to land after v4's preflight to survive it.
- **`meta.stack.base` is `smarthr-ui`**: the library is the component base on this route.

## Token mapping

T2 requires `oklch()`; these are the nine required keys and the optional `surface`, converted from the published semantic tokens' hex with the Oklab transform. Use them verbatim.

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

- **`background` and `surface`**: SmartHR puts the screen on `BACKGROUND` `#f8f7f6` and panels drawn with `Base` on `WHITE`. Both enter `tokens.json`, so a panel the product builds lands on the same white as the library's own. Text on either is `foreground`.
- **`muted` takes `HEAD`**, the table-header ground. `OVER_BACKGROUND` `#f2f1f0` sits 1.8% in lightness from `BACKGROUND`, too close to read as a distinct surface.
- **`accent` takes `BRAND` `#00c4cc`**, the SmartHR blue: the only non-`MAIN` identity hue, exposed by the Tailwind preset as `bg-brand`. It is light, so text on it must be `foreground`.
- **`WARNING_YELLOW` `#ffcc17` has no slot.** It stays in the library, where the components that need it paint it.

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

- **`scale.ratio` is an approximation.** SmartHR's font sizes come from `6 / (6 + d)`: 0.667, 0.75, 0.857, 1, 1.2, 1.5 and 2rem, a harmonic series whose neighbouring ratios differ (1.2, 1.25, 1.333 above the base). `1.2` is the closest single geometric ratio; the `Text` component's `size` prop sets the real sizes.
- **Spacing is char-relative**: one unit is one character at the 16px base. The published tokens run 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 3.5, 4 and 8 characters, which in multiples of 4px is the `steps` array above.

Four entries belong in `meta.defaults_applied` on this route:

- `"color_dark omitted — SmartHR publishes no dark theme"`
- `"motion left at the product-ui default — SmartHR publishes no motion tokens"`
- `"T5 warning accepted — system-ui is the font family smarthr-ui ships"`
- `"T10 warning accepted — SmartHR LAYER1/2/3 all use alpha 0.3, and only the offset and blur differ"`

`assets/tokens_example.smarthr.json` is this mapping written out in full.

## The font is a deliberate decision

`system-ui` is copied from the reference: `smarthr-ui` ships `font-family: system-ui, sans-serif` in its base layer, and the OS renders each language in its own UI font. T5 and S2 both treat `system-ui` as the mark of a font nobody chose. T5 drops to a warning because `meta.reference` is set (`references/tokens-format.md`). S2 reads the built output alone, so keep the family out of the markup and let `smarthr-ui.css` set the body font. The family is recorded in `tokens.json` only; the `theme.css` below leaves it out.

## Wording

The `voice` block and `references/ui-copy.md` apply as written; the project settles its own `voice.terms`. SmartHR's writing style, UI text guidance and 用字用語 are at https://smarthr.design/products/contents/, and the `preset-smarthr` textlint rules in Step 4 check 用字用語 against that guidance.

## theme.css

The standard template quotes the family — `"system-ui", ui-serif, serif` for `h1`–`h3` — and a quoted `"system-ui"` is read as a font name, so headings would fall through to a serif. Generate from a project copy of the template through `--template`:

1. Copy `assets/theme.template.css` beside `tokens.json` as `theme.template.css`.
2. In the copy, delete the `--font-display` and `--font-body` lines from the `@theme inline` block, and the two `font-family` declarations from the base layer.
3. Run `python {SKILL_DIR}/scripts/generate_theme.py tokens.json --template theme.template.css`.

Each regeneration reads the project copy, so `theme.css` stays generated. Load the two stylesheets in this order:

```tsx
import './theme.css'
import 'smarthr-ui/smarthr-ui.css'
```

`check_slop.py` reads the `oklch()` literals out of the generated file, so S1 still fails a raw `#0077c7` in markup. Use the component or the utility class.
