# Digital Agency Design System — Component Reference

The component implementations published by Japan's Digital Agency (デジタル庁デザインシステム), β, MIT-licensed (© デジタル庁). Counts and line numbers below are as of September 2026.

This file is the component reference, in place of shadcn/ui, when `tokens.json` carries
`meta.reference: "digital-agency-design-system"`. The two systems do not mix inside one screen: shadcn styles
through semantic variables and Radix/Base UI primitives, DADS through its own palette utilities and either
`react-aria-components` or plain custom elements. Pick one per surface.

`references/dads.md` holds the token side — the palette mapping and the `theme.css` import. Read it
first; nothing here works without the Tailwind plugin installed.

## There is no CLI

DADS is distributed as example code to copy. `npx shadcn add` cannot reach these components. Copying is the supported route:

```bash
# React
git clone --depth 1 https://github.com/digital-go-jp/design-system-example-components-react
cp -r design-system-example-components-react/src/components/Button src/components/

# HTML
git clone --depth 1 https://github.com/digital-go-jp/design-system-example-components-html
cp -r design-system-example-components-html/src/components/button src/components/
```

Browse before copying: https://design.digital.go.jp/dads/react/ and https://design.digital.go.jp/dads/html/.

Neither repository accepts pull requests. Anything adapted stays adapted locally.

## Which repository

`meta.stack.renderer` decides. `vite-react` and `next-react` take the React repository; `html` takes the HTML
one. The two cover almost the same ground under different names.

| React (`src/components/`) | HTML (`src/components/`) |
|---|---|
| `Accordion` | `accordion` |
| `Blockquote` | `blockquote` |
| `Breadcrumbs` | `breadcrumb` |
| `Button` | `button` |
| `Calendar` | `calendar` |
| `Card` | `card` |
| `Carousel` | `carousel` |
| `Checkbox` | `checkbox` |
| `ChipLabel` | `chip-label` |
| `DatePicker` | `date-picker` |
| `Disclosure` | `disclosure` |
| `Divider` | `divider` |
| `Dl` | `description-list` |
| `Drawer` | `drawer` |
| `EmergencyBanner` | `emergency-banner` |
| `FileUpload` | `file-upload` |
| `HamburgerMenuButton` | `hamburger-menu-button` |
| `Heading` | `heading` |
| `HorizontalMenu` | `horizontal-menu` |
| `Image` | `image` |
| `Input` | `input-text` |
| `Label` | `form-control-label` |
| `LanguageSelector` | `language-selector` |
| `Link` | `link` |
| `List` | `list` |
| `MenuList` | `menu-list` |
| `MenuListBox` | `menu-list-box` |
| `ModalDialog` | `modal-dialog` |
| `NotificationBanner` | `notification-banner` |
| `ProgressIndicator` | `progress-indicator` |
| `Radio` | `radio` |
| `ResourceList` | `resource-list` |
| `SearchBox` | `search-box` |
| `Select` | `select` |
| `StepNavigation` | `step-navigation` |
| `Tab` | `tab` |
| `Table` | `table` |
| `Textarea` | `textarea` |
| `UtilityLink` | `utility-link` |
| `ErrorText`, `Legend`, `SupportText`, `RequirementBadge`, `StatusBadge`, `SeparatedDatePicker` | — |
| — | `switch`, `toc`, `page-navigation` |

45 components on the React side, 42 on the HTML side. `Slot` is an internal helper, and the `deprecated/` and
`v1/` directories are earlier versions — skip all three.

Where a component exists on only one side, build the missing one out of the primitives of the
repository in use: the two have no shared runtime.

## React conventions

`Button` is the pattern the rest follow, so it is worth reading once in full
(`src/components/Button/Button.tsx`, 102 lines). The parts that generalise (excerpt, MIT, © Digital Agency; full licence text in `THIRD_PARTY_NOTICES.md` at the plugin root, or in this skill's directory under a manual install; from [Button.tsx](https://github.com/digital-go-jp/design-system-example-components-react/blob/main/src/components/Button/Button.tsx)):

```tsx
export type ButtonVariant = 'solid-fill' | 'outline' | 'text';
export type ButtonSize = 'lg' | 'md' | 'sm' | 'xs';

export const buttonVariantStyle: { [key in ButtonVariant]: string } = {
  'solid-fill': `
    border-4 border-double border-transparent
    bg-key-900 text-white
    hover:bg-key-1000 hover:underline
    active:bg-key-1200 active:underline
    aria-disabled:bg-solid-gray-300 aria-disabled:text-solid-gray-50
  `,
  // outline, text …
};

export const buttonSizeStyle: { [key in ButtonSize]: string } = {
  lg: 'min-w-[calc(136/16*1rem)] min-h-14 rounded-8 px-4 py-3 text-oln-16B-100',
  // sm and xs add `after:h-[44px]` to reach the 44px touch target without growing the box
};
```

- **Plain style objects.** Variants are plain string maps exported alongside the component, so a variant
  can be reused on another element by importing the map.
- **`aria-disabled` marks a disabled control.** Disabled controls stay focusable and keyboard-reachable; the click
  handler calls `preventDefault()`. Keep this — it is the accessibility position of the system, and
  swapping in `disabled` silently removes the control from the tab order.
- **`asChild` through a local `Slot`.** Same idea as Radix's `Slot`, but a private implementation in
  `src/components/Slot`. Copy it once; every `asChild` component depends on it.
- **Focus is drawn twice**: a black `outline` plus a yellow `ring`, so the indicator survives on any
  background. `forced-colors:` variants cover Windows high-contrast mode.
- **Typography is one utility.** `text-oln-16B-100` sets size, weight, line-height and letter-spacing together.
  Never pair it with `font-bold` or `leading-*`.
- **Radius utilities are numeric**: `rounded-4`, `rounded-6`, `rounded-8`, `rounded-12`, matching the plugin's
  `--radius-*` steps.
- Interactive components import from `react-aria-components`. Install it before copying anything beyond the
  presentational pieces.

### Copying into a Tailwind v4 project

The repository targets Tailwind v3. Every DADS-specific class (`bg-key-900`, `text-oln-16B-100`, `rounded-8`)
comes from the plugin's v4 entry point and needs no change. Tailwind's own renamed utilities do:

| v3 | v4 |
|---|---|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `rounded-sm` | `rounded-xs` |
| `blur-sm` | `blur-xs` |
| `ring` | `ring-3` |
| `outline-none` | `outline-hidden` |

Grep each copied file for those six before wiring it up. React 19 also raises minor type errors against these
components; the README acknowledges it and leaves the fix to the caller.

## HTML conventions

Set out in the repository's own `AGENTS.md`, and worth matching in any markup written alongside:

- BEM naming under a `dads-` prefix, with variants selected by data attributes such as
  `[data-type="solid-fill"]`.
- Custom elements without Shadow DOM, so page CSS still applies. Listeners are removed in
  `disconnectedCallback`.
- Tokens live in `src/global.css` as `:root` custom properties, which is the same arrangement `theme.css` from Step 2 uses. On this route the Tailwind plugin is not needed at all.
- Sizes are written `calc(<px> / 16 * 1rem)`, with `px` reserved for borders.
- The target is WCAG 2.2 AA, verified by visual regression tests run against a set of CSS resets that includes
  Normalize.css and Bootstrap Reboot — so the components assume no particular reset.
