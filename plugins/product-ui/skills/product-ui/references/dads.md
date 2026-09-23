# Digital Agency Design System (DADS)

product-ui is an independent project with no affiliation to or endorsement from the Digital Agency (デジタル庁); this preset uses the token values published in `digital-go-jp/tailwind-theme-plugin` (https://github.com/digital-go-jp/tailwind-theme-plugin) under the MIT licence.

The design system published by Japan's Digital Agency (デジタル庁デザインシステム), currently at β. The component
repositories and the Tailwind plugin are MIT-licensed (© デジタル庁); the other resources below, such as the
Figma library and the illustrations and icons, carry their own terms. This file is the source of record for the DADS route: read it in
Step 1 whenever `meta.reference` is `"digital-agency-design-system"`, and in Step 3 before writing markup.

Choosing DADS replaces the usual token derivation. The palette, the type scale and the components have already
been decided, with WCAG 2.2 AA as the target DADS states, so Step 1 maps the existing values and
invents none, and no screenshot reading takes place.

## Resources

| What | Where |
|---|---|
| Resource index | https://design.digital.go.jp/dads/resources/ |
| Tailwind plugin (tokens) | `@digital-go-jp/tailwind-theme-plugin` — https://github.com/digital-go-jp/tailwind-theme-plugin |
| React components | https://github.com/digital-go-jp/design-system-example-components-react |
| React Storybook | https://design.digital.go.jp/dads/react/ |
| HTML components | https://github.com/digital-go-jp/design-system-example-components-html |
| HTML Storybook | https://design.digital.go.jp/dads/html/ |
| Figma library | https://www.figma.com/community/file/1377880368787735577 |
| Accessibility guidebook | https://www.digital.go.jp/resources/introduction-to-web-accessibility-guidebook |
| Illustrations and icons (separate terms of use) | https://www.digital.go.jp/policies/servicedesign/designsystem/Illustration_Icons |

Versions this file was written against, as of September 2026: plugin `1.0.1`, `@digital-go-jp/design-tokens` `2.x`, Figma v2 series.
Both component repositories are labelled example implementations, not a distributed library.

## What the plugin provides

```css
@import "tailwindcss";
@import '@digital-go-jp/tailwind-theme-plugin/v4';
```

The v4 entry point (`dist/v4.css`) declares an `@theme` block and, as of plugin `1.0.1`, 58 custom utilities.

- **Colour**: thirteen scales at steps 50–1200 (`--color-key-*`, `blue`, `light-blue`, `cyan`, `green`, `lime`,
  `yellow`, `orange`, `red`, `magenta`, `purple`), `--color-solid-gray-50…900` and its `--color-opacity-gray-*`
  counterpart in `rgba()`, plus the semantic pairs `--color-success-1/2`, `--color-error-1/2`,
  `--color-warning-yellow-1/2`, `--color-warning-orange-1/2`, `--color-focus-yellow`, `--color-focus-blue`.
  `--color-focus-yellow` and `--color-warning-yellow-1` hold the same value, `#b78f00`.
- **Typography**: 55 utilities named `text-<group>-<px><B|N>-<leading>`, where the group is `dsp` (display),
  `std` (standard, leading 140–175), `dns` (dense, 120–130), `oln` (one line, 100) or `mono`. `B` is weight 700
  and `N` is 400. `text-std-17N-170` is 17px regular at line-height 1.7; `text-oln-16B-100` is 16px bold at 1.0.
  These are `@utility` blocks setting `font-size`, `font-weight`, `line-height` and `letter-spacing` together —
  not theme variables, so no `--text-*` variable exists to reference.
- **Fonts**: `--font-sans: 'Noto Sans JP', …`, `--font-mono: 'Noto Sans Mono', monospace`, weights 400 and 700.
- **Radius**: `--radius-4/6/8/12/16/24/32` and `--radius-full: 624.9375rem`.
- **Shadow**: `--shadow-1` through `--shadow-8`, each a two-layer shadow at alpha 0.1 and 0.3.
- **List markers**: `list-circle`, `list-square`, `list-lower-latin`.

The plugin does not touch spacing, so Tailwind's own scale stays in place.

## Token mapping

DADS ships hex, and rule T2 requires `oklch()`. These are the nine keys of `tokens.json`, converted from the
plugin's own values with the Oklab transform. Use them verbatim rather than reconverting.

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

Why these and not others:

- `solid-gray-536` and `solid-gray-420` are the two greys DADS itself uses for secondary text and for borders
  on white; the numbers are the contrast ratios they were chosen for.
- DADS has no separate brand accent. `yellow-300` is what its components paint as the focus ring
  (`focus-visible:ring-yellow-300`), so it is the one non-blue hue the system actually shows. It is a light
  colour: text on top of it must be `foreground`, never `primary_foreground`.
- The full palette stays out of `tokens.json` — thirteen scales at thirteen steps would breach T9's ceiling of
  twelve keys. It lives in the plugin's `@theme`, where the utilities pick it up.

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
| `voice` | product-ui's own default | DADS publishes no writing guideline — see below |

Five entries belong in `meta.defaults_applied` on this route, so each departure from the preset carries its reason:

- `"color_dark omitted — DADS β publishes no dark theme"`
- `"motion left at the product-ui default — DADS β publishes no motion tokens"`
- `"spacing left at the product-ui default — the DADS Tailwind plugin declares no spacing scale"`
- `"T10 warning accepted — DADS --shadow-1/2/3 all use alpha 0.1 and 0.3, and only the blur differs"`
- `"voice follows references/ui-copy.md — DADS defines no writing guideline"`

The shadows are rewritten into `oklch(0% 0 0 / a)` because `rgba(0, 0, 0, a)` hides the alpha from T10's check,
and a warning that cannot fire is worse than one that is accepted with a reason.

`assets/tokens_example.dads.json` is this mapping written out in full.

## DADS defines no writing guideline

DADS publishes its visual foundations, its components and its accessibility guidance. The wording of a button, a form label or an error message is left to each project.

`references/ui-copy.md` supplies those rules on this route — this skill's own rules and 文化審議会「公用文作成の考え方」（建議、令和4年1月7日） — and applies unchanged. Tell the user that the wording rules come from this skill.

## theme.css

Generate it from a project copy of the template, through the generator's `--template` option, so that
`theme.css` is never edited by hand:

1. Copy `assets/theme.template.css` beside `tokens.json` as `theme.template.css`.
2. In the copy, add one line directly after `@import "tailwindcss";`:

   ```css
   @import '@digital-go-jp/tailwind-theme-plugin/v4';
   ```

3. Run `python {SKILL_DIR}/scripts/generate_theme.py tokens.json --template theme.template.css`.

The two coexist: the plugin supplies `bg-key-900`, `text-std-17N-170` and the rest, while the template's
`@theme inline` block supplies `bg-primary`, `text-foreground` and the semantic names the rest of this skill
uses. `check_slop.py` reads every `oklch()` literal out of the generated file, so S1 keeps working — and a
raw `#0017c1` written into markup still fails it, which is the intended outcome. Use the utility, not the hex.

## Which implementation to copy

`meta.stack.renderer` decides, with no further question:

| renderer | Repository | Built on |
|---|---|---|
| `vite-react`, `next-react` | `design-system-example-components-react` | `react-aria-components`, Tailwind |
| `html` | `design-system-example-components-html` | `dads-`-prefixed BEM, custom elements without Shadow DOM |

Set `meta.stack.base` to `react-aria` on the React route, and to `null` on the HTML route.

`references/dads-components.md` holds the component inventory and the copying procedure. Route
there in Step 3 instead of to the shadcn reference — the two systems do not mix inside one screen.

The React repository targets Tailwind v3. Its DADS-specific classes come from the plugin and work unchanged
under v4; only Tailwind's own renamed core utilities need fixing as each component is copied.
