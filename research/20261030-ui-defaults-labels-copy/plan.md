# Plan: product-ui defaults, type, labels and copy from the design systems

Repository: `C:\Mycode\ClaudeCode\product-ui` (branch `public`, uncommitted work of the previous round in the tree, all suites passing). Skill root `S = plugins/product-ui/skills/product-ui`; agents `A = plugins/product-ui/agents`.

## Conclusion

- Done: 2 lookup rows that recommended text under 14px (`S/data/ux-guidelines.csv` row 74, `S/data/styles.csv` row 29) now state the 14px floor; `lookup/test_lookup.py` passes.
- Proposed: 15 items in 4 tracks and an integration step. The user settled the 4 decisions they needed (D11 to D14).
- Recommended core: the Japanese type defaults (N1 to N3) and the radius and shadow closure (O1). Both rest on grade A or B design-system values. By a reading of the template, N1 also removes the R19 warning that the default example raises on every Japanese screen; the integration render confirms it.
- Expected effect:
  - A Japanese screen built from the default example gets a Japanese face in every stack. Its leading follows its surface, and its headings wrap without colliding.
  - No radius or box-shadow class can reach Tailwind's default values.
  - Labels and errors gain three rule-based checks from GOV.UK, Microsoft and DADS.

## Basis

Research: `C:\Mycode\ClaudeCode\product-ui\research\20261030-ui-defaults-labels-copy\report.md`. Inventory of the current defaults: `C:\Users\karid\AppData\Local\Temp\claude\C--Mycode-ClaudeCode-product-ui\cb8b0893-99e8-40fd-ae50-bb1c8a625857\scratchpad\defaults-inventory.md`.

Findings that shape the plan:

- The design systems publish values the skill can adopt:
  - Japanese body text at 16px [E21, E62]
  - line height of 1.5 or more for body text, 170% for reading text and 120 to 130% in DADS's dense styles for admin screens [E48, E52, E53]
  - SmartHR paragraphs at 1.5 [E64]
  - DADS standard styles: 160% at 18px, 150% from 20 to 32px, 140% from 36px; letter spacing 2% up to 26px, then 1% and 0 [E49, E51]
- WCAG 1.4.8 caps a line at 80 characters (40 for CJK) and asks for 1.5 line spacing [E73, E74].
- The AI tells for values are uniform application of framework defaults: about 0.5rem radius and 0.1-alpha shadow on every surface, wide tracking everywhere [E99, E101, E102]. The tell's shadow equals Tailwind's `shadow-sm` [E5]. No source ties a single value to AI output.
- Label rules agree across guides:
  - A button names its action [E76, E89].
  - 「こちら」 alone fails as link text, and repeated link text takes an `aria-label` [E81, E86, E87].
  - English errors leave out "please" and the generic "This field is required" [E91, E92, E98].
  - GOV.UK and Microsoft use sentence case; Apple uses title case [E89, E94].
- Tell lists for Japanese prose have weak or opposing evidence: 403 readers detected AI text poorly and judged from surface cues [E119, E121]; a thesis report confirmed 1 of 148 popular claims [E112].

The plan therefore takes values from the design systems, takes wording rules from the style guides, and adds no new word lists.

## Decisions for the user

Taken by the user on 2026-10-30.

| Item | Decision | Effect |
|---|---|---|
| D11 (N1) | Per-slot `family_ja` in `tokens.json`, required when `voice.lang` is `ja` and the slot's family is a Latin face (new T22) | The choice and its provenance are recorded. The schema changes, and an existing ja token file fails T22 until it adds the field |
| D12 (Q4) | 「削除」 on destructive buttons, as SmartHR writes it; C4 drops its destructive exemption | C4 reports 「削除する」. The user approved the change to the GOOD fixture at `test_check_copy.py:128` that this requires |
| D13 (P2) | No brand element on a screen unless the user specified it: no letter tile, no logo slot, no product name, no company name | The portal shell loses its sidebar header by default. A brand element appears only where the brief's `Brand area` line names it |
| D14 (P1) | MASTER.md component CSS refers to the token variables and names the transitioned properties | The component specs stay and follow `tokens.json` |

## Rules for every track

