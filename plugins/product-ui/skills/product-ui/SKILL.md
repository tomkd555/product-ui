---
name: product-ui
description: >-
  Builds web screens that read as a real product: tokens and wording settled before markup,
  shadcn/ui on Tailwind v4 or DADS or SmartHR, a test for whether each
  user-visible string should exist, text at 14px or more (12px for a short Latin-only run), checks and an independent review. REMOVE mode strips annotations and small text from an existing screen;
  lookup data answers palette, pairing, style, chart and stack questions.
  Use for any screen, component or UI wording, and when an interface reads as AI-made.
  trigger words: 画面, ページ, ランディングページ, ダッシュボード, デザイントークン, AIっぽい,
  ダサい, 文字が小さい, 文言, ラベル, エラーメッセージ, UIライティング, マイクロコピー,
  説明っぽい, 説明文が入る, 注釈だらけ, 注記だらけ, キャプション, ヘルプテキスト, 補足テキスト,
  小さい文字の説明, 注釈を消して, 但し書き, 手法の説明, サブテキストを削除, 説明文を消して,
  配色, パレット, フォントの組み合わせ, スタイル, グラスモーフィズム, チャート, DADS, SmartHR,
  UI copy, microcopy, helper text, caption, self-describing UI, shippable copy, palette,
  font pairing, chart type, design style.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill, Agent
---

# product-ui

