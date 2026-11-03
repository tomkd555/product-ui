# Label register

Labels rejected on a screen: buttons, links, headings, form labels, tooltips and placeholders. `scripts/check_copy.py` reads the table below as C36 and reports every label that matches a row, with the replacement and the reason. A project grows its own register in `label-register.md` beside `tokens.json`, in the same three columns; both are read. The format follows the vocabulary register of prose-lint (https://github.com/tomkd555/prose-lint).

## How to add a row

- Add a row when a label is rejected in review, the same day, so the next build cannot repeat it.
- The first column is a Python regex matched against the whole label. Anchor it (`^…$`) unless the row is meant to match inside a longer label.
- Escape a pipe as `\|`; a bare one splits the column.
- `Instead` says what to write. `Why` names the source or the review that rejected it, in one sentence; both are shown with every hit.
- A hit is a warning. A label the reader's own vocabulary uses stays, listed in `voice.allow` with the reason.

## Rejected labels

| Pattern | Instead | Why |
|---|---|---|
| ^データ(が\|は)ありません。?$ | Name the object: 「{object}はありません。」, or 「該当する{object}はありません。」 after a filter. | An empty state names what is empty (SmartHR, 空データ; Stripe Apps, Empty state). |
| ^(Get started\|はじめる\|始める\|始めましょう)$ | Name the action the empty state's title points to, as a verb and a noun: 「請求書を作成」. | A first-use empty state's action matches its title (Stripe Apps, Empty state). |
| ^(詳細を見る\|詳細へ\|View details\|See details)$ | Make the whole row or card the link to the single view, with no second link inside it. | The item is the link to its record (SmartHR, よくあるリスト; DADS, リソースリスト). |
