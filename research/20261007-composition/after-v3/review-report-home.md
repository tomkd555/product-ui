# Design review: ホーム after the rebuild (branch feat/compose-v3, `#/?as=advisor`)

Run by `review-design-lead` on 2026-10-07 against `ui-brief-home.md`. The text below is the lead's report as returned.

Verdict: CONCERNS (0 CRITICAL and 1 WARNING survived corroboration)

## Findings
| # | Perspective | Severity | Location | Evidence | Fix | Corroboration |
|---|---|---|---|---|---|---|
| 1 | P2, P3 | WARNING | hero `p.section-kicker` and `span.figure-compare` | The kicker reads 「世田谷店・2026年10月」 and sits directly above the personal figure 「マイ目標まで あと 2件」. The compare line reads 「目標 9件・世田谷店のペネトレーション 38.6%（前年同月 41.5%）」, so one sentence mixes the personal target with the store's penetration. A reader can take あと 2件 to be the store's gap. | Kicker: 「2026年10月」. Compare line: 「契約 7件／目標 9件」. Move the store ペネトレーション to the manager version. | upheld (medium) |
| 2 | P2, P3 | NOTE | お知らせ `span.nav-badge` vs `h2#notice-heading span.count` | The sidebar badge shows 「2」 (要対応); the pane heading reads 「未読のお知らせ 3件」. Sighted users see nothing that names what the badge counts. | A visible cue for the badge's meaning. | upheld, lowered from WARNING |
| 3 | P2 | NOTE | hero link and 要対応 rows | In-app links render as bold text; the only cue is 「↗」, which usually means an external link. | A trailing 「›」 on the rows and the hero; replace 「↗」. | upheld, lowered from WARNING |
| 4 | P2 | NOTE | `ul.rows` in 要対応 | The contract row, the most important for the 営業スタッフ job, comes last. | Put 満期3か月以内で意向未確認の契約 first. | upheld, lowered from WARNING |
| 5 | P1 | NOTE | 最終更新 line at 375 | The line breaks inside the date. | Wrap the date and time in one nowrap span. | not corroborated |
| 6 | P1 | NOTE | dark hairlines | Dark `--brand-border` oklch(26.1%) on the surface oklch(23.2%) is barely visible. | Raise the dark border to about 32–34% lightness. | not corroborated |
| 7 | P1 | NOTE | hero link vs 「↗」 | The cue sits beside the label, outside the link. | Put the label and the value in one link, or move the cue next to the value. | not corroborated |
| 8 | P2 | NOTE | 「要対応 5件」 | The 5 adds three different objects. | Drop the summed count. | not corroborated |
| 9 | P2 | NOTE | 要対応 rows at 1280 | Label and count sit about 420px apart in a 611px row. | Cap the list width, or move the count next to the label. | not corroborated |
| 10 | P2 | NOTE | header 「佐」 vs sidebar avatar | The same account appears twice in different styles. | Same shape and colour; a caret on the header button. | not corroborated |
| 11 | P3 | NOTE | hero link name 「あと 2件」 | The link's name gives a value, not where it goes. | Name the link by 「マイ目標まで」 plus the value. | not corroborated |
| 12 | P3 | NOTE | header search | The accessible name is 「契約を検索」, the placeholder lists 車種. | Placeholder naming the object. | not corroborated |
| 13 | P3 | NOTE | nav item 「マイ目標」 | A role shortcut to the スタッフ single view. | Record it in the brief as a settled exception. | not corroborated |
| 14 | P3 | NOTE | `h1` 「ホーム」 | Repeats the navigation name. | Naming point only. | not corroborated |

## Rejected findings
| Finding | Why it was rejected |
|---|---|
| P3-2 (WARNING): the header button 「佐」 has only the initial as its name | The bundle gives the button `aria-label` `${name}のメニュー` and hides the initial; the dump marks the control as labelled. |

## Scope covered
| Perspective | Scope | Out of scope |
|---|---|---|
| P0 Measured | 4 dumps (1280, 375, dark-1280, dark-375): 54 text elements, 22 controls, 3 headings each; 17 token colours; plan job class monitor. 0 findings. | none |
| P1 Rendering soundness | 4 screenshots, the 1280 and 375 dumps: overlap, alignment (2:1 pane, 40px gaps), reflow at 375, glyphs, Japanese line breaking, dark legibility. | The minified CSS bundle and the dark dumps; off-canvas drawer tab order. |
| P2 Information design | Cold read from the screenshots: the eye lands on the hero 「あと 2件」 (the dominant element); the first four stops match the reading order; 3 or more emphasis levels survive; no equal-tile row; spacing matches the brief's steps; dark keeps the hierarchy. | Hover, focus and disabled styles. |
| P3 Conformance | The ホーム block: hero Figure, compare line, 要対応 with its count, 未読のお知らせ at 3 rows, Updated line, shell; tiles and panels omitted as briefed; controls wired (R10 empty). | The JS bundle; single views beyond お知らせ. |

Copy questions: 1 no (the hero link is named by its value); 2 no error state rendered; 3 yes, h1 generic; 4 no (rows 1 and 2); 5 yes, except the search field's name and placeholder; 6 no empty state rendered; 7 yes. Structure questions: 1 yes, マイ目標 a role shortcut; 2 yes; 3 navigation only; 4 yes; 5 none.

## Summary
The most important fix is the hero's scope: the kicker and the compare line give store figures beside the advisor's personal 「あと 2件」. All four perspectives ran on light and dark captures at 1280 and 375. No CRITICAL survived.
