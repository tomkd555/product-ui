# Components: shadcn/ui on Base UI, Radix or React Aria, with Tailwind v4

Read from Step 3 of `SKILL.md` when the request installs or adapts a component, binds theme variables to utilities, wires dark mode, builds an accessible dialog, dropdown, form or table, or lays out a responsive page with utility classes. `theme.css` from Step 2 is the only source of colour, type, spacing, radius, shadow and motion.

## Stack

| Layer | Default | Reference |
|---|---|---|
| Components | shadcn/ui on Base UI (`npx shadcn@latest init -b radix` or `-b aria` to switch; recorded in `tokens.json` under `stack.base`) | https://ui.shadcn.com/docs/components |
| Theming and dark mode | CSS variables bound through the two-tier `@theme inline` arrangement in `references/stack-defaults.md` | https://ui.shadcn.com/docs/theming, https://ui.shadcn.com/docs/dark-mode |
| Accessibility | The base supplies focus management and keyboard behaviour; the product writes the accessible names, labels and error text | https://base-ui.com/react/overview/accessibility, https://www.w3.org/WAI/ARIA/apg/patterns/ |
| Utilities | Tailwind v4 | https://tailwindcss.com/docs/styling-with-utility-classes, https://tailwindcss.com/docs/responsive-design, https://tailwindcss.com/docs/theme |

- **Digital Agency Design System.** When `tokens.json` sets `meta.reference: "digital-agency-design-system"`, the components come from `references/dads-components.md`: the React and HTML components デジタル庁 publishes, the copying procedure (there is no CLI), and the `aria-disabled` / `Slot` / numeric-radius conventions they follow. Keep DADS and shadcn on separate surfaces.
- **SmartHR.** `references/smarthr.md` routes to smarthr-ui and its official plugin.
- **Astryx.** `references/astryx.md` routes to `@astryxdesign/core` and Astryx's own CLI.

## Setup

```bash
npx shadcn@latest init            # framework, TypeScript, paths, theme
npx shadcn@latest add button card dialog form
```

Tailwind-only (Vite): `npm install -D tailwindcss @tailwindcss/vite`, add `tailwindcss()` to `vite.config.ts` plugins, and `@import "tailwindcss";` at the top of the stylesheet, which `theme.css` already carries.

## Rules that hold in every component