- Severity policy of the previous plan holds: a value with a published correct answer or a defect is an error; a rule from a single guide or a C-grade tell is a warning, ruled on in the hand-over.
- Each new check gets a test that fails before the change and passes after it, with data that separates the rule from a plausible wrong one. Existing assertions and fixtures change only with the user's approval.
- New messages follow the existing terse 常体 house style of each script.
- `THIRD_PARTY_NOTICES.md` records any further change to lookup data or code.
- References cite this run's items as "research E<n> (ui-defaults)" so they stay apart from "research T<n>" of the previous run.
- Each track updates the documents that describe what it changes, as listed under the track.

## Step 0 (main session, before the tracks)

Create `S/assets/ja_families.json` from `JA_FAMILIES` in `S/scripts/render/check_render.py:100-103`, with the date it was compiled. Tracks 1 and 2 both read it.

## Track 1: theme and tokens (N1 to N3, O1)

Files: `S/scripts/generate_theme.py`, `S/assets/theme.template.css`, `S/scripts/test_generate_theme.py`, `S/scripts/validate_tokens.py`, `S/scripts/test_validate_tokens.py`, `S/assets/tokens_example*.json`, `S/references/tokens-format.md`.

N1. Japanese face in every stack (D11). The default example is a `ja` screen set in `Fraunces` and `Public Sans`. The template writes `"<family>", ui-serif, serif`, so Japanese headings fall to the OS Mincho, and R19 should warn (inventory 3.11 and 3.12, read from the template; no render was run). With D11 (a):

- `typography.<slot>.family_ja` joins the schema. T22 fires when `voice.lang` is `ja` and both the slot's family and its `family_ja` lie outside `ja_families.json`. It lowercases the name and uses R19's substring match (`check_render.py:551`). Like T5, it is an error that becomes a warning when `meta.reference` is set.
- The template lines become `--font-display: "{{typography.display.family}}", {{family_ja.display}}ui-serif, serif;` and `--font-body: "{{typography.body.family}}", {{family_ja.body}}ui-sans-serif, sans-serif;`. The Japanese family therefore sits after the Latin family, which keeps the Latin glyphs, and before the generic family. `generate_theme.py` fills each in-line marker with `"<family_ja>", ` when the field is present and with nothing when it is absent. A test covers an `en` file without the field and a `ja` file with it.
- The example files:

| File | `family_ja` | Reason |
|---|---|---|
| `tokens_example.json` | display `Noto Serif JP`, body `Noto Sans JP` | pairs a serif with `Fraunces` and a sans with `Public Sans` |
| `tokens_example.dads.json` | none | its family is already `Noto Sans JP` |
| `tokens_example.portal-shell.json` | `Noto Sans JP` in both slots | the mockup ships `'Inter', 'Noto Sans JP', …` (`portal-shell.md:65`) |
| `tokens_example.smarthr.json` | none; the T22 warning goes into `defaults_applied` | smarthr-ui ships `system-ui, sans-serif` (`tokens-format.md:152`), and the route reproduces it |

- Provenance takes the optional keys `typography.display.family_ja` and `typography.body.family_ja`; the default example records `derived:`. T19 keeps its four required keys.
- The note in `tokens_example.portal-shell.json:24` that the template takes one family per slot is rewritten.
- `tokens-format.md` gains the field row, the provenance keys and the T22 row.
- Evidence: broken Japanese and Latin mixing (ai-tells-ui E118); DADS names `Noto Sans JP` [E21].

N2. Body leading and tracking by language and surface. `generate_theme.py` expands a new marker in the base layer and sets `--text-base--line-height` to the same value:

| `voice.lang` | `meta.surface` | `body` line height | `body` letter spacing | Source |
|---|---|---|---|---|
| `ja` | `lp` | 1.7 | 0.02em | DADS reading text, 170% and 2% at 16 and 17px [E49, E52] |
| `ja` | `saas` | 1.5 | 0 | SmartHR paragraphs [E64]; DADS minimum [E48] |
| `en` | either | 1.5 | 0 | WCAG 1.4.8 [E74] |

Tables and dense lists keep `text-sm` and its own line height; DADS's dense styles sit at 120 to 130% [E53]. Premise to check at implementation: Tailwind v4 preflight sets `line-height: 1.5` on `html`.

N3. Heading leading for Japanese. `LINE_HEIGHTS` (`S/scripts/generate_theme.py:41`) is keyed to the step name, and puts 1.111 on `text-4xl` and 1 from `text-5xl`. A wrapping Japanese heading at line height 1 collides. For `ja`, each ramp step takes its line height from its computed size in px, following DADS's standard styles [E49, E51]:

