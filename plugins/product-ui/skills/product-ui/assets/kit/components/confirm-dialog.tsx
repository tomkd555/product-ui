// The step before an operation runs (patterns/feedback.confirm.json): an action that cannot be undone or that changes
// many records (references/interaction.md, Destructive and bulk actions), and a registration where the brief's
// Conventions section asks for it. An action the reader can undo skips this step and shows a message with 元に戻す.
import { useEffect, useRef, type ComponentProps, type ReactNode } from "react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { buttonVariants } from "@/components/ui/button"
import { useSubmitGuard } from "@/lib/submit-guard"

/**
 * `title` names the object and the operation (「受注伝票の登録」, 「受注SO-1042の取り消し」). `description` is the
 * sentence of the Conventions section (「登録します。よろしいですか？」), or what the reader loses and what happens next.
 * `confirmLabel` is the word of the operation and `cancelLabel` the dismissing word, both from the Conventions
 * section where it gives them; `destructive` marks an action that removes data. Other attributes go to the dialog:
 * `data-confirm="register"` marks the step before a registration.
 *
 * The confirming button runs `onConfirm` once: a second press while that run is under way, or while the dialog is
 * closing, is dropped (`lib/submit-guard`), so the operation behind the dialog is the guarded one. A dialog that removes data opens with
 * the focus on the dismissing button; any other opens with it on the confirming button, so Enter confirms.
 */
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel,
  cancelLabel = "キャンセル",
  destructive = false,
  onConfirm,
  ...rest
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: ReactNode
  confirmLabel: string
  cancelLabel?: string
  destructive?: boolean
  onConfirm: () => void | Promise<void>
} & Omit<ComponentProps<typeof AlertDialogContent>, "title" | "children">) {
  const commit = useSubmitGuard(onConfirm)
  const confirm = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    if (!open || destructive) return
    const frame = requestAnimationFrame(() => confirm.current?.focus())
    return () => cancelAnimationFrame(frame)
  }, [open, destructive])
  return (
    <AlertDialog open={open} onOpenChange={(next) => onOpenChange(next)}>
      <AlertDialogContent data-pattern="feedback.confirm" {...rest}>
        <AlertDialogHeader>
          <AlertDialogTitle data-pattern-slot="title">{title}</AlertDialogTitle>
          {description && <AlertDialogDescription data-pattern-slot="message">{description}</AlertDialogDescription>}
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel data-pattern-slot="cancel">{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction
            ref={confirm}
            data-pattern-slot="confirm"
            data-guard="button"
            disabled={commit.busy}
            className={destructive ? buttonVariants({ variant: "destructive" }) : undefined}
            onClick={() => {
              if (!open) return
              void commit.run()
              onOpenChange(false)
            }}
          >
            {confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
