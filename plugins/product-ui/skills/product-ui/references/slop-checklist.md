# Slop checks

This file is the source of record for checks S1 through S37. `scripts/check_slop.py` implements the rules written here; change this file first when a check or a threshold changes.

## What is actually being judged

"Does this look AI-generated" is a judgement no script can make and no two reviewers make the same way. A script can settle two things:

1. **Does a value appear that the token set does not contain**: `tokens.json` and `theme.css` hold the answer, so a diff decides it
2. **Is an implementation missing**: form validation and error states are either present or absent

S1, S3, S4, S10 and S17 have a correct answer, or name a trait that harms the reader whether or not anyone suspects AI, and are errors that stop the pipeline. S11 is an error for `<Card>` inside `<Card>` and for an element with the class token `card` inside another with that token, and a warning for every other nested pair of card elements. S2, S5 through S9, S12 through S16 and S18 through S37 claim only a tendency and are warnings (S19 through S37 are ported from impeccable, pbakaus/impeccable at commit df3a4abe, Apache-2.0; each row names its rule); the hand-over rules on each warning (fix it, or keep it with a stated reason). Research rows are cited as "research T<n>" (`research/20261030-ai-tells-ui/report.md`, section 6).

## Scope

Files matching `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`, `.css`.

Excluded: `theme.css` and `tokens.css` (the token definitions themselves), `node_modules/`, `vendor/`, `dist/`, `build/`, `.next/`, `out/`, `.svelte-kit/`, `.git/`, `*.min.css`, `*.test.*`, `*.spec.*`.

## Checks

### S1: a colour outside the token set (error)

**Check.** Find hex literals (`#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`), `rgb()`, `rgba()`, `hsl()`, `hsla()`, `oklch()`, `oklab()`, `lab()` and `lch()`, including an underscore-spaced arbitrary value such as `bg-[oklch(60%_0.2_280)]`. A value written anywhere in the theme file passes: the `theme.css` or `tokens.css` found beneath the paths or up to four directories above them, or the file `--theme` names. With no theme file, every literal is reported. A colour inside an attribute selector within a class token (`[&_.recharts-cartesian-grid_line[stroke='#ccc']]:stroke-border/50`) selects elements by an attribute value and paints nothing, so it is skipped.

**Also checked: Tailwind's default palette (error).** A class `<utility>-<family>-<step>` with an optional `/<opacity>` is reported when the utility is `bg`, `text`, `border`, `ring`, `outline`, `fill`, `stroke`, `from`, `via`, `to`, `divide`, `decoration`, `placeholder`, `caret`, `accent` or `shadow`, the family is one of Tailwind's 22 (`slate`, `gray`, `zinc`, `neutral`, `stone`, `red`, `orange`, `amber`, `yellow`, `lime`, `green`, `emerald`, `teal`, `cyan`, `sky`, `blue`, `indigo`, `violet`, `purple`, `fuchsia`, `pink`, `rose`) and the step is 50–950. It passes when the theme file defines `--color-<family>-<step>`, or when a local stylesheet the theme file `@import`s defines it (a relative path, or a package path under the nearest `node_modules`, read through the package's `exports` map, as the DADS Tailwind plugin's `./v4` maps to `dist/v4.css` with `--color-yellow-300`); an import that cannot be resolved is skipped without a finding, and Tailwind's own stylesheets (`tailwindcss…`) are never read. A colour name the theme defines under its own name (`bg-primary`, `bg-brand-accent`) is not a palette class. Why: the default blue-600 is what ships when no colour was chosen (research T20).

**Allowed.** CSS and JS comments. Fragments inside a URL, such as `href="#..."`, `href="/docs#..."` and `url(#...)`, and `id="#..."`. Achromatic shadow colours `oklch(0% 0 0 / a)` and `oklch(100% 0 0 / a)`. SVG `currentColor`. `transparent` and `inherit`.

**Why.** A model that has the tokens still writes hex literals; this check closes the loop.

### S2: a font reached for by default (warning)

**Check.** Look in `font-family` declarations (the property name as a whole, so `--e-global-typography-primary-font-family` is no declaration; `@font-face` blocks declare a face and are skipped) and Tailwind `font-[...]` arbitrary values for `Space Grotesk`, `Poppins`, `Montserrat`, `Geist` or `Geist Sans` (the same list as T5 in `validate_tokens.py`). Names are compared lower-cased with quotes removed.

**Allowed.** Any position after the first in a fallback list: `"Public Sans", system-ui, sans-serif` passes. Only the leading family raises a warning. `Inter`, `Roboto`, `Open Sans`, `Lato`, `Arial`, `Helvetica`, `system-ui` and `-apple-system` are not on the list.

**Why.** Anthropic's prompting cookbook, [Prompting for frontend aesthetics](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb) (as of September 2026), carries both the ban and its limit: "**Never use:** Inter, Roboto, Open Sans, Lato, default system fonts" and "You still tend to converge on common choices (Space Grotesk, for example) across generations." A written ban leaves the convergence in place, so the ban becomes a check. About a fifth of real screens (19.3%, 37 of 192) lead their dominant text with `Inter`, `Roboto`, `Open Sans`, `Lato`, `Arial`, `Helvetica`, `system-ui` or `-apple-system` by exact name, and 28.1% (54 of 192) when vendored Inter and Geist names and Tailwind's system stack count, so those names are ordinary practice. `Space Grotesk`, `Poppins`, `Montserrat`, `Geist` and `Geist Sans` lead the body text on 5 of 192 screens, all Vercel's own pages or Wantedly. Calibrated on `research/20261106-real-screens`.

**On the threshold.** A tendency, so a warning. `Inter` is outside the list, so a project that sets it on purpose passes.

### S3: a blue-to-purple gradient (error)

**Check.** In `linear-gradient`, `radial-gradient` and `conic-gradient` arguments, and in Tailwind `from-*`, `via-*` and `to-*` classes, find a purple family (purple, violet, fuchsia) together with a blue family (blue, indigo, sky, cyan) or a pink family (pink, rose) on one element. Each gradient call is read to its own closing parenthesis, so the words and values of other elements are no part of it. For raw OKLCH and hex values, it fires when one stop's OKLCH hue falls in 286–330° (the purple band) and another's in 200–286° (the blue band) or in 330–360° and 0–10° (the pink band); hex is converted to OKLCH first, and a stop with chroma below 0.12 has no hue and is skipped, so a pastel tint such as `#b2d5ff` to `#dfd1ff` passes. In a markup file, a `<style>` rule whose class selectors match no class attribute of the file styles nothing and is skipped. Tailwind classes on one element also fire when a `from-purple-*`, `from-violet-*` or `from-indigo-*` stop meets a `to-*` stop in purple, violet, indigo, blue, cyan, pink or fuchsia, so a purple-only gradient reports too (impeccable `ai-color-palette`, `TW_FROM_PURPLE` with `TW_TO_PURPLE`).

