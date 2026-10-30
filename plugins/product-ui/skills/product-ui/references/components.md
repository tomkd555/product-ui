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
- Text sizes follow `references/ban-list.md`: body `text-base` (16px), UI text `text-sm` (14px) or larger, and `text-xs` (12px) only on a Latin-only run of at most 24 characters. `text-[Npx]` under 14 is an ST7 error unless the run is Latin-only, at most 24 characters, and at least 12px.
- Every form ships its states (`required`, `aria-invalid`, `aria-describedby`, a `FormMessage`) or `check_slop.py` S10 stops the pipeline.
- Mobile first: base classes for the narrow layout, `md:` and `lg:` variants for wider; inputs keep 16px on mobile so iOS Safari does not zoom.
- Dark mode toggles the `.dark` class on the root; themed utilities (`bg-background`, `text-foreground`) follow it through the two tiers in `theme.css`, so an element takes a `dark:` variant only where its dark appearance departs from its token, and then with a token class.
- Utility classes on the element are the default; extract a component only for real repetition.
- `Card` is for one unit in a browsed heterogeneous set, or for a group that distance cannot separate; a section of the page is a heading and spacing on the ground, and a `Card` inside a `Card` is `check_slop.py` S11 (`references/composition.md`).

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

A page of sections on the ground, following the theme in both modes; the one `Card` holds the browsed unit the composition plan admits:

```tsx
<main className="min-h-screen bg-background text-foreground">
  <div className="container mx-auto px-4 py-8 space-y-10">
    <section>
      <h2 className="text-2xl font-semibold">満期3か月以内の契約</h2>
      <Table>…</Table>
    </section>
    <section>
      <h2 className="text-lg font-semibold">未読のお知らせ</h2>
      <ul className="divide-y divide-border">…</ul>
    </section>
    <Card><CardContent className="p-6">…</CardContent></Card>
  </div>
</main>
```

Sources: shadcn/ui (https://ui.shadcn.com/llms.txt), Tailwind CSS (https://tailwindcss.com/docs), Base UI (https://base-ui.com), Radix UI (https://radix-ui.com).
