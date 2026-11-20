// The main process of a document window (references/desktop.md, Electron): the window, its safe settings, no default
// menu, the close flow that waits for the renderer's save prompt, and the file operations the preload script exposes.
// The page is served from app://renderer/, IPC answers the app's own page alone, and every permission is refused
// except clipboard-read and clipboard-sanitized-write
// (Electron's security checklist, https://www.electronjs.org/docs/latest/tutorial/security).
import {
  app,
  BrowserWindow,
  dialog,
  ipcMain,
  Menu,
  nativeTheme,
  net,
  protocol,
  shell,
  type FileFilter,
  type IpcMainEvent,
  type IpcMainInvokeEvent,
  type MenuItemConstructorOptions,
} from "electron"
import { readFile, writeFile } from "node:fs/promises"
import { basename, join, normalize, sep } from "node:path"
import { pathToFileURL } from "node:url"
import { EDIT_ACTIONS, type EditAction, type OpenedDocument, type SavedDocument } from "../shared/document-api"
import type { WindowSpec } from "../shared/window-types"

export type DocumentWindowOptions = {
  /** WINDOW_SPEC from scaffold/window-spec.ts: the size, the minimum size, the title, the title row's height and its colours. */
  spec: Pick<WindowSpec, "size" | "minimum" | "title" | "heights" | "colors" | "darkColors">
  /** The application's id, the `appId` of electron-builder.yml: Windows groups the app's windows and notifications by it. */
  appId: string
  /** Absolute path of the built preload script. */
  preload: string
  /** Absolute path of the folder that holds the built renderer (out/renderer), served at app://renderer/ when `rendererUrl` is not set. */
  rendererDir: string
  /** The dev server's URL (`process.env["ELECTRON_RENDERER_URL"]` under electron-vite). */
  rendererUrl?: string
  /** Hex colours of the title row's ground and of the caption buttons' symbols (Electron reads no oklch); `spec.colors` when left out. */
  colors?: { background: string; symbol: string }
  /** The same colours of the dark theme; `spec.darkColors` when left out. Where either holds them, the window follows the system's choice. */
  darkColors?: { background: string; symbol: string }
  /** The file types of the open and save dialogs. */
  filters?: FileFilter[]
  /** The file types of the export dialog; `filters` when left out. */
  exportFilters?: FileFilter[]
}

const ALL_FILES: FileFilter[] = [{ name: "すべてのファイル", extensions: ["*"] }]

const APP_SCHEME = "app"
const APP_HOST = "renderer"
const APP_ORIGIN = `${APP_SCHEME}://${APP_HOST}`

function parse(url: string): URL | null {
  try {
    return new URL(url)
  } catch {
    return null
  }
}

/** Whether `url` (a page URL, or an origin as `senderFrame.origin` reports it) belongs to the app's own page. */
function isAppUrl(url: string): boolean {
  const parsed = parse(url)
  if (!parsed) return false
  if (parsed.protocol === `${APP_SCHEME}:` && parsed.host === APP_HOST) return true
  const dev = app.isPackaged ? undefined : process.env["ELECTRON_RENDERER_URL"]
  const devServer = dev ? parse(dev) : null
  return devServer !== null && parsed.origin === devServer.origin
}

/** Hands an https page or a mail address to the operating system; any other URL is dropped. */
function openExternally(url: string) {
  const parsed = parse(url)
  if (parsed && (parsed.protocol === "https:" || parsed.protocol === "mailto:")) void shell.openExternal(parsed.toString())
}

/** Maps the path of an app:// request to a file inside the renderer folder; null when it leaves the folder. */
function rendererFileOf(rendererDir: string, pathname: string): string | null {
  let decoded: string
  try {
    decoded = decodeURIComponent(pathname)
  } catch {
    return null
  }
  if (decoded.includes("\0")) return null
  const root = normalize(rendererDir).replace(/[\\/]+$/, "")
  const file = normalize(join(root, decoded === "/" ? "/index.html" : decoded))
  return file.startsWith(root + sep) && file.length > root.length + sep.length ? file : null
}

/** Registers an IPC handler that refuses a call from any frame other than the app's own page. */
function handle(channel: string, listener: (event: IpcMainInvokeEvent, ...args: unknown[]) => unknown) {
  ipcMain.handle(channel, (event, ...args: unknown[]) => {
    const origin = event.senderFrame?.origin
    if (origin === undefined || !isAppUrl(origin)) throw new Error(`ipc: sender refused: ${channel}`)
    return listener(event, ...args)
  })
}

