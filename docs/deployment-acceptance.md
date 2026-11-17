# Private deployment acceptance — accepted specification, not executed

Date: **17 November 2026**. Companion to the [Slice 4 architecture](private-hosting-architecture.md).
Every criterion below is **Not run**. This document neither configures hosting nor
authorises a deployment. The owner accepted the Slice 4 architecture and this amended
specification on 17 November 2026. Slice 5A local safeguards are implemented and
owner-accepted 17 November 2026 after independent Mac checks; live security
implementation/execution is not undertaken. Slice 5A is local
safeguards only. Live Stage S testing requires separate Slice 5B authorisation.
Stage S uses only synthetic content. Stage P permits
real private content only in separately authorised Slice 6, after S passes and the
concrete release from explicitly selected committed revisions is owner-approved.

## Common test preparation

Before Stage S, the separately authorised operator must record the actual account,
project, custom domains, Access apps/policies and **all** Pages deployments/aliases from
the dashboard/API, including pagination. Build a private host inventory from the project
production hostname, deployment `url`/`aliases`, custom domains and branch aliases; never
guess a few hashes and call that complete. Reconcile DNS against that inventory. Add any
new URLs returned after each upload. Unknown serving hostname is a failure, not a skip.
For any future Workers fallback, include its separate version, preview, deployment and
custom preview hostnames, not just `workers.dev`.

Synthetic fixture prerequisites: two identifiable versions A/B; pages at `/`, `/bikes/`
and every real detail route; synthetic CSS/SVG/WebP at corresponding asset paths;
unique non-sensitive HTML markers and known byte hashes for **each** file. Add an
unknown-path request and redirect cases. Do not use actual Bike Library information
or the real Standert image. Keep synthetic manifest, response capture and redacted
configuration evidence in an owner-only test directory.

Use four independent request contexts:

- **N**: fresh direct HTTP client without cookies, bearer/service tokens, client certs
  or cached responses. Also use a new private browser profile with no Access/IdP session.
- **U**: an independently authenticated identity not on the allowlist, owned/controlled
  by the tester. No messages to another person are required.
- **A**: authorised owner browser/session; never share its cookies with N or U.
- **R**: a captured owner test session retained securely for revocation tests; not printed
  to logs, shell history, a repository or evidence attachments.

A fresh HTTP GET can be captured as below **only during authorised deployment testing**.
`HOST` and `PATH_FROM_MANIFEST` are populated from the inventoried hosts and expected
file list. This is a read-only test illustration, not a deployment script; no command
in this document was run against hosting in Slice 4.

```sh
curl -q --silent --show-error --compressed --path-as-is \
  --max-time 30 --max-redirs 0 \
  --dump-header response.headers --output response.body \
  "https://${HOST}${PATH_FROM_MANIFEST}"
```

`-q` must be first to avoid `.curlrc` injecting credentials. Use a clean process with
no authenticated proxy/WARP bypass policy. Inspect the first response and then each
redirect hop separately in N; cap the chain and record final host. Use a separate
network where available (for example mobile data) to reduce shared-session/edge effects.
Do not use a service token as a substitute for N or for owner-login tests.

For denied responses, record status, Location, Content-Type, cache headers, UTC time,
request method/path/host and response-body hash; identify the body as an expected
Cloudflare login/denial or non-sensitive error document. Inspect decompressed bodies
for **all synthetic private markers**, full-file matches and representative image-byte
segments. Retain raw captures for reviewer inspection in private storage. In P, compare
against the private release manifest and local private bodies without attaching those
bodies to public logs. Redact cookies, email addresses and token-bearing redirects.

A `302`, `403`, `404` or different body hash by itself is **not** proof of non-disclosure:
error bodies can contain private text and redirects can carry it too. Unexpected image
bodies, partial portal data, unclassified responses or transport failures are failures
or inconclusive—not passes. A disabled URL may return a platform error, but evidence
must show it cannot serve the tested content, and it must be rechecked after updates.

## Executable acceptance matrix

Mode **Auto** means a future independent HTTP/local-check harness, not an existing
implemented test. **Owner** requires browser/dashboard action. All rows apply to S;
repeat applicable non-destructive rows in P after first publication and each update.
Destructive drills use synthetic versions first, with separately approved real emergency
procedures if ever needed.

