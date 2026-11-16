# Standert source contract — Slice 1

## Files inspected and read

- `bikes/standert/kreissage_rs.md`: canonical bike identifier and record.
- `workshop/maintenance_log.csv`: maintenance source.

Only these two files are read from Bike Library. No linked records, inventory,
repaint checklists, fit records, photographs, PDFs or repository metadata are
loaded. No changes or source-format requirements are imposed on Bike Library.

The Markdown begins with `# Standert Kreissäge RS`, followed by Summary and
Documents, then level-one sections Frameset, Drivetrain, Wheels, Cockpit, Setup,
Maintenance, Inventory and Workshop Notes. It contains level-two component groups
and level-three specifications, documentation, evidence and notes. Tables have
pipe-delimited cells and optional alignment markers. Lists include bold labels,
unchecked tasks and indented continuation text. Internal fragment links refer to
Groupset, Wheelset, Headset and Bottom Bracket. `> TODO` in table cells is literal
cell text, not a block quote.

## Rendering

A small standard-library parser in `scripts/bike_library.py` supports precisely
headings (levels 1–3), paragraphs, flat lists with continuation lines, textual
checklist status, tables, horizontal rules, links, emphasis and code spans.
Unsupported blocks, malformed inline syntax and malformed tables fail the build.
Raw HTML is escaped. The page has one h1; subsequent source level-one sections
become h2, with their children shifted together. Introductory Summary and
Documents retain their original nesting. Duplicate headings get deterministic,
unique anchor suffixes. Table wrappers scroll independently and accept keyboard
focus. The section navigation follows the source's major sections.

All source content remains in order, including TODOs, document labels, evidence
labels and inventory labels. Checklists are text, not editable inputs. No inline
TODO is converted to a maintenance event. Local links are rendered as plain labels
with “reference not included”; external HTTP(S) references can remain links with
escaped destinations. Credential-bearing links and common local-host/private-IP
URLs are suppressed. Unresolved anchors are also suppressed with build warnings.
No URL validation can establish future external availability; there are no external
links in the current Standert source. No new dependency is required.

The build reads and renders content before replacing the previous output. Its
explicit static-file allowlist gains exactly one HTML file when configured.
No source paths, environment values, timestamps or git metadata are rendered.
The final URL is `bikes/standert/kreissage_rs/`, derived from the canonical path.

## Maintenance

CSV schema: `work_date,bike,work_done,notes`. Existing bike keys include `standert`,
`bokeh`, `mercian`, `big bro`, `surly` and `burls`. Exact `standert` matching is
intentional; Standert-like variants fail as ambiguous rather than being guessed.
Malformed rows or schema fail. Standert dates must be valid `YYYY-MM-DD` values;
empty dates go into the separate planned-or-undated section. Whitespace-only or
invalid dates fail. Completed rows sort descending by date, preserving CSV order
for ties. Undated rows retain CSV order. Descriptions and notes retain their words
and punctuation; source text is HTML-escaped.

Observed at implementation: **3 completed**, dated 2026-11-06, 2026-11-01 and
2026-06-30; **6 planned or undated**. No status was inferred from descriptions.
The record's “In service” status is preserved even though the maintenance log
records a strip-down; Home does not reconcile or override source statements.

## Privacy and exclusions

Current source includes 35 local references: PDFs, photographs, bike-fit Markdown,
maintenance CSV and inventory CSVs. All are labelled but unlinked; none are copied.
All needed source constructs are supported; there are no silently omitted blocks.
Serial numbers and the frame number are source content and appear in the private
text view. Source text containing common absolute local-path forms fails review
rather than leaking a workstation path. Hosting must enforce access across the
entire site before any publication; no authentication or publication is added.

Suggested Slice 2: owner review of this text browser and its source discrepancies,
then an explicitly selected, re-encoded and EXIF-stripped Standert photograph,
with provenance and privacy tests. Documents and other bikes remain separate work.
