### E31 (B, context, figure)

Tailwind CSS default breakpoints are sm 40rem (640px), md 48rem (768px), lg 64rem (1024px), xl 80rem (1280px), 2xl 96rem (1536px), min-width, mobile-first.

Tailwind Labs, unknown, https://tailwindcss.com/docs/responsive-design

> ut only have it take effect at a certain breakpoint, all you need to do is prefix the utility with the breakpoint name, followed by the : character: HTML <!-- Width of 16 by default, 32 on medium screens, and 48 on large screens --> < img class = "w-16 md:w-32 lg:w-48 " src = "..." /> There are five breakpoints by default, inspired by common device resolutions: Breakpoint prefix Minimum width CSS sm 40rem (640px) @media (width >= 40rem) { ... } md 48rem (768px) @media (width >= 48rem) { ... } lg 64rem (1024px) @media (width >= 64rem) { ... } xl 80rem (1280px) @media (width >= 80rem) { ... } 2xl 96rem (1536px) @media (width >= 96rem) { ... } This works for every utility class in the framework , which means you can change literally anything at a given breakpoint — even things like letter spacing or cursor styles. Here's a simple example of a marketing page component that uses a stacked layout on small sc

### E32 (B, context, figure)

Tailwind CSS max-w container scale runs from max-w-3xs 16rem (256px) to max-w-7xl 80rem (1280px).

Tailwind Labs, unknown, https://tailwindcss.com/docs/max-width

> md); /* 28rem (448px) */ max-w-lg max-width: var(--container-lg); /* 32rem (512px) */ max-w-xl max-width: var(--container-xl); /* 36rem (576px) */ max-w-2xl max-width: var(--container-2xl); /* 42rem (672px) */ max-w-3xl max-width: var(--container-3xl); /* 48rem (768px) */ max-w-4xl max-width: var(--container-4xl); /* 56rem (896px) */ max-w-5xl max-width: var(--container-5xl); /* 64rem (1024px) */ max-w-6xl max-width: var(--container-6xl); /* 72rem (1152px) */ max-w-7xl max-width: var(--container-7xl); /* 80rem (1280px) */ max-w-none max-width: none; max-w-px max-width: 1px; max-w-full max-width: 100%; max-w-dvw max-width: 100dvw; max-w-dvh max-width: 100dvh; max-w-lvw max-width: 100lvw; max-w-lvh max-width: 100lvh; max-w-svw max-width: 100svw; max-w-svh max-width: 100svh; max-w-screen max-width: 100vw; max-w-min max-width: min-content; max-w-max max-width: max-content; max-w-fit max-width: fit-content; container w

### E33 (B, context, figure)

Tailwind CSS max-w-2xl is 42rem (672px) and max-w-3xl is 48rem (768px).

Tailwind Labs, unknown, https://tailwindcss.com/docs/max-width

> ainer-3xs); /* 16rem (256px) */ max-w-2xs max-width: var(--container-2xs); /* 18rem (288px) */ max-w-xs max-width: var(--container-xs); /* 20rem (320px) */ max-w-sm max-width: var(--container-sm); /* 24rem (384px) */ max-w-md max-width: var(--container-md); /* 28rem (448px) */ max-w-lg max-width: var(--container-lg); /* 32rem (512px) */ max-w-xl max-width: var(--container-xl); /* 36rem (576px) */ max-w-2xl max-width: var(--container-2xl); /* 42rem (672px) */ max-w-3xl max-width: var(--container-3xl); /* 48rem (768px) */ max-w-4xl max-width: var(--container-4xl); /* 56rem (896px) */ max-w-5xl max-width: var(--container-5xl); /* 64rem (1024px) */ max-w-6xl max-width: var(--container-6xl); /* 72rem (1152px) */ max-w-7xl max-width: var(--container-7xl); /* 80rem (1280px) */ max-w-none max-width: none; max-w-px max-width: 1px; max-w-full max-width: 100%; max-w-dvw max-width: 100dvw; max-w-dvh max-width: 100dvh; max-w

### E34 (B, context, figure)

shadcn/ui new-york-v4 Button default size is h-9 (36px) with px-4 py-2; lg is h-10 px-6.

shadcn-ui (GitHub), unknown, https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/new-york-v4/ui/button.tsx

