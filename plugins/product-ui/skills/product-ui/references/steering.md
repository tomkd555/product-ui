# Steering an existing screen

A named adjustment of a screen that already ships: 「もっと大胆に」「落ち着かせて」「削ぎ落として」, or the English verbs below. It runs in LIGHT mode on the tokens already in place, then the Step 4 checks.

Two principles hold for every verb. The brief wins over taste. A refinement keeps what the screen already has: it changes only the target the request names, and adds no colour, font, radius, shadow or token the screen does not already own. Where the tokens cannot express the change, name the exact addition and the job it would do, and ask before making it.

Adapted from impeccable 4.8.0, `skill/reference/*.md` (Apache-2.0, Paul Bakaus); see `THIRD_PARTY_NOTICES.md`.

## Verbs that go elsewhere

| Verb | Goes to |
|---|---|
| colorize | `interfaces:better-colors`, within `tokens.json` |
| typeset | `interfaces:better-typography` |
| layout | `interfaces:better-layout`, `references/composition.md` |
| animate | `emil-design-eng` |
| optimize | `agent-skills:performance-optimization` |
| harden | S10, S16 and S17, the brief's States section, `interfaces:break` |
| clarify | C1-C32 in `references/ui-copy.md`, the shippable-text-auditor |
| adapt | R3, R5 and R11 at 1280 and 375, `interfaces:better-layout` |
| polish | `interfaces:better-ui`, `emil-design-eng` |

## bolder

**Changes.** One named section rises to the strength the rest of the screen already shows: the display face at full weight, the screen's own structural devices, a change of density or pace that makes the section a peak. Make the one decisive move in full, then quiet what sits around it; when every element gets louder, the section gets flatter.

**Stays.** Everything outside the named target, the section's claims unless the user supplies new ones, and every convention that drives an action.

**Limits.** No new colour, font or token. More effects are the opposite of bolder.

**Check.** With the copy stripped out, the bare structure still says what the section is and why it matters, and the section reads as the same brand.

## quieter

**Changes.** Visual intensity drops while the screen keeps its point of view:

- colour used for state and the primary action, on more neutral ground
- weights down a step (900 to 600, 700 to 500) and more space
- thinner borders or none; decorative gradients, glows, patterns and extra shadows removed
- motion over 10-20px with ease-out curves; decorative motion removed

**Stays.** The hierarchy, with one to three anchors that still stand out and three emphasis levels (R14); colour, which carries the state cues; the affordances of every functional element.

**Limits.** No bounce or elastic easing (S21). No gray text on a coloured ground (R33): use a darker shade of that colour. Lowering the accent saturation (impeccable gives 70-85%) or the scale ratio changes `tokens.json`: name the change and ask, as the principles above say.

**Check.** Tasks complete as before, long text reads more easily, and the screen still has a character of its own.

## distill

**Changes.** Whatever does not serve the screen's one primary goal goes, moves behind a disclosure, or merges with its neighbour:

- one primary action, with the secondary actions cut to those the task uses
- information said once
- borders, shadows and backgrounds that serve no hierarchy or function removed; no card inside a card (S11)
- secondary content in a side panel moves inline or behind a disclosure; the navigation stays
- fewer sizes and weights on the screen, all drawn from the tokens
- shorter copy with the same meaning (`references/ui-copy.md`)
- dead CSS and unused components removed

**Stays.** Every function the user needs, labels and ARIA, the information a decision needs, and the families and type ramp in `tokens.json`.

**Limits.** A complex domain keeps the complexity its task needs. The hand-over lists each removed feature or option with the reason.

**Check.** The primary action is obvious, and every function the screen had is still reachable.

## delight

**Changes.** One moment that earns it, stated first in one sentence: what the user should feel, and why that feeling belongs to this product. Candidates are a meaningful completion, a wait shown with truthful progress, a first-use or empty state that makes the next action clear, and a recovery that leads with the problem and the fix.

**Stays.** The speed and clarity of the primary task.

**Limits.**

- Delight never delays, blocks or hides the task, never fakes progress, and never plays sound without consent.
- Errors about loss, money, privacy or blocked work get no joke.
- Intensity follows frequency: a routine save just feels certain.
- Copy uses the product's own words.
- Motion goes through `emil-design-eng` and the motion tokens, honours reduced motion, and stops when hidden.

**Check.** A neighbouring product could not use the moment unchanged, and the screen stays fast and obvious without it.

## onboard

**Changes.** The shortest path to the first real result:

- real functionality with sample data or a template
- one concept at a time, at the point of use
- empty states that carry the action creating the first item, and a template where one exists
- a tour, when one is needed, of 3-7 steps on the real interface

**Stays.** Access to the whole product: onboarding can be skipped, shows once, and remembers dismissals.

**Limits.** Onboarding lives in a dismissible surface (a tour, a first-run panel, a help page) or nowhere (`references/ban-list.md`). Helper text carries only a format, a limit, a consequence or a legal requirement. A help link names what it opens (C15). Welcome copy, time estimates and explanations stay out of the layout.

**Check.** A new user reaches the first real result without reading anything that stays on the screen afterwards.

## overdrive

**Changes.** One part of the interface does something users do not expect from a web page: a table that scrolls 100k rows smoothly, a dialog that morphs out of its trigger, a search that filters without a flicker.

**Stays.** What the product does; overdrive changes how it feels.

**Limits.**

- Before any code, offer the user 2-3 directions with their browser support, performance cost and complexity, and build only the one picked.
- Every technique degrades to a good static version behind `@supports` or a feature check.
- 60fps on a mid-range device; heavy resources start near the viewport and pause off-screen.
- No sound without opt-in, and one extraordinary moment per screen.

**Check.** Removing the effect makes the screen worse, the fallback still looks right, and a render in Chrome shows the timing and the frames.
