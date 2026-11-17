# Slice 4 — Private hosting architecture investigation

Investigation and owner acceptance: **17 November 2026**. Status: **Owner-accepted**.
The decisions below are accepted architecture; implementation, account-specific
feasibility and deployment acceptance remain unverified. No permission to deploy follows.
No account, hosting, identity, DNS, credential or remote configuration was changed.
Deployment tests are specified separately in [deployment acceptance](deployment-acceptance.md).

## Reconciled baseline

| Item | Observed state |
| --- | --- |
| Home | `main`, clean before investigation |
| HEAD and cached `origin/main` | `eff24aa4e3221d15b41bb266f1d91025cf2c400d` — add multi-bike Bike Library browser |
| Remote | `https://github.com/tim-jc/pastthegrid-home.git` |
| Fresh remote check | `git ls-remote origin refs/heads/main` failed: DNS could not resolve GitHub; cached agreement is not fresh remote verification |
| Acceptance | Slice 3 explicitly accepted 16 November; desktop and narrow-window review; native mobile Safari deferred |
| Existing conventions | README plus bounded Markdown documents under `docs/`; no roadmap, architecture or decision directory existed |
| Canonical Bike Library HEAD | `07031f74738c15d0bdbb7bc1cfc3c0a618b857c2`; worktree already dirty |
| Existing source edits | Brother, Burls and Standert Markdown; `inventory/to_source.csv` — left untouched |
| Identity sibling | Clean; copied identity already versioned in Home; no build access required |

No material Home conflict or unexpected Home edit was found. Uncommitted canonical working-tree edits
do not block documentation research or publication from separately selected committed
revisions. Releases must use isolated, clean checkouts or equivalent immutable exports
of both repositories; everyday worktrees are neither release inputs nor modified.
The first production source revision is deferred until first private publication.
No content build from the dirty everyday checkout was needed for this investigation. Older Slice 2 notes about an unapplied
photo-link patch are historical; current README and Slice 3 audit supersede them.
No existing hosting decision is contradicted: the README already requires boundary
authentication and excludes client-side access control.

Current build: Python 3.9+, libwebp `cwebp`/`dwebp` (validated 1.6.0); tests also use
`cjpeg`. No Python packages or runtime server. `BIKE_LIBRARY_ROOT` is build-time only.
Eight exact Markdown paths in `config/bikes.json`, `workshop/maintenance_log.csv` and
one approved source JPEG are read. `scripts/build.py` emits 15 files in ignored
`dist/`: ten HTML files, two CSS files, two identity SVGs and one derivative WebP.
Unconfigured builds intentionally emit the five-file placeholder. Publishing that
fallback accidentally must become a release error. No current publication manifest,
deployment wrapper, release archive, cache-header policy or infrastructure verifier
exists; these are **proposals for the next slice**, not claimed protections today.

## Accepted architecture and conditional feasibility

**Accepted: a dedicated Cloudflare Pages Direct Upload project in the existing
Cloudflare account, Access on every serving hostname/path/asset, and owner-triggered
local build and publication from the Mac to `home.pastthegrid.uk`.** Preserve Python
static generation and keep the public Past the Grid site separate. No managed external
build service or automatic Git-triggered publication is selected. Adoption remains
conditional on passing synthetic security acceptance on the actual account; no live
configuration or publication is authorised by architecture acceptance.

Pages supports prebuilt static uploads [C01]. The site's small file inventory and
relative routes fit it without a framework, API, database or Pages Functions.
Cloudflare documents Access coverage for both the production Pages hostname and
preview wildcard, plus a separate custom-domain application [C02]. This establishes
documented feasibility, **not proof of this account's configuration or a universal
cache/hostname privacy guarantee**. An unverified host, policy override or cache result
means stop and keep the site local.

### Plans and cost constraints