**Why.** A purple gradient running to blue or pink is the default accent of generated interfaces (research T1: `#7c3aed` to `#ec4899`), and it marks a colour nobody chose. Real screens that pair blue and purple ship them in brand gradients that style nothing visible (WordPress preset classes and bundle rules no element uses, a closed mega menu) or in user-chosen colours. A saturated gradient, both stops at OKLCH chroma 0.12 or more, shows in product-owned UI on 0 of 192 screens, and the one visible blue-to-purple case is a pastel card (chroma 0.070 and 0.064), 1 of 192. Calibrated on `research/20261106-real-screens`.

### S4: three or more font families (error)

**Check.** Across the whole scope, count the distinct families appearing in leading position, in `font-family` declarations (matched as S2 matches them, outside `@font-face` blocks) and in Tailwind `font-[...]` arbitrary values that name a family (a numeric value such as `font-[600]` sets the weight and is skipped). Names are lower-cased, with quotes, `!important` and a trailing ` fallback` removed. Three or more raises an error.

**Allowed.** These names do not count:

- CSS generic and system keywords: `serif`, `sans-serif`, `monospace`, `cursive`, `fantasy`, `math`, `emoji`, `fangsong`, `system-ui`, `ui-sans-serif`, `ui-serif`, `ui-monospace`, `ui-rounded`, `-apple-system`, `BlinkMacSystemFont`, `var(…)`, `inherit`, `initial`, `unset`, `revert`, `null`, `caption`, `icon`, `menu`, `message-box`, `small-caption`, `status-bar`;
- monospace families (`Menlo`, `Consolas`, `Fira Code` and the like); code blocks need one;
- icon faces: a name containing `icon`, `symbol`, `awesome`, `material` or `glyph`;
- CJK and script faces: a name with `jp`, `sc`, `tc`, `kr` or `cjk` as a separate word, or containing `hiragino`, `meiryo`, `メイリオ`, `yu gothic`, `游`, `ゴシック`, `明朝`, `mincho`, `biz ud`, `yakuhan` or `ms pgothic`.

**Why.** Two families, one for display and one for body, give every hierarchy a screen needs. A third adds a voice without adding a level. The names left out belong to a type system that real screens ship in several parts: a fallback face per script, an icon font, the OS keyword. Counted that way, 3 or more families lead the text on about 2% of real screens (4 to 7 of 192, by how weights of one family merge), and on none once system keywords and CJK faces are left out. Calibrated on `research/20261106-real-screens`.

### S5: more than five colours outside the token set (warning)

**Check.** Count the distinct values S1 found, including those silenced with `ignore S1`. More than five raises a warning.

**Why.** Past five colours a palette stops carrying meaning: the reader can no longer tell which colour signals what. Counting suppressed values catches colours accumulating one suppression at a time.

### S6: a single radius everywhere (warning)

**Check.** Collect `border-radius` values and Tailwind `rounded-*` classes. Excluding `0`, `0px`, `none`, `9999px`, `full` and `50%`, a warning fires when exactly one distinct value remains and it appears in five or more places.

**Why.** Identical padding, radius and card height across a whole screen, with no weight difference anywhere, is a recurring observation about generated interfaces. The five-occurrence floor keeps small surfaces, where one radius is correct, out of it.

**On the threshold.** One radius across a surface can be a deliberate choice, so this stays a warning. A project where it fires on a deliberate single radius silences it with `ignore-file S6` and the reason.

### S7: one alpha across every shadow (warning)

**Check.** Collect the alpha values inside `box-shadow` colours: the part after `/`, or the fourth comma-separated part, with `%` read as a fraction (`10%` is 0.1) and the number compared as a number (`.1` and `0.10` are one value). A colour with no alpha written is skipped. A warning fires when exactly one distinct value remains, it falls between 0.05 and 0.15, and it appears in three or more places.

**Why.** The same observations name one shadow near 0.1 alpha on every card. The 0.05–0.15 bound lets a deliberately heavy or deliberately faint shadow, applied consistently, pass.

**On the threshold.** As for S6: a warning, silenced with `ignore-file S7` and the reason where the single alpha is deliberate.

### S8: emoji standing in for icons (warning)

**Check.** Find elements whose entire content is emoji (`<tag …>emoji</tag>`, with the same tag closing it), and `<li>`, `<button>`, `<a>` and headings (`<h1>`–`<h6>`) whose direct text begins with an emoji. An emoji is one of:

- a code point in U+1F300–1FAFF or U+1F1E6–1F1FF (pictographs, flags);
- a BMP code point with Emoji_Presentation=Yes (U+231A–231B, 23E9–23EC, 23F0, 23F3, 25FD–25FE, 2614–2615, 2648–2653, 267F, 2693, 26A1, 26AA–26AB, 26BD–26BE, 26C4–26C5, 26CE, 26D4, 26EA, 26F2–26F3, 26F5, 26FA, 26FD, 2705, 270A–270B, 2728, 274C, 274E, 2753–2755, 2757, 2795–2797, 27B0, 27BF, 2B1B–2B1C, 2B50, 2B55);
- any symbol followed by U+FE0F, keycap sequences included.

**Allowed.** Arrows, `★`, `☆`, `✔`, `✕` and the other text-presentation symbols without U+FE0F: they render as monochrome glyphs. Text between two elements (`</a> ♥️ <a`) is no element's whole content. Emoji inside the running text of a paragraph or heading. A match on a line carrying `aria-hidden` is skipped; a match that spans several lines is skipped when any of them carries it. Line breaks inside the element do not hide the emoji, and an emoji sequence joined with U+200D (👨‍💻) counts as one emoji.

**Why.** Emoji used as iconography is a listed tell. It marks a skipped decision about which icon set to use. Real screens use an emoji where it is the content (reactions, user-chosen avatars, message categories) and use SVG or text glyphs in chrome (★ ratings, ✔ checks, ← → pagers, ✕ close buttons); 87% of the 373 findings on text-presentation symbols were such glyphs. A pictographic emoji in place of a nav or button icon appears on 2 of 192 screens, and in a product's own chrome on 6 of 192 (3.1%). Calibrated on `research/20261106-real-screens`.

### S9: em-dashes piling up (warning)

**Check.** Count `—` (U+2014) in visible text. Three or more in one file raises a warning. The Japanese full-width dash `―` (U+2015) is out of scope.

**Allowed.** Comments, the contents of `<code>`, `<pre>`, `<script>` and `<style>`, and attribute values. In `.jsx` and `.tsx`, a string literal outside a tag counts as visible text.

