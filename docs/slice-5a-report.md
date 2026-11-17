# Slice 5A completion report

17 November 2026. **Owner-accepted following independent Mac acceptance checks.**
Git closure is reported separately after execution; acceptance does not authorise 5B.

## Baseline and scope

Started on clean `main` at accepted Slice 4 commit
`b1452ecc768187a0dbf45fac825d7b0575b4a1aa`, matching cached `origin/main`.
Fresh GitHub verification again failed with DNS resolution. No material baseline
conflict was found; 5A was the next accepted roadmap milestone. The owner commission
authorised local implementation, not live configuration or publication.

Created:

- `scripts/prepare_release.py` — committed exports, private staging, manifest/tar,
  verify/restore, local preflight, synthetic fixtures, receipt import/retention plan.
- `scripts/publication_safety.py` — independent exact-inventory and content validator.
- `release/headers.txt` and `release/404.html` — two reviewed release-only controls.
- `tooling/deployment/package.json`, `.node-version`, `pins.json` — exact selected
  deployment versions with installation/lock/live-upload flags false.
- `tests/test_publication.py` — thirteen new tests with synthetic Git repositories.
- `docs/release-runbook.md` and this report.

Modified only README, deployment acceptance specification and roadmap to describe
actual local implementation. Existing application build/parser/image processor, source
registries, source HTML/CSS/assets, previous tests and `.gitignore` are unchanged.

## Implementation and example

Follow the exact commands in the [operator runbook](release-runbook.md). The short
acceptance procedure prepares fixtures and A/B, inspects/validates the manifest and
archive, rejects an unexpected PDF, detects valid-CSS mutation, restores archived bytes
and demonstrates disabled publication preflight, without credentials or real Bike Library.

Selected committed inputs are read via `git ls-tree`/`cat-file` into isolated exports;
no source checkout operation, reset/stash/clean, fetch, submodule or LFS download occurs.
Dirty fixture working trees were tested and remain unchanged. The build subprocess
gets a minimal environment and private TMPDIR; output is independently validated and
frozen. Manifest, policy snapshots, logs (not retained) and archive are outside the
only potentially uploadable `publication/` tree. A successful build is never permission.

A locally exercised A manifest contained this excerpt (not a standalone manifest):

```json
{
  "schema": 1,
  "release_id": "synthetic-a-177498dc755a4d2c8b5193e2dd42e43a",
  "mode": "synthetic",
  "fixture_version": "A",
  "state": "prepared-not-deployed",
  "sources": {
    "home": "b1452ecc768187a0dbf45fac825d7b0575b4a1aa",
    "bike_library": "e75451965426b074e461ea3e0343ead1a46687d4"
  },
  "archive_sha256": "a3d9374c1c5c8d3bb47f30f8f82a42890184cb4c2c992bf017e634923a2fda89"
}
```

The `bike_library` ID above belongs to a **generated local fixture repository**, not
the actual canonical Bike Library. Full generated manifest also contains UTC time,
source/config/controller hashes, build versions, deployment pins and unverified flags,
file sizes/media types/SHA-256s, local validation, storage classification and URL cases.
Prepared manifest hash: `249dc39323e822ac02cced6c7b01abf24c04429ea7d61c0326ef6498cd848080`.
The independently verified B archive checksum was
`0ace58506582aeac616ceb3e2adba3a7f624883101223d1bbc9547dccb864a10`.
Both examples were retained in transient owner-only synthetic storage, without claiming
that `/tmp` is encrypted or durable. The runbook reproduces them with new IDs/times.

The exact 17-file publication set is:

```text
index.html
bikes/index.html
bikes/brother/big_bro/index.html
bikes/burls/burls_v2/index.html
bikes/dolan/seta/index.html
bikes/mason/bokeh/index.html
bikes/mercian/super_vigorelli/index.html
bikes/nukeproof/cub_scout_14/index.html
bikes/standert/kreissage_rs/index.html
bikes/surly/bridge_club/index.html
assets/css/home.css
assets/identity/identity.css
assets/identity/symbol.svg
assets/identity/favicon.svg
assets/bikes/standert/hero.webp
_headers
404.html
```

Only path identifiers resemble production. All fixture-visible text and image pixels
are neutral; the fixture never accesses actual Bike Library data. The one WebP is
32×16 synthetic pixels, not the approved private source photograph. The same committed
source build, derivative encoding, independent safety validator, archive and frozen-stage
checks are used before synthetic neutralisation, and the final neutral site is revalidated.
No generated source record is kept as a second system of record.

## Verification

- **38 tests passed:** 25 existing, 13 new. Command:
  `python3 -m unittest discover -s tests -v`.
- Negative coverage: invalid/missing revisions and canonical configuration, missing
  image/config source, LFS pointer, malformed records, placeholder build, stale output,
  extra PDF/Markdown/CSV/JPEG/env/Worker/redirect files, unsafe asset source, symlink/FIFO,
  metadata-bearing WebP, active HTML, broken links, leaked local path, changed valid CSS,
  invalid controls/error page, corrupt archive and missing publication authorisation.
- Validation failures stop before a mocked uploader; API dry-run still has zero upload
  invocations and no live adapter. CLI preflight cannot claim Access/owner evidence.
