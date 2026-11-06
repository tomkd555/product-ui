# Digital Agency Design System: Component Reference

The component implementations published by Japan's Digital Agency (デジタル庁デザインシステム), β, MIT-licensed (© デジタル庁).

This is the component reference, in place of shadcn/ui, when `tokens.json` carries `meta.reference: "digital-agency-design-system"`. shadcn styles through semantic variables and Radix/Base UI primitives; DADS styles through its own palette utilities, in React components that import React alone or in plain custom elements. Pick one system per surface.

`references/dads.md` holds the token side and the `theme.css` import. Read it first; the React components need the plugin's `v4.css`, from npm or vendored, and the HTML route runs without it.

## There is no CLI

DADS is distributed as example code, outside the reach of `npx shadcn add`. Clone the repository into a temporary directory outside the project, copy the directories the screen needs from the project root, and delete the clone:

```bash
# React: list the component directories after -cf -, with Slot for the asChild components
tmp="$(mktemp -d)"
git clone --depth 1 https://github.com/digital-go-jp/design-system-example-components-react "$tmp/dads"
mkdir -p src/components
tar -C "$tmp/dads/src/components" --exclude='*.stories.tsx' --exclude='*.test.tsx' \
  --exclude='*.mdx' --exclude='component-spec.md' -cf - Button Slot | tar -C src/components -xf -
cp "$tmp/dads/LICENSE" src/components/LICENSE-dads
rm -rf "$tmp"

# HTML: global.css holds the custom properties the component stylesheets read
tmp="$(mktemp -d)"
git clone --depth 1 https://github.com/digital-go-jp/design-system-example-components-html "$tmp/dads"
mkdir -p src/components
tar -C "$tmp/dads/src/components" --exclude='*.stories.ts' --exclude='*.vrt.js' \
  --exclude='*.test.js' --exclude='*.unit.js' --exclude='*.mdx' -cf - button | tar -C src/components -xf -
cp "$tmp/dads/src/global.css" src/dads-global.css
cp "$tmp/dads/LICENSE" src/components/LICENSE-dads
rm -rf "$tmp"
```

The `tar` pair copies the component files. It leaves out the stories and tests, which import Storybook and the test runners, and the Storybook docs. `LICENSE-dads` keeps the repository's MIT notice beside the copied code, as the licence requires.

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
| `Calendar` (stories only) | `calendar` |
| `Card` (stories only) | `card` (DADS: 「単一の主題に関するコンテンツをまとめて表示するコンテナ」, and tables for comparison; the container rule in `references/composition.md` says the same) |
| `Carousel` | `carousel` |
| `Checkbox` | `checkbox` |
| `ChipLabel` | `chip-label` |
| `DatePicker` | `date-picker` |
| `Disclosure` | `disclosure` |
| `Divider` | `divider` |
| `Dl` | `description-list` |
| `Drawer` (stories only) | `drawer` |
| `EmergencyBanner` | `emergency-banner` |
| `ErrorText` | the error-text part of `form-control-label` |
| `FileUpload` | `file-upload` |
| `FormControlLabel`, which also exports `Label`, `Legend`, `RequirementBadge`, `StatusBadge` and `SupportText` | `form-control-label` |
| `HamburgerMenuButton` | `hamburger-menu-button` |
| `Heading` | `heading` |
| `HorizontalMenu` | `horizontal-menu` |
| `Image` | `image` |
| `Input` | `input-text` |
| `LanguageSelector` | `language-selector` |
| `Link` | `link` |
| `List` | `list` |
| `MenuList` | `menu-list` |
| `MenuListBox` | `menu-list-box` |
| `ModalDialog` | `modal-dialog` |
| `NotificationBanner` | `notification-banner` |
| `PageNavigation` | `page-navigation` |
| `ProgressIndicator` | `progress-indicator` |
| `Radio` | `radio` |
| `ResourceList` | `resource-list` |
| `SearchBox` | `search-box` |
| `Select` | `select` |
| `SeparatedDatePicker` | the separated variant of `date-picker` |
| `StepNavigation` | `step-navigation` |
| `Switch` | `switch` |
| `Tab` | `tab` |
| `Table` (stories only) | `table` |
| `Textarea` | `textarea` |
| `UtilityLink` | `utility-link` |
| none | `toc` |

