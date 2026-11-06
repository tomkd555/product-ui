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

## Setup

```bash
npx shadcn@latest init            # framework, TypeScript, paths, theme
npx shadcn@latest add button card dialog form
```

Tailwind-only (Vite): `npm install -D tailwindcss @tailwindcss/vite`, add `tailwindcss()` to `vite.config.ts` plugins, and `@import "tailwindcss";` at the top of the stylesheet, which `theme.css` already carries.

## Rules that hold in every component

- Colours, fonts, radii and shadows come from `theme.css` variables (`bg-background`, `text-muted-foreground`, `rounded-md`, `shadow-sm`); a literal in a class string is what `check_slop.py` S1 reports.
- `accent` takes shadcn's meaning: `bg-accent` is the hover and selected surface. The product's highlight colour is `bg-brand-accent` / `text-brand-accent`. Tailwind's default palette classes (`bg-blue-600`) are S1 errors unless `theme.css` defines that colour name.
- Text sizes follow `references/ban-list.md`: body `text-base` (16px), UI text `text-sm` (14px) or larger, and `text-xs` (12px) only on a Latin-only run of at most 24 characters. `text-[Npx]` under 14 is an ST7 error unless the run is Latin-only, at most 24 characters, and at least 12px. shadcn's own components carry sizes under that minimum: `Badge` is `text-xs`, `Button` at size `sm` and `xs` is `text-[0.8rem]` and `text-xs`, the `Avatar` fallback at size `sm` is `text-xs`, `ChartContainer` and `ChartTooltipContent` are `text-xs`, and so are `SelectLabel`, `DropdownMenuLabel` and `DropdownMenuShortcut`. Set them to `text-sm` in the project's copy when the screen first imports the component (the `Badge` then takes `h-6` in place of `h-5`): S35 and ST7 read every variant of an imported file, the unused ones too. `SelectTrigger` fixes its own height (`data-[size=default]:h-8`), so a height class on it takes the `!` modifier or the trigger's size prop.
- shadcn's components ship English strings: `Previous`, `Next`, `More pages` and the `aria-label`s of `Pagination`, `Close` in `Dialog` and `Sheet`, `breadcrumb` on `Breadcrumb`. On a Japanese screen, pass the product's own words for each one.
- A button that signs in with an identity provider follows the provider's own button guidelines, its mark included, from the asset the provider publishes. The mark is the provider's, so the rule against an invented logo leaves it alone. Where the asset is not at hand, the button carries the provider's name as text and the hand-over lists the missing mark.
- A link that looks like a button is an `<a>` with `buttonVariants()`. Base UI's `Button` with `render={<a href=… />}` gives the link `role="button"`, and shadcn's `Pagination` ships its links that way.
- Base UI's `Checkbox` puts the `id` prop on its hidden input and gives the visible `role="checkbox"` element a generated id: focus an invalid checkbox through a ref.
- The destructive `Alert` paints its description at `text-destructive/90`, which falls under 4.5:1 on a light ground with many palettes: set it to `text-destructive` or the text colour and check the pair.
- Tailwind's base styles give a link the colour and decoration of the text around it. The links that production screens colour take `text-primary` or an underline in the markup (`references/real-screens.md`, Every screen).
- A chart series takes `var(--chart-1)` to `var(--chart-5)`, which `theme.css` binds to the primary, the brand accent and three neutral steps. A chart that needs more hues gets them in `tokens.json`, from the chart rows of the lookup.
- A chart is drawn at rest: a Recharts series sets `isAnimationActive={false}`. The entry animation is motion nobody asked for, and a capture taken during it shows half a chart.
- Every form ships its states (`required`, `aria-invalid`, `aria-describedby`, a `FormMessage`) or `check_slop.py` S10 stops the pipeline. Where the project carries no `form` component and no react-hook-form (shadcn's Base UI set ships neither), a plain `<form>` carries the same states: `required` and `aria-invalid` on the control, `aria-describedby` pointing at a message with `role="alert"` under the field.
- Mobile first: base classes for the narrow layout, `md:` and `lg:` variants for wider; inputs keep 16px on mobile so iOS Safari does not zoom.
- Dark mode toggles the `.dark` class on the root; themed utilities (`bg-background`, `text-foreground`) follow it through the two tiers in `theme.css`, so an element takes a `dark:` variant only where its dark appearance departs from its token, and then with a token class.
- Utility classes on the element are the default; extract a component only for real repetition.
- `Card` goes where production screens of the kind draw a panel (`references/real-screens.md` names the enclosed regions of each kind; the container table is in `references/composition.md`): a record with an image or several lines in a browsed set, a plan on a pricing page, a breakdown on a monitoring screen, an account form on a tinted ground. A `Card` opened directly inside a `Card` is `check_slop.py` S11.
- The screen sits in the product's shell: a header with the product name or logo, the navigation, and the account controls, then `<main>` ("The shell" in `references/composition.md`). A project that already has a shell component uses it.

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
