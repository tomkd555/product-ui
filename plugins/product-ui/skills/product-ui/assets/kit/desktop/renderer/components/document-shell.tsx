// The document window: the title row, the ribbon, the task panes beside the document, the status bar, the file view
// and the save prompt, laid out as references/desktop.md describes, with the window's keys (the command table's keys,
// Alt and F10 for key tips, F6, Ctrl+F1, Shift+F10, Esc). The window never scrolls as a whole.
// A state the review captures is read once from the URL: `?view=file&page=new`, `?pane=properties`, `?prompt=save`,
// `?doc=sample` (a plain browser only); the window starts on a new untitled document and keeps its state in memory.
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import type { Icon } from "@/components/command-button"
import { FileView, isPageItem } from "@/components/file-view"
import { KeyTipContext, type KeyTipScope } from "@/components/key-tip"
import { Ribbon } from "@/components/ribbon"
import { ErrorNotice, SavePrompt } from "@/components/save-prompt"
import { StatusBar } from "@/components/status-bar"
import { TaskPane } from "@/components/task-pane"
import { TitleRow } from "@/components/title-row"
import { announceCommand, dialogOpen, isTextField, runCommand, useCommandKeys, type CommandHandlers, type CommandSpec } from "@/lib/commands"
import { documentHandlers, saveDocument } from "@/lib/document-commands"
import { documentStore, useDocument, useDocumentTitle } from "@/lib/document-state"
import { getHost, sampleFromQuery } from "@/lib/host"
import type { WindowSpec } from "../../../shared/window-types"

type Side = "left" | "right"

/** How long a result message stays in the status bar, in milliseconds. */
export const NOTIFY_MS = 5000

/** What the application's handlers can do to the window. */
export type ShellApi = {
  paneOpen: (side: Side) => boolean
  togglePane: (side: Side) => void
  showFile: (page?: string) => void
  /** Closes the file view and shows the document, for a page's own control (a template of 新規) that returns to it. */
  showDocument: () => void
  /** Shows `text` at the left of the status bar for NOTIFY_MS, then returns to the `status` items; a second call replaces the first. */
  notify: (text: string) => void
  /** Shows the kit's error dialog with `message`; `operation` is the command id of what failed, whose title FAILURE_TITLES gives (`save`: 「保存できませんでした」). */
  fail: (message: string, operation?: string) => void
  /** Runs `next` at once, or after the save prompt where the document holds unsaved changes. */
  guard: (next: () => void | Promise<void>) => void
}

export type PaneContent = { id: string; node: ReactNode }

type Failure = { message: string; operation?: string }

type Prompt = { proceed: () => void | Promise<void>; cancel?: () => void }

const REGIONS = ["tab-row", "left-pane", "document", "right-pane", "status-bar"]

function closeWindow() {
  getHost().setDirty(false)
  window.close()
}

