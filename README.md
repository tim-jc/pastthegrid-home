# Past the Grid Home

A locally generated, read-only portal for personal cycling information. Configured
builds provide eight Bike Library records and one explicitly approved Standert
photograph. Bike Library remains the canonical source; Home stores no second copy
of its records. Nothing is deployed or published by this project.

## Build and preview

Python 3.9+ is required. Configured content builds also need installed libwebp
`cwebp` and `dwebp` on PATH (validated with 1.6.0). There are no Python packages or
runtime network dependencies. Tests additionally use `cjpeg` for synthetic fixtures.

```sh
BIKE_LIBRARY_ROOT="$HOME/Documents/Cycling/bike-library" python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8000/bikes/ or start at http://127.0.0.1:8000 and follow
Bike Library. Stop preview with Ctrl-C. Loopback binding keeps it on this computer.
Every detail page returns to the library; its brand returns Home.

Without source configuration the accepted Slice 0 placeholder remains available:

```sh
python3 scripts/build.py
```

Ensure `BIKE_LIBRARY_ROOT` is unset for that command. This removes any previous
configured output, including the bike pages and derivative photo. Explicitly empty,
invalid or missing configured roots fail rather than falling back silently.

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

## Layout and source contract

- `src/index.html`: placeholder page and shared page shell.
- `src/assets/css/home.css`: Home layout and technical record styles.
- `src/assets/identity/`: copied canonical identity assets.
- `config/bikes.json`: eight exact Markdown paths and verified maintenance CSV keys.
- `config/assets.json`: the single approved image publication entry.
- `scripts/build.py`: explicit static-file and generated-page orchestration.
- `scripts/bike_library.py`: source reader, narrow Markdown renderer and index.
- `scripts/image_assets.py`: fresh image encoding and metadata validation.
- `tests/`: isolated synthetic source/image fixtures and standard-library tests.
- `docs/`: provenance, source audits and validation results.
- `dist/`: generated output, ignored by Git; never edit it directly.

All eight registered Markdown files and `workshop/maintenance_log.csv` are required
when configured. Titles and Summary descriptors are read from source each build.
Exact CSV keys associate maintenance; unknown keys, malformed rows or invalid dates
fail for review. Dated entries sort newest first; undated work stays separate. No
maintenance is inferred from Markdown checklists, status or project documents.
New bikes require an explicit registry/mapping review. There is no recursive content
or asset publishing. Absolute/traversal paths and source symlink escapes fail.

The identity comes from sibling `pastthegrid-site`, with copied assets and recorded
provenance in `docs/asset-provenance.md`. There is no build/runtime dependency on it.

## Photographs and privacy

Only `photos/standert/standert.jpg` is approved. It is freshly decoded, oriented,
resized and encoded as `assets/bikes/standert/hero.webp`. The actual encoded output
is checked for metadata and decoded again. Original files are never modified.
See `docs/standert-photo.md` for settings and provenance. Replace the canonical
image and rerun the build to regenerate; codec-version changes can change bytes.

The canonical Standert Markdown now contains the approved photo reference. Only
that exact image reference maps to its displayed figure. Other local image, PDF,
fit and inventory reference labels remain visible without clickable destinations.
No other binaries are copied. No galleries, editing, telemetry or remote resources.

Source records can contain frame/component identifiers and technical pairing notes.
Treat all generated output as private even though Git ignores it. Environment files
are ignored; never add credentials or private originals to the Home repository.

The intended future address is `home.pastthegrid.uk`. Hosting-boundary authentication
must cover all HTML and asset URLs before publication, using a separate deployment
slice. Client-side JavaScript and robots directives do not provide access control.
There is no Cloudflare, DNS, hosting or deployment configuration here.

## Acceptance status

Slice 3 — Multi-bike Bike Library browser — **Accepted by the owner on
16 November 2026** following desktop and narrow-browser-window review.
Native mobile Safari testing remains outstanding and was deferred without blocking
acceptance. No precise viewport-width or browser-console pass is claimed.

`docs/multi-bike-audit.md` records sources, routes, maintenance mappings, structural
differences and content checks. `docs/validation.md` records automated results,
browser limitations and owner acceptance. Acceptance does not authorise publication
or deployment. Subsequent proposed architecture work is described below.

## Accepted private hosting architecture — Slice 4

The owner accepted Slice 4 on **17 November 2026**. The
[architecture](docs/private-hosting-architecture.md) selects Cloudflare Pages Direct
Upload in the existing account, owner-triggered local Mac builds, and exact-owner-email
one-time PIN across every serving hostname/path/asset. Adoption remains conditional on
successful synthetic security acceptance; nothing is configured or published.

The intended browser experience is approximately 30 days, using supported one-month
application/global sessions and policy Same as application, with actual precedence,
renewal and Safari behavior still to verify. The owner accepts mailbox-possession
assurance and the uploader token's account-level residual risk, including potential
impact on the public site. A dedicated time-limited minimum-permission token must be
stored in macOS Keychain and retrieved only for explicitly authorised publication;
administrator credentials remain separate. No credential values enter logs or artefacts.

Every private release must use selected committed Home and Bike Library revisions in
isolated clean inputs, with both full Git IDs in its manifest. Everyday worktree edits
neither enter nor block that release and must not be modified, stashed or cleaned.
The first production revisions are deferred until first private publication.
Retain current/previous known-good production deployments and their encrypted local
artefacts until superseded, plus lightweight release history; no arbitrary archive expiry.

All twenty [deployment acceptance tests](docs/deployment-acceptance.md) remain **Not run**.
The [roadmap](docs/roadmap.md) separates Slice 5A local safeguards, Slice 5B live
synthetic proof and Slice 6 first private publication. Each needs its own authorisation;
this acceptance/Git closure does not begin Slice 5A or permit publication.


## Local publication safeguards — Slice 5A

A separate standard-library release workflow is implemented and **owner-accepted
on 17 November 2026** following independent Mac checks. It does not change ordinary builds or enable live uploading. Follow the
[release runbook](docs/release-runbook.md) to generate synthetic A/B fixtures, export
explicit committed inputs, prepare a frozen 17-file stage, independently validate its
manifest/archive, and demonstrate rejection of extra files and mutated bytes.

Private-mode archives/staging require operator-confirmed encrypted local storage;
permissions and ignored directories are not encryption. Only generated synthetic
fixtures were exercised in this slice. Exact Node/Wrangler pins are recorded separately;
installation/transitive lock verification is blocked by npm DNS and remains unverified.
All formal deployment tests remain Not run; Slice 5B needs separate authorisation.
