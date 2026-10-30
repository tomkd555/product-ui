### E1 (B, supports, fact)

Tailwind CSS v4.3 default theme sets --spacing to 0.25rem (4px base unit).

Tailwind Labs, 2026, https://tailwindcss.com/docs/theme

> 07 39.5 ); --color-taupe-400 : oklch ( 71.4 % 0.014 41.2 ); --color-taupe-500 : oklch ( 54.7 % 0.021 43.1 ); --color-taupe-600 : oklch ( 43.8 % 0.017 39.3 ); --color-taupe-700 : oklch ( 36.7 % 0.016 35.7 ); --color-taupe-800 : oklch ( 26.8 % 0.011 36.5 ); --color-taupe-900 : oklch ( 21.4 % 0.009 43.1 ); --color-taupe-950 : oklch ( 14.7 % 0.004 49.3 ); --color-black : #000 ; --color-white : #fff ; --spacing : 0.25 rem ; --breakpoint-sm : 40 rem ; --breakpoint-md : 48 rem ; --breakpoint-lg : 64 rem ; --breakpoint-xl : 80 rem ; --breakpoint-2xl : 96 rem ; --container-3xs : 16 rem ; --container-2xs : 18 rem ; --container-xs : 20 rem ; --container-sm : 24 rem ; --container-md : 28 rem ; --container-lg : 32 rem ; --container-xl : 36 rem ; --container-2xl : 42 rem ; --container-3xl : 48 rem ; --container-4xl : 56 rem 

### E2 (B, supports, fact)

Tailwind CSS v4.3 default radius scale runs xs 0.125rem, sm 0.25rem, md 0.375rem, lg 0.5rem, then xl 0.75rem, 2xl 1rem, 3xl 1.5rem, 4xl 2rem.

Tailwind Labs, 2026, https://tailwindcss.com/docs/theme

> ld : 600 ; --font-weight-bold : 700 ; --font-weight-extrabold : 800 ; --font-weight-black : 900 ; --tracking-tighter : -0.05 em ; --tracking-tight : -0.025 em ; --tracking-normal : 0 em ; --tracking-wide : 0.025 em ; --tracking-wider : 0.05 em ; --tracking-widest : 0.1 em ; --leading-tight : 1.25 ; --leading-snug : 1.375 ; --leading-normal : 1.5 ; --leading-relaxed : 1.625 ; --leading-loose : 2 ; --radius-xs : 0.125 rem ; --radius-sm : 0.25 rem ; --radius-md : 0.375 rem ; --radius-lg : 0.5 rem ; --radius-xl : 0.75 rem ; --radius-2xl : 1 rem ; --radius-3xl : 1.5 rem ; --radius-4xl : 2 rem ; --shadow-2xs : 0 1 px rgb ( 0 0 0 / 0.05 ); --shadow-xs : 0 1 px 2 px 0 rgb ( 0 0 0 / 0.05 ); --shadow-sm : 0 1 px 3 px 0 rgb ( 0 0 0 / 0.1 ), 0 1 px 2 px -1 px rgb ( 0 0 0 / 0.1 ); --shadow-md : 0 4 px 6 px -1 px rgb ( 0 0 0 / 0.1 ), 0 2 px 4 px -2 px rgb ( 0 0 0 / 0.1 ); --shadow-lg : 0 10 px 15 px -

### E3 (B, supports, fact)

Tailwind CSS v4.3 default leading scale: tight 1.25, snug 1.375, normal 1.5, relaxed 1.625, loose 2.

Tailwind Labs, 2026, https://tailwindcss.com/docs/theme

> extralight : 200 ; --font-weight-light : 300 ; --font-weight-normal : 400 ; --font-weight-medium : 500 ; --font-weight-semibold : 600 ; --font-weight-bold : 700 ; --font-weight-extrabold : 800 ; --font-weight-black : 900 ; --tracking-tighter : -0.05 em ; --tracking-tight : -0.025 em ; --tracking-normal : 0 em ; --tracking-wide : 0.025 em ; --tracking-wider : 0.05 em ; --tracking-widest : 0.1 em ; --leading-tight : 1.25 ; --leading-snug : 1.375 ; --leading-normal : 1.5 ; --leading-relaxed : 1.625 ; --leading-loose : 2 ; --radius-xs : 0.125 rem ; --radius-sm : 0.25 rem ; --radius-md : 0.375 rem ; --radius-lg : 0.5 rem ; --radius-xl : 0.75 rem ; --radius-2xl : 1 rem ; --radius-3xl : 1.5 rem ; --radius-4xl : 2 rem ; --shadow-2xs : 0 1 px rgb ( 0 0 0 / 0.05 ); --shadow-xs : 0 1 px 2 px 0 rgb ( 0 0 0 / 0.05 ); --shadow-sm : 0 1 px 3 px 0 rgb ( 0 0 0 / 0.1 ), 0 1 px 2 

### E4 (B, supports, fact)

