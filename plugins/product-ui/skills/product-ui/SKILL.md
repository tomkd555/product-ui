---
name: product-ui
description: >-
  Builds web screens that read as a real product: tokens and wording settled before markup,
  shadcn/ui on Tailwind v4 or DADS or SmartHR, an OOUI or task-oriented structure chosen at intake, a test for whether each
  user-visible string should exist, text at 14px or more (12px for a short Latin-only run), checks and an independent review. REMOVE mode strips annotations and small text from an existing screen;
  lookup data answers palette, pairing, style, chart and stack questions.
  Use for any screen, component or UI wording, and when an interface reads as AI-made.
  trigger words: 画面, ページ, ランディングページ, ダッシュボード, デザイントークン, AIっぽい,
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

One entry point for building and reworking web interfaces. Every design decision lands in `tokens.json` — the colours, the type and the wording — and the result reaches the user once the check scripts and one independent reviewer have passed it. The lookup data under `scripts/lookup/` and `data/` comes from ui-ux-pro-max (`THIRD_PARTY_NOTICES.md`).

`{SKILL_DIR}` is the absolute path of this skill's directory: `<plugin root>/skills/product-ui` under the plugin, `~/.claude/skills/product-ui` under a manual install. Under the plugin the agents carry the `product-ui:` prefix (`product-ui:review-design-lead`) and the hook registers itself; a manual install uses the bare agent names. The commands say `python`; on macOS and Linux run `python3`.

## Principles

1. **Tokens before markup.** The tokens are settled first and the implementation reads only those variables, because "did this file use a value outside the token set" is checkable. Wording follows the same rule: `tokens.json` carries a `voice` block, and `check_copy.py` asks whether the implementation used it.
2. **A string exists only if a product writer could defend it.** A label labels, an error says what to do, an empty state says the list is empty. Text that explains the screen, describes the layout, defends a number or fills a slot is deleted.
3. **Text is 14px or more.** Body text is 16px. A Latin-only run of at most 24 characters (a unit, a timestamp, a code) may go to 12px. A string that only fits at 11px is deleted.
4. **Prohibitions live in scripts.** A rule written as "never do X" belongs in `check_slop.py`, `check_copy.py` or `check_shippable_text.py`, where a file can fail it.
5. **Review happens elsewhere.** Step 5 hands the rendered result to a reviewer who holds none of the context that produced it.

## Out of scope

This skill covers interactive screens. These belong to other tools:

- HTML documents, reports, and a dashboard that is a static report page
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

STANDARD escalates to DEEP once the surface spans more than one screen, and the escalation holds for the rest of the work. The first line of the reply after intake states the mode and the reason — `Mode: STANDARD — one new screen, tokens.json absent` — so the user sees the cost before any agent starts.

## Routing

| Request | Goes to |
|---|---|
| Whether a user-visible string should exist; stripping annotations, captions, helper text and small text | `references/ban-list.md`; the REMOVE mode |
| The words on a Japanese screen: labels, buttons, errors, empty states | `references/ui-copy.md` |
| The words on an English screen | `interfaces:better-writing`, with `references/ui-copy.md` for what the checks enforce |
| Which objects a product shows, their list and detail views, what the navigation lists, where an action sits | `references/ooui.md` |
| A shadcn component; dark mode; an accessible dialog, dropdown, form or table; a responsive layout in utility classes | `references/components.md` and the official documentation it links |
| Palettes, font pairings, visual styles, chart types, UX rules, per-stack rules | `references/lookup.md` and `scripts/lookup/search.py` |
| Building on the Digital Agency Design System | `references/dads.md` for the tokens, `references/dads-components.md` for the components |
| Building on the SmartHR Design System or smarthr-ui | `references/smarthr.md` for the tokens, SmartHR's own Claude Code plugin for the components |
| A new landing page or marketing site | `hallmark` for the page layout, this skill for tokens and checks |
| Polishing an existing interface | `interfaces:better-ui`, `interfaces:better-layout`, `interfaces:better-typography`, `interfaces:better-colors` |
| Whether motion belongs, and how it should feel | `emil-design-eng`; Apple-like gesture motion to `apple-design` |
| Finding places that should animate, auditing all motion, reviewing motion in a diff | `find-animation-opportunities`, `improve-animations`, `review-animations` (user-invoked) |
| Keyboard, focus, screen readers, accessible names | `interfaces:better-accessibility` |

When more than one row applies, tokens come first and review comes last; the order in between follows the request.

The external skills are published separately: `hallmark` at https://github.com/Nutlope/hallmark, the `interfaces` plugin at https://github.com/jakubkrehel/skills, and the motion skills at https://github.com/emilkowalski/skills. Where one is missing from the install, do that row's work in the main session and say so in the hand-over.

