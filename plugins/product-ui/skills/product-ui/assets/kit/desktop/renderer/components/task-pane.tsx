// A task pane beside the document: a 36px header with the title and a close button, and a splitter on the inner edge
// that drags the width in 1px steps, moves it by 16px with the arrow keys and restores the default on a double click
// (references/desktop.md, Task panes). The width is a state of the window, never saved in the document.
import { useRef, type KeyboardEvent, type PointerEvent, type ReactNode } from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

const KEY_STEP = 16

export function TaskPane({
  side,
  title,
  width,
  defaultWidth,
  min,
  max,
  onWidth,
  onClose,
  hidden,
  children,
}: {
  side: "left" | "right"
  title: string
  width: number
  defaultWidth: number
  min: number
  /** The widest the pane may be now: its own maximum, less what the document's minimum width leaves. */
  max: number
  onWidth: (width: number) => void
  onClose: () => void
  /** The pane stays mounted, so its fields keep their drafts, while the window is too narrow to show it. */
  hidden?: boolean
  children?: ReactNode
}) {
  const start = useRef<{ x: number; width: number } | null>(null)
  const clamp = (value: number) => Math.max(min, Math.min(max, Math.round(value)))
  // A pane at the left grows as its right edge moves right; a pane at the right grows as its left edge moves left.
  const sign = side === "left" ? 1 : -1
  const onKeyDown = (event: KeyboardEvent) => {
    const move = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0
    if (!move) return
    event.preventDefault()
    onWidth(clamp(width + move * sign * KEY_STEP))
  }
  const onMove = (event: PointerEvent) => {
    if (start.current) onWidth(clamp(start.current.width + sign * (event.clientX - start.current.x)))
  }
  return (
    <aside
      data-region={`${side}-pane`}
      aria-label={title}
      tabIndex={-1}
      hidden={hidden}
      style={{ width }}
      className={cn("relative flex shrink-0 flex-col bg-background outline-none", side === "left" ? "border-r border-border" : "border-l border-border")}
    >
      <div className="flex h-9 shrink-0 items-center justify-between border-b border-border bg-muted pr-1 pl-3 text-sm font-semibold">
        <span className="truncate">{title}</span>
        <button
          type="button"
          aria-label={`${title}を閉じる`}
          onClick={onClose}
          className="grid size-6 place-items-center rounded-md hover:bg-background focus-visible:ring-2 focus-visible:ring-ring"
        >
          <X className="size-4" />
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-auto p-3">{children}</div>
      <div
        role="separator"
        aria-orientation="vertical"
        aria-label={`${title}の幅`}
        aria-valuenow={width}
        aria-valuemin={min}
        aria-valuemax={max}
        tabIndex={0}
        onKeyDown={onKeyDown}
        onDoubleClick={() => onWidth(clamp(defaultWidth))}
        onPointerDown={(event) => {
          event.currentTarget.setPointerCapture(event.pointerId)
          start.current = { x: event.clientX, width }
        }}
        onPointerMove={onMove}
        onPointerUp={() => {
          start.current = null
        }}
        className={cn(
          "group absolute inset-y-0 z-10 flex w-1.5 cursor-col-resize justify-center outline-none",
          side === "left" ? "-right-[3px]" : "-left-[3px]",
        )}
      >
        <span className="w-px bg-border group-hover:bg-primary group-focus-visible:bg-primary" />
      </div>
    </aside>
  )
}
