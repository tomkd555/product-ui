// The one format of each kind of value, used by every screen of the build.
// Dates are kept as `2026-11-13` and times as `2026-11-13T09:40`, which sort as text.

/** `2026-11-13` or `2026-11-13T09:40` as `2026/11/13`; a missing value as an empty string. */
export function formatDate(iso: string | null | undefined) {
  return iso ? iso.slice(0, 10).replaceAll("-", "/") : ""
}

/** `2026-11-13T09:40` as `2026/11/13 09:40`. */
export function formatDateTime(iso: string | null | undefined) {
  return iso ? `${formatDate(iso)} ${iso.slice(11, 16)}` : ""
}

/** `1280000` as `1,280,000`. */
export function formatNumber(n: number) {
  return n.toLocaleString("ja-JP")
}

/** `1280000` as `1,280,000円`. */
export function formatYen(n: number) {
  return `${formatNumber(n)}円`
}

/** `56` as `56件`; `unit` takes the counter of the object (名, 社, 枚). */
export function formatCount(n: number, unit = "件") {
  return `${formatNumber(n)}${unit}`
}

/** An entry of the same day as `now` as `12分前` or `3時間前`, any other as its date and time. */
export function formatWhen(iso: string, now: string) {
  if (iso.slice(0, 10) !== now.slice(0, 10)) return formatDateTime(iso)
  const minutes = Math.round((Date.parse(`${now}:00Z`) - Date.parse(`${iso}:00Z`)) / 60000)
  if (minutes < 1) return "たった今"
  if (minutes < 60) return `${minutes}分前`
  return `${Math.floor(minutes / 60)}時間前`
}
