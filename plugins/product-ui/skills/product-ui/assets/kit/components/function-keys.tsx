// The function keys of an entry screen as one row of buttons (patterns/action.function-keys.json). Each button shows
// its key and the word of its operation; the key runs the button through lib/keys (useKeyButtons).
import type { ComponentProps } from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

/** The row. It stays at the foot of the window while the page scrolls; pass `className="static"` for a toolbar. */
export function FunctionKeys({ className, children, ...rest }: ComponentProps<"div">) {
  return (
    <div
      role="toolbar"
      aria-label="ファンクションキー"
      className={cn("sticky bottom-0 z-10 flex flex-wrap gap-2 border-t border-border bg-background py-3", className)}
      {...rest}
    >
      {children}
    </div>
  )
}

/** One key: `keyName` is the key as the Conventions section writes it (`F12`), `children` the word of its operation. */
export function FunctionKey({ keyName, className, children, ...rest }: { keyName: string } & ComponentProps<typeof Button>) {
  return (
    <Button type="button" variant="outline" data-key={keyName} className={cn("h-10 gap-2 px-3", className)} {...rest}>
      <kbd className="font-sans text-sm text-muted-foreground">{keyName}</kbd>
      {children}
    </Button>
  )
}
