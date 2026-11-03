# Benchmark: what each rendered item tells its reader

Six requests, seven screens, used to measure product-ui before and after the pattern library (`../plan.ja.md`, Phase 0 and Phase 6). Each request names its reader and the reader's job, and supplies the sample data, so the build has no intake question to ask and every run renders the same records.

| Bench | Screens | Reader, frequency, expertise | Job fields: what the reader needs from each item |
|---|---|---|---|
| `invoices` | list `/`, detail `/invoices/INV-2026-0403` | 経理担当者, daily, intermediate | list: 取引先, 請求金額, 支払期日, ステータス; detail: those and 明細 |
| `reservations` | list `/` | 受付スタッフ, daily, intermediate | お客様名, 日時, メニュー, 担当スタッフ, ステータス |
| `staff` | list `/` | 社員, occasional, intermediate | 氏名, 部署, 役職, 内線番号, メールアドレス |
| `orders` | list `/` | 購入者, occasional, novice | 商品, 注文日, 配送状況, お届け予定日 |
| `inbox` | list `/` | サポート担当者, daily, expert | 件名, お客様, 受付日時, ステータス, 担当者 |
| `products` | list `/` | 購入者, occasional, novice | 商品名, 価格, 評価, レビュー件数, 容量 |

The job fields are this benchmark's reading of each stated job; they are the fixed yardstick, and a build is free to show more.

## Files

- `<bench>/bench.json`: the request as the user would type it, `today`, the user group, the object with its fields (`[label, kind]`) and locators, and the screens with their job fields.
- `<bench>/data.json`: the sample records. Every locator value is unique across a bench's records.
- `measure.py`: renders a screen through `cdp.js` and scores it; its docstring holds the matching rules.

## Measures

| Measure | Meaning |
|---|---|
| `found` | records whose item was located on the screen, of `records` |
| `mean_fields_per_item` | fields of the record the item shows, of `fields_available` |
| `job_coverage` | mean share of the job fields each item shows |
| `items_with_all_job_fields` | items that show every job field |
| `never_shown` | fields no item shows |
| `items_linked` | items that are, or sit inside, a link |
| `enclosures` | boxes `cdp.js` counts as enclosures in <main> |
| `labels` | C18 to C21 findings from `check_copy.py` over the app source |

A datetime counts as shown when the item shows its time, because a list grouped by day carries the date in the group heading.

## Running

Build each app, serve it (`vite preview`), then:

```bash
python measure.py invoices list http://localhost:4301/ --out ../baseline --src <app>/src --skill <skill dir>
python measure.py invoices detail http://localhost:4301/invoices/INV-2026-0403 --out ../baseline
```
