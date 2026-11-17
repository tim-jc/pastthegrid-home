# Local release runbook — Slice 5A

Status: **owner-accepted 17 November 2026** following independent Mac checks.
Acceptance does not authorise Slice 5B or live publication.
No live uploader, Cloudflare login, Keychain retrieval or account inspection is present.
All formal A01–A20 outcomes remain **Not run**. See the
[accepted architecture](private-hosting-architecture.md),
[acceptance specification](deployment-acceptance.md) and [roadmap](roadmap.md).

## Prerequisites and trust

Run from Home with Python 3.9+, Git, cwebp/dwebp (tested 1.6.0) and cjpeg (tested
libjpeg-turbo 3.2.0). Existing application builds and preview commands are unchanged.
This workflow adds Python standard-library modules only. It does not need Node or
Wrangler installed to prepare/verify local releases; an installed Node version is
recorded, not used for upload.

Select only owner-reviewed committed Home code: its three build scripts run as a
local subprocess. This is not a sandbox for malicious Git revisions. The release
controller and independent validator are separate trusted tools; their exact source
hashes, hosting controls and deployment pins are recorded in the manifest alongside
the two committed application/canonical inputs. Review/commit this tooling before
future private publication. Git access here is local/read-only; no fetch or credential
operation occurs. Git SHA-1 repositories are supported; other object formats fail clearly.

## Short owner acceptance: entirely synthetic

These commands use only generated fixture repositories. They do not open the real
Bike Library. `/tmp` is suitable **only because these fixtures contain no private data**.
Do not infer encryption from `/tmp`, permissions or Git ignore rules.

```sh
ptg_demo=$(mktemp -d /tmp/ptg-release-accept.XXXXXX)
ptg_home_ref=$(git rev-parse HEAD)
python3 scripts/prepare_release.py fixtures \
  --home-repo . --home-ref "$ptg_home_ref" --directory "$ptg_demo/fixtures"
ptg_bike_repo="$ptg_demo/fixtures/canonical"
ptg_bike_ref=$(git -C "$ptg_bike_repo" rev-parse HEAD)
ptg_release_a=$(python3 scripts/prepare_release.py prepare \
  --home-repo . --home-ref "$ptg_home_ref" \
  --bike-repo "$ptg_bike_repo" --bike-ref "$ptg_bike_ref" \
  --storage "$ptg_demo/releases" --synthetic-version A)
ptg_release_b=$(python3 scripts/prepare_release.py prepare \
  --home-repo . --home-ref "$ptg_home_ref" \
  --bike-repo "$ptg_bike_repo" --bike-ref "$ptg_bike_ref" \
  --storage "$ptg_demo/releases" --synthetic-version B)
python3 scripts/prepare_release.py verify "$ptg_release_a"
python3 scripts/prepare_release.py verify "$ptg_release_b"
python3 -m json.tool "$ptg_release_a/manifest.json"
tar -tf "$ptg_release_a/publication.tar"
```

`verify` independently recomputes the exact inventory, media/content rules, file hashes,
links, WebP decoding/metadata, control-file bytes, manifest checksum and every archive
member/hash. Expect 17 files, `prepared-not-deployed`, full source Git IDs, unique
`SYNTHETIC-A-*` or `SYNTHETIC-B-*` markers and deployment tests `Not run`. The source
route/asset path identifiers necessarily match the application paths; **rendered fixture
text, titles, CSS, SVGs, photo pixels, notes and CSV contain no real bike/owner data**.
No private source repository is copied or read. A and B share neutral photo pixels but
have distinct HTML/CSS/SVG markers and known per-file hashes. The manifest lists slash
redirect, direct-index normalisation and unknown-path test cases. No `_redirects` file
is added: actual Pages normalisation behavior is for Slice 5B to test, not simulate as fact.

Reject an unexpected file on a disposable copy:

```sh
cp -R "$ptg_release_a" "$ptg_demo/rejected"
chmod u+w "$ptg_demo/rejected/publication"
printf '%s\n' 'unexpected synthetic file' > "$ptg_demo/rejected/publication/extra.pdf"
chmod -R go-rwx "$ptg_demo/rejected"
find "$ptg_demo/rejected/publication" -type f -exec chmod 400 {} +
find "$ptg_demo/rejected/publication" -type d -exec chmod 500 {} +
python3 scripts/prepare_release.py verify "$ptg_demo/rejected"
```

