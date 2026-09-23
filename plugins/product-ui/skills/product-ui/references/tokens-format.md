# tokens.json format

This file is the source of record for the structure and validation rules of `tokens.json`. `scripts/validate_tokens.py` implements the rules written here; change this file first when a rule changes. A worked example lives in `assets/tokens_example.json`.

## Why tokens come first

Telling a model not to use a colour does not hold. Anthropic's prompting cookbook, [Prompting for frontend aesthetics](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb) (as of September 2026), names the fonts to avoid and still has to add "You still tend to converge on common choices (Space Grotesk, for example) across generations." A negative instruction cannot be checked; "did this file use a value outside the token set" can.

So the tokens are settled before any markup exists, and the implementation uses only those variables. Tailwind CSS v4's `@theme` emits each declared variable as a CSS custom property and, at the same time, decides which utility classes exist. A colour outside the token set has no class to write.

## Structure

```json
{
  "meta": {
    "name": "project name",
    "surface": "saas",
    "reference": "product being referenced, or null",
    "stack": {
      "renderer": "vite-react",
      "tailwind": "4",
      "base": "base-ui"
    },
    "defaults_applied": ["items settled by default rather than asked about"]
  },
  "color": {
    "background": "oklch(98.5% 0.002 247)",
    "foreground": "oklch(20% 0.01 247)",
    "surface": "oklch(100% 0 0)",
    "primary": "oklch(55% 0.18 27)",
    "primary_foreground": "oklch(99% 0.002 27)",
    "muted": "oklch(96% 0.004 247)",
    "muted_foreground": "oklch(50% 0.012 247)",
    "border": "oklch(92% 0.005 247)",
    "destructive": "oklch(58% 0.21 27)",
    "accent": "oklch(72% 0.14 85)"
  },
  "color_dark": {
    "background": "oklch(16% 0.008 247)",
    "foreground": "oklch(96% 0.004 247)"
  },
  "typography": {
    "display": { "family": "Fraunces", "source": "Google Fonts", "weights": [400, 700] },
    "body": { "family": "Public Sans", "source": "Google Fonts", "weights": [400, 500, 700] },
    "scale": { "ratio": 1.25, "base_px": 16 }
  },
  "spacing": { "base_px": 4, "steps": [1, 2, 3, 4, 6, 8, 12, 16, 24] },
  "radius": { "sm": "0.125rem", "md": "0.375rem", "lg": "0.75rem", "full": "9999px" },
  "shadow": {
    "sm": "0 1px 2px 0 oklch(0% 0 0 / 0.04)",
    "md": "0 4px 12px -2px oklch(0% 0 0 / 0.08)",
    "lg": "0 16px 40px -8px oklch(0% 0 0 / 0.14)"
  },
  "motion": {
    "duration": { "fast": "120ms", "base": "200ms", "slow": "320ms" },
    "easing": { "standard": "cubic-bezier(0.2, 0, 0, 1)", "spring": "linear(0, 0.4, 0.9, 1.02, 1)" }
  },
  "voice": {
    "lang": "ja",
    "register": "敬体",
    "button_form": "終止形。サ変は「する」を省く",
    "katakana_choon": "jtf",
    "case": null,
    "terms": { "サインイン": "ログイン", "消去": "削除" },
    "allow": []
  }
}
```

## Fields

### meta

| Field | Required | Value |
|---|---|---|
| `name` | yes | non-empty string |
| `surface` | yes | `saas` or `lp` |
| `reference` | yes | name of the product being referenced, or `null` |
| `stack.renderer` | yes | `vite-react` / `astro-react` / `next-react` / `html` / `server-templates` |
| `stack.tailwind` | yes | `"4"`. Version 3 is out of scope for this skill |
| `stack.base` | yes | `base-ui` / `radix` / `react-aria` / `smarthr-ui`, or `null` when `stack.renderer` is `html` or `server-templates` |
| `defaults_applied` | yes | array of strings recording what Step 0 settled by default instead of asking. May be empty |

`stack-defaults.md` holds the permitted pairings of `surface` and `stack.renderer`.

