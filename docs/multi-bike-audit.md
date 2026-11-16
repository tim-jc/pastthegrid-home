# Slice 3 — source audit and implementation

Audit date: 2026-11-12. All source inspection is read-only.

## Inventory, status, mappings and generated routes

Bike identifiers remain the canonical Markdown paths. Every path below is relative
to Bike Library; each route has a generated `index.html` beneath it.

| Source under `bikes/` | Canonical title | Explicit status | CSV key | Completed | Undated | Route |
| --- | --- | --- | --- | ---: | ---: | --- |
| `brother/big_bro.md` | Brother Big Bro | In service | `big bro` | 1 | 1 | `/bikes/brother/big_bro/` |
| `burls/burls_v2.md` | Burls V2 | In service | `burls` | 2 | 0 | `/bikes/burls/burls_v2/` |
| `dolan/seta.md` | Dolan Seta | `> TODO` | None assigned | 0 | 0 | `/bikes/dolan/seta/` |
| `mason/bokeh.md` | Mason Bokeh | In service | `bokeh` | 6 | 1 | `/bikes/mason/bokeh/` |
| `mercian/super_vigorelli.md` | Mercian Super Vigorelli | In service | `mercian` | 1 | 0 | `/bikes/mercian/super_vigorelli/` |
| `nukeproof/cub_scout_14.md` | Nukeproof Cub Scout 14" | Not recorded | None assigned | 0 | 0 | `/bikes/nukeproof/cub_scout_14/` |
| `standert/kreissage_rs.md` | Standert Kreissäge RS | In service | `standert` | 3 | 6 | `/bikes/standert/kreissage_rs/` |
| `surly/bridge_club.md` | Surly Bridge Club | In service | `surly` | 1 | 0 | `/bikes/surly/bridge_club/` |

All six CSV identifiers have a single corresponding record. These associations
follow the model/manufacturer names in the audited records and the work descriptions;
there is no competing candidate for any identifier. Dolan and Nukeproof have no
observed CSV identifiers, so their registry values are null rather than invented
keys. Future unknown or differently spelt CSV identifiers fail the build for review.
No record explicitly says historical/retired. Status is never derived from dates,
maintenance absence or TODO content.

Two further Markdown files are supporting project documents, not bike records:
`bikes/standert/repaint/README.md` and `bikes/standert/repaint/build-sheet.md`.
They were inspected for classification but are not build inputs or generated pages.
They contain project decisions, planning and procurement tasks, not CSV maintenance.
The README also uses underscore emphasis and a nonstandard `-[Mockup]` list line;
these are not needed by the supported bike renderer and have not been added.

## Actual structural differences

All eight primary records start with one canonical title and Summary, followed by
multiple level-one component sections with lower-level specification headings.
They contain flat lists, paragraphs, pipe tables, links and horizontal separators.
The accepted Standert checklist and continuation-line support remain.

- Brother includes separate Brakes, child handlebars/saddle, quoted TODOs and
  external FreeSpoke links with verification notes.
- Burls has two wheelsets, repeated headings and quoted incomplete specifications.
- Dolan is largely an explicit TODO scaffold. Its unknown fields remain unknown.
- Mason has two wheelsets, fourth-level `ENVE M525` under Rims, quoted invoice
  discrepancy notes and a technical pairing-code note. No value is reproduced here.
- Mercian has fixed-wheel-specific drivetrain/brake sections, detailed spoke lengths
  and a different set of torque/consumable tables.
- Nukeproof lacks Status, Strava ID and source Maintenance/Inventory/Workshop Notes
  sections. It has manufacturer references, child fit guidance and a four-column
  wheel table. Generic CSV empty states are appended without inventing source sections.
- Standert retains its photo, extensive bottom-bracket checklist and technical notes.
- Surly has a three-column geometry table, accessories sections and many quoted TODOs.

Added renderer support is limited to flat quoted paragraphs with existing inline
formatting and headings through level five (mapped at most to HTML h6). Nested
quotes/lists, fenced code and ordered lists still fail clearly. No supported source
block is omitted. Repeated headings receive stable numeric suffixes; generated
landmark and maintenance anchors are reserved to prevent collisions.

## Design and boundaries

