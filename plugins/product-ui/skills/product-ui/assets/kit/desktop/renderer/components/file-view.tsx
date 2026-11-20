// The file view behind the ファイル tab: a navigation column 160px wide, 戻る first, and the page of the selected
// item at the right (references/desktop.md, File view). It covers everything under the title row.
// product-ui: ignore-file S16 the commands are the fixed list of the Command set, and a group or an item without commands is left out
import type { ReactNode } from "react"
import { iconOf, type Icon } from "@/components/command-button"
import { Tip } from "@/components/floating"
import { KeyTip } from "@/components/key-tip"
import { isEnabled, keysOfSpec, tooltipText, type CommandHandlers, type CommandSpec } from "@/lib/commands"
import { cn } from "@/lib/utils"

/** The items that show a page when the application supplies one; every other item acts and closes the view. */
export const PAGE_ITEMS = ["new", "export", "print"]

export function isPageItem(spec: CommandSpec): boolean {
  return PAGE_ITEMS.includes(spec.id) || spec.action === "app"
}

export function FileView({
  top,
  commands,
  handlers,
  icons,
  page,
  pages,
  onActivate,
  onRun,
}: {
  /** The title row's height: the view starts under it. */
  top: number
  /** The commands of the `file-view` place, in the order of the Command set. */
  commands: CommandSpec[]
  handlers: CommandHandlers
  icons?: Record<string, Icon>
  /** The id of the item whose page shows. */
  page: string | null
  /** The page of an item, by command id; `run` runs the item's command and closes the view. */
  pages?: Record<string, (context: { run: () => void }) => ReactNode>
  /** Opens the item's page, or runs it and closes the view where the item has no page. */
  onActivate: (spec: CommandSpec) => void
  /** Runs the item's command and closes the view. */
  onRun: (spec: CommandSpec) => void
}) {
  const body = commands.filter((spec) => spec.action !== "app")
  const foot = commands.filter((spec) => spec.action === "app")
  const selected = commands.find((spec) => spec.id === page)
  const item = (spec: CommandSpec) => {
    const Glyph = iconOf(spec.id, icons)
    const keys = keysOfSpec(spec)
    return (
      <Tip key={spec.id} text={tooltipText(spec, isEnabled(spec, handlers))}>
        <button
          type="button"
          data-command={spec.id}
          data-key={keys[0]}
          aria-current={spec.id === page ? "page" : undefined}
          aria-disabled={isEnabled(spec, handlers) ? undefined : true}
          onClick={() => isEnabled(spec, handlers) && onActivate(spec)}
          className={cn(
            "flex h-10 w-full items-center gap-2 px-3 text-left text-sm text-foreground outline-none hover:bg-background focus-visible:ring-2 focus-visible:ring-ring aria-disabled:text-muted-foreground aria-disabled:hover:bg-transparent",
            spec.id === page && "bg-background font-bold",
          )}
        >
          <Glyph className="size-4 shrink-0" />
          {spec.label}
        </button>
        <KeyTip scope="file" tip={spec.keytip} />
      </Tip>
    )
  }
  return (
    <div data-region="file-view" style={{ top }} className="absolute inset-x-0 bottom-0 z-30 flex bg-background">
      <nav aria-label="ファイル" className="flex w-40 shrink-0 flex-col bg-muted">
        {body.map((spec) => (
          <div key={spec.id} className="flex">
            {item(spec)}
          </div>
        ))}
        <div className="mt-auto flex flex-col">{foot.map(item)}</div>
      </nav>
      <div data-file-page={selected?.id} className="min-w-0 flex-1 overflow-auto p-6">
        {selected && (
          <>
            <p className="text-lg font-semibold">{selected.label}</p>
            {pages?.[selected.id]?.({ run: () => onRun(selected) })}
          </>
        )}
      </div>
    </div>
  )
}
