# Default stack

This file is the source of record for what this skill builds with when the request names nothing. A project that already has a stack keeps it; these defaults settle the greenfield case.

## The layers

| Layer | Default | Why this one |
|---|---|---|
| Tokens | Tailwind CSS v4 `@theme`, with context-dependent tokens in a two-tier `@theme inline` plus `:root`/`.dark` arrangement | A variable declared in `@theme` is emitted as a CSS custom property and decides which utility classes exist. "A value outside the token set cannot be written" holds structurally rather than by instruction |
| Components | shadcn/ui on **Base UI** | Focus management and keyboard behaviour need a base that supplies them, and React is the only ecosystem where three such bases are first-class options in shadcn |
| SaaS renderer | Vite + React | An application screen is mostly interaction — state, events, focus — and that is where an application framework earns its cost |
| Landing-page renderer | Astro, using the same React components as islands | Astro renders every UI component to HTML and CSS by default, stripping client JavaScript. The component layer stays shared with the SaaS side, so nothing is implemented twice |

## Permitted pairings

`validate_tokens.py` check T8 enforces this table.

| `meta.surface` | `stack.renderer` | Note |
|---|---|---|
| `saas` | `vite-react` | default |
| `saas` | `next-react` | when the project already runs Next.js |
| `lp` | `astro-react` | default |
| `lp` | `next-react` | when the landing page lives inside an existing Next.js app |
| `lp` | `html` | a single self-contained file, no build step. `stack.base` is `null` |
| `saas` | `server-templates` | **warned, not permitted.** An existing application that renders its screens from server templates — Flask, Django, Rails, htmx — with no bundler. `stack.base` is `null`. T8 warns instead of failing, and `defaults_applied` records that dialogs and menus have no component base, so focus management and keyboard behaviour follow the APG dialog pattern linked below, written by hand |

`saas` with `html` is rejected. A single HTML file has no component base, which leaves focus management and keyboard behaviour to be rewritten by hand on every dialog. `server-templates` admits the same gap for a project that already exists and cannot be moved; it is never a choice for a new one.

## Why not Next.js by default

Next.js describes itself as a framework for building full-stack web applications. Routing, server execution and React Server Components are surface a UI-generation task does not need, and every additional surface is somewhere generation can fail. It stays a sound choice for a project already built on it, which is why the pairing table admits it.

## Tailwind v4 in practice

### The two tiers

`@theme` alone is not enough for anything that changes with context. Values declared inside `@theme inline` get no global CSS variable, so nothing exists to override later. Dark mode therefore needs two tiers, which is also the shape shadcn/ui itself uses:

```css
@import "tailwindcss";

/* Tier 1 — the raw palette. Global variables, overridable. */
:root {
  --brand-bg: oklch(98.5% 0.002 247);
  --brand-fg: oklch(20% 0.01 247);
}

.dark {
  --brand-bg: oklch(16% 0.008 247);
  --brand-fg: oklch(96% 0.004 247);
}

/* Tier 2 — semantic names bound to the tier above, and the utilities they generate. */
@theme inline {
  --color-background: var(--brand-bg);
  --color-foreground: var(--brand-fg);
}
```

`bg-background` now follows the theme in both modes. Declaring the semantic names directly in a plain `@theme` block would freeze them.

`assets/theme.template.css` carries this arrangement filled in from `tokens.json`.

### What changed from v3

Configuration moved into CSS. A `tailwind.config.js` still works for backward compatibility but is no longer detected automatically — it has to be pulled in with `@config`. The default palette moved from rgb to oklch. The browser floor is Safari 16.4, Chrome 111, Firefox 128; below that, v4 does not run.

Anything written for v3 is a hazard here rather than a head start: a config-file answer to "how do I add a colour" is now the wrong answer.

## The component base

shadcn/ui defaults new projects to Base UI ([changelog, July 2026](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default)). Radix remains supported — updates and new components ship for both — and React Aria Components is a first-class base as well ([changelog](https://ui.shadcn.com/docs/changelog/2026-07-react-aria)). Three viable bases is the practical hedge: a stall in any one of them costs one flag to `shadcn init`.

Pick a different base with `shadcn init -b radix` or `-b aria` ([CLI reference](https://ui.shadcn.com/docs/cli)), and record the choice in `tokens.json` under `stack.base`.

`stack.base` takes a fourth value, `smarthr-ui`. It is not a headless base but a component library carrying its own styling, so it replaces both layers at once; `references/smarthr.md` holds that route.

### The "every shadcn app looks the same" objection

It is a real observation, and shadcn's own changelog concedes it ([December 2025](https://ui.shadcn.com/docs/changelog/2025-12-shadcn-create)): "all apps started looking the same. I guess the defaults were a little _too_ good."

The cause is the untouched default theme. This skill settles tokens before any component is installed, which is the direct answer. Nothing in the objection argues against the accessibility behaviour the base supplies, which is what the components are being used for.

## Reference documents

As of September 2026, Tailwind publishes no `llms.txt`: the pull request adding one was closed with docs traffic cited as the reason ([tailwindcss.com#2388](https://github.com/tailwindlabs/tailwindcss.com/pull/2388)). Radix serves none at `radix-ui.com/llms.txt` either. Astro removed its own and pointed to its MCP server ([withastro/docs#13538](https://github.com/withastro/docs/pull/13538)). So this file summarises the Tailwind material that matters, and the rest comes through MCP.

| Source | How to reach it |
|---|---|
| shadcn/ui registry | MCP server: `pnpm dlx shadcn@latest mcp init --client claude` |
| Astro documentation | MCP server at `https://mcp.docs.astro.build/mcp` |
| Tailwind theme variables | `https://tailwindcss.com/docs/theme` |
| Tailwind upgrade notes and browser floor | `https://tailwindcss.com/docs/upgrade-guide` |
| Base UI | `https://base-ui.com/react/overview/quick-start` |
| Dialog and focus requirements | `https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/` |

Supplying documentation has a modest effect; the tokens and the lint carry the quality here. On real-world class-level code generation, comprehensive docstrings in the class skeleton improved results by 1–3% (Rahman, Khatoonabadi and Shihab, [arXiv:2510.26130](https://arxiv.org/abs/2510.26130)).

## Watch for a reason to move off Tailwind

The token layer rests on one library, so it carries a stated exit. Watch Tailwind's release cadence on its [releases page](https://github.com/tailwindlabs/tailwindcss/releases).

Move when either of these becomes true:

- No patch release for six months
- A published CVE unfixed for ninety days

The exit is mechanical. `@theme` already emits ordinary CSS custom properties, so the token layer survives as plain CSS; what is lost is the generated utility classes and the lint rules that police them.

Two other things worth watching, each with a cheaper answer:

- **The component base stalls.** From July 2025 to April 2026 the main branch of [radix-ui/primitives](https://github.com/radix-ui/primitives/commits/main) took about four commits a month before activity recovered. If Base UI slows the same way, switch with `shadcn init -b radix` or `-b aria`
- **Astro drops its React integration.** Move landing pages to Vite + React and handle static output at build time
