### E94 (B, supports, fact)

Anthropic's cookbook aesthetics prompt tells the model to avoid generic fonts such as Arial and Inter (vendor-authored prompt).

Anthropic, unknown, https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/coding/prompting_for_frontend_aesthetics.ipynb

> etadata": {}, "outputs": [], "source": [ "DISTILLED_AESTHETICS_PROMPT = \"\"\"\n", " \n", "You tend to converge toward generic, \"on distribution\" outputs. In frontend design, this creates what users call the \"AI slop\" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight. Focus on:\n", "\n", "Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.\n", "\n", "Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.\n", "\n", "Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus o

### E95 (B, supports, fact)

The same prompt lists clichéd color schemes, naming purple gradients on white backgrounds, as an AI-generated aesthetic to avoid.

Anthropic, unknown, https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/coding/prompting_for_frontend_aesthetics.ipynb

> eals (animation-delay) creates more delight than scattered micro-interactions.\n", "\n", "Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.\n", "\n", "Avoid generic AI-generated aesthetics:\n", "- Overused font families (Inter, Roboto, Arial, system fonts)\n", "- Clichéd color schemes (particularly purple gradients on white backgrounds)\n", "- Predictable layouts and component patterns\n", "- Cookie-cutter design that lacks context-specific character\n", "\n", "Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid th

### E96 (B, supports, fact)

The prompt names Space Grotesk as a font the model still converges on, showing its own avoid-list is shifting.

Anthropic, unknown, https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/coding/prompting_for_frontend_aesthetics.ipynb

