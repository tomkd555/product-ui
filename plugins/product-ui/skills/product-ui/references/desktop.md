# Desktop: the document window

Source of record for `meta.surface: desktop`: an application in its own window, built with Electron. It settles the regions of the window, their sizes, the commands and keys of the window itself, the file view, the save prompt and how Electron carries them out; the `## Window`, `## Commands` and `## File view` sections of `ui-brief.md` and the `## Command set` section `scripts/patterns/resolve.py` writes; `scripts/check_desktop.py` (DK1 to DK8); and R52 to R55 in `scripts/render/check_render.py`. Read it at Step 0 when the request asks for a desktop application, an Electron app, or an app that works like Word, Excel or PowerPoint, at Step 3 before the brief's desktop sections are written, and when one of these checks fires.

The window the skill builds is the document window of Microsoft Office: a title row, a ribbon under it, the file view behind the ファイル tab, task panes beside the document, and a status bar. The figures come from two sources:

- `research/20261121-office-window-measure/measured.md`: Word, Excel and PowerPoint of Microsoft 365 (16.0.20625) read through UI Automation at 1440×900, 1024×700 and 800×600 at 96 dpi, with the file view, the key tips and the prompt on closing a changed document. The title row, the tab row, the command area and the status bar have the same height in all three applications at all three sizes.
- `research/20261121-office-desktop-conventions/report.md`: what Microsoft's pages state about the ribbon, the keys, the dialogs and Electron's title bar. No Microsoft page states the height of the current ribbon, so every size below is this skill's own value, derived from the measurement.

The keys, the words of the commands and the save prompt belong to the profile `ms-office` (`profiles/ms-office.json`, `references/profiles.md`); this file names them where the window needs them.

## When the surface is desktop

