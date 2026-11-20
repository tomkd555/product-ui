// The type of WINDOW_SPEC, which scaffold.py writes from the brief's `## Window` section (references/desktop.md).
// The main process reads the sizes, the renderer reads the rest.

export type PaneSpec = { title: string; width: number; min: number; max: number; open: boolean }
export type TabSpec = { name: string; keytip: string }

export type WindowSpec = {
  size: { width: number; height: number }
  minimum: { width: number; height: number }
  /** The title row's text; `{file}` stands for the document's name. */
  title: string
  leftPane: PaneSpec | null
  rightPane: PaneSpec | null
  documentMinWidth: number
  /** Names of the status bar's items; the right end may name `ズーム` (the zoom controls) and `合わせる` (the fit button). */
  statusBar: { left: string[]; right: string[] }
  /** Hex colours of the title row's ground (`muted`) and of the caption buttons' symbols (`foreground`), written from tokens.json. */
  colors: { background: string; symbol: string }
  /** The same colours from the dark theme; absent where tokens.json declares none. */
  darkColors?: { background: string; symbol: string }
  heights: { titleRow: number; tabRow: number; commandArea: number; statusBar: number }
  tabs: TabSpec[]
  /** The groups in the order they collapse; groups it leaves out collapse after them, the rightmost first. */
  collapse: string[]
  /** The sentence and the three buttons (save, do not save, cancel) of the prompt on closing a changed document. */
  closePrompt: { sentence: string; buttons: string[] }
}
