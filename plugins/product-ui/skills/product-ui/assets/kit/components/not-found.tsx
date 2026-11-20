// The screen of an address the product does not have, shown inside the shell.
import { Link } from "react-router-dom"
import { usePageTitle } from "@/components/app-shell"

/** `home` is the collection the reader goes on from, under its own name. */
export function NotFound({ product, home }: { product: string; home: { label: string; to: string } }) {
  usePageTitle(`ページが見つかりません | ${product}`)
  return (
    <div className="space-y-4 py-12">
      <h1 className="text-xl font-bold">ページが見つかりません</h1>
      <p className="text-base">アドレスに誤りがないか確認してください。</p>
      <p className="text-base">
        <Link to={home.to} className="text-primary underline underline-offset-4">
          {home.label}
        </Link>
      </p>
    </div>
  )
}