| Web rule | Under `desktop` |
|---|---|
| Principle 2: the product's header, navigation and footer | The title row carries the document's name and the product's name, `<file name> - <product name>`, as Office's title row does (「文書1 - Word」). The window has no header, no logo, no footer and no navigation of links |
| Pages on routes, states on URLs | One window, which opens a new untitled document and keeps its state in memory. The query states exist for captures: a state the review captures is reached through a query on the renderer's URL (`?view=file&page=new`, `?pane=properties`, `?prompt=save`), which the kit reads once at start, and `?doc=sample` fills the document with the sample document, which the kit's host answers in a plain browser; the host also sets the selection to the sample's length and the history to one undo step, so that undo, cut, copy and delete are enabled for the commands probe. `references/interaction.md` asks for state in the URL; the desktop surface follows this file |
| Captures at 1280px and 375px | Captures at the window's default size and its minimum size, from `## Window` |
| R8: an h1 or an h2 on the screen | The window carries no heading, as Office's does not; R8 reads `document.title`, which equals the title row's text |
| The page scrolls | The window never scrolls as a whole (R52). The document area, the panes and the file view scroll inside themselves |
| Toasts for results | The window has no toast. A result the reader need not act on (保存しました) shows in the left area of the status bar, through `notify(text)` of `ShellApi`, for 5 seconds (the kit's `NOTIFY_MS`, which stands where `messages.duration_ms` is unset), and then the area returns to the `status` items; a second `notify` replaces the first, and the kit calls it after a save, a save as and an export succeed (「保存しました」, 「保存しました」, 「エクスポートしました」); this is the skill's own choice, since no Microsoft page states how a document window reports a result. `## Conventions` prints `messages.result` as `status-bar`. A result the reader must act on is a dialog |

Text stays at 14px or more (principle 5 of `SKILL.md`). Office sets its ribbon at 9 point, 12px at 96 dpi (`report.md`, [E76]), so each row that carries text is the measured height plus the difference in line height between 12px and 14px text. A key tip and the key text of a tooltip are Latin-only runs of at most 24 characters and may sit at 12px (`references/ban-list.md`).

## The window

| Region | Office, measured | Build |
|---|---|---|
| Window | | default 1280×720, minimum 500×480 (`## Window`). Microsoft asks for a minimum width of at most 500 effective pixels so that the window takes part in snap layouts ([E125]); the default fits the work area of a 1366×768 screen |
| Title row | 48px | 48px |
| Quick access toolbar | buttons 28×29px, 16px icons | buttons 28×28px, 16px icons: 上書き保存, 元に戻す, やり直し |
| Minimise, maximise, close | 48×48px | drawn by Electron's `titleBarOverlay`, 48px high |
| Tab row | 31px | 36px |
| Command area | 101px | 112px: 84px of commands, a 20px row for the group names, 4px of padding above and below |
| Large command | 42 to 48px wide, 76px high, 32px icon | 48px wide or more, 84px high: a 32px icon, then the label in up to 2 lines |
| Small command | 24×24px, 16px icon | 24px high, a 16px icon, the label to its right; 3 in a column |
| Dialog box launcher | 16×16px | 24×24px, at the right end of the group name row |
| Task pane | 350px wide, a 28px header | 350px wide by default, 280 to 480px by drag; a 36px header |
| Splitter | | a 6px hit area with a 1px line |
| Status bar | 22px | 28px |
| File view navigation | 160px wide, items 40px high | 160px wide, items 40px high |
| Save prompt | 460×323px, buttons 24px high | `min(28rem, 100vw - 2rem)` wide (448px at most), buttons 32px high |

From the top: the title row, the tab row, the command area, then the panes and the document side by side, then the status bar. The document area keeps the minimum width `## Window` gives it (200px by default, which leaves room for a 280px pane at the 500px minimum window). Where a pane would leave the document narrower, the pane's drag stops; at the minimum window size the right pane closes first, then the left.

### Title row

- Left to right: 8px of padding, the quick access toolbar, the document title centred in the free width, and the area Electron's caption buttons take at the right end. The renderer reads the free width from `env(titlebar-area-x)` and `env(titlebar-area-width)` ([E67]).
- The row is a drag region (`app-region: drag`, [E66]); every control in it is `app-region: no-drag`.
- The document title is `<file name> - <product name>`, with `*` after the file name while the document has unsaved changes, and `無題` for a document never saved. The renderer sets `document.title` to the same string, so the taskbar shows it.
- The quick access toolbar holds 上書き保存, 元に戻す and やり直し, in that order, as Excel and PowerPoint show them. 元に戻す and やり直し are disabled while their stack is empty.

### Tab row and command area

- ファイル is the first item of the tab row and opens the file view; it holds no commands of its own ([E11]). The tabs after it come from `## Commands`. ホーム is first and selected at start. A tab is `role="tab"` and the command area its `role="tabpanel"`.
- Take the tabs the application's commands need. Microsoft's guideline allows at most 7 core tabs and asks most programs for 4 or fewer ([E6]); Office's own tab names (ホーム, 挿入, デザイン, 表示, ヘルプ) are the names to use where a tab holds what Office's tab holds. A common command (切り取り, コピー) is disabled when it cannot run, and gets no contextual tab ([E6]).
- Groups sit side by side, separated by a 1px line, each with its name under it in the group name row. A group has large commands, columns of up to 3 small commands, or both. A command with a menu shows ▾ and opens a menu; a split command runs its main action from its upper part and opens the menu from its lower part.
- Every command shows a tooltip after 500ms: its name, then its keys in parentheses, 「上書き保存 (Ctrl+S)」 ([E46]). A disabled command's tooltip adds the condition under which it runs, in the words of `## Commands`' `Enabled when`, which complete 「…と実行できます」. A disabled ribbon, quick access or file view command stays focusable, so that its tooltip shows on focus as well as on hover: the kit sets `aria-disabled="true"` in place of `disabled` and ignores the click. `references/interaction.md` puts a disabled control's reason beside it; on this surface this rule replaces that one for these commands.
- **Collapsing.** When the window narrows and the groups no longer fit, the groups collapse one at a time into a single button that carries the group's icon and name and opens the group's commands under it, as Office's groups do ([E9], measured). The order is the `- Collapse:` line of `## Commands`; without it, the rightmost group collapses first and the first group (クリップボード) last. When every group is collapsed and the row still does not fit, the command area hides and the tab row alone shows; a click on a tab then opens its command area over the document until a command runs or Esc is pressed. This is Office's "タブのみを表示" state ([E12]), and Ctrl+F1 switches to it and back at any width ([E26]).

### File view

- A click on ファイル, or Alt then F, shows the file view over everything under the title row, as Office's Backstage view does. Its navigation column is 160px wide; the first item, 戻る, and the Esc key return to the document ([E120]). While it shows, the regions under it (the tab row, the command area, the panes, the document and the status bar) carry `inert`: Tab and a click reach none of them, and R32 leaves their text out.
- Its items, in Office's order (measured): 戻る, 新規, 開く, 上書き保存, 名前を付けて保存, 印刷, エクスポート, 閉じる, and オプション at the foot. 印刷, エクスポート and オプション appear where the application has that operation. Office's ホーム, 情報, 共有, アカウント and フィードバック belong to Microsoft 365's accounts and cloud and are left out. An item that opens a page (新規, エクスポート, 印刷, オプション) shows it to the right; an item that acts (上書き保存, 名前を付けて保存, 開く, 閉じる) closes the view and runs.
- `## File view` lists the items and what each runs. `resolve.py` writes the list from the operations the application declares.

### Task panes

- A task pane sits beside the document, at the right unless the brief places it at the left (Word's ナビゲーション pane sits at the left). Its header is 36px high and holds its title and a 24×24px close button (×). A pane opens from a command (a check in the 表示 tab, or the command that needs it) and closes with × or the same command.
- Its width is a state of the window, never saved in the document. The splitter on its inner edge drags it in 1px steps, ← and → on the focused splitter move it by 16px, and a double click restores the default.

### Document area

- The document area holds the application's own document (a page, a canvas, a sheet), named in the `document` row of `## Window` and built as the application's component. It takes no kind of `references/real-screens.md` and no pattern; the sections of the panes take patterns.

### Status bar

- The left end holds the state of the document as short items: counts (ページ1/3, 要素12), the selection, the language. The right end holds, left to right, the view buttons where the application has views, 縮小 (−), the zoom slider 100px wide, 拡大 (+), the zoom in percent, and a fit button where the document is a canvas; the button prints the label of the `zoom-fit` command (ウィンドウに合わせる). This is the order of Excel's and PowerPoint's status bars ([E15], measured).
- Every item that takes a click is a button with an accessible name.

### Save prompt

- The prompt shows when the window closes, and before 新規 and 開く, while the document has unsaved changes. Its sentence, as Office prints it, is 「このファイルの変更内容を保存しますか?」, and its buttons are 保存 (Alt+S), 保存しない (Alt+N) and キャンセル (Esc), right-aligned in that order, with 保存 the default (measured; [E52], [E55], [E56]). The words come from the profile's `confirm.close`.
- 保存 saves (and asks for a file name where the document has none) and then goes on with the operation; 保存しない goes on without saving; キャンセル returns to the document. A save that fails returns to the document with the error, and the window stays open.
- A dialog in the window (the save prompt and the error dialog) keeps its row of buttons, right-aligned in Office's order, and its width `min(28rem, 100vw - 2rem)` at every window width, including the widths below 640px, where shadcn's `sm:` classes give a dialog 320px wide with the buttons stacked in reverse. The kit's two dialogs set the classes that keep both. An application's own shadcn dialog overrides the `sm:` classes the same way: a footer with `flex-row justify-end`, and a content with `max-w-[min(28rem,calc(100vw-2rem))]` at the base, at `sm:` and at `data-[size=default]:`.
- The error dialog (`ErrorNotice`) shows a failure the reader must act on. Its title is the `title` prop, else the title that `FAILURE_TITLES` (beside `ErrorNotice`) gives the command id of the failed operation, else 「エラー」: open 「開けませんでした」, save and save as 「保存できませんでした」, export 「エクスポートできませんでした」, print 「印刷できませんでした」, new 「新規作成できませんでした」, close 「閉じられませんでした」, undo 「元に戻せませんでした」, redo 「やり直せませんでした」, cut 「切り取れませんでした」, copy 「コピーできませんでした」, paste 「貼り付けられませんでした」, select all 「すべて選択できませんでした」, delete 「削除できませんでした」; the shell passes the id of the command that failed.
- The application draws the prompt as a modal dialog in the renderer. Office's prompt is a window Office draws itself (measured: its class is Office's own), and a prompt in the renderer is captured by the review like any other state (`?prompt=save`).

## Keys

The profile `ms-office` lists the keys and the word of each command (`references/profiles.md`). The window adds the keys of its regions:

- **Alt or F10** shows the key tips: one letter or digit on each tab, on ファイル and on each command of the quick access toolbar ([E27], [E35]). A key tip's letter selects its tab and shows the key tips of that tab's commands; a command's key tip runs it. Esc goes back one step, and at the first step hides the key tips and returns the focus to the document ([E36]). A key tip is an element with `data-keytip` holding its letters.
- The key tips of Office's tabs and commands are the defaults: ファイル F, ホーム H, 挿入 N, 表示 W, ヘルプ Y; on the quick access toolbar 1, 2, 3 in order; on ホーム 貼り付け V, 切り取り X, コピー C (measured). In the file view the key tips are Office's (measured): 新規 N, 開く O, 上書き保存 S, 名前を付けて保存 A, 印刷 P, エクスポート E, 閉じる C, オプション T, and 戻る takes B. The commands the operations add to ホーム and 表示 take すべて選択 A, 削除 D, 検索 FD, 置換 R, ズーム Q and ウィンドウに合わせる J, this skill's own choice. A command of the application's own takes the key tip `## Commands` gives it; where the row gives none, it takes the first Latin letter of its tab's name that is still free in the tab, else the first free letter from A to Z. A tab of the application's own takes the first Latin letter of its name that is still free, else the first free letter from A to Z, so a tab with a Japanese name takes a letter from A to Z. Two key tips where one begins the other (A and AL) stop `resolve.py`.
- **A collapsed group** carries a key tip in its tab's scope: the digit of the group's position among the tab's groups, 1 for the first group up to 9 (`data-group-tip`). This is the kit's choice; Office's collapsed groups carry tips of their own that this file does not measure. The digit opens the group's panel and keeps the tab's key tips showing, so the key tips of the group's commands show inside the panel; R55 counts the collapsed groups' key tips among the tab's commands.
- **F6** moves the focus between the tab row, the document, the open task panes and the status bar; Shift+F6 goes back ([E23], [E38]).
- **Ctrl+F** opens the 検索 dialog, as PowerPoint does ([E31]); under the product `word` it opens a pane at the left with the search box and the results, as Word's ナビゲーション pane does ([E30]).
- **Shift+F10** opens the context menu of the selection ([E24]). A context menu lists commands without their keys ([E46]).
- **Ctrl+F1** collapses the command area to the tab row and restores it ([E26]).
- While the focus is in a text field outside the document area (`[data-region="document"]`), Ctrl+X, Ctrl+C, Ctrl+V, Ctrl+Z, Ctrl+Y, Ctrl+A, Delete and Backspace act on the field's text and reach no command. Inside the document area, whose page or canvas may itself be a text field, Ctrl+Z and Ctrl+Y run the window's undo and redo commands; Ctrl+X, Ctrl+C, Ctrl+V, Ctrl+A, Delete and Backspace keep acting on the text and also announce the command while it is enabled (`product-ui:command` with its id, no `preventDefault`).
- **F1** opens the help where the application has one. An application without help leaves F1 unbound and the profile's help command out of the command set: `resolve.py` writes no help command and `## Conventions` lists F1 ヘルプ only where the command set holds help, and an application with help lists it as a row of `## Commands` that takes F1.
- No command depends on a key alone: each is also on the ribbon, the file view or a menu ([E45]).

## Electron

Electron 13 and later draw the caption buttons through the Window Controls Overlay, which keeps Windows' snap layouts on the maximise button ([E121], [E125]). The kit (`references/components.md`, The kit) carries these rules out:

- **The window.** `BrowserWindow` with `titleBarStyle: 'hidden'` and `titleBarOverlay: { color, symbolColor, height: 48 }`, the colours from `WINDOW_SPEC.colors` (`muted` and `foreground` of `tokens.json`, in hex, since Electron reads no oklch; `darkColors` from the dark theme) unless the main entry passes `colors` ([E65], [E129]); `minWidth` and `minHeight` from `## Window` ([E127]); `show: false` until `ready-to-show`.
- **Security.** `webPreferences` keeps `contextIsolation: true`, `sandbox: true` and `nodeIntegration: false`, and never sets `webSecurity: false`. The renderer reaches the file system through the functions the preload script exposes with `contextBridge`, one per operation (open, save, save as, export). The kit also takes the protections of Electron's security checklist (https://www.electronjs.org/docs/latest/tutorial/security): the renderer is served from `app://renderer/` through `protocol.handle`, each IPC handler refuses a frame from another origin than the app's page and checks the type of every argument, every permission request is refused except `clipboard-read` and `clipboard-sanitized-write`, which the app's own page may use, `will-navigate` and the window-open handler keep the window on the app's page and hand an `https:` or `mailto:` link to the system, and `requestSingleInstanceLock` keeps one instance, whose window comes to the front on a second launch. The window carries `name` with `windowStatePersistence`, so that Electron restores its position and size, and a text field shows 切り取り, コピー and 貼り付け on a right click and on Shift+F10.
- **The menu.** `Menu.setApplicationMenu(null)` removes Electron's default menu and the menu bar ([E72]). The ribbon is the command surface, so the window's keys are the renderer's: the kit's command table handles them on `keydown`. No key is registered with `globalShortcut`, which takes the key while the application is out of focus ([E51], [E74]). `@electron-toolkit/utils`' `optimizer.watchWindowShortcuts` binds F12 to DevTools in development, and F12 is 名前を付けて保存, so the kit leaves it out and opens DevTools with Ctrl+Shift+I in development only.
- **What the kit runs and what the application runs.** The kit's handlers run new, open, save, save as, export, close, print, zoom and zoom-fit, and the edit commands: undo, redo, cut, copy, paste, select all and delete call the preload function `edit(action)`, and the main process checks `action` against `undo`, `redo`, `cut`, `copy`, `paste`, `selectAll` and `delete` before it calls the matching `webContents` action on the focused element; a click on a command keeps the focus where it was, so that the action reaches the field or the document the reader was in. Where the preload functions are absent (a plain browser), the host falls back to `document.execCommand` where it exists. An application's own handler for the same id replaces the default. Find, replace and every command of the application's own (`app-01` and on) are the application's to supply.
- **Fit.** The default `zoom-fit` run sets the zoom at which the element marked `data-document-page` fits inside the document region: the smaller of the width ratio and the height ratio, rounded down to a whole percent, within the zoom range (10 to 400), and 100 where no element carries the mark. The element's layout size is its size at 100%, so the application scales it with `transform`, not with the CSS `zoom` property.
- **Closing.** The main process stops the window's `close` event while the renderer reports unsaved changes, sends the renderer a close request, and closes the window when the renderer answers after its save prompt.
- **The renderer in a browser.** Where the preload's functions are absent, the kit's host module answers them from memory: open returns the sample document, save keeps the text. The renderer then runs in Chrome, which is how Step 5 captures it.

## The brief's desktop sections

A brief with `meta.surface: desktop` has a `## Composition` block with `Kind: desktop window` and `Density: compact`, from the sizes measured in The window above, and carries three sections after `## Composition`, written at Step 3, and `resolve.py` writes a fourth.

### `## Window`

```
## Window

| Item | Value |
|---|---|
| size | 1280x720 |
| minimum | 500x480 |
| title | {file} - 構成図エディター |
| left pane | アイコン 280 240-400 open |
| right pane | プロパティ 350 280-480 closed |
| document | 構成図のキャンバス; minimum width 200 |
| status bar | 要素数, 選択数 / ズーム, 合わせる |
```

`size` and `minimum` are width x height in px. A pane row gives its title, its default width, its range and whether it is open at start, or `none`. The `status bar` row lists the left items, then `/`, then the right items. `resolve.py` fills a row left out with the value of this file and adds the rows of the fixed regions, `title row height` 48, `tab row height` 36, `command area height` 112 and `status bar height` 28, which R53 measures.

### `## Commands`

```
## Commands

| Tab | Group | Command | Size | Keys | Key tip | Enabled when | Runs |
|---|---|---|---|---|---|---|---|
| ホーム | 配置 | グループ化 | large | Ctrl+G | G | 2つ以上の要素を選択している | 選択した要素をグループにまとめる |

- Operations: new, open, save, save-as, close, undo, redo, cut, copy, paste, select-all, delete, export, print, find, replace, zoom
- Collapse: 配置, 編集
```

One row per command of the application's own; `Size` is `large`, `small`, `menu` or `check`. `- Operations:` lists the document operations the application has, by the profile's action names. `- Collapse:` gives the order in which groups collapse. The commands of the operations are left out of the table: `resolve.py` writes them. A row may still name a command of the profile, by its word, to give it a key the profile leaves empty (削除 with Delete, as long as no other command holds the key) or to replace its `Enabled when` or its `Runs`; its Tab, Group and Size are required cells that the operation's own place overrides, and its `Runs` stays in the command set. A row that changes a key the profile gives stops the run. A row that repeats the profile's keys keeps them. A row names a command of the profile only where `- Operations:` lists its operation.

### `## File view`

```
## File view

| Item | Page or action |
|---|---|
| 新規 | 空白の図と5つのテンプレート |
| エクスポート | PNGとSVG、倍率、背景 |
```

One row per item that opens a page, saying what the page holds. `resolve.py` adds the items that act (上書き保存, 名前を付けて保存, 開く, 閉じる) and 戻る.

### `## Command set`

Written by `resolve.py` from `## Commands`, `## File view` and the profile; an edit here is overwritten. It holds every command of the window in one table with the columns `Id`, `Place`, `Tab`, `Group`, `Command`, `Size`, `Action`, `Keys`, `Key tip`, `Enabled when`, `Runs`, in this order of rows: the quick access toolbar, the file view, then each tab's commands in the order of the tabs and groups.

- `Place` is `quick-access`, `file-view` or `ribbon`.
- `Id` is the action's name for a command of the profile (`save`, `undo`; a command that sits in two places, such as 上書き保存 on the quick access toolbar and in the file view, keeps one id and takes one row per place), and `app-01`, `app-02` and on, in the order of `## Commands`, for a command of the application's own.
- `Action` is the profile's action, or `app` for a command of the application's own.
- `Keys` is `none` for a command without keys; `Key tip` is the letters after Alt, or after the tab's letter for a command of a tab.
- `Enabled when` is `always` where the command always runs; otherwise it is the condition, written to complete 「…と実行できます」 (元に戻せる操作がある, 文書内で範囲を選択している). The defaults are 元に戻せる操作がある for undo, やり直せる操作がある for redo, and 文書内で範囲を選択している for cut, copy and delete; a row of `## Commands` replaces them.

The rows of the operations, with their places:

| Operation | Place, tab, group | Size |
|---|---|---|
| save | quick-access; file-view | small |
| undo, redo | quick-access | small |
| new, open, save-as, print, export, close | file-view | |
| paste | ribbon, ホーム, クリップボード | large |
| cut, copy | ribbon, ホーム, クリップボード | small |
| select-all, delete, find, replace | ribbon, ホーム, 編集 | small |
| zoom | ribbon, 表示, ズーム: ズーム (menu) and ウィンドウに合わせる (large) | |

The word and the keys of each row come from the profile. The commands of a tab go after the application's own commands of the same group; a group the operations add goes where Office has it: クリップボード first on ホーム, 編集 last on ホーム, ズーム last on 表示. ホーム is the first tab, and 表示 the last when only the zoom puts it there. 戻る takes the id `back`, the fit command `zoom-fit`, and an item of `## File view` that names no operation of the profile (オプション) an `app-` id after the rows of `## Commands`. A row of `## Commands` that names a command of the profile with other keys than the profile gives, or a key the profile gives another command, stops the run with the conflict named. A desktop brief needs `## Window`, `## Commands` and `meta.profile`; `resolve.py` stops on a brief that lacks one of them.

### The command table file

`scaffold.py` writes `scaffold/command-set.ts` from `## Command set`, one object per line, in the order of the section, so that `check_desktop.py` (DK5) reads it line by line. The build copies it to `src/renderer/src/`, so the same brief gives the same ribbon on every run:

```ts
// Written by scripts/patterns/scaffold.py from the ## Command set section of ui-brief.md; change the brief and run it again.
import type { CommandSpec } from "@/lib/commands"

export const COMMAND_SET: CommandSpec[] = [
  { id: "save", place: "quick-access", tab: "", group: "", label: "上書き保存", size: "small", action: "save", keys: "Ctrl+S", keytip: "1", enabledWhen: "always" },
]
```

It also writes `scaffold/window-spec.ts` from `## Window`: `WINDOW_SPEC` with `size`, `minimum`, `title`, the panes, the document's minimum width, the fixed heights of the regions, `colors` (`{ background, symbol }` in hex: `muted` and `foreground` of `tokens.json`, converted from oklch and clipped to sRGB) and `darkColors` where `tokens.json` declares `color_dark`, the tabs with their key tips, the collapse order and the save prompt's sentence and buttons from the profile. The build copies it to `src/shared/`, where the main process and the renderer both import it: the main process reads the minimum size and the title row height from it, and DK2 compares both with `## Window`.

### Markers the checks read

The kit's parts carry these attributes, and a window built without the kit carries them as well:

| Attribute | On | Read by |
|---|---|---|
| `data-region` | the regions: `title-row`, `quick-access`, `tab-row`, `command-area`, `document`, `left-pane`, `right-pane`, `status-bar`, `file-view` | R53, DK3 |
| `data-command` | each control that runs a command, with its `Id` from `## Command set` | R54, DK5 |
| `data-key` | each control of a command that has keys, with its `Keys` | R54, PF2 |
| `data-keytip` | each key tip while it shows, with its letters | R55 |
| `data-confirm="close"` | the save prompt | DK7, PF3 |
| `data-file-tab` | the ファイル tab | R54 |
| `data-document-page` | the page or canvas of the document, which the default `zoom-fit` run fits inside the document region | the kit (no check) |

The kit's command table dispatches `new CustomEvent("product-ui:command", { detail: { id } })` on `window` each time a command runs, from a click, a key or a key tip.

## Look

The look comes from `tokens.json`, as on every surface: the window's chrome (the title row, the tab row, the status bar, the file view's navigation) takes `muted`, the command area and the panes take `surface` or `background`, the selected tab is marked by a 3px bar in `primary`, and a hover or selected fill on the muted chrome takes `background`, since `accent` equals `muted` there. The face is `font-family: 'Segoe UI Variable', 'Yu Gothic UI', sans-serif`: Microsoft names the first for Latin text and the second as the user-interface font of current Windows for Japanese ([E99]). Step 1 writes `typography.display` and `typography.body` with `family` `Segoe UI Variable` and `family_ja` `Yu Gothic UI`, the provenance of both `reference: references/desktop.md`, and runs no font lookup: the lookup's faces come from Google Fonts, which the window's content security policy blocks. Where `tokens.json` declares a dark theme (`WINDOW_SPEC.darkColors` is set), the window follows the system's choice through `prefers-color-scheme`: the kit's shell sets `.dark` on the root; with no dark theme the shell leaves the root as it is, and `runDocumentApp` takes `darkColors` (from `WINDOW_SPEC.darkColors` unless the entry passes them) for the title row's caption buttons. Icons come from lucide. The window prints no Microsoft name, logo or icon: Microsoft's trademark guidelines count logos, icons, trade dress and fonts among its brand assets ([E85]).

