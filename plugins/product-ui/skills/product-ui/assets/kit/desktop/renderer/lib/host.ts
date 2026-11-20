// The renderer's access to the file system: the preload script's functions in the Electron window, and an in-memory
// stand-in where they are absent, so that the renderer also runs in a plain browser (the review captures it there).
import type { DocumentApi, OpenedDocument } from "../../../shared/document-api"

export type DocumentHost = DocumentApi

let sample: OpenedDocument = { path: "sample.txt", name: "sample.txt", content: "" }
let memory: DocumentHost | null = null

/** The document `open` returns in a plain browser. */
export function setSampleDocument(document: OpenedDocument) {
  sample = document
}

/** The sample document where the page was asked for it with `?doc=sample` in a plain browser, else null (the capture's way to a filled document). */
export function sampleFromQuery(): OpenedDocument | null {
  if (window.documentApi) return null
  return new URLSearchParams(window.location.search).get("doc") === "sample" ? { ...sample } : null
}

function createMemoryHost(): DocumentHost {
  const files = new Map<string, string | Uint8Array>()
  const keep = (name: string, content: string | Uint8Array) => {
    files.set(name, content)
    return { path: name, name }
  }
  return {
    open: async () => ({ ...sample }),
    save: async (path, content, suggestedName) => keep(path ?? suggestedName, content),
    saveAs: async (content, suggestedName) => keep(suggestedName, content),
    export: async (content, suggestedName) => keep(suggestedName, content).path,
    // A plain browser has no clipboard command of its own: execCommand answers where the browser still has it.
    edit: async (action) => {
      if (typeof document.execCommand === "function") document.execCommand(action)
    },
    setDirty: () => {},
    onCloseRequest: () => () => {},
    answerClose: () => {},
  }
}

/** The preload script's API when the window has it, else the in-memory stand-in. */
export function getHost(): DocumentHost {
  if (window.documentApi) return window.documentApi
  memory ??= createMemoryHost()
  return memory
}
