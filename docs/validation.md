# Slice 0 validation — 2026-11-12

- `python3 scripts/build.py`: passed on Python 3.9.6.
- `python3 -m unittest discover -s tests -v`: all six tests passed.
- `git diff --check`: passed.
- Canonical sibling repository: clean working tree before and after inspection.
- No Bike Library files read, copied or generated. No commit, push or deployment.

Automated checks cover exact output inventory, ignoring unselected input, stale
output removal, byte-identical rebuilds, missing-asset errors before output
replacement, symlink rejection, relative HTML references and anchors, absence of
script/iframe and external CSS/SVG dependencies, identity checksums, and Git
exclusion of generated output and environment files.

## Browser review remains pending

The execution sandbox denied binding the loopback HTTP server with
`PermissionError: [Errno 1] Operation not permitted`. The browser also rejected
`file:` navigation under its URL policy. No visual browser checks were completed;
static checks alone do not establish reflow, font rendering or keyboard behavior.

On the owner's machine, run the README preview command and check each width:

| Viewport width | Visual review |
| --- | --- |
| 320px | Pending |
| 375px | Pending |
| 390px | Pending |
| 768px | Pending |
| 1024px | Pending |
| 1280px | Pending |

At each width confirm no horizontal overflow, intact square symbol and wordmark,
legible typography and sensible stacking. Use Tab to reveal the skip link and
brand focus outline, then activate the skip link to reach main content. Also
check 200% zoom. With browser network disabled and cache disabled, open the
built `dist/index.html` directly and confirm CSS, symbol and favicon load; the
static reference checks find no network-dependent assets.

# Slice 1 validation — 2026-11-12

- Full standard-library suite: all 13 tests passed, including synthetic Standert
  fixtures, escaping, tables, links, date/schema errors, matching, empty states,
  both environment build modes, no source writes, exact output and determinism.
- Actual checkout build: passed; 3 completed and 6 planned-or-undated records.
- Independent generated-text comparison: all 74 source headings, all 238 table
  cells and all 16 nonempty selected maintenance fields found in page text.
- All generated internal links and fragment targets resolve. Exactly the original
  five static files plus `bikes/standert/kreissage_rs/index.html` are emitted.
- Rebuilding actual content produces byte-identical output. No PDF or photograph
  is copied. No absolute workstation paths or environment names occur in HTML.
- `git diff --check`: passed. No commit, push or deployment.

Browser validation remains blocked: the Slice 1 server launch again returned
`PermissionError: [Errno 1] Operation not permitted` at socket binding. The earlier
browser `file:` restriction remains applicable; it was not bypassed. No rendered
viewport, keyboard, network-disabled or visual source-comparison pass is claimed.
The six-width matrix above remains pending for the generated Standert page too.
Check table-region scrolling separately from document overflow, long strings,
Back to Home and section links, focus, identity assets, and both maintenance
sections. Generated output is left in configured Standert mode for owner review.

# Slice 2 validation — 2026-11-12

- All 19 tests pass, including generated JPEG fixtures containing GPS/EXIF,
  thumbnail pointers, XMP and comments, orientation correction and safe manifests.
- Actual approved derivative: 1600 × 901 WebP, 258,026 bytes, container verified
  free of all metadata chunks and independently decoded successfully.
- Derivative inspected visually: whole bike retained; no cropping or distortion.
- Actual-site build repeated with byte-identical output. Original photograph hash
  unchanged. Exactly five original static files, one bike HTML and one WebP emitted.
- All local page/image references and anchors resolve; no source paths or environment
  values in HTML. No other photographs or PDFs in generated output.
- `git diff --check`: passed. No commit, push or deployment.
- Canonical Markdown edit is blocked by workspace permissions; owner patch provided.
- Local server binding again denied. Browser widths 320, 375, 390, 768, 1024 and
  1280px all remain pending, including layout shift, focus and rendered reflow.

# Slice 3 validation — 2026-11-12

- Full suite: all 25 tests passed. Added multi-bike synthetic fixtures cover the
  eight-source registry, index routes, deeper headings, quoted technical notes,
  no-maintenance records, exact maintenance matching and sorting, invalid rows on
  another bike, unknown identifiers, unsafe source paths/symlinks and failure
  preserving previous output. Existing Standert and image-security tests pass.
- Actual configured build: eight detail pages, library index and original Home.
- Independent generated-text check: all 524 headings, 1,915 table cells and 359
  other nonempty source lines accounted for after normalising Markdown and notices.
- Actual output: exactly 15 files. One approved WebP; no other Bike Library binaries.
  Encoded image metadata validation passes; all local HTML/image links and fragment
  targets resolve; HTML contains no absolute source paths or environment names.
- Actual rebuild: byte-identical output. Existing source repositories were not modified.
- `git diff --check`: passed. No commits, pushes, deployment or dependencies added.
- Owner browser acceptance remains pending: local HTTP server binding is denied by
  sandbox (`PermissionError: [Errno 1] Operation not permitted`). No desktop/mobile
  visual, document-overflow, console or focus result is claimed. Exact preview and
  page/viewport review steps are in `docs/multi-bike-audit.md` and README.


## Slice 3 owner acceptance — 16 November 2026

**Status: Accepted.** The owner reviewed the site on desktop and in a narrow
browser window, confirmed both looked satisfactory for this first pass, and
explicitly accepted Slice 3. Native mobile Safari testing remains outstanding
and is deferred without blocking acceptance. This supersedes the pending owner
acceptance status above; the original automated-browser limitations remain valid.
No exact viewport matrix, console check or native-phone pass is claimed.
No code changes, commit, push, deployment or new slice form part of this acceptance.
