// The state of the open document: its name, text, unsaved changes and the figures the commands and the status bar read.
// The title row and document.title print one string (references/desktop.md, Title row).
import { useEffect, useSyncExternalStore } from "react"

export type DocumentState = {
  name: string | null
  path: string | null
  content: string
  dirty: boolean
  undoDepth: number
  redoDepth: number
  selection: number
  zoom: number
}

export const UNTITLED = "無題"
export const ZOOM_RANGE = { min: 10, max: 400, step: 10 }

const initial: DocumentState = { name: null, path: null, content: "", dirty: false, undoDepth: 0, redoDepth: 0, selection: 0, zoom: 100 }
let state = initial
const listeners = new Set<() => void>()

function set(patch: Partial<DocumentState>) {
  state = { ...state, ...patch }
  listeners.forEach((listener) => listener())
}

/** The store the application writes to: `edit` after each change, `setHistory` and `setSelection` as its stacks change. */
export const documentStore = {
  get: () => state,
  subscribe: (listener: () => void) => {
    listeners.add(listener)
    return () => {
      listeners.delete(listener)
    }
  },
  /** A new, unsaved and unchanged document. */
  reset: () => set({ ...initial }),
  /** An untitled document that holds `content` and has no unsaved changes, for an application that starts from a template. */
  create: (content: string) => set({ ...initial, content }),
  /** Replaces the document with one just opened. */
  load: (name: string, path: string, content: string) => set({ ...initial, name, path, content }),
  /** Sets the text and marks the document as changed. */
  edit: (content: string) => set({ content, dirty: true }),
  /** Marks the document as changed without setting its text, for an application that keeps its model elsewhere. */
  touch: () => set({ dirty: true }),
  saved: (name: string, path: string) => set({ name, path, dirty: false }),
  setHistory: (undoDepth: number, redoDepth: number) => set({ undoDepth, redoDepth }),
  setSelection: (selection: number) => set({ selection }),
  setZoom: (zoom: number) => set({ zoom: Math.min(ZOOM_RANGE.max, Math.max(ZOOM_RANGE.min, Math.round(zoom))) }),
}

export function useDocument(): DocumentState {
  return useSyncExternalStore(documentStore.subscribe, documentStore.get)
}

/** `<file> - <product>` from the template of the brief's title row: `*` after the name while the document is changed. */
export function documentTitle(template: string, name: string | null, dirty: boolean): string {
  return template.replace("{file}", `${name ?? UNTITLED}${dirty ? "*" : ""}`)
}

/** Keeps document.title equal to the title row's text and returns it. */
export function useDocumentTitle(template: string): string {
  const { name, dirty } = useDocument()
  const title = documentTitle(template, name, dirty)
  useEffect(() => {
    document.title = title
  }, [title])
  return title
}