A React row marked (stories only) has Storybook stories and no component file: the stories compose the other components with plain markup, and a screen copies the markup of the story it needs. `Slot` is an internal helper outside the table, which the `asChild` components import, and `deprecated/` holds retired components. A component missing on one side is built from the primitives of the repository in use, since the two share no runtime.

## React conventions

`Button` (`src/components/Button/Button.tsx`) is the pattern the rest follow; read it once in full. The parts that generalise (excerpt, MIT, © Digital Agency; full licence text in `THIRD_PARTY_NOTICES.md` at the plugin root, or in this skill's directory under a manual install; from [Button.tsx](https://github.com/digital-go-jp/design-system-example-components-react/blob/main/src/components/Button/Button.tsx)):

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
- The component files import `react`, and `FileUpload` also imports `react-dom`. They don't import any other package. `react-aria-components` and `@internationalized/date` appear in the Calendar, DatePicker and SeparatedDatePicker stories alone, which build the calendar popup with them. Install both when a screen copies that calendar, and record `react-aria` as `meta.stack.base` (`references/dads.md`, Which implementation to copy).

### Copying into a Tailwind v4 project

A copied component is one of the screen's own files, so Step 4 reads it: a hex fill in its SVG (`#666` in `StepNavigation`) is an S1 error, and takes `currentColor` with a text utility. The inventory holds no time field; a time takes `Input` with `type="time"`. Where `react-aria-components` and `@internationalized/date` cannot be installed, `DatePicker` is used without `DatePickerCalendarButton`, and Step 4 lists the rendered component files one by one.

The components join `className` after their own classes, with no merge step, and `Input` and `Select` carry `max-w-full`: a width goes on an element that wraps the field, and a grid that holds fields declares its columns (`grid-cols-1`).

The repository targets Tailwind v3. DADS-specific classes (`bg-key-900`, `text-oln-16B-100`, `rounded-8`, `shadow-1`) come from the plugin's v4 entry point and the `theme.css` of this route, and work unchanged. These v3 forms need fixing:

| v3 | v4 |
|---|---|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `rounded-sm` | `rounded-xs` |
| `blur-sm` | `blur-xs` |
| `ring` | `ring-3` |
| `outline-none` | `outline-hidden` |
| `top-[--baseline-offset]`, `bg-[--bg]`: a custom property in square brackets, without `var()` | `top-(--baseline-offset)`, `bg-(--bg)` |
| `[--bg:theme(colors.white)]`, `[--bg:theme(colors.solid-gray.50)]`: `theme()` with a dot path | `[--bg:var(--color-white)]`, `[--bg:var(--color-solid-gray-50)]` |
| `desktop:`, the 48em screen of the v3 plugin | `desktop:`, unchanged: `theme.css` on this route declares `--breakpoint-desktop: 48em` |

Grep each copied file for the left column before wiring it up. v4 compiles `top-[--baseline-offset]` to `top: --baseline-offset`, a declaration the browser drops, so the Checkbox and Radio marks and the DatePicker background lose their values. Accordion, EmergencyBanner and NotificationBanner use `desktop:`, and the plugin doesn't declare a breakpoint for it. Without the `theme.css` line, v4 compiles those classes to no CSS. The components target React 19. For a React 18 project, the repository's `docs/using-with-react-v18.md` lists the changes: wrap each component that takes a `ref` in `forwardRef`, and change `RefObject<T | null>` to `RefObject<T>` in `useModalDialog`, `useTab` and `useTabAria`.

## HTML conventions

From the repository's own `AGENTS.md`; match them in markup written alongside:

- BEM naming under a `dads-` prefix, with variants selected by data attributes such as `[data-type="solid-fill"]`.
- Custom elements without Shadow DOM, so page CSS still applies. Listeners are removed in `disconnectedCallback`.
- Tokens live in `src/global.css` as `:root` custom properties, the same arrangement as `theme.css` from Step 2. The component stylesheets read them (`--color-key-900`). The copy command brings the file in as `src/dads-global.css`, and the page loads it before the component CSS. The HTML route runs without the Tailwind plugin.
- Sizes are written `calc(<px> / 16 * 1rem)`, with `px` reserved for borders.
- The target is WCAG 2.2 AA, verified by visual regression tests against a set of CSS resets that includes Normalize.css and Bootstrap Reboot, so the components assume no particular reset.
