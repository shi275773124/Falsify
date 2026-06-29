# Falsify Homepage Design System

## Color tokens

Warm black:
- `--ink-950: #050504`
- `--ink-900: #0b0a08`
- `--ink-850: #11100d`

Paper:
- `--paper-50: #f4f1ea`
- `--paper-100: #eee8dd`
- `--paper-200: #ded6c8`

Text:
- `--text-on-dark: #f2ede3`
- `--text-on-paper: #15130f`
- `--text-muted-dark: #9a9286`
- `--text-muted-paper: #6e665b`

Rules:
- `--rule-dark: rgba(244, 241, 234, 0.14)`
- `--rule-paper: rgba(20, 18, 15, 0.16)`

States:
- `--critical-red: #d71916`
- `--critical-red-deep: #9f1412`
- `--pass-green: #6f8c68`
- `--debt-amber: #b88a3d`

Red is only for BLOCK, FAILED, raw artifact required, and critical findings.

## Typography

Display:
- Instrument Serif / Georgia
- Large English hero headlines only.

Sans:
- Inter, Apple system fonts, Segoe UI
- Body, navigation, buttons, product content, Chinese mode.

Mono:
- IBM Plex Mono / SFMono / Consolas
- Metadata, artifact labels, report fields, IDs.

Chinese:
- Apple/PingFang style sans stack.
- No mono for Chinese quote or Chinese primary headings.

## Spacing rhythm

Global sections use large, calm vertical spacing:
- Desktop: 92-150px section padding.
- Tablet/mobile: collapsed but still breathing; avoid dense stacked leftovers.

Product objects:
- 8px radius maximum.
- Thin rules.
- Tactile paper surfaces.
- No nested decorative cards.

## Components

Hero workspace:
- Review room shell.
- Claim card.
- Attack path.
- Verdict card.
- Raw artifact card.
- Founder field note.

Product loop:
- Five short steps.
- Should be readable in one scan.
- Mobile becomes compact chips or stacked product steps without hard line clutter.

Use-case tile:
- Title.
- Claim.
- Attack.
- Verdict badge.

Artifact archive:
- Artifact list.
- Selected detail object.
- Download or inspect action.

Verdict states:
- PASS uses muted green.
- PASS_WITH_DEBT uses amber.
- BLOCK uses critical red and strong mono wordmark.

Founder field note:
- Portrait plus source quote.
- Quote uses sans.
- Label and metadata use mono.

## Responsive behavior

Desktop:
- Hero copy and workspace side by side.
- Product workspace is visible in the first viewport.

Mobile:
- Hero copy first.
- CTA full width.
- Product loop chips remain compact.
- Workspace follows without horizontal overflow.
- Language toggle stays visible and polished.
