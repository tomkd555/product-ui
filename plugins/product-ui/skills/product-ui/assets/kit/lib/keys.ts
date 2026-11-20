// The keys of an entry screen, as the brief's Conventions section gives them (references/profiles.md):
// Enter moves from field to field, and a function key or a shortcut runs the button that shows it.
import { useEffect, type RefObject } from "react"

export type EnterKeys = { enter: "next-field" | "none"; enterLast: "register" | "none" }

const OWN_ENTER = new Set(["submit", "button", "reset", "image", "file"])

const FIELDS = 'input, select, textarea, [role="combobox"], [role="checkbox"], [role="radio"], [role="switch"]'

/** The controls Enter moves to, in the order of the document: the fields the reader fills. */
function fieldsOf(root: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(FIELDS)).filter(
    (el) =>
      !(el as HTMLInputElement).disabled &&
      !(el instanceof HTMLInputElement && (el.readOnly || el.type === "hidden" || OWN_ENTER.has(el.type))) &&
      el.tabIndex !== -1 &&
      el.getClientRects().length > 0,
  )
}

/**
 * Under `enter: "next-field"`, Enter in a field of `ref` moves the focus to the next field and Shift+Enter to the
 * previous one. A textarea, a button and an open list keep their own Enter, and so does a text being converted by an
 * input method; Enter in the field before one of them moves the focus onto it.
 * In the last field Enter calls `onRegister` where `enterLast` is `"register"`, and does nothing otherwise.
 * In the lines of a slip, Enter in the last field of the last line opens the next line (the button marked
 * `data-line-add`) while that line holds a value; from an empty last line Enter goes on as above.
 * The form carries `data-enter="next-field"`, which the checks read.
 */
export function useEnterKeys(ref: RefObject<HTMLElement | null>, keys: EnterKeys, onRegister?: () => void) {
  const { enter, enterLast } = keys
  useEffect(() => {
    const root = ref.current
    if (!root || enter !== "next-field") return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Enter" || event.isComposing || event.keyCode === 229 || event.ctrlKey || event.altKey || event.metaKey) return
      const target = event.target
      if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) return
      if (target.getAttribute("aria-expanded") === "true") return
      const fields = fieldsOf(root)
      const at = fields.indexOf(target)
      if (at === -1) return
      event.preventDefault()
      const row = target.closest<HTMLElement>("tbody tr")
      const add = row && !row.nextElementSibling ? root.querySelector<HTMLButtonElement>("[data-line-add]") : null
      if (!event.shiftKey && row && add && fieldsOf(row).at(-1) === target && fieldsOf(row).some((el) => el instanceof HTMLInputElement && el.type !== "checkbox" && el.type !== "radio" && el.value.trim() !== "")) {
        add.click()
        requestAnimationFrame(() => {
          const opened = row.parentElement?.lastElementChild
          if (opened instanceof HTMLElement) fieldsOf(opened)[0]?.focus()
        })
        return
      }
      const next = fields[at + (event.shiftKey ? -1 : 1)]
      if (next) {
        next.focus()
        if (next instanceof HTMLInputElement) next.select()
      } else if (!event.shiftKey && enterLast === "register") {
        onRegister?.()
      }
    }
    root.addEventListener("keydown", onKeyDown)
    return () => root.removeEventListener("keydown", onKeyDown)
  }, [ref, enter, enterLast, onRegister])
}

const MODIFIERS = ["Ctrl", "Shift", "Alt"] as const

/** A key event as the Conventions section writes a key: `F12`, `Ctrl+F`, `Shift+F8`, `Ctrl+Enter`. */
function keysOf(event: KeyboardEvent): string {
  const held = { Ctrl: event.ctrlKey || event.metaKey, Shift: event.shiftKey, Alt: event.altKey }
  const key = event.key.length === 1 ? event.key.toUpperCase() : event.key
  return [...MODIFIERS.filter((name) => held[name]), key].join("+")
}

function runKey(event: KeyboardEvent) {
  if (event.isComposing || event.keyCode === 229 || event.repeat) return
  const keys = keysOf(event)
  if (!/^F\d{1,2}$/.test(keys) && !keys.includes("+")) return
  const dialogs = document.querySelectorAll('[role="alertdialog"], [role="dialog"], dialog[open]')
  if (Array.from(dialogs).some((dialog) => dialog.getClientRects().length > 0)) return
  const buttons = Array.from(document.querySelectorAll<HTMLButtonElement>(`[data-key="${keys}"]`))
  if (buttons.length === 0) return
  // A key that the rows of a table carry (the lines of a slip) runs the one in the row that holds the focus, and rests
  // while the focus is outside the rows.
  const row = document.activeElement?.closest("tr")
  const button = buttons.find((candidate) => row?.contains(candidate)) ?? buttons.find((candidate) => !candidate.closest("tbody tr"))
  if (!button) return
  event.preventDefault()
  if (!button.disabled) button.click()
}

let users = 0

/**
 * A function key or a shortcut runs the button that carries it in `data-key` (`data-key="F12"`, `data-key="Ctrl+F"`),
 * so every key is also a control the reader can click. The browser's own action for that key is stopped. While a
 * dialog is open the keys rest. Call it once in the screen that holds the buttons.
 */
export function useKeyButtons() {
  useEffect(() => {
    if (users++ === 0) window.addEventListener("keydown", runKey)
    return () => {
      if (--users === 0) window.removeEventListener("keydown", runKey)
    }
  }, [])
}
