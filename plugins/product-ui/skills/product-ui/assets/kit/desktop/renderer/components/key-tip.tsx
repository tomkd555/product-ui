// Key tips: the letters Alt shows on the tabs and the commands (references/desktop.md, Keys). The shell holds the
// state; a control prints its tip with <KeyTip scope=... tip=... /> while the scope is the one showing.
import { createContext, useContext } from "react"

/** `root` (tabs, ファイル, quick access), `tab:<name>` (a tab's commands), `file` (the file view's items), or null when off. */
export type KeyTipScope = string | null

export const KeyTipContext = createContext<{ scope: KeyTipScope; typed: string }>({ scope: null, typed: "" })

export function KeyTip({ scope, tip }: { scope: string; tip: string }) {
  const state = useContext(KeyTipContext)
  if (state.scope !== scope || tip === "none" || !tip.startsWith(state.typed)) return null
  return (
    <span
      data-keytip={tip}
      className="pointer-events-none absolute bottom-0 left-1/2 z-40 -translate-x-1/2 rounded-sm bg-foreground px-1 text-xs leading-4 text-background"
    >
      {tip}
    </span>
  )
}
