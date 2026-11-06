---
name: product-ui
description: >-
  Builds web screens that read as a real product: each screen composed from what production screens of its kind carry
  (regions, sizes and wording measured on real screens), tokens and wording settled before markup,
  shadcn/ui on Tailwind v4 or DADS or SmartHR, an OOUI or task-oriented structure chosen at intake, the users recorded
  and each screen planned (its job, its dominant element, its reading order, its containers) before markup, each container
  built from a pattern drawn from production design systems and chosen from the brief by a script, a test for whether each
  user-visible string should exist, text at 14px or more (12px for a short Latin-only run), checks and an independent review. REMOVE mode strips annotations and small text from an existing screen;
  lookup data answers palette, pairing, style, chart and stack questions.
  Use for any screen, component or UI wording, and when an interface reads as AI-made.
  trigger words: 画面, ページ, ランディングページ, ダッシュボード, デザイントークン, AIっぽい,
  構成, レイアウト, カードだらけ, 全部カード, 同じ画面, テンプレ感, 誰向け,
  カードに情報がない, 欲しい情報がない, 一覧に何を出すか, 項目の選び方, ラベリング, 空状態, ステータス,
  ダサい, 文字が小さい, 文言, ラベル, エラーメッセージ, UIライティング, マイクロコピー,
  説明っぽい, 説明文が入る, 注釈だらけ, 注記だらけ, キャプション, ヘルプテキスト, 補足テキスト,
  小さい文字の説明, 注釈を消して, 但し書き, 手法の説明, サブテキストを削除, 説明文を消して,
  配色, パレット, フォントの組み合わせ, スタイル, グラスモーフィズム, チャート, DADS, SmartHR,
  OOUI, オブジェクト指向UI, タスク指向,
  UI copy, microcopy, helper text, caption, self-describing UI, shippable copy, palette,
  font pairing, chart type, design style.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill, Agent
---

# product-ui

One entry point for building and reworking web interfaces. Each screen is composed from what production screens of its kind carry (`references/real-screens.md`), every design decision lands in `tokens.json` (the colours, the type and the wording), and the result reaches the user once the check scripts and one independent reviewer have passed it. The lookup data and scripts under `scripts/lookup/` and `data/` come from ui-ux-pro-max, adapted to this skill (`THIRD_PARTY_NOTICES.md`).

`{SKILL_DIR}` is the absolute path of this skill's directory: `<plugin root>/skills/product-ui` under the plugin, `~/.claude/skills/product-ui` under a manual install. Under the plugin the agents carry the `product-ui:` prefix (`product-ui:review-design-lead`) and the hook registers itself; a manual install uses the bare agent names. The commands say `python`; on macOS and Linux run `python3`.

## Principles