Tailwind CSS v4.3 default tracking scale: tighter -0.05em, normal 0em, wide 0.025em, wider 0.05em, widest 0.1em.

Tailwind Labs, 2026, https://tailwindcss.com/docs/theme

> --tracking-tighter : -0.05 em ; --tracking-normal : 0 em ; --tracking-wide : 0.025 em ;

### E5 (B, supports, fact)

Tailwind CSS v4.3 default shadow-sm is a two-layer shadow: 0 1px 3px at 10% black plus 0 1px 2px -1px at 10% black.

Tailwind Labs, 2026, https://tailwindcss.com/docs/theme

> es New Roman" , Times , serif ; --font-mono : ui-monospace , SFMono-Regular , Menlo , Monaco , Consolas , "Liberation Mono" , "Courier New" , monospace ; --color-red-50 : oklch ( 0.971 0.013 17.38 ); --color-red-100 : oklch ( 0.936 0.032 17.717 ); --color-red-200 : oklch ( 0.885 0.062 18.334 ); /* ... */ --shadow-2xs : 0 1 px rgb ( 0 0 0 / 0.05 ); --shadow-xs : 0 1 px 2 px 0 rgb ( 0 0 0 / 0.05 ); --shadow-sm : 0 1 px 3 px 0 rgb ( 0 0 0 / 0.1 ), 0 1 px 2 px -1 px rgb ( 0 0 0 / 0.1 ); /* ... */ } This is why utilities like bg-red-200 , font-serif , and shadow-sm exist out of the box — they're driven by the default theme, not hardcoded into the framework like flex-col or pointer-events-none . For a list of all of the default theme variables, see the default theme variable reference . Customizing your theme The default theme variables are very general purpose and suitable for bu

### E6 (B, supports, fact)

Tailwind CSS v4.3 default text-size scale starts at xs 0.75rem and sm 0.875rem.

Tailwind Labs, 2026, https://tailwindcss.com/docs/theme

> --text-xs : 0.75 rem ; --text-sm : 0.875 rem ;

### E7 (B, supports, fact)

shadcn/ui theming docs set the base --radius to 0.625rem in the default :root block.

shadcn/ui, unknown, https://ui.shadcn.com/docs/theming