**Why.** Repeatedly named as a trace of generated prose.

### S10: a form with no state design (error)

**Check.** The check runs on a `<form>` element that holds an entry field, and on a file that uses `useForm`, `react-hook-form`, `Formik` or `zodResolver`. An entry field is an `<input>` of type `email`, `password`, `tel`, `url` or `file`, or a `<textarea>`. Look anywhere in the file for at least one of:

- the word `required`, `aria-required`, `aria-invalid`, `aria-describedby`, or a `pattern` attribute;
- something recognisable as error display: `role="alert"`, or a JSX expression reading `errors.`, `errorMessage`, `helperText` or `FormMessage`.

None of them present raises an error.

**Allowed.** A form that meets any of these:

- its tag carries `role="search"`, or its `action`, `id` or `class` contains `search`, `filter`, `sort`, `lookup` or `track`;
- it holds an input of `type="search"`, or an input named `q`, `query`, `keyword`, `kw` or `search`;
- it holds only text, number, select, button and hidden inputs, as a Rails `button_to` or an OAuth button does;
- its one visible field is an `email` input, a single-field subscription.

**Why.** A generated form often ships with no validation, no error states and no mark on the required fields. None of that shows in a screenshot, so a visual review misses it and a check has to find it. Of 124 real screens that contain a `<form>`, most forms are site search (including POST searches on Japanese portals), faceted filters, sort selects, tracking-number lookups and button-only forms: 32 of the 34 screens with a form and no state markup carry only forms of these kinds. A visible data-entry form with no required, `aria-invalid`, `aria-describedby`, `pattern` or alert markup appears on about 1% of screens (1 to 2 of 192). Calibrated on `research/20261106-real-screens`.

### S11: a card inside a card (error for the exact forms, warning for the rest)

**Check.** In markup files (`.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.astro`), keep a stack of the open tags: push each opening tag, pop at its closing tag, skip self-closing tags (`/>`) and the HTML void elements (`img`, `br`, `hr`, `input`, `meta`, `link`, `source`, `track`, `wbr`, `area`, `base`, `col`, `embed`, `param`). A *card element* is an opening tag that is either:

- the JSX component `<Card` exactly (`<CardContent`, `<CardHeader`, `<CardTitle`, `<CardFooter` and `<CardDescription` are other components), or
- any element whose `class` or `className` attribute holds a token equal to `card` or `panel`, or ending in `-card`, `_card`, `-panel` or `_panel`. `stat-card` and `kpi_panel` count; `card-title`, `card-body` and `panel-heading` do not. Tokens are split on whitespace, and a JSX `className={...}` expression is read for its string literals only. A token holding `--` (a BEM modifier such as `card__image--aspect-card`) is no card, nor is one whose stem before the suffix ends in `tab`, `tabs`, `dropdown`, `menu`, `nav`, `popover`, `tooltip`, `flyout` or `drawer` (`tab-panel`, `gl-new-dropdown-panel`). An element with `role="tabpanel"`, `hidden` or `aria-hidden="true"`, and every element inside it, is no card.

The finding is reported at the line of a card element that opens while another card element in the same file is still open. It is an error when `<Card>` opens inside `<Card>`, or an element with the exact class token `card` opens inside another with the exact token `card`. Every other nested pair of card elements (a suffix form such as `stat-card` or `panel`) is a warning. Comments and the contents of `<script>`, `<style>` and `<pre>` are skipped, as for the other checks.

**Allowed.** shadcn's `CardContent`, `CardHeader` and the like inside `Card`. Sibling cards. A `card-title` or `card-body` class inside a card. A card inside a `<dialog>` or an element with `role="dialog"`: a dialog is its own surface, so the search for an enclosing card stops there.

