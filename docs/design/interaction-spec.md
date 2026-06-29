# Falsify Homepage Interaction Spec

## Navigation

The top navigation is quiet and supportive. It should not feel like a docs site.

Links:
- Loop
- Stack
- Use cases
- Case
- Archive
- Reality
- Docs
- GitHub

Mobile:
- Menu button opens the link panel.
- Language toggle remains visible.
- No horizontal overflow.

## Language toggle

Requirements:
- Keyboard reachable.
- `aria-pressed` updates.
- `document.documentElement.lang` updates to `en` or `zh-CN`.
- All visible homepage copy switches through the content map.
- Founder quote remains the original source quote.

## Reveal motion

Use subtle reveal only:
- Product loop steps.
- Stack steps.
- Use-case tiles.
- Sharpe proof columns.
- Artifact archive.

No scroll-jacking. No flashy red animation. Respect `prefers-reduced-motion`.

## Product object behavior

Hero workspace:
- Objects feel alive through hierarchy, spacing, and state contrast.
- No fake app controls that imply unavailable features.

Artifact archive:
- Rows can be static for now, but must visually imply an inspectable archive.
- Selected artifact detail should be readable without opening a modal.

Sample review:
- Existing local review interaction remains.
- If live provider setup is missing, show a clear setup fallback and allow sample review.

## Visual QA checklist

Inspect:
- Desktop EN
- Desktop Chinese
- Mobile EN
- Mobile Chinese
- Hero first viewport
- Product loop
- Use cases
- Sharpe 4 case
- Raw artifact archive

Pass criteria:
- No horizontal overflow.
- No text clipped by container.
- BLOCK is strong but not the only meaningful object.
- Product loop and use cases are visible and practical.
- Raw artifact archive feels inspectable.
- Founder portrait and quote are preserved.
- Page feels like a coherent product world.
