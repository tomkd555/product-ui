// One field of a form: its label, the required mark, the control and the message under it, with the attributes that
// tie them together. The form itself takes `noValidate`, so the messages of lib/form show in place of the browser's.
import { useId, type ComponentProps, type ReactNode } from "react"
import { cn } from "@/lib/utils"

export type ControlProps = { id: string; required?: boolean; "aria-invalid": boolean; "aria-describedby"?: string }

/**
 * `children` receives the attributes of the control and spreads them on it: `{(control) => <Input {...control} … />}`.
 * `hint` is a constraint the reader needs before typing (半角数字 8桁); `error` is the message of lib/form's `validate`.
 * `requiredMark` is the mark of a required field, as the brief's Conventions section gives it (`required_mark`):
 * 「必須」 beside the label, or an asterisk read out as 必須. Other attributes (a pattern's slot) go to the field's root.
 */
export function FormField({
  label,
  required = false,
  requiredMark = "text",
  hint,
  error,
  className,
  children,
  ...rest
}: {
  label: string
  required?: boolean
  requiredMark?: "text" | "asterisk"
  hint?: string
  error?: string
  children: (control: ControlProps) => ReactNode
} & Omit<ComponentProps<"div">, "children">) {
  const id = useId()
  const describedBy = [hint && `${id}-hint`, error && `${id}-error`].filter(Boolean).join(" ") || undefined
  return (
    <div className={cn("space-y-1.5", className)} {...rest}>
      <label htmlFor={id} className="flex items-center gap-2 text-sm font-medium">
        {label}
        {required &&
          (requiredMark === "asterisk" ? (
            <span data-required-mark="asterisk" className="text-destructive">
              <span aria-hidden="true">*</span>
              <span className="sr-only">必須</span>
            </span>
          ) : (
            <span data-required-mark="text" className="text-destructive">
              必須
            </span>
          ))}
      </label>
      {children({ id, required: required || undefined, "aria-invalid": Boolean(error), "aria-describedby": describedBy })}
      {hint && (
        <p id={`${id}-hint`} className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}
