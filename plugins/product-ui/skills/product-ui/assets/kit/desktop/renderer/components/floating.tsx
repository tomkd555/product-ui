// Two small floating parts of the window: the tooltip a command shows after 500ms, and the panel under a control
// (a command's menu, a collapsed group). Both are placed with position: fixed, so no clipped region hides them.
import { useEffect, useRef, useState, type ReactNode } from "react"

const TOOLTIP_DELAY_MS = 500

type Place = { left: number; top: number }

function below(anchor: HTMLElement): Place {
  const rect = anchor.getBoundingClientRect()
  return { left: Math.max(4, rect.left), top: rect.bottom + 4 }
}

/** Wraps one control: after 500ms of hover or focus, shows `text` (a second line after a newline) under it. */
export function Tip({ text, hidden = false, children }: { text: string; hidden?: boolean; children: ReactNode }) {
  const anchor = useRef<HTMLSpanElement>(null)
  const timer = useRef<number | undefined>(undefined)
  const [place, setPlace] = useState<Place | null>(null)
  const start = () => {
    window.clearTimeout(timer.current)
    if (hidden) return
    timer.current = window.setTimeout(() => anchor.current && setPlace(below(anchor.current)), TOOLTIP_DELAY_MS)
  }
  const stop = () => {
    window.clearTimeout(timer.current)
    setPlace(null)
  }
  useEffect(() => () => window.clearTimeout(timer.current), [])
  // A menu open under the control takes the tooltip's place.
  useEffect(() => {
    if (hidden) {
      window.clearTimeout(timer.current)
      setPlace(null)
    }
  }, [hidden])
  return (
    <span ref={anchor} className="relative inline-flex" onPointerEnter={start} onPointerLeave={stop} onFocus={start} onBlur={stop} onPointerDown={stop}>
      {children}
      {place && (
        <span
          role="tooltip"
          style={{ position: "fixed", left: place.left, top: place.top }}
          className="pointer-events-none z-50 max-w-72 rounded-md bg-foreground px-2 py-1 text-sm whitespace-pre-line text-background"
        >
          {text}
        </span>
      )}
    </span>
  )
}

/** A panel under `anchor` that closes on a press outside it or on Esc. */
export function FloatingPanel({
  anchor,
  onClose,
  role = "menu",
  label,
  children,
}: {
  anchor: HTMLElement | null
  onClose: () => void
  role?: string
  label: string
  children: ReactNode
}) {
  const panel = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const onPress = (event: PointerEvent) => {
      if (event.target instanceof Node && !panel.current?.contains(event.target) && !anchor?.contains(event.target)) onClose()
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation()
        onClose()
      }
    }
    document.addEventListener("pointerdown", onPress)
    document.addEventListener("keydown", onKey, true)
    return () => {
      document.removeEventListener("pointerdown", onPress)
      document.removeEventListener("keydown", onKey, true)
    }
  }, [anchor, onClose])
  if (!anchor) return null
  const place = below(anchor)
  return (
    <div
      ref={panel}
      role={role}
      aria-label={label}
      style={{ position: "fixed", left: place.left, top: place.top }}
      className="z-40 flex min-w-32 flex-col rounded-md border border-border bg-background p-1 shadow-md"
    >
      {children}
    </div>
  )
}
