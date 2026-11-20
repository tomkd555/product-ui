// The behaviour of a collection view: search, filters, a row of views, sort and pages, all kept in the URL,
// so a reload, a shared link and the way back from a record show the same rows.
import { useState } from "react"
import { useLocation, useSearchParams } from "react-router-dom"

export type SortDir = "asc" | "desc"
type SortValue = string | number | null | undefined

export type CollectionConfig<T> = {
  /** The texts of a record that the search box reads. */
  text?: (row: T) => string[]
  /** One filter per URL parameter: whether the record matches the chosen value. */
  filters?: Record<string, (row: T, value: string) => boolean>
  /** The row of views above the table (未出荷, 自分の担当, one per state). `counts` holds how many records each view has under the search and the filters. */
  views?: Record<string, (row: T) => boolean>
  /** The columns the reader may sort by. An empty value sorts last in both directions. */
  sorts: Record<string, (row: T) => SortValue>
  defaultSort: { key: string; dir: SortDir }
  /** The order of two records with the same sort value, usually the identifier. */
  tie: (row: T) => string
  pageSize?: number
}

export function useCollection<T>(records: T[], config: CollectionConfig<T>) {
  const [params, setParams] = useSearchParams()
  const { pathname } = useLocation()
  const pageSize = config.pageSize ?? 20

  const q = params.get("q") ?? ""
  const view = params.get("view") ?? ""
  const sort = params.get("sort") ?? config.defaultSort.key
  const dirParam = params.get("dir")
  const dir: SortDir = dirParam === "asc" || dirParam === "desc" ? dirParam : config.defaultSort.dir
  const page = Math.max(1, Number(params.get("page")) || 1)
  const filterKeys = Object.keys(config.filters ?? {})

  // The records under the search and the filters, before a view narrows them.
  const needle = q.trim().toLowerCase()
  const matched = records.filter((row) => {
    for (const key of filterKeys) {
      const value = params.get(key)
      if (value && !config.filters![key](row, value)) return false
    }
    if (!needle) return true
    return (config.text?.(row) ?? []).some((text) => text.toLowerCase().includes(needle))
  })

  const counts: Record<string, number> = {}
  for (const [name, match] of Object.entries(config.views ?? {})) counts[name] = matched.filter(match).length

  const inView = config.views?.[view]
  const sortValue = config.sorts[sort] ?? config.sorts[config.defaultSort.key]
  const empty = (v: SortValue) => v === null || v === undefined || v === ""
  const rows = [...(inView ? matched.filter(inView) : matched)].sort((a, b) => {
    const va = sortValue(a)
    const vb = sortValue(b)
    if (empty(va) !== empty(vb)) return empty(va) ? 1 : -1
    const order = va! < vb! ? -1 : va! > vb! ? 1 : config.tie(a) < config.tie(b) ? -1 : 1
    return dir === "asc" ? order : -order
  })

  const pages = Math.max(1, Math.ceil(rows.length / pageSize))
  const current = Math.min(page, pages)
  const shown = rows.slice((current - 1) * pageSize, current * pageSize)

  /** Sets or clears parameters. Any change but a page change returns to the first page. Typed text passes `replace`, so the history holds one entry per search. */
  function update(changes: Record<string, string | null>, options?: { replace?: boolean }) {
    const next = new URLSearchParams(params)
    for (const [key, value] of Object.entries(changes)) {
      if (value === null || value === "") next.delete(key)
      else next.set(key, value)
    }
    if (!("page" in changes)) next.delete("page")
    setParams(next, { replace: options?.replace })
  }

  function hrefWith(changes: Record<string, string | null>) {
    const next = new URLSearchParams(params)
    for (const [key, value] of Object.entries(changes)) {
      if (value === null || value === "") next.delete(key)
      else next.set(key, value)
    }
    const search = next.toString()
    return search ? `${pathname}?${search}` : pathname
  }

  return {
    /** The search text. */
    q,
    /** The chosen view, or an empty string for every record. */
    view,
    /** The value of one filter, or an empty string. */
    filter: (key: string) => params.get(key) ?? "",
    /** Whether a search, a filter or a view narrows the records: the empty state then reads 該当する…はありません。 */
    narrowed: Boolean(q.trim() || view || filterKeys.some((key) => params.get(key))),
    sort,
    dir,
    /** The records under the search and the filters. */
    matched,
    /** How many of `matched` each view holds. */
    counts,
    /** Every record of the current view, sorted. */
    rows,
    /** The records of the current page. */
    shown,
    pages,
    current,
    /** The position of the first and the last record shown, for 「56件中21〜40件」. */
    from: rows.length === 0 ? 0 : (current - 1) * pageSize + 1,
    to: Math.min(current * pageSize, rows.length),
    update,
    /** Clears the search, the filters and the view. */
    clear: () => update(Object.fromEntries(["q", "view", ...filterKeys].map((key) => [key, null]))),
    /** Sorts by a column: its first direction on the first click, the other direction on the next. */
    toggleSort: (key: string, first: SortDir = "asc") =>
      update({ sort: key, dir: sort === key ? (dir === "asc" ? "desc" : "asc") : first }),
    /** The address of a view, with the search and the filters kept. */
    viewHref: (name: string | null) => hrefWith({ view: name, page: null }),
    /** The address of a page of the current rows. */
    pageHref: (n: number) => hrefWith({ page: n === 1 ? null : String(n) }),
  }
}

/** The rows the reader ticked, for a bulk action. A change of the rows shown keeps the selection; `clear` ends it. */
export function useSelection() {
  const [selected, setSelected] = useState<ReadonlySet<string>>(new Set())
  return {
    selected,
    count: selected.size,
    has: (id: string) => selected.has(id),
    toggle(id: string) {
      const next = new Set(selected)
      if (!next.delete(id)) next.add(id)
      setSelected(next)
    },
    /** Ticks every id given, or unticks them when all are ticked: the checkbox of the header row. */
    toggleAll(ids: string[]) {
      const next = new Set(selected)
      const all = ids.length > 0 && ids.every((id) => next.has(id))
      for (const id of ids) {
        if (all) next.delete(id)
        else next.add(id)
      }
      setSelected(next)
    },
    /** Extends the selection to every record the filter gives. */
    selectAll: (ids: string[]) => setSelected(new Set(ids)),
    clear: () => setSelected(new Set()),
  }
}