### color and color_dark

`color` is required and carries these nine keys, plus the optional `surface`: `background`, `foreground`, `primary`, `primary_foreground`, `muted`, `muted_foreground`, `border`, `destructive`, `accent`.

`surface` is an optional tenth key: the ground a panel, card or table sits on, where that differs from the page ground. Declare it when the page ground is tinted and the panels are not — a SaaS screen usually works this way, and SmartHR is the case that made the key necessary. Leave it out when panels sit directly on `background`, as they do on DADS. `foreground` reads on both, so there is no `surface_foreground`; add one only if a project turns up where the text colour genuinely differs.

`color_dark` is optional. When present, its keys must be a subset of `color`'s — write only the colours that dark mode overrides.

Every value is written in `oklch(...)` notation. OKLCH has been available in all major browsers since May 2023, and holds hue and chroma steady as lightness moves. A hex or `rgb()` value is an error.

The key count of `color` stays at twelve or fewer; past that, T9 warns. A palette with no dominant colour, every hue given equal weight, is one of the things that makes a generated screen read as unconsidered.

#### Deriving the colours

Contrast is not earned by muddying a colour. A brand blue pulled down to L 40% and C 0.08 "so the white text passes" is a different, duller colour, and the screen that results reads as nobody's. The rules below keep the brand value intact and move something else instead.

1. **Hue comes from the brand or the reference.** The neutrals — `background`, `muted`, `border`, `muted_foreground` — share that hue at chroma ≤ 0.012, so the page ground belongs to the same product as the buttons. Pure grey (`0 0`) is a choice only when the reference makes it, as DADS does.
2. **Chroma of `primary`, `accent` and `destructive` is never lowered to earn contrast.** When a pairing fails, move the lightness of the *other* side — a lighter ground under a mid-tone primary, a darker `foreground` on a tinted background — or change which colour carries the text.
3. **A light primary or accent (L above 65%) takes `foreground` as its text, not `primary_foreground`.** SmartHR's brand colour and the DADS accent yellow both work this way; `references/dads.md` and `references/smarthr.md` each record the case. Text colour follows the ground it sits on, not the name of the token.
4. **`destructive` keeps its chroma even beside a quiet palette.** A desaturated red is the one place where dullness costs the reader a warning.
5. **Derive with the tools that already hold the arithmetic.** `interfaces:better-colors` handles OKLCH gamut limits and the pairing of a hue across lightness steps; `scripts/lookup/search.py` (`references/lookup.md`) supplies candidate palettes and font pairings when the brand names none. Step 1 routes to both before writing a value by hand.

The rendered check of a pairing stays with Step 5, as the last section of this file says.

### typography

Exactly two families: `display` and `body`. A third is an error. Using one face for both is allowed — write the same `family` in both slots.

A `family` matching any of `Inter`, `Roboto`, `Open Sans`, `Lato`, `Arial`, `Helvetica`, `system-ui`, `-apple-system`, `Space Grotesk`, `Poppins`, `Montserrat` is an error. These are what a model reaches for when no choice has been made, so their presence marks the absence of a decision. To use one deliberately, keep it out of `tokens.json`, record the reason in `defaults_applied`, and set it in the implementation directly.

It falls to a warning when `meta.reference` names a product, because a reference system settles the family upstream and the value was then copied from that system. `smarthr-ui` ships `system-ui` as its font family, which is the case this covers; `references/smarthr.md` records it. The warning still stands, so `defaults_applied` carries the reason.

`scale.ratio` falls between 1.067 and 1.618. `scale.base_px` falls between 16 and 18: 16px is the standard body size and 14px the minimum for running text and UI text (`references/ban-list.md`), so a scale whose base sits below 16 has nowhere to put its small step.

### spacing

`base_px` is 4 or 8. `steps` is an ascending array of integers with at least five entries.

### radius

At least three steps: `sm`, `md`, `lg`. All three carrying the same value is an error — a single radius across a whole screen flattens the weight differences that tell a reader which element matters.