1. **Real screens are the standard.** `references/real-screens.md` records what production screens of each kind carry: their regions, their sizes and their wording, measured on real screens (`research/20261106-real-screens/report.md`). A screen is composed from that record, and a check keeps a threshold only where real screens stay inside it.
2. **A screen ships inside its product.** Every real screen carries its product's header with the logo or the product name, its navigation where the kind has one (a sign-in or sign-up form carries the header alone), and the controls a screen of its kind has: a create action above a collection, a link from each row to its record, pagination. The build draws them. The header shows the product name as text where `meta.logo` is `null`, and a control whose destination lies outside this build is a link to the route it will open. A control never reports an effect it does not have, and a logo mark is drawn only from a file the user supplied.
3. **Tokens before markup.** The tokens are settled first and the implementation reads only those variables, because "did this file use a value outside the token set" is checkable. Wording follows the same rule: `tokens.json` carries a `voice` block, and `check_copy.py` asks whether the implementation used it.
4. **A string exists only if a product writer could defend it.** A label labels, an error says what to do, an empty state says the list is empty. Text that explains the screen, describes the layout, defends a number or fills a slot is deleted.
5. **Text is 14px or more.** Reading text is 16px, and the rows, cells and labels of a dense screen sit at 14px. A Latin-only run of at most 24 characters (a unit, a timestamp, a code) may go to 12px. A string that only fits at 11px is deleted. This minimum is this skill's own rule: real screens set metadata and dense rows smaller, and `references/real-screens.md` gives beside each real size the size to build with.
6. **Prohibitions live in scripts.** A rule written as "never do X" belongs in `check_slop.py`, `check_copy.py` or `check_shippable_text.py`, where a file can fail it.
7. **Review happens elsewhere.** Step 5 hands the rendered result to a reviewer who holds none of the context that produced it.
8. **The screen is composed before it is built.** `tokens.json` records who uses the product (`meta.users`), and `ui-brief.md` records, before any markup, the kind of screen and the regions it carries (`references/real-screens.md`), what the screen is for, who reads it, what dominates, in what order it is read and which container each section gets (`references/composition.md`). The reviewer judges the whole screen against that plan before judging its parts.
9. **Every visible choice has a source.** Colours, type and the logo record where they came from (`meta.provenance`, `meta.logo`), because a value equal to a known default with no recorded source shows that nobody chose it. The brief's `Brand area` line lists the brand elements the screen draws. Proof on a screen (figures, testimonials, customer logos) comes from the brief's Proof section or stays off the screen. Each collection, fetch and form has its empty, loading and error state in the brief.
10. **Each container carries what its pattern names.** What a row, a table, a card, a record's header or an empty state shows comes from a pattern in `patterns/`, drawn from what production design systems publish about that component and naming its sources (`references/patterns.md`). The brief ranks each object's properties by the reader's job, `scripts/patterns/resolve.py` picks the pattern and fills its slots from that ranking, and the same brief gives the same patterns and the same skeletons on every run.

## Out of scope

This skill covers interactive screens. These belong to other tools:

- HTML documents, reports, and a dashboard that is a static report page (a public status page is a screen of the Monitoring kind)
- Personas, journey maps, usability tests
- Logos, CIP, icon and social image generation
- PowerPoint decks

## Modes

| Mode | Condition | What runs | Cost |
|---|---|---|---|
| LIGHT | One local change to an existing screen, with tokens already in place | Steps 3 and 4 | scripts only |
| STANDARD | A new screen or page, or a redesign | Steps 0 through 6 | one review round |
| DEEP | A whole product surface, or the user asks for thoroughness | Steps 0 through 6, with Step 5 on every distinct screen | one review round per screen |
| REMOVE | The screen exists and carries annotations or small text: 「注釈を消して」「サブテキストを削除して」「文字が小さい」 | The REMOVE procedure, then Step 4 | scripts plus the auditor |

STANDARD escalates to DEEP once the surface spans more than one screen, and the escalation holds for the rest of the work. The steps of one flow on one route (入力, 確認, 完了) are one screen with states, and the brief lists each state. A state that only a server reaches in production (完了 after a submission, a sign-in error) is built and shown by a URL the brief names, such as `?state=done`, so the review can render it; the submit control still posts to its route. A mock gives the same kind of URL to every other state the brief lists that a plain load of the entry does not show (確認, a validation error, an incident in progress on a status page). A view the request leaves out (the single view behind a collection, the create form behind 「新規」) stays outside the build, and the screen links to its route. The first line of the reply after intake states the mode and the reason, `Mode: STANDARD (one new screen, tokens.json absent)`, so the user sees the cost before any agent starts.

## Routing