One entry point for building and reworking web interfaces. Every design decision lands in `tokens.json` — the colours, the type, and the wording — and nothing reaches the user until the check scripts and one independent reviewer have passed it. Incorporates lookup data from ui-ux-pro-max (see `THIRD_PARTY_NOTICES.md` at the plugin root, or in this skill's directory under a manual install); it lives under `scripts/lookup/` and `data/` and is reached from the routing table below.

Read `{SKILL_DIR}` below as the absolute path of this skill's directory: `<plugin root>/skills/product-ui` under the plugin, `~/.claude/skills/product-ui` under a manual install. Under the plugin the agents are `product-ui:review-design-lead`, `product-ui:review-design-auditor`, `product-ui:review-verifier` and `product-ui:shippable-text-auditor`, and the hook in `hooks/` registers itself; under a manual install the agents carry the same names without the `product-ui:` prefix. The commands below say `python`; on macOS and Linux run them with `python3`.

## Principles

1. **Tokens before markup.** A model told not to use a colour returns to it on the next generation. "Did this file use a value outside the token set" is checkable, so the tokens are settled first and the implementation reads only those variables. The same holds for wording: `tokens.json` carries a `voice` block, and `check_copy.py` asks whether the implementation used it.
2. **A string exists only if a product writer could defend it.** A label labels, an error says what to do, an empty state says the list is empty. Text that explains the screen, describes the layout, defends a number or fills a slot does not ship. `references/ban-list.md` names each ban and is read before any string is written.
3. **Nothing below the minimum size.** Body text is 16px, and no text is under 14px, except a Latin-only run of at most 24 characters (a unit, a timestamp, a code), which may go to 12px. The rule is enforced three times: at generation by the ban list, after every write by the `ui-text-lint` hook, which reports errors back to Claude, and after rendering by `check_render.py` R7. A string that only fits at 11px is deleted, not shrunk.
4. **Prohibitions live in scripts, not prose.** Anything written as "never do X" belongs in `check_slop.py`, `check_copy.py` or `check_shippable_text.py`. A rule nobody can fail is a rule nobody follows.
5. **Review happens elsewhere.** Step 5 hands the rendered result to a reviewer with none of the context that produced it. Self-review is not review.

## Out of scope

This skill covers interactive screens. These belong to other tools:

- HTML documents, reports, and a dashboard that is a static report page with no interaction
- Personas, journey maps, usability tests
- Logos, CIP, icon and social image generation
- PowerPoint decks

## Modes

| Mode | Condition | What runs | Cost |
|---|---|---|---|
| LIGHT | One local change to an existing screen, with tokens already in place | Steps 3 and 4 only | scripts only, no agent |
| STANDARD | A new screen or page, or a redesign | Steps 0 through 6 | one review round: `review-design-lead` plus `shippable-text-auditor` |
| DEEP | A whole product surface, or the user asks for thoroughness | Steps 0 through 6, plus Step 5 on every distinct screen | one review round per screen |
| REMOVE | The screen exists and carries annotations or small text: 「注釈を消して」「サブテキストを削除して」「文字が小さい」 | The REMOVE procedure below, then Step 4 | scripts plus the auditor |

Work that starts as STANDARD escalates to DEEP once the surface turns out to span more than one screen. It never de-escalates. The first line of the reply after intake states the mode and the reason — `Mode: STANDARD — one new screen, tokens.json absent` — so the user sees the cost before any agent starts.

## Routing

| Request | Goes to | Typical wording |
|---|---|---|
| Whether a user-visible string should exist at all; stripping annotations, captions, helper text and small text | `references/ban-list.md`; the REMOVE mode | 「説明っぽい文字を消して」「注釈だらけ」「但し書きを消して」「文字が小さい」 |
| The words on a Japanese screen — labels, buttons, errors, empty states | `references/ui-copy.md` | 「文言を直して」「ラベルがしっくりこない」 |
| The words on an English screen | `interfaces:better-writing`, with `references/ui-copy.md` for what the checks enforce | 「英語のUI文言を見て」 |
| Installing or adapting a shadcn component; dark mode; an accessible dialog, dropdown, form or table; a responsive layout in utility classes | `references/components.md` and the official documentation it links | 「Dialog を追加して」「ダークモードを付けて」 |
| Palettes, font pairings, visual styles, chart types, UX rules, per-stack rules (22 stacks) | `references/lookup.md` and `scripts/lookup/search.py` | 「配色の候補を出して」「フォントの組み合わせ」「SwiftUI ではどう書く」 |
| Building on the Digital Agency Design System | `references/dads.md` for the tokens, `references/dads-components.md` for the components | 「デジタル庁デザインシステムで」「行政のサイトとして」 |
| Building on the SmartHR Design System or smarthr-ui | `references/smarthr.md` for the tokens, SmartHR's own Claude Code plugin for the components | 「SmartHR のデザインシステムで」 |
| A new landing page or marketing site | `hallmark` for structure, this skill for tokens and checks | 「ランディングページを作って」 |
| Polishing an existing interface | `interfaces:better-ui`, `interfaces:better-layout`, `interfaces:better-typography`, `interfaces:better-colors` | 「野暮ったい」「余白を整えて」 |
| Whether motion belongs, and how it should feel | `emil-design-eng`; Apple-like gesture motion to `apple-design` | 「アニメーションを付けるべきか」 |
| Finding places that should animate, auditing all motion, reviewing motion in a diff | `find-animation-opportunities`, `improve-animations`, `review-animations` (user-invoked) | 「動かせるところある？」 |
| Keyboard, focus, screen readers, accessible names | `interfaces:better-accessibility` | 「キーボード操作を確認して」 |
| Charts and data display | `references/lookup.md` (`--domain chart`) for the chart type; the chart library through `references/components.md` | 「グラフを作って」 |

The external skills this table names are published separately: `hallmark` at https://github.com/Nutlope/hallmark, the `interfaces` plugin (`interfaces:*`) at https://github.com/jakubkrehel/skills, and `emil-design-eng`, `apple-design`, `find-animation-opportunities`, `improve-animations` and `review-animations` at https://github.com/emilkowalski/skills. Where one is not installed, do that row's work in the main session and say so in the hand-over.

When more than one row applies, tokens come first and review comes last; the order in between follows the request.

## tokens.json

```json
{
  "meta": { "name": "…", "surface": "saas|lp", "reference": "…|null",
            "stack": { "renderer": "…", "tailwind": "4", "base": "…" },
            "defaults_applied": [] },
  "color": { /* nine required keys, all oklch(), plus the optional surface */ },
  "color_dark": { /* optional, a subset of color */ },
  "typography": { "display": {…}, "body": {…}, "scale": { "ratio": 1.25, "base_px": 16 } },
  "spacing": {…}, "radius": {…}, "shadow": {…}, "motion": {…},
  "voice": { "lang": "ja", "register": "敬体", "button_form": "…",
             "katakana_choon": "jtf", "case": null,
             "terms": { "使わない語": "使う語" }, "allow": [] }
}
```

`references/tokens-format.md` is the source of record for the fields and the validation rules; `typography.scale.base_px` is 16 to 18. `assets/tokens_example.json` is a filled-in example, and `assets/tokens_example.{dads,smarthr}.json` are the two presets.

## Pipeline

### Step 0 — Intake

Detect the existing stack first (`package.json`, `tailwind.config.*`, an `@import "tailwindcss"`), then ask at most three questions in one AskUserQuestion round: the surface (landing page or application), any product being used as a reference, and confirmation of what the detection found. Settle anything else by default and record each such decision in `meta.defaults_applied`.

The reference question offers the two presets first — デジタル庁デザインシステム (`references/dads.md`) for public-sector sites and SmartHR (`references/smarthr.md`) for Japanese B2B SaaS dense with forms and tables — and なし, where the tokens are derived from the request or from a reference product the user names.

Do not spend a question on the interface language; read it off the project. `register` defaults to 敬体 and `katakana_choon` to `jtf`; record both in `meta.defaults_applied`. Skip this step when `tokens.json` exists and the request is a local change.

### Step 1 — Settle the tokens

Write `tokens.json`. Derive the colours by the rules under "Deriving the colours" in `references/tokens-format.md`; route the arithmetic to `interfaces:better-colors` and the candidate palettes and pairings to `scripts/lookup/search.py` (`references/lookup.md`) before writing a value by hand. Settle `voice` in the same pass: write `terms` for the product, one word per operation, reading the words already on existing screens first; `assets/voice_terms.ja.json` carries the 長音 pairs C9 checks.

When `meta.reference` names a preset, copy that reference's mapping instead. For any other reference product, work from a screenshot and a written description of it together.

### Step 2 — Mechanical check on the tokens

```bash
python {SKILL_DIR}/scripts/validate_tokens.py tokens.json --json
python {SKILL_DIR}/scripts/generate_theme.py tokens.json
```

One error sends this back to Step 1, and the generator does not run. `generate_theme.py` writes `theme.css` beside `tokens.json` from `assets/theme.template.css`, including a `--text-*` scale that starts at `text-xs` (12px, Latin-short only) and `text-sm` (14px). Never edit `theme.css` by hand; change `tokens.json` and run the generator again.

### Step 3 — Build

Follow the routing table. Colours, type, spacing, radius, shadow and motion come from `theme.css` variables only; components follow `references/components.md` or the preset's component reference.

Read `references/ban-list.md` and `references/ui-copy.md` **before** writing any string a user will see. The ban list settles whether a string exists and how small text may be; ui-copy.md settles how a string that exists is worded. When the brief gives no real content for a slot, leave `[TODO: …]` in a comment, not on the screen, and ask the user one question; inventing prose to fill a slot is itself a defect.

### Step 4 — Mechanical checks on the output

```bash
python {SKILL_DIR}/scripts/check_slop.py <path> --json
python {SKILL_DIR}/scripts/check_copy.py <path> --emit-prose copy-prose.md --json
python {SKILL_DIR}/scripts/check_shippable_text.py <path> --json
```

```bash
npx textlint --config {SKILL_DIR}/assets/textlintrc.ui.json copy-prose.md
```

textlint is optional and this plugin does not install it; the README names the npm packages `assets/textlintrc.ui.json` needs. When `npx textlint` is unavailable, skip it and write `textlint skipped: not installed` in the hand-over — the three Python scripts still gate.

An error from any of the three scripts sends this back to Step 3. `check_shippable_text.py` resolves the size every text run gets through the stylesheets and reports ST7 for anything under the minimum, ST10 for a declaration under it, and ST1–ST6, ST8 and ST9 for text that should not exist; its warnings do not stop the pipeline but are ruled on one by one — delete the annotation, or keep it and name the allowance. Text that explains the design or the way through the screen is deleted whichever severity reported it. Do not start Step 5 while any finding remains.

`check_copy.py` covers the labels; textlint covers the prose-shaped strings written to `copy-prose.md`. Fix each textlint finding; deleting the string counts as a fix. The one exception is a string under the carve-out in `references/ui-copy.md`.

Silence a misfire of `check_slop.py` or `check_copy.py` in the file itself, as `product-ui: ignore <ID> <reason>` or `product-ui: ignore-file <ID> <reason>` (forms in `references/slop-checklist.md` and `references/ui-copy.md`). Suppress only a misfire; fix a string the check read correctly. `check_shippable_text.py` reads no suppression form: its errors are fixed, and each warning kept is named with its allowance in the hand-over.

### Step 5 — Independent review

`review-design-lead` ships in this plugin with `review-design-auditor` and `review-verifier`; it needs Node 22 or later and a Chrome install, and it finds its renderer and its measurement script through the `scripts:` line of its instruction. It takes three inputs — `plan:`, `target:` and `scripts: {SKILL_DIR}/scripts/render` — and returns `{"error": …}` when one is missing. Write `ui-brief.md` beside `tokens.json` from `assets/brief.template.md` first: the screen's purpose in one sentence, the paths, the surface type, whether controls are wired, and the seven copy questions listed at the tail of `references/ui-copy.md`.

Then launch both agents in one message, each with `model: opus`:

- `review-design-lead`, with `plan: ui-brief.md`, `target:` the project directory, and `scripts: {SKILL_DIR}/scripts/render`. It renders through headless Chrome (`scripts/render/cdp.js`) at 1280px and 375px and runs `scripts/render/check_render.py`, whose R7 measures the text-size minimum on the computed size — the check the source scripts cannot make for a size set from JavaScript or a transform.
- `shippable-text-auditor` (`agents/shippable-text-auditor.md` in this plugin), with the built file paths and the surface type (`application` or `landing`) and nothing else — not the brief, not the reasoning. It returns `remove` and `rewrite` findings.

Rule on each finding individually: delete the string where the finding is that it should not exist, rewrite it where the finding is about wording, and keep it only under the carve-out in `references/ui-copy.md`, naming the clause in the hand-over. 不合格 (BLOCK), or any critical finding, sends this back to Step 3. Two returns at most; report anything still unresolved as an open question.

When the step cannot run — Node or Chrome is missing, no renderable entry point, or no Agent tool — say so in the hand-over as `Step 5 skipped: <reason>`, run `check_shippable_text.py --dom` over a `cdp.js` dump if one can be captured, and answer the seven copy questions against the built files.

### Step 6 — Hand over

List what was produced, any string kept under the carve-out with the clause it falls under, any size kept under the Latin-short allowance, and anything left open.

## REMOVE — stripping what already shipped

Run when the screen exists and carries the annotations or the small text.

```bash
python {SKILL_DIR}/scripts/check_shippable_text.py <path> --json
```

Every finding is a deletion candidate here, warnings included: the user has asked for the annotations gone, so a warning is deleted unless step 5 below keeps it.

1. Delete the element, not the string alone. A `<p class="hint">` emptied of its text still holds its margin.
2. Delete what the element leaves behind — the wrapper with nothing else inside it, the prop, the import, the class rule nothing references any more.
3. Never shorten instead, and never shrink instead. A trimmed annotation is still an annotation; an ST7 run is raised to 14px or deleted, and the stylesheet rule that set it is fixed at its declaration (the finding names the selector).
4. Run `shippable-text-auditor` afterwards for the phrasings no pattern reaches, and delete what it returns; in this mode a `rewrite` verdict is deleted as well, unless the string names something the reader cannot get from the screen.
5. Keep a string only under an allowance named in `references/ban-list.md` — a constraint line under a field, a legend over a genuinely ambiguous encoding, a Latin-short run at 12px — and name the allowance in the hand-over.
6. Re-run the script until it reports nothing but the strings kept that way, then run Step 4 in full.

## The hook

`hooks/ui_text_lint.py` (registered by `hooks/hooks.json`) is a PostToolUse hook: it runs after every Write or Edit of a `.html`, `.htm`, `.css`, `.scss`, `.jsx`, `.tsx`, `.vue`, `.svelte` or `.astro` file, in any project, with `check_shippable_text.py --checks ST7,ST8,ST10`. The write has already happened when it runs. An error is reported back to Claude with the findings and the fix, up to three times per file; a warning is reported back to Claude as well, and the write stands. `node_modules`, `fixtures`, `vendor`, `dist`, `build`, `.git`, `*.min.*` and this plugin's own directory are skipped. The hook covers screens built by other skills too, because it runs outside this pipeline.

When the hook reports an error: raise the size at the declaration it names, or delete the run, and write the file again.

## Gates

| Gate | Passes when | Otherwise |
|---|---|---|
| Step 2 | `validate_tokens.py` exits 0 | back to Step 1 |
| Step 4 | `check_slop.py`, `check_copy.py` and `check_shippable_text.py` all exit 0, every textlint finding is fixed, and every `check_shippable_text.py` warning is ruled on | back to Step 3 |
| Step 5 | 合格 (CLEAN) or 条件付き合格 (CONCERNS), and every `shippable-text-auditor` finding ruled on | back to Step 3, twice at most |

Verdicts: 不合格 (BLOCK) / 条件付き合格 (CONCERNS) / 合格 (CLEAN). When resuming interrupted work, decide the next step from which files exist — `tokens.json`, `theme.css`, the built output — not from the conversation.

The Step 2 and Step 4 scripts exit 0 on pass and 1 on failure (`check_shippable_text.py` exits 2 when a directory holds no file in scope), and print readable output when `--json` is omitted. `check_slop.py` locates `theme.css` on its own: it searches beneath the paths first, then up to four directories above them. `check_copy.py` looks for `tokens.json` only upward: in the directory holding the paths, then up to three directories above it (`--tokens` names the file directly); `check_shippable_text.py` reads `meta.surface` from the nearest `tokens.json` for ST3 (`--surface lp|app` overrides), takes `--checks <IDs>` to run a subset, `--css <file.css>` to add a stylesheet to the cascade, and `--dom <dump.json>` to judge a `cdp.js` dump.

## Files

| File | Holds | Read it |
|---|---|---|
| `references/ban-list.md` | The generation-time bans, the text-size minimum, and checks ST1–ST10 with their thresholds and allowances | Step 3, before writing any user-visible string; REMOVE mode; when a check fails |
| `references/ui-copy.md` | How a Japanese interface words a button, a label, an error and an empty state; the English consensus; checks C1–C16; the carve-out; the seven copy questions | Step 3 and Step 4 |
| `references/tokens-format.md` | `tokens.json` fields, how the colours are derived, rules T1–T17 | Step 1, and when a token check fails |
| `references/slop-checklist.md` | Checks S1–S10 and their allowances | Step 4, and when a check misfires |
| `references/stack-defaults.md` | The default stack, the Tailwind v4 two-tier arrangement, the reasons to move off it | Step 0 and Step 1 |
| `references/components.md` | shadcn/ui on Base UI with Tailwind v4: setup, the rules every component keeps, the patterns, and links to the official shadcn/ui, Base UI and Tailwind documentation | Step 3, for component work |
| `references/lookup.md` | How to search `data/` for palettes, pairings, styles, charts, UX rules and per-stack rules | Step 1 and Step 3 |
| `references/dads.md`, `references/dads-components.md` | The Digital Agency Design System: tokens, and the 45 React / 42 HTML components with the copying procedure | Whenever `meta.reference` names it |
| `references/smarthr.md` | The SmartHR Design System and smarthr-ui | Whenever `meta.reference` names it |
| `scripts/check_shippable_text.py` | ST1–ST10, `--dom`, `--checks` | Step 4, REMOVE, the hook |
| `scripts/lookup/search.py` | The lookup CLI over `data/` | Through `references/lookup.md` |
| `agents/shippable-text-auditor.md` | The existence auditor, opus, reads the built text cold | Step 5 and REMOVE |
| `agents/review-design-lead.md`, `review-design-auditor.md`, `review-verifier.md`; `scripts/render/` | The rendered review: the lead, its auditors, the verifier, `cdp.js` and `check_render.py` (R1–R11) | Step 5 |
| `hooks/ui_text_lint.py`, `hooks/hooks.json` | The PostToolUse hook and its registration | When the hook reports an error |
