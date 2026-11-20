// Exposes the document operations to the renderer: one function per operation and the close request and answer
// (references/desktop.md, Electron). Import it from the project's preload entry (`import "./document-api"`).
import { contextBridge, ipcRenderer } from "electron"
import type { DocumentApi } from "../shared/document-api"

const api: DocumentApi = {
  open: () => ipcRenderer.invoke("document:open"),
  save: (path, content, suggestedName) => ipcRenderer.invoke("document:save", path, content, suggestedName),
  saveAs: (content, suggestedName) => ipcRenderer.invoke("document:save-as", content, suggestedName),
  export: (content, suggestedName) => ipcRenderer.invoke("document:export", content, suggestedName),
  edit: (action) => ipcRenderer.invoke("document:edit", action),
  setDirty: (dirty) => ipcRenderer.send("document:dirty", dirty),
  onCloseRequest: (listener) => {
    const handler = () => listener()
    ipcRenderer.on("document:close-request", handler)
    return () => {
      ipcRenderer.removeListener("document:close-request", handler)
    }
  },
  answerClose: (allow) => ipcRenderer.send("document:close-answer", allow),
}

contextBridge.exposeInMainWorld("documentApi", api)