A US jury found in 2018 that an office suite infringed Microsoft's patents on its user interface ([E83]). The skill builds applications that are not office suites; where the request is for a word processor, a spreadsheet or a presentation program, the hand-over says that its window follows the conventions of the product it competes with.

## Checks

### DK1 to DK8: `scripts/check_desktop.py`, on the source (Step 4)

```bash
python {SKILL_DIR}/scripts/check_desktop.py <project-dir> --json
```

It reads the main process, the preload script and the renderer under the project, and the brief beside the nearest `tokens.json` (`--brief` names another). A project whose `tokens.json` is not on `desktop` gives no finding.

| ID | Finding |
|---|---|
| DK1 | a `BrowserWindow` whose `webPreferences` sets `contextIsolation: false`, `sandbox: false`, `nodeIntegration: true` or `webSecurity: false` |
| DK2 | the `titleBarOverlay` height differs from the title row, or `minWidth` and `minHeight` differ from `## Window`'s minimum |
| DK3 | no element of the title row carries `app-region: drag`, or a control inside it lacks `no-drag` |
| DK4 | a call of `globalShortcut.register` |
| DK5 | a command of `## Command set` missing from the kit's command table, or one whose word, tab, group or keys differ |
| DK6 | two commands with one key, or a Ctrl+Alt combination ([E49]) |
| DK7 | no handler of the window's `close` event that waits for the renderer, or no element with `data-confirm="close"` in the renderer |
| DK8 | Electron's default menu left in place (no `Menu.setApplicationMenu`), or `optimizer.watchWindowShortcuts` called |