| Request | Goes to |
|---|---|
| What production screens of this kind carry: the regions, the sizes, the wording of each slot | `references/real-screens.md` |
| The application shell: the header, the navigation, the content column | "The shell" in `references/composition.md` |
| Whether a user-visible string should exist; stripping annotations, captions, helper text and small text | `references/ban-list.md`; the REMOVE mode |
| The words on a Japanese screen: labels, buttons, errors, empty states | `references/ui-copy.md` |
| The words on an English screen | `interfaces:better-writing`, with `references/ui-copy.md` for what the checks enforce |
| Which objects a product shows, their collection and single views, what the navigation lists, where an action sits | `references/ooui.md` |
| What a screen is for and who reads it; what goes first and what dominates; whether a section is a panel, a table, a list or a heading on the ground; whether a KPI row exists | `references/composition.md` |
| What a row, a table, a card, a record's header, a task list, a status or an empty state carries, and which of an object's properties each shows | `references/patterns.md`, `scripts/patterns/resolve.py` and `scaffold.py` |
| A shadcn component; dark mode; an accessible dialog, dropdown, form or table; a responsive layout in utility classes | `references/components.md` and the official documentation it links |
| Palettes, font pairings, visual styles, chart types, UX rules, per-stack rules | `references/lookup.md` and `scripts/lookup/search.py` |
| Building on the Digital Agency Design System | `references/dads.md` for the tokens, `references/dads-components.md` for the components |
| Building on the SmartHR Design System or smarthr-ui | `references/smarthr.md` for the tokens, SmartHR's own Claude Code plugin for the components |
| A new landing page or marketing site | `references/real-screens.md` (Landing page, Pricing page) for the sections and their order; `hallmark` for the page layout where it is installed; this skill for tokens and checks |
| A named adjustment of an existing screen: bolder, quieter, distill, delight, onboard, overdrive, and the verbs it routes on | `references/steering.md`, in LIGHT mode, then Step 4 |
| Polishing an existing interface | `interfaces:better-ui`, `interfaces:better-layout`, `interfaces:better-typography`, `interfaces:better-colors` |
| Whether motion belongs, and how it should feel | `emil-design-eng`; Apple-like gesture motion to `apple-design` |
| Finding places that should animate, auditing all motion, reviewing motion in a diff | `find-animation-opportunities`, `improve-animations`, `review-animations` (user-invoked) |
| Keyboard, focus, screen readers, accessible names | `interfaces:better-accessibility` |

When more than one row applies, tokens come first and review comes last; the order in between follows the request.

The external skills are published separately: `hallmark` at https://github.com/Nutlope/hallmark, the `interfaces` plugin at https://github.com/jakubkrehel/skills, and the motion skills at https://github.com/emilkowalski/skills. Where one is missing from the install, do that row's work in the main session and say so in the hand-over.

## Pipeline

When resuming interrupted work, decide the next step from which files exist, and from those alone: `tokens.json`, `theme.css`, `ui-brief.md` (with its `## Slots` table once `resolve.py` has run), `scaffold/`, the built output.

### Step 0: Intake

Skip this step when `tokens.json` exists and the request is a local change.

Detect the existing stack (`package.json`, `tailwind.config.*`, an `@import "tailwindcss"`); a project with none takes the defaults in `references/stack-defaults.md`. Then ask at most four questions in one AskUserQuestion round:

- **Surface**: landing page (`lp`, a marketing page) or application (`saas`, a screen a person operates, behind a login or public: a search-results page, a sign-up form and a public-service form are applications).
- **Reference**: デジタル庁デザインシステム (`references/dads.md`) for public-sector sites, SmartHR (`references/smarthr.md`) for Japanese B2B SaaS dense with forms and tables, or なし, where the tokens come from the request or from a product the user names.
- **Structure**: オブジェクト指向UI (OOUI) or タスク指向UI, recorded in `meta.structure` as `ooui` or `task`. Put first the one the table under "Choosing the structure" in `references/ooui.md` points to. A request that already names one settles it, and the question is left out.
- **Users**: the groups who use the product, each with a role, how often they use it (daily, weekly, occasional, first time), their expertise (novice, intermediate, expert) and the outcome they come for; a device or setting of use the request reports goes into the group's `context`. Offer the roles the request implies as options. The answer goes into `meta.users` with `basis: reported`; a group settled by default goes in with `basis: assumed`. An `lp` surface spends no question on it.
- **Brand**: the product's name, its colour, its typeface and its logo file. Asked only when the request names none of them. A preset named in the Reference answer overrides the colour and typeface of the Brand answer.
- **Stack**: a question only when the detection is ambiguous; otherwise the detected stack is recorded in `meta.defaults_applied`.

