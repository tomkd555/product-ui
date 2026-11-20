// What a form does on submit: every field checked at once, the messages shown beside their fields,
// the focus moved to the first field in error. The submit button stays enabled throughout.

/** One rule per field: the message of the first rule that fails, in the words of references/ui-copy.md (Error messages). */
export type Rules<V> = { [K in keyof V]?: (value: V[K], values: V) => string | undefined }
export type Errors<V> = { [K in keyof V]?: string }

export function validate<V extends Record<string, unknown>>(values: V, rules: Rules<V>): Errors<V> {
  const errors: Errors<V> = {}
  for (const key of Object.keys(rules) as (keyof V)[]) {
    const message = rules[key]?.(values[key], values)
    if (message) errors[key] = message
  }
  return errors
}

/** Moves the focus to the first control of the form marked `aria-invalid`. Call it after the errors have rendered. */
export function focusFirstInvalid(form: HTMLFormElement | null) {
  const control = form?.querySelector<HTMLElement>('[aria-invalid="true"]')
  control?.focus()
  control?.scrollIntoView({ block: "center" })
}