| Computed size | Line height |
|---|---|
| under 18px | the `body` value of N2 |
| 18px to under 20px | 1.6 |
| 20px to under 36px | 1.5 |
| 36px and up | 1.4 |

`en` keeps the current list. `test_generate_theme.py` asserts the `ja` values at ratios 1.125 and 1.25 and the unchanged `en` list.

O1. Radius and shadow closed to the tokens. Tailwind keeps its own extra radius and shadow steps beside the three token steps the template defines. `rounded-2xl` and `shadow-xl` therefore render Tailwind's defaults, which is the tell [E99, E102] (ai-tells-ui E11, E15). The template resets `--radius-*` and `--shadow-*` to `initial` as it does for `--text-*`. It then aliases each extra step to the nearest token step:

| Extra step | Token step |
|---|---|
| radius `xs` | `sm` |
| radius `xl` to `4xl` | `lg` |
| shadow `2xs` and `xs` | `sm` |
| shadow `xl` and `2xl` | `lg` |

The `inset-shadow-*` and `drop-shadow-*` namespaces stay out of scope: the tell names box shadows on cards. shadcn components that use `rounded-xl` keep a radius, now the token one. `test_generate_theme.py` asserts that the output holds both resets and every alias. Premises to check at implementation:

- the step names in Tailwind 4.3.3 `theme.css`
- the radius and shadow classes that shadcn's current components use
- whether `stack-defaults.md` replaces shadcn's own `--radius` block with `theme.css`

O1 lands before N2 and N3 inside this track, since all three edit the template and the generator.

## Track 2: render checks (N4, N5, Q1 and the R24 of P2)

Files: `S/scripts/render/check_render.py`, `S/scripts/render/cdp.js`, the render tests, `S/references/composition.md`.

Common rules for R21 and R22: a text element counts when its rect lies inside `scope.rect` (the first `<main>`, else `<body>`, `cdp.js:189`), its computed `lineHeight` holds a px value, and its height holds 2 or more lines. An element whose `lineHeight` is `normal` is skipped. `R19`'s list moves to `ja_families.json`.

N4. R21, reading leading (warning). A `p`, `li`, `dd` or `blockquote` element of 16 to 18px that meets the common rules and has a line height under 1.5 times its font size. Headings, table cells and text under 16px are out of scope. Source: WCAG 1.4.8, DADS 150% minimum [E74, E25]. `cdp.js` already dumps `tag`, `lineHeight`, `letterSpacing` and `rect` for each text element (`cdp.js:94-100`).

N5. R22, line length (warning). An element that meets the common rules and holds more than 40 full-width characters per line (width / (font size + letter spacing in px) > 40) when its text contains CJK, or more than 80 characters per line (width / (0.5 × font size) > 80) otherwise. Source: WCAG 1.4.8 [E73]. `composition.md` gains the measure `max-w-[40em]` for Japanese reading text: 640px at 16px, 40 full-width characters, and 39 with 0.02em tracking.

Q1. R23, one link name for two or more destinations (warning). Two or more links in one capture with the same visible text, different `href` and no `aria-label` that tells them apart. Source: DADS on 「もっと詳しく」 [E87]. `cdp.js` adds `ariaLabel` to each control; today `text` falls back to `aria-label` only when the text is empty.

The track extends the check list in the `check_render.py` docstring (`:53-60`).

## Track 3: copy and source checks (Q2 to Q5, R1, R2 and the C21 change of P2)

Files: `S/scripts/check_copy.py`, `S/scripts/test_check_copy.py`, `S/scripts/check_slop.py`, `S/scripts/test_check_slop.py`, `S/assets/stock_words.json`, `S/references/ui-copy.md`, `S/references/slop-checklist.md`.

Q2. C29, English error filler (warning). An `error` string containing `please`, or exactly `This field is required` or `Required` after trimming. Source: GOV.UK [E91, E92], Atlassian [E98]. Like C6 and C16, it skips `PRECISION_DIRS`. `invalid` stays with C16. No Japanese counterpart is added: the run found no source for one.

Q3. C30, case against `voice.case` (warning). An English `button` or `heading` of 2 or more words, checked only when `voice.case` is `sentence` or `title`; `null` skips it.

