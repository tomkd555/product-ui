// The command table of the document window: what each command of scaffold/command-set.ts runs, the tooltip, and the
// keys. A command runs the same way from a click, a key or a key tip, and each run dispatches `product-ui:command`
// on window with the command's id, which the review's key probe reads (references/desktop.md, Markers the checks read).
import { useEffect, useRef } from "react"

export type CommandSpec = {
  id: string
  place: "quick-access" | "file-view" | "ribbon"
  tab: string
  group: string
  label: string
  size: "" | "large" | "small" | "menu" | "check"
  action: string
  /** `none`, or the keys written as the profile writes them, joined by `, `. */
  keys: string
  /** `none`, or the letters after Alt (after the tab's letters for a command of a tab). */
  keytip: string
  /** `always`, or the condition under which the command runs. */
  enabledWhen: string
}

export type MenuItem = { label: string; run: () => void }

/** What a command does at run time. `enabled` defaults to true; `menu` lists the items a `menu` command opens. */
export type CommandHandler = {
  run?: () => void | Promise<void>
  enabled?: boolean
  checked?: boolean
  menu?: MenuItem[]
}

export type CommandHandlers = Record<string, CommandHandler | undefined>

export const COMMAND_EVENT = "product-ui:command"

/** The keys of a command as a list. */
export function keysOfSpec(spec: CommandSpec): string[] {
  return spec.keys === "none" || spec.keys === "" ? [] : spec.keys.split(", ")
}

/** The tooltip: the name and the keys, 「上書き保存 (Ctrl+S)」; a disabled command adds the condition under which it runs. */
export function tooltipText(spec: CommandSpec, enabled: boolean): string {
  const keys = keysOfSpec(spec)
  const name = keys.length > 0 ? `${spec.label} (${keys.join(", ")})` : spec.label
  return !enabled && spec.enabledWhen !== "always" ? `${name}\n${spec.enabledWhen}と実行できます` : name
}

export function isEnabled(spec: CommandSpec, handlers: CommandHandlers): boolean {
  return handlers[spec.id]?.enabled !== false
}

/** Dispatches the command event. A command with no handler still dispatches it, so the table can be probed before the application wires it. */
export function announceCommand(id: string) {
  window.dispatchEvent(new CustomEvent(COMMAND_EVENT, { detail: { id } }))
}

/** Runs a command unless it is disabled; the result is the handler's, for a caller that waits for it. */
export function runCommand(spec: CommandSpec, handlers: CommandHandlers): void | Promise<void> {
  if (!isEnabled(spec, handlers)) return
  announceCommand(spec.id)
  return handlers[spec.id]?.run?.()
}

const MODIFIERS = ["Ctrl", "Shift", "Alt"] as const

/** A key event as the profile writes a key: `F12`, `Ctrl+F`, `Shift+F10`. */
export function keyOfEvent(event: KeyboardEvent): string {
  const held = { Ctrl: event.ctrlKey || event.metaKey, Shift: event.shiftKey, Alt: event.altKey }
  const key = event.key.length === 1 ? event.key.toUpperCase() : event.key
  return [...MODIFIERS.filter((name) => held[name]), key].join("+")
}

// While the focus is in a text field outside the document area these keys act on the field's text and reach no command.
// In the document area, Ctrl+Z and Ctrl+Y run the window's undo and redo; the other six keep acting on the text and
// announce their command.
const FIELD_KEYS = new Set(["Ctrl+X", "Ctrl+C", "Ctrl+V", "Ctrl+Z", "Ctrl+Y", "Ctrl+A", "Delete", "Backspace"])
const DOCUMENT_RUNS = new Set(["Ctrl+Z", "Ctrl+Y"])
const DOCUMENT_AREA = '[data-region="document"]'
const TEXT_INPUT_TYPES = new Set(["", "text", "search", "url", "tel", "email", "password", "number"])

export function isTextField(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  if (target instanceof HTMLInputElement) return TEXT_INPUT_TYPES.has(target.type)
  return target instanceof HTMLTextAreaElement || target.isContentEditable
}

export function dialogOpen(): boolean {
  return Array.from(document.querySelectorAll('[role="alertdialog"], [role="dialog"]')).some((el) => el.getClientRects().length > 0)
}

/**
 * The keys of the table run their commands: on `keydown`, a key that a command lists runs it and the browser's own
 * action for the key is stopped. The text-field rules above and an open dialog leave the key alone.
 */
export function useCommandKeys(specs: CommandSpec[], handlers: CommandHandlers) {
  const latest = useRef(handlers)
  useEffect(() => {
    latest.current = handlers
  })
  useEffect(() => {
    const byKey = new Map<string, CommandSpec>()
    for (const spec of specs) {
      for (const key of keysOfSpec(spec)) if (!byKey.has(key)) byKey.set(key, spec)
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.isComposing || event.keyCode === 229 || event.repeat || dialogOpen()) return
      const key = keyOfEvent(event)
      const spec = byKey.get(key)
      if (!spec) return
      if (FIELD_KEYS.has(key) && isTextField(event.target)) {
        const inDocument = event.target instanceof Element && event.target.closest(DOCUMENT_AREA) !== null
        if (!inDocument) return
        if (!DOCUMENT_RUNS.has(key)) {
          if (isEnabled(spec, latest.current)) announceCommand(spec.id)
          return
        }
      }
      event.preventDefault()
      void runCommand(spec, latest.current)
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [specs])
}
