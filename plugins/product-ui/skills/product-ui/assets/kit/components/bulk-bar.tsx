// The bar of a bulk action: it appears with the selection, states how many records are selected and offers
// to extend the selection to every record the filter gives.
import type { ComponentProps, ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { formatNumber } from "@/lib/format"
import { cn } from "@/lib/utils"

/**
 * `count` is the number of records selected and `total` the number the filter gives. `onSelectAll` extends the
 * selection to all of them; leave it out where the action is limited to the rows in view. `children` are the
 * actions, each a button named by its verb.
 */
export function BulkBar({
  count,
  total,
  unit = "件",
  onSelectAll,
  onClear,
  children,
  className,
  ...rest
}: { count: number; total: number; unit?: string; onSelectAll?: () => void; onClear: () => void; children: ReactNode } & ComponentProps<"div">) {
  if (count === 0) return null
  return (
    <div
      role="region"
      aria-label="選択した項目の操作"
      className={cn("flex flex-wrap items-center gap-x-4 gap-y-2 rounded-lg border border-border bg-muted px-3 py-2", className)}
      {...rest}
    >
      <p aria-live="polite" className="text-sm font-medium tabular-nums">
        {formatNumber(count)}
        {unit}を選択中
      </p>
      {onSelectAll && count < total && (
        <Button type="button" variant="link" className="h-9 px-0" onClick={onSelectAll}>
          条件に合う{formatNumber(total)}
          {unit}をすべて選択
        </Button>
      )}
      <div className="flex flex-wrap items-center gap-2">{children}</div>
      <Button type="button" variant="ghost" className="ml-auto h-9" onClick={onClear}>
        選択を解除
      </Button>
    </div>
  )
}
