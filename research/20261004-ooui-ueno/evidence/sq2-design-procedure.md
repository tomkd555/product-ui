# 書籍『オブジェクト指向UIデザイン』と上野氏の講演・記事は、設計手順を手順書とチェック項目に書ける粒度でどう定めているか

## Evidence
| Claim | Publisher | URL | Published | Grade | Quote | Corroboration |
|---|---|---|---|---|---|---|
| Book (Sociomedia, Ueno, Fujii; Gijutsu-Hyoron) published 2020-06-05; Ch.2 is "Design Process for OOUI", Ch.3 practice, Ch.4-5 workouts (9+9 exercises), Ch.6 philosophy. A revised edition is listed for 2026. | gihyo.jp (Gijutsu-Hyoron) | https://gihyo.jp/book/2020/978-4-297-11351-3 | 2020-06-05 | B | no quote (WebFetch summary; TOC paraphrased) | single_source |
| Process has three steps: 1 object extraction (model), 2 views and navigation (interaction), 3 layout pattern application (presentation). | Ueni (Speaker Deck, personal; Sociomedia-related) | https://speakerdeck.com/uenitty/design-process-of-ooui | 2020-09-30 | C | 1. オブジェクトの抽出（モデル）2. ビューとナビゲーションの検討（インタラクション）3. レイアウトパターンの適用（プレゼンテーション） | corroborated (gihyo, yiio note) |
| Same three steps described in secondary reading notes (extract objects, design views, create layouts). | yiio (note.com) | https://note.com/yiio/n/n646b6a031626 | 2021-08-25 | C | ①オブジェクトを抽出する②ビューを設計する③レイアウトを作成する、の3ステップで行われます | corroborated |
| Object test criteria (checkable): expressible as a countable noun; manageable as a set of the same kind; has common actions. | Ueni (Speaker Deck) | https://speakerdeck.com/uenitty/design-process-of-ooui | 2020-09-30 | C | 数えられる名詞として表せる・同種の集合として管理され得る・共通のアクションを持っている | single_source |
| Two view types: collection (several same-type objects, key attributes) and single (one object, more attributes). | Ueni (Speaker Deck) | https://speakerdeck.com/uenitty/design-process-of-ooui | 2020-09-30 | C | ビュー（ひとまとまりの情報表示領域）の種類は大きく2つ・コレクション...・シングル... | corroborated (yiio: 各オブジェクトにコレクション（一覧）ビューとシングル（詳細）ビュー) |
| Call relation: selecting one object in a collection view shows its single view (master-detail). | Ueno Manabu, Sociomedia blog | https://www.sociomedia.co.jp/8740 | 2019-03-05 | B | コレクションビューの中でユーザーがひとつのオブジェクトを選ぶと、その内容を表示するシングルビューが表示されるという振る舞いになります。 | single_source |
| Root navigation items are noun phrases following object-based operation syntax. | Ueno Manabu, Sociomedia blog | https://www.sociomedia.co.jp/8740 | 2019-03-05 | B | ナビゲーション項目は名詞形の表現になり、オブジェクトベースの操作構文に沿ったものになります。 | corroborated (iret.media on verb-free nav) |
| Navigation transitions are designed by linking views with arrows for references between views. A selection criterion for root nav was only seen in a search summary (objects that are entry points of use), unquoted. | yiio (note.com) | https://note.com/yiio/n/n646b6a031626 | 2021-08-25 | C | ビュー同士の参照関係を矢印で繋ぎ、ナビゲーション遷移を設計します | single_source |
| Action placement: object-select then action-select syntax kept across the whole app. | Ueno Manabu, Sociomedia blog | https://www.sociomedia.co.jp/8740 | 2019-03-05 | B | オブジェクト選択 → アクション選択という操作構文をできるだけアプリケーション全体で踏襲します。 | corroborated (iret.media) |
| Verbs belong inside object screens or action buttons; object+action menus such as 顧客登録 multiply items and paths. | iret.media | https://iret.media/198776 | 2026-06-11 | C | 動詞はナビゲーション項目ではなく、「オブジェクトの画面内に配置する」「アクションボタンとして設置する」のがOOUIの鉄則です。 | corroborated (Sociomedia blog) |
| CRUD pattern: pressing 変更 on a contract or 新規 above the list turns the single-view pane into an edit form (create/update in the single-view pane). | Ueno Manabu, Sociomedia blog | https://www.sociomedia.co.jp/8740 | 2019-03-05 | B | ユーザーが契約の「変更」ボタンを押した時、あるいは一覧の上にある「新規」ボタンを押した時には、シングルビュー部分のペインが編集用のフォームに変わるようにします。 | single_source |
| Layout step: choose UI parts from a pattern collection by purpose; reuse generalized layout patterns. | yiio (note.com) | https://note.com/yiio/n/n646b6a031626 | 2021-08-25 | C | 用途に応じたUIパーツをパターン集から選び、配置していきます | single_source |
| The three steps are iterated in any order and adjusted repeatedly. | Ueni (Speaker Deck) | https://speakerdeck.com/uenitty/design-process-of-ooui | 2020-09-30 | C | これらを順不同で繰り返し調整し、全体としてのまとまりを作り上げる | corroborated (Sociomedia blog 全体と部分の往復) |
| Whole-and-part iteration: define parts from the whole, redefine the whole from parts, repeat. | Ueno Manabu, Sociomedia blog | https://www.sociomedia.co.jp/8740 | 2019-03-05 | B | 全体の状態から部分を定め直し、部分の状態から全体を定め直す。この繰り返しです。 | corroborated |