The commands restore restrictive permissions and the frozen publication modes before
verification, so the inventory test is independent of permission rejection. Expect
`Publication inventory does not match approved policy`; never continue to publication.
Then demonstrate mutation detection on a separate disposable copy:

```sh
cp -R "$ptg_release_a" "$ptg_demo/mutated"
chmod u+w "$ptg_demo/mutated/publication/assets/css/home.css"
printf '\n/* deliberate fixture mutation */\n' >> "$ptg_demo/mutated/publication/assets/css/home.css"
chmod -R go-rwx "$ptg_demo/mutated"
find "$ptg_demo/mutated/publication" -type f -exec chmod 400 {} +
find "$ptg_demo/mutated/publication" -type d -exec chmod 500 {} +
python3 scripts/prepare_release.py verify "$ptg_demo/mutated"
```

Permissions are again restored before verification. Expect
`Publication bytes differ from frozen manifest`, even though the CSS remains valid.
Test unsafe permissions separately; do not mistake that earlier guard for an inventory
or content-mutation result. The owner independently observed all three guards.
Verify retained originals and restore exact archived output without rebuilding:

```sh
python3 scripts/prepare_release.py verify "$ptg_release_a"
python3 scripts/prepare_release.py restore "$ptg_release_a" --target "$ptg_demo/restored"
python3 scripts/prepare_release.py verify "$ptg_release_b"
python3 scripts/prepare_release.py preflight "$ptg_release_a" \
  --account aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --project synthetic-example \
  --hostname home.pastthegrid.uk
```

The last command **must fail**: the CLI cannot assert live Access evidence or owner
publication authorisation. It invokes neither Wrangler nor a network adapter. The
account/project strings above are dummy destination inputs, not account discovery.
The API-only dry-run interface can exercise validation flags in tests, but always
reports zero upload invocations and has no upload callback or live adapter.

Review these seven demonstrations: prepare, inspect manifest/inventory, independent
validation, extra-file rejection, mutation rejection, archive verification/restore,
and zero live publication. No browser/security acceptance is implied. Cleanup is manual
and limited to the newly generated synthetic demo directory; no automatic archive deletion.

## Private release preparation interface (not exercised or authorised here)

Future Slice 6 operator syntax, after separate approval and successful Slice 5B:

```sh
python3 scripts/prepare_release.py prepare \
  --home-repo /path/to/home --home-ref FULL_HOME_COMMIT \
  --bike-repo /path/to/bike-library --bike-ref FULL_BIKE_COMMIT \
  --storage /path/on/encrypted-volume/releases --confirm-encrypted-storage
```

These paths are placeholders. No real production source revision is selected in 5A.
The controller resolves both full commits before exporting explicit required blobs;
Git branches/refs may be supplied explicitly but their resolved full IDs become the
manifest inputs. No source Git checkout is reset/stashed/cleaned. Dirty everyday
worktrees are ignored: only selected committed blobs enter isolated exports.

Missing revisions/configuration/files, symlink/gitlink inputs, Git LFS pointers,
unmaterialised JPEGs, invalid CSV/Markdown or ordinary placeholder builds fail closed.
Only required source blobs are exported; no recursive submodules/LFS downloads.
Hashes of every canonical input and selected Home build/config/source file are checked
before/after processing. Temp exports are removed on success/failure; a prior release
is never deleted or overwritten. Release IDs are unique; timestamps/IDs intentionally
differ on each preparation, while identical source/toolchain/version yields identical
publication bytes and deterministic tar archives.

## Storage, permissions and encryption

**Private mode requires an owner-attested encrypted volume**: for example a mounted
crypted APFS volume/encrypted disk image or verified FileVault-protected local storage,
not an unencrypted external drive, synced public folder or general `/tmp`. Verify
those arrangements independently before asserting `--confirm-encrypted-storage`.
The software checks ownership and 0700 storage permissions, not whether a disk is encrypted.
That flag is an attestation, not a technical encryption check. Synthetic mode can use
ordinary owner-only storage and records `synthetic-only-no-private-data` explicitly.

