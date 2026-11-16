# Identity asset provenance

Canonical source: `../pastthegrid-site`, commit
`0fa1228c7b9806e591335e6ea2719dc428ebc323` (clean working tree at inspection).
Copied unchanged on 2026-11-12. No runtime or build dependency on the source repo.
The source's `docs/visual-identity.md` defines portable copying as the adoption
convention; this manifest adds per-file integrity checks for Home.

| Source path | Home path | SHA-256 |
| --- | --- | --- |
| `assets/identity.css` | `src/assets/identity/identity.css` | `90ab7e542d2acebe40ca3ab4fa7196dade6453b2f3ca8e17b77947a5dc176605` |
| `assets/symbol.svg` | `src/assets/identity/symbol.svg` | `7973aea5fa3078d68da03b6229aa6af455e65d6ada9ba00fdeff6bacf932b33a` |
| `assets/favicon.svg` | `src/assets/identity/favicon.svg` | `ea7d44363ecb1b174b9537aa2cc0e1d5ed962cfbd81d1612824ce643ed31d292` |

## Adoption choices

Use the Field Notebook paper surface and canonical semantic tokens unchanged:
paper `#F1EFE7`, midnight `#172630`, muted `#52635C`, accent `#9B582E`,
surface `#E7E9DF`, line `#C8CDC2`, focus `#854822`. Base sage, copper and survey
blue remain available in the copied stylesheet; the dark theme is also retained.

The 40-unit route symbol is displayed square, alongside the live HTML wordmark
(weight 600, tight tracking, copper full stop). This follows the canonical
accessible lockup rather than copying the SVG wordmark. The favicon retains its
original geometry. No hero illustration, dark symbol or unused wordmark SVG is copied.

Typography uses installed Avenir Next / Avenir / Segoe UI / sans-serif and
SFMono-Regular / Consolas / Liberation Mono / monospace; no font files or network
requests. Home retains square surfaces, hairline rules, the 4px spacing family,
24px mobile gutters, wrapping headers, stacked mobile content and visible focus.
Application layout lives separately in `src/assets/css/home.css`. Home disables
the foundation's smooth scrolling; it introduces no motion.