> ark:focus-visible:ring-destructive/40", outline: "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:border-input dark:bg-input/30 dark:hover:bg-input/50", secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80", ghost: "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50", link: "text-primary underline-offset-4 hover:underline", }, size: { default: "h-9 px-4 py-2 has-[>svg]:px-3", xs: "h-6 gap-1 rounded-md px-2 text-xs has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3", sm: "h-8 gap-1.5 rounded-md px-3 has-[>svg]:px-2.5", lg: "h-10 rounded-md px-6 has-[>svg]:px-4", icon: "size-9", "icon-xs": "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3", "icon-sm": "size-8", "icon-lg": "size-10", }, }, defaultVariants: { variant: "default", size: "default", }, } ) functio

### E35 (B, context, figure)

shadcn/ui new-york-v4 Button sm is h-8 px-3 and lg is h-10 px-6; icon is size-9.

shadcn-ui (GitHub), unknown, https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/new-york-v4/ui/button.tsx

> rk:bg-input/30 dark:hover:bg-input/50", secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80", ghost: "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50", link: "text-primary underline-offset-4 hover:underline", }, size: { default: "h-9 px-4 py-2 has-[>svg]:px-3", xs: "h-6 gap-1 rounded-md px-2 text-xs has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3", sm: "h-8 gap-1.5 rounded-md px-3 has-[>svg]:px-2.5", lg: "h-10 rounded-md px-6 has-[>svg]:px-4", icon: "size-9", "icon-xs": "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3", "icon-sm": "size-8", "icon-lg": "size-10", }, }, defaultVariants: { variant: "default", size: "default", }, } ) function Button({ className, variant = "default", size = "default", asChild = false, ...props }: React.ComponentProps < "button"> & VariantProps & { asChild?: boolean }) { const Comp = asChild ? Slot.Root : "button" r

### E36 (B, context, figure)

shadcn/ui sidebar defaults: width 16rem, mobile width 18rem, icon-collapsed width 3rem.

shadcn-ui (GitHub), unknown, https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/new-york-v4/ui/sidebar.tsx

> york-v4/ui/separator" import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, } from "@/registry/new-york-v4/ui/sheet" import { Skeleton } from "@/registry/new-york-v4/ui/skeleton" import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger, } from "@/registry/new-york-v4/ui/tooltip" const SIDEBAR_COOKIE_NAME = "sidebar_state" const SIDEBAR_COOKIE_MAX_AGE = 60 * 60 * 24 * 7 const SIDEBAR_WIDTH = "16rem" const SIDEBAR_WIDTH_MOBILE = "18rem" const SIDEBAR_WIDTH_ICON = "3rem" const SIDEBAR_KEYBOARD_SHORTCUT = "b" type SidebarContextProps = { state: "expanded" | "collapsed" open: boolean setOpen: (open: boolean) => void openMobile: boolean setOpenMobile: (open: boolean) => void isMobile: boolean toggleSidebar: () => void } const SidebarContext = React.createContext (null) function useSidebar() { const context = React.useContext(SidebarContext) if (!context) { throw new

### E37 (A, context, figure)

IBM Carbon 2x grid breakpoints: Small 320px 4 columns margin 0; Medium 672px 8 columns margin 16px; Large 1056px 16 columns; Max 1584px 16 columns margin 24px; gutter padding 16px.

IBM Carbon Design System, unknown, https://carbondesignsystem.com/elements/2x-grid/overview/

> rd breakpoints to maintain layout integrity across screen sizes. For best results, test designs and code at each of these standard breakpoints. Create custom breakpoints to accommodate special needs, by writing your own media queries and CSS rules. Refer to the grid code package for more information. Breakpoint Value (px/rem) Columns Size (%) Size Padding Margin Small 320 / 20 4 25% 80 px 16 px 0 Medium 672 / 42 8 12.5% 80 px 16 px 16 px Large 1056 / 66 16 6.25% 64 px 16 px 16 px X-Large 1312 / 82 16 6.25% 80 px 16 px 16 px Max 1584 / 99 16 6.25% 96 px 16 px 24 px For best results, test designs and code at each of these standard breakpoints. Grid behaviors In user interfaces, screen size is dictated by the device and the user’s chosen window size. We may know content in advance, or the content may be dynamic. Carefully consider the user’s goal for their screen space, particularly when displaying dynamic content. If a user’s goal is to see more items, scale

### E38 (A, context, figure)

IBM Carbon data table row heights: xs 24px, sm 32px, md 40px, lg 48px, xl 64px (density modes).

IBM Carbon Design System, unknown, https://carbondesignsystem.com/components/data-table/style/

> asurements for columns in a data table | px/rem Rows Row sizes are customizable. The column header row should always match the row size of the table. Column header and row text is always centered in the row with the exception of the extra large which is offset by padding-top: 16px . Extra large row heights are only recommended if your data is expected to have two lines of content in a single row. Size Height (px / rem) Extra small (xs) 24 / 1.5 Small (sm) 32 / 2 Medium (md) 40 / 2.5 Large (lg) 48 / 3 Extra large (xl) 64 / 4 Data table row and header heights: extra small, small, medium, large, and extra large. Enhancements After the simple table structure, tables can be enhanced by adding any of the following: selectable rows, expanding rows, row menus, table batch actions, overall table menu, and/or table filter. Element Property px / rem Spacing token Checkbox height, width 20 / 

### E39 (A, context, figure)

Carbon data table text is 14px (0.875rem) for column header SemiBold and row text Regular, with 16px cell left/right padding.

IBM Carbon Design System, unknown, https://carbondesignsystem.com/components/data-table/style/

> button See ghost button Button See primary button * Denotes a contextual color token that will change values based on the layer it is placed on. Batch action bar Element Property Color token Bar background-color $background-brand Summary text-color $text-on-color Button See primary button Typography Element Font-size (px/rem) Font-weight Type token Table header 20 / 1.25 Regular / 400 $heading-03 Column header 14 / 0.875 SemiBold / 600 $heading-compact-01 Row text 14 / 0.875 Regular / 400 $body-compact-01 Structure Tables are a configurable and customizable component. Designers can pick and choose certain elements and interactions. The basic table style is the required base from which tables can be developed. Basic tables are composed of a header row followed by rows of data below. Element Property px / rem Spacing token Table header margin-top 16 / 1 $spacing-05 margin-bottom 24 / 1.5 $spacing-06

### E40 (A, context, figure)

GOV.UK Design System sets the default maximum page width at 1020px.

GOV.UK Design System, unknown, https://design-system.service.gov.uk/styles/layout/

>  layout. For most types of page, we recommend using either a ‘two-thirds’ or a ‘two-thirds and one-third’ layout. That stops lines of text getting so long that the page becomes difficult to read on desktop devices. This would usually mean no more than 75 characters per line. Never make assumptions about what devices people are using. Design for different screen sizes rather than specific devices. The default maximum page width is 1020px, but you can make it wider if your content requires it. Common layouts Two-thirds Open this example in a new tab : common two-thirds – layout HTML HTML < div class = "govuk-width-container" > < a href = "#" class = "govuk-back-link" > Back </ a > < main class = "govuk-main-wrapper" > < div class = "govuk-grid-row" > < div class = "govuk-grid-column-two-thirds" > < h1 class = "govuk-heading-xl" > Two-thirds column </ h1 > < p class = "govuk-body" > Thi

### E41 (A, context, figure)

GOV.UK spacing scale (static) units 1-9 are 5, 10, 15, 20, 25, 30, 40, 50, 60px.

GOV.UK Design System, unknown, https://design-system.service.gov.uk/styles/spacing/

>  the smallest units (0-3) stays the same for all screen sizes. The responsive spacing scale Spacing unit Small screens Large screens 0 0 0 1 5px 5px 2 10px 10px 3 15px 15px 4 15px 20px 5 15px 25px 6 20px 30px 7 25px 40px 8 30px 50px 9 40px 60px Static spacing The static spacing scale stays the same for all screen sizes, and uses the same spacing as ‘large screens’ in the responsive spacing scale. The static spacing scale Spacing unit All screens 0 0 1 5px 2 10px 3 15px 4 20px 5 25px 6 30px 7 40px 8 50px 9 60px Applying spacing in your own CSS If you want to reference the spacing scale in your CSS, use the spacing helpers. Using the responsive spacing helper To use the responsive spacing scale, include either: the govuk-responsive-margin mixin the govuk-responsive-padding mixin For example, to apply spacing unit 6 for 30px padding on large screens and 20px on small screens, use: @include govuk-responsiv

### E42 (A, context, figure)

Android/Material 3 window size classes: Compact width < 600dp; Expanded 840dp to <1200dp; Large 1200dp to <1600dp; Extra-large >= 1600dp.

Android Developers (Google), unknown, https://developer.android.com/develop/ui/compose/layouts/adaptive/window-size-classes

> esign of your breakpoint-based layouts. Size class Breakpoint Device representation Compact width width < 600dp 99.96% of phones in portrait Medium width 600dp ≤ width < 840dp 93.73% of tablets in portrait, most large unfolded inner displays in portrait Expanded width 840dp ≤ width < 1200dp 97.22% of tablets in landscape, most large unfolded inner displays in landscape are at least expanded width Large width 1200dp ≤ width < 1600dp Large tablet displays Extra-large width width ≥ 1600dp Desktop displays Compact height height < 480dp 99. 78% of phones in landscape Medium height 480dp ≤ height < 900dp 96.56% of tablets in landscape, 97.59% of phones in portrait Expanded height height ≥ 900dp 94.25% of tablets in portrait Note: Most apps can build an adaptive UI by considering only the width window size class. However, also consider the height window size class for scenarios such a

### E43 (A, context, figure)

Android documentation defines Compact width as under 600dp.

Android Developers (Google), unknown, https://developer.android.com/develop/ui/compose/layouts/adaptive/window-size-classes

>  height-based window size classes. As visualized in the figures, the breakpoints allow you to continue thinking about layouts in terms of devices and configurations. Each size class breakpoint represents a majority case for typical device scenarios, which can be a helpful frame of reference as you think about the design of your breakpoint-based layouts. Size class Breakpoint Device representation Compact width width < 600dp 99.96% of phones in portrait Medium width 600dp ≤ width < 840dp 93.73% of tablets in portrait, most large unfolded inner displays in portrait Expanded width 840dp ≤ width < 1200dp 97.22% of tablets in landscape, most large unfolded inner displays in landscape are at least expanded width Large width 1200dp ≤ width < 1600dp Large tablet displays Extra-large width width ≥ 1600dp Desktop displays Compact height height < 480dp 99

### E44 (A, context, figure)

SmartHR Design System offers two Button sizes: normal (通常) and small (小), the small for saving space; no pixel values on the page.

SmartHR Design System, unknown, https://smarthr.design/products/components/button/

> い場合があります。 単独で利用する場合は、 prefix props または suffix props にアイコンを設定し、操作できる要素であることが視覚的に伝わりやすいようにしてください。 詳しくは、 色以外の情報でもボタンであることを伝える を参照してください。 AnchorButton AnchorButtonは、リンク( a 要素)をボタンのように装飾にするコンポーネントです。 アクションボタンとして表現したい場合は、Buttonを使用してください。 リンクを新規ウィンドウで開く場合には、テキストの右側に 別タブで開く アイコン( OpenInNewTabIcon )が自動で配置されます。 レイアウト ボタンサイズやアイコンの有無で、コンポーネント内のレイアウトにバリエーションがあります。「 サイズ小 かつ アイコン付き(左) 」のように組み合わせることもできます。 ボタンサイズ 2種類の大きさのボタンを使用できます。 SmartHR UIでは、サイズ( size props)で指定できます。 種類 表示例 説明 通常 ボタン 通常のサイズです。 小 ボタン レイアウトの都合上、スペースを節約したいときに使うサイズです。 アイコンの有無 アイコンは、ボタンを押して実行される操作やUIを想起させる役割や、ボタンに視覚的なアクセントを与える役割を持ちます。 アイコン付きボタン ラベルテキストの左右にアイコンを配置できます。 SmartHR UIでは、 アイコン付き(左) はプレフィックス( prefix props)に、 アイコン付き(右) はサフィックス( suffix props)に Icon を指定することで表現できます。 アイコン付き(左) と アイコン付き(右) の例と役割は以下の表を参考にしてください。 種類 表示例 アイコンの役割 アイコン付き(左) 項目を追加 ダウンロード ボタンを押したと

### E45 (A, context, figure)

Primer React Button has three sizes: small, medium (default) and large; large is for emphasis and used sparingly.

GitHub Primer, unknown, https://primer.style/components/button

> "horizontal" align="center" wrap="wrap"> <Button variant="primary">Primary</Button> <Button variant="default">Default</Button> <Button variant="invisible">Invisible</Button> <Button variant="danger">Danger</Button> </Stack> Show full code Full-width Activate Copy Reset Open in StackBlitz code editor < Button block > Activate </ Button > <Button block>Activate</Button> Show full code Size variants Medium (default): Best for most interfaces. Small: For compact spaces or less prominent actions. Large: Use sparingly to emphasize an action. More often than not a medium sized Button will be more appropriate. Small Medium (default) Large Copy Reset Open in StackBlitz code editor < Stack direction = " horizontal " align = " center " > < Button size = " small " > Small </ Button > < Button > Medium (default) </ Button > < Button size = " large " > Large </ Button > </ Stack > <Stack direction="horizontal" align="center"> <Button size="s