## Pipeline

When resuming interrupted work, decide the next step from which files exist, and from those alone: `tokens.json`, `theme.css`, the built output.

### Step 0 — Intake

Skip this step when `tokens.json` exists and the request is a local change.

Detect the existing stack (`package.json`, `tailwind.config.*`, an `@import "tailwindcss"`); a project with none takes the defaults in `references/stack-defaults.md`. Then ask at most four questions in one AskUserQuestion round:

- **Surface**: landing page or application.
- **Reference**: デジタル庁デザインシステム (`references/dads.md`) for public-sector sites, SmartHR (`references/smarthr.md`) for Japanese B2B SaaS dense with forms and tables, or なし, where the tokens come from the request or from a product the user names.
- **Structure**: オブジェクト指向 (OOUI) or タスク指向, recorded in `meta.structure` as `ooui` or `task`. Put first the one the table under "Choosing the structure" in `references/ooui.md` points to. A request that already names one settles it, and the question is left out.
- **Stack**: confirmation of what the detection found.

Settle everything else by default and record each default in `meta.defaults_applied`; `register` defaults to 敬体 and `katakana_choon` to `jtf`. Read the interface language off the project and spend no question on it.

### Step 1 — Settle the tokens

Write `tokens.json` in the shape `references/tokens-format.md` defines. `assets/tokens_example.json` is a filled-in example, and `assets/tokens_example.{dads,smarthr}.json` are the two presets.

- **Colours**: follow "Deriving the colours" in `references/tokens-format.md`. Route the arithmetic to `interfaces:better-colors` and the candidate palettes and pairings to `scripts/lookup/search.py` (`references/lookup.md`) before writing a value by hand.
- **Voice**: write `terms` for the product, one word per operation, reading the words already on existing screens first. `assets/voice_terms.ja.json` carries the 長音 pairs C9 checks.
- **Reference**: when `meta.reference` names a preset, copy that reference's mapping. For any other reference product, work from a screenshot and a written description of it together.

### Step 2 — Mechanical check on the tokens

```bash
python {SKILL_DIR}/scripts/validate_tokens.py tokens.json --json
python {SKILL_DIR}/scripts/generate_theme.py tokens.json
```

An error from `validate_tokens.py` sends this back to Step 1 before the generator runs. `generate_theme.py` writes `theme.css` beside `tokens.json`, with a `--text-*` scale that starts at `text-xs` (12px, Latin-short only) and `text-sm` (14px). Change `theme.css` only through `tokens.json` and the generator.

### Step 3 — Build

Follow the routing table. Colours, type, spacing, radius, shadow and motion come from `theme.css` variables only; components follow `references/components.md` or the preset's component reference.

When `meta.structure` is `ooui`, work through the three steps in `references/ooui.md` before any markup, and keep the object table for the Step 5 brief.

Read `references/ban-list.md` and `references/ui-copy.md` before writing any string a user will see. The ban list settles whether a string exists and how small text may be; ui-copy.md settles how a string that exists is worded. When the brief gives no real content for a slot, leave `[TODO: …]` in a source comment and ask the user one question; prose invented to fill a slot is a defect.

### Step 4 — Mechanical checks on the output

```bash
python {SKILL_DIR}/scripts/check_slop.py <path> --json
python {SKILL_DIR}/scripts/check_copy.py <path> --emit-prose copy-prose.md --json
python {SKILL_DIR}/scripts/check_shippable_text.py <path> --json
```

```bash
npx textlint --config {SKILL_DIR}/assets/textlintrc.ui.json copy-prose.md
```

- **Errors**: an error from any of the three scripts sends this back to Step 3.
- **Warnings**: rule on each `check_shippable_text.py` warning: delete the annotation, or keep it and name its allowance in the hand-over. Delete text that explains the design or the way through the screen at either severity.
- **textlint**: it covers the prose-shaped strings `check_copy.py` writes to `copy-prose.md`. Fix each finding; deleting the string counts as a fix, and a string under the carve-out in `references/ui-copy.md` stays. textlint is optional: the plugin leaves its install to the user, and the README names the npm packages. When `npx textlint` is unavailable, skip it and write `textlint skipped: not installed` in the hand-over; the three Python scripts still gate.
- **Misfires**: silence a misfire of `check_slop.py` or `check_copy.py` in the file itself, as `product-ui: ignore <ID> <reason>` or `product-ui: ignore-file <ID> <reason>` (forms in `references/slop-checklist.md` and `references/ui-copy.md`). Suppress only a misfire; fix a string the check read correctly. Fix every `check_shippable_text.py` error, because that script reads no suppression form.

Step 5 starts once no finding remains.