| ID / area | Preconditions | Procedure | Expected outcome | Evidence | Mode |
| --- | --- | --- | --- | --- | --- |
| A01 URL inventory and policies | S project contains synthetic A; operator can inspect project and Access | Enumerate every deployment/alias/domain; map exact production host, wildcard hash/branch hosts and custom host to effective Access app. Inspect more-specific path apps, Bypass/Everyone/service policies and cache overrides | No unmapped URL, broader identity grant or public asset exception; whole-host paths covered | Redacted inventory, app/policy export or screenshots, reviewer mapping | Owner + Auto |
| A02 Unauthenticated HTML | A01 complete; N has no session | For every host, GET every HTML file at direct `index.html` paths and clean directory URLs; also `/bikes` without slash, `/`, unknown route and HTTP equivalent. Inspect each redirect hop and body | Only login/denial/non-sensitive error; no synthetic or real private body/fragment; HTTP never returns portal data | Complete host × HTML-path results and classified captures | Auto + private browser |
| A03 Unauthenticated assets | N; expected CSS/SVG/WebP list | GET every asset directly on every host, not through HTML navigation; repeat with `Range: bytes=0-63`, HEAD and OPTIONS | No asset bytes on GET/range or body-bearing variants; method changes do not bypass authentication. HEAD alone is not proof | Body/hash/type comparisons and method-specific headers | Auto |
| A04 Default hostname | S custom domain is working; exact `<project>.pages.dev` known | Repeat A02/A03 on the production Pages host independently of custom-domain session; inspect redirects rather than assuming they authenticate | No content bypass through default host or redirect chain | Default-host captures and exact Access-app match | Auto + Owner |
| A05 Preview, branch and history | S A and B exist; at least one synthetic preview/branch alias intentionally created for testing | Repeat A02/A03 for every returned hash, production hash, preview hash, branch alias and historical A URL. After alias advances to B, retest A directly | Old and current URLs remain protected; no reliance on noindex or an unused branch | Deployment/alias list before/after, full path matrix | Auto + Owner |
| A06 Alternate domains and URL forms | Inventory plus registered custom domains available | Probe each listed alternate domain, trailing/duplicate slash, percent-encoded `index.html` segment and query-string variants using N. Inspect any normalisation redirects; verify no unlisted custom domain exists | Same denied content boundary; no broader host/policy match | URL variants, configuration review and response classifications | Auto + Owner |
| A07 Warm caches and validators | A can retrieve all synthetic resources | Warm each host/path in A; immediately repeat the identical GET in separate N, then use random query, `If-None-Match` from A, Range and alternate Accept-Encoding. Repeat after A→B update and revocation | N receives no resource bytes and no unauthorised validator success that authorises reuse of private content. Unexpected 304/206 requires investigation, not an automatic pass | Warm/cold timestamped request pairs, ETag/cache headers, body inspection | Auto |
| A08 Authorised functionality | A successfully completes chosen IdP flow | Open Home, index and all eight details; compare authorised decompressed HTML/image hashes with release output, following canonical redirects; check direct photo, CSS and SVG | Correct release, specifications, grouping and 1600×901 approved image; all navigation works | Hash report, release ID, redacted browser screenshots | Auto + Owner |
| A09 Unauthorised identity | U is separate from owner and absent from every allow policy | Complete the configured login flow as U; request the same page/asset matrix, including through default and history hosts. With OTP, delivery refusal alone is insufficient—test body boundary too | U cannot retrieve any portal content despite an identity login elsewhere | Redacted identity/policy evidence and body matrix | Owner + Auto |
| A10 Expiry and reauthentication | Accepted one-month application, policy Same as application (or identical supported one-month override), and one-month global settings recorded; A token issue/expiry times captured privately | Verify actual supported values and precedence; test separate browsers and hostname token issuance. In a separately authorised synthetic scope, shorten durations to exercise app renewal while global is valid, and reauthentication after both expire; restore month-long settings and inspect actual token lifetime. Record longer-term owner observations without claiming a simulated short test proves 30 days elapsed | Approximately 30-day per-browser experience is supported by settings/token evidence, not yet assumed demonstrated; valid app token may outlive global expiry; no rolling-idle or strict first-login 30-day cap claimed; no WARP/client override | Redacted effective configuration, token timestamps, challenge/renewal record, restored settings and native-browser observation | Owner |
| A11 Revocation | A/R is active; five-minute threshold approved | Remove identity allowance across all portal apps, explicitly revoke existing sessions, start timer; retry old R cookies and fresh owner login on all hosts until threshold. Do not only clear local browser cookies | No network private-content retrieval or new authorised login within five minutes; old saved bytes explicitly excluded | Operator-action timestamp, redacted token identifier, timed response/body classifications | Owner + Auto |
| A12 Desktop browser | S passed; A on owner's normal desktop browser | Login, navigate index/Standert/Mason/Brother/Nukeproof, scroll tables, tab focus, direct asset and logout; inspect console/network and 200% zoom | No broken links/assets, application console errors or document overflow; table scroll contained; no external runtime content requests except identity flow | Browser/version, viewport, screenshots and redacted console/network summary | Owner |
| A13 Mobile browser | Owner has iPhone/mobile Safari and authorised identity | On phone, repeat login/navigation and direct-image tests on Wi-Fi and mobile data; rotate screen, inspect tables, return from mail/IdP, logout and new-tab retrieval | Usable native mobile layout and stable authentication; image uncropped; no document-level horizontal overflow or login loop | Phone/OS/browser versions, screenshots and owner sign-off | Owner |
| A14 Publication manifest | Release stage frozen; independently derived expected set available | Compare exact recursive file set, hashes, sizes/MIME, approved WebP metadata and paths; reject symlinks, originals/PDFs, source/env/metadata/functions/redirects not explicitly approved. Verify zero bytes outside intended stage are upload inputs | Only reviewed files and approved derivative/control exceptions selected; current site expected 15 content files, plus separately reviewed hosting controls if introduced | Private manifest, safety report, archive hash | Auto + owner manifest approval |
| A15 Canonical read-only/revisions | Explicit committed Home and Bike Library revisions selected; isolated clean checkouts/immutable exports; source credential read-only | Verify both full Git identifiers in manifest and selected input hashes before/after build; inspect credential grant. Using synthetic local fixtures, show everyday worktree edits neither enter the release nor block an export from a selected commit; do not modify the owner's real worktrees. Simulate unavailable committed inputs and missing approved photo | No canonical modification/stash/clean; only chosen commits enter release; dirty/mutated isolated inputs fail, unrelated everyday edits do not; no placeholder/stale publication | Both full commit IDs, input-hash comparison, isolation/read-only proof and negative tests | Auto + Owner |
| A16 Failed validation blocks upload | Synthetic upload harness/test double counts invocations; no live upload required | Exercise bad date, unknown CSV key, unsupported Markdown, extra PDF, wrong image metadata, missing source configuration, mutated stage and failed Access preflight | Zero upload calls for every failure; previous deployed release untouched | Negative-test log and zero-call assertion, no sensitive values | Auto |
| A17 Safe update/failure recovery | Synthetic A validated production; B locally approved; both have receipts | Repeat preflight, upload B only when authorised, inventory new URLs; compare A/B hashes across hosts and all denial tests. Simulate transport failure and inspect deployment state before retry | B verified, no public window/new alias bypass, uncertain upload reconciled rather than blindly retried | Receipts, timestamps, deployment list and repeated matrix | Owner + Auto |
| A18 Rollback | Synthetic A/B are successful production deployments; A archive/manifest retained | Confirm current boundary, restore A by production deployment ID; compare A output and denied responses on every current/old host. If deleted, separately authorise archive re-upload | Exact known-good A restored securely; Access unchanged/verified; preview cannot be selected as rollback target | A hashes, deployment IDs, policy-state comparison and response matrix | Owner + Auto |
| A19 Historical removal and retention | Synthetic A is superseded by verified B and C; current/previous production IDs and encrypted artefacts recorded; lightweight release history retained | Confirm C is current and B previous, with both encrypted local artefacts available and hashes verified. Only then remove superseded A's local artefact and unnecessary hosted history using alias-aware supported controls; retest A URLs including warmed paths; preserve A's lightweight source/deployment/manifest/verification record | Current and previous known-good deployments and local artefacts retained until superseded, no arbitrary 30-day expiry; superseded URL cannot retrieve A; all remaining hosts protected; no physical erasure claim | Before/after inventory, archive hash/retention checks, release-history entries, deletion results and A-URL captures | Owner + Auto |
| A20 Emergency withdrawal | Synthetic active A and old B; five-minute drill target approved | Block identities on all host scopes and revoke tokens; test N/U/R. Stop uploads; replace active content with non-sensitive release and remove history if needed; retest every URL. Do not delete Access first or rely on DNS removal | Network retrieval denied within five minutes; serving content neutralised with evidence; residual copies/propagation failures explicitly recorded | Timed drill log, all-host captures, remaining-deployment inventory | Owner + Auto |