`full` (`9999px`) does not count toward the step total.

### shadow

At least three steps: `sm`, `md`, `lg`. Identical alpha across every step is a warning.

### motion

`duration` carries `fast`, `base` and `slow`, each a string in milliseconds. A `base` outside 120–400ms is a warning. `easing` requires `standard`.

### voice

The wording the interface uses, settled before any string is written, for the same reason the colours are. `references/ui-copy.md` holds the rules these fields feed, and `scripts/check_copy.py` reads them.

| Field | Required | Value |
|---|---|---|
| `lang` | yes | `ja` or `en` |
| `register` | when `lang` is `ja` | `敬体` or `常体` |
| `case` | when `lang` is `en` | `sentence` or `title`. Write `null` for a Japanese interface |
| `button_form` | no | a sentence recording the shape a button label takes. The default is 「終止形。サ変は「する」を省く」 |
| `katakana_choon` | no | `jtf` or `wordrabbit`. Defaults to `jtf` |
| `terms` | yes | an object mapping a word to stop using to the word this product uses. May be empty |
| `allow` | no | words and labels that the checks skip |

`terms` is the copy equivalent of the colour set: the project settles the word, and check C10 asks whether the implementation used it. Settle one entry for each operation the screens offer that has competing words (`references/ui-copy.md`, The operation vocabulary). A product whose business genuinely says 「サインイン」 leaves that word out of `terms`.

`katakana_choon` is a project setting because the Japanese authorities disagree. The JTF style guide keeps the 長音 on every word. wordrabbit drops it from a word of five characters or more, counted with the 長音, so 「ブラウザー」 becomes 「ブラウザ」 and 「ユーザー」 keeps its 長音. Check C9 asks whether the project is consistent with itself, and its message names the form the setting implies.

Sentence case versus title case is a field for the same reason: Polaris, GOV.UK, Material 3, Atlassian and Carbon all mandate sentence case; Mailchimp uses title case for global navigation; Apple declines to choose and asks only for consistency.

## Validation rules

`scripts/validate_tokens.py` checks these mechanically. An error means the token set does not hold together; a warning means it holds but departs from what this skill recommends.

| ID | Kind | Check |
|---|---|---|
| T1 | error | a required field is missing, or holds a value outside what the Fields section allows: `meta.name` empty, `meta.surface`, `stack.base`, `typography.scale.base_px`, `spacing.base_px` or a `motion.duration` value out of range, `defaults_applied` not an array, `spacing.steps` short or out of order, a missing `shadow` step |
| T2 | error | a `color` or `color_dark` value is not in `oklch(...)` notation |
| T3 | error | a `color_dark` key has no counterpart in `color` |
| T4 | error | three or more typography families |
| T5 | error | a typography family appears on the forbidden list. A warning when `meta.reference` is set |
| T6 | error | a missing `sm`, `md` or `lg` radius step, or all three identical |
| T7 | error | `stack.tailwind` is not `"4"` |
| T8 | error | the `surface` and `stack.renderer` pairing is absent from the table in `stack-defaults.md`. A warning for the pairings that table marks as warned — an existing project the skill did not choose the stack for |
| T9 | warning | more than twelve `color` keys |
| T10 | warning | identical alpha across every shadow step |
| T11 | warning | `motion.duration.base` outside 120–400ms |
| T12 | warning | `scale.ratio` outside 1.067–1.618 |
| T13 | error | `voice` is missing, `lang` is neither `ja` nor `en`, `terms` is missing or not an object, or `allow` is present and not an array |
| T14 | error | `lang` is `ja` and `register` is neither `敬体` nor `常体` |
| T15 | error | `lang` is `en` and `case` is neither `sentence` nor `title` |
| T16 | error | a `terms` entry maps a word to itself, or to a word that is itself a key |
| T17 | warning | `terms` is empty while `lang` is `ja` |

Contrast ratio is deliberately absent. It can be approximated from OKLCH lightness, but what a pairing actually looks like depends on the rendered result, so Step 5 — the independent review through `review-design-lead` — judges it against the running page.
