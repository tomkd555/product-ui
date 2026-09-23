# Components — shadcn/ui on Base UI, Radix or React Aria, with Tailwind v4

This file is read from Step 3 of `SKILL.md` when the request installs or adapts a component, binds theme variables to utilities, wires dark mode, builds an accessible dialog, dropdown, form or table, or lays out a responsive page with utility classes. Step 1 settles the tokens; `theme.css` generated in Step 2 is the only source of colour, type, spacing, radius, shadow and motion, and the classes below read it.

## Stack

| Layer | Default | Reference |
|---|---|---|
| Components | shadcn/ui on Base UI (`npx shadcn@latest init -b radix` or `-b aria` to switch; recorded in `tokens.json` under `stack.base`) | https://ui.shadcn.com/docs/components |
| Theming and dark mode | CSS variables bound through the two-tier `@theme inline` arrangement in `references/stack-defaults.md` | https://ui.shadcn.com/docs/theming, https://ui.shadcn.com/docs/dark-mode |
| Accessibility | The base supplies focus management and keyboard behaviour; the product writes the accessible names, labels and error text | https://base-ui.com/react/overview/accessibility, https://www.w3.org/WAI/ARIA/apg/patterns/ |
| Utilities | Tailwind v4 | https://tailwindcss.com/docs/styling-with-utility-classes, https://tailwindcss.com/docs/responsive-design, https://tailwindcss.com/docs/theme |

**Digital Agency Design System.** When `tokens.json` sets `meta.reference: "digital-agency-design-system"`, the components come from `references/dads-components.md`: it catalogues the 45 React and 42 HTML components デジタル庁 publishes, the copying procedure (there is no CLI), and the `aria-disabled` / `Slot` / numeric-radius conventions they follow. Do not mix DADS and shadcn in one surface. **SmartHR.** `references/smarthr.md` routes to smarthr-ui and its official plugin.

## Setup

```bash
npx shadcn@latest init            # framework, TypeScript, paths, theme
npx shadcn@latest add button card dialog form
```

Tailwind-only (Vite): `npm install -D tailwindcss @tailwindcss/vite`, add `tailwindcss()` to `vite.config.ts` plugins, and `@import "tailwindcss";` at the top of the stylesheet — which `theme.css` already carries.

## Rules that hold in every component

- Colours, fonts, radii and shadows come from `theme.css` variables (`bg-background`, `text-muted-foreground`, `rounded-md`, `shadow-sm`); a literal in a class string is what `check_slop.py` S1 reports.
- Text sizes follow `references/ban-list.md`: body `text-base` (16px), UI text no smaller than `text-sm` (14px), and `text-xs` (12px) only on a Latin-only run of at most 24 characters. `text-[Npx]` under 14 is an ST7 error unless the run is Latin-only, at most 24 characters, and at least 12px.
- Every form ships its states — `required`, `aria-invalid`, `aria-describedby`, a `FormMessage` — or `check_slop.py` S10 stops the pipeline.
- Mobile first: base classes for the narrow layout, `md:` and `lg:` variants for wider; inputs keep 16px on mobile so iOS Safari does not zoom.
- Dark mode through the `.dark` class and the `dark:` variant on every themed element, never a second palette.
- Extract a component only for real repetition; utility classes on the element are the default.

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

Responsive card grid that follows the theme in both modes:

```tsx
<div className="min-h-screen bg-background text-foreground">
  <div className="container mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <Card><CardContent className="p-6"><h3 className="text-xl font-semibold">注文</h3></CardContent></Card>
  </div>
</div>
```

Sources: shadcn/ui (https://ui.shadcn.com/llms.txt), Tailwind CSS (https://tailwindcss.com/docs), Base UI (https://base-ui.com), Radix UI (https://radix-ui.com).
