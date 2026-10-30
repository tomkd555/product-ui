# Design review: 販売店 single, tab 実績 after the rebuild (branch feat/compose-v3, `#/stores/s1?as=manager`)

Run by `review-design-lead` on 2026-10-07 against `ui-brief-results.md`. The text below is the lead's report as returned.

Verdict: CONCERNS (0 CRITICAL and 6 WARNING remain after corroboration; the only CRITICAL, P3-1, was upheld but lowered to WARNING)

## Findings
| # | Perspective | Severity | Location | Evidence | Fix | Corroboration |
|---|---|---|---|---|---|---|
| 1 | P3 | WARNING | section 月別の契約明細 | The brief's reading order lists 月別の契約明細 with no condition; the bundle renders it only when the period covers more than one month, and the capture ran under 今月. | Record the more-than-one-month condition in the brief's block. | upheld; lowered from CRITICAL |
| 2 | P1, P2 | WARNING | .figure-row, figure 契約件数, 1280 | The hero, 前年同月 and バリ保 share the first row; 契約件数 wraps under the hero and the tops sit at three y values. | A hero column plus small figures sharing one top edge, or a smaller column gap. | upheld |
| 3 | P3 | WARNING | 「年代と商品：弱い関連」 | The disclosure gives p 0.205 and Cramér's V 0.11, while 販売店の比較 calls p 0.954 「誤差の範囲です」. The copy claims an association the test does not support. | 「年代による商品の違いは誤差の範囲です」. | upheld |
| 4 | P3 | WARNING | h2#customer-mix count 「全販売店420名」 | The section names its store scope and no period; 420 cannot be this month's figure (this month's 新車販売台数 across the stores is 280). | Name the period or the population in the count. | upheld |
| 5 | P3 | WARNING | th 「95%区間」 | The compare lines say 「95%信頼区間」, the table headers 「95%区間」, for the same interval. | One term, or register the short form. | upheld |
| 6 | P3 | WARNING | button 「実績を書き出す」 | The brief's Structure row for 販売店 lists no export. | Add it to the 販売店 actions and name the format, or remove the button. | upheld |
| 7 | P0 | NOTE | pressed segment button in dark | `color-mix(in oklch, var(--color-foreground) 18%, var(--color-surface))` matches no token. | A named token for the pressed fill. | upheld; lowered to NOTE |
| 8 | P1 | NOTE | tab 「RMコメント」 at 375 | The fourth tab is cut at the content edge; the row scrolls without a cue. | Smaller tab padding or an edge fade. | upheld; lowered to NOTE |
| 9 | P2 | NOTE | h2 販売店の比較 and the verdict | The verdict sentence is 18px/700 like the heading, so the two read as two headings. | 16px/600 for the verdict. | upheld; lowered to NOTE |
| 10 | P3 | NOTE | 「いつもの範囲」 | voice.terms maps 管理帯 to 管理限界; the page uses いつもの範囲. | Register いつもの範囲 as the reader-facing name. | upheld; lowered to NOTE |
| 11 | P1, P3 | NOTE | details 「率の差と効果量」 | 「−0.4pt」 uses U+2212, other negatives the hyphen-minus. | One formatter. | not corroborated |
| 12 | P1 | NOTE | monthly trend legend at 375 | The legend item 実績 wraps alone; the x axis drops 8月. | Shorter labels; fixed tick interval. | not corroborated |
| 13 | P2 | NOTE | buttons 実績を書き出す / 直近12か月で比べる | Both share one secondary style; at 375 the export button takes its own row. | A primary style for 直近12か月で比べる. | not corroborated |
| 14 | P2 | NOTE | h2 お客様属性別の商品構成 | The 全販売店 scope appears only as a muted count. | The scope in the heading or a kicker. | not corroborated |
| 15 | P2 | NOTE | dl under the monthly trend | Two dd weights in one list. | One weight per role. | not corroborated |
| 16 | P2 | NOTE | the last four sections | Same shape and weight; nothing marks the verdict section as the one to act on. | Mark the verdict section as the lead of the lower half. | not corroborated |
| 17 | P2 | NOTE | figure values with 「↗」 | Figure links are plain dark text with a small arrow; table links are blue. | One link style; ↗ only for links that leave the page. | not corroborated |
| 18 | P3 | NOTE | hero label 「ペネトレーション」 | The brief names it 「ペネトレーション（全商品）」; the バリ保 figure beside it is also a penetration. | 全商品 in the kicker. | not corroborated |
| 19 | P3 | NOTE | 「いつもより多い／少ない」 | The series is a rate. | 「いつもより高い／低い」. | not corroborated |
| 20 | P3 | NOTE | disclosure labels 「χ²とCramér's V」「率の差と効果量」 | They name the computation. | Label by what the reader checks. | not corroborated |
| 21 | P3 | NOTE | figure links | The link text is a number and an arrow; four links lead to four kinds of destination. | Accessible names naming the destination. | not corroborated |
| 22 | P3 | NOTE | 「前年同月のペネトレーション」 and the option 「前年同期比較」 | Two names for one comparison. | 前年同月 for one month, 前年同期 otherwise, in both places. | not corroborated |

## Rejected findings
| Finding | Why it was rejected |
|---|---|
| R-1 (P0, WARNING): div with a 22x22 hit area | Passive wrapper nodes inside the charts; every operable control meets 24px. |
| P1-1 (P1, WARNING): tables clipped at 375 | `.table-wrap` scrolls horizontally and shows scroll shadows. |

## Scope covered
| Perspective | Scope | Out of scope |
|---|---|---|
| P0 Measured | 4 dumps: about 367 text elements, 88 controls, 7 headings each; 17 token colours; plan job class monitor; no console errors. | Judgement calls. |
| P1 | 4 screenshots, the 375 dump in full, the 1280 dump through the figure row: overlap, alignment, reflow, charts and tables, Japanese line breaks, dark separation. | The rest of the 1280 rects; the minified CSS. |
| P2 | Cold reads: the eye lands on 38.6%, the dominant element; 3 to 4 emphasis levels; the first stops match the brief; groups by distance, no panels; density fits a monitor screen; the dark theme keeps the hierarchy. | Line numbers. |
| P3 | The full 1280 dump text, the brief's 実績 block, Readers and Structure, tokens.json voice; the arithmetic behind the figures checked. Copy questions: 1 yes (export format unstated); 2 no error rendered; 3 yes; 4 no (rows 3, 4); 5 no (rows 5, 10, 22); 6 no empty state; 7 yes. Structure questions: all yes; the interval term varies. | The JS bundle; only the 今月 period captured. |

## Summary
Fix the two false statements first: 「年代と商品：弱い関連」 at p 0.205, and the 「全販売店420名」 count under a 「世田谷店・今月」 page without its period. Then put 契約件数 back in the same figure row as the other small figures, and use one name for the 95% interval. The review covered the 実績 tab at 1280 and 375 in both themes under 今月 only. With 0 CRITICAL and 6 WARNING, the work can move on once the warnings are ruled on.