`config/bikes.json` is an explicit supported-source registry with verified CSV keys,
not a second record store. Titles, descriptors and statuses are read from source on
every build. All eight registered files are required; missing files fail before
replacing output. New bikes require an explicit registry/mapping review. Discovery
iterates this registry, not arbitrary recursive Markdown or asset directories.

The same renderer serves all bikes, with no per-bike templates. Standert alone gets
the existing approved hero. CSV is read and validated once for the build, then rows
are associated by exact keys. All malformed rows, unknown keys, invalid nonempty
dates and empty work descriptions fail. Dates sort descending, ties preserve source
order, and undated rows preserve source order. No checklist or project task is merged.

Home links to `/bikes/`, a restrained text index. Each detail header returns to that
index, while the brand returns Home. The existing stable detail URLs and Standert
layout, tables, maintenance and photograph are retained. Index descriptors use only
Summary status/material/size/year fields; missing status is explicitly labelled.

All local reference destinations remain suppressed except the approved Standert
image reference mapped to its displayed figure. This slice introduces no clickable
local-document links or automatic Markdown-to-page linking. Ordinary external source
references remain normal links, never runtime resource requests.

## Content and asset checks

Independent actual-source/generated-text comparisons checked 524 headings, 1,915
individual table cells and 359 other nonempty source lines, normalising Markdown
formatting and display-only exclusion notices. All matched. Every local reference
label remains visible. Local reference counts by record: Brother 8, Burls 20,
Dolan 5, Mason 24, Mercian 9, Nukeproof 1, Standert 36, Surly 5. Standert's count
includes its now-present canonical approved photograph link; all other destinations
are unlinked. References include PDF manuals/invoices, JPEG/PNG evidence, fit Markdown,
CSV inventory/maintenance and wheelbuilding diagrams. None is followed or copied.

The existing image manifest and processing code are unchanged. Its traversal,
symlink containment, format checks, pixel re-encoding, orientation and actual WebP
metadata-container checks remain covered. Exactly 15 output files exist: five
original static files, Home (included among those five), the bike index, eight bike
pages and the single approved WebP. No source originals, PDFs or other binaries
are present. Relative links and all fragment targets resolve; no absolute local
paths or environment names are present in generated HTML. Repeated real builds
are byte-identical.

These generated records contain private technical identifiers and source notes,
including a pairing-code note. Keep output local and private. No source values
were redacted or rewritten and no hosting security is claimed.

## Files changed for Slice 3

- Added `config/bikes.json` — supported source paths and verified CSV associations.
- Updated `scripts/bike_library.py` — registry, generic reader/parser/rendering/index.
- Updated `scripts/build.py` — shared source/CSV orchestration and multi-page output.
- Updated `src/assets/css/home.css` — text index, quoted notes and deeper headings.
- Updated `tests/test_bike_library.py` — multi-bike fixtures and output inventory.
- Added `tests/test_multi_bike.py` — structure, association, path and failure tests.
- Updated `README.md`, `docs/validation.md` and added this audit document.

No new dependencies, source repository changes, commits, pushes or deployment.

## Remaining owner acceptance

Browser automation could not run: server binding is denied by the execution sandbox.
No rendered mobile/desktop overflow, console, focus or layout pass is claimed.

```sh
BIKE_LIBRARY_ROOT="$HOME/Documents/Cycling/bike-library" python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open `http://127.0.0.1:8000/bikes/`. Review Standert, Mason (deeper headings and two
wheelsets), Brother (quoted notes and child components), and Nukeproof (no maintenance).
At 320, 375, 390, 768, 1024 and 1280px confirm no document overflow, table scrolling,
photo sizing, return links, focus and correct maintenance grouping. Check browser
console for errors and network requests for local identity/image assets only.


## Slice 3 owner acceptance — 16 November 2026

**Status: Accepted.** The owner reviewed the site on desktop and in a narrow
browser window, confirmed both looked satisfactory for this first pass, and
explicitly accepted Slice 3. Native mobile Safari testing remains outstanding
and is deferred without blocking acceptance. This supersedes the pending owner
acceptance status above; the original automated-browser limitations remain valid.
No exact viewport matrix, console check or native-phone pass is claimed.
No code changes, commit, push, deployment or new slice form part of this acceptance.
