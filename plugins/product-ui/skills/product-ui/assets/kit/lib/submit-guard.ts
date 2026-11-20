// One run at a time for an operation that sends data: a second click while the first run is under way is
// dropped, and the control that started it takes no click until the run ends (references/profiles.md, waiting.block).
import { useCallback, useRef, useState } from "react"

/**
 * `run` calls `action` unless a run is under way; `busy` is true from the call until the action returns, or until
 * the promise it returns settles. The control takes `disabled={busy}` and `data-guard="button"`.
 */
export function useSubmitGuard<Args extends unknown[]>(action: (...args: Args) => void | Promise<void>) {
  const running = useRef(false)
  const [busy, setBusy] = useState(false)
  const run = useCallback(
    async (...args: Args) => {
      if (running.current) return
      running.current = true
      setBusy(true)
      try {
        await action(...args)
      } finally {
        running.current = false
        setBusy(false)
      }
    },
    [action],
  )
  return { run, busy }
}