Official sources retrieved on the investigation date advertise static Pages requests
as free/unlimited [C03], Free-plan limits of 20,000 files, 25 MiB per asset and 500
builds/month [C04], and Access Free for teams under 50 users [C05]. The Access page
lists paid pay-as-you-go at USD 7/user/month, paid annually. A one-owner static portal
appears within Free capacity; that is a design assessment, not a billing commitment.
Check actual account eligibility, seat counting, retained-log availability and terms
before configuration. Domain registration, paid support or optional products are not
included in this estimate. No paid plan is authorised here.

Direct Upload cannot later be converted into Git integration in-place [C01]; moving
to CI Direct Upload is still possible without switching project type. A later managed
Git-build move requires a new project and full authentication re-acceptance.

## Threat model and URL boundary

Protect records, identifiers/pairing notes, photo pixels, derived HTML, release
archives, logs, source checkout and deployment history. Threats include anonymous URL
knowledge, an authenticated but unapproved identity, stale sessions, accidental aliases,
misconfigured cache rules, compromised build/upload credentials, and an operator
uploading a parent directory. Cloudflare and the chosen IdP are trusted processors;
authorised browsers receive plaintext. This is access control, not end-to-end encryption,
and cannot retract screenshots, downloads, prior browser memory or provider backups.

The accepted Access policy design allows only the owner's exact identity and chosen login
method, default-denies everyone else, and has no Everyone, Bypass, service-token,
IP-based or path-specific exception. Audit all overlapping applications: more specific
paths override broader policies and do not inherit them [C06]. Leave Path empty for
whole-host protection; a subdomain wildcard does not include its parent hostname.
Cloudflare authentication endpoints may legitimately return login UI, but must never
return portal bodies. Protect assets even where their identity graphics are public elsewhere.

| URL surface | Proposed control | Evidence classification / remaining test |
| --- | --- | --- |
| `home.pastthegrid.uk` and every path | Exact-host Access application, empty Path; proxied Cloudflare custom domain | Whole-host matching documented [C06]; test `/`, `/bikes/`, each page, direct `index.html`, redirects, unknown paths |
| Direct photo, CSS and SVG paths | Same host-wide boundary, no public asset exemption | Inference from matching; test each published file, not just pages |
| `<project>.pages.dev` | Separate exact production-host Access application | Explicit procedure in Pages known issues [C02]; not covered by preview toggle |
| `<hash>.<project>.pages.dev` | Separate `*.<project>.pages.dev` Access application | Preview protection documented [C07]; inventory/test every returned deployment URL, including production hashes |
| `<branch>.<project>.pages.dev` | Same wildcard plus explicit inventory of branch aliases | Immutable hashes and mutable aliases documented [C07]; no routine preview uploads proposed |
| Old deployment hashes/aliases | Same enduring host policies; delete unneeded deployments | Test old URLs after update, rollback and deletion; deletion is not assumed to erase all copies |
| Any additional custom domain or deeper hostname | Prohibited unless separately inventoried, protected and tested | One wildcard matches one level [C06]; never assume blanket coverage |
| HTTP, redirects and alternate URL forms | HTTPS-only entry; no body on initial HTTP hop; inspect each redirect | DNS/TLS/Access interaction is empirical; DNS failure alone is not an authentication test |
| Warm CDN/custom cache, validators and byte ranges | No custom Cache Everything/TTL override; test unauthenticated after authorised warm-up | Pages has internal and optional zone caches [C08]; effective boundary must be demonstrated |
| Authorised browser memory/disk | Propose `Cache-Control: private, no-store` on every portal resource; no service worker/offline cache | Reduces persistence, cannot revoke already received bytes; verify effective headers and history behavior |

Use Cloudflare's documented sequence to create the preview application, remove its
wildcard to protect the production Pages hostname, then re-enable preview protection
and confirm **both** applications exist [C02]. Add the custom-domain application
separately, before attaching private content. Do not trust the default preview policy's
Cloudflare-account membership; inspect and narrow its actual identity rules.

