// The product's shell: the header with the product name, the navigation and the content column.
// product-ui: ignore-file S16 the navigation is a fixed list the build passes in, and the row is left out when it holds no item
import { useEffect, type ReactNode } from "react"
import { Link, NavLink, Outlet } from "react-router-dom"
import { Toaster } from "@/components/ui/sonner"
import { cn } from "@/lib/utils"

export type NavItem = { label: string; to: string }

/** Sets the title of the browser tab: the page's own title, then the product's name. */
export function usePageTitle(title: string) {
  useEffect(() => {
    document.title = title
  }, [title])
}

/**
 * `nav` lists the collections this build holds, each under the plural name of its object; an item whose view
 * the build lacks stays out. `user` is the signed-in person's name, printed as text. `maxToasts` is how many toasts
 * show at a time (`messages.max` of the brief's Conventions section), and `keysAtFoot` lifts them above a row of
 * function keys at the foot of the screen (`keys.display` `bottom`).
 */
export function AppShell({
  product,
  nav = [],
  user,
  maxToasts = 1,
  keysAtFoot = false,
  children,
}: {
  product: string
  nav?: NavItem[]
  user?: string
  maxToasts?: number
  keysAtFoot?: boolean
  children?: ReactNode
}) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-background">
        <div className="mx-auto flex min-h-14 max-w-7xl flex-wrap items-center gap-x-6 px-4 md:px-6">
          <Link to="/" className="text-base font-bold text-foreground">
            {product}
          </Link>
          {nav.length > 0 && (
            <nav aria-label="メイン" className="flex flex-wrap gap-1">
              {nav.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    cn("rounded-md px-3 py-2 text-sm hover:bg-accent", isActive ? "font-bold text-primary" : "text-foreground")
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          )}
          {user && <span className="ml-auto text-sm text-foreground">{user}</span>}
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 pt-6 pb-16 md:px-6 md:pt-8">{children ?? <Outlet />}</main>
      <Toaster
        position="bottom-right"
        duration={5000}
        visibleToasts={maxToasts}
        offset={keysAtFoot ? { bottom: 88, right: 24 } : undefined}
        mobileOffset={keysAtFoot ? { bottom: 88 } : undefined}
        containerAriaLabel="通知"
        toastOptions={{ classNames: { toast: "!text-sm", actionButton: "!h-8 !text-sm" } }}
      />
    </div>
  )
}