The Step 2 and Step 4 scripts exit 0 on pass and 1 on failure, and print readable output when `--json` is omitted; `check_shippable_text.py` exits 2 when a directory holds no file in scope. `check_slop.py` finds `theme.css` beneath the paths, then up to four directories above them. `check_copy.py` finds `tokens.json` in the directory holding the paths, then up to three directories above it; `--tokens` names the file directly. `check_shippable_text.py` reads `meta.surface` from the nearest `tokens.json` for ST3 (`--surface lp|saas` overrides). It takes `--checks <IDs>` to run a subset, `--css <file.css>` to add a stylesheet to the cascade, and `--dom <dump.json>` to judge a `cdp.js` dump.

When a check fails, read the reference that owns its ID:

| IDs | Script | Reference |
|---|---|---|
| T1–T17 | `validate_tokens.py` | `references/tokens-format.md` |
| S1–S10 | `check_slop.py` | `references/slop-checklist.md` |
| C1–C17 | `check_copy.py` | `references/ui-copy.md`; `references/ooui.md` for C17 |
| ST1–ST10 | `check_shippable_text.py` | `references/ban-list.md` |

### Step 5 — Independent review

The step needs a renderable entry point, Node 22 or later, a Chrome install and the Agent tool.

Write `ui-brief.md` beside `tokens.json` from `assets/brief.template.md`: the screen's purpose in one sentence, the paths, the surface type, whether controls are wired, and the seven copy questions. When `meta.structure` is `ooui`, fill the template's Structure section with the object table from Step 3 and keep its five structure questions; otherwise delete that section.

Then launch both agents in one message, each with `model: opus`:

- `review-design-lead`, with `plan: ui-brief.md`, `target:` the project directory, and `scripts: {SKILL_DIR}/scripts/render`; it requires all three and returns `{"error": …}` when one is missing. It renders through headless Chrome at 1280px and 375px and measures the page with `check_render.py` (R1–R11). R7 measures the computed text size, which covers a size set from JavaScript or a transform.
- `shippable-text-auditor`, with the built file paths and the `meta.surface` value (`saas` or `lp`) only; the brief and the reasoning stay with you. It returns `remove` and `rewrite` findings.

Rule on each finding individually: delete the string where the finding is that it should go, rewrite it where the finding is about wording, and keep it only under the carve-out in `references/ui-copy.md`, naming the clause in the hand-over.

The verdicts are 不合格 (BLOCK), 条件付き合格 (CONCERNS) and 合格 (CLEAN). 条件付き合格 and 合格 pass once every finding is ruled on. 不合格, or any critical finding, sends this back to Step 3. Two returns at most; report anything still unresolved as an open question.

When the step cannot run, write `Step 5 skipped: <reason>` in the hand-over, run `check_shippable_text.py --dom` over a `cdp.js` dump if one can be captured, and answer the brief's copy questions and structure questions against the built files.

### Step 6 — Hand over

List what was produced, any string kept under the carve-out with the clause it falls under, any size kept under the Latin-short allowance, and anything left open.

## REMOVE — stripping what already shipped

```bash
python {SKILL_DIR}/scripts/check_shippable_text.py <path> --json
```

Every finding is a deletion candidate here, warnings included.

1. Delete the whole element along with its string. A `<p class="hint">` emptied of its text still holds its margin.
2. Delete what the element leaves behind: the empty wrapper, the prop, the import, the class rule that has lost its last user.
3. Delete an annotation whole; a trimmed annotation is still an annotation. An ST7 run is raised to 14px or deleted, and the stylesheet rule that set it is fixed at its declaration (the finding names the selector).
4. Run `shippable-text-auditor` afterwards and delete what it returns. A `rewrite` verdict is deleted as well, unless the string names something the reader cannot get from the screen.
5. Keep a string only under an allowance named in `references/ban-list.md` — a constraint line under a field, a legend over a genuinely ambiguous encoding, a Latin-short run at 12px — and name the allowance in the hand-over.
6. Re-run the script until it reports only the strings kept that way, then run Step 4 in full.

## The hook

`hooks/ui_text_lint.py` is a PostToolUse hook in the plugin install; its reports carry the tag `[ui-text-lint]`. After every Write or Edit of a `.html`, `.htm`, `.css`, `.scss`, `.jsx`, `.tsx`, `.vue`, `.svelte` or `.astro` file, in any project, it runs `check_shippable_text.py --checks ST7,ST8,ST10` and reports the findings and the fix back to Claude. The write has already happened when it runs.

- **Error**: reported up to three times per file. Raise the size at the declaration it names, or delete the run, and write the file again.
- **Warning**: reported, and the write stands.
- **Skipped paths**: `node_modules`, `fixtures`, `vendor`, `dist`, `build`, `.git`, `*.min.*` and this plugin's own directory.