Bulk redirects from `pages.dev` to the custom domain are a documented alternative
[C09], but **not the recommended primary privacy boundary**. They introduce another
matching/control layer and a redirect success does not prove every hashed asset URL
is safe. If used, retain Access protection and test every hop.

### Caching, headers and residual risk

Pages documents edge caching, validators, potential additional custom-domain caches
and retention of old assets in a data centre for up to a week [C08]. Do not equate
no-store, a purge, noindex, CORS or a hidden URL with authentication. Retain Access
while changing/deleting content. No broad zone purge that affects the public site is
proposed; use host-scoped URL purging where available and validate it.

In the implementation slice, add and allowlist a generated `_headers` control file
[C10] with no-store and no-referrer, remove permissive cross-origin headers if present,
and review a restrictive CSP appropriate to the existing no-script page. Avoid
conflicting duplicate Cache-Control directives. These headers are not in today's
15-file output. Consider a non-sensitive `404.html` to avoid Pages' default SPA
fallback serving Home on unknown routes [C08]. Any new control/error file must be
explicitly reviewed in the publication manifest. Browser/cache behavior and authentication
precedence are acceptance tests, not inferred from the header file's existence.

### Identity, sessions and revocation

**Accepted authentication:** email one-time PIN (OTP), restricted to the owner's
exact email address. The address is a future private configuration value, not recorded
in these documents. The owner accepts mailbox-possession assurance; OTP is not
independent MFA. Protect the mailbox with strong MFA. Cloudflare's PIN expires after
ten minutes [C11]. No VPN, WARP or extra client software is required. Google [C12],
GitHub [C13] and Cloudflare IdP [C14] were investigated alternatives, not selected
fallback login methods; do not accidentally enable them or broad account membership.

**Accepted intended experience: approximately 30 days authenticated per browser.**
Select Cloudflare's supported **one-month application session**, policy duration
**Same as application** (or the identical supported one-month override), and
**one-month global session**, on each portal Access application. These are settings
to implement and verify, not observations of a configured account. Use the supported
UI/API representation of one month rather than inventing a duration string.

Session precedence is client-session override (if enabled), then policy duration,
then application default; global session controls IdP reauthentication [C15]. No
client/WARP-session override is permitted. An application token remains usable until
its own expiry unless revoked. When it expires, a still-valid global session can
silently renew it after policy evaluation; if the global session has also expired,
new authentication is required. Global expiry alone does not terminate an otherwise
valid application token. Applications on different hostnames can receive tokens at
different times, so these settings do not establish a strict 30-day wall-clock cap
from the first login, or a demonstrated sliding 30-day idle timeout. Cookies cleared,
private browsing, logout, policy changes or revocation can prompt earlier login.
Each browser has its own session. Verify actual token timing, hostname renewal and
Safari behavior in Slice 5B; **the intended month-long experience is not demonstrated**.

For revocation, first remove the owner identity from **every** portal policy (or apply
a verified temporary deny policy), then revoke existing app/user tokens. Revocation
alone allows a still-authorised identity to log in again [C15]. Accepted independently verified operational
acceptance target: old-token and fresh-login network requests blocked on all hosts
within **five minutes** of the policy change and explicit revocation, measured from
the operator action. This is an owner-selected test threshold, not a Cloudflare SLA.
Do not rely on session expiry or an IdP-only disable event for immediate denial.
Already displayed/downloaded bytes are outside that limit.

## Build/publication options

| Model | Content and credentials | Reproducibility, audit and operations | Assessment |
| --- | --- | --- | --- |
| Local build → authenticated Direct Upload | Canonical source and temporary pixels stay on owner computer; Cloudflare receives only approved output. Read-only Git access and separate upload token | Record two immutable commits, tool versions and output hashes; explicit owner action; private local archive for rollback; depends on owner computer | **Accepted initial model**; smallest added trust boundary |
| GitHub Actions → Direct Upload | Private source and derived content enter runner workspace; separate cross-repository read credential plus Cloudflare token; logs/artifacts can disclose content | Pin action SHAs and codecs, use protected manual environment, ephemeral hosted runner, no untrusted PR jobs, no caches/artifact uploads containing content. Automation helps later; source changes do not automatically trigger Home safely without coordination | Viable later, separate workflow/security review; not justified for first deployment |
| Cloudflare Git-integrated build | Pages supports private repos [C16], but integration with Home does not establish access to the separate private Bike Library. Additional authenticated fetch and secret would be required | Must fetch exact source revision, install/pin codecs and avoid sensitive logs/caches; automatic branch/PR deployments enlarge exposure. Separate source updates need explicit triggering | More moving parts than needed; not recommended initially |

