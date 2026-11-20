# Astryx

product-ui is an independent project with no affiliation to or endorsement from Meta Platforms, Inc. This preset uses the token values published in `@astryxdesign/theme-neutral` (https://github.com/meta/astryx) under the MIT licence.

Astryx is the React design system Meta publishes at https://astryx.atmeta.com/. Its packages are all MIT-licensed (© 2026 Meta Platforms, Inc.):

- `@astryxdesign/core`: the components and the theme system
- `@astryxdesign/cli`: component docs, themes and scaffolding
- seven themes: `@astryxdesign/theme-neutral`, `-butter`, `-chocolate`, `-gothic`, `-matcha`, `-stone` and `-y2k`

Read this file in Step 1 whenever `meta.reference` is `"astryx"`, in Step 3 before writing markup, and in Step 4 for the doctor run.

Astryx has already settled the palette, the type scale, the spacing scale and the components, so Step 1 maps the neutral theme's published values. Astryx also ships help for AI agents (https://astryx.atmeta.com/docs/working-with-ai): a CLI that prints each component's API from the installed version, an agent block for `CLAUDE.md`, a workflow that starts each page from a template, a `doctor` check, and an MCP server. This route sets them up with the project and runs them inside product-ui's steps.

## Resources

| What | Where |
|---|---|
| Getting started | https://astryx.atmeta.com/docs/getting-started |
| Components | https://astryx.atmeta.com/components, or `npm run astryx -- component <Name>` |
| Tokens | https://astryx.atmeta.com/docs/tokens, or `npm run astryx -- docs tokens` |
| Tailwind and cascade layers | https://astryx.atmeta.com/docs/styling-libraries |
| Theme authoring | `npm run astryx -- docs author-a-theme` |
| Working with AI | https://astryx.atmeta.com/docs/working-with-ai |
| Code rubric | `npm run astryx -- docs is-my-code-good` |
| Repository | https://github.com/meta/astryx |

Written against, as of November 2026: `@astryxdesign/core`, `@astryxdesign/cli` and `@astryxdesign/theme-neutral` 0.7.11, `@stylexjs/stylex` and `@stylexjs/unplugin` 0.19.1, React 19.3, Tailwind CSS 4.3, Vite 8.3.

## The stack

Astryx needs React 19 or later, and the CLI Node 22.13 or later.

- **`meta.reference` and `meta.stack.base` are both `astryx`**, `meta.surface` is `saas` and `meta.stack.renderer` is `vite-react` (T8). The setup below is written and tested for Vite.
- **The components arrive as prebuilt CSS.** `@astryxdesign/core/astryx.css` holds the compiled StyleX classes of every component.
- **The project's own StyleX source needs a compiler.** Astryx's page templates are StyleX source. The build runs `@stylexjs/unplugin` for them, and `astryx.css` keeps supplying the components' styles.
- **Layout comes from Astryx's components.** `AppShell`, `LayoutHeader`, `VStack`, `HStack`, `Grid`, `Section` and `Text` take the place of `div`, `header` and `span`, as the agent block's rule "No <div>" and doctor's purity check ask.
- **Tailwind stays at v4.** A utility from `theme.css` goes in `className` where no component prop serves. Tailwind's utilities sit in the last cascade layer, so a utility on a component overrides the component's default (`rounded-none` on a `Button` renders a radius of 0). Astryx's `@astryxdesign/core/tailwind-theme.css` bridge stays out: it repoints Tailwind names such as `rounded-lg` and `shadow-md` at Astryx's variables, and `theme.css` already binds those names from `tokens.json`.

## Project setup

The setup runs once in Step 2, after `generate_theme.py` has written `theme.css`, and before Step 3. Set the project up in this order, in a Vite `react-ts` project, which already holds its `tsconfig.json`.

1. **Install.** A project on React 18 moves to React 19 on the user's decision: ask before this install.

   ```bash
   npm install react@19 react-dom@19 @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex
   npm install -D @astryxdesign/cli @stylexjs/unplugin tailwindcss @tailwindcss/vite
   ```

2. **The CLI alias.** Add `"astryx": "node node_modules/@astryxdesign/cli/clients/cli/bin/astryx.mjs"` to the `scripts` of `package.json`, and run every Astryx command as `npm run astryx -- <command>`. The agent block writes its commands as `npx astryx <command>`, and Astryx's documentation recommends the alias because agents call the wrong binary path. The alias runs the installed version, whose component APIs match the code. The props move between 0.x releases.
3. **Ask the user once**, in one AskUserQuestion round with two questions: whether to add Astryx's agent block to the project's `CLAUDE.md` (step 4), and whether to register Astryx's MCP server for the project (step 7). Both change files that every later session in the project reads.
4. **The agent block**, when the user agreed. `npm run astryx -- init --features agents --agent claude` appends Astryx's block (between `<!-- ASTRYX:START -->` and `<!-- ASTRYX:END -->`) to the project's `CLAUDE.md`, or writes `.claude/CLAUDE.md` when the project has none, and keeps the file's other text. The block holds the component index, the workflow below, Astryx's coding rules and a CLI reference. `npm run astryx -- doctor --built .` confirms it under the `agent-docs` check. Without the block, this file's workflow still runs, and doctor's `agent-docs` check reports the missing block, which gets the ruling "declined by the user".
5. **`vite.config.ts`.**

   ```ts
   import {defineConfig} from 'vite';
   import react from '@vitejs/plugin-react';
   import tailwindcss from '@tailwindcss/vite';
   import stylex from '@stylexjs/unplugin';

   export default defineConfig({plugins: [stylex.vite(), react(), tailwindcss()]});
   ```

6. **The product theme**, the stylesheets and the entry, as the next two sections give them.
7. **The MCP server**, when the user agreed. `claude mcp add --transport http --scope project astryx https://astryx.atmeta.com/mcp` writes `.mcp.json`, and its tools `search(query)` and `get(name)` load in the next session. It answers from Astryx's published documentation, components from `@canary` included. Props therefore come from the CLI, and the server serves searches across components, documentation and templates. Its queries name components, topics and kinds of screen.
8. **The global skill.** `npm run astryx -- init --user` writes `~/.agents/skills/astryx/SKILL.md` and links it into `~/.claude/skills/astryx`, which reaches every project on the machine. Run it on the user's request alone. Inside this project, the project's block takes precedence over it.

**An existing project** keeps what it has. Add the `stylex.vite()` entry to the `plugins` of its Vite config, put the layer statement and the Astryx imports at the head of its entry stylesheet, and wrap its root element in `Theme` and `InternationalizationProvider`. Its other configuration, imports and providers stay as they are.

## The product theme

The neutral theme sets body and label text at 14px and supporting text at 12px, which breaks principle 5 of `SKILL.md`. The product therefore renders under its own theme, which extends neutral at the scale neutral itself applies on touch screens (`{base: 16, ratio: 1.1736}`). The theme also raises `--font-size-xs` and heading 6, which that scale still sets at 12px, to 14px.

`src/themes/product/productTheme.ts`:

```ts
import {defineTheme} from '@astryxdesign/core/theme';
import {neutralTheme} from '@astryxdesign/theme-neutral';

const fallbacks = '"Noto Sans JP", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

const small = {
  '--font-size-xs': '0.875rem',
  '--text-heading-6-size': 'var(--font-size-sm)',
};

export const productTheme = defineTheme({
  name: 'product',
  extends: neutralTheme,
  typography: {
    scale: {base: 16, ratio: 1.1736},
    body: {family: 'Figtree', fallbacks},
    heading: {family: 'Figtree', fallbacks, weights: {3: 'bold', 4: 'bold'}},
    code: {
      family: 'ui-monospace',
      fallbacks: '"SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
    },
  },
  tokens: small,
  adaptations: {
    rules: [{when: {pointer: 'coarse', width: {below: 'lg'}}, value: {tokens: small}}],
  },
});
```

`src/themes/product/productTheme.doc.mjs`:

```js
/** @type {import('@astryxdesign/cli/authoring').ThemeDoc} */
export default {
  type: 'theme',
  name: 'product',
  displayName: 'Product',
  description: 'Neutral at a 16px base.',
  maintained: false,
};
```

`src/themes/product/product.fonts.css`, beside the stylesheet `theme build` writes:

```css
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600;700&display=swap');
```

```bash
npm run astryx -- theme build src/themes/product/productTheme.ts
npm run astryx -- theme add product
```

`theme build` writes `product.css` and `product.js` beside the source. `theme add` writes `src/astryx-themes.ts`, which imports them and `product.fonts.css`. In a project without a `tsconfig.json` it writes `astryx-themes.js`, which strict TypeScript rejects with TS7016. The setup therefore runs it after `tsconfig.json` exists.

- **The restated faces and the adaptation rule.** A child theme's `typography` replaces the base's whole typography config, so the body, heading and code faces are restated. Neutral's touch adaptation sets `--font-size-xs` back to 12px, so the `adaptations` rule repeats the two tokens after it.
- **What renders.** Body and label text render at 16px. Supporting text, `Badge`, `Breadcrumbs`, headings 5 and 6 and the `Stepper`'s step number render at 14px. `--font-size-2xs` to `--font-size-4xs` (10px to 7px) stay as Astryx sets them. Product code leaves those sizes unused, and R7 fails a run that renders at them.
- **Japanese.** `"Noto Sans JP"` heads the fallbacks, so Astryx's components draw Japanese in the face `typography.<slot>.family_ja` sets (T22).
- **Fonts.** The theme sets Figtree and Noto Sans JP as families, and `product.fonts.css` loads both at the four weights the theme uses. Doctor's `theme-fonts` check warns on any external font import. Neutral's own `fonts.css` loads Figtree from Google Fonts the same way. On this route `product.fonts.css` takes the place of the `<link>` in `index.html` that `references/stack-defaults.md` describes.

## Stylesheets and the entry

`src/index.css`:

```css
@layer reset, theme, base, astryx-base, astryx-theme, components, utilities;

@import "../theme.css";
@import "@astryxdesign/core/reset.css";
@import "@astryxdesign/core/astryx.css";

html.dark,
html.dark [data-astryx-theme] {
  color-scheme: dark;
}
```

`src/main.tsx`:

```tsx
import './index.css';
import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {Theme} from '@astryxdesign/core/theme';
import {InternationalizationProvider} from '@astryxdesign/core/i18n';
import jaJP from '@astryxdesign/core/locales/ja-JP.generated.js';
import {themes, defaultThemeSlug} from './astryx-themes';
import App from './App';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Theme theme={themes[defaultThemeSlug]} mode="light">
      <InternationalizationProvider locale="ja-JP" messages={{'ja-JP': jaJP}}>
        <App />
      </InternationalizationProvider>
    </Theme>
  </StrictMode>,
);
```

- **The layer statement comes first.** The first stylesheet that declares a layer fixes its rank, and this order puts Tailwind's utilities above Astryx's component styles. Placed after the Tailwind import, Astryx's reset wins over every utility, and neither the build nor the console reports it (`/docs/styling-libraries`).
- **`index.css` loads before the theme.** `main.tsx` imports it on its first line, ahead of `astryx-themes`, which imports `product.css` and `product.fonts.css`.
- **An English interface** drops `InternationalizationProvider`: Astryx falls back to its bundled `en` catalog.

## Token mapping

T2 requires `oklch()`. The table converts the neutral theme's hex for the required keys and the optional `surface`, `success`, `warning` and `info` with the Oklab transform. Use the values verbatim. Each Astryx colour is a `light-dark()` pair, and the dark side goes into `color_dark`.

| `tokens.json` | Astryx token | light | oklch | dark | oklch |
|---|---|---|---|---|---|
| `background` | `--color-background-body` | `#f1f1f1` | `oklch(95.8% 0 0)` | `#1b1b1b` | `oklch(22.2% 0 0)` |
| `foreground` | `--color-text-primary` | `#000000` | `oklch(0% 0 0)` | `#ffffff` | `oklch(100% 0 0)` |
| `surface` | `--color-background-surface` | `#ffffff` | `oklch(100% 0 0)` | `#262626` | `oklch(26.9% 0 0)` |
| `primary` | `--color-accent` | `#1b1b1b` | `oklch(22.2% 0 0)` | `#f1f1f1` | `oklch(95.8% 0 0)` |
| `primary_foreground` | `--color-on-accent` | `#ffffff` | `oklch(100% 0 0)` | `#111111` | `oklch(17.8% 0 0)` |
| `muted` | `--color-background-muted` | `#f1f1f1` | `oklch(95.8% 0 0)` | `#1b1b1b` | `oklch(22.2% 0 0)` |
| `muted_foreground` | `--color-text-secondary` | `#474747` | `oklch(39.8% 0 0)` | `#9e9e9e` | `oklch(69.9% 0 0)` |
| `border` | `--color-border` on the surface | `#ebebeb` | `oklch(94% 0 0)` | `#3c3c3c` | `oklch(35.6% 0 0)` |
| `destructive` | `--color-error` | `#c9303a` | `oklch(55.3% 0.189 23)` | `#ff705d` | `oklch(71.6% 0.178 30)` |
| `accent` | `--color-info` | `#0074e2` | `oklch(56.9% 0.189 255)` | `#6d9cfe` | `oklch(70.3% 0.153 264)` |
| `success` | `--color-success` | `#198100` | `oklch(52.6% 0.174 141)` | `#64af4c` | `oklch(68.3% 0.154 139)` |
| `warning` | `--color-warning` | `#ffce2f` | `oklch(87% 0.167 90)` | one value in both modes | |
| `info` | `--color-info` | `#0074e2` | `oklch(56.9% 0.189 255)` | `#6d9cfe` | `oklch(70.3% 0.153 264)` |

- **`primary` is near-black.** Neutral's primary `Button` fills with `--color-accent`, `#1b1b1b`.
- **`accent` takes `--color-info`**, the blue neutral uses for its selected ring (`--shadow-inset-selected`) and its status fill. Neutral has no other hue of its own. In `theme.css` the key `accent` fills the `brand-accent` utility.
- **`border` is opaque.** Astryx's border is black at 8% (white at 10% in dark), and `colour.py` ignores alpha, so `tokens.json` holds the colour that border gives on the `surface` colour. Astryx's components still draw the translucent border from their `--color-border`.
- **`muted` equals `background`**, as in neutral. It reads as a distinct fill on the white `surface`, where table headers and secondary fills sit.
- **`color_dark` leaves out `warning`.** Astryx paints `#ffce2f` in both modes.

Everything else:

| Field | Value | Source |
|---|---|---|
| `radius.sm` / `md` / `lg` / `full` | `0.375rem` / `0.625rem` / `0.75rem` / `9999px` | `--radius-inner`, `--radius-element`, `--radius-container`, `--radius-full` |
| `shadow.sm` / `md` / `lg` | the light side of `--shadow-low` / `med` / `high`, without their inset ring (transparent in light) | neutral |
| `typography.display` and `body` | `family` `Figtree`, `family_ja` `Noto Sans JP` | neutral ships Figtree; the product theme adds the Japanese face |
| `typography.scale.ratio` / `base_px` | `1.1736` / `16` | the product theme |
| `spacing.base_px` / `steps` | `4` / `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]` | `--spacing-1` to `--spacing-12`, 4px to 48px |
| `motion.duration` `fast` / `base` / `slow` | `125ms` / `300ms` / `700ms` | `--duration-fast`, `--duration-medium`, `--duration-slow` |
| `motion.easing.standard` | `cubic-bezier(0.24, 1, 0.4, 1)` | `--ease-standard` |
| `voice` | product-ui's own default | see Wording |

Four entries belong in `meta.defaults_applied` on this route:

- `"Astryx theme product extends neutral at typography.scale base 16, ratio 1.1736 — the neutral theme's own touch scale, so supporting text draws at 14px"`
- `"color.border is the opaque equivalent of Astryx --color-border (black at 8%, white at 10% in dark) on the surface — the contrast check reads no alpha"`
- `"color.muted equals color.background — Astryx neutral paints --color-background-muted and --color-background-body alike"`
- `"motion copied from Astryx neutral (fast 125ms, medium 300ms, slow 700ms) — theme.css and Astryx both declare --duration-fast"`

`assets/tokens_example.astryx.json` is this mapping written out in full.

**Another Astryx theme** maps the same way: install `@astryxdesign/theme-<slug>`, read its values from `node_modules/@astryxdesign/theme-<slug>/dist/theme.css`, convert each hex with `hex_to_oklch` in `scripts/colour.py`, and set `extends` in the product theme to that theme's export. `gothic` is dark-only: its values go into `color`, and `color_dark` is left out.

## theme.css and the names both declare

`theme.css` is generated from `tokens.json` as on every route, and stays unchanged. A few custom-property names exist on both sides:

| Name | `theme.css` | Astryx | What each side reads |
|---|---|---|---|
| `--duration-fast` | unlayered, on `:root` | layer `astryx-theme`, on each `[data-astryx-theme]` element | Inside the `Theme` wrapper, Astryx's own value. On `<html>`, which the root `Theme` also marks, the unlayered value wins, and portals read it. `tokens.json` carries Astryx's 125ms, so both sides agree |
| `--color-border`, `--color-accent`, `--color-success`, `--color-warning`, `--color-info`, `--radius-full`, `--ease-standard` | `@theme inline` | layer `astryx-theme` | The product's utilities inline `theme.css`'s value; Astryx's components read Astryx's. `--color-accent` differs on purpose: in `theme.css` it is shadcn's hover surface, in Astryx the primary fill |

The base layer's `border-color: var(--color-border)` resolves to Astryx's translucent border inside the `Theme` wrapper.

## The dark theme

The root `Theme` takes `mode="light"`, and the two rules at the end of `index.css` switch Astryx's `light-dark()` colours with the class `dark` on `<html>`. That class therefore turns the product's utilities and Astryx's components dark together, and the review's dark capture, which adds the same class, renders both. With `mode="system"` the wrapper would follow the OS preference while the product's utilities follow the class. A product that ships light only deletes `color_dark` from `tokens.json`; the two rules then never apply.

## Wording

The `voice` block and `references/ui-copy.md` apply as written; the project settles its own `voice.terms`.

- **Built-in strings.** Astryx's own strings, such as the pagination and stepper labels read by screen readers, come from its `ja-JP` catalog through `InternationalizationProvider`. A catalog string that disagrees with `voice.terms` is replaced through the provider's `overrides` prop, `overrides={{'ja-JP': {'<key>': '<word>'}}}`; the keys are listed in `node_modules/@astryxdesign/core/locales/ja-JP.json`.
- **`EmptyState`'s `title` renders as a heading.** `check_copy.py` therefore raises C8 on the 「。」 that the `state.empty` pattern's sentence ends with. Rule on it in the hand-over under `references/ui-copy.md`: a sentence ends with 「。」 wherever it appears.

## Step 3 with Astryx's workflow

The agent block's workflow starts every page from a template. On this route that workflow runs after `ui-brief.md` holds its Composition, its `## Slots` table and the pattern notes `scaffold.py` writes for the `astryx` stack. The brief stays the plan the Step 5 reviewer checks.

1. **Find the template.** `npm run astryx -- build "<kind and purpose>"` describes the screen in English words from the brief's Kind line and its Purpose sentence, such as `"work tool collection: a table of cases the reader compares by status and due date"`. It names a page template, two alternatives, blocks for the parts the template lacks and components. Take the template whose frame holds the regions of the brief's Regions line, the shell first. `npm run astryx -- template --list --type page` lists the other page templates.
2. **Scaffold it.** `npm run astryx -- template <name> --type page <path>` copies the page into the project. `<path>` is the screen's own file, such as `src/pages/Cases.tsx`, and the entry or the router renders it in place of `App`. Install the dependencies the `build` output names (`@heroicons/react` for most page templates).
3. **Keep the frame, replace the content.** The template's frame, gap and padding stay. Every string, record, media item and navigation entry the template carries is demo content, and the brief, its `## Sample data` and the patterns supply what replaces it. A region or section the brief omits is deleted, and the brief's Omitted line keeps its reason. The template's logo mark goes too: the header shows `meta.name` as text unless `meta.logo` names a file (principle 2).
4. **Fill each section.** Each pattern note names the Astryx component for its section (`maps_to.astryx`). `npm run astryx -- template <Block>` supplies a block for a part the template lacks, and `npm run astryx -- component <Name> --dense` prints a component's props before the first use. The `data-pattern` attributes go on the components.
5. **The brief decides a disagreement.** Where the template's frame departs from the brief, such as a tile row the brief rules out or a card around every section, the frame is changed to the brief.

An existing page keeps its frame: blocks and components go inside its sections, as the agent block says.

## Components

- **`data-*` reaches the DOM.** Every component passes `data-*` props to its root element, so `data-pattern`, `data-pattern-slot` and `data-pattern-field` go on the component itself.
- **A table whose rows carry `data-pattern`** is written in children mode: `TableHeader`, `TableBody`, `TableRow`, `TableHeaderCell` and `TableCell` inside `Table`.
- **`Step` takes its index in `step`**, as in `<Step step={0} label="申請" />`. Without `step` the indicator prints NaN.

## Step 4: doctor

On this route Step 4 also runs Astryx's own check, which the agent block requires before a build is delivered:

```bash
npm run build
npm run astryx -- doctor --built .
```

`--built .` names the project folder, so doctor reads the source as well as the build output that `npm run build` has just written. Run on `dist`, it reads the build output alone. A `fail` sends the work back to Step 3, and each `warn` gets a ruling in the hand-over.

- **`built-astryx-purity`** lists each raw element and each `className` with the component, prop or token to use. Replace the element with the component it gives. A raw element stays where its HTML meaning is needed. A `className` stays where it holds a `theme.css` utility that no prop provides. The ruling says which case applies. `npm run astryx -- docs is-my-code-good` holds Astryx's full rubric.
- **`theme-fonts`** warns while `product.fonts.css` imports from Google Fonts. Keep it with that reason.
- **`cli-on-path`** concerns the bare `astryx` command. The route runs the CLI through the npm alias.

The product-ui checks of Step 4 read the template's code as any other source. On a scaffolded template, `check_copy.py` flags the demo strings it left behind (C26 on English labels on a Japanese screen) and `check_slop.py` a collection with no empty state (S16).

## Upgrading Astryx

These steps run when the user asks to upgrade Astryx. The `--apply` step rewrites project code and the agent block.

1. Move every `@astryxdesign/*` package to the same release.
2. `npm run astryx -- upgrade --from <old core version> --apply` updates the code and refreshes the agent block.
3. `npm run astryx -- theme build src/themes/product/productTheme.ts` and `npm run astryx -- theme add product` rebuild the product theme. Doctor's `theme-local-builds` check reports a stale build.
4. `npm run astryx -- doctor --built .` and the Step 4 checks run again.

## Which rules decide

The agent block brings Astryx's rules into every session in the project, beside this skill's. They divide the work this way:

| Matter | Decided by |
|---|---|
| Components, layout and styling | Astryx's agent block: components and props first, then utilities backed by tokens, palettes through the theme |
| Whether a string exists, and its words | `references/ban-list.md`, `references/ui-copy.md` and the section's pattern. Astryx's guidance that an empty state explains what happened yields to them |
| The composition: regions, dominant element, reading order, containers | `ui-brief.md` |
| A record's state | `status.badge` on `Badge`, which Astryx's Badge documentation gives to states such as Active and Failed. The block's line "Badge = counts only" yields to that documentation |