export function DocumentShell({
  spec,
  commands,
  appHandlers,
  panes,
  pages,
  status,
  icons,
  groupIcons,
  launchers,
  extension,
  children,
}: {
  /** WINDOW_SPEC from scaffold/window-spec.ts. */
  spec: WindowSpec
  /** COMMAND_SET from scaffold/command-set.ts. */
  commands: CommandSpec[]
  /** The handlers of the application's own commands (and any operation it replaces), by command id. */
  appHandlers?: (api: ShellApi) => CommandHandlers
  /** The content of the task panes; `id` is what `?pane=` names (`left` and `right` also work). */
  panes?: { left?: PaneContent; right?: PaneContent }
  /** The page of each file view item that shows one, by command id. */
  pages?: Record<string, (context: { run: () => void }) => ReactNode>
  /** The text of the status bar's items, by name. */
  status?: Record<string, string>
  icons?: Record<string, Icon>
  groupIcons?: Record<string, Icon>
  launchers?: Record<string, () => void>
  extension?: string
  /** The document area. */
  children: ReactNode
}) {
  const query = useRef(new URLSearchParams(window.location.search))
  const doc = useDocument()
  const title = useDocumentTitle(spec.title)

  const [view, setView] = useState<"document" | "file">(query.current.get("view") === "file" ? "file" : "document")
  const [page, setPage] = useState<string | null>(query.current.get("page"))
  const [tab, setTab] = useState(spec.tabs[0]?.name ?? "")
  const [override, setOverride] = useState<"hidden" | "shown" | null>(null)
  const [hidden, setHidden] = useState(false)
  const [peek, setPeek] = useState(false)
  const [tips, setTips] = useState<{ scope: KeyTipScope; typed: string }>({ scope: null, typed: "" })
  const [prompt, setPrompt] = useState<Prompt | null>(query.current.get("prompt") === "save" ? { proceed: () => {} } : null)
  const [error, setError] = useState<Failure | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const noticeTimer = useRef<number | undefined>(undefined)
  const wanted = query.current.get("pane")
  const [open, setOpen] = useState<Record<Side, boolean>>({
    left: (spec.leftPane?.open ?? false) || wanted === "left" || (wanted !== null && wanted === panes?.left?.id),
    right: (spec.rightPane?.open ?? false) || wanted === "right" || (wanted !== null && wanted === panes?.right?.id),
  })
  const [widths, setWidths] = useState({ left: spec.leftPane?.width ?? 0, right: spec.rightPane?.width ?? 0 })
  const [bodyWidth, setBodyWidth] = useState(0)
  const body = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = body.current
    if (!el) return
    const watch = new ResizeObserver((entries) => setBodyWidth(entries[0].contentRect.width))
    watch.observe(el)
    return () => watch.disconnect()
  }, [])

  useEffect(() => {
    const sample = sampleFromQuery()
    if (!sample) return
    // The capture's sample has a selection and one undo step, so that undo, cut, copy and delete are enabled for the commands probe.
    documentStore.load(sample.name, sample.path, sample.content)
    documentStore.setSelection(sample.content.length)
    documentStore.setHistory(1, 0)
  }, [])
  useEffect(() => () => window.clearTimeout(noticeTimer.current), [])
  const notify = useCallback((text: string) => {
    window.clearTimeout(noticeTimer.current)
    setNotice(text)
    noticeTimer.current = window.setTimeout(() => setNotice(null), NOTIFY_MS)
  }, [])
  useEffect(() => getHost().setDirty(doc.dirty), [doc.dirty])
  useEffect(
    () =>
      getHost().onCloseRequest(() =>
        setPrompt({ proceed: () => getHost().answerClose(true), cancel: () => getHost().answerClose(false) }),
      ),
    [],
  )

  const guard = useCallback((next: () => void | Promise<void>) => {
    if (documentStore.get().dirty) setPrompt({ proceed: next })
    else void next()
  }, [])

  const api: ShellApi = {
    paneOpen: (side) => open[side],
    togglePane: (side) => setOpen((now) => ({ ...now, [side]: !now[side] })),
    showFile: (target) => {
      setView("file")
      setPage(target ?? null)
    },
    showDocument: () => setView("document"),
    fail: (message, operation) => setError({ message, operation }),
    notify,
    guard,
  }
  const handlers: CommandHandlers = {}
  const merged = {
    ...documentHandlers(doc, { extension, guard, fail: (message, id) => setError({ message, operation: id }), notify, closeWindow }),
    back: { run: () => setView("document") },
    ...appHandlers?.(api),
  }
  // Any command that runs closes the file view first.
  for (const [id, handler] of Object.entries(merged)) {
    handlers[id] = handler && { ...handler, run: handler.run && (() => (setView("document"), handler.run?.())) }
  }

  const ribbon = useMemo(() => commands.filter((c) => c.place === "ribbon"), [commands])
  const quick = useMemo(() => commands.filter((c) => c.place === "quick-access"), [commands])
  const fileItems = useMemo(() => commands.filter((c) => c.place === "file-view"), [commands])
  const unique = useMemo(() => commands.filter((c, i) => commands.findIndex((o) => o.id === c.id) === i), [commands])
  useCommandKeys(unique, handlers)

  const activateFileItem = (item: CommandSpec) => {
    if (item.id === "back") return setView("document")
    if (isPageItem(item) && pages?.[item.id]) {
      announceCommand(item.id)
      return setPage(item.id)
    }
    void runCommand(item, handlers)
    setView("document")
  }

  // The window follows the system's light or dark choice where tokens.json declares a dark theme (spec.darkColors); theme.css swaps its palette under .dark.
  useEffect(() => {
    if (!spec.darkColors) return
    const media = window.matchMedia("(prefers-color-scheme: dark)")
    const apply = () => document.documentElement.classList.toggle("dark", media.matches)
    apply()
    media.addEventListener("change", apply)
    return () => media.removeEventListener("change", apply)
  }, [spec.darkColors])

  const state = useRef({ tips, view, hidden, override, peek, tab, prompt, error })
  useEffect(() => {
    state.current = { tips, view, hidden, override, peek, tab, prompt, error }
  })
  // Alt shows the key tips when it is released with no other key pressed while it was held, as Office does, so
  // Alt+Tab, Alt+Shift and Alt+半角/全角 leave them off.
  const altAlone = useRef(false)
  const act = useRef<(event: KeyboardEvent) => void>(() => {})
  useEffect(() => {
    const offTips = () => setTips({ scope: null, typed: "" })
    const targets = (scope: string): { tip: string; run: () => void }[] => {
      if (scope === "root") {
        return [
          { tip: "F", run: () => (setView("file"), setTips({ scope: "file", typed: "" })) },
          ...spec.tabs.map((entry) => ({
            tip: entry.keytip,
            run: () => {
              setTab(entry.name)
              if (state.current.hidden) setPeek(true)
              setTips({ scope: `tab:${entry.name}`, typed: "" })
            },
          })),
          ...quick.map((item) => ({ tip: item.keytip, run: () => (offTips(), void runCommand(item, handlers)) })),
        ]
      }
      if (scope === "file") return fileItems.map((item) => ({ tip: item.keytip, run: () => (offTips(), activateFileItem(item)) }))
      const commandTips = ribbon
        .filter((item) => `tab:${item.tab}` === scope)
        .map((item) => ({
          tip: item.keytip,
          run: () => {
            offTips()
            const button = document.querySelector<HTMLElement>(`[data-region="command-area"] [data-command="${item.id}"]`)
            // A rendered button takes the click, which opens a menu and closes a collapsed group's panel; a collapsed group renders none until its panel opens.
            if (button) return button.click()
            setPeek(false)
            void runCommand(item, handlers)
          },
        }))
      // A collapsed group's button opens its panel and keeps the tab's key tips, so the commands' tips show inside the panel.
      const groupTips = Array.from(document.querySelectorAll<HTMLElement>("[data-group-tip]")).map((button) => ({
        tip: button.getAttribute("data-group-tip") ?? "",
        run: () => (button.click(), setTips({ scope, typed: "" })),
      }))
      return [...commandTips, ...groupTips]
    }
    const press = (scope: string, typed: string) => {
      const found = targets(scope)
      const exact = found.find((entry) => entry.tip === typed)
      if (exact) exact.run()
      else if (found.some((entry) => entry.tip.startsWith(typed))) setTips({ scope, typed })
    }
    const focusRegion = (step: number) => {
      const present = REGIONS.filter((name) => document.querySelector(`[data-region="${name}"]:not([hidden])`))
      const current = (document.activeElement as HTMLElement | null)?.closest("[data-region]")?.getAttribute("data-region")
      const at = present.indexOf(current === "command-area" || current === "title-row" ? "tab-row" : (current ?? ""))
      const next = present[(at + step + present.length) % present.length]
      const region = document.querySelector<HTMLElement>(`[data-region="${next}"]`)
      const target =
        next === "tab-row" ? region?.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]') : next === "status-bar" ? region?.querySelector<HTMLElement>("button, input") : region
      target?.focus()
    }
    act.current = (event) => {
      const s = state.current
      if (event.key !== "Alt") altAlone.current = false
      if (s.prompt || s.error !== null || dialogOpen()) return
      const plain = !event.ctrlKey && !event.metaKey && !event.shiftKey
      if (s.tips.scope !== null) {
        if (event.key === "Escape") {
          event.preventDefault()
          event.stopPropagation()
          if (s.tips.scope === "root") {
            offTips()
            document.querySelector<HTMLElement>('[data-region="document"]')?.focus()
          } else {
            setTips({ scope: "root", typed: "" })
            setPeek(false)
            setView("document")
          }
          return
        }
        if (event.key === "Alt") return
        if (event.key === "F10") return (event.preventDefault(), offTips())
        if (event.key.length === 1 && !event.ctrlKey && !event.metaKey) {
          event.preventDefault()
          press(s.tips.scope, s.tips.typed + event.key.toUpperCase())
        }
        return
      }
      if (event.key === "Alt" && !event.ctrlKey && !event.shiftKey) {
        event.preventDefault()
        if (!event.repeat) altAlone.current = true
      } else if (event.key === "F10" && plain) {
        event.preventDefault()
        setTips({ scope: "root", typed: "" })
      } else if (event.altKey && plain && event.key.length === 1) {
        event.preventDefault()
        setTips({ scope: "root", typed: "" })
        press("root", event.key.toUpperCase())
      } else if (event.key === "Escape") {
        if (s.view === "file") setView("document")
        else if (s.peek) setPeek(false)
      } else if (event.key === "F6" && !event.ctrlKey && !event.altKey) {
        event.preventDefault()
        focusRegion(event.shiftKey ? -1 : 1)
      } else if (event.key === "F1" && event.ctrlKey && !event.shiftKey && !event.altKey) {
        event.preventDefault()
        setOverride((s.override ? s.override === "hidden" : s.hidden) ? "shown" : "hidden")
        setPeek(false)
      } else if (event.key === "F10" && event.shiftKey && !event.ctrlKey && !isTextField(document.activeElement)) {
        // A text field keeps Shift+F10, so the main process shows its 切り取り, コピー and 貼り付け menu.
        event.preventDefault()
        const el = document.activeElement
        if (el instanceof HTMLElement) {
          const rect = el.getBoundingClientRect()
          el.dispatchEvent(
            new MouseEvent("contextmenu", { bubbles: true, clientX: rect.left + rect.width / 2, clientY: rect.top + rect.height / 2 }),
          )
        }
      }
    }
  })
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => act.current(event)
    const onKeyUp = (event: KeyboardEvent) => {
      if (event.key !== "Alt") return
      const alone = altAlone.current
      altAlone.current = false
      if (alone && state.current.tips.scope === null && !state.current.prompt && state.current.error === null && !dialogOpen()) {
        event.preventDefault()
        setTips({ scope: "root", typed: "" })
      }
    }
    const onBlur = () => {
      altAlone.current = false
      setTips({ scope: null, typed: "" })
    }
    window.addEventListener("keydown", onKeyDown, true)
    window.addEventListener("keyup", onKeyUp, true)
    window.addEventListener("blur", onBlur)
    return () => {
      window.removeEventListener("keydown", onKeyDown, true)
      window.removeEventListener("keyup", onKeyUp, true)
      window.removeEventListener("blur", onBlur)
    }
  }, [])

  // The right pane closes first, then the left, when the document would fall under its minimum width. A pane closed
  // for width stays mounted and hidden, so its fields keep their drafts.
  let showLeft = open.left && spec.leftPane !== null
  let showRight = open.right && spec.rightPane !== null
  const wantLeft = showLeft
  const wantRight = showRight
  const used = () => spec.documentMinWidth + (showLeft ? widths.left : 0) + (showRight ? widths.right : 0)
  if (bodyWidth > 0 && used() > bodyWidth) showRight = false
  if (bodyWidth > 0 && used() > bodyWidth) showLeft = false
  const room = (side: Side) => bodyWidth - spec.documentMinWidth - (side === "left" ? (showRight ? widths.right : 0) : showLeft ? widths.left : 0)

  const pane = (side: Side, shown: boolean) => {
    const config = side === "left" ? spec.leftPane : spec.rightPane
    const content = panes?.[side]
    if (!config) return null
    return (
      <TaskPane
        side={side}
        title={config.title}
        width={widths[side]}
        defaultWidth={config.width}
        min={config.min}
        max={Math.max(config.min, Math.min(config.max, room(side)))}
        onWidth={(width) => setWidths((now) => ({ ...now, [side]: width }))}
        onClose={() => setOpen((now) => ({ ...now, [side]: false }))}
        hidden={!shown}
      >
        {content?.node}
      </TaskPane>
    )
  }

  const confirmed = (after: () => void | Promise<void>) => {
    setPrompt(null)
    void after()
  }
  const [saveWord, discardWord, cancelWord] = spec.closePrompt.buttons
  // While the file view covers the window, what lies under it takes no focus and no click.
  const covered = view === "file"

  return (
    <KeyTipContext.Provider value={tips}>
      <div className="relative flex h-screen min-w-0 flex-col overflow-hidden bg-background text-foreground">
        <TitleRow height={spec.heights.titleRow} title={title} commands={quick} handlers={handlers} icons={icons} />
        <div className="contents" inert={covered}>
          <Ribbon
            spec={spec}
            commands={ribbon}
            handlers={handlers}
            icons={icons}
            groupIcons={groupIcons}
            launchers={launchers}
            tab={tab}
            onTab={setTab}
            onFile={() => setView((now) => (now === "file" ? "document" : "file"))}
            fileOpen={view === "file"}
            override={override}
            onHidden={setHidden}
            peek={peek}
            onPeek={setPeek}
          />
        </div>
        <div ref={body} inert={covered} className="flex min-h-0 flex-1 border-t border-border">
          {wantLeft && pane("left", showLeft)}
          <main data-region="document" tabIndex={-1} style={{ minWidth: spec.documentMinWidth }} className="min-w-0 flex-1 overflow-auto outline-none">
            {children}
          </main>
          {wantRight && pane("right", showRight)}
        </div>
        <div className="contents" inert={covered}>
          <StatusBar
            height={spec.heights.statusBar}
            left={spec.statusBar.left}
            right={spec.statusBar.right}
            values={status}
            notice={notice}
            zoom={doc.zoom}
            fit={commands.find((c) => c.id === "zoom-fit")}
            handlers={handlers}
          />
        </div>
        {view === "file" && (
          <FileView
            top={spec.heights.titleRow}
            commands={fileItems}
            handlers={handlers}
            icons={icons}
            page={page}
            pages={pages}
            onActivate={(item) => {
              if (item.id === "back" || !(isPageItem(item) && pages?.[item.id])) activateFileItem(item)
              else setPage(item.id)
            }}
            onRun={(item) => (void runCommand(item, handlers), setView("document"))}
          />
        )}
        <SavePrompt
          open={prompt !== null}
          sentence={spec.closePrompt.sentence}
          buttons={[saveWord, discardWord, cancelWord]}
          onSave={() => {
            const current = prompt
            if (!current) return
            void saveDocument(extension).then(
              (saved) => (saved ? confirmed(current.proceed) : setPrompt(null)),
              (failure: unknown) => {
                setPrompt(null)
                setError({ message: failure instanceof Error ? failure.message : String(failure), operation: "save" })
              },
            )
          }}
          onDiscard={() => prompt && confirmed(prompt.proceed)}
          onCancel={() => {
            prompt?.cancel?.()
            setPrompt(null)
          }}
        />
        <ErrorNotice message={error?.message ?? null} operation={error?.operation} onClose={() => setError(null)} />
      </div>
    </KeyTipContext.Provider>
  )
}