GitHub's default workflow token is scoped to its own repository, not a second private
repository [G01]. If CI is later chosen, prefer an appropriately scoped short-lived
GitHub App installation credential or a read-only, single-repository deploy key;
set checkout credential persistence off. Never assume the Home repo's token can read
Bike Library. No CI workflow or private submodule is introduced by this design.

### Canonical source and credential boundaries

Use a clean detached checkout/export of the owner-selected **full Bike Library commit**
in an owner-only build workspace, with no recursive submodules/LFS fetch unless
separately audited. Verify that all explicitly required files are materialised; fail if
missing, an LFS pointer or undecodable. A committed pointer is not a photograph.
Record both full Git commit identifiers in the release manifest. Reject dirty or
mutated isolated release inputs, not unrelated edits in everyday working trees.
Never modify, stash, clean or otherwise interfere with the owner's existing Bike
Library worktree. Selected committed revisions may be exported from it read-only or
obtained via a separate checkout. First production revision selection remains deferred.

For future fetching, prefer a dedicated read-only Bike Library deploy key (single repo,
read-only by default [G02]) with passphrase/Keychain protection (deploy keys are
long-lived, so expiry is not assumed); or narrowly scoped,
expiring repository-read token. No Git credential enters `dist/`, Cloudflare build settings
or the public identity repo. Local read-only input mount/permissions should be used
where practical; verify before/after input hashes. This avoids modifying canonical data
without maintaining a second authoritative copy. Temporary exact-revision checkouts
are disposable build inputs, not manually edited record stores.

| Boundary | Proposed access and custody |
| --- | --- |
| Owner / IdP → Access | Exact owner identity; device/browser tokens protected; account recovery/MFA managed outside repo |
| GitHub → local build | Dedicated repository-read credential in OS credential store; no write permission; rotate on compromise or device change; review at least every 90 days |
| Local upload → Cloudflare Pages | Account-specific `Cloudflare Pages: Edit` token, dedicated time-limited token (proposed maximum lifetime ≤30 days), retrieved from macOS Keychain only for explicitly authorised publication; no DNS/Access/admin permission [C17] |
| Operator → Access/DNS setup | Separate interactive administrator session with MFA; never reuse that credential as routine uploader |
| Build workspace → publication | Private stage, exact file/hash manifest and separate operator authorisation; no parent directories or wildcard upload |

Cloudflare's documented Pages token is **account-level**; project-only resource scope
is not established by this investigation [C17]. The owner **explicitly accepts** its
potential ability to affect other Pages projects, including the public Past the Grid
website. Retain the existing Cloudflare account; do not introduce another account.
Still verify and use the minimum available Pages permissions and account scope.
This risk acceptance is not permission to create a credential or perform publication.

Use a dedicated, time-limited upload token stored in **macOS Keychain**, retrieved only
during explicitly authorised publication. No DNS/Access/admin privileges on that token;
keep administrator credentials separate for infrastructure configuration. Never include
credential values in repositories, logs, command history, manifests or publication
output. Revoke old tokens after a separately authorised replacement and test with
synthetic content before use. No live token is created or rotated in Slice 4. The
exact token expiry/rotation schedule is a future operational setting; the suggested
≤30-day token lifetime is distinct from both browser sessions and artefact retention.
Wrangler and its Node runtime add **deployment tooling**, not a frontend dependency;
exact supported versions/lockfile need review in the next slice, not `npx latest`.

