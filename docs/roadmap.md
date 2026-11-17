# Past the Grid Home roadmap

Updated 17 November 2026. Acceptance is distinct from implementation, commit,
remote verification, deployment and publication.

| Slice | Scope | Status |
| --- | --- | --- |
| 0 | Static build, local preview and shared identity | Accepted |
| 1 | Canonical Standert specifications, notes and maintenance | Accepted |
| 2 | Explicitly approved Standert derivative photograph | Accepted |
| 3 | Eight-bike library index and shared detail pages | Accepted 16 November 2026; committed at `eff24aa`; native mobile Safari deferred |
| 4 | Private hosting architecture and deployment acceptance specification | **Owner-accepted 17 November 2026** with amended sessions, credentials, retention and source policy; no hosting configured |
| 5A | Local publication safeguards | Proposed; not authorised or started |
| 5B | Live synthetic hosting proof | Proposed; requires separate explicit authorisation; no real private content |
| 6 | First private publication and operational acceptance | Proposed; requires successful synthetic acceptance and separate explicit publication authorisation |

The [accepted architecture](private-hosting-architecture.md) preserves conditional
Pages Direct Upload, owner-triggered Mac builds and the existing Cloudflare account.
The [deployment acceptance specification](deployment-acceptance.md) retains all twenty
criteria, each **Not run**. Account-specific feasibility and intended approximately
30-day per-browser sessions have not been demonstrated. Failure to prove complete
authentication coverage must fail closed and return for an alternative design decision.

## Slice 5A — Local publication safeguards

Proposed scope, awaiting its own commission:

- Release build tooling and explicitly selected committed Home/Bike Library revisions.
- Isolated clean checkouts or immutable exports, without interference with everyday
  worktrees; unrelated uncommitted changes do not block selected committed inputs.
- Publication manifest containing both full Git IDs; independent safety validation.
- Private staging, encrypted current/previous release archives retained until superseded,
  and lightweight release history.
- Reviewed hosting headers and error controls.
- Pinned deployment tooling, synthetic fixtures and automated negative tests.
- Local verification only: no Cloudflare/DNS changes, credentials or live publication.

This Git closure does not authorise beginning Slice 5A or installing tooling.

## Slice 5B — Live synthetic hosting proof

Requires separate explicit authorisation. Proposed scope:

- Configure Cloudflare Pages/Access in the existing account and publish synthetic content only.
- Independently verify every hostname, path and asset using direct requests and body checks.
- Desktop and native mobile browser acceptance, supported month-long session behavior
  and independently measured five-minute access revocation.
- Synthetic update, rollback, retention and emergency withdrawal drills (A01–A20).
- Report evidence and limitations for owner acceptance. No Bike Library private content.

## Slice 6 — First private publication

Requires successful synthetic acceptance and separate explicit publication authorisation:

- Select actual committed production revisions of Home and Bike Library (deferred until here).
- Generate, verify and obtain owner approval of the concrete private release/manifest.
- Reconfirm security safeguards, publish explicitly authorised output, and independently
  verify deployment and operational access across personal devices.
- Record both full source revisions, deployment IDs, manifest hashes and verification
  outcomes; retain current/previous verified production releases and encrypted artefacts
  until superseded, then safely remove unnecessary older copies while retaining history.

No automatic publication follows architecture acceptance, Git closure or a successful
build. No galleries, PDFs, editing, search, other repository changes or public-site
redesign are included. Do not silently add runtime authentication if Pages fails.