**Why.** An enclosure is a strong grouping cue, so a box inside a box asserts a second relation that the reader has to resolve, and it adds padding, border and shadow around the same content. The SmartHR Design System's [Base component](https://smarthr.design/products/components/base/) says so of its own container: 「Baseの上にBaseを重ねることもレイヤー順序を把握しづらくさせます」. Nielsen Norman Group's [The Principle of Common Region](https://www.nngroup.com/articles/common-region/) describes the boundary around a set of elements as the cue that makes them read as one group, which is why a second boundary inside the first reads as a second group. Markup cannot show whether a wrapper named `card` draws a box, or whether a responsive twin is hidden, so the suffix forms are warnings and the rendered check R12 judges what is drawn. The exact forms (`<Card>` in `<Card>`, `card` in `card`) appear in 1 of 192 real screens' markup and in none rendered; a visible box inset inside another box appears on about 15% to 19% of real screens. Calibrated on `research/20261106-real-screens`.

### S12: gradient text (warning)

**Check.** One element carrying both `bg-clip-text` and `text-transparent`, or a declaration `background-clip: text` or `-webkit-background-clip: text`.

**Allowed.** `text-transparent` or `bg-clip-text` alone, and `background-clip: padding-box` and the like.

**Why.** Gradient headline text is the first named tell of generated pages (research T2). A plain colour from the token set carries the same emphasis.

### S13: glass (warning)

**Check.** A `backdrop-blur-*` class, or a `backdrop-filter: blur(...)` declaration (also `-webkit-backdrop-filter`; one finding per line).

**Allowed.** A full-viewport overlay: `fixed inset-0` on the same element, a component whose name ends in `Overlay`, or a rule that sets `position: fixed` with `inset: 0` or whose selector names an overlay.

**Why.** A blurred translucent panel over a decorative backdrop is the glassmorphism default (research T7). A scrim behind a dialog has a function and stays.

### S14: motion defaults (warning)

**Check.** The same entrance animation on three or more elements of one file: the same `animate-*` class; the same `data-aos` value; `whileInView`; or a motion `initial` that sets `opacity: 0`. An `animate-*` class counts when its token has no variant prefix (no `:` before `animate-`), its name does not start with `spin`, `ping`, `pulse`, `bounce`, `marquee` or `none`, and an arbitrary `animate-[…]` value does not contain `infinite`.

**Allowed.** `transition-all` and `transition: all`. Named transition properties (`transition-colors`, `transition: opacity .2s`). Two elements sharing an entrance animation. Different animations on different elements. Animations behind a variant (`data-[motion^=from-]:animate-fade-in`), spinners, pulses and marquees, which mark a state or a loop.

**Why.** Everything fading up on scroll is a motion default (research T8). Motion that marks a state change tells the reader something. `transition: all` is ordinary production CSS: 16.7% of real screens (32 of 192) declare it on their own elements in inline CSS alone, as `transition-all duration-150` on inputs, buttons and nav or as `transition: all .2s` on buttons and links. One entrance animation on three or more elements appears on 0 of 192 screens. Calibrated on `research/20261106-real-screens`.

### S15: template chrome (warning)

**Check.** Three signs, each reported on its own:

- two or more elements in one file that are uppercase, track 0.05em or more and are followed by an `<h1>`, `<h2>` or `<h3>` as the next element sibling (the small spaced eyebrow). Uppercase is the class `uppercase`, `text-transform: uppercase` in the element's `style`, or a rule of the file whose class selector the element carries. Tracking of 0.05em or more is `tracking-wider`, `tracking-widest`, `tracking-[Nem]` with N of 0.05 or more, `tracking-[Npx]` with N of 0.05 times the element's font size (16px when it sets none) or more, or a `letter-spacing` of 0.05em or more from the same sources;
- link or button text (`<a>`, `<button>`, `<Link>`, `<Button>`) ending in `→`, `↗`, `›`, `»` or `->`;
- a text node joining three or more parts with ` · `.

**Allowed.** `uppercase` without tracking. Spaced uppercase labels that no heading follows: footer and navigation group labels, badges. An arrow in a paragraph. A skip link (`href` starting with `#` and text starting with `Skip`) and a link with an `sr-only` or `visually-hidden` class. Two parts joined by a middle dot. Middle dots in `<title>`, `<head>`, `<script>`, `<style>` and attribute values.

**Why.** The eyebrow label, the arrow after every call to action and the dot-joined meta line are template chrome (research T9). The label alone names the action. Small spaced uppercase labels are routine on real screens (2 or more visible on 12.0%), as footer and navigation group headings and as badges; an eyebrow directly above a heading appears on 1.6% to 3.6%, link text ending in an arrow on 2.6% once skip links are set aside, and a dot-joined meta line on 0.5%. Calibrated on `research/20261106-real-screens`.

### S16: missing states (warning)

**Check.** In markup files, one finding per file and per missing state:

- the file renders a collection (`.map(` whose callback returns an element) and has no empty branch: `.length === 0`, `!x.length`, `.length ?`, `isEmpty` or an `Empty…` component;
- the file fetches (`fetch(`, `useQuery`, `useSWR`, `axios`) and has no loading branch (`loading`, `sending`, `submitting`, `saving`, `pending`, `isLoading`, `isPending`, `isSubmitting`, `isFetching`, `Skeleton`, `Spinner`, `Suspense`) or no error branch (`error`, `isError`, `ErrorBoundary`, `catch`).

The words match as whole identifiers in code. Comments, `import` statements, string contents (a CSS class `"error"`, `loading="lazy"`) and CSS-module members (`styles.error`) do not count.

**Allowed.** A `.map(` whose receiver is an identifier bound in the same file to an array literal with `const` (`const KINDS = [...]`): a fixed list of options, kinds or channels is never empty. A file that renders its state in a sibling component: silence it with `ignore-file S16` and name that component. A collection that is never empty (the items of an order, rows passed in as a fixed list) takes `ignore S16` with that reason, as the brief's States section records it.

**Why.** A screen with no empty, loading or error state fails the reader the first time the data is late or absent, whatever made it (research T26). The brief's States section lists them; this check finds the files that skipped it.

### S17: a toast-only action (error)

**Check.** An `onClick`, `onSelect` or `onSubmit` handler whose whole body is one `toast(...)`, `toast.<name>(...)` or `alert(...)` call, written inline in the attribute.

**Allowed.** A handler that does anything else as well: a state change, a request, `preventDefault()`. A handler passed by name.

**Why.** The control reports an effect it does not have, and the reader believes the work is done (research T27). Do the work, show the control disabled, or leave it out.

### S18: a pulsing New or Live badge (warning)

**Check.** An element carrying `animate-pulse` or `animate-ping` whose whole text is `New` or `Live` (any case) or 「新着」, with the closing tag straight after it. The scan reads the text that follows the opening tag as well as its attributes. A pulsing element with other text or none, and `animate-spin` or `animate-bounce`, pass this form (a small empty round pulsing element falls under the second form below).

**Allowed.** `ignore S18` with the reason, where the thing really is live and the badge names what is live.

**Why.** Noqta lists the pulsing "Live" or "New" pill copied onto features that are neither as an overused AI UI pattern (research E103 (ui-defaults), grade C), hence a warning. A status badge names the progress or the action asked of the reader (`references/ui-copy.md`, Status labels).

**Second form: a pulsing dot.** impeccable's `pulsing-dot` (`scan_css_text_for_pulsing_dot` in `crates/core/src/checks/css_scan.rs`, pbakaus/impeccable at df3a4abe, Apache-2.0). Two forms, each reported on its own:

- a CSS rule with an `animation` that runs `infinite` (or `animation-name` with `animation-iteration-count: infinite`), whose keyframes pulse, or whose name holds `pulse`, `blink` or `ping` when the file defines no such keyframes; with a `width` and `height` of 2 to 16px each, the longer side at most 1.5 times the shorter, and a `border-radius` of at least 40% (or `999px`, or 0.4 of the shorter side). Keyframes pulse as impeccable's `collect_pulse_keyframes` reads them: they declare `opacity` or `box-shadow`, or a `transform` scale at any factor on more than one axis (all `scaleX` or all `scaleY` is a bar that fills or an eye that blinks), and they neither move nor resize the box. They move it when two steps' translations, at the same percentage, differ by 4px or more (a centred ring that repeats `translate(-50%, -50%)` does not move, and a 3px bob does not either), or when an offset or margin changes by 4px or more without its opposite side. They resize it when two steps declare different `height`s at the same `width`. Rules inside `@media (prefers-reduced-motion: reduce)` are skipped. The rules of one selector merge, a comma list counts each selector, and a selector gives one finding;
- an element with `animate-ping` or `animate-pulse`, `rounded-full` and a `w-`, `h-` or `size-` class of 1 to 4 (4 to 16px), whatever it holds. When a `w-` and an `h-` class both carry a number, that number reads at 4px a step, so `h-4 w-48` is a 16 by 192px bar and passes; the 2 to 16px and 1.5 gates apply to those two sizes. A class list that repeats gives one finding.

**Allowed.** A larger box, a bar or a skeleton line (the gates above). `ignore S18` with the reason where the dot is tied to data that changes and is labelled. An element that holds a label is not exempt: impeccable's static scan has no emptiness gate.

**Difference from impeccable.** impeccable reports a dot in a `header` or `nav` as an error and finds the element by its selector; this check always warns and reads the rule's own declarations. It resolves no `var()` in `width`, `height` or `border-radius`.

### S19: an accent border on one side of a card (warning)

**Check.** impeccable's `side-tab` (`REGEX_MATCHERS` in `crates/detect/src/regex_matchers.rs`, with the card gate in `crates/detect/src/detect_text.rs` and `crates/core/src/checks/rules.rs`). A stripe, and a card it sits on.

*The stripe.* In a tag outside `blockquote`, `nav`, `pre`, `code`, `input`, `span` and `a`: `border-l-N`, `border-r-N`, `border-s-N` or `border-e-N` with N of 4 or more, or 2 or more when the tag also carries a `rounded` class other than `rounded-none`. In CSS: `border-left` or `border-right` of `Npx solid <colour>` with N of 3 or more (2 or more with a `border-radius` in the same block) and a colour that is not neutral (a neutral colour is a keyword such as `transparent`, `black`, `gray`, or a colour whose channels spread under 30; a border with no colour after `solid` is not neutral); `border-left-width` or `border-right-width` of 3px or more; `border-inline-start` or `border-inline-end` of `Npx solid` with N of 3 or more (the word `solid` is required), and `border-inline-start-width` or `border-inline-end-width` of 3px or more; and a style object `borderLeft` or `borderRight` of `Npx solid` with N of 3 or more. A line holding `<blockquote`, `<nav`, `<pre`, `<code`, `<a`, `<input` or `<span` is skipped for the CSS forms.

*The card.* The stripe counts only when its box is rounded 4px or more on both corners away from it (the two corners the stripe does not touch; `border-radius: 8px 0 0 8px` under a left rule is square, `0 12px 12px 0` is rounded). A box with no radius, or `border-radius: 0`, is square. A corner that cannot be read (`var()`, a theme token) counts as rounded, so the finding stays. The corners come from the tag's `rounded-*` classes (`rounded` and `rounded-sm` read 4px, `rounded-xs` 2px, `rounded-md` 6px, `rounded-lg` 8px, `rounded-full` 9999px, `rounded-[Npx]` N; a side class sets its corners, a class behind a variant can only raise one) and `border-radius` in its `style`, from the declaration block of a CSS rule, and, where those leave the box square, from the other rules of the file tied to the box: a rule that shares its class with the tag (`.card` and `.card.is-active`), or one that names the same last compound. A file that imports a stylesheet, or a tag with a `css` prop or a class expression, may be rounded where the scan cannot see it, so only `rounded-none` or a literal square radius on the tag itself silences it there.

One finding for each element: a tag, or a declaration block, reports once however many stripes it holds.

**Allowed.** A neutral border, a thinner one, a square card, and the elements above. `ignore S19` with the reason.

**Why.** The thick coloured stripe on one side of a card is the most recognisable tell of generated interfaces (impeccable's rule text). A subtler accent or none carries the same grouping.

**Difference from impeccable.** The stripe-child form (a narrow empty coloured child element) and the `::before`/`::after` and inset-shadow stripes need element geometry and are left to R-checks on the rendered page, as is the exemption of a circle (an arc of a ring). A `border-l-N` class is judged without its colour, as impeccable judges it. impeccable resolves the box through a CSS index with nesting, Sass and styled-component rules; this check ties a box to the rules of its file by shared class or tag name only.

### S20: a thick accent border on a rounded element (warning)

**Check.** impeccable's `border-accent-on-rounded`. A tag with a `rounded` class (not `rounded-none`) and `border-t-N` or `border-b-N` with N of 1 or more, unless it carries `animate-spin`. In CSS: `border-top` or `border-bottom` of `Npx solid` with N of 3 or more in a block that sets a `border-radius` other than `0`, `0px` or `none`.

**Allowed.** `ignore S20` with the reason.

**Why.** The border clashes with the rounded corners (impeccable's rule text); drop the border or the radius.

### S21: bounce and elastic easing (warning)

**Check.** impeccable's `bounce-easing` (`ANIMATE_BOUNCE_RE`, `ANIMATION_BOUNCE_RE`, `CUBIC_BEZIER_RE`; `check_html_patterns` in `crates/core/src/checks/html_patterns.rs`). The class `animate-bounce`; an `animation` or `animation-name` value with a token holding `bounce`, `elastic`, `wobble`, `jiggle` or `spring`, unless the file defines that keyframes name and its steps only scale within 0 to 1, fade or ease inside their range (a loader dot that swells and shrinks); and a `cubic-bezier(x1, y1, x2, y2)` with y1 or y2 below -0.1 or above 1.1, except a custom property that no `var()` reads. The values -0.1 and 1.1 pass.

**Allowed.** `ignore S21` with the reason. S14 still lists `bounce` among the static animations that are not entrance animations; that rule is separate.

**Why.** Bounce and elastic easing feel dated; real objects decelerate smoothly, so exponential ease-out (quart, quint, expo) replaces them (impeccable's rule text).

### S22: a blinking cursor (warning)

**Check.** impeccable's `blinking-cursor` (`check_element_blinking_cursor_dom` and `keyframes_toggle_visibility_dom` in `crates/core/src/checks/element_checks.rs`), ported for the part a source scan decides. A CSS rule whose infinite animation uses keyframes that toggle visibility: a step sets `opacity` to 0.15 or less (0.16 does not) or `visibility` to `hidden`, and no step declares anything but those and `animation-timing-function`. The box is a caret, 1 to 24px wide, 6 to 48px tall and at least as tall as wide (`1x6` and `24x48` report, `1x5` and `24x49` do not), or an underscore, 1 to 6px tall and 4 to 24px wide (`4x1` and `24x6` report, `24x7` and `3x3` do not); a `border-radius` that makes it a round dot (S18's gate) passes. An element of such a class whose whole text is one cursor glyph (`_`, `|`, `▌` and the other block glyphs) reports too.

**Allowed.** A caret inside a real editable surface; `ignore S22` with the reason.

**Difference from impeccable.** impeccable measures the rendered box and checks that the cursor sits in the first 1200px and outside an editable ancestor. This check has no layout: it applies the size gate from the declarations only, and does not exempt an editable ancestor or a position below the first viewport.

**Why.** A blinking cursor in a hero simulates typing where no input exists and borrows the developer-tool look as decoration (impeccable's rule text).

### S23: an organic clip-path (warning)

**Check.** impeccable's `organic-clip-path` (`scan_css_text_for_organic_clip_path` in `crates/core/src/checks/css_scan.rs`). `clip-path: polygon(...)` with 10 or more vertices (a leading fill rule counts as one), the number of off-grid coordinates at least the vertex count (a coordinate is off-grid when it is more than 0.5 from a multiple of 25), and a shape that is neither rectilinear (every vertex shares its x or y with the next) nor a zigzag (two to four values on one axis, even steps on the other, alternating teeth); and `clip-path: path(...)` with 3 or more curve commands (`C`, `S`, `Q`, `T`, `A` in either case).

The arguments are read with balanced parentheses, so a `calc()` or `var()` vertex is one coordinate and the polygon keeps its vertex count.

**Allowed.** `circle()`, `inset()`, `ellipse()`, a polygon of fewer than 10 vertices or on the 25% grid. `ignore S23` with the reason.

**Difference from impeccable.** impeccable exempts a `path()` that draws a rounded rectangle (a squircle); this check does not read the path geometry, so a squircle with 3 or more curve commands takes `ignore S23`.

**Why.** CSS approximating a torn edge, blob or silhouette reads as the cheap version of the effect (impeccable's rule text).

### S24: a raster under a near-opaque wash (warning)

**Check.** impeccable's `buried-raster` (`scan_css_text_for_buried_raster`). A `background` or `background-image` value with a `url(...)` and a gradient, where a gradient listed before the first `url(` has every colour stop at alpha 0.9 or more (an `rgb()` or `hsl()` without alpha, a 3 or 6 digit hex, and the names white, black, ivory, beige, linen, snow and cream count as alpha 1; an `oklch()` stop is not read). A `background-blend-mode` or `mix-blend-mode` other than `normal` in the same block, and a gradient listed after the `url(`, pass. Alpha 0.9 is reported, 0.89 passes. A gradient with a `transparent` stop is a scrim, not a wash: only a wash whose stops all reach alpha 0.9 counts.

**Allowed.** A scrim that fades to `transparent`, or any stop under alpha 0.9. `ignore S24` with the reason.

**Difference from impeccable.** This is stricter than impeccable's static scan: its `scan_css_text_for_buried_raster` reads no `transparent` stop, so it reports a black-to-transparent scrim over a photograph, and this check does not. impeccable also reports a raster on an element at near-zero opacity, which needs the rendered element.

**Why.** The page shows the wash; the produced image ships as a cost with no effect (impeccable's rule text).

### S25: a hard offset shadow (warning)

**Check.** impeccable's `hard-offset-shadow` (`check_hard_offset_shadow` in `crates/core/src/checks/hard_offset_shadow.rs`; advisory there, hence a warning here). A `box-shadow` layer (also a `shadow-[...]` class, underscores as spaces) that is not `inset`, has alpha above 0.1 (0.1 passes, 0.11 reports), a blur of 0, a spread of 0 or more and an offset of 4px or more on either axis (3px passes).

**Allowed.** A deliberate neobrutalist direction; `ignore S25` with the reason.

**Why.** An unblurred displaced shadow can be an intentional direction. This is a review prompt, not evidence of generated work (impeccable's rule text).

### S26: a coloured glow shadow (warning)

**Check.** impeccable's `dark-glow` (`scan_css_text_for_glow`, `glow_is_perceptible`). A `box-shadow` or `text-shadow` layer whose colour channels spread 30 or more, with a blur over 4px, blur multiplied by alpha of 3.0 or more, and blur / 2 + spread above 0. A zero offset reports on any page; a layer with an offset reports only on a dark page, read as impeccable's `css_text_has_dark_root_bg` reads it: a `background` or `background-color` of a dark hex or `rgb()` (relative luminance under 0.1) on any selector, a `bg-gray`, `bg-slate`, `bg-zinc`, `bg-neutral` or `bg-stone` class at step 800 or 900 to 950 anywhere in the file, or a `:root`, `html` or `body` background (a `var()` resolved within the file) at relative luminance under 0.1 and alpha over 0.5. A custom property named after a background (`--color-background`) is no background. Channel spread 30 reports (29 passes), blur 5px at alpha 1 reports (4px passes).

**Allowed.** Neutral shadows. `ignore S26` with the reason.

**Why.** A coloured halo is the default "cool" look of generated interfaces (impeccable's rule text); neutral shadows carry elevation.

**Difference from impeccable.** impeccable also tests the lit area against the element's size and the lift over the surface it lands on; this check has no layout and applies the declaration floor only.

### S27: a radial halo on a dark page (warning)

**Check.** impeccable's `radial-halo` (`scan_css_text_for_radial_halo`). On a dark page (as S26, which also lists the spread, blur and alpha bounds): a `background` value without `url(` holding a non-repeating `radial-gradient(` with 2 or more colour stops, no stop with a `px` position within 24px (25px reports), a last stop at alpha 0.05 or less (`transparent` included), and a first stop at alpha 0.7 or more (0.69 passes) with channels spread 24 or more.

**Allowed.** `ignore S27` with the reason.

**Why.** The same tell as a glowing shadow, drawn with a gradient (impeccable's rule text).

### S28: a radial spotlight glow (warning)

**Check.** impeccable's `radial-spotlight-glow` (`radial_spotlight_stops`, `radial_spotlight_fits` in `crates/core/src/checks/measures.rs`). A `background` value holding a non-repeating `radial-gradient(` whose last stop is at alpha 0.05 or less, with one or two stops above alpha 0.05, each under alpha 0.45 (0.45 passes), at least one with channels spread 24 or more, and at least one of those chromatic stops reaching an effective alpha of 0.14 (the stop's alpha times the block's `opacity`; impeccable's `RADIAL_GLOW_MIN_EFFECTIVE_ALPHA`, 0.14 reports and 0.13 passes: a fainter layer is a tint of the ground). When the same block sets both `width` and `height`, the surface must reach 240 by 160px.

**Allowed.** `ignore S28` with the reason.

**Difference from impeccable.** impeccable measures the rendered surface, the contrast of the glow against it and whether it sits behind text. This check applies the size gate only where the block declares both sides, and skips the contrast and text tests.

**Why.** An accent cloud floating over the copy is a reflex decoration (impeccable's rule text).

### S29: a marquee (warning)

**Check.** impeccable's `marquee` (`scan_css_text_for_marquee`, `collect_marquee_keyframes`). A `<marquee>` element; or a rule whose infinite animation uses keyframes with a `translateX` (or `translate3d`) percentage travel of 20 or more (for several percentages the spread, for one the absolute value; 19 passes), unless the keyframes with a single percentage also scale or fade. Rules inside `prefers-reduced-motion: reduce` are skipped.

An indeterminate progress animation (a bar whose keyframes run `translateX(-100%)` to `translateX(100%)` under an infinite animation) matches as well, as it does in impeccable; `ignore S29` with the reason covers it.

**Allowed.** `ignore S29` with the reason.

**Why.** Continuously auto-scrolling content demands attention it has not earned and hides half of itself (impeccable's rule text).

### S30: a broken image (warning)

**Check.** impeccable's `broken-image` (`image_source_is_missing`). An `<img>` with no `src`, `srcset`, bound `:src` or lazy `data-src` attribute carrying a value; an empty value or `#` counts as none. A `{...spread}` or an expression value (`src={url}`) passes, and so does the shorthand `{src}` or `{srcset}` in a `.svelte` or `.astro` file and `v-bind="object"` in a `.vue` file.

**Allowed.** `ignore S30` with the reason.

**Why.** An `<img>` with an empty or placeholder source ships as a broken-image box (impeccable's rule text).

### S31: repeating-gradient stripes (warning)

**Check.** impeccable's `repeating-stripes-gradient` (`repeating_gradient_repeats` in `crates/core/src/checks/html_patterns.rs`; advisory there). A `repeating-linear-gradient`, `repeating-radial-gradient` or `repeating-conic-gradient` whose ramp does not run from 0 to the full length (`100%`, `360deg`, `1turn`, or no position): a gradient that starts at 0 and ends at the full length draws once and passes. A radial gradient with a size other than the default, a `var()` stop and an unreadable stop list count as repeating. One finding for each file.

**Allowed.** `ignore S31` with the reason.

**Why.** Repeating stripes as surface decoration are a recurring generated-interface signature (impeccable's rule text).

### S32: a grid-line background (warning)

**Check.** impeccable's `codex-grid-background` (`grid_background_hits` in `crates/core/src/checks/css_scan.rs`; advisory there). A declaration block (or `style` attribute) with 2 or more hairline layers (`1px, transparent 1px` pairs, or `transparent calc(100% - Npx)`, N up to 3 digits) in `background` or `background-image`, and a pixel cell from `background-size` or `/ Npx` in the shorthand. One hairline layer passes. One finding for each file.

**Allowed.** A real canvas, map or chart; `ignore S32` with the reason.

**Why.** A decorative grid drawn with hairline gradients is a recurring generated-interface signature (impeccable's rule text).

### S33: a font outside the theme's font tokens (warning)

**Check.** impeccable's `design-system-font` (`is_allowed_font` in `crates/detect/src/design_system.rs`), with the theme in place of `DESIGN.md`. Runs only when `theme.css` declares `--font-*` tokens. The first non-generic family of each `font-family` declaration (and `fontFamily` in a style object) must be a family named in a `--font-*` value of the theme; generic families, `var()` and interpolated stacks, and monospace faces (S4's list) pass.

**Allowed.** `ignore S33` with the reason where the face is a deliberate addition; add it to the theme in that case.

**Why.** A font the theme does not declare is drift from the type system (impeccable's rule text).

### S34: a radius outside the theme's radius tokens (warning)

**Check.** impeccable's `design-system-radius` (`is_allowed_radius_raw`; advisory there). Runs only when `theme.css` declares `--radius-*` tokens in px or rem. A `border-radius` (or `borderRadius`) token more than 0.5px from every theme radius fails (4.5px passes against a 4px token, 4.6px fails); 0.5px or less, `0`, `none`, a percentage, `var()` and `calc()` pass, and so does a value of 99px or more when the theme has a pill radius.

**Allowed.** `ignore S34` with the reason.

**Why.** A radius off the documented scale is drift (impeccable's rule text).

### S35: a font size off the theme's text ramp (warning)

**Check.** impeccable's `design-system-font-size` (`is_allowed_font_size_raw`; advisory there). Runs only when `theme.css` declares `--text-*` sizes in px or rem. A literal `font-size` in px or rem (also `fontSize` and `text-[Npx]`) more than 0.5px from every ramp size fails; for `clamp(min, preferred, max)` the first and last argument are tested. `var()`, `vw`, `em` and other units pass.

**Allowed.** `ignore S35` with the reason.

**Why.** A size off the type ramp is drift (impeccable's rule text).

### S36: letter-spacing pulled too tight (warning)

**Check.** impeccable's `extreme-negative-tracking` (`tracking_is_crushed` in `crates/core/src/checks/text_rules.rs`). A `letter-spacing` below -0.07em, or below -0.09em where the same block sets a `font-size` of 40px or more (-0.07em and -0.09em pass). A value in px or rem needs a `font-size` in the same block to convert. A `clamp(min, preferred, max)` size is judged by its larger endpoint. A `style` attribute is read as a block. A `tracking-[-Nem]` class follows the same bounds on an element with more than 20 characters of its own text (a size of 40px or more takes the display bound: `text-5xl` and larger, or `text-[40px]` and larger; `text-4xl` is 36px and does not). A markup file whose visible text is mostly CJK passes; a stylesheet carries no element text, so it takes no such exemption, and a Japanese stylesheet uses `product-ui: ignore-file S36 <reason>`.

**Allowed.** `ignore S36` with the reason.

**Why.** Tracking tighter than the point where characters keep their shapes costs legibility (impeccable's rule text).

**Difference from impeccable.** impeccable reads the computed `letter-spacing` and text of one element; this check reads the declaration and, for the CJK exemption, the text of the whole markup file.

### S37: wide tracking on body text (warning)

**Check.** impeccable's `wide-tracking` (`check_element_quality` in `crates/html/src/quality.rs`). A `letter-spacing` above 0.05em (0.05em passes) in a block without `text-transform: uppercase`. A `tracking-widest` or `tracking-[Nem]` class above 0.05em on an element whose own text is longer than 20 characters, unless the element has `uppercase`, or its text is all capitals and at most 40 characters (20 characters pass, 21 report; 40 capitals pass, 41 report). A `style` attribute is read as a block. A markup file whose visible text is mostly CJK passes; in a stylesheet the exemption does not apply, and a Japanese stylesheet uses `product-ui: ignore-file S37 <reason>`.

**Allowed.** Short uppercase labels. `ignore S37` with the reason.

**Why.** Letter spacing above 0.05em on body text disrupts the natural grouping of characters and slows reading (impeccable's rule text).

**Difference from impeccable.** A CSS rule is judged without the element text, so a spaced rule that styles only short labels takes `ignore S37`; the Tailwind form reads the element's own text.

## Suppressing a misfire

A misfire returns on every rerun until the reason sits where the script can read it. Two comment forms do that, and the reason is part of the syntax:

| Form | Where | Silences |
|---|---|---|
| `product-ui: ignore S8 <reason>` | the line before the finding, or the same line | that ID on that line only. For the per-line checks: S1, S2, S3, S8, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19–S37 |
| `product-ui: ignore-file S9 <reason>` | anywhere in a scanned file | that ID for the whole file (S9, S12–S16, S18, S19–S37) or, for the per-run checks S4, S5, S6 and S7, for the whole run |

Comment syntax follows the file: `<!-- -->` in HTML, `/* */` in CSS, `{/* */}` in JSX. A form with no reason after the ID is reported as **S0 (warning)** and suppresses nothing, so a bare `ignore` cannot pass silently.

```html
<!-- product-ui: ignore-file S9 title separators in <title>, not prose -->
```

Suppress only a misfire, where the check read the line wrong; where it read the line correctly, fix the line. The reason states how the check misread it, for a later reader to verify.

## Out of reach for this script

Step 5, the independent review through `review-design-lead`, judges these against the rendered page:

- Headline copy that says nothing ("Scale without limits." and its relatives, which would suit any product)
- The reused shape of centred hero, then three equal-width cards
- Whether anything guides the eye
- Measured contrast ratios
- Links and controls that look interactive and lead nowhere, on a screen the brief marks `wired` (R10 measures links without a destination; a mock's placeholders are accepted)
- A handler that reports success through a named function (S17 reads inline handlers only)
- A feature row with no enclosure (R20 needs boxes to count)
- Gradient text, glass, one large radius on every container, a missing Japanese typeface and icon-and-heading tile rows as they render: `scripts/render/check_render.py` measures them on the live page as R16 to R20

## Measured on the rendered page

`scripts/render/check_render.py` measures these on the live page at Step 5. They are ported from impeccable 4.8.0 (Apache-2.0; see `THIRD_PARTY_NOTICES.md`), and each entry names the impeccable rule it follows.

- **R20: a row of icon-and-heading tiles.** Three or more equal tiles on screen on one line (the same size within 2px), each with an svg or img of 24px or more whose bottom lies at or above the tile's first heading top plus 8px, and no drawn box of 64x64 or more inside. A WARNING when every tile carries a painted icon tile (the criteria of the next entry). A NOTE for a row of image or screenshot cards, which real landing pages ship. Calibrated on `research/20261106-real-screens`.
- **R20 also** reports, once per page and capture, rounded icon containers of 32 to 128px (ratio 0.7 to 1.4, tinted at alpha 0.05 or more, with a background image or bordered, radius under half the width, the icon under 95% of the width) that end at most 4px below the top of the heading that follows them, and lists the headings in the evidence. Source: impeccable `icon-tile-stack`. Not ported: an icon given as `<img>` or as a CSS background (svg, `i` icon classes and a leading emoji count).
- **R18: one radius on every container.** A WARNING when 5 or more containers (boxes on screen, 64x64 or more, holding text, with a px radius under half their shorter side) share one radius of 16px or more and no container has another non-zero radius. A single small radius is what established design systems ship. Calibrated on `research/20261106-real-screens`.
- **R25: italic serif display headline.** A WARNING when an h1 or an h2 of 48px and up is italic (oblique passes) and set in a serif (a known serif face, or a stack that names `serif`). An editorial register may keep it; otherwise set the headline in roman or in a sans display face. Source: impeccable `italic-serif-display`. Not ported: nothing known.
- **R26: kicker above a heading.** A WARNING for a tracked uppercase label (2 to 34 characters, at most 14px or 0.45 of the heading size up to 16px, spacing at least 0.06em) in p, span, div or small directly above an h1 to h4 of 20px and up. Nav, ul/ol/li, form, table, figure, breadcrumb, `aria-hidden`, card and app-panel contexts, dates, step numbers and document numbering are exempt; a label that R27 reports is left to it. Delete the label or fold its words into the heading. Source: impeccable `kicker-above-heading`. Not ported: nothing known.
- **R27: hero eyebrow.** A WARNING for a label of 14px or less directly above an h1 of 48px and up, set as tracked caps (1.6px or 0.08em), accent-coloured bold (weight 700 and up, channel spread 40 or more in any colour notation) or dash-prefixed (an accent `::before` or `::after` dash of 8 to 80 by 1 to 6px). A dated line passes in the tracked-caps form under 1.6px of spacing. Source: impeccable `hero-eyebrow-chip`. Not ported: nothing known.
- **R28: numbered section labels.** A NOTE when two or more tiny labels (`01`, `2 /`) with distinct indexes up to 40 sit beside h2 to h4. Let the hierarchy carry the sequence. Source: impeccable `numbered-section-labels` (advisory). Not ported: `#1` hash labels.
- **R29: oversized hero headline.** A WARNING for an h1 of 40 or more characters at 72px and up that takes 28% of the viewport height or 25% of its area. Set a long headline smaller or cut the copy. Source: impeccable `oversized-h1`. Not ported: nothing known.
- **R31: content invisible at rest.** A CRITICAL when the page holds 200 or more characters and 150 or more of them, over 30%, sit at opacity 0 or visibility hidden after load, measured over the whole document. A hidden box counts when it and its ancestors sit in normal flow (position static, relative or sticky) and it lies outside header, nav, `[role=banner|navigation|menu|menubar|tooltip|dialog]`, `[popover]`, closed disclosures (a previous sibling of it or of its 3 nearest ancestors holds a control with `aria-expanded=false`), inactive slides beside a shown slide, and boxes whose class words include menu, nav, drawer, dropdown, flyout, modal, tooltip, popover, popup, tip, hovercard, share, clone or duplicate. Left out of both counts: closed interface (inside nav, `inert`, closed `aria-controls` targets, tab and accordion panels, drawers, modals, mega-menu, submenu and dropdown classes, fixed boxes parked off screen), unstarted sliders, boxes a scroll or view timeline holds, timed fade-ins and loops, boxes parked outside a clipping ancestor, and the tags select, option, optgroup, datalist and dialog. The 8 largest hidden boxes, and 8 boxes inside them, are scrolled to and measured again; one that shows counts as shown. Make content visible by default. Source: impeccable `content-hidden-at-rest` (error). Not ported: animations are read from the Web Animations API, CSS transitions do not count as fade-ins, the clip test is geometric, each probe waits at most 250 ms, and the class-swap image reveal is left out.
- **R33: gray text on a colour.** A WARNING for gray ink (HSL lightness 0.3 to 0.85, saturation under 0.2) on a background that reads as colour (channel spread 40 or more, more on a near-black; a pale tint of OKLCH lightness 0.9 and up needs chroma 0.09). Text in a, blockquote, nav, input, textarea, select, pre, code, span, th, td, tr, li, label, button, hr and the media and svg tags, disabled text, and text on an image or gradient are exempt. Use a darker shade of the background or white. Source: impeccable `gray-on-color`. Not ported: the gradient-stop check.
- **R41: hairline border with a wide shadow.** A NOTE when 3 or more boxes that are siblings under one DOM parent (sizes within 25%) wear a border of 1.5px or less on 2 or more sides (alpha at least 0.28) and a shadow halo of 32px or more (alpha at least 0.12). Commit to a defined edge or a soft elevation. Source: impeccable `gpt-thin-border-wide-shadow` (advisory). Not ported: the wrapper-depth walk.
