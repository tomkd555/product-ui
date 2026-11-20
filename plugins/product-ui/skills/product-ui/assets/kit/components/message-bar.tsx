// The result of an operation, or an error the reader acts on (patterns/feedback.message.json), in the form the
// brief's Conventions section gives: a toast, a bar at the top of the content, or a line beside the control.
import { useCallback, useRef, useState, type ComponentProps, type ReactNode } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export type MessageTone = "success" | "error" | "info"
export type MessageKind = "toast" | "bar" | "near-control"
export type Message = { id: number; text: string; tone: MessageTone; undo?: () => void }
/** `messages.result`, `messages.duration_ms` (`null` for until-closed) and `messages.max` of the Conventions section. */
export type MessageRules = { result: MessageKind | "new-entry"; durationMs: number | null; max: number }

const TONE: Record<MessageTone, string> = {
  success: "border-border",
  info: "border-border",
  error: "border-destructive text-destructive",
}

/**
 * One message. `durationMs` is the time it stays, or `null` when it stays until closed; a message that stays
 * carries the control that closes it. `undo` adds 元に戻す for an operation that can be taken back.
 */
export function MessageBar({
  kind,
  tone = "success",
  durationMs,
  undo,
  onClose,
  className,
  children,
  ...rest
}: {
  kind: MessageKind
  tone?: MessageTone
  durationMs: number | null
  undo?: () => void
  onClose?: () => void
  children: ReactNode
} & ComponentProps<"div">) {
  return (
    <div
      data-pattern="feedback.message"
      data-message="result"
      data-message-kind={kind}
      data-duration={durationMs ?? "until-closed"}
      role={tone === "error" ? "alert" : "status"}
      className={cn(
        "flex items-center gap-3 rounded-md border bg-background px-4 py-3 text-sm",
        kind === "toast" && "w-[22rem] max-w-[calc(100vw-2rem)] shadow-md",
        TONE[tone],
        className,
      )}
      {...rest}
    >
      <p data-pattern-slot="text" className="min-w-0 flex-1">
        {children}
      </p>
      {undo && (
        <Button type="button" variant="outline" data-pattern-slot="action" className="h-8" onClick={undo}>
          元に戻す
        </Button>
      )}
      {durationMs === null && onClose && (
        <Button type="button" variant="ghost" data-pattern-slot="close" className="h-8" onClick={onClose}>
          閉じる
        </Button>
      )}
    </div>
  )
}

/**
 * The messages of one screen under the rules of the Conventions section. `show` adds a message: a toast goes to the
 * toaster of the shell, a bar or a line beside the control goes into `messages`, which the screen renders with
 * `Messages`. The newest `max` stay, and a timed one leaves after `durationMs`; for toasts the shell holds the
 * limit (`maxToasts` of `AppShell`). Under `new-entry` nothing is shown:
 * the screen empties its form and returns the focus to the first field.
 */
export function useMessages({ result, durationMs, max }: MessageRules) {
  const [messages, setMessages] = useState<Message[]>([])
  const next = useRef(0)
  const close = useCallback((id: number) => setMessages((list) => list.filter((message) => message.id !== id)), [])
  const show = useCallback(
    (text: string, options: { tone?: MessageTone; undo?: () => void } = {}) => {
      const tone = options.tone ?? "success"
      if (result === "new-entry") return
      if (result === "toast") {
        toast.custom(
          (id) => (
            <MessageBar kind="toast" tone={tone} durationMs={durationMs} undo={options.undo} onClose={() => toast.dismiss(id)}>
              {text}
            </MessageBar>
          ),
          { duration: durationMs ?? Infinity },
        )
        return
      }
      const id = ++next.current
      setMessages((list) => [...list, { id, text, tone, undo: options.undo }].slice(-max))
      if (durationMs !== null) window.setTimeout(() => close(id), durationMs)
    },
    [result, durationMs, max, close],
  )
  return { messages, show, close }
}

/** The bar or the line beside the control: place it at the top of the content, or next to the control that ran. */
export function Messages({
  messages,
  kind,
  durationMs,
  onClose,
  className,
}: {
  messages: Message[]
  kind: Exclude<MessageKind, "toast">
  durationMs: number | null
  onClose: (id: number) => void
  className?: string
}) {
  if (messages.length === 0) return null
  return (
    <div className={cn("space-y-2", className)}>
      {messages.map((message) => (
        <MessageBar
          key={message.id}
          kind={kind}
          tone={message.tone}
          durationMs={durationMs}
          undo={message.undo}
          onClose={() => onClose(message.id)}
        >
          {message.text}
        </MessageBar>
      ))}
    </div>
  )
}
