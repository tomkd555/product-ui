// One control that runs a command of the table, in the sizes the ribbon, the quick access toolbar and the file view
// use. It carries data-command and data-key (references/desktop.md, Markers the checks read), the tooltip and the key tip.
// product-ui: ignore-file S16 the commands are the fixed list of the Command set, and a group or an item without commands is left out
import { useRef, useState, type ComponentType } from "react"
import {
  ArrowLeft,
  BoxSelect,
  ChevronDown,
  ClipboardPaste,
  Copy,
  Download,
  FileOutput,
  FilePlus,
  FolderOpen,
  Maximize,
  Printer,
  Redo2,
  Replace,
  Save,
  SaveAll,
  Scissors,
  Search,
  Settings,
  Square,
  Trash2,
  Undo2,
  X,
  ZoomIn,
} from "lucide-react"
import { FloatingPanel, Tip } from "@/components/floating"
import { KeyTip } from "@/components/key-tip"
import {
  announceCommand,
  isEnabled,
  keysOfSpec,
  runCommand,
  tooltipText,
  type CommandHandlers,
  type CommandSpec,
} from "@/lib/commands"
import { cn } from "@/lib/utils"

export type Icon = ComponentType<{ className?: string }>

const ICONS: Record<string, Icon> = {
  save: Save,
  "save-as": SaveAll,
  undo: Undo2,
  redo: Redo2,
  cut: Scissors,
  copy: Copy,
  paste: ClipboardPaste,
  "select-all": BoxSelect,
  delete: Trash2,
  find: Search,
  replace: Replace,
  new: FilePlus,
  open: FolderOpen,
  print: Printer,
  export: FileOutput,
  close: X,
  zoom: ZoomIn,
  "zoom-fit": Maximize,
  back: ArrowLeft,
  options: Settings,
}

/** The icon of a command: the application's own (`icons`), else the kit's for the profile's operations. */
export function iconOf(id: string, icons?: Record<string, Icon>): Icon {
  return icons?.[id] ?? ICONS[id] ?? (id.startsWith("app-") ? Square : Download)
}

export type CommandVariant = "ribbon" | "quick-access" | "file-view"

/**
 * `scope` is the key tip scope this control's tip belongs to. `onRun` runs after the command ran from a click, so that
 * the shell can close a panel or the file view. A `menu` command opens its items under it.
 */
const EDIT_COMMANDS = new Set(["undo", "redo", "cut", "copy", "paste", "select-all", "delete"])

export function CommandButton({
  spec,
  handlers,
  icons,
  variant,
  scope,
  onRun,
  className,
}: {
  spec: CommandSpec
  handlers: CommandHandlers
  icons?: Record<string, Icon>
  variant: CommandVariant
  scope: string
  onRun?: () => void
  className?: string
}) {
  const ref = useRef<HTMLButtonElement>(null)
  const [open, setOpen] = useState(false)
  const handler = handlers[spec.id]
  const enabled = isEnabled(spec, handlers)
  const Glyph = iconOf(spec.id, icons)
  const keys = keysOfSpec(spec)
  const isMenu = spec.size === "menu"
  const large = variant === "ribbon" && (spec.size === "large" || isMenu)
  const iconOnly = variant === "quick-access"
  // The quick access toolbar and the file view sit on the muted chrome, where `accent` equals the ground.
  const fill = variant === "ribbon" ? "hover:bg-accent aria-pressed:bg-accent" : "hover:bg-background aria-pressed:bg-background"
  const click = () => {
    if (!enabled) return
    if (isMenu) {
      announceCommand(spec.id)
      setOpen((now) => !now)
      return
    }
    void runCommand(spec, handlers)
    onRun?.()
  }
  return (
    <Tip text={tooltipText(spec, enabled)} hidden={open}>
      <button
        ref={ref}
        type="button"
        data-command={spec.id}
        data-key={keys[0]}
        aria-label={iconOnly ? spec.label : undefined}
        aria-keyshortcuts={keys.length > 0 ? keys.join(" ") : undefined}
        aria-haspopup={isMenu ? "menu" : undefined}
        aria-expanded={isMenu ? open : undefined}
        aria-pressed={spec.size === "check" ? handler?.checked === true : undefined}
        aria-disabled={enabled ? undefined : true}
        // A click on an edit command keeps the focus where it was, so that the command reaches the field or the document it was in; any other button takes the focus, which commits a field that commits on blur.
        onMouseDown={(event) => EDIT_COMMANDS.has(spec.id) && event.preventDefault()}
        onClick={click}
        className={cn(
          "[app-region:no-drag] inline-flex items-center rounded-md text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring aria-disabled:text-muted-foreground aria-disabled:hover:bg-transparent",
          fill,
          large && "min-h-21 w-auto min-w-12 flex-col justify-start gap-0.5 px-1.5 pt-1",
          !large && !iconOnly && "h-6 justify-start gap-1.5 px-1.5",
          iconOnly && "size-7 justify-center",
          variant === "file-view" && "h-10 w-full gap-2 rounded-none px-3",
          className,
        )}
      >
        <Glyph className={cn(large ? "size-8" : "size-4", "shrink-0")} />
        {!iconOnly && (
          <span className={cn(large ? "line-clamp-2 text-center leading-tight" : "whitespace-nowrap")}>
            {spec.label}
            {isMenu && <ChevronDown className="ml-0.5 inline size-3.5 align-middle" aria-hidden />}
          </span>
        )}
      </button>
      <KeyTip scope={scope} tip={spec.keytip} />
      {open && (
        <FloatingPanel anchor={ref.current} onClose={() => setOpen(false)} label={spec.label}>
          {(handler?.menu ?? []).map((item) => (
            <button
              key={item.label}
              type="button"
              role="menuitem"
              onClick={() => {
                setOpen(false)
                item.run()
                onRun?.()
              }}
              className="rounded-sm px-3 py-1.5 text-left text-sm hover:bg-accent"
            >
              {item.label}
            </button>
          ))}
        </FloatingPanel>
      )}
    </Tip>
  )
}