> -foreground ); --color-sidebar-border: var(--sidebar-border ); --color-sidebar-ring: var(--sidebar-ring ); --radius-sm: calc(var(--radius ) * 0 . 6 ); --radius-md: calc(var(--radius ) * 0 .8 ); --radius-lg: var(--radius ); --radius-xl: calc(var(--radius ) * 1 .4 ); --radius-2xl: calc(var(--radius ) * 1 .8 ); --radius-3xl: calc(var(--radius ) * 2 .2 ); --radius-4xl: calc(var(--radius ) * 2 .6 ); } :root { --radius : 0.625 rem ; --background : oklch ( 1 0 0 ) ; --foreground : oklch ( 0.145 0 0 ) ; --card : oklch ( 1 0 0 ) ; --card-foreground : oklch ( 0.145 0 0 ) ; --popover : oklch ( 1 0 0 ) ; --popover-foreground : oklch ( 0.145 0 0 ) ; --primary : oklch ( 0.205 0 0 ) ; --primary-foreground : oklch ( 0.985 0 0 ) ; --secondary : oklch ( 0.97 0 0 ) ; --secondary-foreground : oklch ( 0.205 0 0 ) ; --muted : oklch ( 0.97 0

### E8 (B, supports, fact)

shadcn/ui derives radius-sm as 0.6x and radius-md as 0.8x of --radius, with radius-lg equal to --radius.

shadcn/ui, unknown, https://ui.shadcn.com/docs/theming

> e base corner radius scale. Cards, inputs, buttons, popovers, and the derived radius-* tokens. The chart tokens are covered in more detail in the Chart theming docs . Radius Scale # --radius is the base radius token for your theme. We derive a small radius scale from it so components can use consistent corner sizes while still sharing a single source of truth. app/globals.css Copy @theme inline { --radius-sm: calc(var(--radius ) * 0 .6 ); --radius-md: calc(var(--radius ) * 0 .8 ); --radius-lg: var(--radius ); --radius-xl: calc(var(--radius ) * 1 .4 ); --radius-2xl: calc(var(--radius ) * 1 .8 ); --radius-3xl: calc(var(--radius ) * 2 .2 ); --radius-4xl: calc(var(--radius ) * 2 .6 ); } This means: radius-lg is the base value. Smaller radii scale down from --radius . Larger radii scale up from --radius . Changing --radius updates the entire radius scale. Adding New Tokens # To add a new token, define it u

### E9 (B, supports, fact)

shadcn/ui colour roles are pairs of background and foreground tokens, for example primary and primary-foreground.

shadcn/ui, unknown, https://ui.shadcn.com/docs/theming

> y overriding the same tokens inside a .dark selector. See the dark mode docs for adding a theme provider and toggling the .dark class. Token Convention # We use semantic background and foreground pairs. The base token controls the surface color and the -foreground token controls the text and icon color that sits on that surface. The background suffix is omitted for the surface token. For example, primary pairs with primary-foreground . Given the following CSS variables: Copy --primary: oklch(0 .205 0 0 ); --primary-foreground: oklch(0 .985 0 0 ); The background color of the following component will be var(--primary) and the foreground color will be var(--primary-foreground) . Copy < div className = "bg-primary text-primary-foreground" > Hello </ div > Theme Tokens # These tokens live in your CSS file under :root and .dark . T

### E10 (A, supports, figure)

GOV.UK static spacing scale: units 0 to 9 equal 0, 5, 10, 15, 20, 25, 30, 40, 50, 60 px.

GOV.UK, unknown, https://design-system.service.gov.uk/styles/spacing/

>  the smallest units (0-3) stays the same for all screen sizes. The responsive spacing scale Spacing unit Small screens Large screens 0 0 0 1 5px 5px 2 10px 10px 3 15px 15px 4 15px 20px 5 15px 25px 6 20px 30px 7 25px 40px 8 30px 50px 9 40px 60px Static spacing The static spacing scale stays the same for all screen sizes, and uses the same spacing as ‘large screens’ in the responsive spacing scale. The static spacing scale Spacing unit All screens 0 0 1 5px 2 10px 3 15px 4 20px 5 25px 6 30px 7 40px 8 50px 9 60px Applying spacing in your own CSS If you want to reference the spacing scale in your CSS, use the spacing helpers. Using the responsive spacing helper To use the responsive spacing scale, include either: the govuk-responsive-margin mixin the govuk-responsive-padding mixin For example, to apply spacing unit 6 for 30px padding on large screens and 20px on small screens, use: @include govuk-responsiv

### E11 (A, supports, fact)

GOV.UK states every point on its type scale uses a line height that is a multiple of 5px.

GOV.UK, unknown, https://design-system.service.gov.uk/styles/type-scale/

> le . The type scale is a collection of font sizes and line heights that underpin all of the typographic styles on GOV.UK. It has been tested and iterated for readability on different devices. When creating new components, always start by using the existing typography styles. If you need to create a new style, align it with one of the points on the type scale. How it works Like the spacing scale , every point on the type scale uses a line height in a multiple of 5px. This creates a consistent vertical rhythm, which makes pages easier to scan and read. GOV.UK Frontend outputs CSS in relative units like em or rem . This helps the type resize better when zoomed or magnified. We’ve used pixels (px) here so it’s easier to understand. Responsive behaviour The type scale changes based on screen size. The scale for ‘large screens’ is used when the screen is wider th

### E12 (A, supports, figure)

GOV.UK large-screen body (point 19) is 19px with 25px line height; govuk-body-s (point 16) is 16px with 20px line height.

GOV.UK, unknown, https://design-system.service.gov.uk/styles/type-scale/

> changes based on screen size. The scale for ‘large screens’ is used when the screen is wider than the tablet breakpoint (640px). Large screens Point on type scale Used by Font size Line height 80 Only used in exceptional circumstances 80px 80px 48 govuk-heading-xl 48px 50px 36 govuk-heading-l 36px 40px 27 Only used in exceptional circumstances 27px 30px 24 govuk-heading-m , govuk-body-l 24px 30px 19 govuk-heading-s , govuk-body 19px 25px 16 govuk-body-s 16px 20px Small screens Point on type scale Used by Font size Line height 80 Only used in exceptional circumstances 53px 55px 48 govuk-heading-xl 32px 35px 36 govuk-heading-l 27px 30px 27 Only used in exceptional circumstances 21px 25px 24 govuk-heading-m , govuk-body-l 21px 25px 19 govuk-heading-s , govuk-body 19px 25px 16 govuk-body-s 16px 20px Using the type scale in your own CSS Include the govuk-font 

### E13 (A, supports, figure)

IBM Carbon spacing tokens $spacing-01 to $spacing-05 are 2, 4, 8, 12, 16 px, built from multiples of two, four and eight.

IBM, unknown, https://carbondesignsystem.com/elements/spacing/overview/

> ign. Each level of the spacing scale has its own token. Spacing tokens can be used inside of components for building and between components for layout spacing. Spacing scale Use the spacing scale when building individual components. It includes small increments needed to create appropriate spatial relationships for detail-level designs. This scale is applied and used within all Carbon components. Token rem px Example $spacing-01 0.125 2 $spacing-02 0.25 4 $spacing-03 0.5 8 $spacing-04 0.75 12 $spacing-05 1 16 $spacing-06 1.5 24 $spacing-07 2 32 $spacing-08 2.5 40 $spacing-09 3 48 $spacing-10 4 64 $spacing-11 5 80 $spacing-12 6 96 $spacing-13 10 160 Applying spacing The spacing scale can be applied to margin or padding properties, as well as to both vertical and horizontal edges. The token takes the place of the values normally assigned to margin and padding . The following are all approved ways to syn

### E14 (B, supports, figure)

GitHub Primer border radius tokens: small 3px, medium 6px (also default), large 12px, full 9999px.

GitHub, unknown, https://primer.style/foundations/primitives/size

> -thick Copy to clipboard 0.125rem 2px --borderWidth-thicker Copy to clipboard 0.25rem 4px --borderWidth-thin Copy to clipboard 0.0625rem 1px Border radius View in Storybook Sample CSS variable Output value Source value --borderRadius-default Copy to clipboard 0.375rem {borderRadius.medium} --borderRadius-full Copy to clipboard 624.9375rem 9999px --borderRadius-large Copy to clipboard 0.75rem 12px --borderRadius-medium Copy to clipboard 0.375rem 6px --borderRadius-small Copy to clipboard 0.1875rem 3px Outline View in Storybook Sample CSS variable Output value Source value --outline-focus-offset Copy to clipboard -0.125rem {focus.outline-offset} --outline-focus-width Copy to clipboard 0.125rem {focus.outline-width} Breakpoints View in Storybook CSS variable Output value Source value --breakpoint-xsmall Copy to clipboard 20rem 320px --breakpoint-small Copy to clipboard 34rem 544px --breakpoint-m

### E15 (B, supports, figure)

GitHub Primer base size tokens include 2px and 4px steps (base-size-2, base-size-4).

GitHub, unknown, https://primer.style/foundations/primitives/size

> 5rem -24px --base-size-negative-20 Copy to clipboard -1.25rem -20px --base-size-negative-16 Copy to clipboard -1rem -16px --base-size-negative-12 Copy to clipboard -0.75rem -12px --base-size-negative-8 Copy to clipboard -0.5rem -8px --base-size-negative-6 Copy to clipboard -0.375rem -6px --base-size-negative-4 Copy to clipboard -0.25rem -4px --base-size-negative-2 Copy to clipboard -0.125rem -2px --base-size-2 Copy to clipboard 0.125rem 2px --base-size-4 Copy to clipboard 0.25rem 4px --base-size-6 Copy to clipboard 0.375rem 6px --base-size-8 Copy to clipboard 0.5rem 8px --base-size-12 Copy to clipboard 0.75rem 12px --base-size-16 Copy to clipboard 1rem 16px --base-size-20 Copy to clipboard 1.25rem 20px --base-size-24 Copy to clipboard 1.5rem 24px --base-size-28 Copy to clipboard 1.75rem 28px --base-size-32 Copy to clipboard 2rem 32px --base-size-36 Copy to clipboard 2.25rem 3

### E16 (B, supports, fact)

Atlassian Design System uses an 8px base unit for its spacing scale.

Atlassian, unknown, https://atlassian.design/foundations/spacing

> eates a more harmonious experience for the end user. A spacing system also lays a foundation for responsive design and customisable UI density in the future, which will enhance the overall quality and accessibility of our apps. 8 pixel base unit Our spacing system is built around a base unit of 8 pixels. This base unit determines the spacing scale and ensures visual consistency across apps. Scale Building off of the 8px base unit, the main foundation of our spacing system is the spacing scale. This scale is a limited set of space values that can be used to lay out UI elements in a consistent way. Each spacing value is a multiple of the base unit and ranges from 0px to 80px to allow for flexibility while still maintaining consistency across different layouts. Space tokens The 8px base unit also forms the basis of our space

### E17 (B, supports, figure)

Atlassian space tokens include space.100 = 8px, space.150 = 12px, space.200 = 16px.

Atlassian, unknown, https://atlassian.design/foundations/spacing

> 00 is 200% of the size of the base unit, therefore represents 16px. Each space token should be used in place of the raw pixel or REM values when adding space between components or objects on a page. Usage examples are detailed below. Token Base unit multiplier REM Pixels Visual representation space. 0 0× 0rem 0px space.025 0.25× 0.125rem 2px space.050 0.5× 0.25rem 4px space.075 0.75× 0.375rem 6px space.100 1× 0.5rem 8px space.150 1.5× 0.75rem 12px space.200 2× 1rem 16px space.250 2.5× 1.25rem 20px space.300 3× 1.5rem 24px space.400 4× 2rem 32px space.500 5× 2.5rem 40px space.600 6× 3rem 48px space.800 8× 4rem 64px space.1000 10× 5rem 80px Negative values Our space token system also includes negative values from space.negative.025 to space.negative.400 (-2px to -32px) available in code. These can be useful for breaking out of a container's padding or for overlapp

### E18 (B, supports, fact)

Microsoft Fluent 2 reduces corner radius to 2px for rectangle shapes smaller than 32px.

Microsoft, unknown, https://fluent2.microsoft.design/shapes

>  reference point for floating surfaces associated with a single object, like callouts or popovers. Forms are then distinguished from their surroundings either by fills or borders. Fill Fill styles can define and emphasize a shape. Border Borders identify the bounding container on unfilled shapes, like cards. Corner radius In most cases, corner radiuses on rectangle shapes are 4 pixels by default. For shapes smaller than 32 pixels, the corner angle is reduced to 2 pixels. For large and extra-large components, 8 pixel and 12 pixel angles are used. Follow iOS and Android guidelines for mobile contexts. Corner radius tokens Use these radius tokens to change the corner radius on elements. Token Usage Value None Navigation bars, tab bars 0 pixels Small Small badges 2 pixels Medium Buttons, dropdown 4 pixels Large Large buttons 8 pixels X-Large Button sheets, popovers 1

### E19 (B, supports, fact)

Fluent 2 states the default corner radius for rectangle shapes is 4px.

Microsoft, unknown, https://fluent2.microsoft.design/shapes

>  in a list. Beak A beak offers a reference point for floating surfaces associated with a single object, like callouts or popovers. Forms are then distinguished from their surroundings either by fills or borders. Fill Fill styles can define and emphasize a shape. Border Borders identify the bounding container on unfilled shapes, like cards. Corner radius In most cases, corner radiuses on rectangle shapes are 4 pixels by default. For shapes smaller than 32 pixels, the corner angle is reduced to 2 pixels. For large and extra-large components, 8 pixel and 12 pixel angles are used. Follow iOS and Android guidelines for mobile contexts. Corner radius tokens Use these radius tokens to change the corner radius on elements. Token Usage Value None Navigation bars, tab bars 0 pixels Small Small badges 2 pixels Medium Buttons, drop

### E20 (A, supports, fact)

DADS (v2.18.2) says style guides typically define about 3 to 5 spacing scale values.

デジタル庁, 2024-05-30, https://design.digital.go.jp/dads/foundations/spacing/

> ちます。 情報やコンテンツの階層や序列に基づいて間隔値を調整します。通常、重要な要素は注目を集めるためにより大きな間隔値を与え、重要でない要素はより小さい間隔値を与えます。 読みやすさと視覚的な明確さを保つため、余白を効果的に使用します。過度な間隔で要素を詰め込むのを避け、要素間に十分なスペースがあることを確認し、密集し、詰まった感じをできる限り回避します。 レスポンシブデザインでは、異なる画面サイズやデバイスでの間隔値を考慮します。さまざまなビューポートで間隔が適切にスケーリングされ、視覚的なバランスが保たれることを確認します。 余白ルールの例 余白ルールは基準となる余白の単位を選定し、基準単位の倍率スケールからルールの範囲を決めます。一般的に利用されることの多い基準単位は8 CSS pxです。この基準単位をもとに、コンポーネントやデザインエレメントのレイアウトを検討することとなります。スタイルガイドで定義される余白スケールは、3つから5つ程度になることが多いといえます。 余白は通常コンポーネントが直接ともなっていたり、テンプレート内に定義済みとなるため、余白を単体で配置することはありません。余白スケールのトークン化は必要に応じて実施してください。 余白スケールの適用例 余白スケールは、マージンまたはパディングに適用し、レイアウトに一定のルールとしての余白ルールを提供します。下記の例では、基準単位に等倍の8 CSS px、3倍の24 CSS px、8倍の64 CSS pxという3つの余白スケールを使うという余白ルールを定めたうえで、コンポーネントを配置しています。視覚的に関係性をつくったり視認性を高めるデザインにするために、3つの異なる余白スケールを用途に応じて組 み合わせています。 余白による関係性の明示 余白の大きさを適切に調整して、情報の関連性を視覚的に示すことができます。 通常、お互いに近い位置に配置された要素は関連があると見なされます。この原則を

### E21 (A, supports, fact)

DADS sets 16 CSS px or larger as the reference size for body text and UI.

デジタル庁, unknown, https://design.digital.go.jp/dads/foundations/typography/

> たスタイルを作り上げるものです。また、大きさは可読性と視認性に直接作用するため、読みやすさや分かりやすさを確保 するうえで最も重要なデザインエレメントのひとつです。 書体の大きさには、それぞれに意図された用途や意味づけがなされます。ウェブサイトで使用される本文や見出しなど、要素に応じて割り当てられる書体の大きさは、ウェブサイト内での一貫性を保つようにしてください。 デジタル庁デザインシステムで定義する書体の大きさは、用途別に使用される書体の大きさを考慮し、規範的な大きさの目安となります。コンテンツの種類等により、必要に応じて大きさを追加したり変更したうえでスタイルガイドに反映してください。 大きさ(CSS px) 主な用途 48 ~ 64 視覚的なインパクトが必要なデザイン要素としての文字サイズ。 16 ~ 45 読み物コンテンツ向けに多く使用される見出しや本文を構成する文字サイズ。なお、本文やUIにおいては16 CSS px以上が基準値となります。 14 基本的には使用しません。フッター要素などコンテンツに付随する情報や、UIやコンテンツを構成する際の領域的な制約がある場合のように標準的な文字サイズ(16 CSS px以上)の使用が難しいケースにおいてのみ使用される文字サイズです。なお、14 CSS px未満の大きさの使用は原則として許容されません。 行ボックスの高さ( line-height ) 可読性や視覚的な認知負荷等を考慮し、読み物コンテンツにおける本文テキストの行ボックスの高さ(行高)はフォントサイズに対して少なくとも1.5倍を維持することを推奨します。この行高がもたらす行間により、視覚的に十分な余裕が生まれ、テキストが読みやすくなります。 ただし、必要となる行間は文字の大きさや用途によって異なります。見出しなど文字サイズが大きくなるものは、本文よりも行間を狭めたほうが可読性が維持されます。 また、用途によっては可読性の向

### E22 (A, supports, figure)

DADS Standard text styles use letter-spacing of 0, 1% (0.01em) or 2% (0.02em) depending on font size.

デジタル庁, unknown, https://design.digital.go.jp/dads/foundations/typography/

> 140 48 B 140% Normal テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 Dsp-64N-140 64 N 140% Dsp-57N-140 57 N 140% Dsp-48N-140 48 N 140% Standard (Std) Standardテキストは、ページの文書構造を形成する見出しや本文など、多くの要素において最も使用される普遍的なテキストスタイルです。 見出しは大きさの段階によって数種必要となりますが、見出しとして常に本文との違いが視覚的に明確になるように設定します。 見出しや本文はスマートフォンやPCなど、デバイスによってその読みやすさが異なる場合がありますので、デバイスでの可読性や視認性を考慮して、必要な場合はそれぞれのスタイルを選択してください。 視認性、可読性の観点から、基本的にフォントサイズは16 CSS px以上で使用します。 文字間隔( letter-spacing )はフォントサイズの大小に応じて、 0 、 1% ( 0.01em )、 2% ( 0.02em )に指定されています。 Bold テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 文字間隔 Std-45B-140 45 B 140% 0 Std-36B-140 36 B 140% 1% Std-32B-150 32 B 150% 1% Std-28B-150 28 B 150% 1% Std-26B-150 26 B 150% 2% Std-24B-150 24 B 150% 2% Std-22B-150 22 B 150% 2% Std-20B-150 20 B 150% 2% Std-18B-160 18 B 160% 2% Std-17B-170 17 B 170% 2% Std-16B-170 16 B 170% 2% Std-16B-175 16 B 175% 2% Normal テキストスタイル名 大きさ (CSS px) 太さ レベル

### E23 (A, supports, figure)

DADS Standard bold styles pair 18px with line height 160% and 17px or 16px with 170%, each with letter-spacing 2%.

デジタル庁, unknown, https://design.digital.go.jp/dads/foundations/typography/

> を考慮して、必要な場合はそれぞれのスタイルを選択してください。 視認性、可読性の観点から、基本的にフォントサイズは16 CSS px以上で使用します。 文字間隔( letter-spacing )はフォントサイズの大小に応じて、 0 、 1% ( 0.01em )、 2% ( 0.02em )に指定されています。 Bold テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 文字間隔 Std-45B-140 45 B 140% 0 Std-36B-140 36 B 140% 1% Std-32B-150 32 B 150% 1% Std-28B-150 28 B 150% 1% Std-26B-150 26 B 150% 2% Std-24B-150 24 B 150% 2% Std-22B-150 22 B 150% 2% Std-20B-150 20 B 150% 2% Std-18B-160 18 B 160% 2% Std-17B-170 17 B 170% 2% Std-16B-170 16 B 170% 2% Std-16B-175 16 B 175% 2% Normal テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 文字間隔 Std-45N-140 45 N 140% 0 Std-36N-140 36 N 140% 1% Std-32N-150 32 N 150% 1% Std-28N-150 28 N 150% 1% Std-26N-150 26 N 150% 2% Std-24N-150 24 N 150% 2% Std-22N-150 22 N 150% 2% Std-20N-150 20 N 150% 2% Std-18N-160 18 N 160% 2% Std-17N-170 17 N 170% 2% Std-16N-170 16 N 170% 2% Std-16N-175 16 N 175% 2% Dense (Dns) Denseテキストは管理画面や業務シ

### E24 (A, supports, figure)

DADS Dense text styles for admin screens include 14px at line height 120%.

デジタル庁, unknown, https://design.digital.go.jp/dads/foundations/typography/

> の情報提示など、表示領域に制約がある場合のテキストスタイルとして使用します。 すべての文字間隔( letter-spacing )は 0 に指定されています。 Bold テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 Dns-17B-130 17 B 130% Dns-17B-120 17 B 120% Dns-16B-130 16 B 130% Dns-16B-120 16 B 120% Dns-14B-130 14 B 130% Dns-14B-120 14 B 120% Normal テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 Dns-17N-130 17 N 130% Dns-17N-120 17 N 120% Dns-16N-130 16 N 130% Dns-16N-120 16 N 120% Dns-14N-130 14 N 130% Dns-14N-120 14 N 120% Oneline (Oln) Onelineテキストは1行展開を前提として、主にUI要素への適用を想定したテキストスタイルです。 行間の余白を最小限にすることでUIパーツに対するデザイン、及びコーディング実装調整コストの軽減を優先したデキストスタイルとなります。 すべての行高は 100% に設定されています。 すべての文字間隔( letter-spacing )は 2% ( 0.02em )に指定されています。 Bold テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 Oln-17B-100 17 B 100% Oln-16B-100 16 B 100% Oln-14B-100 14 B 100% Normal テキストスタイル名 大きさ (CSS px) 太さ レベル 行高 Oln-17N-100 17 N 100% Oln-16N-100 16 N 100% Oln-

### E25 (A, supports, fact)

DADS lists 150% as the minimum line height for body text on general websites.

デジタル庁, unknown, https://design.digital.go.jp/dads/foundations/typography/

> 用途によっては可読性の向上以外の事項が優先される場合があります。たとえば管理画面や業務用システムの画面など、限られた画面領域で表示する情報量を優先したい場合などは、行間をかなり狭めた表示にすることがあります。 デジタル庁デザインシステムでは多様な用途を鑑みて、用途別に目安としての行高を幅広く定義しています。これらの行高をウェブサイトや画面別の目的に従って追加、変更して使用します。 行高の定義 line-height 主な用途 100% 主にボタンなど、コンポーネント内で使用されるワンラインのテキストで上下の余白を持っていない行間 120% 主に管理画面や業務システムの画面等で、膨大な情報を一覧表示したりなど、限られた画面領域での表示情報量を最優先した行間 130% 主に管理画面や業務システムの画面等で使用する、表示情報量を優先した行間 140% 見出しなど、やや大きな文字に使用される行間 150% 一般的なウェブサイトの本文や見出しで使用される行間(本文の行間としては最低限度) 160% 一般的なウェブサイトの本文で使用される行間 170% 一般的なウェブサイトの本文で使用する、心理的負荷の軽減を考慮した行間 175% 一般的なウェブサイトの本文で使用する、心理的負荷の軽減を考慮した行間。採用するグリッド幅やフォントサイズに応じて170%と使い分ける 注意:Figmaの仕様上、 line-height の値に % を使用していますが、実際のCSSではnumber(単位なし数値)で実装してください。 テキストスタイル名の構成 テキストスタイルにフォントのサイズや太さ、行高といったフォントプロパティをつなげてタイポグラフィトークンを定義しています。 テキストスタイルの種類 用途に応じて使用可能な5種類のテキストスタイルを用意しています。 Display (Dsp) Displayテキストは、主に冒頭で大きく掲出されるテキストやメッセージを伝えるヘッドコピーなど、視覚

### E26 (A, supports, fact)

DADS defines drop shadow Style 1 to 8 applied by elevation level.

デジタル庁, 2025-10-29, https://design.digital.go.jp/dads/foundations/elevation/

> 操作を遮断するために、オーバーレイ表示の上のコンポーネントとの間に敷き詰められる透過背景です。 ドロップシャドウとエレベーション ドロップシャドウは、ボタンやカードなどのエレベーションをもちうるコンポーネントが、その下にある背景(bodyのサーフェス)に影を落とす視覚効果です。高さレベル0の場合、それらは背景の表面上に描かれている表現となります。高さレベル1の時はドロップシャドウが強くなり、背景からわずかに浮いているように見える表現となります。疑似的な立体感を提供するドロップシャドウは、要素への注意をひいたり、可視性や階層感 を高めるためによく使用されます。 ドロップシャドウの色、サイズ、透明度を調整することで、単一要素あるいは要素同士のエレベーションを演出します。 ほとんどの要素の高さは高さレベル0です。サービス全体で使用するコンポーネントがそれぞれどのような高さレベルをもつかを定義し、高さレベルに応じたStyle 1~8のドロップシャドウを適用してください。 ドロップシャドウは、ダイアログやスナックバーなど、エレベーションをもちうるコンポーネントで使用されます。ドロップシャドウの効果は下地との視覚的な高さを表現します。サービス全体で使用する各コンポーネントで必要な高さレベルに応じたスタイルを適用します。 基本となる高さレベルを設定し、それを元に必要なレベルをいくつか設定します。 サービス全体で使用するコンポーネントを網羅したうえで、必要となる高さレベルを考えることで、デザインに統一感をもたらすだけでなく、高さの違いから生じる矛盾も回避できます。 多くの場合、高さのレベルの高いものはオーバーレイ表示するコンポーネントが覆いかぶさる表現のために、あるいはHover時にボタンが飛び出すような視覚効果として使用されます。 ドロップシャドウでコントラスト比を確保することはできません 高さを持つ要素は、その要素が置かれる面(背景色)に対して、3:1以上

### E27 (A, supports, figure)

Web Almanac 2022 CSS chapter: font-size values use px in 71% of declarations and em in 15% (2022 data).

HTTP Archive, 2022, https://almanac.httparchive.org/en/2022/css

> wing the length units used on the most pages. The most popular length unit is pixels ( px ), used on 71% of pages, followed by percentage ( % ) on 18%, em on 8%, and rem on 2%. Figure 1.13. Most popular <length> units by percent of pages. Pixel lengths remain the most popular at 71%, the same percentage as in 2021. The spread of usage remains roughly the same too. Property px <number> em % rem pt font-size (▲2%) 71% 2% (▼1%) 15% 5% (▲1%) 6% (▼1%) 2% border-radius (▼1%) 64% (▼1%) 20% 3.13% (▲1%) 11% (▲2%) 2% 0% line-height (▼5%) 49% (▲4%) 35% 12.94% (▼1%) 2% (▲1%) 1% 0% border (▼1%) 70% 28% 2% 0% 0% 0% text-indent (▼5%) 26% (▲13%) 65% (▼4%) 5% (▼3%) 5% 0% 0% vertical-align (▼26%) 3% (▼9%) 3% (▲39%) 94% 0% 0% 0% gap (▲4%) 25% (▼6%) 10% (▲32%) 33% 0% (▼31%) 32% 0% margin-inline-start (▼31%) 7% (▲3%) 49% (▲30%) 44% 0% 0% 0% grid-gap (▲5%) 68% (▼

### E28 (A, supports, figure)

Web Almanac 2022 CSS chapter: line-height uses px in 49% and unitless numbers in 35% of declarations (2022 data).

HTTP Archive, 2022, https://almanac.httparchive.org/en/2022/css

> ollowed by percentage ( % ) on 18%, em on 8%, and rem on 2%. Figure 1.13. Most popular <length> units by percent of pages. Pixel lengths remain the most popular at 71%, the same percentage as in 2021. The spread of usage remains roughly the same too. Property px <number> em % rem pt font-size (▲2%) 71% 2% (▼1%) 15% 5% (▲1%) 6% (▼1%) 2% border-radius (▼1%) 64% (▼1%) 20% 3.13% (▲1%) 11% (▲2%) 2% 0% line-height (▼5%) 49% (▲4%) 35% 12.94% (▼1%) 2% (▲1%) 1% 0% border (▼1%) 70% 28% 2% 0% 0% 0% text-indent (▼5%) 26% (▲13%) 65% (▼4%) 5% (▼3%) 5% 0% 0% vertical-align (▼26%) 3% (▼9%) 3% (▲39%) 94% 0% 0% 0% gap (▲4%) 25% (▼6%) 10% (▲32%) 33% 0% (▼31%) 32% 0% margin-inline-start (▼31%) 7% (▲3%) 49% (▲30%) 44% 0% 0% 0% grid-gap (▲5%) 68% (▼1%) 10% (▼2%) 7% 0% (▼1%) 15% 0% margin-block-end (▼1%) 3% (▲54%) 85% (▼53%) 12% 0% 0% 0% padding-inl

### E29 (A, supports, figure)

Web Almanac 2022 CSS chapter: six-digit #RRGGBB hex is used on 49% of pages, the most common colour format (2022 data).

HTTP Archive, 2022, https://almanac.httparchive.org/en/2022/css

>  been a small increase in the number of properties with a depth of one, and a small decrease in the number with a depth of two. However, it does not seem from the data that our use of custom properties has become much more complex in the past year. Colors Explore the results View data View query View image Show description of Figure 1.28 Bar chart showing the color formats used on the most pages. the six-digit #RRGGBB syntax is used on 49% of pages, three-digit #RGB on 25% of pages, the rgba function on 14% of pages, the transparent keyword on 8% of pages, a named color on 2%, the rgb function on 1%, and the rest of the formats were used on less than 1% of pages, including: eight-digit #RRGGBBAA , hsla function, currentColor keyword, four-digit #RGBA , system color keywords, hsl function, color function, hwb function, lch function, and fina

### E30 (A, supports, fact)

The 2025 Web Almanac lists 16 chapters starting with Fonts, WebAssembly, Third Parties and Generative AI; its table of contents has no CSS chapter (2024 CSS page not retrievable here).

HTTP Archive, 2025, https://almanac.httparchive.org/en/2025/

> The 2025 Web Almanac Skip navigation Web Almanac By HTTP Archive Contributors Methodology Search Search Search Search Table of Contents Table of Contents Home Table of Contents Foreword Part I. Page Content Chapter 1: Fonts Chapter 2: WebAssembly Chapter 3: Third Parties Chapter 4: Generative AI Part II. User Experience Chapter 5: SEO Chapter 6: Accessibility Chapter 7: Performance Chapter 8: Privacy Chapter 9: Security Chapter 10: Capabilities Chapter 11: PWA Part III. Content Publishing Chapter 12: CMS Chapter 13: Ecommerce Part IV. Content Distribution Chapter 14: Page Weight Chapter 15: CDN Chapter 16: Cookies Appendices Methodology Contributors Search Ebook Ebook PDF (12MB) 2025 202