## Decision and evidence rules

All A01–A20 must have outcomes and evidence, not ticks inferred from configuration.
Their current status is **Not run**. Slice 4 acceptance approves the design, not results.
Separate Slice 5B authorisation can permit live synthetic testing; neither this
Slice 4 documentation/Git closure nor a later Slice 5A local commission permits it. For stage P, approved identity/session settings must be restored
and retested after any synthetic revocation drill. Do not lock the owner out of their
Cloudflare administrator recovery account while testing the portal identity.

A transport/DNS outage or unavailable phone is **inconclusive/deferred**, never a pass.
Native phone testing was deferred for local Slice 3 acceptance; remote private hosting
introduces a new login boundary and requires actual device testing before deployment
acceptance. A public-content leak, unidentified hostname, uncertain caching or inability
to revoke tokens is a **no-go** for real data. Keep synthetic content only, or withdraw
private data if already present. Do not lower the criteria to make Pages pass; return
to the alternative-architecture decision in the investigation.

Retain a private evidence record with criterion ID, S/P stage, UTC timestamp,
release/manifest hash, host inventory, browser/client versions, outcome and reviewer.
No private response bodies, cookies, pairing notes or photograph bytes go into public
issues, CI logs, repository documentation or shared screenshots. Cloudflare dashboards
alone are insufficient; independent N/U/R HTTP results are required.


## Slice 5A local evidence boundary

The [release runbook](release-runbook.md) maps implemented synthetic local tests to
portions of A14–A16. This is not formal execution or a pass of any deployment criterion.
All A01–A20 remain **Not run**. Slice 5A has no live uploader and performed no live
hosting, identity, credential, DNS or publication action. Effective response controls
and deployment-tool installation remain unverified.


Slice 5A owner acceptance covers local preparation/verification only. Owner-observed
archive checks and negative responses are recorded in the [report](slice-5a-report.md).
No live criterion has been executed; **all A01–A20 remain Not run**. URL-path privacy,
toolchain verification and external manifest checksum retention remain carry-forward
items, not grounds to weaken live acceptance.
