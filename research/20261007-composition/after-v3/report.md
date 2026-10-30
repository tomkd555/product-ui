# 販社ポータル V3 rebuilt on the composition plan (2026-10-07)

Branch `feat/compose-v3` in the worktree `C:\Mycode\ClaudeCode\hansya_Portal_V3-compose`, unmerged. The user asked for the whole mock on a separate branch after the Home-only rebuild; this directory holds the evidence.

## What changed

- `src/ui-brief.md`: one Composition block per screen (23 blocks), the reader groups, the cold-read, copy and reader-fit questions, the Structure table. `src/tokens.json` carries `meta.users` (three groups, `basis: assumed`) and the dark border at L 32%; `muted_foreground` moved to L 52% so 14px text on the ground reaches 4.5:1.
- `src/components/ui.tsx`: `Section`, `Figure` (`hero` and `small`), `FigureRow`; `Kpi` and `KpiRow` retired; `Gone` and `NoAccess` without a card.
- Every screen under `src/screens/`: sections on the page ground; a hero figure with small figures beside it on the monitor screens (ホーム, 実績, RMコメント, スタッフ single); counts as `.count-filters` buttons or a `.facts` line on lookup and enter screens; cards kept for the vehicle cards, the comparison tray, the customer-facing plan cards and the login form.
- `portal-v3-screens.md`: the KPI rule of 2.3 became the composition rule, and the view blocks name figures and sections.

## Measurements

| Run | R12 nested | R13 spacing | R14 emphasis | R15 equal tiles | Other |
|---|---|---|---|---|---|
| before (original tree, home and market) | none | none | none | 1 WARNING (market, 4 tiles of 220x139 under a lookup plan) | R1 4.42:1 muted text, R2 and R5 |
| after, 27 captures of 23 screens | none | none | none | none | R5 only (a 22x22 chart wrapper, judged passive by a verifier) |

Source checks after: `check_slop.py` 0/0, `check_copy.py` 0/0 over 338 strings, `check_shippable_text.py` 0 errors and the pre-existing ST10 warning on `.nav-badge` (a Latin-only count). `validate_tokens.py` 0 errors, the two T5 warnings the preset records.

## Independent reviews

| Screen | Before | After | Surviving WARNINGs after the fix commit |
|---|---|---|---|
| ホーム | BLOCK (the equal tiles as CRITICAL, corroborated) | CONCERNS, 1 WARNING | 0: the hero kicker and compare line now carry the month and 契約／目標 alone |
| 契約 | not reviewed | CONCERNS, 6 WARNING | 1 in part: the 意向 cells keep the product wording the requirements set |
| 実績 | not reviewed | CONCERNS, 6 WARNING | 1 in part: 「95%区間」 stays in table headers, as the requirements set (§7) |

The 実績 review found two statements that were untrue (「弱い関連」 at p 0.205; 「全販売店420名」 without its population); both are fixed. The reports are `review-report-home.md`, `review-report-contracts.md`, `review-report-results.md`; the before report is `../before/review-report.md`.

## Left for a later pass

- Chart details at 375 (legend wrapping, tick spacing), the header search against the in-page search, the row cue for 要対応 rows, the three names of the contract number across placeholders, the two account avatars in the shell.
- `voice.terms` holds 管理帯 → 管理限界 while the screens say いつもの範囲 (the requirements' UI name).
- Only the 今月 period of 実績 and the manager account were captured for most screens.

## What the run taught the skill

- `--plan` must read the block of the captured screen: fixed in `check_render.py` (the block whose route matches the Built files line).
- A divider line is no enclosure: `cdp.js` counts a box from two border sides, a fill or a shadow.
- A tint of a token is on-token, and a translucent background is composited over its base: `check_render.py` R2 and R1.
- The harness returns a subagent's report as text, so the lead's `report.md` is written by the caller.