The DK checks are errors: four verification builds showed them free of misfires. Silence a misfire in the file as `product-ui: ignore DK2 <reason>`.

### R52 to R55, on the rendered window (Step 5)

The review captures the renderer at the two sizes of `## Window`, with `cdp.js <url> <width>x<height>`. `PROBE=commands`, run on the `?doc=sample` state when the plan's `Captures:` list holds it and on the entry otherwise (an empty document disables undo, cut, copy and delete, and the probe skips disabled controls; the kit's host gives the `?doc=sample` state a selection and one undo step, so those controls are enabled), presses each key a control carries in `data-key`, with the file view opened once through the ファイル tab (`data-file-tab`) so that its items' keys are read too, then Alt, the key tip of the first tab after ファイル and Esc, and writes what happened into the dump's `probes`; the kit's command table dispatches a `product-ui:command` event on `window` with the command's id each time a command runs, and that event is what the probe records. Chrome keeps some keys before the page sees them (Ctrl+X, Ctrl+C and Ctrl+V for its clipboard, Ctrl+N and Ctrl+T for a new window or tab), while Electron hands them to the page, so the probe sends these as a `keydown` event on `window` and marks them `synthetic` in the dump.

| ID | Finding |
|---|---|
| R52 | the document element scrolls: the window scrolls as a whole |
| R53 | a region whose height differs from the `… height` rows of `## Window` by more than 1px (the title row, the tab row, the command area, the status bar), or a document area narrower than its minimum at the minimum size. A command area of height 0 is the tab-only state and is left out |
| R54 | a key in `data-key` whose command did not run when the key was pressed |
| R55 | Alt showed no element with `data-keytip`, a tab's key tip showed no key tip of the tab's commands, or Esc left them showing |

All four are CRITICAL, under the same rule as the DK checks.

On the desktop surface R14 does not run: the window's chrome sets every label at 14px, with bold for the selected tab and the pane headers, and the levels a reader follows belong to the document, whose text follows the zoom.