Take the questions in the order Surface, Reference, Structure, Users, Brand, Stack, and skip each one the request or the project already settles. A question the cap of four leaves out, or one the user cannot be asked, is settled by default and recorded in `meta.defaults_applied`: Surface from what the request builds; Reference as なし, or デジタル庁デザインシステム where the request builds a screen of a Japanese public body in a project that holds no component library yet; Structure as the row of the table under "Choosing the structure" in `references/ooui.md` that the request fits; Users with `basis: assumed` (a field the request states is `reported`, and `basis` may map each field to its own value); Brand with colours from the lookup under `lookup:` provenance, `meta.logo: null` and the product name from the request. Where the request names no product, `meta.name` takes the request's own words for it (「アクセス解析」 from 「自社サイトのアクセス解析画面」), and `meta.defaults_applied` records the name as assumed. A screen of a public body names its operator in the header and the footer: where the request leaves the operator unnamed, the header shows the service's name, the operator is an open slot (`[TODO: 自治体名]`), and the hand-over asks for it. A Reference preset named in the request settles Brand with `reference:` provenance; when Reference is asked in the same round, Brand is asked too, and a preset answer overrides it.

Settle everything else by default and record each default in `meta.defaults_applied`; `register` defaults to 敬体 and `katakana_choon` to `jtf`. Read the interface language off the project and spend no question on it.

### Step 1: Settle the tokens

Write `tokens.json` at the project root, in the shape `references/tokens-format.md` defines; `theme.css` and `ui-brief.md` sit beside it. `assets/tokens_example.json` is a filled-in example, and `assets/tokens_example.{dads,smarthr}.json` are the two presets.

- **Colours**: follow "Deriving the colours" in `references/tokens-format.md`. Route the arithmetic to `interfaces:better-colors` where it is installed, else follow those rules by hand and check each pair with `python {SKILL_DIR}/scripts/colour.py contrast "<a>" "<b>"`. Candidate palettes and pairings come from `scripts/lookup/search.py` (`references/lookup.md`) before a value is written by hand: `--design-system` with `--surface saas` or `--surface lp`, and `--lang ja` on a Japanese interface. Beside a colour equal to a Tailwind default the lookup prints the value that clears T20; that value goes into `tokens.json`. The ground is light unless the request asks for a dark interface (`references/real-screens.md`, Every screen): the lookup prints its palettes for a light screen, with a white ground and the text at a lightness of 30% or under.
- **Voice**: write `terms` for the product, one word per operation, reading the words already on existing screens first. `assets/voice_terms.ja.json` carries the 長音 pairs C9 checks.
- **Reference**: when `meta.reference` names a preset, copy that reference's mapping. For any other reference product, work from a screenshot and a written description of it together.
- **Provenance**: write `meta.provenance` with one entry each for `color.primary`, `color.accent`, `typography.display` and `typography.body`, every value starting with `brand:`, `reference:`, `user:`, `lookup:` or `derived:` and naming the source. A palette taken from the lookup is recorded as `lookup:`; T20 warns on a Tailwind default colour from it: keep the colour with a ruling in the hand-over, or take the nearest darker lightness its message gives. Write `meta.logo` as the path of the product's logo file, or `null`; with `null` the header shows the product name as text, and no letter tile, monogram or drawn mark stands in for the logo. On a `ja` interface, a type slot whose family is a Latin face takes a Japanese `family_ja` (T22).

### Step 2: Mechanical check on the tokens

```bash
python {SKILL_DIR}/scripts/validate_tokens.py tokens.json --json
python {SKILL_DIR}/scripts/generate_theme.py tokens.json
```

