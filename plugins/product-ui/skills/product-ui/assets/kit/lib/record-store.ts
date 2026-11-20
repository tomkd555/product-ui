// The sample records with the changes the reader makes to them. A mock keeps the changes in sessionStorage,
// so a reload shows each record as the reader left it; a wired build replaces this file with its API client.
import { useSyncExternalStore } from "react"

export function createRecordStore<T extends { id: string }>(storageKey: string, seed: T[]) {
  const listeners = new Set<() => void>()
  let records = load()

  function load(): T[] {
    try {
      const raw = sessionStorage.getItem(storageKey)
      return raw ? (JSON.parse(raw) as T[]) : seed
    } catch {
      return seed
    }
  }

  /** Replaces the records and returns a function that restores them as they were, for 元に戻す. */
  function commit(next: T[]) {
    const before = records
    write(next)
    return () => write(before)
  }

  function write(next: T[]) {
    records = next
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(next))
    } catch {
      // Storage may be unavailable; the change still holds until the page is left.
    }
    listeners.forEach((listener) => listener())
  }

  function subscribe(listener: () => void) {
    listeners.add(listener)
    return () => {
      listeners.delete(listener)
    }
  }

  return {
    /** Every record, re-read by the component on each change. */
    useRecords: () => useSyncExternalStore(subscribe, () => records),
    /** One record, re-read by the component on each change; `undefined` for an id the product does not hold. */
    useRecord: (id: string | undefined) => useSyncExternalStore(subscribe, () => records.find((r) => r.id === id)),
    add: (record: T) => commit([record, ...records]),
    /** Changes one record through `change`, which returns the record's next value. */
    update: (id: string, change: (record: T) => T) => commit(records.map((r) => (r.id === id ? change(r) : r))),
    /** Changes every record whose id is given: a bulk action. */
    updateMany: (ids: Iterable<string>, change: (record: T) => T) => {
      const set = new Set(ids)
      return commit(records.map((r) => (set.has(r.id) ? change(r) : r)))
    },
    remove: (ids: Iterable<string>) => {
      const set = new Set(ids)
      return commit(records.filter((r) => !set.has(r.id)))
    },
  }
}
