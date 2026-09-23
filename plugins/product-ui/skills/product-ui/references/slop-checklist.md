# Slop checks

This file is the source of record for checks S1 through S10. `scripts/check_slop.py` implements the rules written here; change this file first when a check or a threshold changes.

## What is actually being judged

"Does this look AI-generated" is a judgement no script can make and no two reviewers make the same way. The checks target what a script can settle.

A script can check two things:

1. **Does a value appear that the token set does not contain** — `tokens.json` and `theme.css` hold the answer, so a diff decides it
2. **Is an implementation missing** — form validation and error states are either present or absent

The remaining checks (S5 through S9) claim no more than a tendency, so all of them are warnings. Only S1–S4 and S10, where a correct answer exists, stop the pipeline.

## Scope

Files matching `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`, `.css`.

Excluded: `theme.css` and `tokens.css` (the token definitions themselves), `node_modules/`, `dist/`, `build/`, `.next/`, `out/`, `.svelte-kit/`, `.git/`, `*.min.css`, `*.test.*`, `*.spec.*`.

## Checks

### S1 — a colour outside the token set (error)

**Check.** Find hex literals (`#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`), `rgb()`, `rgba()`, `hsl()` and `hsla()`. A value written anywhere in the theme file passes: the `theme.css` or `tokens.css` found beneath the paths or up to four directories above them, or the file `--theme` names. With no theme file, every literal is reported.

**Allowed.** CSS and JS comments. Fragment references such as `href="#..."` and `id="#..."`. SVG `currentColor`. `transparent` and `inherit`.

**Why.** A model that has the tokens still writes hex literals. Checking whether the tokens were used is what closes the loop.

### S2 — a font reached for by default (error)

**Check.** Look in `font-family` declarations and Tailwind `font-[...]` arbitrary values for `Inter`, `Roboto`, `Open Sans`, `Lato`, `Arial`, `Helvetica`, `system-ui`, `-apple-system`, `Space Grotesk`, `Poppins` or `Montserrat`.

**Allowed.** Any position after the first in a fallback list — `"Public Sans", system-ui, sans-serif` passes. Only the leading family raises an error.

**Why.** Anthropic's prompting cookbook, [Prompting for frontend aesthetics](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb) (as of September 2026), carries both the ban and its limit: "**Never use:** Inter, Roboto, Open Sans, Lato, default system fonts" and "You still tend to converge on common choices (Space Grotesk, for example) across generations." A written ban leaves the convergence in place, so the ban becomes a check.

### S3 — a blue-to-purple gradient (error)

**Check.** In `linear-gradient`, `radial-gradient` and `conic-gradient` arguments, and in Tailwind `from-*`, `via-*` and `to-*` classes, find a blue family (blue, indigo, sky, cyan) and a purple family (purple, violet, fuchsia) appearing together. For raw OKLCH and hex values, decide it on whether two or more stops fall in the 240–300 degree hue range.

**Why.** A blue-to-purple gradient is the default accent of generated interfaces, and it marks a colour nobody chose.

### S4 — three or more font families (error)

**Check.** Across the whole scope, count the distinct families appearing in leading position. Three or more raises an error.

**Allowed.** Monospace families (`ui-monospace`, `Menlo`, `Consolas`, `Fira Code` and the like) do not count — code blocks need one.

**Why.** Two families — one for display, one for body — give every hierarchy a screen needs. A third family adds a voice without adding a level.

### S5 — more than five colours outside the token set (warning)

**Check.** Count the distinct values S1 found. More than five raises a warning.

**Why.** A palette past five colours stops carrying meaning: the reader can no longer tell which colour signals what. It counts the colours S1 found, including those silenced with `ignore S1`, so it catches colours accumulating through suppressions while each S1 error stops the pipeline on its own.

### S6 — a single radius everywhere (warning)

**Check.** Collect `border-radius` values and Tailwind `rounded-*` classes. Excluding `0`, `0px`, `none`, `9999px`, `full` and `50%`, a warning fires when exactly one distinct value remains and it appears in five or more places.

**Why.** Identical padding, radius and card height across a whole screen is a recurring observation about generated interfaces — the absence of any weight difference. The five-occurrence floor keeps small surfaces, where one radius is correct, out of it.

**On the threshold.** One radius across a surface can be a deliberate choice, so this check stays a warning. A project where it fires on a deliberate single radius silences it with `ignore-file S6` and the reason.

### S7 — one alpha across every shadow (warning)

**Check.** Collect the alpha values inside `box-shadow` colours. A warning fires when exactly one distinct value remains, it falls between 0.05 and 0.15, and it appears in three or more places.

**Why.** The same observations name one shadow near 0.1 alpha on every card. Bounding it to 0.05–0.15 avoids catching a deliberately heavy or deliberately faint shadow applied consistently.

**On the threshold.** Same caution as S6.

### S8 — emoji standing in for icons (warning)

**Check.** Find elements whose entire content is emoji, and `<li>`, `<button>` and `<a>` whose direct text begins with an emoji.

**Allowed.** Emoji inside the running text of a paragraph or heading. Any line carrying `aria-hidden` is skipped whole.

**Why.** Emoji used as iconography is a listed tell. It marks a skipped decision about which icon set to use.

### S9 — em-dashes piling up (warning)

**Check.** Count `—` (U+2014) in visible text. Three or more in one file raises a warning.

**Allowed.** Comments, the contents of `<code>` and `<pre>`, and attribute values.

**Why.** Repeatedly named as a trace of generated prose. The Japanese full-width dash `―` (U+2015) is out of scope.

### S10 — a form with no state design (error)

**Check.** On finding a `<form>` element, or `useForm`, `react-hook-form`, `Formik` or `zodResolver` in the file, look for at least one of, anywhere in the file: the word `required`, `aria-required`, `aria-invalid`, `aria-describedby`, a `pattern` attribute, or something recognisable as error display (`role="alert"`, a JSX expression reading `errors.`, `errorMessage`, `helperText` or `FormMessage`). None of them present raises an error.

**Allowed.** A file carrying `role="search"` or `type="search"`, read as a search form.

**Why.** A generated form often ships with no validation, no error states and no mark on the required fields. None of that shows in a screenshot, so a visual review misses it and a check has to find it.

## Suppressing a misfire

A misfire returns on every rerun until the reason sits where the script can read it. Two comment forms do that, and the reason is part of the syntax:

| Form | Where | Silences |
|---|---|---|
| `product-ui: ignore S8 <reason>` | the line before the finding, or the same line | that ID on that line only. For the per-line checks: S1, S2, S3, S8, S10 |
| `product-ui: ignore-file S9 <reason>` | anywhere in a scanned file | that ID for the whole file — S9 — or, for the per-run checks S4, S5, S6 and S7, for the whole run |

Comment syntax follows the file: `<!-- -->` in HTML, `/* */` in CSS, `{/* */}` in JSX. A form with no reason after the ID is reported as **S0 (warning)** and suppresses nothing, so a bare `ignore` cannot pass silently.

```html
<!-- product-ui: ignore-file S9 title separators in <title>, not prose -->
```

Suppress only a misfire — the check read the line wrong. Where it read the line correctly, fix the line. The reason states how the check misread it; that is what a later reader checks.

## Out of reach for this script

Step 5 — the independent review through `review-design-lead` — judges these against the rendered page.

- Headline copy that says nothing ("Scale without limits." and its relatives, which would suit any product)
- The reused shape of centred hero, then three equal-width cards
- Whether anything guides the eye
- Measured contrast ratios
- Interactive elements that look interactive and do nothing