### Private artefact and manifest proposal

Use an owner-only workspace on encrypted local storage; `umask 077`, private TMPDIR
for the current image pipeline's temporary original/pixel files, no cloud-sync/public
folder. Ignored `dist/` is not a security boundary and does not restrict file modes.
Preserve the normal development commands; add a separate release-only gate in the next
slice which requires explicit source configuration and committed revisions.

A private release record outside the uploaded tree should include: release ID/time,
both full Home and Bike Library Git commit IDs, source/config input hashes, Python/libwebp/cjpeg/
Wrangler/Node versions, output relative paths, sizes, MIME types and SHA-256s,
application-test result, independent safety-check result and archive checksum.
After upload, append deployment ID, every alias/hostname, Access app IDs and a redacted
policy fingerprint, approval identity/time, verification evidence and previous known-good
release. Do not publish this record; no absolute local paths, token values or sensitive
metadata in it. Commit IDs alone do not guarantee byte reproducibility; retain exact
verified output in an encrypted private archive plus the toolchain record.

The publication gate must derive expected files from reviewed source/asset registries
and the explicit static list, independently of directory contents. Compare exact sets,
reject symlinks/special files, unexpected HTML/assets, originals, PDFs, `.git`, env files,
source maps, functions, `_worker.js`, unreviewed redirects/routes and stale content.
Validate metadata on actual output image bytes, all internal links and absence of local
paths/secrets. Review any newly proposed `_headers`/404 as explicit control exceptions.
Do not merely accept every file with `.html` or `.webp` suffix. Freeze a read-only stage
and verify hashes again immediately before upload to prevent stale/mutated output.
Retain the current and previous known-good Cloudflare production deployments and
encrypted local copies of both verified publication artefacts **until superseded**,
without an arbitrary expiry. Keep lightweight release history with both full source
revisions, deployment identifiers, manifest hashes and verification outcomes.
After a new release is independently verified, advance current/previous pointers and
remove the older superseded artefact and unnecessary hosted history using the safe
retention procedure below; never remove the only verified rollback target first.
Discard temporary source/pixels/log bodies after checks. Do not cache or publish them
as CI artifacts. File deletion on SSD is not a guarantee of forensic erasure; encrypted
storage and retention discipline are the intended safeguards.

## Accepted lifecycle design — not implemented

All actions below require a separately authorised implementation/deployment slice.

1. **Prepare synthetic-only release.** Choose exact project name in the existing account, owner OTP address,
   policies and session limits. Build non-sensitive pages/assets with distinctive
   markers at every planned path, plus two synthetic versions for history tests.
   No real records, photos, titles/identifiers or source checkout enters this release.
2. **Establish boundary.** Create the dedicated Direct Upload project with only that
   synthetic output if the platform requires an initial deployment. Configure exact
   production Pages, wildcard deployment and custom-domain Access applications.
   Configure Access for `home.pastthegrid.uk` before its site attachment/DNS work.
   Inspect other applications, cache rules and aliases without changing public-site
   behavior. No automatic Git deploys, branch custom domains, analytics or public buckets.
3. **Prove it independently.** Execute the acceptance matrix, including multiple
   synthetic deployments and historical aliases, warmed-cache tests, revocation and
   rollback. Recheck propagation from a separate network where possible. Lack of
   URL enumeration, evidence or a passing boundary test is a no-go, never a waiver.
4. **Create private release locally.** Select explicit committed Home/source revisions in isolated clean checkouts/exports;
   build with a frozen toolchain, run existing tests plus the proposed publication gate,
   inspect private output locally and freeze stage/archive. Selected inputs unavailable, dirty or mutated,
   missing approved image or wrong fallback output means no upload. Uncommitted edits
   in the everyday working trees do not block a separately selected immutable release.
5. **Reconfirm safeguards and authorise.** Re-inventory actual hostnames and Access
   policy state immediately before upload; synthetic evidence must match that state.
   Obtain explicit owner approval of the concrete release manifest and destination.
   No token availability, accepted architecture or passing build implies publication consent.
