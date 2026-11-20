// A collection with nothing to show, as patterns/state.empty.json describes it.
import type { ReactNode } from "react"

/**
 * `object` is the plural name of the object (受注). `narrowed` is true when a search, a filter or a view is set:
 * the state then points to another condition, and the search and the filters stay in view above it.
 * `action` is the control that adds the first record, shown before first use only.
 */
export function EmptyState({ object, narrowed = false, action }: { object: string; narrowed?: boolean; action?: ReactNode }) {
  return (
    <div data-pattern="state.empty" className="space-y-2 border-t border-border py-12 text-center">
      <p data-pattern-slot="title" className="text-base font-bold">
        {narrowed ? `該当する${object}はありません。` : `${object}はありません。`}
      </p>
      {narrowed && (
        <p data-pattern-slot="description" className="text-sm text-muted-foreground">
          別の条件を試してください。
        </p>
      )}
      {!narrowed && action && (
        <div data-pattern-slot="action" className="pt-2">
          {action}
        </div>
      )}
    </div>
  )
}
