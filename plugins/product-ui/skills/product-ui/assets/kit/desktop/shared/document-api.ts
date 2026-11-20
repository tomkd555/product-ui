// The functions the preload script exposes to the renderer with contextBridge, one per operation of a document
// window (references/desktop.md, Electron). The main process, the preload script and the renderer import the types.

/** The edit actions of `webContents` that `edit` runs on the focused element. */
export const EDIT_ACTIONS = ["undo", "redo", "cut", "copy", "paste", "selectAll", "delete"] as const
export type EditAction = (typeof EDIT_ACTIONS)[number]

export type OpenedDocument = { path: string; name: string; content: string }
export type SavedDocument = { path: string; name: string }

export type DocumentApi = {
  /** Asks for a file and returns its text; null when the reader cancels. */
  open: () => Promise<OpenedDocument | null>
  /** Writes the text to `path`; a null `path`, or one the main process never handed out, asks for a file name. Null when the reader cancels. */
  save: (path: string | null, content: string, suggestedName: string) => Promise<SavedDocument | null>
  /** Asks for a file name and writes the text there. Null when the reader cancels. */
  saveAs: (content: string, suggestedName: string) => Promise<SavedDocument | null>
  /** Asks for a file name and writes the exported text, or the bytes of a binary file, there; returns the path, or null when the reader cancels. */
  export: (content: string | Uint8Array, suggestedName: string) => Promise<string | null>
  /** Runs an edit action on the focused element of the window; the main process refuses a name outside EDIT_ACTIONS. */
  edit: (action: EditAction) => Promise<void>
  /** Tells the main process whether the document holds unsaved changes, so that it stops the window from closing. */
  setDirty: (dirty: boolean) => void
  /** Calls `listener` when the reader closes the window while the document holds unsaved changes; returns the way to stop listening. */
  onCloseRequest: (listener: () => void) => () => void
  /** Answers a close request: true closes the window, false keeps it open. */
  answerClose: (allow: boolean) => void
}

declare global {
  interface Window {
    /** Present in the Electron window; absent in a plain browser, where lib/host.ts answers from memory. */
    documentApi?: DocumentApi
  }
}