6. **Upload the exact stage.** Use pinned Wrangler Direct Upload with a named project,
   account and production target; no source directory upload, no ad hoc preview branch.
   Capture returned deployment IDs/aliases without logging tokens or content.
7. **Verify release.** Enumerate URLs again. Run independent anonymous/unauthorised
   checks first, then authorised body/image hash and navigation checks on every file.
   If any new hostname exists outside proven protection, withdraw/deny immediately.
8. **Record and retain.** Record receipt, hashes, policy state and evidence privately;
   only mark deployed/verified after all required tests pass. Remove unnecessary history
   after maintaining current and one previous verified production rollback target.

An upload timeout is **unknown deployment state**, not proof of failure: inspect the
project's deployment list before retrying. Do not make repeated private uploads while
investigating. A failed preflight preserves the current site; a post-upload privacy
failure invokes withdrawal, not just content rollback. Boundary changes invalidate
prior synthetic evidence and require new non-sensitive validation before private use.

### Rollback, history and withdrawal

Pages supports reverting to successful **production** deployments; previews are not
rollback targets [C18]. Keep current and previous known-good production deployment IDs
behind the same policies, with encrypted local artefacts retained until superseded
and lightweight release history retained after artefact removal. To roll back: verify target receipt/hash and boundary state,
choose known-good production ID, verify every live/old host anonymously and then
compare authorised content. Content rollback does not restore Access/DNS/headers outside
the deployment; independently restore and test configuration when that was the fault.
If target was removed, re-upload the archived verified output only after fresh approval
and boundary preflight. Do not rebuild against today's Bike Library and call it rollback.

List all deployments and aliases, not just production's newest pointer. Delete unneeded
ones through supported Pages deletion; non-production aliased deployments may require
force [C19]. Do not assume the current active production deployment can be deleted
in place: switch to a safe non-sensitive production release first where necessary.
Test removed URLs; keep policies over the exact/wildcard hosts in place. Cloudflare
notes project deletion difficulties beyond 100 deployments [C02]; routine small retention
helps but does not replace access controls. No immediate physical erasure guarantee
is inferred from deletion or purge; pursue provider support if required.

Emergency procedure: block all portal identities on all three host scopes, revoke
sessions, stop further uploads/revoke a compromised upload credential, then verify
anonymous **and previously authorised** direct requests cannot retrieve content. If
policy control is uncertain, neutralise serving content with an owner-authorised
non-sensitive replacement and remove historical deployments; if necessary delete the
project after recording IDs. DNS removal alone does not close `pages.dev`, and deleting
Access apps while content exists can expose it. Use scoped cache invalidation only
as additional cleanup and retest old URLs. Escalate if a direct route still serves
content; record incident and potential exposure. Nothing can retract bytes already saved
by a browser or third party. Proposed drill target: five-minute network denial, with
withdrawal completion separately evidenced, not a guaranteed provider purge deadline.

## If Pages cannot pass the complete boundary

Do not deploy private content to Pages. The bounded alternative is **Workers Static
Assets + Access on the custom domain**, `workers_dev = false` and explicit `preview_urls = false` for Version URLs, no separately configured
Preview/Deployment resources or custom preview domains. The production-host switch
does not disable those other URL families [C20, C21, C23]. Cloudflare documents explicit
controls over these alternate routes [C20, C21]. For defence in depth, a small Worker
could strictly verify Access JWT signature/issuer/audience/expiry and permitted host
before serving assets, with `assets.run_worker_first = true` and no fail-open error path.
Static assets otherwise bypass Worker code by default [C22]. All asset requests and any
remaining URL families would need the same synthetic matrix; no default/cache setting
is assumed secure. This retains generated static content but introduces runtime code,
JWT/key-cache upkeep and Workers billing/limits. It needs a new bounded design/owner
approval, not an automatic fallback. Cloudflare Tunnel to a local static server is another
possible direction, but adds origin uptime/patching and home-network dependencies;
not recommended over a verified managed static option for this small portal.

