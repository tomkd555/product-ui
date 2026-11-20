// How the ribbon's groups collapse as the window narrows (references/desktop.md, Tab row and command area).

/** The order in which a tab's groups collapse: the groups the brief's `- Collapse:` line names, then the rest from the rightmost. */
export function collapseOrder(groups: string[], listed: string[]): string[] {
  const named = listed.filter((name) => groups.includes(name))
  return [...named, ...groups.filter((name) => !named.includes(name)).reverse()]
}

/**
 * Which groups collapse into one button so that the row fits `available` px: groups collapse one at a time in `order`
 * (indices into `widths`) while the row is too wide. `tabOnly` is true when every group is collapsed and the row still
 * does not fit; the command area then hides and the tab row alone shows.
 */
export function planCollapse(widths: number[], order: number[], collapsedWidth: number, available: number) {
  let total = widths.reduce((sum, width) => sum + width, 0)
  const collapsed: number[] = []
  for (const index of order) {
    if (total <= available) break
    if (widths[index] <= collapsedWidth) continue
    total += collapsedWidth - widths[index]
    collapsed.push(index)
  }
  return { collapsed, tabOnly: total > available }
}
