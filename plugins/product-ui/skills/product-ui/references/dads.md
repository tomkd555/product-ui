# Digital Agency Design System (DADS)

product-ui is an independent project with no affiliation to or endorsement from the Digital Agency (デジタル庁); this preset uses the token values published in `digital-go-jp/tailwind-theme-plugin` (https://github.com/digital-go-jp/tailwind-theme-plugin) under the MIT licence.

The design system published by Japan's Digital Agency (デジタル庁デザインシステム), currently at β. The component repositories and the Tailwind plugin are MIT-licensed (© デジタル庁); the other resources below, such as the Figma library and the illustrations and icons, carry their own terms. Read this file in Step 1 whenever `meta.reference` is `"digital-agency-design-system"`, and in Step 3 before writing markup.

DADS has already settled the palette, the type scale and the components, targeting WCAG 2.2 AA, so Step 1 maps the existing values, invents none and reads no screenshot.

## Resources

| What | Where |
|---|---|
| Resource index | https://design.digital.go.jp/dads/resources/ |
| Tailwind plugin (tokens) | `@digital-go-jp/tailwind-theme-plugin` (https://github.com/digital-go-jp/tailwind-theme-plugin) |
| React components | https://github.com/digital-go-jp/design-system-example-components-react |
| React Storybook | https://design.digital.go.jp/dads/react/ |
| HTML components | https://github.com/digital-go-jp/design-system-example-components-html |
| HTML Storybook | https://design.digital.go.jp/dads/html/ |
| Figma library | https://www.figma.com/community/file/1377880368787735577 |
| Accessibility guidebook | https://www.digital.go.jp/resources/introduction-to-web-accessibility-guidebook |
| Illustrations and icons (separate terms of use) | https://www.digital.go.jp/policies/servicedesign/designsystem/Illustration_Icons |

This file describes `@digital-go-jp/tailwind-theme-plugin` 2.0.0, which is built on `@digital-go-jp/design-tokens` 2.1.0 and which the plugin's README pairs with the Figma library 2.3.0 to 2.18.2. Both component repositories are example implementations meant to be copied into a project.

## What the plugin provides

```css
@import "tailwindcss";
@import '@digital-go-jp/tailwind-theme-plugin/v4';
```

The v4 entry point (`dist/v4.css`, exported as `./v4`) declares one `@theme` block and the typography utilities as `@utility` blocks.

- **Colour**: the scales at steps 50–1200 (`--color-key-*`, `blue`, `light-blue`, `cyan`, `green`, `lime`,
  `yellow`, `orange`, `red`, `magenta`, `purple`), `--color-solid-gray-50…900` and its `--color-opacity-gray-*`
  counterpart in `rgba()`, plus the semantic pairs `--color-success-1/2`, `--color-error-1/2`,
  `--color-warning-yellow-1/2`, `--color-warning-orange-1/2`, `--color-focus-yellow`, `--color-focus-blue`.
  `--color-focus-yellow` and `--color-warning-yellow-1` hold the same value, `#b78f00`.
- **Typography**: utilities named `text-<group>-<px><B|N>-<leading>`, where the group is `dsp` (display),
  `std` (standard, leading 140–175), `dns` (dense, 120–130), `oln` (one line, 100) or `mono`. `B` is weight 700
  and `N` is 400. `text-std-17N-170` is 17px regular at line-height 1.7; `text-oln-16B-100` is 16px bold at 1.0.
  Each is an `@utility` block setting `font-size`, `font-weight`, `line-height` and `letter-spacing` together,
  so there is no `--text-*` variable to reference.
- **Fonts**: `--font-sans: 'Noto Sans JP', sans-serif`, `--font-mono: 'Noto Sans Mono', monospace`, and the weights
  `--font-weight-400` and `--font-weight-700` (`font-400`, `font-700`).
- **Line height**: `--leading-100/120/130/140/150/160/170/175`, so `leading-150` is 1.5.
- **Radius**: `--radius-4/6/8/12/16/24/32` and `--radius-full: 624.9375rem`.
- **Shadow**: `--shadow-1` through `--shadow-8`, each a two-layer shadow at alpha 0.1 and 0.3.
- **Spacing**: Tailwind's own scale, which the plugin leaves in place.

The plugin doesn't declare a breakpoint or a list-marker utility. Its migration guide (`MIGRATION.md`) writes the markers as `list-[lower-latin]`, `list-[circle]` and `list-[square]`, and gives `--breakpoint-desktop: 48em` for the `desktop:` variant the React components use. `theme.css` on this route declares that breakpoint.

## Token mapping

T2 requires `oklch()`; these nine keys are converted from the plugin's hex with the Oklab transform. Use them verbatim.

| `tokens.json` | DADS variable | hex | oklch |
|---|---|---|---|
| `background` | `--color-white` | `#ffffff` | `oklch(100% 0 0)` |
| `foreground` | `--color-solid-gray-900` | `#1a1a1a` | `oklch(21.8% 0 0)` |
| `primary` | `--color-key-900` | `#0017c1` | `oklch(38% 0.245 264)` |
| `primary_foreground` | `--color-white` | `#ffffff` | `oklch(100% 0 0)` |
| `muted` | `--color-solid-gray-50` | `#f2f2f2` | `oklch(96.1% 0 0)` |
| `muted_foreground` | `--color-solid-gray-536` | `#767676` | `oklch(56.6% 0 0)` |
| `border` | `--color-solid-gray-420` | `#949494` | `oklch(66.7% 0 0)` |
| `destructive` | `--color-error-1` | `#ec0000` | `oklch(59.2% 0.243 29)` |
| `accent` | `--color-yellow-300` | `#ffd43d` | `oklch(88.3% 0.164 92)` |

- `solid-gray-536` and `solid-gray-420` are the greys DADS itself uses for secondary text and for borders on white; the numbers are the contrast ratios they were chosen for.
- `yellow-300` is the focus ring DADS components paint (`focus-visible:ring-yellow-300`), the one non-blue hue the system shows; DADS has no separate brand accent. The key `accent` fills the `brand-accent` utility (`bg-brand-accent`); shadcn's `bg-accent` stays the hover and selected surface. It is a light colour, so text on it must be `foreground`.
- The full palette stays in the plugin's `@theme`, where the utilities pick it up: every scale at every step would breach T9's ceiling of twelve keys.

Everything else:

| Field | Value | Source |
|---|---|---|
| `radius.sm` / `md` / `lg` / `full` | `0.25rem` / `0.5rem` / `0.75rem` / `624.9375rem` | `--radius-4/8/12/full` |
| `shadow.sm` / `md` / `lg` | `--shadow-1/2/3`, with each `rgba(0,0,0,a)` rewritten as the equivalent `oklch(0% 0 0 / a)` | plugin |
| `typography.display.family` and `body.family` | `Noto Sans JP` | `--font-sans` |
| `typography.scale.ratio` / `base_px` | `1.125` / `16` | closest ratio to the `std` sizes 16, 18, 20, 22, 24, 26, 28, 32, 36, 45 |
| `spacing` | product-ui's own default | the plugin declares none |
| `motion` | product-ui's own default | DADS β publishes no motion tokens |
| `color_dark` | omitted | DADS β has no dark theme |
| `voice` | product-ui's own default | DADS publishes no writing guideline, see below |

The shadows are written in `oklch(0% 0 0 / a)` because `rgba(0, 0, 0, a)` hides the alpha from T10, and a warning accepted with a reason beats one that cannot fire.

Five entries belong in `meta.defaults_applied` on this route:

- `"color_dark omitted — DADS β publishes no dark theme"`
- `"motion left at the product-ui default — DADS β publishes no motion tokens"`
- `"spacing left at the product-ui default — the DADS Tailwind plugin declares no spacing scale"`
- `"T10 warning accepted — DADS --shadow-1/2/3 all use alpha 0.1 and 0.3, and only the blur differs"`
- `"voice follows references/ui-copy.md — DADS defines no writing guideline"`

`assets/tokens_example.dads.json` is this mapping written out in full.

## DADS defines no writing guideline

DADS publishes visual foundations, components and accessibility guidance, and leaves the wording of buttons, labels and errors to each project. `references/ui-copy.md` applies unchanged on this route: this skill's own rules and 文化審議会「公用文作成の考え方」（建議、令和4年1月7日）. Tell the user the wording rules come from this skill.

## Installing the plugin

The npm package and a vendored copy deliver the same `v4.css`. Each route gives the import line that step 2 under theme.css adds.

**From npm**, when the project installs packages:

```bash
npm install @digital-go-jp/tailwind-theme-plugin@^2
```

The import line is `@import '@digital-go-jp/tailwind-theme-plugin/v4';`.

**Vendored**, when the project cannot install the package. The MIT licence permits copying the file into the project, provided the copyright and permission notice goes with the copy:

1. Download two files from the repository at tag `v2.0.0`. `examples-v4/src/tailwind-theme-plugin/v4.css` there is the file the npm package ships as `dist/v4.css`.
   - https://raw.githubusercontent.com/digital-go-jp/tailwind-theme-plugin/v2.0.0/examples-v4/src/tailwind-theme-plugin/v4.css
   - https://raw.githubusercontent.com/digital-go-jp/tailwind-theme-plugin/v2.0.0/LICENSE
2. Save them as `vendor/tailwind-theme-plugin/v4.css` and `vendor/tailwind-theme-plugin/LICENSE` beside `tokens.json`. The CSS file doesn't hold a licence notice, so make this its first line:

   ```css
   /*! @digital-go-jp/tailwind-theme-plugin 2.0.0, dist/v4.css. MIT License, Copyright (c) 2023 デジタル庁; the full text is in LICENSE beside this file. */
   ```

3. The import line is `@import './vendor/tailwind-theme-plugin/v4.css';`.

The Step 4 checks skip `vendor/` when they walk a directory; `check_slop.py` still follows the theme's import of the vendored file for the plugin's colour names.

## theme.css

Generate it from a project copy of the template, so `theme.css` stays generated:

1. Copy `assets/theme.template.css` beside `tokens.json` as `theme.template.css`.
2. In the copy, add the import line of the chosen route directly after `@import "tailwindcss";`.
3. Run `python {SKILL_DIR}/scripts/generate_theme.py tokens.json --template theme.template.css`.

With `meta.reference` set to `"digital-agency-design-system"`, the generator leaves out the template's `--radius-*: initial` and `--shadow-*: initial` resets, so the plugin's numbered steps that the components use (`rounded-4` to `rounded-32`, `shadow-1` to `shadow-8`) stay defined. It also declares `--breakpoint-desktop: 48em`. Tailwind's own steps, such as `rounded-2xl` and `shadow-xl`, still resolve to the token steps. The `--text-*` reset stays: the plugin's typography utilities are `@utility` blocks, which a theme reset leaves in place.

The plugin supplies `bg-key-900`, `text-std-17N-170` and the rest; the template's `@theme inline` block supplies `bg-primary`, `text-foreground` and the semantic names this skill uses. `check_slop.py` reads the `oklch()` literals out of the generated file, so S1 still fails a raw `#0017c1` in markup. Use the utility class.

## Which implementation to copy

`meta.stack.renderer` decides, with no further question:

| renderer | Repository | Built on |
|---|---|---|
| `vite-react`, `next-react` | `design-system-example-components-react` | React 19 and Tailwind classes; the component files import `react` and `react-dom` alone |
| `html` | `design-system-example-components-html` | `dads-`-prefixed BEM, custom elements without Shadow DOM |

On the React route, `meta.stack.base` is `react-aria` where the screen copies the calendar popup, which builds on React Aria (`assets/tokens_example.dads.json` shows this case), and otherwise the base the project's other components use (`base-ui` in a current shadcn project): T1 requires a component base for a React renderer, and the other copied DADS components import React alone. Set it to `null` on the HTML route.

Step 3 takes every component on this route from `references/dads-components.md`, which holds the inventory and the copying procedure; DADS and shadcn stay on separate screens.