// Paths this process handed to a window (by opening or saving); a save to any other path asks for a file name.
const known = new Set<string>()

function parentOf(event: IpcMainInvokeEvent) {
  return BrowserWindow.fromWebContents(event.sender) ?? undefined
}

function registerFileOperations(filters: FileFilter[], exportFilters: FileFilter[]) {
  handle("document:open", async (event): Promise<OpenedDocument | null> => {
    const parent = parentOf(event)
    const options = { properties: ["openFile" as const], filters }
    const picked = parent ? await dialog.showOpenDialog(parent, options) : await dialog.showOpenDialog(options)
    if (picked.canceled || picked.filePaths.length === 0) return null
    const path = picked.filePaths[0]
    known.add(path)
    return { path, name: basename(path), content: await readFile(path, "utf-8") }
  })

  const writeTo = async (
    event: IpcMainInvokeEvent,
    path: unknown,
    content: unknown,
    suggestedName: unknown,
    saveFilters: FileFilter[] = filters,
    binary = false,
  ) => {
    const validContent = typeof content === "string" || (binary && content instanceof Uint8Array)
    if (!validContent || typeof suggestedName !== "string" || (path !== null && typeof path !== "string")) {
      throw new Error("invalid document")
    }
    let target = path !== null && known.has(path) ? path : null
    if (target === null) {
      const parent = parentOf(event)
      const options = { defaultPath: suggestedName, filters: saveFilters }
      const picked = parent ? await dialog.showSaveDialog(parent, options) : await dialog.showSaveDialog(options)
      if (picked.canceled || !picked.filePath) return null
      target = picked.filePath
      known.add(target)
    }
    await (typeof content === "string" ? writeFile(target, content, "utf-8") : writeFile(target, content))
    return { path: target, name: basename(target) }
  }
  handle("document:save", (event, path, content, suggestedName): Promise<SavedDocument | null> => writeTo(event, path, content, suggestedName))
  handle("document:save-as", (event, content, suggestedName): Promise<SavedDocument | null> => writeTo(event, null, content, suggestedName))
  handle("document:export", async (event, content, suggestedName): Promise<string | null> => {
    const saved = await writeTo(event, null, content, suggestedName, exportFilters, true)
    return saved ? saved.path : null
  })
}

/** Runs a `webContents` edit action (cut, copy, paste, undo, redo, select all, delete) on the focused element; any other name is refused. */
function registerEditOperation() {
  handle("document:edit", (event, action) => {
    if (typeof action !== "string" || !EDIT_ACTIONS.includes(action as EditAction)) throw new Error("invalid edit action")
    event.sender[action as EditAction]()
  })
}

// The permissions the window grants to the app's own page: reading the clipboard and writing sanitized content to it.
const ALLOWED_PERMISSIONS = new Set(["clipboard-read", "clipboard-sanitized-write"])

/**
 * Stops the window's `close` event while the renderer reports unsaved changes, asks the renderer to show its save
 * prompt, and closes the window when the renderer answers that it may close.
 */
function installCloseFlow(win: BrowserWindow) {
  let unsaved = false
  let confirmed = false
  const onDirty = (event: IpcMainEvent, dirty: unknown) => {
    if (event.sender === win.webContents && typeof dirty === "boolean") unsaved = dirty
  }
  const onAnswer = (event: IpcMainEvent, allow: unknown) => {
    if (event.sender !== win.webContents || allow !== true) return
    confirmed = true
    win.close()
  }
  ipcMain.on("document:dirty", onDirty)
  ipcMain.on("document:close-answer", onAnswer)
  win.on("close", (event) => {
    if (!unsaved || confirmed) return
    event.preventDefault()
    win.webContents.send("document:close-request")
  })
  win.on("closed", () => {
    ipcMain.off("document:dirty", onDirty)
    ipcMain.off("document:close-answer", onAnswer)
  })
}

/**
 * Shows 切り取り, コピー and 貼り付け on a text field and コピー on selected text, on a right click and on Shift+F10. The items
 * carry no role, so the menu lists them without their keys, as Office's context menus do.
 */
function attachContextMenu(win: BrowserWindow) {
  win.webContents.on("context-menu", (_event, params) => {
    const items: MenuItemConstructorOptions[] = []
    if (params.isEditable) {
      items.push(
        { label: "切り取り(&T)", enabled: params.editFlags.canCut, click: () => win.webContents.cut() },
        { label: "コピー(&C)", enabled: params.editFlags.canCopy, click: () => win.webContents.copy() },
        { label: "貼り付け(&P)", enabled: params.editFlags.canPaste, click: () => win.webContents.paste() },
      )
    } else if (params.selectionText.trim() !== "") {
      items.push({ label: "コピー(&C)", click: () => win.webContents.copy() })
    }
    if (items.length > 0) Menu.buildFromTemplate(items).popup({ window: win })
  })
}