- Same-source synthetic A preparations produce byte-identical publication tar output;
  unique release identity/timestamp are deliberately not deterministic. Exact restore
  matches frozen payload without a newer-source rebuild.
- Retained A/B manifests, image structure/independent decode, archive checksums and all
  member hashes were verified. Simulation current/previous/superseded planning does
  not promote production, delete data or change immutable manifests.
- Documentation links and `git diff --check` pass; all formal A01–A20 remain **Not run**.
- Sibling Git statuses unchanged: canonical Bike Library retains its four pre-existing
  edits (Brother/Burls/Standert and inventory); public identity repository stays clean.
  No sibling writes, real private release, account inspection, credentials, DNS,
  publication, GitHub workflow, commit or push occurred.

Local mapping: A14 inventory/content/manifest/archive checks; A15 explicit commits,
isolation, materialisation and source hashes; A16 negative gating/test-double evidence.
These are local portions, **not full deployment passes**. Effective headers, historical
hosts, caches, browser authentication, session lifetime/revocation and real rollback/
withdrawal remain outside 5A verification.

## Limitations, accepted boundaries and readiness

No architectural departure is required. Private archives are plaintext tar files
**on operator-confirmed encrypted storage**, not portable encrypted tar containers.
The operator must independently verify FileVault/APFS/encrypted-volume arrangements;
software checks ownership/modes and records attestation, not disk encryption. Synthetic
examples carry an explicit non-private storage classification. No real private source
was used to test private-mode artefact storage.

Read-only modes/hashes detect accidental mutation; they are not an adversarial signing
system against the same user replacing both manifest and checksum. Retain an external
trusted manifest hash in later private receipts/history. Secret pattern checks cannot
prove arbitrary source prose contains no sensitive text; private source review remains
necessary. Controller/source hashes and exact output archives supplement commit IDs.

The deployment pins (Node 24.22.3 / Wrangler 4.164.0) were selected from official release/
package evidence. Local Node is 26.13.1. npm metadata lookup failed with ENOTFOUND;
installation, engine compatibility on this Mac and a transitive lockfile remain unverified.
No dependency installation or Wrangler execution was performed. See runbook sources and
reproducible installation follow-up; do not use `npx latest` or enable live upload prematurely.

Slice 5A is owner-accepted. Before 5B: close/reconcile this implementation baseline,
resolve/review pinned deployment installation
and lockfile, confirm encrypted storage/operator conventions, and issue separate explicit
synthetic live-testing authority. No production source selection or private publication
is implied. Slice 6 remains a separate publication boundary.


## Owner acceptance evidence — 17 November 2026

The owner formally accepted Slice 5A after independently observing on the Mac:

- FileVault enabled; all 38 tests passed in **7.295 seconds**.
- Synthetic A and B prepared; manifest and archive inspected against the approved
  17-file inventory; both independently verified.
- Unsafe filesystem permissions, unexpected content and post-preparation mutation rejected.
- A restored without rebuilding; both original releases intact and independently verified.
- Deployment preflight failed closed.

Owner-reproduced archive SHA-256:

| Fixture | SHA-256 |
| --- | --- |
| A | `a3d9374c1c5c8d3bb47f30f8f82a42890184cb4c2c992bf017e634923a2fda89` |
| B | `0ace58506582aeac616ceb3e2adba3a7f624883101223d1bbc9547dccb864a10` |

Owner-observed negative responses:

- `Unsafe release object/permissions`
- `Publication inventory does not match approved policy`
- `Publication bytes differ from frozen manifest`
- `Owner authorisation and independent live Access evidence required`

This is owner-reported evidence, distinct from the assistant's earlier synthetic tests.
The runbook now restores private/frozen filesystem permissions before inventory and
mutation verification, ensuring those checks exercise their intended guards separately.
No implementation change is part of this acceptance update.

Outstanding: pinned Node/Wrangler installation and dependency locking; privacy review
of model names in synthetic URL paths before live publication; trusted external manifest
checksum retention; confirmation that proposed `~/.local/share/pastthegrid-home/releases/`
is non-synchronised and FileVault-protected; a simpler publication command in Slice 6.
All formal live A01–A20 remain **Not run**. No 5B work or publication is authorised.

## Acceptance closure attempt — 17 November 2026

Starting branch/HEAD: `main` at `b1452ecc768187a0dbf45fac825d7b0575b4a1aa`,
matching cached `origin/main`. Pending paths matched the reported Slice 5A implementation;
only documentation acceptance corrections were made during this closure commission.
All 38 tests passed again in 7.221s; 20 internal documentation links and diff hygiene
checks passed. Sibling statuses remain unchanged and all A01–A20 remain Not run.

Git staging failed because the workspace sandbox denied creating `.git/index.lock`
(`Operation not permitted`). No changes were staged, no commit was created and no push
was performed. Fresh remote verification also failed: `Could not resolve host: github.com`.
**Owner acceptance is complete; Git closure is incomplete.** Implementation/documentation
remain available unstaged for closure with repository-write and GitHub network access.
Slice 5B has not begun and requires separate explicit authorisation.