> Arial, system fonts)\n", "- Clichéd color schemes (particularly purple gradients on white backgrounds)\n", "- Predictable layouts and component patterns\n", "- Cookie-cutter design that lacks context-specific character\n", "\n", "Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!\n", " \n", "\"\"\"" ] }, { "cell_type": "markdown", "metadata": {}, "source": [ "## Results\n", "\n", "Here are the results of UI generations both with and without the prompt section above.\n", "\n", "Without guidance, Claude often defaults to simplistic designs with white and purple backgrounds. With the aesthetics prompt, it produces mo

### E97 (B, supports, fact)

The cookbook's only before/after evidence for the prompt is a qualitative statement with no rating or sample size; self-reported by the vendor.

Anthropic, unknown, https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/coding/prompting_for_frontend_aesthetics.ipynb

>  Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!\n", " \n", "\"\"\"" ] }, { "cell_type": "markdown", "metadata": {}, "source": [ "## Results\n", "\n", "Here are the results of UI generations both with and without the prompt section above.\n", "\n", "Without guidance, Claude often defaults to simplistic designs with white and purple backgrounds. With the aesthetics prompt, it produces more varied and visually interesting designs.\n", "\n", "### Example 1: SaaS Landing Page\n", "**Prompt:** `\"Create a SaaS landing page for a project management tool\"`\n", "\n", " \n", " \n", " \n", "\n", "**Without Aesthetics Prompt**\n", "\n", "![Baseline output without aesthetics guidance](../images/frontend_aesthetics/baseline_saas.png)\n", "\n", " \n", " \n", "\n", "**With Aesthetics Prompt**\n", "\n", "![Enhanced output with distille

### E98 (B, supports, fact)

Anthropic's frontend-design skill (undated, current repo version) says fade-and-slide-up section entrances and hover transitions on every card read as AI-generated.

Anthropic (anthropics/skills), unknown, https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md

> numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence. Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed. Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance. ## Process: plan, revi

### E99 (B, supports, fact)

The frontend-design skill lists #D97757 (Anthropic's own accent) as a tell in user briefs.

Anthropic (anthropics/skills), unknown, https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md

> with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance. ## Process: plan, review against the brief, build, critique For calibration, AI-generated design right now clusters around some traits: 1. a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta or warm-clay accent (often near #D97757 — Anthropic's own Claude-interaction accent, so on a user's brief it reads as a tell); 2. a near-black background with a single bright acid-green or vermilion accent; 3. a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns; 4. the SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow (rgba(0,0,0,.1)) under each, and gradient washes as decoration;

### E100 (B, supports, fact)

The frontend-design skill names a SaaS-card kit (identical shadows, gradient washes as decoration) among traits of AI-generated design.

Anthropic (anthropics/skills), unknown, https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md

> y accent (often near #D97757 — Anthropic's own Claude-interaction accent, so on a user's brief it reads as a tell); 2. a near-black background with a single bright acid-green or vermilion accent; 3. a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns; 4. the SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow (rgba(0,0,0,.1)) under each, and gradient washes as decoration; 5. template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots ('A · B · C'); labels built as 'WORD — fragment' with a spaced em dash; tinted near-black (#0B0B0B, #111) standing in for black; a monospace face for small data labels; a '→' appended to link and button text. All traits are legitimate for some briefs

### E101 (B, context, fact)

Vercel's web-interface-guidelines forbid 'transition: all'; the rule set targets accessibility, interaction and performance, with no AI-look rules.

Vercel Labs, unknown, https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md

> next to fields; focus first error on submit - Placeholders end with `...` and show example pattern - `autocomplete="off"` on non-auth fields to avoid password manager triggers - Warn before navigation with unsaved changes (`beforeunload` or router guard) ### Animation - Honor `prefers-reduced-motion` (provide reduced variant or disable) - Animate `transform`/`opacity` only (compositor-friendly) - Never `transition: all`—list properties explicitly - Set correct `transform-origin` - SVG: transforms on ` ` wrapper with `transform-box: fill-box; transform-origin: center` - Animations interruptible—respond to user input mid-animation - Autoplay motion >5 seconds alongside other content needs pause, stop, or hide controls - Muted decorative loops must stop under `prefers-reduced-motion` ### Typography - `...` not `...` - Curly quotes `“` `”` no

### E102 (B, context, fact)

Vercel's guidelines forbid removing the focus outline without a replacement.

Vercel Labs, unknown, https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md

> , ` `, ` `, ` `) before ARIA - Headings hierarchical ` `–` `; include skip link for main content - `scroll-margin-top` on heading anchors - Meaningful media needs captions, transcripts, or descriptions as applicable - Media controls need keyboard support; decorative media needs assistive-tech hiding ### Focus States - Interactive elements need visible focus: `focus-visible:ring-*` or equivalent - Never `outline-none` / `outline: none` without focus replacement - Use `:focus-visible` over `:focus` (avoid focus ring on click) - Group focus with `:focus-within` for compound controls - Sticky headers/footers/overlays must not cover the focused element ### Forms - Inputs need `autocomplete` and meaningful `name` - Use correct `type` (`email`, `tel`, `url`, `number`) and `inputmode` - Never block paste (`onPaste` + `preventDefault`) - Labels clickable (`html

### E103 (C, supports, figure)

Impeccable (95.8k GitHub stars at fetch) ships a no-LLM detector of 62 deterministic rules for AI-slop tells (self-described).

Paul Bakaus (GitHub), 2026, https://github.com/pbakaus/impeccable

> for what you want. "Make it pop" leaves your agent to guess. /impeccable bolder the pricing cards loads a playbook written for that one move and points it at one target. A reviewer. critique scores the design against usability heuristics and ranks what to fix first. audit checks accessibility, performance, theming, and responsive behavior, with findings ranked P0 (blocking) to P3 (polish). A slop detector. 62 deterministic rules flag the tells above, plus quality problems like cramped padding and skipped headings. No LLM, no API key. Impeccable is strongest on interfaces that already exist: point it at a page or a component and iterate. It builds new pages too; see Build something new for how to get the most out of that harder mode. To start, pick one component: /impeccable critique the pricing cards How it works Run /impeccable init once per project. It reads your code, asks only what it can't infer (who the product is for, 

### E104 (C, supports, fact)

Impeccable's README lists as recurring tells: Inter for everything, purple-to-blue gradients, nested cards.

Paul Bakaus (GitHub), 2026, https://github.com/pbakaus/impeccable

> mpeccable Same model (Fable 5.1), same brief: a fourteen-room family guesthouse on the Ligurian coast. Without Impeccable, it builds the tasteful default: cream page, thin serif, italic accent, pill buttons. With it, the page is built around one picture: the house at night, seen from the water. For a full project, see the Neo Mirai case study : a conference site taken from mockup to shipped page. Why Inter for everything. Purple-to-blue gradients. Cards nested in cards, gray text on colored backgrounds, a rounded-square icon tile above every heading. Ask an agent for a page with no other guidance and these show up again and again, across models and projects. Words for what you want. "Make it pop" leaves your agent to guess. /impeccable bolder the pricing cards loads a playbook written for that one move and points it at one target. A reviewer. critique scores the desi

### E105 (C, context, fact)

Impeccable's detector is a CLI that scans a directory or rendered URL.

Paul Bakaus (GitHub), 2026, https://github.com/pbakaus/impeccable

> your agent edits and hands the findings back before the agent calls the work done. This is where most slop gets caught: without the hook, the detector only runs when someone remembers to run it. It's available on Claude Code, Cursor, Codex, GitHub Copilot, Grok Build, and Hermes Agent, and the installer sets it up. Say yes. Automatic design checks . In CI or your terminal. The CLI needs no agent: npx impeccable detect src/ # scan a directory npx impeccable detect https://example.com # scan a rendered page (uses your installed Chrome or Edge) npx impeccable detect --json . # machine-readable output npx impeccable detect --github src/ # GitHub Actions annotations npx impeccable detect --list-rules # every rule with its id and description Source files like JSX and TSX get the pattern rules only. Rules that need a rendered page, such as low contrast and tiny text, run when you scan a URL, so point the

### E106 (C, supports, figure)

The ux-skill repo documents 152 regex-based anti-pattern rules powering a linter for AI-generated UI tells (self-described).

Laith0003 (GitHub), 2026-06, https://github.com/Laith0003/ux-skill/wiki/Anti-Patterns-Reference

> d to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert {{ message }} Laith0003 ux-skill Repository navigation Code Issues Pull requests 1 ( 1 ) Discussions Actions Projects Wiki Security and quality Insights More items Anti Patterns Reference Jump to bottom Laith0003 edited this page Jun 3, 2026 · 1 revision Anti-Patterns Reference This page documents the 152 anti-pattern rules that power the ux-skill linter. Each rule encodes one tell of AI-generated UI: a specific, repeatable choice that unconstrained models reach for by default, which makes their output recognizable as machine-made. The linter is deterministic and regex-based, runs with no model call, and exits non-zero on Critical and High findings, so it is safe to put in CI. The rule data lives in data/anti-patterns.json and is the canonical sou

### E107 (C, supports, fact)

anti-ai-slop skill's first hard rule bans unbranded purple/indigo and reflexive gradients.

Vinayak Shukla (GitHub), 2026, https://github.com/Vinayak-Shukla-03/anti-ai-slop

> rences/web-ui.md App / dashboard / landing-page tells + fixes, plus a reliability section (a blank page can't be un-slopped). references/presentations.md Deck / slide tells + fixes (kicker-every-slide, bullet-rhythm, thank-you-slide, the "deck chrome" kit). references/toolkit.md Concrete swap-ins: palettes, font pairings, scales — and a divergence matrix so a set of artifacts doesn't re-converge. The nine hard rules (the short version) No unbranded purple/indigo and no reflexive gradient. Never the system font or Inter/Geist flat — a real display + body pairing. No uniform-everything — a radius/padding hierarchy; size and space signal priority. No emoji as icons — a real, consistent icon set. No transition: all and no blanket fade-in — purposeful motion only. No benefit-speak ("Elevate", "Unlock", "Seamlessly", "not X — it's Y"). No fabricated precision — real numbers with a source, or none. Break the tem

### E108 (C, supports, fact)

anti-ai-slop bans Inter/Geist used flat, uniform radius/padding and emoji as icons.

Vinayak Shukla (GitHub), 2026, https://github.com/Vinayak-Shukla-03/anti-ai-slop

> pped). references/presentations.md Deck / slide tells + fixes (kicker-every-slide, bullet-rhythm, thank-you-slide, the "deck chrome" kit). references/toolkit.md Concrete swap-ins: palettes, font pairings, scales — and a divergence matrix so a set of artifacts doesn't re-converge. The nine hard rules (the short version) No unbranded purple/indigo and no reflexive gradient. Never the system font or Inter/Geist flat — a real display + body pairing. No uniform-everything — a radius/padding hierarchy; size and space signal priority. No emoji as icons — a real, consistent icon set. No transition: all and no blanket fade-in — purposeful motion only. No benefit-speak ("Elevate", "Unlock", "Seamlessly", "not X — it's Y"). No fabricated precision — real numbers with a source, or none. Break the template skeleton — content and audience drive structure. No second-order monoculture — if you make a set , force it to diverge (ground, display face, accent, stance). Plus a ship-blocke

### E109 (C, supports, fact)

anti-ai-slop bans blanket fade-ins and benefit-speak copy.

Vinayak Shukla (GitHub), 2026, https://github.com/Vinayak-Shukla-03/anti-ai-slop

> rings, scales — and a divergence matrix so a set of artifacts doesn't re-converge. The nine hard rules (the short version) No unbranded purple/indigo and no reflexive gradient. Never the system font or Inter/Geist flat — a real display + body pairing. No uniform-everything — a radius/padding hierarchy; size and space signal priority. No emoji as icons — a real, consistent icon set. No transition: all and no blanket fade-in — purposeful motion only. No benefit-speak ("Elevate", "Unlock", "Seamlessly", "not X — it's Y"). No fabricated precision — real numbers with a source, or none. Break the template skeleton — content and audience drive structure. No second-order monoculture — if you make a set , force it to diverge (ground, display face, accent, stance). Plus a ship-blocker: render it and look before calling any UI done — beautiful code that doesn't mount 

### E110 (C, context, figure)

anti-ai-slop's validation is a self-run 10-artifact corpus (5 apps, 5 decks) rebuilt and scored by its author; no external rater data (self-reported, 10 stars).

Vinayak Shukla (GitHub), 2026, https://github.com/Vinayak-Shukla-03/anti-ai-slop

> bricated precision — real numbers with a source, or none. Break the template skeleton — content and audience drive structure. No second-order monoculture — if you make a set , force it to diverge (ground, display face, accent, stance). Plus a ship-blocker: render it and look before calling any UI done — beautiful code that doesn't mount is worth zero. How it was built Empirically, not from vibes. A baseline corpus of 10 artifacts (5 apps + 5 decks) was generated with no design guidance to capture Claude's unprompted defaults, dissected for recurring tells, cross-checked against how designers and dev communities describe "AI slop," distilled into these rules, then used to rebuild the same 10 — and the rebuilds were rendered and scored. A second pass caught a second-order monoculture (the fix's own overused escape hatch) and hardened the skill with the ant

### E111 (B, context, figure)

UI-Bench (arXiv 2025-08) benchmarks 10 AI text-to-app tools with 300 sites and 4,000+ expert pairwise judgments; it ranks visual quality and does not measure whether output looks AI-made.

arXiv, 2025-08, https://arxiv.org/abs/2508.20410

> ies of AI Text-to-App Tools, by Sam Jung and 2 other authors View PDF HTML (experimental) Abstract: AI text-to-app tools promise high quality applications and websites in minutes, yet no public benchmark rigorously verifies those claims. We introduce UI-Bench, the first large-scale benchmark that evaluates visual excellence across competing AI text-to-app tools through expert pairwise comparison. Spanning 10 tools, 30 prompts, 300 generated sites, and 4,000+ expert judgments, UI-Bench ranks systems with a TrueSkill-derived model that yields calibrated confidence intervals. UI-Bench establishes a reproducible standard for advancing AI-driven web design. We release (i) the complete prompt set, (ii) an open-source evaluation framework, and (iii) a public leaderboard. The generated sites rated by participants will be released soon. View the UI-Bench leaderboard at this h