## Falsifier
| Query | What came back | Does it change the answer |
|---|---|---|
| オブジェクト指向UIデザイン 書籍 手順は固定できない 順不同 プレゼンテーションから逆算 上野学; plus fetch of ekrits.jp interview 上野学「オブジェクト指向デザインの道具論」 | The book keeps the same 3 steps. Sources state the steps are iterated in any order, sometimes starting from presentation (search-result summary, unquoted). ekrits interview (2020-10-28, grade C trade media): Ueno says design cannot be reduced to mechanical rules and needs abductive reasoning from embodied experience; the method came out of practice. | Partly. The three-step sequence stands as the book's frame. The authors say the steps are iterated freely and that judgment cannot be fully fixed as rules. A one-pass checklist carries this author-stated limit. |

## Search log
| Query | Facet | Sources adopted |
|---|---|---|
| オブジェクト指向UIデザイン 設計手順 オブジェクト抽出 コレクションビュー シングルビュー ナビゲーション | definition | gihyo (via search), yiio |
| 上野学 OOUI メインオブジェクト ルートナビゲーション アクション 配置 CRUD パターン | practice | iret.media |
| OOUI 設計プロセス 行き来 試行錯誤 ソシオメディア オブジェクト抽出 ビュー レイアウトパターン | definition | speakerdeck uenitty, sociomedia.co.jp/8740 |
| Sociomedia OOUI object-oriented UI design process collection view single view (allowed_domains sociomedia.co.jp, gihyo.jp) | definition (primary sweep) | gihyo book page, sociomedia.co.jp/8740 |
| オブジェクト指向UIデザイン 書籍 手順は固定できない 順不同 プレゼンテーションから逆算 ルールではない 上野学 | falsifier | ekrits.jp |
| Fetches: speakerdeck, sociomedia 8740, gihyo, yiio, iret, ekrits | all | as above |

## Gaps
- Book body text was not read (paid book; only TOC and secondary summaries). The book's own rules for root-navigation selection criteria, action placement variants and CRUD layout patterns are unconfirmed; the 2019 Sociomedia blog post is the nearest primary text. Reading Ch.2-3 of the book settles it.
- Data facet (figures): none found beyond a search-summary claim of 5-20x fewer screens; not adopted, no quote.
- No scholarly source searched (the sub-question asks what the procedure says and makes no effectiveness claim).
- Floors met: 6 searches including the falsifier; independent origins: gihyo, Sociomedia, Speaker Deck, note.com, iret.media, ekrits (6). Speaker Deck author "Ueni" affiliation to Sociomedia is unverified.
- Quotes come from WebFetch transcription requests; the tool may have normalised them, so verify before reuse.