- Under `sentence`: a word after the first that starts with a capital. Words of `meta.name`, `voice.terms` and `voice.allow` pass, and so do all-capital acronyms.
- Under `title`: a lower-case word of 5 or more letters. The threshold is this skill's own; it leaves short articles, conjunctions and prepositions alone without a word list.
- Source: GOV.UK and Microsoft for sentence case, Apple for title case [E89, E94]; the project's setting decides.
- `ui-copy.md:162` and `:417` drop the statement that no check reads the case.

Q4. Destructive button (D12). With D12 (a): `ui-copy.md` lines 83 to 92 write 「削除」 on the button and in the dialog, and the dialog title takes 「{対象}の削除」 [E79]. C4 reports 「削除する」 like any other サ変 + する label. The exemption at `check_copy.py:494` (`and not item.destructive`) goes, and with it the `DESTRUCTIVE` pattern and the `destructive` attribute (`check_copy.py:118, 185-192, 289, 314`), which nothing else reads. C4's **Allowed** and **On the threshold** paragraphs (`ui-copy.md:192-194`) are rewritten to match.

Q5. Status labels. `ui-copy.md` gains a rule for the gap in inventory 4.29: a status badge is a noun phrase naming the progress or the action asked of the reader, and an ongoing state takes 「○○中」 [E82, E83]. S18 (warning) in `check_slop.py`: `animate-pulse` or `animate-ping` on an element whose whole text is `New` or `Live` (any case) or 「新着」 [E103, grade C]. Premise to check at implementation: the scan scope of `check_slop.py` reads the element's text beside its class.

R1. Re-base the reasons. C22 to C25 keep their patterns and warning level. Their **Why** paragraphs add the style-guide rule each enforces (Microsoft on unnecessary words [E95], GOV.UK on "please note" [E92]) beside the previous run's tell sources. They also state that Japanese tell lists carry weak evidence [E112, E119].

R2. Remove 「を実現」 from `japanese_stock` (C23). It is a common verb phrase in plain product copy, its only source is one practitioner (ai-tells-ui E113), and the Japanese evidence weighs against single-word markers [E112, E119]. The word also leaves the list in C23's **Check** paragraph (`ui-copy.md:341`). The headline template 「手間なく.{1,12}を実現」 stays. A test with a plain sentence ending in 「を実現します」 asserts no C23.

The track extends the check lists for S18: `slop-checklist.md:3` (the range), `:12` (the warning list) and `:181` (the per-line ignore list), and the `S1-S17` strings in `check_slop.py` (`:4`, `:777`).

## Track 4: lookup, portal shell and brief (P1, P2 without R24)

Files: `S/scripts/lookup/design_system.py`, `S/scripts/lookup/test_lookup.py`, `S/references/portal-shell.md`, `S/assets/shell.portal-shell.css`, `S/assets/brief.template.md`, `plugins/product-ui/THIRD_PARTY_NOTICES.md`.

P1. MASTER.md component CSS (D14). `S/scripts/lookup/design_system.py:764-878` writes Tailwind's spacing values 4 to 64px, four shadow steps, radii of 8, 12 and 16px, px paddings and `transition: all 200ms ease`. S14 warns on the last, and `tokens.json` contradicts the rest (inventory 1.31 to 1.33). With D14 (a):