## Accepted decisions, future choices and unverified evidence

The owner accepted on 17 November 2026:

- Conditional Pages Direct Upload in the existing Cloudflare account, owner-triggered
  local Mac build/publication, no managed build or automatic Git publication.
- Exact-owner-email OTP and its mailbox-possession assurance; approximately 30-day
  per-browser authentication using supported one-month app/global sessions; no client
  software; independently verified five-minute revocation target.
- Dedicated time-limited minimum-permission uploader token in macOS Keychain, retrieved
  only for authorised publication, with separate administrator credentials. Account-level
  residual risk, including impact on the public site, is explicitly accepted.
- Current/previous known-good production deployments and encrypted local artefacts
  retained until superseded, plus lightweight release history; no arbitrary artefact expiry.
- Explicit selected committed Home/Bike Library revisions in isolated clean inputs;
  everyday worktree edits do not prevent releases and must not be altered.
- Separate Slice 5A local safeguards, Slice 5B live synthetic proof and Slice 6 private
  publication authorisation boundaries, as recorded in the [roadmap](roadmap.md).

Future operational choices: exact project name, private owner email configuration,
actual first production commits (deferred until Slice 6), pinned deployment tool versions,
token expiry/rotation schedule, Keychain item conventions and encrypted archive location.
None is a live configuration action authorised by this documentation closure.

Account-specific evidence still unverified: ownership/eligibility and effective policies,
production-hash/alias coverage, propagation, warm-cache isolation, policy overrides,
effective cache headers, month-long Safari session/hostname renewal behavior, revocation
timing, deleted-history retrieval and actual available token scope. No hosting endpoint
has been queried for acceptance. **All twenty deployment tests remain Not run.**

If Pages cannot demonstrate complete authentication coverage, fail closed and return
to the alternative architecture investigation above. Architecture acceptance does not
weaken the test criteria or authorise that alternative automatically.

## Official sources

All sources below were retrieved **17 November 2026**. Product behavior/limits can
change; recheck at implementation. URLs are evidence, not configuration authority.

