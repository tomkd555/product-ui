# Baseline: product-ui 1.2.0 on the benchmark (2026-11-03)

Phase 0 of `../plan.ja.md`. Each request in `../bench/` was built with product-ui 1.2.0, as it stands on `main` at 3821daa, following SKILL.md Steps 0 to 4, and measured with `../bench/measure.py` at 1280px. Three agents built two benchmarks each, in a shared Vite workspace with the dependencies preinstalled; the apps live outside the repository, and `<bench>/ui-brief.md` and `<bench>/tokens.json` here are copies of what each build wrote.

How the runs differed from a user's session:

- Step 0 asked nothing. Each run settled the intake from `bench.json` and recorded it in `meta.defaults_applied`: surface `saas`, no reference, the structure from `references/ooui.md`, users `basis: reported`, colours from the lookup.
- Step 5 did not run. No review verdict is recorded, to bound the cost of seven screens. textlint did not run.
- shadcn/ui components were written by hand on @base-ui/react; the CLI was not used.

## Results

| Bench / screen | Records found | Fields per item (of all) | Job coverage | Items with every job field | Fields no item shows | Enclosures | C18–C21 |
|---|---|---|---|---|---|---|---|
| invoices / list | 12 of 12 | 7.0 of 7 | 1.0 | 12 | none | 2 | 0 |
| invoices / detail | single | 9 of 9 | every job field | — | none | 1 | — |
| staff / list | 15 of 15 | 5.0 of 7 | 1.0 | 15 | 勤務地, 社員番号 | 1 | 0 |
| orders / list | 8 of 8 | 6.9 of 7 | 1.0 | 8 | none | 1 | 0 |
| products / list | 12 of 12 | 6.0 of 6 | 1.0 | 12 | none | 12 | 0 |
| reservations / list | 12 of 12 | 5.0 of 7 | 1.0 | 12 | 予約番号, 電話番号 | 3 | 0 |
| inbox / list | 6 of 12 | 4.2 of 7 | 1.0 | 6 | 担当者, 問い合わせ番号 | 1 | 0 |

- Every check script of 1.2.0 passed with 0 errors in every build. The inbox build silenced two S16 warnings as misfires, with reasons; the others raised no warning.
- inbox opens on its 未対応 tab, so six records are on the screen; 担当者 is empty on every one of them, which the measure does not score.
- Five of the seven screens are tables (`tr`), one is a list (`li`), and the products screen is a table with an image cell. No screen is a card grid. The products table draws each image cell as an enclosure, which is why it counts 12.
- The screenshots are `<bench>-<screen>.png`; the scores per item are in `<bench>-<screen>.json`.

## What the baseline shows

With the sample data supplied and the reader's job stated, 1.2.0 already shows every field the job needs on every item, and no generic or feature-shaped label. The composition plan, the container rule and the reader-fit questions carried the screen there. The defect the plan sets out to remove, a card that carries none of the information the reader wants, did not occur under these requests.

So this benchmark cannot show the new version doing better on information content: it measures 1.0 already. What it can still compare is what 1.2.0 has no way to produce: a named pattern per container, the same skeleton from the same brief, and the conformance checks PT1 to PT7 and R42 to R47.

To measure the defect itself, a request has to leave the data or the job out, so the build chooses the fields. Running such requests is not part of this baseline; it is an open decision for the owner, with its cost (a build of seven screens took three agents about 700k tokens).
