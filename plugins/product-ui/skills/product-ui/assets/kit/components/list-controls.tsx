// The controls above and below a collection: the search box, the filters, the row of views, the sortable
// column header, the count and the page links. Each one takes its state from `useCollection` (lib/collection).
// Extra props go to the root element, so a control takes the slot attribute of its pattern where it is placed:
// <ViewTabs data-pattern-slot="filter" … />.
// product-ui: ignore-file S16 the options, the views and the pages are fixed lists the page passes in; EmptyState shows the empty collection
import type { ComponentProps } from "react"
import { Link } from "react-router-dom"
import { ArrowDownIcon, ArrowUpIcon, SearchIcon } from "lucide-react"
import { buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { TableHead } from "@/components/ui/table"
import type { SortDir } from "@/lib/collection"
import { formatNumber } from "@/lib/format"
import { cn } from "@/lib/utils"

const selectClass =
  "h-9 w-full rounded-lg border border-input bg-background px-2.5 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 md:w-auto md:text-sm"

/** `label` is the accessible name (受注を検索); `placeholder` names the properties the search reads. */
export function SearchField({
  value,
  onChange,
  label,
  placeholder,
  className,
  ...rest
}: { value: string; onChange: (value: string) => void; label: string; placeholder?: string } & Omit<ComponentProps<"div">, "onChange">) {
  return (
    <div className={cn("relative w-full md:w-80", className)} {...rest}>
      <SearchIcon className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
      <Input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        aria-label={label}
        className="h-9 pl-8"
      />
    </div>
  )
}

export type Option = { value: string; label: string }

/** A filter on one property. `label` is the property (取引先) and `all` the choice that lifts the filter (すべての取引先). */
export function FilterSelect({
  label,
  all,
  options,
  value,
  onChange,
  className,
  ...rest
}: { label: string; all: string; options: Option[]; value: string; onChange: (value: string) => void } & Omit<
  ComponentProps<"select">,
  "onChange" | "value"
>) {
  return (
    <select aria-label={label} value={value} onChange={(event) => onChange(event.target.value)} className={cn(selectClass, className)} {...rest}>
      <option value="">{all}</option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  )
}

/** The sort of a folded table, where the column headers are out of view. Each option's value is `<key>-<dir>`. */
export function SortSelect({
  options,
  sort,
  dir,
  onChange,
  className,
  ...rest
}: { options: Option[]; sort: string; dir: SortDir; onChange: (sort: string, dir: SortDir) => void } & Omit<ComponentProps<"select">, "onChange">) {
  return (
    <select
      aria-label="並び替え"
      value={`${sort}-${dir}`}
      onChange={(event) => {
        const at = event.target.value.lastIndexOf("-")
        onChange(event.target.value.slice(0, at), event.target.value.slice(at + 1) as SortDir)
      }}
      className={cn(selectClass, "md:hidden", className)}
      {...rest}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  )
}

export type ViewTab = { name: string; label: string; count?: number; href: string }

/** The views of the collection as links, the first being every record (`name` empty). `current` is the chosen view. */
export function ViewTabs({ label, tabs, current, className, ...rest }: { label: string; tabs: ViewTab[]; current: string } & ComponentProps<"nav">) {
  return (
    <nav aria-label={label} className={cn("flex flex-wrap gap-x-5 border-b border-border", className)} {...rest}>
      {tabs.map((tab) => {
        const active = tab.name === current
        return (
          <Link
            key={tab.name}
            to={tab.href}
            aria-current={active ? "true" : undefined}
            className={cn(
              "-mb-px flex h-10 items-center gap-1.5 border-b-2 text-sm",
              active ? "border-primary font-bold text-foreground" : "border-transparent text-muted-foreground hover:text-foreground",
            )}
          >
            {tab.label}
            {tab.count !== undefined && <span className="tabular-nums">{formatNumber(tab.count)}</span>}
          </Link>
        )
      })}
    </nav>
  )
}

/** The header of a column the reader sorts by. `end` aligns it with a column of numbers. */
export function SortHead({
  label,
  active,
  dir,
  onSort,
  end = false,
  className,
  ...rest
}: { label: string; active: boolean; dir: SortDir; onSort: () => void; end?: boolean } & ComponentProps<typeof TableHead>) {
  return (
    <TableHead aria-sort={active ? (dir === "asc" ? "ascending" : "descending") : "none"} className={cn(end && "text-right", className)} {...rest}>
      <button type="button" onClick={onSort} className={cn("inline-flex h-9 items-center gap-1 font-medium hover:text-primary", end && "flex-row-reverse")}>
        {label}
        {active && (dir === "asc" ? <ArrowUpIcon className="size-4" aria-hidden /> : <ArrowDownIcon className="size-4" aria-hidden />)}
      </button>
    </TableHead>
  )
}

/** How many records the view holds: 「56件」, or 「56件中21〜40件」 where the rows run over several pages. */
export function RecordCount({
  total,
  from,
  to,
  pages,
  unit = "件",
  className,
  ...rest
}: { total: number; from: number; to: number; pages: number; unit?: string } & ComponentProps<"p">) {
  return (
    <p className={cn("text-sm tabular-nums text-muted-foreground", className)} {...rest}>
      {pages > 1 ? `${formatNumber(total)}${unit}中${formatNumber(from)}〜${formatNumber(to)}${unit}` : `${formatNumber(total)}${unit}`}
    </p>
  )
}

function pageList(pages: number, current: number) {
  if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1)
  const keep = [1, current - 1, current, current + 1, pages].filter((n) => n >= 1 && n <= pages)
  return [...new Set(keep)].sort((a, b) => a - b)
}

/** The page links under a collection; it renders nothing while the rows fit one page. `href` gives the address of a page. */
export function Pagination({
  pages,
  current,
  href,
  className,
  ...rest
}: { pages: number; current: number; href: (page: number) => string } & ComponentProps<"nav">) {
  if (pages <= 1) return null
  const list = pageList(pages, current)
  return (
    <nav aria-label="ページ" className={cn("flex justify-end", className)} {...rest}>
      <ul className="flex flex-wrap items-center gap-1">
        {current > 1 && (
          <li>
            <Link to={href(current - 1)} className={buttonVariants({ variant: "ghost", className: "h-9" })}>
              前へ
            </Link>
          </li>
        )}
        {list.map((n, i) => (
          <li key={n} className="flex items-center gap-1">
            {i > 0 && n - list[i - 1] > 1 && (
              <span className="px-1 text-sm text-muted-foreground" aria-hidden>
                …
              </span>
            )}
            <Link
              to={href(n)}
              aria-current={n === current ? "page" : undefined}
              aria-label={`${n}ページ目`}
              className={buttonVariants({
                variant: n === current ? "secondary" : "ghost",
                className: cn("h-9 min-w-9 px-2 tabular-nums", n === current && "font-bold"),
              })}
            >
              {n}
            </Link>
          </li>
        ))}
        {current < pages && (
          <li>
            <Link to={href(current + 1)} className={buttonVariants({ variant: "ghost", className: "h-9" })}>
              次へ
            </Link>
          </li>
        )}
      </ul>
    </nav>
  )
}
