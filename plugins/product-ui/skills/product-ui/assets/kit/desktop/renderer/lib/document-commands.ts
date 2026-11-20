// What the commands of the document operations do (new, open, save, save as, export, close, print, zoom, and the
// edit commands undo, redo, cut, copy, paste, select all and delete), through the host (lib/host.ts) and the document
// store. An application adds the handlers of its own commands, and may replace any of these by naming the same id;
// find and replace are the application's.
import type { CommandHandlers } from "@/lib/commands"
import { documentStore, UNTITLED, ZOOM_RANGE, type DocumentState } from "@/lib/document-state"
import { getHost } from "@/lib/host"
import type { EditAction } from "../../../shared/document-api"

export const ZOOM_PRESETS = [50, 75, 100, 150, 200]

/** The element the `zoom-fit` command fits into the document region; the application marks its page or canvas with it. */
export const DOCUMENT_PAGE = "[data-document-page]"

/**
 * The zoom, in whole percent within ZOOM_RANGE, at which the element marked `data-document-page` fits the document
 * region: the smaller of the width and height ratios, rounded down. The element's layout size (`offsetWidth` and
 * `offsetHeight`) is its size at 100%, so the application scales it with `transform`. 100 where no element carries the mark.
 */
export function fitZoom(): number {
  const page = document.querySelector<HTMLElement>(DOCUMENT_PAGE)
  const region = document.querySelector<HTMLElement>('[data-region="document"]')
  if (!page || !region || page.offsetWidth === 0 || page.offsetHeight === 0) return 100
  const style = getComputedStyle(region)
  const width = region.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight)
  const height = region.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom)
  const percent = Math.floor(Math.min(width / page.offsetWidth, height / page.offsetHeight) * 100)
  return Math.min(ZOOM_RANGE.max, Math.max(ZOOM_RANGE.min, percent))
}

export type DocumentContext = {
  /** The file extension, with its dot, that a new file name takes (`.drawio`). */
  extension?: string
  /** Runs `next` at once when the document holds no unsaved changes; otherwise shows the save prompt first. */
  guard: (next: () => void | Promise<void>) => void
  /** Shows a failure the reader must act on, as a dialog; `id` is the command that failed, whose title the dialog takes from FAILURE_TITLES. */
  fail: (message: string, id?: string) => void
  /** Shows a result the reader need not act on (「保存しました」) in the status bar. */
  notify: (text: string) => void
  /** Closes the window once the reader has answered the save prompt. */
  closeWindow: () => void
}

export function suggestedName(name: string | null, extension = ""): string {
  return name ?? `${UNTITLED}${extension}`
}

/** Saves to the document's path (asking for a file name where it has none); false when the reader cancels. */
export async function saveDocument(extension?: string): Promise<boolean> {
  const doc = documentStore.get()
  const saved = await getHost().save(doc.path, doc.content, suggestedName(doc.name, extension))
  if (!saved) return false
  documentStore.saved(saved.name, saved.path)
  return true
}

export async function saveDocumentAs(extension?: string): Promise<boolean> {
  const doc = documentStore.get()
  const saved = await getHost().saveAs(doc.content, suggestedName(doc.name, extension))
  if (!saved) return false
  documentStore.saved(saved.name, saved.path)
  return true
}

/** The handlers of the profile's document operations, for the state `doc`. */
export function documentHandlers(doc: DocumentState, context: DocumentContext): CommandHandlers {
  const attempt = async (id: string, job: () => Promise<unknown>) => {
    try {
      await job()
    } catch (error) {
      context.fail(error instanceof Error ? error.message : String(error), id)
    }
  }
  const edit = (id: string, action: EditAction) => () => attempt(id, () => getHost().edit(action))
  return {
    new: { run: () => context.guard(() => documentStore.reset()) },
    open: {
      run: () =>
        context.guard(() =>
          attempt("open", async () => {
            const opened = await getHost().open()
            if (opened) documentStore.load(opened.name, opened.path, opened.content)
          }),
        ),
    },
    save: { run: () => attempt("save", async () => (await saveDocument(context.extension)) && context.notify("保存しました")) },
    "save-as": { run: () => attempt("save-as", async () => (await saveDocumentAs(context.extension)) && context.notify("保存しました")) },
    export: {
      run: () =>
        attempt("export", async () => {
          if (await getHost().export(doc.content, suggestedName(doc.name, context.extension))) context.notify("エクスポートしました")
        }),
    },
    close: { run: () => context.guard(context.closeWindow) },
    print: { run: () => window.print() },
    undo: { enabled: doc.undoDepth > 0, run: edit("undo", "undo") },
    redo: { enabled: doc.redoDepth > 0, run: edit("redo", "redo") },
    cut: { enabled: doc.selection > 0, run: edit("cut", "cut") },
    copy: { enabled: doc.selection > 0, run: edit("copy", "copy") },
    paste: { run: edit("paste", "paste") },
    "select-all": { run: edit("select-all", "selectAll") },
    delete: { enabled: doc.selection > 0, run: edit("delete", "delete") },
    zoom: { menu: ZOOM_PRESETS.map((percent) => ({ label: `${percent}%`, run: () => documentStore.setZoom(percent) })) },
    "zoom-fit": { run: () => documentStore.setZoom(fitZoom()) },
  }
}