All preparation uses umask 077 and private temporary storage under the release store;
the image processor's temporary raw original/pixels stay there. Source files are
read-only; publication directories/files are frozen 0500/0400. A same-user process
can undo those modes; hashes catch accidental mutation but this is not protection
against an attacker who can replace both manifest and its checksum. Retain an external
trusted manifest hash (later in the private receipt/history) for that threat. Metadata
and tar are read-only, outside the uploadable tree. No credentials are stored anywhere.

`publication.tar` is a deterministic **plaintext tar format inside encrypted storage**,
not a separately password-encrypted portable file. Current/previous local artefacts are
encrypted at rest by that required volume. Do not copy the tar/stage elsewhere unencrypted.
Restore only to a new owner-only target on the same trusted encrypted storage for private
releases. Storage/restore checks cannot prove encryption or prevent a privileged user
reading data. No secure-erasure guarantee is made for SSDs or provider backups.

## Layout and manifest identity

```text
<release-id>/
  publication/          # only this frozen tree could be uploaded later
  publication.tar       # exact rollback bytes; never uploaded as an asset
  manifest.json         # immutable preparation record
  manifest.sha256       # checksum of manifest; retain trusted hash independently
  metadata/
    bikes.json          # selected policy, hashed against committed config
    assets.json         # selected asset allowlist, also hashed
```

Manifest schema 1 contains release ID, UTC preparation time, mode/fixture version,
`prepared-not-deployed`, both full Git IDs, selected input/config hashes, controller
hashes, observed build versions and selected deployment pins/unverified-install flags,
relative file paths/sizes/media types/SHA-256s, local validation results, archive checksum,
synthetic URL cases and storage attestation. No absolute local paths, content bodies,
credentials or unnecessary personal data. File hash inventory is the exact payload
identity; manifest hash identifies the complete preparation record. Receipt events refer
to this hash without rewriting the immutable manifest.

## Independent safety boundary and hosting controls

The validator does not import the builder or its file list. It derives expected output
from its own reviewed static list, selected bike registry, strictly approved Standert
asset entry and two exact reviewed hosting files: `release/headers.txt` → `_headers`,
`release/404.html` → `404.html`. It rejects extra/missing files, symlinks, hardlinks,
special files, empty/unexpected directories, stale output, PDFs/JPEGs/Markdown/CSV,
unknown controls/Workers/redirects, broken links, scripts/forms/active attributes,
external runtime resource links, remote CSS/SVG resources, duplicate anchors, common
local-path/credential signatures and mutated declared bytes. MIME/content checks and
actual WebP structure plus independent `dwebp` decoding supplement suffix checks.
Secret-signature scanning is finite, not universal DLP: owner review remains necessary
for intentionally private source text (including technical pairing notes).

Release-only controls detach default cache/referrer headers, request private no-store,
no-referrer, nosniff, no framing, remove permissive ACAO and apply a CSP with no scripts,
external content, forms or inline styles. The non-sensitive 404 avoids the default
SPA fallback design. Exact contents are enforced; **effective Cloudflare headers,
Access behavior, redirects, CDN caches and 404 responses remain unverified until 5B**.
These controls are not authentication. Development `dist/` remains unchanged (15 files).

## Deployment tooling status

