// The prompt on closing a changed document, and before 新規 and 開く: the profile's sentence and its three buttons,
// 保存 the default, 保存しない, キャンセル (references/desktop.md, Save prompt). The application draws it as a modal dialog.
// `ErrorNotice` is the dialog of a failure the reader must act on, such as a save that failed.
import { useEffect } from "react"
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"

const ACCELERATORS = { save: "S", discard: "N" }

/** The dialog's title for each operation that can fail, by command id. */
export const FAILURE_TITLES: Record<string, string> = {
  open: "開けませんでした",
  save: "保存できませんでした",
  "save-as": "保存できませんでした",
  export: "エクスポートできませんでした",
  print: "印刷できませんでした",
  new: "新規作成できませんでした",
  close: "閉じられませんでした",
  undo: "元に戻せませんでした",
  redo: "やり直せませんでした",
  cut: "切り取れませんでした",
  copy: "コピーできませんでした",
  paste: "貼り付けられませんでした",
  "select-all": "すべて選択できませんでした",
  delete: "削除できませんでした",
}

// A dialog in the window keeps its width and its one row of buttons at every window width: shadcn's `sm:` classes
// (640px) would give a window of 500px a 320px dialog with the buttons stacked in reverse.
const DIALOG_WIDTH =
  "w-[min(28rem,calc(100vw-2rem))] max-w-[min(28rem,calc(100vw-2rem))] sm:max-w-[min(28rem,calc(100vw-2rem))] data-[size=default]:max-w-[min(28rem,calc(100vw-2rem))] data-[size=default]:sm:max-w-[min(28rem,calc(100vw-2rem))]"
const DIALOG_HEADER = "place-items-start text-left"
const DIALOG_FOOTER = "flex-row justify-end"

export function SavePrompt({
  open,
  sentence,
  buttons,
  onSave,
  onDiscard,
  onCancel,
}: {
  open: boolean
  /** `confirm.close_sentence` of the Conventions section. */
  sentence: string
  /** `confirm.close_buttons`: save, do not save, cancel. */
  buttons: string[]
  onSave: () => void
  onDiscard: () => void
  onCancel: () => void
}) {
  useEffect(() => {
    if (!open) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (!event.altKey || event.ctrlKey || event.metaKey) return
      const key = event.key.toUpperCase()
      if (key === ACCELERATORS.save) onSave()
      else if (key === ACCELERATORS.discard) onDiscard()
      else return
      event.preventDefault()
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [open, onSave, onDiscard])
  const [save, discard, cancel] = buttons
  return (
    <AlertDialog open={open} onOpenChange={(next) => !next && onCancel()}>
      <AlertDialogContent data-confirm="close" className={DIALOG_WIDTH}>
        <AlertDialogHeader className={DIALOG_HEADER}>
          <AlertDialogTitle className="text-base font-normal">{sentence}</AlertDialogTitle>
        </AlertDialogHeader>
        <AlertDialogFooter className={DIALOG_FOOTER}>
          <Button type="button" autoFocus className="h-8" aria-keyshortcuts="Alt+S" onClick={onSave}>
            {save}
            <kbd className="font-sans text-xs">Alt+S</kbd>
          </Button>
          <Button type="button" variant="outline" className="h-8" aria-keyshortcuts="Alt+N" onClick={onDiscard}>
            {discard}
            <kbd className="font-sans text-xs">Alt+N</kbd>
          </Button>
          <Button type="button" variant="outline" className="h-8" onClick={onCancel}>
            {cancel}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

export function ErrorNotice({
  message,
  operation,
  title,
  onClose,
}: {
  message: string | null
  /** The command id of the operation that failed; the title comes from FAILURE_TITLES. */
  operation?: string
  /** The dialog's title; else the one FAILURE_TITLES gives `operation`, else 「エラー」. */
  title?: string
  onClose: () => void
}) {
  return (
    <AlertDialog open={message !== null} onOpenChange={(next) => !next && onClose()}>
      <AlertDialogContent className={DIALOG_WIDTH}>
        <AlertDialogHeader className={DIALOG_HEADER}>
          <AlertDialogTitle className="text-base">{title ?? FAILURE_TITLES[operation ?? ""] ?? "エラー"}</AlertDialogTitle>
          <AlertDialogDescription>{message}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter className={DIALOG_FOOTER}>
          <Button type="button" className="h-8" onClick={onClose}>
            閉じる
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
