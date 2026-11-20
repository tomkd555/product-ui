// The lines of a slip (patterns/entry.slip.json): one row per line, a column per property, a line added at the
// foot and removed in its row. The cells are written by the screen, so each keeps its slot attributes.
// product-ui: ignore-file S16 a slip being entered always holds a line, which the screen passes in
import type { ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { cn } from "@/lib/utils"

export type LineColumn = { label: string; numeric?: boolean; required?: boolean }
/** A shortcut of the Conventions section on the lines: its keys (`Ctrl+Insert`) and its word (行挿入). */
export type LineKey = { keys: string; label: string }

/**
 * `children` renders the cells of one line and receives `set`, which changes that line. `blank` makes an empty line.
 * `insert`, `remove` and `add` take the shortcuts the Conventions section lists for a line (`row-insert`, `row-delete`,
 * `row-new`). Without `remove` the row's button reads 行を削除, without `add` the button at the foot reads 行を追加, and
 * without `insert` a line is added at the foot alone.
 * `requiredMark` is the mark of a required column (`required_mark` of the Conventions section).
 */
export function LineGrid<Line>({
  lines,
  onChange,
  blank,
  columns,
  insert,
  remove,
  add,
  requiredMark = "text",
  className,
  children,
}: {
  lines: Line[]
  onChange: (lines: Line[]) => void
  blank: () => Line
  columns: LineColumn[]
  insert?: LineKey
  remove?: LineKey
  add?: LineKey
  requiredMark?: "text" | "asterisk"
  className?: string
  children: (line: Line, set: (patch: Partial<Line>) => void, index: number) => ReactNode
}) {
  const setLine = (index: number, patch: Partial<Line>) =>
    onChange(lines.map((line, at) => (at === index ? { ...line, ...patch } : line)))
  const insertAt = (index: number) => onChange([...lines.slice(0, index), blank(), ...lines.slice(index)])
  const removeAt = (index: number) => onChange(lines.filter((_, at) => at !== index))
  return (
    <div className={cn("space-y-3", className)}>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column.label} className={column.numeric ? "text-right" : undefined}>
                  {column.label}
                  {column.required &&
                    (requiredMark === "asterisk" ? (
                      <span data-required-mark="asterisk" className="ml-1 text-destructive">
                        <span aria-hidden="true">*</span>
                        <span className="sr-only">必須</span>
                      </span>
                    ) : (
                      <span data-required-mark="text" className="ml-2 text-destructive">
                        必須
                      </span>
                    ))}
                </TableHead>
              ))}
              <TableHead>
                <span className="sr-only">行の操作</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {lines.map((line, index) => (
              <TableRow key={index}>
                {children(line, (patch) => setLine(index, patch), index)}
                <TableCell className="w-px py-0.5 whitespace-nowrap">
                  {insert && (
                    <Button type="button" variant="ghost" className="h-8" data-pattern-slot="line-action" data-key={insert.keys} onClick={() => insertAt(index)}>
                      {insert.label}
                    </Button>
                  )}
                  <Button type="button" variant="ghost" className="h-8" data-pattern-slot="line-action" data-key={remove?.keys} onClick={() => removeAt(index)}>
                    {remove?.label ?? "行を削除"}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <Button type="button" variant="outline" data-line-add data-pattern-slot="line-action" data-key={add?.keys} onClick={() => onChange([...lines, blank()])}>
        {add?.label ?? "行を追加"}
      </Button>
    </div>
  )
}