/** Creates the document window: no menu bar, the caption buttons drawn by Electron over the title row. */
export function createDocumentWindow(options: DocumentWindowOptions): BrowserWindow {
  const { spec } = options
  const light = options.colors ?? spec.colors
  const dark = options.darkColors ?? spec.darkColors
  const colorsNow = () => (dark && nativeTheme.shouldUseDarkColors ? dark : light)
  const colors = colorsNow()
  const win = new BrowserWindow({
    width: spec.size.width,
    height: spec.size.height,
    minWidth: spec.minimum.width,
    minHeight: spec.minimum.height,
    // Electron restores the window's position, size and maximized state by its name.
    name: "document",
    windowStatePersistence: true,
    show: false,
    title: spec.title.replace("{file}", "無題"),
    backgroundColor: colors.background,
    titleBarStyle: "hidden",
    titleBarOverlay: { color: colors.background, symbolColor: colors.symbol, height: spec.heights.titleRow },
    webPreferences: {
      preload: options.preload,
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  })
  win.once("ready-to-show", () => win.show())
  // The window stays on the app's page: an https or mailto link opens in the user's browser or mail program.
  win.webContents.setWindowOpenHandler(({ url }) => {
    openExternally(url)
    return { action: "deny" }
  })
  win.webContents.on("will-navigate", (event, url) => {
    if (isAppUrl(url)) return
    event.preventDefault()
    openExternally(url)
  })
  win.webContents.session.setPermissionRequestHandler((_contents, permission, callback, details) =>
    callback(ALLOWED_PERMISSIONS.has(permission) && isAppUrl(details.requestingUrl)),
  )
  win.webContents.session.setPermissionCheckHandler((_contents, permission, requestingOrigin) =>
    ALLOWED_PERMISSIONS.has(permission) && isAppUrl(requestingOrigin),
  )
  attachContextMenu(win)
  if (dark) {
    const repaint = () => {
      const now = colorsNow()
      win.setBackgroundColor(now.background)
      win.setTitleBarOverlay({ color: now.background, symbolColor: now.symbol, height: spec.heights.titleRow })
    }
    nativeTheme.on("updated", repaint)
    win.on("closed", () => nativeTheme.off("updated", repaint))
  }
  if (!app.isPackaged) {
    // F12 is 名前を付けて保存, so DevTools sit on Ctrl+Shift+I and only in development.
    win.webContents.on("before-input-event", (event, input) => {
      if (input.type === "keyDown" && input.control && input.shift && input.key.toLowerCase() === "i") {
        win.webContents.toggleDevTools()
        event.preventDefault()
      }
    })
  }
  installCloseFlow(win)
  void win.loadURL(options.rendererUrl ?? `${APP_ORIGIN}/index.html`)
  return win
}

/**
 * Starts the application: one instance, the app:// scheme for the renderer, no default menu, the file operations and
 * the window. Call it from the main entry before the `ready` event, as electron-vite's main entry runs.
 */
export function runDocumentApp(options: DocumentWindowOptions) {
  protocol.registerSchemesAsPrivileged([{ scheme: APP_SCHEME, privileges: { standard: true, secure: true, supportFetchAPI: true } }])
  // A second launch hands over to the running window: two processes would each write the same user-data folder.
  if (!app.requestSingleInstanceLock()) {
    app.quit()
    return
  }
  app.on("second-instance", () => {
    const [win] = BrowserWindow.getAllWindows()
    if (!win) return
    if (win.isMinimized()) win.restore()
    win.focus()
  })
  Menu.setApplicationMenu(null)
  app.whenReady().then(() => {
    app.setAppUserModelId(options.appId)
    protocol.handle(APP_SCHEME, (request) => {
      const url = new URL(request.url)
      const file = url.host === APP_HOST ? rendererFileOf(options.rendererDir, url.pathname) : null
      return file === null ? new Response(null, { status: 404 }) : net.fetch(pathToFileURL(file).toString())
    })
    registerEditOperation()
    registerFileOperations(options.filters ?? ALL_FILES, options.exportFilters ?? options.filters ?? ALL_FILES)
    createDocumentWindow(options)
    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) createDocumentWindow(options)
    })
  })
  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit()
  })
}
