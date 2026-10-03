# Digital Agency Design System — Component Reference

The component implementations published by Japan's Digital Agency (デジタル庁デザインシステム), β, MIT-licensed (© デジタル庁). Counts and line numbers below are as of September 2026.

This is the component reference, in place of shadcn/ui, when `tokens.json` carries `meta.reference: "digital-agency-design-system"`. shadcn styles through semantic variables and Radix/Base UI primitives; DADS styles through its own palette utilities and either `react-aria-components` or plain custom elements. Pick one system per surface.

`references/dads.md` holds the token side and the `theme.css` import. Read it first; the React components need the Tailwind plugin installed, and the HTML route runs without it.

## There is no CLI

DADS is distributed as example code, outside the reach of `npx shadcn add`. Copy it:

```bash
# React
git clone --depth 1 https://github.com/digital-go-jp/design-system-example-components-react
cp -r design-system-example-components-react/src/components/Button src/components/

# HTML
git clone --depth 1 https://github.com/digital-go-jp/design-system-example-components-html
cp -r design-system-example-components-html/src/components/button src/components/
```

Browse before copying: https://design.digital.go.jp/dads/react/ and https://design.digital.go.jp/dads/html/.

Neither repository accepts pull requests; adaptations stay local.

## Which repository

`meta.stack.renderer` decides: `vite-react` and `next-react` take the React repository, `html` the HTML one.

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

Skip `Slot` (an internal helper) and the `deprecated/` and `v1/` directories (earlier versions). A component missing on one side is built from the primitives of the repository in use, since the two share no runtime.

## React conventions

`Button` (`src/components/Button/Button.tsx`, 102 lines) is the pattern the rest follow; read it once in full. The parts that generalise (excerpt, MIT, © Digital Agency; full licence text in `THIRD_PARTY_NOTICES.md` at the plugin root, or in this skill's directory under a manual install; from [Button.tsx](https://github.com/digital-go-jp/design-system-example-components-react/blob/main/src/components/Button/Button.tsx)):

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

- **Plain style objects.** Variants are string maps exported beside the component, so another element can import and reuse one.
- **`aria-disabled` marks a disabled control.** The control stays focusable and keyboard-reachable, and the click handler calls `preventDefault()`. Keep it: this is the system's accessibility position, and `disabled` would drop the control from the tab order.
- **`asChild` through a local `Slot`**, a private counterpart of Radix's `Slot` in `src/components/Slot`. Copy it once; every `asChild` component depends on it.
- **Focus is drawn twice**: a black `outline` plus a yellow `ring`, so the indicator survives on any background. `forced-colors:` variants cover Windows high-contrast mode.
- **Typography is one utility.** `text-oln-16B-100` sets size, weight, line-height and letter-spacing together; never pair it with `font-bold` or `leading-*`.
- **Radius utilities are numeric**: `rounded-4`, `rounded-6`, `rounded-8`, `rounded-12`, matching the plugin's `--radius-*` steps.
- Interactive components import from `react-aria-components`; install it before copying anything beyond the presentational pieces.

### Copying into a Tailwind v4 project

The repository targets Tailwind v3. DADS-specific classes (`bg-key-900`, `text-oln-16B-100`, `rounded-8`) come from the plugin's v4 entry point and work unchanged. Tailwind's own renamed utilities need fixing:

| v3 | v4 |
|---|---|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `rounded-sm` | `rounded-xs` |
| `blur-sm` | `blur-xs` |
| `ring` | `ring-3` |
| `outline-none` | `outline-hidden` |

Grep each copied file for those six before wiring it up. React 19 raises minor type errors against these components; the README acknowledges them and leaves the fix to the caller.

## HTML conventions

From the repository's own `AGENTS.md`; match them in markup written alongside:

- BEM naming under a `dads-` prefix, with variants selected by data attributes such as `[data-type="solid-fill"]`.
- Custom elements without Shadow DOM, so page CSS still applies. Listeners are removed in `disconnectedCallback`.
- Tokens live in `src/global.css` as `:root` custom properties, the same arrangement as `theme.css` from Step 2. The HTML route runs without the Tailwind plugin.
- Sizes are written `calc(<px> / 16 * 1rem)`, with `px` reserved for borders.
- The target is WCAG 2.2 AA, verified by visual regression tests against a set of CSS resets that includes Normalize.css and Bootstrap Reboot, so the components assume no particular reset.