| ID | Official source | Relevant evidence |
| --- | --- | --- |
| C01 | [Pages Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/) | Prebuilt uploads and project-type constraint |
| C02 | [Pages known issues](https://developers.cloudflare.com/pages/platform/known-issues/) | Separate production/preview/custom Access setup; deletion limitation |
| C03 | [Pages pricing](https://developers.cloudflare.com/pages/functions/pricing/) | Static request pricing versus Functions |
| C04 | [Pages limits](https://developers.cloudflare.com/pages/platform/limits/) | Builds, file count, size and preview limits |
| C05 | [Access pricing](https://www.cloudflare.com/sase/products/access/) | Free/paying user-plan constraints |
| C06 | [Access application paths](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/app-paths/) | Host/path matching and override precedence |
| C07 | [Pages preview deployments](https://developers.cloudflare.com/pages/configuration/preview-deployments/) | Public defaults; immutable deployments and branch aliases |
| C08 | [Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/) | SPA fallback, caching, validators and asset retention |
| C09 | [Redirect Pages hostname](https://developers.cloudflare.com/pages/how-to/redirect-to-custom-domain/) | Optional bulk redirect behavior |
| C10 | [Pages headers](https://developers.cloudflare.com/pages/configuration/headers/) | Header override mechanism and conflicts |
| C11 | [One-time PIN](https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/) | Mailbox login and PIN expiry |
| C12 | [Google IdP](https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/google/) | Personal Google integration |
| C13 | [GitHub IdP](https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/github/) | OAuth-based identity option |
| C14 | [Cloudflare IdP change](https://developers.cloudflare.com/changelog/post/2026-05-19-cloudflare-as-identity-provider/) | Do not assume legacy default IdP |
| C15 | [Access sessions](https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/session-management/) | Precedence, renewal, explicit revocation and re-login |
| C16 | [Pages Git integration](https://developers.cloudflare.com/pages/get-started/git-integration/) | Private repo support and automatic builds |
| C17 | [Direct Upload with CI](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/) | Account Pages Edit upload permission |
| C18 | [Pages rollbacks](https://developers.cloudflare.com/pages/configuration/rollbacks/) | Production-only rollback targets |
| C19 | [Delete deployment API](https://developers.cloudflare.com/api/resources/pages/subresources/projects/subresources/deployments/methods/delete/) | Deletion and aliased non-production handling |
| C20 | [Workers hostname controls](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/) | Persist disabled default hostname in configuration |
| C21 | [Workers version URLs](https://developers.cloudflare.com/workers/versions-and-deployments/version-urls/) | Separate alternate URL controls; old preview URL redirects here |
| C22 | [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/) | Asset routing and run-worker-first option |
| C23 | [Workers Previews configuration](https://developers.cloudflare.com/workers/previews/configuration/) | Separate Preview resources and configuration |
| G01 | [GitHub checkout](https://github.com/actions/checkout) | Separate private-repository credential and checkout permissions |
| G02 | [GitHub deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys) | Single-repository read-only key option |


## Original investigation verification (before acceptance and Git closure)

Completed locally on 17 November 2026:

- All **25 existing tests passed** using synthetic source/image fixtures. No dirty
  live Bike Library build or publication was performed.
- Documentation local links checked: seven links resolve; A01–A20 present with all
  future deployment outcomes explicitly Not run. Official source URLs were retrieved
  through documentation research; no authenticated account state was read.
- `git diff --check` passed. Diff against HEAD for `scripts/`, `src/`, `config/`,
  `tests/` and `.gitignore` is empty. Only README and the three new Markdown documents
  (`private-hosting-architecture.md`, `deployment-acceptance.md`, `roadmap.md`) changed.
- Bike Library retains the same four pre-existing modified paths; identity sibling
  remains clean. No command wrote to either repository.
- Fresh GitHub verification remains unavailable due to DNS. No API calls to configure
  or inspect live Cloudflare accounts, no website uploads, synthetic publication,
  DNS edits, credential operations, commit or push occurred.

The investigation was complete for review at that point. The owner has since accepted
Slice 4 on 17 November 2026 with the decisions incorporated above. Implementation has
not begun; no deployment acceptance test has run. Git closure is reported separately
after its commands have completed, without implying successful remote verification.

## Acceptance and Git closure verification — 17 November 2026

The owner authorised these four documentation files only for commit and push; Slice
5A remains unauthorised. Starting Home branch/HEAD: `main` at
`eff24aa4e3221d15b41bb266f1d91025cf2c400d`, matching cached `origin/main`.
Only README and the three outstanding Slice 4 documents were present as changes.
Fresh `git ls-remote` again failed because GitHub DNS could not resolve; do not treat
cached tracking state as verified GitHub closure.

Before the commit attempt: all 25 existing tests passed, eight local documentation
links resolved, A01–A20 remained present and Not run, superseded short-session and
artefact-expiry settings were removed, and `git diff --check` passed. The application,
source/asset registries, tests and `.gitignore` are unchanged from HEAD. Bike Library
retains the same four pre-existing modified paths and the identity sibling remains
clean. No sibling writes, tooling installation, credential operations, infrastructure
changes or publication occurred. Actual commit/push/remote-verification outcomes are
reported after execution; this section does not pre-claim success.

Git closure outcome: staging the four named files failed with
`Unable to create .git/index.lock: Operation not permitted` under the workspace
sandbox. No files were staged, no new commit was created and no push was performed.
Fresh remote verification also failed with `Could not resolve host: github.com`.
Slice 4 architecture acceptance is recorded, but **Git closure is incomplete**.
The documentation is ready for closure in an environment that permits repository
metadata writes and GitHub connectivity; Slice 5A implementation has not started.