Exact selected pins are in `tooling/deployment/package.json`, `.node-version` and
`pins.json`: Node **24.22.3**, Wrangler **4.164.0**. Sources consulted 17 November 2026:
[Node release](https://nodejs.org/en/blog/release/v24.22.3),
[Wrangler package](https://www.npmjs.com/package/wrangler?activeTab=readme), and
[Cloudflare installation guidance](https://developers.cloudflare.com/workers/wrangler/install-and-update/).
The Node release is LTS; Wrangler documents Current/Active/Maintenance Node support.

Observed local Node is 26.13.1, not the selected pin. npm registry resolution failed
with ENOTFOUND. Neither the exact Node nor Wrangler installation, engine compatibility
on this Mac, nor a resolved transitive lockfile is verified. No dependencies were installed.
Pins therefore remain `installation_verified: false`, `dependency_lock_verified: false`
and `live_upload_enabled: false`. Exact version selection is provided; full reproducible
npm dependency resolution remains a disclosed blocker to tooling readiness for 5B.

In a subsequent authorised tooling session, select/verify the pinned Node using an
owner-approved version manager or signed official download, generate and review the
lockfile under `tooling/deployment`, then use `npm ci` and the local binary. Never use
unpinned `npx latest`. No install/deploy npm scripts or functional live upload command
exist here. Future upload must consume a freshly verified stage, an externally trusted
manifest hash, named account/project/hostname, concrete owner authorisation and current
independent Access evidence. Slice 5A provides only local preflight and test doubles.

## Receipts, retention and rollback

Preparation never means deployed or production-known-good. `receipt` imports a separate
strict-schema evidence record into an owner-only ledger; it performs no network access
and changes neither archive nor manifest. `simulation` is separate from
`owner-attested-live`. A live-kind record is a future operator attestation of external
verification, not verification this local parser can perform. No live receipt is imported
in 5A. IDs and evidence hashes are retained without response bodies or tokens.

Receipt fields: `schema:1`, `kind`, `deployment_id`, `account`, `project`,
`hostname:home.pastthegrid.uk`, timezone-aware `verified_at`, `outcome:verified|failed`,
and `evidence_sha256` (hash of separately retained private verification evidence).

```sh
python3 scripts/prepare_release.py receipt "$ptg_release_a" \
  --file /path/to/simulation-receipt.json --ledger "$ptg_demo/ledger"
python3 scripts/prepare_release.py retention --ledger "$ptg_demo/ledger" \
  --account aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --project synthetic-example --kind simulation
```

The non-destructive retention plan identifies current/previous **distinct verified**
releases per destination and kind, and lists older superseded candidates. Failed receipts
do not promote a release. Simulation receipts never promote production pointers. Nothing
is deleted automatically. Retain current and previous known-good production deployments
and encrypted local artefacts until superseded. Only after new release verification and
checking both retained archive hashes should the owner separately authorise removing
older artefacts/hosted history; retain lightweight receipts with revisions, IDs, manifest
hashes and verification outcomes. `restore` reads the exact validated tar members into a
new frozen stage; no new canonical data/build is used. Any incompatible later safety
policy requires an explicit review of an older release rather than silently weakening checks.

## Verification scope and next steps

Tests map local portions of A14–A16 to `tests/test_publication.py`:

| Criterion | Implemented local evidence |
| --- | --- |
| A14 | Exact 17-file inventory, metadata-free derivative checks, MIME/content policy, controls, links, declared hashes, symlink/FIFO/source/PDF/stale/active-content rejection, archive validation |
| A15 | Synthetic committed input exports, full IDs, input hashes, dirty everyday worktree isolation, invalid/missing/LFS/config/source-record failures, unchanged fixture repositories |
| A16 | Failed preflight and mutated/extra publication tests stop before test-double invocation; no live adapter exists; fallback placeholder rejected |

None of A14–A16, or any other A01–A20 criterion, is fully passed by this slice.
Native device login, response headers, all host/cache routes, month-long sessions,
revocation, real updates/rollback/withdrawal and credential handling remain 5B work.
Slice 5A is owner-accepted. Before 5B: reconcile/close its Git baseline,
resolve/review deployment tool installation/lockfile and explicitly authorise synthetic
infrastructure work. No real private release is prepared or published here.


## Accepted evidence and carry-forward — 17 November 2026

The owner independently reported FileVault enabled, all 38 tests passing in 7.295s,
A/B preparation and inventory inspection, independent verification, permission/inventory/
mutation rejection, exact archive restore, intact originals, and fail-closed preflight.
These are **owner-observed**, not newly repeated by the assistant. Exact archive hashes
and observed messages are recorded in the [Slice 5A report](slice-5a-report.md).
All formal A01–A20 remain Not run; no live security conclusion follows.

Carry forward before the relevant future operations:

- Install/verify the pinned Node/Wrangler toolchain and reviewed dependency lock.
- Review actual bike model names in synthetic URL paths before any live publication.
- Retain trusted manifest checksums externally, independently of their release directories.
- Proposed permanent store: `~/.local/share/pastthegrid-home/releases/`; confirm it is
  non-synchronised and on FileVault-protected storage before using private artefacts.
  FileVault being enabled alone does not establish those properties for every location.
- Simplify the owner-facing publication command as a Slice 6 usability objective.

No carry-forward item authorises beginning Slice 5B, installing tooling, retrieving
credentials or publishing content during acceptance/Git closure.