- Colours, fonts, radii and shadows come from `theme.css` variables (`bg-background`, `text-muted-foreground`, `rounded-md`, `shadow-sm`); a literal in a class string is what `check_slop.py` S1 reports.
- `accent` takes shadcn's meaning: `bg-accent` is the hover and selected surface. The product's highlight colour is `bg-brand-accent` / `text-brand-accent`. Tailwind's default palette classes (`bg-blue-600`) are S1 errors unless `theme.css` defines that colour name.
- Text sizes follow `references/ban-list.md`: body `text-base` (16px), UI text `text-sm` (14px) or larger, and `text-xs` (12px) only on a Latin-only run of at most 24 characters. `text-[Npx]` under 14 is an ST7 error unless the run is Latin-only, at most 24 characters, and at least 12px. shadcn's own components carry sizes under that minimum: `Badge` is `text-xs`, `Button` at size `sm` and `xs` is `text-[0.8rem]` and `text-xs`, the `Avatar` fallback at size `sm` is `text-xs`, `ChartContainer` and `ChartTooltipContent` are `text-xs`, and so are `SelectLabel`, `DropdownMenuLabel` and `DropdownMenuShortcut`; Sonner's toast is 13px and its action button 12px, set through `toastOptions.classNames` (`toast: "!text-sm"`, `actionButton: "!h-8 !text-sm"`), since the captures hold no toast and no check reads it. Set them to `text-sm` in the project's copy when the screen first imports the component (the `Badge` then takes `h-6` in place of `h-5`): S35 and ST7 read every variant of an imported file, the unused ones too. `SelectTrigger` fixes its own height (`data-[size=default]:h-8`), so a height class on it takes the `!` modifier or the trigger's size prop.
- shadcn's components ship English strings: `Previous`, `Next`, `More pages` and the `aria-label`s of `Pagination`, `Close` in `Dialog` and `Sheet`, `breadcrumb` on `Breadcrumb`. On a Japanese screen, pass the product's own words for each one where the component takes a prop, and edit the string in the project's copy under `components/ui/` where the component writes it inline, as `dialog.tsx` and `sheet.tsx` write `Close`.
- A button that signs in with an identity provider follows the provider's own button guidelines, its mark included, from the asset the provider publishes. The mark is the provider's, so the rule against an invented logo leaves it alone. Where the asset is not at hand, the button carries the provider's name as text and the hand-over lists the missing mark.
- A link that looks like a button is an `<a>` with `className={cn(buttonVariants({ variant: "outline" }))}`; `cn()` keeps the variant's border beside other classes. Base UI's `Button` with `render={<a href=… />}` gives the link `role="button"`, and shadcn's `Pagination` ships its links that way.
- Base UI's `Checkbox` puts the `id` prop on its hidden input and gives the visible `role="checkbox"` element a generated id: focus an invalid checkbox through a ref.
- The destructive `Alert` paints its description at `text-destructive/90`, which falls under 4.5:1 on a light ground with many palettes: set it to `text-destructive` or the text colour and check the pair.
- Tailwind's base styles give a link the colour and decoration of the text around it. The links that production screens colour take `text-primary` or an underline in the markup (`references/real-screens.md`, Every screen).
- A chart series takes `var(--chart-1)` to `var(--chart-5)`, which `theme.css` binds to the primary, the brand accent and three neutral steps. A chart that needs more hues gets them in `tokens.json`, from the chart rows of the lookup.
- A chart's value axis states its unit, on the ticks (`1,500万円`) or beside the chart's heading (`週別売上（万円）`), and a date axis that crosses a year prints the year once.
- A chart is drawn at rest: a Recharts series sets `isAnimationActive={false}`. The entry animation is motion nobody asked for, and a capture taken during it shows half a chart.
- Every form ships its states (`required`, `aria-invalid`, `aria-describedby`, a `FormMessage`) or `check_slop.py` S10 stops the pipeline. Where the project carries no `form` component and no react-hook-form (shadcn's Base UI set ships neither), a plain `<form>` carries the same states: `required` and `aria-invalid` on the control, `aria-describedby` pointing at a message with `role="alert"` under the field.
- Mobile first: base classes for the narrow layout, `md:` and `lg:` variants for wider; inputs keep 16px on mobile so iOS Safari does not zoom.
- Dark mode toggles the `.dark` class on the root; themed utilities (`bg-background`, `text-foreground`) follow it through the two tiers in `theme.css`, so an element takes a `dark:` variant only where its dark appearance departs from its token, and then with a token class.
- Utility classes on the element are the default; extract a component only for real repetition.
- `Card` goes where production screens of the kind draw a panel (`references/real-screens.md` names the enclosed regions of each kind; the container table is in `references/composition.md`): a record with an image or several lines in a browsed set, a plan on a pricing page, a breakdown on a monitoring screen, an account form on a tinted ground. A `Card` opened directly inside a `Card` is `check_slop.py` S11.
- The screen sits in the product's shell: a header with the product name or logo, the navigation, and the account controls, then `<main>` ("The shell" in `references/composition.md`). A project that already has a shell component uses it.

## The kit

`assets/kit/` holds the parts every application screen repeats, written for the `shadcn` stack: React, Tailwind v4 through `theme.css`, the shadcn/ui components under `@/components/ui` and react-router-dom. `scripts/kit.py` copies them into the project at Step 3, before the first screen is built. From then on they are the project's own files, changed where `assets/kit/kit.json` says a project changes them.

```bash
python {SKILL_DIR}/scripts/kit.py <project-dir>                       # every part
python {SKILL_DIR}/scripts/kit.py <project-dir> form-field line-grid  # the named parts, with the parts they need
python {SKILL_DIR}/scripts/kit.py --list
```

It writes into `<project-dir>/src` where that directory exists (the directory the `@/` alias points to), keeps a file the project already holds unless `--force` is given, and prints what is left to do: the shadcn components to add, the packages to install and the stylesheet import of `kit.css`.

| Part | File | Gives |
|---|---|---|
| `format` | `lib/format.ts` | The one format of each kind of value: dates, amounts, counts |
| `collection` | `lib/collection.ts` | Search, filters, views, sort and pages kept in the URL; the selection of a bulk action |
| `record-store` | `lib/record-store.ts` | The sample records with the reader's changes, each change returning its undo |
| `form` | `lib/form.ts` | Every field checked on submit, and the focus on the first field in error |
| `keys` | `lib/keys.ts` | Enter from field to field in an entry form; a function key or a shortcut running the button that carries it (`references/interaction.md`, Keys) |
| `submit-guard` | `lib/submit-guard.ts` | One run at a time for an operation that sends data |
| `app-shell` | `components/app-shell.tsx` | The header with the product name, the navigation, the content column and the toaster. `maxToasts` takes `messages.max` of the Conventions section, and `keysAtFoot` lifts the toasts above a row of function keys |
| `not-found` | `components/not-found.tsx` | The screen of an address the product does not have |
| `status-badge` | `components/status-badge.tsx` | The pattern `status.badge` |
| `empty-state` | `components/empty-state.tsx` | The pattern `state.empty` |
| `list-controls` | `components/list-controls.tsx` | The search field, the filters, the sort, the view tabs, the count and the pagination of a collection |
| `bulk-bar` | `components/bulk-bar.tsx` | The bar of a bulk action |
| `confirm-dialog` | `components/confirm-dialog.tsx` | The pattern `feedback.confirm` |
| `form-field` | `components/form-field.tsx` | A field's label, its required mark, its control and its message |
| `function-keys` | `components/function-keys.tsx` | The pattern `action.function-keys` |
| `message-bar` | `components/message-bar.tsx` | The pattern `feedback.message`: a toast, a bar or a line beside the control |
| `line-grid` | `components/line-grid.tsx` | The lines of the pattern `entry.slip` |
| `table-fold` | `kit.css` | A table whose rows fold into list items under 768px |
| `desktop-main` | `main/document-window.ts` | The Electron window of a document: `titleBarStyle: 'hidden'` with Electron's caption buttons at the title row's height, the minimum size, the safe `webPreferences`, every permission refused except `clipboard-read` and `clipboard-sanitized-write`, no default menu, the close flow that waits for the save prompt, the file operations (export takes text or bytes, with its own file filters), the title row's colours from `WINDOW_SPEC`, DevTools on Ctrl+Shift+I in development only |
| `desktop-preload` | `preload/document-api.ts` | `contextBridge` functions: open, save, save as, export, `edit(action)` (the main process checks `action` against `EDIT_ACTIONS`), the unsaved-changes flag, the close request and answer |
| `desktop-window-types`, `desktop-document-api` | `shared/window-types.ts`, `shared/document-api.ts` | The types `WINDOW_SPEC` and the preload API share between the main process, the preload script and the renderer |
| `desktop-host` | `lib/host.ts` | The preload API, or an in-memory stand-in so that the renderer runs in a plain browser; `?doc=sample` there opens the sample document |
| `desktop-document-state` | `lib/document-state.ts` | The document's name, unsaved changes, history depths, selection and zoom; `create(content)` for an untitled document that holds a template; the title `<file> - <product>` kept equal to `document.title` |
| `desktop-commands` | `lib/commands.ts` | `CommandSpec`, the keys with the text-field rules (outside and inside the document area), the tooltip, the `product-ui:command` event |
| `desktop-document-commands` | `lib/document-commands.ts` | What new, open, save, save as, export, close, print, zoom, zoom-fit (the element marked `data-document-page` fits the document region) and the edit commands (undo, redo, cut, copy, paste, select all, delete, through `edit`) run |
| `desktop-ribbon-layout` | `lib/ribbon-layout.ts` | The order and the plan in which the ribbon's groups collapse |
| `desktop-floating`, `desktop-key-tip`, `desktop-command-button` | `components/floating.tsx`, `key-tip.tsx`, `command-button.tsx` | The tooltip and the panel, the key tips (`data-keytip`), and the control of one command (`data-command`, `data-key`) |
| `desktop-title-row`, `desktop-ribbon`, `desktop-file-view`, `desktop-task-pane`, `desktop-status-bar`, `desktop-save-prompt` | `components/title-row.tsx` and the files of those names | The regions of the document window (`references/desktop.md`) |
| `desktop-shell` | `components/document-shell.tsx` | The regions laid out (the file view's cover makes the regions under it `inert`; a pane closed for width stays mounted and hidden), the window's keys, the save prompt flow, `ShellApi` (`paneOpen`, `togglePane`, `showFile`, `showDocument`, `fail`, `notify`, `guard`) and the capture states read from the URL query |

- A screen imports a part where it would otherwise write that behaviour again. The search of a collection, the validation of a form and the keys of an entry screen then behave the same in every build.
- A part that draws a pattern carries the pattern's attributes (`data-pattern`, `data-pattern-slot`), so the checks read a screen built on the kit as they read one built from a skeleton. Step 4 runs over the parts the screen imports.
- The skeletons `scaffold.py` writes for the patterns from business packages import the kit (`FormField`, `LineGrid`, `FunctionKeys`, `ConfirmDialog`, `useMessages`, `useEnterKeys`, `useKeyButtons`, `useSubmitGuard`) and pass it the values of the brief's Conventions section (`references/profiles.md`).
- The parts keep the rules above: theme variables, text at 14px or more, Japanese strings.
- The `desktop-*` parts go only into a project with electron-vite's layout (`src/main`, `src/renderer/src`): main and preload parts into `src/main` and `src/preload`, the shared types into `src/shared`, the renderer parts under `src/renderer/src`. There the desktop parts always go in, and a part named on the command line (`form-field`, `line-grid`), one the skeletons of the document area or a pane import, joins them under `src/renderer/src`. The project copies `scaffold/window-spec.ts` and `scaffold/command-set.ts` (written by `scaffold.py` on `desktop`) to `src/shared/window-spec.ts` and `src/renderer/src/command-set.ts`. The project's main entry calls `runDocumentApp` with `WINDOW_SPEC`, the app id and the paths of the preload script and the renderer folder (`out/renderer`, served at `app://renderer/`); the title row's caption button colours come from `WINDOW_SPEC.colors` and `darkColors` (hex, written by `scaffold.py` from `tokens.json`) unless the entry passes `colors` or `darkColors`, and `filters` and `exportFilters` name the file types of the open and save dialogs and of the export dialog, its preload entry imports `./document-api`, and its renderer renders `<DocumentShell spec={WINDOW_SPEC} commands={COMMAND_SET}>`; the tsconfigs include `src/shared`. The `@/` alias is declared in `tsconfig.web.json` for the build and in the root `tsconfig.json` for the shadcn CLI, which reads only the root file: the root `tsconfig.json` carries `"compilerOptions": { "baseUrl": ".", "paths": { "@/*": ["src/renderer/src/*"] } }`, since `npx shadcn add` otherwise writes into a literal `@/` folder.
- The `html`, `dads`, `smarthr` and `astryx` stacks take the kit as the description of the behaviour and write it on their own components.

## Patterns

The patterns below follow the shadcn/ui documentation examples (MIT, © 2023 shadcn; full licence text in `THIRD_PARTY_NOTICES.md` at the plugin root, or in this skill's directory under a manual install).

Form with validation (react-hook-form + zod):

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
    <FormField control={form.control} name="email" render={({ field }) => (
      <FormItem>
        <FormLabel>メールアドレス</FormLabel>
        <FormControl><Input type="email" required aria-invalid={!!form.formState.errors.email} {...field} /></FormControl>
        <FormMessage />
      </FormItem>
    )} />
    <Button type="submit" className="w-full">保存</Button>
  </form>
</Form>
```

A page in its shell, following the theme in both modes; the sections sit on the ground and the one `Card` holds the unit the composition plan encloses:

```tsx
<div className="min-h-screen bg-background text-foreground">
  <header className="flex h-14 items-center gap-6 border-b border-border px-4">
    <a href="/" className="font-semibold">{productName}</a>
    <nav aria-label="メイン" className="flex gap-4 text-sm">…</nav>
    <div className="ml-auto flex items-center gap-2">…</div>
  </header>
  <main className="container mx-auto px-4 py-8 space-y-10">
    <section>
      <h2 className="text-2xl font-semibold">満期3か月以内の契約</h2>
      <Table>…</Table>
    </section>
    <section>
      <h2 className="text-lg font-semibold">未読のお知らせ</h2>
      <ul className="divide-y divide-border">…</ul>
    </section>
    <Card><CardContent className="p-6">…</CardContent></Card>
  </main>
</div>
```

Sources: shadcn/ui (https://ui.shadcn.com/llms.txt), Tailwind CSS (https://tailwindcss.com/docs), Base UI (https://base-ui.com), Radix UI (https://radix-ui.com).