- radii become `var(--radius-sm|md|lg)`, shadows `var(--shadow-sm|md|lg)` (the modal's `--shadow-xl` becomes `--shadow-lg`)
- paddings become `calc(var(--spacing) * n)` with the same n at a 4px base
- transitions name their properties and use `var(--duration-base) var(--ease-standard)`
- the spacing and shadow tables give way to a pointer to `theme.css`
- `lookup/test_lookup.py` asserts that the output holds no `transition: all`, no radius literal and no `--shadow-xl`
- `THIRD_PARTY_NOTICES.md` adds "component CSS in MASTER.md that refers to the theme's variables" to its list of modifications

P2. Brand elements only on request (D13). `S/references/portal-shell.md:12,23,84,101-108` and `S/assets/shell.portal-shell.css:76-110` draw a sidebar header with an initial in a primary-coloured tile, a product name and a company name. `tokens-format.md:95` and `S/SKILL.md:109` set the product name as a wordmark when `meta.logo` is `null`. With D13:

- `S/assets/brief.template.md` gains `- Brand area: {{none | the elements the user asked for}}` under `## Screen`, `none` by default.
- The portal shell drops the sidebar header from its markup and CSS, and the header comment at `shell.portal-shell.css:10` then lists `.sidebar-nav / .sidebar-footer`. In `portal-shell.md`, line 12 drops the tile, the product name and the subtitle; line 19 drops "the product name and"; line 23 drops the tile, so the brand colour appears in three places; line 84 drops "the logo initial" and "the sidebar title". A header the brief asks for is written per project.
- Lines 19, 65, 82 and 84 also take N1's change: the template now carries a Japanese family per slot, and the portal example sets `Noto Sans JP`.
- Integration step 1 rewrites `tokens-format.md:95` and `S/SKILL.md:109` to one wording: with `null`, nothing is drawn in the logo's place, and a brand element appears only where the brief's `Brand area` lists it. `A/review-design-auditor.md:108` widens its WARNING to any logo, letter tile, product name, company name, tagline or copyright line that the brief's `Brand area` does not list.
- Track 3 rewrites C21: the message at `check_copy.py:461` and the **Check** paragraph at `ui-copy.md:323` allow a string equal to `meta.name` only where the brief's `Brand area` lists the product name, and drop the "logo or sidebar title" reason.
- R24 (warning, Track 2): a rendered text element whose trimmed text equals `meta.name`, read from the `--tokens` file, when the brief's `Brand area` is `none` or absent. Without `--tokens`, R24 is skipped and the scope line says so, as R2 does (`check_render.py:775`). A render test covers three cases: the name with `Brand area: none` gives R24; the name with `Brand area` listing it gives none; no `--tokens` skips R24.

## Integration (main session, after the tracks)

1. The brand rule of P2 goes into `tokens-format.md:95`, `S/SKILL.md:109` and `A/review-design-auditor.md:108`. Check lists outside the tracks name the new checks (T22, R21 to R24, C29, C30 and S18). The files are `S/SKILL.md`, the two review agents `A/review-design-auditor.md` and `A/review-design-lead.md`, and `README.md`.
2. Full suites and self-checks.
3. `generate_theme.py` on the four examples, then `validate_tokens.py` on each.
4. One generated Japanese page built with the Tailwind CLI and rendered through `cdp.js` and `check_render.py`. The page carries `rounded-2xl` and `shadow-xl` probes and Japanese paragraphs and headings. Pass: no R19, the probes compute to the token values, and R21 and R22 fire only on the paragraphs built to break them. If the Tailwind CLI cannot run here, this step is reported as unverified.
5. `/code-review` at high on the diff.

## Not proposed

- Type scale: `typography.scale.base_px` 16 to 18 and the default ratio 1.25 stay. The base matches DADS and SmartHR at 16px [E21, E62]; Tailwind's own neighbouring steps run at ratios 1.11 to 1.25 (report, section 3).
- Colour defaults: no source gives the colour count of a highly rated palette (report, section 1). T9, T20 and T21 from the previous round stay.
- Motion defaults: the run collected no duration or easing values. T11's range of 120 to 400ms stays.
- Spacing base of 5px (GOV.UK [E10]): Tailwind's multiplier serves 4 and 8; no reader effect is reported.
- A check on spacing values or step counts: no source ties a spacing value to AI output or to reader harm.
- New English or Japanese stock words (GPT-5-era words [E110]): words such as "enhance" are ordinary UI verbs, and the evidence on lists is weak.
- Hit area at 44px: R5 checks the WCAG 2.5.8 floor of 24px; the 44px in `dads-components.md` and the lookup rows is a recommendation above that floor, so the files agree.
- Inventory items that are no defect: `設定` as a heading (the existence auditor keeps it, the design auditor asks for a more specific one; the two questions differ), the 10 and 11 stock words (`seamlessly` is covered by the `ly` rule), the spring and weight values in `tokens-format.md` (a separate example).
- Values from award-recognised sites: the run found none (report, Disagreements and limits).

## Done when

- Every test file and self-check passes, with a fail-before test for each new check and each defect fix.
- The integration render shows no R19 finding on the default example's Japanese page.
- `test_generate_theme.py` shows the radius and shadow resets and aliases in every generated `theme.css`, and the integration probes compute to the token values.