An error from `validate_tokens.py` sends this back to Step 1 before the generator runs. Rule on each warning in the hand-over: fix it, or keep it with a stated reason. `generate_theme.py` writes `theme.css` beside `tokens.json`: Tailwind v4 source, or plain CSS custom properties with `--plain` and for the `html` renderer. A project that already has a stylesheet joins it as "Using theme.css in an existing project" in `references/stack-defaults.md` says. Its `--text-*` scale starts at `text-xs` (12px, Latin-short only) and `text-sm` (14px); `text-base` and the steps above it are computed from `typography.scale` (`base_px` and `ratio`), and `--spacing` from `spacing.base_px`, so regenerating replaces Tailwind's fixed steps. Change `theme.css` only through `tokens.json` and the generator.

### Step 3: Build

Before any markup, read the section of `references/real-screens.md` for the kind of screen the request asks for. Then write `ui-brief.md` beside `tokens.json` from `assets/brief.template.md`: the screen's purpose in one sentence and the Composition section from `references/composition.md`, one block per screen (kind, regions, job class, reader, dominant element, reading order, density, archetype, grouping cue per section, what is constant and what is decided here, omissions, the tile row or `none`). The Regions line lists the regions the kind carries, the shell first; a region real screens usually carry is built unless the request rules it out or its content would be a fact about the business that the request does not give (steps 3 and 4 of "How to use it" in `references/real-screens.md`), and the Omitted line gives the reason for each one left out. When `meta.structure` is `ooui`, work through the three steps in `references/ooui.md` first and fill the brief's Structure section with the object table. The brief is the plan the Step 5 reviewer conforms the screen to, so a decision the markup departs from is changed in the brief first.

Then fill the brief's `## Objects` table and each block's `- Sections:` list (`references/patterns.md`): one row per object, its properties ranked by the reader's job, and one line per section saying what it holds. Run

```bash
python {SKILL_DIR}/scripts/patterns/resolve.py ui-brief.md
python {SKILL_DIR}/scripts/patterns/scaffold.py ui-brief.md
```

`resolve.py` picks each section's pattern from `patterns/index.json` and writes the `## Slots` table; when it stops, it names the one question the brief has to answer (whether the reader compares the records, which property is the identifier), and that question goes to the user when the request does not answer it. `scaffold.py` writes one skeleton per section under `scaffold/`, in the stack `tokens.json` names. Build each section from its skeleton: keep its slots, their order and the `data-pattern`, `data-pattern-slot` and `data-pattern-field` attributes, bind the record's keys and write the words. A slot added or dropped on the screen is changed in the brief first, and both scripts run again.

