// The title row: the quick access toolbar at the left, the document's title centred in the free width, and at the
// right the area Electron's caption buttons take (references/desktop.md, Title row). The row is a drag region and every
// control in it is no-drag.
// product-ui: ignore-file S16 the commands are the fixed list of the Command set, and a group or an item without commands is left out
import { CommandButton, type Icon } from "@/components/command-button"
import type { CommandHandlers, CommandSpec } from "@/lib/commands"

export function TitleRow({
  height,
  title,
  commands,
  handlers,
  icons,
}: {
  height: number
  title: string
  /** The commands of the `quick-access` place, in the order of the Command set. */
  commands: CommandSpec[]
  handlers: CommandHandlers
  icons?: Record<string, Icon>
}) {
  return (
    <header data-region="title-row" style={{ height }} className="shrink-0 bg-muted [app-region:drag]">
      <div
        style={{ marginLeft: "env(titlebar-area-x, 0px)", width: "env(titlebar-area-width, 100%)", height }}
        className="grid grid-cols-[1fr_auto_1fr] items-center pl-2"
      >
        <div data-region="quick-access" role="toolbar" aria-label="クイック アクセス ツール バー" className="flex w-fit items-center gap-0.5 [app-region:no-drag]">
          {commands.map((spec) => (
            <CommandButton key={spec.id} spec={spec} handlers={handlers} icons={icons} variant="quick-access" scope="root" />
          ))}
        </div>
        <p className="min-w-0 max-w-[60vw] truncate px-2 text-center text-sm text-foreground">{title}</p>
        <span />
      </div>
    </header>
  )
}
