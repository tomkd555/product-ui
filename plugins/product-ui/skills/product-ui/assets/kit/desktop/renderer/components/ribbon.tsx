// The tab row and the command area: ファイル, the tabs, and under the selected tab its groups of large, small, menu and
// check commands, each group with its name and an optional dialog box launcher. Groups collapse into one button as the
// window narrows, and the command area hides when even that does not fit (references/desktop.md, Tab row and command area).
// product-ui: ignore-file S16 the commands are the fixed list of the Command set, and a group or an item without commands is left out
import { useEffect, useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent } from "react"
import { ArrowDownRight, ChevronDown, LayoutGrid } from "lucide-react"
import { CommandButton, type Icon } from "@/components/command-button"
import { FloatingPanel } from "@/components/floating"
import { KeyTip } from "@/components/key-tip"
import type { CommandHandlers, CommandSpec } from "@/lib/commands"
import { collapseOrder, planCollapse } from "@/lib/ribbon-layout"
import { cn } from "@/lib/utils"
import type { WindowSpec } from "../../../shared/window-types"

const COLLAPSED_WIDTH = 72
const SIDE_PADDING = 16

type Plan = { collapsed: string[]; tabOnly: boolean }

/** The commands of a group as columns: a large or menu command stands alone, small and check commands stack 3 to a column. */
function columnsOf(commands: CommandSpec[]): CommandSpec[][] {
  const columns: CommandSpec[][] = []
  for (const spec of commands) {
    const last = columns[columns.length - 1]
    const stackable = spec.size === "small" || spec.size === "check"
    if (stackable && last && last.length < 3 && (last[0].size === "small" || last[0].size === "check")) last.push(spec)
    else columns.push([spec])
  }
  return columns
}

function GroupCommands({
  commands,
  handlers,
  icons,
  scope,
  onRun,
}: {
  commands: CommandSpec[]
  handlers: CommandHandlers
  icons?: Record<string, Icon>
  scope: string
  onRun?: () => void
}) {
  return (
    <div className="flex h-21 items-start gap-1">
      {columnsOf(commands).map((column) => (
        <div key={column[0].id} className="flex flex-col">
          {column.map((spec) => (
            <CommandButton key={spec.id} spec={spec} handlers={handlers} icons={icons} variant="ribbon" scope={scope} onRun={onRun} />
          ))}
        </div>
      ))}
    </div>
  )
}

