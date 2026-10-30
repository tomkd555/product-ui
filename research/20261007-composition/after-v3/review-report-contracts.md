# Design review: 契約 (collection) after the rebuild (branch feat/compose-v3, `#/contracts?as=manager`)

Run by `review-design-lead` on 2026-10-07 against `ui-brief-contracts.md`. The text below is the lead's report as returned, condensed to the findings and the rulings the caller took.

Verdict: CONCERNS (0 CRITICAL, 6 WARNING after corroboration)

## Findings and rulings
| # | Severity | Location | Evidence | Ruling |
|---|---|---|---|---|
| 1 | WARNING | the table at 375 | All six columns scroll sideways inside the wrapper; 満期, the 要対応 badge and 意向 sit off-screen with a faint scroll cue. | Fixed: the table stacks below 640px with the stylesheet's existing `max-sm` utilities. |
| 2 | WARNING | the filter controls at 375 | About 470px of controls come before the first contract. | Fixed: the three selects share one three-column row below 40rem. |
| 3 | WARNING | table rows at 1280 | Rows run 77 to 109px tall because 満期 stacks three lines. | Fixed: date, 「あとNか月」 and the badge share one line. |
| 4 | WARNING | the 意向 column | The widest column (321px) shows 「未確認」 on 71 of 84 rows while 満期 wraps. | Fixed: 意向 capped at 200px. |
| 5 | WARNING | the filter row at 1280 | The selects drop to a second row against the brief's "one row". | Fixed: count buttons, selects and the search share one row; the search takes the remaining width. |
| 6 | WARNING | the 意向 select against the column values | The select offers the three groups; the cells show product-specific wording; the count button adds a third form. | Fixed in part: the count button takes the group name 「新車に乗り換える」. The cells keep the product wording and the select the group names, as the requirements set them (§4 S07 and §7 intentions). |
| 7 | NOTE | a 22x22 div near the chart | Measured hit area under 24px. | Left: the verifier of the 実績 review found the same node to be a passive chart wrapper. |
| 8 | NOTE | the 要対応 badge as the only row cue | Flagged rows read as taller rows. | Left for a later pass. |
| 9 | NOTE | two contract searches | Header and in-page search with different field lists. | Left: the header search is the requirements' C03. |
| 10 | NOTE | the chart window | The chart left out the month marked 「あと24か月」. | Fixed: the window is 25 months. |
| 11 | NOTE | th 担当 | voice.terms maps 担当者 to 営業スタッフ. | Fixed: 営業スタッフ. |
| 12 | NOTE | 車種 cell wraps 'STEP WGN' | | Fixed: nowrap. |
| 13–18 | NOTE | control widths at 375, sticky header height, 使い方ガイド link width, chart labels at 375, filter group edges, control heights | | Left for a later pass. |
| 19 | NOTE | h2 「契約の一覧 84件」 restates the h1 and the 「すべて 84」 button | | Fixed: 「満期が近い順の契約」 without a count. |
| 20 | NOTE | all bars one blue | | Left. |
| 21 | NOTE | only the customer name opens the contract | | Left: the name link is the row's entry, as on the other collections. |
| 22 | NOTE | the HC-… number has no label and three names across placeholders | | Left for a later pass. |

## Scope covered
P0 measured four captures (524 and 516 text elements, 89 controls, 3 headings), with only the 22px div firing. P1 read all four screenshots, the 1280, 375 and dark-1280 dumps and the stylesheet. P2's cold read: the eye lands on the selected 「すべて 84」 then the table; two to three emphasis levels; the stop order matches the brief; four count buttons, each a filter the brief names; groups separated by distance; no tile run; the content specific to contracts; the density missed "dense rows" (fixed above). P3: copy questions 1 yes, 2 and 6 unrenderable, 3 yes, 4 no (the chart window, fixed), 5 no (意向 vocabulary, 担当, the HC number), 7 yes; structure questions all yes.

The lead noted that `check_render.py --plan` read the job class of the first block (ホーム, monitor) for this lookup screen; the reader now takes the block whose route matches the Built files line.
