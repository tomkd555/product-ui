// The status bar: the document's state as short items at the left; at the right the view buttons, 縮小 (−), the zoom
// slider 100px wide, 拡大 (+), the zoom in percent, and the fit button (references/desktop.md, Status bar).
// product-ui: ignore-file S16 the commands are the fixed list of the Command set, and a group or an item without commands is left out
import { Minus, Plus } from "lucide-react"
import { runCommand, type CommandHandlers, type CommandSpec } from "@/lib/commands"
import { documentStore, ZOOM_RANGE } from "@/lib/document-state"

const ZOOM_ITEM = "ズーム"
const FIT_ITEM = "合わせる"

const buttonClass = "grid size-6 place-items-center rounded-md text-foreground outline-none hover:bg-background focus-visible:ring-2 focus-visible:ring-ring"

export function StatusBar({
  height,
  left,
  right,
  values,
  notice,
  zoom,
  fit,
  handlers,
}: {
  height: number
  /** The names of the left items; `values` gives the text of each, by name (`{ 要素数: "要素数12" }`). */
  left: string[]
  /** The names of the right items: `ズーム` stands for the zoom controls, `合わせる` for the fit button; other names are text. */
  right: string[]
  values?: Record<string, string>
  /** A result message (`notify` of the shell): while it is set, it takes the place of the left items. */
  notice?: string | null
  zoom: number
  /** The `zoom-fit` command of the Command set, where the application has one; the button takes its label. */
  fit?: CommandSpec
  handlers: CommandHandlers
}) {
  const setZoom = (value: number) => documentStore.setZoom(value)
  return (
    <footer data-region="status-bar" style={{ height }} className="flex shrink-0 items-center justify-between gap-4 bg-muted px-3 text-sm text-foreground">
      <div aria-live="polite" className="flex min-w-0 items-center gap-4">
        {notice ? (
          <span data-notice className="whitespace-nowrap">
            {notice}
          </span>
        ) : (
          left.map((name) => (
            <span key={name} className="whitespace-nowrap">
              {values?.[name] ?? name}
            </span>
          ))
        )}
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {right.map((name) => {
          if (name === ZOOM_ITEM) {
            return (
              <div key={name} role="group" aria-label="ズーム" className="flex items-center gap-1">
                <button type="button" aria-label="縮小" onClick={() => setZoom(zoom - ZOOM_RANGE.step)} className={buttonClass}>
                  <Minus className="size-4" />
                </button>
                <input
                  type="range"
                  aria-label="ズーム"
                  min={ZOOM_RANGE.min}
                  max={ZOOM_RANGE.max}
                  step={ZOOM_RANGE.step}
                  value={zoom}
                  onChange={(event) => setZoom(Number(event.target.value))}
                  className="w-25 accent-primary"
                />
                <button type="button" aria-label="拡大" onClick={() => setZoom(zoom + ZOOM_RANGE.step)} className={buttonClass}>
                  <Plus className="size-4" />
                </button>
                <span className="w-12 text-right whitespace-nowrap tabular-nums">{zoom}%</span>
              </div>
            )
          }
          if (name === FIT_ITEM) {
            const label = fit?.label ?? name
            return (
              <button
                key={name}
                type="button"
                data-command={fit?.id}
                aria-label={label}
                onClick={() => (fit ? void runCommand(fit, handlers) : setZoom(100))}
                className="h-6 rounded-md px-2 text-sm text-foreground outline-none hover:bg-background focus-visible:ring-2 focus-visible:ring-ring"
              >
                {label}
              </button>
            )
          }
          return (
            <span key={name} className="whitespace-nowrap">
              {values?.[name] ?? name}
            </span>
          )
        })}
      </div>
    </footer>
  )
}