The brief also carries the sections the checks and the reviewer read: `## Proof` (each figure, testimonial, customer logo and claim the screen shows, with its source; empty means the screen shows none), `## States` (per screen: each collection's empty state, each fetch's loading and error state, each form's validation), `## Sample data` (who supplied it; mock data varies names, dates and amounts and carries no statistic the reader did not ask for) and, on `lp`, the lead content (what the reader sees first: the product itself, named). Sample data covers the content the product would hold (the names of people, sites and organisations, titles, message bodies, dates, amounts) and is invented for a mock, at the volume a production screen of the kind holds: a full page of records in a collection, the whole thread on a record. An amount the screen computes from, such as a fee per item or a unit price, is sample data too, and the hand-over names it as invented. A form opens empty, as production forms do: its sample data are the options and the records it lists, and a filled form is one of the brief's states at its own URL. A photograph a record would hold is a neutral block at the photograph's size with its `alt` text, and an avatar is the person's initials (for a Japanese name, the first character of the family name); stock art and drawn illustrations stay out. The interface's own strings follow the ban list. A control whose destination is outside this build links to the route it will open; a control that would only pretend (a save that changes nothing and shows a toast) is wired to its real effect or left out.

Then follow the routing table. Colours, type, spacing, radius, shadow and motion come from `theme.css` variables only; components follow `references/components.md` or the preset's component reference; containers follow the table in `references/composition.md`, and what each container carries follows its pattern.

Read `references/ban-list.md` and `references/ui-copy.md` before writing any string a user will see. The ban list settles whether a string exists and how small text may be; ui-copy.md settles how a string that exists is worded. When the brief gives no real content for a slot, leave `[TODO: …]` in a source comment and ask the user one question that lists every open slot; prose invented to fill a slot is a defect. Content that screens of the kind always state and the request leaves open (税込 or 税抜 beside a price, the 受付番号 after a submission) goes into the same question. When the user cannot be asked, the slot stays empty, the `[TODO]` stays in the source, and the question goes into the hand-over's open list.

### Step 4: Mechanical checks on the output

```bash
python {SKILL_DIR}/scripts/check_slop.py <paths> --json
python {SKILL_DIR}/scripts/check_copy.py <paths> --emit-prose {OUT}/copy-prose.md --json
python {SKILL_DIR}/scripts/check_shippable_text.py <paths> --json
python {SKILL_DIR}/scripts/check_pattern.py <paths> --json
```

```bash
npx --no-install textlint --config {SKILL_DIR}/assets/textlintrc.ui.json {OUT}/copy-prose.md
```

`<paths>` are the screen's own files: the ones the brief's `Built files` line lists and the components they import. A vendored component the screen never renders stays out of the run. `{OUT}` is a review directory outside the deliverable and new for this run: the path `mktemp -d` prints, or a folder the project's `.gitignore` lists. The prose file, the captures and the measurements go there and stay out of the project's files.

- **Errors**: an error from any of the four scripts sends this back to Step 3. `check_pattern.py` reads the brief beside `tokens.json` (`--brief` names another) and resolves it as `resolve.py` does; a brief that cannot be resolved leaves its plan checks (PT2's plan half, PT6, PT7) unread, and the output says why. Its PT1, PT2, PT4 and PT5 are warnings until the calibration settles them as errors; rule on each like any warning.
- **Warnings**: every warning from `check_slop.py`, `check_copy.py`, `check_shippable_text.py` and `check_pattern.py` gets a ruling in the hand-over: fixed, or kept with its reason. For a `check_shippable_text.py` warning, delete the annotation, or keep it and name its allowance. Delete text that explains the design or the way through the screen at either severity.
- **textlint**: it covers the prose-shaped strings `check_copy.py` writes to `copy-prose.md`. Fix each finding; deleting the string counts as a fix, and a string under the carve-out in `references/ui-copy.md` stays. textlint is optional: the plugin leaves its install to the user, and the README names the npm packages. `--no-install` keeps npx from downloading it. When the command fails because textlint is absent, or exits with `No rules found` or a message that the config holds no rules because the presets are missing, skip it and write `textlint skipped: textlint or its presets are not installed` in the hand-over; the Python scripts still gate.
- **prose-lint**: when the `prose-lint` skill is installed (https://github.com/tomkd555/prose-lint), invoke it on `copy-prose.md` with `style=business` as well, and rule on each of its findings as on a textlint finding: fix the string, delete it, or keep it under the carve-out. It reads the prose-shaped strings only; the labels stay with `check_copy.py` and the label register. When it is not installed, write `prose-lint skipped: not installed` in the hand-over.
- **Misfires**: silence a misfire of `check_slop.py`, `check_copy.py` or `check_pattern.py` in the file itself, as `product-ui: ignore <ID> <reason>` or `product-ui: ignore-file <ID> <reason>` (forms in `references/slop-checklist.md` and `references/ui-copy.md`). Suppress only a misfire; fix a string the check read correctly. Fix every `check_shippable_text.py` error, because that script reads no suppression form.

Step 5 starts once no error remains and every warning has its ruling.

The Step 2 and Step 4 scripts exit 0 on pass and 1 on failure, and print readable output when `--json` is omitted; `check_shippable_text.py` exits 2 when a directory holds no file in scope. `check_slop.py` finds `theme.css` beneath the paths, then up to four directories above them. `check_copy.py` finds `tokens.json` in the directory holding the paths, then up to three directories above it; `--tokens` names the file directly. C27 reads the `## Proof` section of `ui-brief.md` beside `tokens.json`; `--brief PATH` names another brief. `check_shippable_text.py` reads `meta.surface` from the `tokens.json` nearest its first path for ST3 (`--surface lp|saas` overrides). It takes `--checks <IDs>` to run a subset, `--css <file.css>` to add a stylesheet to the cascade, and `--dom <dump.json>` to judge a `cdp.js` dump.

When a check fails, read the reference that owns its ID:

| IDs | Script | Reference |
|---|---|---|
| T1–T23 | `validate_tokens.py` | `references/tokens-format.md` (T19 provenance, T20 default colour, T21 tinted neutrals, T22 Japanese family, T23 status words) |
| S1–S37 | `check_slop.py` | `references/slop-checklist.md`; `references/composition.md` for S11 |
| C1–C36 | `check_copy.py` | `references/ui-copy.md`; `references/ooui.md` for C17; `references/composition.md` for C18–C21; `references/patterns.md` for the label forms C33–C36 read |
| ST1–ST10 | `check_shippable_text.py` | `references/ban-list.md` |
| PV1–PV8 | `scripts/patterns/validate.py` | `references/patterns.md` |
| PT0–PT7 | `check_pattern.py` | `references/patterns.md` |
| R1–R48 | `check_render.py` (Step 5) | `references/composition.md` for R4, R12–R15, R21–R22, R30, R32, R34–R37 and R39, and for the conditions of R1, R3, R5–R8, R10 and R19 under "What the checks cover"; `references/slop-checklist.md` for R16–R20, R25–R29, R31, R33 and R41; `references/ui-copy.md` for R24, R38, R40 and R48; R23 sits under "What the checks cover" in `references/composition.md`; `references/patterns.md` for R42–R47 |

### Step 5: Independent review

The step needs a renderable entry point, Node 22 or later, a Chrome install and the Agent tool. The entry point is served over HTTP: a bundler's `dist/index.html` loads its script as a module and renders blank from a `file://` URL, so serve the output directory (`python -m http.server <port> --bind 127.0.0.1 --directory dist`) and render `http://127.0.0.1:<port>/`.

Complete the `ui-brief.md` written in Step 3: the built file paths, the entry file to render and whether the controls are wired. The Proof, States and Sample data sections stay; P3 compares the rendered screen with them. The template's Objects, Composition and Slots sections, the eight cold-read questions, the seven copy questions, the three reader-fit questions and the three content questions stay; the Structure section stays when `meta.structure` is `ooui` and is deleted otherwise.

Then launch both agents in one message, each with `model: opus`:

- `review-design-lead`, with `plan: ui-brief.md`, `target:` the directory the entry point is served from (the build output, `dist`, of a bundler project; else the project directory), and `scripts: {SKILL_DIR}/scripts/render`; it requires all three and returns `{"error": …}` when one is missing. It renders through headless Chrome at 1280px and 375px and measures the page with `check_render.py` (R1–R48, with `--plan` reading the brief's job class for R15). R7 measures the computed text size, which covers a size set from JavaScript or a transform; R12 to R15 measure nested enclosures, spacing steps, emphasis levels and equal tile rows; R16 to R20 flag gradient text, backdrop blur, one large radius on every container, a missing Japanese font and icon tiles above headings; R25 to R41 are the impeccable ports listed in the reference files; R42 to R48 measure whether each element that names its pattern carries its slots, and its status words (`references/patterns.md`). P2 answers the cold-read questions from the screenshot before reading the dump.
- `shippable-text-auditor`, with the built file paths and the `meta.surface` value (`saas` or `lp`) only; the brief and the reasoning stay with you. It returns `remove` and `rewrite` findings.

Rule on each finding individually: delete the string where the finding is that it should go, rewrite it where the finding is about wording, and keep it only under the carve-out in `references/ui-copy.md`, naming the clause in the hand-over.

The verdicts are 不合格 (BLOCK), 条件付き合格 (CONCERNS) and 合格 (CLEAN). 条件付き合格 and 合格 pass once every finding is ruled on. 不合格, or any critical finding, sends this back to Step 3. Two returns at most; report anything still unresolved as an open question.

When the step cannot run, write `Step 5 skipped: <reason>` in the hand-over. When the Agent tool is available, still launch `shippable-text-auditor` as above. The measured part needs no agent: serve the output, capture each width, and run both scripts over the dumps.

```bash
SHOT={OUT}/1280.png DUMP={OUT}/1280.json node {SKILL_DIR}/scripts/render/cdp.js http://127.0.0.1:<port>/ 1280 > {OUT}/console-1280.txt &&
SHOT={OUT}/375.png DUMP={OUT}/375.json node {SKILL_DIR}/scripts/render/cdp.js http://127.0.0.1:<port>/ 375 > {OUT}/console-375.txt &&
python {SKILL_DIR}/scripts/render/check_render.py {OUT}/1280.json {OUT}/375.json --console {OUT}/console-1280.txt --console {OUT}/console-375.txt --tokens tokens.json --plan ui-brief.md --out {OUT}/measured.json --text
python {SKILL_DIR}/scripts/check_shippable_text.py --dom {OUT}/1280.json --json
```

Each state URL the brief names is captured the same way, into its own files (`{OUT}/confirm-1280.json`). A state that only an interaction reaches takes the script's third argument, a JavaScript expression run on the page before the dump: `node {SKILL_DIR}/scripts/render/cdp.js <url> 1280 "document.querySelector('form').requestSubmit()"`.

A capture that exits with a code other than 0 writes no dump: run it again before measuring, and set `CDP_TIMEOUT_MS` above its 60000 on a loaded machine. The `title` at the head of each dump names the page that was rendered; confirm it is this screen before reading the findings, since another server on the same port answers just as well. Fix what the scripts report as Step 4 does, look at both screenshots, answer the brief's cold-read, copy, reader-fit and structure questions against the built files, and list those answers in the hand-over as the author's own, unreviewed.

### Step 6: Hand over

List what was produced, any string kept under the carve-out with the clause it falls under, any size kept under the Latin-short allowance, and anything left open.

## REMOVE: stripping what already shipped

```bash
python {SKILL_DIR}/scripts/check_shippable_text.py <path> --json
```

Every finding is a deletion candidate here, warnings included.

1. Delete the whole element along with its string. A `<p class="hint">` emptied of its text still holds its margin.
2. Delete what the element leaves behind: the empty wrapper, the prop, the import, the class rule that has lost its last user.
3. Delete an annotation whole; a trimmed annotation is still an annotation. An ST7 run is raised to 14px or deleted, and the stylesheet rule that set it is fixed at its declaration (the finding names the selector).
4. Run `shippable-text-auditor` afterwards and delete what it returns. A `rewrite` verdict is deleted as well, unless the string names something the reader cannot get from the screen.
5. Keep a string only under an allowance named in `references/ban-list.md` (a constraint line under a field, a legend over an ambiguous encoding, a Latin-short run at 12px) and name the allowance in the hand-over.
6. Re-run the script until it reports only the strings kept that way, then run Step 4 in full.

## The hook

`hooks/ui_text_lint.py` is a PostToolUse hook in the plugin install; its reports carry the tag `[ui-text-lint]`. After every Write or Edit of a `.html`, `.htm`, `.css`, `.scss`, `.jsx`, `.tsx`, `.vue`, `.svelte` or `.astro` file, in any project, it runs `check_shippable_text.py --checks ST7,ST8,ST10` and reports the findings and the fix back to Claude. The write has already happened when it runs.

- **Error**: reported up to three times per file. Raise the size at the declaration it names, or delete the run, and write the file again.
- **Warning**: reported, and the write stands.
- **Skipped paths**: `node_modules`, `fixtures`, `vendor`, `dist`, `build`, `.git`, `*.min.*` and this plugin's own directory.