export function Ribbon({
  spec,
  commands,
  handlers,
  icons,
  groupIcons,
  launchers,
  tab,
  onTab,
  onFile,
  fileOpen,
  override,
  onHidden,
  peek,
  onPeek,
}: {
  spec: WindowSpec
  /** The commands of the `ribbon` place. */
  commands: CommandSpec[]
  handlers: CommandHandlers
  icons?: Record<string, Icon>
  groupIcons?: Record<string, Icon>
  /** Groups that have a dialog box launcher, by group name, with what the launcher opens. */
  launchers?: Record<string, () => void>
  tab: string
  onTab: (name: string) => void
  onFile: () => void
  fileOpen: boolean
  /** Ctrl+F1's choice: hide the command area, show it, or (null) follow the width. */
  override: "hidden" | "shown" | null
  /** Reports whether the command area is hidden, so that Ctrl+F1 can switch it. */
  onHidden: (hidden: boolean) => void
  /** Whether a click on a tab has opened the hidden command area over the document. */
  peek: boolean
  onPeek: (open: boolean) => void
}) {
  const root = useRef<HTMLDivElement>(null)
  const elements = useRef(new Map<string, HTMLElement>())
  const widths = useRef<Record<string, number>>({})
  const [rootWidth, setRootWidth] = useState(0)
  const [tick, setTick] = useState(0)
  const [plans, setPlans] = useState<Record<string, Plan>>({})
  const [openGroup, setOpenGroup] = useState<string | null>(null)
  const anchors = useRef(new Map<string, HTMLButtonElement>())

  const groups = useMemo(() => {
    const names: string[] = []
    for (const command of commands) if (command.tab === tab && !names.includes(command.group)) names.push(command.group)
    return names
  }, [commands, tab])
  const key = groups.join("/")
  const plan = plans[tab]
  const autoHidden = plan?.tabOnly ?? false
  const hidden = override ? override === "hidden" : autoHidden

  useEffect(() => {
    const el = root.current
    if (!el) return
    const watch = new ResizeObserver((entries) => setRootWidth(entries[0].contentRect.width))
    watch.observe(el)
    return () => watch.disconnect()
  }, [])

  // The width of each expanded group is read where it is drawn and kept for the plan, which also needs the groups it has collapsed.
  useLayoutEffect(() => {
    let changed = false
    elements.current.forEach((el, name) => {
      if (widths.current[name] !== el.offsetWidth) {
        widths.current[name] = el.offsetWidth
        changed = true
      }
    })
    if (changed) setTick((n) => n + 1)
  })

  useLayoutEffect(() => {
    if (rootWidth === 0) return
    const measured = groups.map((group) => widths.current[`${tab}/${group}`])
    if (measured.some((width) => width === undefined)) return
    const order = collapseOrder(groups, spec.collapse).map((name) => groups.indexOf(name))
    const result = planCollapse(measured, order, COLLAPSED_WIDTH, rootWidth - SIDE_PADDING)
    const next: Plan = { collapsed: result.collapsed.map((index) => groups[index]), tabOnly: result.tabOnly }
    setPlans((now) => (JSON.stringify(now[tab]) === JSON.stringify(next) ? now : { ...now, [tab]: next }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rootWidth, tab, key, tick, spec.collapse])

  useEffect(() => onHidden(hidden), [hidden, onHidden])

  const onTabKeys = (event: KeyboardEvent) => {
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0
    if (!step) return
    const names = spec.tabs.map((entry) => entry.name)
    const next = names[(names.indexOf(tab) + step + names.length) % names.length]
    event.preventDefault()
    onTab(next)
    requestAnimationFrame(() => document.getElementById(`tab-${names.indexOf(next)}`)?.focus())
  }

  const area = (
    <div
      role="tabpanel"
      id={`panel-${spec.tabs.findIndex((entry) => entry.name === tab)}`}
      aria-labelledby={`tab-${spec.tabs.findIndex((entry) => entry.name === tab)}`}
      data-region="command-area"
      style={{ height: spec.heights.commandArea }}
      className="flex items-stretch overflow-hidden bg-background px-2 py-1"
    >
      {groups.map((group, position) => {
        const inGroup = commands.filter((command) => command.tab === tab && command.group === group)
        const scope = `tab:${tab}`
        if (plan?.collapsed.includes(group)) {
          return (
            <div key={group} style={{ width: COLLAPSED_WIDTH }} className="relative shrink-0 border-r border-border px-1">
              <button
                ref={(el) => {
                  if (el) anchors.current.set(group, el)
                }}
                type="button"
                data-group-collapsed={group}
                data-group-tip={position < 9 ? String(position + 1) : undefined}
                aria-haspopup="true"
                aria-expanded={openGroup === group}
                onClick={() => setOpenGroup((now) => (now === group ? null : group))}
                className="flex h-full w-full flex-col items-center gap-0.5 rounded-md px-1 pt-1 text-sm text-foreground outline-none hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring"
              >
                {(() => {
                  const Glyph = groupIcons?.[group] ?? LayoutGrid
                  return <Glyph className="size-8 shrink-0" />
                })()}
                <span className="line-clamp-2 text-center leading-tight">{group}</span>
                <ChevronDown className="size-3.5" aria-hidden />
              </button>
              {position < 9 && <KeyTip scope={scope} tip={String(position + 1)} />}
              {openGroup === group && (
                <FloatingPanel anchor={anchors.current.get(group) ?? null} onClose={() => setOpenGroup(null)} role="group" label={group}>
                  <GroupCommands
                    commands={inGroup}
                    handlers={handlers}
                    icons={icons}
                    scope={scope}
                    onRun={() => {
                      setOpenGroup(null)
                      onPeek(false)
                    }}
                  />
                </FloatingPanel>
              )}
            </div>
          )
        }
        return (
          <div
            key={group}
            ref={(el) => {
              if (el) elements.current.set(`${tab}/${group}`, el)
              else elements.current.delete(`${tab}/${group}`)
            }}
            role="group"
            aria-label={group}
            className="flex shrink-0 flex-col border-r border-border px-1"
          >
            <GroupCommands commands={inGroup} handlers={handlers} icons={icons} scope={scope} onRun={() => onPeek(false)} />
            <div className="relative flex h-5 items-center justify-center text-sm text-muted-foreground">
              <span className="whitespace-nowrap">{group}</span>
              {launchers?.[group] && (
                <button
                  type="button"
                  aria-label={`${group}の詳細設定を開く`}
                  onClick={launchers[group]}
                  className="absolute right-0 bottom-0 grid size-6 place-items-center rounded-md hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <ArrowDownRight className="size-4" />
                </button>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )

  return (
    <div ref={root} className="relative shrink-0">
      <div data-region="tab-row" style={{ height: spec.heights.tabRow }} className="flex items-end bg-muted px-2">
        <span className="relative flex h-full">
          <button
            type="button"
            data-file-tab
            aria-expanded={fileOpen}
            onClick={onFile}
            className="h-full px-4 text-sm text-foreground outline-none hover:bg-background focus-visible:ring-2 focus-visible:ring-ring"
          >
            ファイル
          </button>
          <KeyTip scope="root" tip="F" />
        </span>
        <div role="tablist" aria-label="リボン" onKeyDown={onTabKeys} className="flex h-full">
          {spec.tabs.map((entry, index) => (
            <span key={entry.name} className="relative flex h-full">
              <button
                type="button"
                role="tab"
                id={`tab-${index}`}
                aria-selected={entry.name === tab}
                aria-controls={`panel-${index}`}
                tabIndex={entry.name === tab ? 0 : -1}
                onClick={() => {
                  onTab(entry.name)
                  if (hidden) onPeek(!(peek && entry.name === tab))
                }}
                className={cn(
                  "relative h-full px-4 text-sm text-foreground outline-none hover:bg-background focus-visible:ring-2 focus-visible:ring-ring",
                  entry.name === tab && "font-bold after:absolute after:inset-x-1 after:bottom-0 after:h-[3px] after:bg-primary",
                )}
              >
                {entry.name}
              </button>
              <KeyTip scope="root" tip={entry.keytip} />
            </span>
          ))}
        </div>
      </div>
      {!hidden && area}
      {hidden && peek && <div className="absolute inset-x-0 top-full z-20 shadow-md">{area}</div>}
    </div>
  )
}
