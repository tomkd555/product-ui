// The state of a record, as patterns/status.badge.json describes it: one word, one tone per state on every screen.
import { cn } from "@/lib/utils"

type Tone = "muted" | "primary" | "info" | "success" | "warning" | "destructive"

// Fill this map from the states of the object table in ui-brief.md, each state under the word the screen prints.
const TONE: Record<string, Tone> = {}

// The word carries the state and the border carries the colour, so the text keeps its contrast on every palette.
// `info`, `success` and `warning` are optional colours of tokens.json: a tone used here needs its colour there.
// A product that fills its badges sets the fill and the text here, the text being `text-foreground` or
// `text-primary-foreground`, whichever reaches 4.5:1 on the fill (scripts/colour.py contrast).
const CLASS: Record<Tone, string> = {
  muted: "border-transparent bg-muted text-muted-foreground",
  primary: "border-primary bg-background text-primary",
  info: "border-info bg-background text-foreground",
  success: "border-success bg-background text-foreground",
  warning: "border-warning bg-background text-foreground",
  destructive: "border-destructive bg-background text-destructive",
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      data-pattern="status.badge"
      className={cn("inline-flex h-6 items-center rounded-md border px-2 text-sm font-medium whitespace-nowrap", CLASS[TONE[status] ?? "muted"])}
    >
      <span data-pattern-slot="label">{status}</span>
    </span>
  )
}
