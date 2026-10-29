# OWASP Juice Shop — source-only security review

Target: `C:\Users\User\Projects\web-security-audit-workspace\juice-shop`  
Application version: 20.3.0 (`package.json`). Commit identity: not supplied/established. Review date: 2026-10-29. Target remained read-only.

This is an intentionally vulnerable training application. The findings describe the security boundaries its source actually implements; they are not an assertion that the educational project accidentally introduced them. No application was started, no deployed service was contacted, and no payload or regression test was executed. All checks below are source analysis; proposed regression checks are recommendations.

## Executive assessment

The code allows unauthenticated SQL query manipulation, disclosure of a reusable JWT signing key, privileged self-registration, cross-account resource access, and exposure of password hashes and MFA secrets. Separate paths permit filesystem writes and server-side JavaScript evaluation when their challenge gates are enabled. Browser trust bypasses, financial validation gaps, unsafe recovery, and LLM tool authorization defects expand the attack surface.

The most useful repair order is: remove public secret and data exposure and rotate keys; establish one validated principal and explicit generated-API authorization; replace interpreter and filesystem primitives; then repair browser rendering, financial invariants, and LLM tool enforcement. Safety-mode toggles do not replace these controls.

**Evidence convention:** Confirmed means a complete source-level security violation is established (source-proven), not runtime reproduction. Supported means the source establishes a dangerous path but a material gate, browser policy, library behavior, or deployment prerequisite remains unverified. Severity describes bounded impact in this application, independently of confidence. Source anchors are relative to the target root. Secrets are identified by location only.

## Scope and architecture

Angular SPA and server-rendered Pug/Handlebars pages; Express middleware and custom routes; Finale-generated Sequelize APIs; SQLite relational data; in-process MarsDB review/order collections; file uploads and static/FTP/log/infrastructure serving; JWT/cookie/cache identity; Socket.IO training notifications; external image retrieval, OAuth browser flow, web3 integrations, and LLM chat/tool calls. Roles considered: unauthenticated, customer, deluxe, accounting, administrator, and another user's identity. Trusted configuration and server filesystem are separate boundaries from user input.

Read: complete server registration, every `routes/*.ts` handler, all `models/*.ts`, core security/shared startup code, all frontend Services files, selected frontend components and build configuration, and deployment/security-relevant configuration. Exact reviewed files and residual scope are recorded below and in `process.md`. Runtime and external advisory verification were excluded. Effective reverse-proxy/browser policy, resolved third-party implementation, build artifacts, and active challenge configuration were unavailable.

## Findings

### WSA-001 — SQL concatenation bypasses login and exposes database rows

**High · Confirmed · source-proven.** Unauthenticated callers control email in `POST /rest/user/login` and `q` in `GET /rest/products/search`. Registration is in [server.ts:616](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:616>) and [server.ts:622](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:622>). [routes/login.ts:33](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/login.ts:33>) concatenates email into SQL; hashing the separate password does not bind email. A selected row is converted into an authenticated session at [routes/login.ts:18](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/login.ts:18>). MFA remains a separate check for accounts with a configured secret. [routes/search.ts:20](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/search.ts:20>) truncates the search string to 200 characters, then interpolates it twice in SQL at line 22 and returns result rows at line 70. Length limits do not escape SQL syntax.

Expected: inputs are SQL values, never query syntax. Actual: predicate alteration and union-style reads can expose SQLite tables, including credentials, and login can select an account without its password. This is not evidence of operating-system command execution or stacked-query support.

**Fix:** bind both search and login parameters; use explicit projections and a password-verification routine after fetching one unique identity. **Regression:** synthetic quote/metacharacter inputs must remain literal searches; attempts to alter login predicates must fail; valid logins, MFA checks, and literal searches must still work. Reference: [Security topic](https://portswigger.net/web-security/sql-injection).

### WSA-002 — Public infrastructure source exposes the application's reusable signing key

**High · Confirmed · source-proven.** [lib/insecurity.ts:21](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:21>) embeds the RSA private signing key used at line 54. The same private key is embedded in [infrastructure/terraform/networking.tf:171](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/infrastructure/terraform/networking.tf:171>). [server.ts:269](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:269>) exposes `/infrastructure`, and lines 280–286 return `.tf` source after removing comment markers, not key material. `lib/terraformCustomization.ts` changes application naming without removing this secret. The public key is also intentionally served; it is not itself secret.

An unauthenticated reader can obtain the private key and produce valid signatures containing chosen user data/roles. [lib/insecurity.ts:184](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:184>) accepts a newly presented signed token into the authenticated-user cache, and role checks at lines 152–170 trust its payload. Impact is account and privileged-role impersonation within deployments using this key; no need to claim algorithm confusion or break RSA.

**Fix:** remove private keys from source and public infrastructure responses; rotate the signing key and invalidate all old sessions. Use environment-specific managed secrets and validate token purpose, issuer, audience, expiry and live subject state. **Regression:** public paths and built artifacts contain no private keys; an old-key token and a fabricated privileged token fail; only server-issued tokens under the new key succeed. Reference: [Security topic](https://portswigger.net/web-security/jwt).

### WSA-003 — Public registration accepts privileged model fields

**High · Confirmed · source-proven from generated API registration.** `POST /api/Users` is public ([server.ts:431](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:431>)). Its pre-hooks trim values and record challenge events; they do not establish a write-field allowlist. The generated resource at [server.ts:505](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:505>) / [server.ts:522](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:522>) maps the User model, and [models/user.ts:76](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/user.ts:76>) accepts `customer`, `deluxe`, `accounting`, or `admin` as role values. Model defaults apply only when the caller does not provide a value. Response `excludeAttributes` is not request authorization.

An attacker can register with a privileged role, then authenticate normally and pass role-dependent checks. Related writable security fields such as `totpSecret` and `isActive` have no explicit registration projection; their exact Finale write behavior should be verified when dependencies are available. The role path does not rely on a forged JWT. A special-case rejection of one accountant email does not prohibit an accounting role on another email ([models/user.ts:125](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/user.ts:125>)).

**Fix:** accept only email/password and permitted profile fields; force customer role and server-owned lifecycle/MFA fields. Create privileged accounts through a separate authorized operation. **Regression:** submit role/admin, accounting, MFA and lifecycle fields during registration; role must remain customer and unauthorized fields must be rejected or ignored. Legitimate registration must work. Reference: [Security topic](https://portswigger.net/web-security/access-control).

### WSA-004 — Generated and adjacent APIs lack role and ownership enforcement

**High · Confirmed · source-proven authorization omissions.** The resource loop at [server.ts:501](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:501>) generates CRUD without an application ownership/role policy. Earlier middleware only partially restricts it:

| Surface | Evidence and actual boundary failure |
| --- | --- |
| Products | [server.ts:392](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:392>) permits any JWT to create; line 393 leaves update authentication commented out. Anonymous callers can change product data/prices by ID. DELETE is denied. |
| Users / authentication details | [server.ts:386](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:386>) and line 421 require any JWT, not administrator. Ordinary customers can enumerate other users and associated email, role and last-login data. [routes/authenticatedUsers.ts:26](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/authenticatedUsers.ts:26>) masks password and TOTP, so those fields are not claimed exposed by that handler. |
| Complaints | [server.ts:404](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:404>) allows any JWT to list all complaints; POST does not overwrite `UserId`. Item routes are denied. |
| Feedback | [server.ts:384](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:384>) only requires a JWT for item access; DELETE is not role restricted. A customer can delete another user's feedback. POST is public with a caller-controlled `UserId`; PUT is denied at line 456. |
| Recycles | [server.ts:411](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:411>) invokes [routes/recycles.ts:12](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/recycles.ts:12>) without authentication; the lookup carries only the requested ID. Address/schedule data can be read by an anonymous caller who supplies another record's ID. The list-blocking handler is not protection for item access. |
| Complaint / Recycle / PrivacyRequest attribution | [server.ts:405](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:405>), line 409 and line 467 authenticate a token but do not assign `UserId` from the principal. Foreign keys validate existence, not authority to act as that user. |

These are concrete exposed record/operation boundaries; the report does not assume a real payment processor or external fulfillment. Other generated resources and positive controls are tabulated in the coverage section.

**Fix:** deny operations by default; add server role policy and owner-scoped queries at every generated operation; derive attribution from the validated principal and use write allowlists. **Regression:** a two-user/one-admin operation matrix must reject anonymous and cross-user reads/writes/deletes, preserve public product reading and public feedback policy, and allow authorized administrator operations only. Reference: [Security topic](https://portswigger.net/web-security/api-testing).

### WSA-005 — Address PUT changes ownership before an owner check

**High · Confirmed · source-proven.** Address list/read/delete are explicitly owner-scoped in `routes/address.ts`, invoked at [server.ts:472](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:472>), line 474 and line 475. Their sibling PUT at line 473 merely invokes `appendUserId`, which overwrites request `UserId` with the caller's ID ([lib/insecurity.ts:173](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:173>)), then lets Finale update by the URL's record ID. [models/address.ts:25](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/address.ts:25>) defines the owner relation without an immutability hook.

A logged-in user can PUT another user's address ID, transferring its owner to themselves; their subsequent correctly scoped GET can disclose the address. Knowing or enumerating an ID is required. Appending identity to the update values is not equivalent to adding it to the update predicate.

**Fix:** update with `where: {id, UserId: principal.id}` and an allowlist that excludes owner changes; make owner immutable after creation. **Regression:** A updating B's address must affect zero rows and preserve B's owner/content; A may update their own address; read/delete controls must remain intact. Reference: [Security topic](https://portswigger.net/web-security/access-control/idor).

### WSA-006 — Basket IDs and item IDs are not scoped to the authenticated owner

**High · Confirmed · source-proven.** `/rest/basket` requires a token and appends a user ID ([server.ts:379](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:379>)), but [routes/basket.ts:19](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/basket.ts:19>) fetches the requested basket by ID without that owner. [routes/coupon.ts:18](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/coupon.ts:18>) changes the requested basket by primary key, and [routes/order.ts:35](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:35>) checks out the requested basket without owner qualification and empties it at line 51. Generated BasketItem list/read/delete have only authentication ([server.ts:381](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:381>)), while the update check ([routes/basketItems.ts:68](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/basketItems.ts:68>)) also looks up by item ID without owner qualification.

A customer who supplies another basket/item ID can read basket contents, modify quantities, delete items, apply coupons or consume its contents through checkout. This does not prove charges to another person's card; checkout's payment defects are described separately. [models/basketitem.ts:47](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/basketitem.ts:47>) and line 99 prevent changing BasketId/ProductId on existing rows, but do not prevent editing/deleting an unowned row.

**Fix:** resolve all baskets/items through the principal's basket relation; apply the owner predicate to fetch, mutation and checkout; do not accept caller basket identity where it can be derived. **Regression:** A cannot list, read, coupon, mutate or check out B's basket/items; normal own-basket operations succeed. Reference: [Security topic](https://portswigger.net/web-security/access-control/idor).

### WSA-007 — Duplicate JSON keys separate basket authorization from the saved owner

**High · Confirmed · source-proven.** [server.ts:341](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:341>) retains raw JSON while also parsing it; [lib/utils.ts:188](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/utils.ts:188>) uses a second custom parser that preserves duplicate values. In [routes/basketItems.ts:21](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/basketItems.ts:21>), the add handler parses the raw body, checks the first BasketId at line 37, then selects the later value for the insert at lines 40–43. The conventional parser's value is also used by the earlier quantity middleware.

A logged-in caller can provide their own basket ID first and another user's ID second in one JSON object. Authorization succeeds on the first while the inserted item belongs to the second. This is distinct from missing owner checks in WSA-006: the checked value and the used value differ.

**Fix:** parse once into a validated DTO, reject duplicate property names if ambiguity matters, and derive BasketId from the caller. **Regression:** duplicate BasketId bodies must be rejected; first/last ordering must never change ownership; a single legitimate ID still inserts into the caller's basket. Reference: [Security topic](https://portswigger.net/web-security/api-testing).

### WSA-008 — Review authors and update targets are controlled by the caller

**Medium · Confirmed · source-proven.** [server.ts:653](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:653>) exposes review creation without authentication. [routes/createProductReviews.ts:23](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/createProductReviews.ts:23>) persists request author/message. Authenticated PATCH at [server.ts:654](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:654>) reaches [routes/updateProductReviews.ts:16](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/updateProductReviews.ts:16>), which queries only `_id: req.body.id` and performs a multi-update without an author predicate. A customer can change another review, and an anonymous caller can forge reviews under another email. Non-scalar IDs also reach the database selector; broad operator-based updates are a supported extension pending exact MarsDB behavior, not needed to prove unowned single-ID updates.

**Fix:** require a principal, derive author from a stable subject, validate scalar IDs and use `{_id, authorId}` with one-row updates. **Regression:** anonymous author spoofing, A editing B's ID, and object/operator IDs fail; own-review edits succeed. Verify no more than one row changes. Reference: [Security topic](https://portswigger.net/web-security/nosql-injection).

### WSA-009 — Redacted email is used as an authorization key

**High · Confirmed · source-proven.** Orders store email after replacing every vowel with `*` ([routes/order.ts:170](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:170>)). [routes/orderHistory.ts:15](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/orderHistory.ts:15>) and [routes/dataExport.ts:22](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/dataExport.ts:22>) apply the same lossy transform to the current user's email and query orders by that value ([routes/dataExport.ts:33](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/dataExport.ts:33>)). The chat tool uses the same comparison ([routes/chat.ts:164](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/chat.ts:164>)). Registration does not require proving control of the email address.

Different accounts, for example synthetic `alice@example.test` and `elice@example.test`, map to the same stored value. A colliding account can see/export the other's orders through the ordinary authenticated endpoints. This is a cross-account boundary failure, not merely weakened anonymization.

**Fix:** store an immutable user ID on orders and authorize with it; keep redaction exclusively for display. Migrate existing records with an unambiguous owner mapping. **Regression:** two distinct emails with identical masked forms must see only their own orders in history, export and chat; renaming an email must not transfer ownership. Reference: [Security topic](https://portswigger.net/web-security/access-control).

### WSA-010 — Full User objects expose password hashes and MFA secrets

**High · Confirmed · source-proven.** Public memories GET ([server.ts:650](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:650>)) executes `MemoryModel.findAll({include: UserModel})` in [routes/memory.ts:23](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/memory.ts:23>). User has no default exclusion scope ([models/user.ts:119](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/user.ts:119>)); the generated API's response exclusions at [server.ts:505](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:505>) do not apply to this association. It can therefore serialize password hashes and TOTP secrets of memory contributors to an unauthenticated reader.

[routes/login.ts:18](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/login.ts:18>) and [routes/2fa.ts:33](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/2fa.ts:33>) / line 42 also sign full user objects into readable JWT payloads. JWT signing does not encrypt them. [routes/currentUser.ts:27](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/currentUser.ts:27>) accepts caller-selected fields from its cached full user, and password/IP update responses return the full model ([routes/changePassword.ts:56](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/changePassword.ts:56>), [routes/resetPassword.ts:46](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/resetPassword.ts:46>), [routes/saveLoginIp.ts:33](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/saveLoginIp.ts:33>)). Those authenticated/self responses are secondary exposure paths, not a claim they disclose arbitrary other users by themselves. Weak hashes compound WSA-014.

**Fix:** explicit public DTOs and model default scopes; token claims only subject/session metadata and strictly necessary authorization claims; never serialize hashes, recovery secrets or TOTP seeds. Rotate exposed TOTP seeds and invalidate affected sessions. **Regression:** recursively inspect public memories, tokens, whoami selections and mutation responses for sensitive fields, including users with MFA enabled; expected public fields remain available. Reference: [Security topic](https://portswigger.net/web-security/information-disclosure).

### WSA-011 — Browser OAuth flow creates a predictable local password

**High · Confirmed · source-proven.** [frontend/src/app/oauth/oauth.component.ts:31](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/oauth/oauth.component.ts:31>) derives a password as Base64 of reversed email, registers at line 32 and logs in with it at line 47. The OAuth flag is not a server-side identity proof; [routes/login.ts:33](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/login.ts:33>) still authenticates by local email/password. Provider userinfo is fetched by the browser rather than verified and bound by the backend ([frontend/src/app/Services/user.service.ts:68](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/Services/user.service.ts:68>)).

Anyone knowing an OAuth-created account's email can compute its local password and use the normal login endpoint. A subsequently enabled TOTP factor remains a barrier; this does not assert MFA bypass for every such account. OAuth client IDs are public identifiers and are not reported as secrets.

**Fix:** perform a server-verified authorization-code/PKCE flow; bind verified issuer/subject to a user; do not create a deterministic local password. Disable or randomize existing derived credentials and require verified enrollment for a separate password. **Regression:** knowledge of email alone cannot log in; invalid provider proof and mismatched issuer/audience/redirect fail; legitimate provider login and MFA succeed. Reference: [Security topic](https://portswigger.net/web-security/oauth).

### WSA-012 — Recovery answers are publicly returned and can be planted for unconfigured users

**High · Confirmed · source-proven.** [routes/appConfiguration.ts:11](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/appConfiguration.ts:11>) returns the entire configuration after removing only the LLM API URL. It therefore includes recovery answers declared in [config/default.yml:1053](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/config/default.yml:1053>) and line 1058. [data/datacreator.ts:348](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/data/datacreator.ts:348>) uses those values to create corresponding security answers. [routes/resetPassword.ts:35](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/resetPassword.ts:35>) accepts email plus matching answer as sufficient authority to change the password, with no email-delivered one-use proof or MFA check. Actual secret values are omitted here.

Separately, public `POST /api/SecurityAnswers` ([server.ts:418](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:418>) and resource line 513) does not bind UserId to a principal. [models/securityAnswer.ts:29](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/securityAnswer.ts:29>) makes UserId unique: an attacker can plant an answer for a victim with no existing answer, but this path does **not** overwrite an existing unique answer. Both paths allow unauthorized credential reset within their stated account populations.

**Fix:** expose an explicit public configuration DTO; remove knowledge-question recovery in favor of short-lived single-use verified recovery tokens; bind any enrollment to a recently authenticated account. **Regression:** configuration contains no recovery material; A cannot enroll recovery for B; accounts with no answer and with an existing answer both resist foreign enrollment; reset requires a fresh one-use proof and revokes old sessions. Reference: [Security topic](https://portswigger.net/web-security/authentication/other-mechanisms).

### WSA-013 — Password change omits mandatory current-password verification and logs secrets in URLs

**High · Confirmed · source-proven.** `GET /rest/user/change-password` is registered at [server.ts:617](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:617>). [routes/changePassword.ts:13](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/changePassword.ts:13>) reads current/new/repeat from the query; line 39 checks current password only if it is truthy, then line 51 changes the password for the cached bearer identity. A stolen valid session can turn into lasting credential takeover without knowing the current password. This is not an unauthenticated reset or proof that ordinary cross-site forms can set a bearer header.

Combined access logging records the full request URL ([server.ts:356](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:356>)), and `/support/logs` is public ([server.ts:301](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:301>)). Consequently password values used by this flow can enter publicly accessible logs. The report does not claim any particular live password was present in a log; no logs were opened.

**Fix:** use POST with a body, require current password or fresh step-up proof, redact secrets in logs, remove public log serving and revoke previous sessions. **Regression:** omitted/empty/wrong current passwords fail, valid changes work, old tokens stop working, and request/error logs never contain new/current passwords. Reference: [Security topic](https://portswigger.net/web-security/authentication/other-mechanisms).

### WSA-014 — Fast unsalted password hashing and a shared recovery-answer key

**Medium · Confirmed · source-proven.** [lib/insecurity.ts:41](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:41>) uses unsalted MD5, and [models/user.ts:70](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/user.ts:70>) applies it as the password setter. Equal passwords yield equal values and offline guessing has no adaptive work factor. Recovery answers use a source-embedded fixed HMAC key ([lib/insecurity.ts:42](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:42>), [models/securityAnswer.ts:42](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/securityAnswer.ts:42>)); this is not equivalent to protecting low-entropy answers with an independent secret. WSA-001/010 give realistic hash-disclosure paths. No hash cracking was performed.

**Fix:** use an established memory-hard password hash with unique salts and cost settings, migrate on login/reset, and replace knowledge-answer recovery. **Regression:** equal passwords produce different stored hashes, correct/incorrect password verification works, legacy hashes migrate safely, and no plaintext/hash appears in output DTOs. Reference: [Security topic](https://portswigger.net/web-security/authentication/password-based).

### WSA-015 — Cached sessions outlive expiry and account security changes

**High · Confirmed · source-proven for cache-only consumers.** Tokens are issued for six hours ([lib/insecurity.ts:54](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:54>)), but the token/user maps at lines 70–91 have no TTL. `updateAuthenticatedUsers` verifies a token only when it is absent from the cache (line 184). `appendUserId` and `authenticatedUsers.from/get` trust cached entries without rechecking expiry or live account state. `security.verify` at line 55 performs a JWS signature check, not JWT expiry validation; accounting/deluxe/customer role helpers reuse it at lines 152–170.

Thus cache-only routes such as profile, password change, owner-scoped address/card/wallet helpers can continue accepting a previously cached expired credential. Password change/reset, logout (browser deletion only), and MFA changes do not revoke all tokens. Routes that independently run `expressJwt` may still reject expired tokens; the finding is not a universal bypass of that middleware. `isActive` is declared at [models/user.ts:113](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/user.ts:113>) but no enforcement was found; operational account-disable semantics were not supplied, so that is a control gap rather than a separately demonstrated disable bypass.

**Fix:** central validation on every authenticated request with expiry, purpose and current session/account state; bounded session storage; revoke/rotate on logout, password and MFA changes. **Regression:** after advancing time, changing credentials, disabling an account or logging out, replay against both JWT-middleware and cache-only endpoints fails; current sessions still work. Reference: [Security topic](https://portswigger.net/web-security/jwt).

### WSA-016 — MFA and session tokens share an acceptance domain

**High · Confirmed · source-proven partial MFA bypass.** Login issues a signed `password_valid_needs_second_factor_token` after password verification ([routes/login.ts:36](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/login.ts:36>)). [lib/insecurity.ts:52](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:52>) validates only the signature/standard JWT checks without requiring a session purpose, issuer, audience or completed MFA. Generated API gates such as Users, Complaints and Products use this middleware without requiring cached `data.id` ([server.ts:386](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:386>), line 404 and line 392). A person knowing an MFA user's password can therefore use the temporary token for these operations before providing TOTP. Cache-dependent handlers may reject its different payload, so full session equivalence is not claimed.

The `/rest/2fa/verify` handler itself checks token type and TOTP ([routes/2fa.ts:20](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/2fa.ts:20>)–31), but uses signature-only `security.verify`, accepting cryptographically valid expired temporary tokens. Setup tokens contain a secret and type without subject binding (line 73), and setup verifies the signature but not expiry (line 115). Password checking limits setup abuse; this is not an independent passwordless MFA takeover claim.

**Fix:** separate token types and validation functions/keys or require explicit purpose/audience and subject claims everywhere. Bind short-lived single-use MFA/setup transactions to the user and initiating session. **Regression:** temporary/setup tokens fail all session APIs; expired/replayed/wrong-user tokens fail MFA setup/verification; a fresh successful second factor issues a proper session token. Reference: [Security topic](https://portswigger.net/web-security/authentication/multi-factor).

### WSA-017 — Stored username is evaluated as server-side JavaScript

**Critical · Supported · source-proven interpreter path, challenge gate unresolved.** A logged-in user can update their username through `POST /profile` ([server.ts:687](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:687>), [routes/updateUserProfile.ts:38](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/updateUserProfile.ts:38>)). `GET /profile` retrieves it from the database, recognizes `#{...}`, and directly executes the extracted expression with `eval` in the Node module at [routes/userProfile.ts:57](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/userProfile.ts:57>)–65 before compiling the Pug template at line 90. Username HTML sanitization does not make a JavaScript expression safe.

If `challenge137` is enabled, this is execution of attacker-controlled JavaScript with the server process's authority, not just browser HTML injection. File/network/process effects depend on deployed permissions; no command or escape payload was run. [lib/utils.ts:153](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/utils.ts:153>) applies environment/safety-mode gates, and the effective deployment gate was not established. [config/unsafe.yml:2](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/config/unsafe.yml:2>) explicitly disables safety mode.

**Fix:** remove eval and user-controlled template-source substitution; use a fixed template with escaped locals. **Regression:** a synthetic arithmetic interpolation marker must be displayed literally rather than evaluated; verify the same for template syntax, while ordinary profile names render correctly. Check all safety-mode variants. Reference: [Security topic](https://portswigger.net/web-security/server-side-template-injection).

### WSA-018 — NoSQL filters contain attacker-built JavaScript expressions

**High · Supported · source-proven query construction, gated engine behavior unexecuted.** Public review retrieval ([server.ts:652](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:652>)) concatenates a route ID into `$where` in [routes/showProductReviews.ts:36](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/showProductReviews.ts:36>); truncating it to 40 characters does not bind it as a value. Public order tracking ([server.ts:637](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:637>)) interpolates the supplied ID into a quoted `$where` expression in [routes/trackOrder.ts:18](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/trackOrder.ts:18>), with a 60-character limit. These gated branches allow filter-expression manipulation rather than exact product/order matching. [routes/showProductReviews.ts:17](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/showProductReviews.ts:17>) also exposes a busy-wait helper with a per-call bound of two seconds.

Expected: scalar equality. Supported impact: disclosure of other matching orders/reviews and repeated interpreter work when the relevant challenges are enabled and MarsDB evaluates `$where`. This review does not claim MongoDB-server vulnerabilities, unrestricted host execution, or a sandbox escape: the store is in-process MarsDB ([data/mongodb.ts:9](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/data/mongodb.ts:9>)) and implementation/runtime was not available. The LLM review tool converts its product ID with `Number` ([routes/chat.ts:147](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/chat.ts:147>)), so it is not the same raw-string injection path.

**Fix:** eliminate `$where`; use typed scalar selectors and strict identifier schemas. **Regression:** quotation/operators/expression fragments return no unintended records or are rejected; legitimate IDs return their exact records; request handling never evaluates supplied code. Reference: [Security topic](https://portswigger.net/web-security/nosql-injection).

### WSA-019 — XML upload enables external entity filesystem reads

**High · Supported · source-proven unsafe parser setup, challenge gate/runtime library unresolved.** Unauthenticated `/file-upload` ([server.ts:335](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:335>)) accepts XML by filename. When `challenge026` is enabled, [routes/fileUpload.ts:77](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileUpload.ts:77>) calls `parseXmlString`; [lib/xml.ts:22](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/xml.ts:22>) grants host filesystem providers and line 35 enables `XML_PARSE_NOENT` and `XML_PARSE_DTDLOAD`. Expanded XML is serialized and up to 400 characters are included in the error response ([routes/fileUpload.ts:83](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileUpload.ts:83>), global [server.ts:702](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:702>) error handler).

A local-file external entity can disclose files readable by the process within the returned excerpt. The VM timeout is an availability bound, not a filesystem authorization control. Environment gating is material; this review does not claim network entity retrieval or actual host files read.

**Fix:** prohibit DTD/external entity loading, remove filesystem providers, use a constrained parser and avoid returning input/parser contents in errors. **Regression:** with a synthetic fixture file, an external entity must be rejected or remain unexpanded; normal XML works; nested entities cannot monopolize the worker. Run under all configured challenge modes in an isolated test. Reference: [Security topic](https://portswigger.net/web-security/xxe).

### WSA-020 — ZIP containment is checked against the application root, allowing overwrites

**High · Supported · source-proven write path, challenge/permissions prerequisites.** Unauthenticated ZIP uploads reach [routes/fileUpload.ts:27](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileUpload.ts:27>). Entry paths are resolved from `uploads/complaints`, but line 33 tests only whether the result contains the working-directory string. Line 34 writes the original combined path. An entry such as `../../ftp/audit-fixture.md` remains inside the application root while escaping the complaint directory. Existing files can be overwritten because the stream uses the default write mode. The substring test also does not express a proper path-boundary relation.

When `challenge044` is enabled and the destination is writable, an anonymous caller can modify files elsewhere in the app tree, including public content. [routes/videoHandler.ts:71](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/videoHandler.ts:71>) embeds subtitle contents in script text, giving a supported browser-injection extension if an attacker overwrites the configured subtitle file. Server execution through overwritten code is not asserted without a later load/restart path. The compressed upload limit does not bound expanded bytes or entry count.

**Fix:** resolve each entry beneath a dedicated upload root; reject traversal, absolute paths and links; verify containment with path-relative semantics; prevent overwrites; cap expanded size/count and keep files outside served/code directories. **Regression:** synthetic traversal, prefix-collision, absolute, link and oversized archives cannot write outside a temporary upload root; a small valid archive succeeds. Reference: [Security topic](https://portswigger.net/web-security/file-path-traversal).

### WSA-021 — YAML reconstruction and synchronous evaluation expose resource-exhaustion paths

**Medium · Supported · source-proven expensive primitives, limits/library behavior unexecuted.** [routes/fileUpload.ts:109](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileUpload.ts:109>) sends unauthenticated YAML to `yaml.load` and then `JSON.stringify` inside a two-second VM ([routes/fileUpload.ts:114](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileUpload.ts:114>)). The manifest selects legacy js-yaml, but no resolved implementation/advisory validation was performed; unsafe native-type deserialization is a lead, not a claimed RCE. Alias graphs can multiply serialization work despite a small source upload. [routes/b2bOrder.ts:23](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/b2bOrder.ts:23>) similarly evaluates a caller-supplied string with a two-second VM when its challenge is enabled; that endpoint requires a JWT ([server.ts:447](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:447>)). XML parsing in WSA-019 is another synchronous interpreter path.

Impact is bounded individual event-loop stalls and possible memory pressure, repeated without a per-endpoint work budget. The timeout is a useful partial control and precludes describing an unbounded loop as proven. Exact YAML expansion behavior and native-call interruption need isolated library tests.

**Fix:** use safe data-only schemas, limit aliases/depth/expanded size, eliminate B2B expression evaluation, and isolate remaining parsers with strict memory/time/concurrency budgets. **Regression:** small alias/deep-nesting fixtures and bounded computational inputs are rejected quickly without blocking unrelated requests; ordinary data succeeds. Reference: [Security topic](https://portswigger.net/web-security/deserialization).

### WSA-022 — Download handlers reject only forward slashes on a Windows-capable application

**High · Supported · source-proven Windows path mismatch.** [routes/keyServer.ts:13](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/keyServer.ts:13>), [routes/logfileServer.ts:13](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/logfileServer.ts:13>), [routes/quarantineServer.ts:13](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/quarantineServer.ts:13>), and [routes/fileServer.ts:17](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileServer.ts:17>) reject `/` but not `\`, then resolve user names against their nominal roots and send the resulting absolute files. On Windows, a URL-decoded backslash traversal component can escape the intended directory, for example a synthetic `..\config\audit-fixture.yml` relative to a sibling file root. The public registrations are in [server.ts:289](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:289>)–303. The FTP variant also applies an extension check, addressed in WSA-023.

The proof is a platform-specific mismatch between filtering and filesystem semantics; actual Express decoding, proxy normalization, deployment OS and readable-file response were not tested. On POSIX the same backslash is generally a literal character, so this is not asserted as cross-platform traversal. Impact is disclosure of files readable by the application process on an affected Windows deployment.

**Fix:** accept a strict filename identifier or resolve and verify a path-relative containment boundary on the actual platform; reject both separators/absolute paths and use a constrained root. **Regression:** on Windows and POSIX, encoded separators, drive/UNC/absolute paths and parent components cannot escape a temporary fixture root; normal names remain accessible. Reference: [Security topic](https://portswigger.net/web-security/file-path-traversal).

### WSA-023 — Filename allowlisting occurs before application-level null-marker truncation

**Medium · Confirmed · source-proven.** [routes/fileServer.ts:26](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileServer.ts:26>) accepts `.md`/`.pdf`, then calls `cutOffPoisonNullByte` at line 27. [lib/insecurity.ts:44](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:44>) removes a literal `%00` and everything following it; line 32 of the handler opens the altered name. Thus the verified and used names differ. A name shaped as `package.json.bak%00.pdf` passes the suffix check but selects `package.json.bak`. HTTP transport would need to preserve a literal percent marker through decoding (normally percent-encoding the percent); no request was executed. This is explicit application truncation, not a claim that Node accepts an actual NUL in a filesystem path.

Listed FTP backups such as `package.json.bak`, `package-lock.json.bak`, coupon data and diagnostics can become downloadable despite the nominal file policy. The file contents were not opened to extract additional secrets.

**Fix:** remove null-marker truncation; decode/canonicalize once, reject ambiguous names, then validate the exact value sent to the filesystem. **Regression:** literal and encoded null-marker suffix tricks fail, backups remain inaccessible, and approved documents still download. Reference: [Security topic](https://portswigger.net/web-security/file-path-traversal).

### WSA-024 — Public listings expose invoices, logs and internal artifacts

**Medium · Confirmed · source-proven exposure policy; actual generated contents not inspected.** `/ftp`, `/support/logs`, `/encryptionkeys`, and `/infrastructure` are publicly listed/served ([server.ts:269](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:269>), line 289, line 297 and line 301). Checkout writes PDFs into FTP ([routes/order.ts:45](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:45>)), and its server does not check invoice ownership ([routes/fileServer.ts:32](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/fileServer.ts:32>)). The listing removes any need to guess a PDF name. Access logs contain full URLs and activity ([server.ts:356](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:356>)), including the password-change query in WSA-013. Checked-in internal files are present under FTP; only directory names were inspected.

An anonymous reader can access generated invoices and request activity when those files exist, plus published internal files allowed by the extension policy. Startup PDF cleanup ([lib/startup/cleanupFtpFolder.ts:13](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/startup/cleanupFtpFolder.ts:13>)) limits lifetime across restarts, not access between restarts. Private-key compromise is counted in WSA-002; this item concerns broader confidentiality.

**Fix:** move invoices/logs outside public roots; authorize each invoice using its owner, serve explicit public assets only, disable listings and redact request logging. **Regression:** A cannot list/download B's invoice or logs even knowing filenames; A can retrieve their own invoice through the authorized endpoint; public documentation remains available. Reference: [Security topic](https://portswigger.net/web-security/information-disclosure).

### WSA-025 — Profile-image URL fetch has no outbound destination or redirect policy

**High · Confirmed · source-proven unrestricted server-side fetch.** A logged-in cookie user submits `imageUrl`; [routes/profileImageUrlUpload.ts:24](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/profileImageUrlUpload.ts:24>) calls `fetch(url)` without a host/IP allowlist, private-address exclusion, redirect revalidation or request timeout. The successful response is written to a same-origin public file at lines 28–32. The route is registered at [server.ts:337](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:337>).

The server can be induced to contact destinations reachable from its network, and successful response bodies can be retrieved from the resulting upload path. Specific cloud metadata endpoints, internal credentials and non-HTTP schemes are not claimed reachable; actual network topology/fetch behavior was not exercised. Extension selection does not verify the response is an image. Failed fetches store the supplied URL directly at line 36.

**Fix:** prefer uploaded images; otherwise enforce allowed HTTPS origins, validate resolved addresses and each redirect, use a restricted egress service, and set body/time limits before persisting validated image bytes. **Regression:** local/private/link-local, redirect-to-private and slow/oversized fixture responses fail; approved remote image retrieval works. Reference: [Security topic](https://portswigger.net/web-security/ssrf).

### WSA-026 — URL image upload publishes active SVG on the application origin

**High · Supported · source-proven publication, browser policy unverified.** [routes/profileImageUrlUpload.ts:28](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/profileImageUrlUpload.ts:28>) permits an SVG extension based solely on the URL string and writes unvalidated response bytes under `frontend/dist/frontend/assets/public/images/uploads`. [server.ts:315](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:315>) serves that directory on the application origin. An authenticated attacker controlling a remote `.svg` resource can publish an active document and send its public URL to another user. Navigating directly to an SVG differs from rendering it in an `<img>`; the latter does not by itself prove script execution.

Supported impact is same-origin script execution when the served content type and effective browser CSP permit active SVG. The built-in app has no global restrictive CSP; an external proxy policy was not available. The uploaded-file profile route does perform content sniffing ([routes/profileImageFileUpload.ts:23](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/profileImageFileUpload.ts:23>)), so it is not interchangeable with this URL path.

**Fix:** decode and re-encode permitted raster images, reject SVG/HTML, serve user content from an isolated origin with restrictive policy and response types. **Regression:** active SVG/HTML disguised as images cannot execute on the application origin; valid raster avatars still display. Reference: [Security topic](https://portswigger.net/web-security/file-upload).

### WSA-027 — Memory-image uploads write unbounded data before authentication

**Medium · Confirmed · source-proven.** [server.ts:338](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:338>) runs `uploadToDisk.single('image')` before `appendUserId`. Disk-upload configuration at [server.ts:720](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:720>)–739 checks only the client-supplied MIME type for PNG/JPEG and has no file-size limit. It stores timestamped files in a publicly served uploads directory. A later authentication rejection does not remove the file already written.

Anonymous requests can consume disk space and create purported image files, even if no memory record is created. The separate in-memory complaint uploader has a 200,000-byte limit ([server.ts:714](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:714>)); that control does not cover this disk uploader. Claimed impact is storage/availability and unauthorized file placement, not automatic script execution from a `.png` extension with no-sniff enabled.

**Fix:** authenticate before processing the body, enforce byte/count quotas and content decoding, store in temporary nonpublic space and clean up on failure. **Regression:** anonymous, oversized and invalid-content uploads create no residual files; valid authenticated small images create exactly one expected file. Reference: [Security topic](https://portswigger.net/web-security/file-upload).

### WSA-028 — Data-erasure body is spread into template-engine options

**High · Supported · source-proven option injection, layout resolution unverified.** Authenticated `POST /dataerasure` passes `...req.body` to `res.render` in [routes/dataErasure.ts:107](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/dataErasure.ts:107>) and line 123. Caller `layout` is therefore a rendering option, not just display data. The gated branch resolves a path and excludes a few substrings at lines 103–105, returning the first 100 rendered characters; the other branch still spreads the body, so disabling this challenge does not remove option injection. The field interface declaring email/securityAnswer is a compile-time type only.

If the configured Handlebars engine resolves attacker-selected layouts as expected, readable local templates/files can be disclosed through the rendered response. Engine implementation/build configuration was not available, so unrestricted arbitrary file read or execution is not claimed confirmed. There is no path allowlist rooted in a trusted template directory.

**Fix:** pass an explicit DTO and constant layout; never spread request data into engine options; remove file-path selection from the request. **Regression:** layout/view/engine option names and parent/absolute paths cannot affect template choice or reveal a synthetic fixture; ordinary erasure result rendering succeeds. Reference: [Security topic](https://portswigger.net/web-security/server-side-template-injection).

### WSA-029 — Angular trust bypasses render attacker-controlled HTML

**High · Supported · source-proven HTML sinks, effective browser policy unverified.** Several paths explicitly bypass Angular's HTML sanitizer:

| Input and prerequisite | Source-to-sink trace |
| --- | --- |
| Crafted search link | [frontend/src/app/search-result/search-result.component.ts:136](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/search-result/search-result.component.ts:136>) reads route `q`; line 143 trusts it as HTML; corresponding HTML line 11 inserts it. |
| Crafted tracking link | [routes/trackOrder.ts:15](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/trackOrder.ts:15>) retains HTML when challenge105 is enabled and line 22 echoes an unmatched order ID. [frontend/src/app/track-result/track-result.component.ts:49](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/track-result/track-result.component.ts:49>) trusts that returned ID; [frontend/src/app/track-result/track-result.component.html:9](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/track-result/track-result.component.html:9>) inserts it. The service URL-encodes the request segment, preventing path traversal but not HTML rendering after the response. |
| Anonymous product modification | Unprotected Product PUT (WSA-004) reaches the description setter in [models/product.ts:51](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/product.ts:51>); when `challenge113` is enabled it stores raw description. [frontend/src/app/search-result/search-result.component.ts:112](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/search-result/search-result.component.ts:112>) trusts it; [frontend/src/app/product-details/product-details.component.html:18](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/product-details/product-details.component.html:18>) inserts it. |
| Attacker registration viewed by an administrator | [models/user.ts:56](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/user.ts:56>) allows raw email when `challenge096` is enabled. Authentication-details returns it; [frontend/src/app/administration/administration.component.ts:74](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/administration/administration.component.ts:74>) trusts email, and HTML line 26/113 renders it. There is no server email-format validator to make the value inherently inert. |
| Own stored last-login header | [routes/saveLoginIp.ts:18](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/saveLoginIp.ts:18>) accepts `true-client-ip`; [frontend/src/app/last-login-ip/last-login-ip.component.ts:40](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/last-login-ip/last-login-ip.component.ts:40>) trusts the stored value and HTML line 10 renders it. This is limited to the affected account unless another route or session compromise lets an attacker write its header. |

These permit HTML injection; script execution/account actions require a victim reaching the view and a permissive effective browser policy. The application does not set a global restrictive CSP, but deployment/browser execution was excluded. Sanitized feedback also reaches trust-bypass sites; an exact sanitizer bypass was not established and is not included as a confirmed input path.

**Fix:** remove bypassSecurityTrustHtml for untrusted strings, render identifiers/search as text, and use a maintained narrowly configured sanitizer only for intended rich product descriptions. Restrict product writes and use a fixed CSP as defense in depth. **Regression:** synthetic event-handler/HTML payloads from each input render inertly; valid text and approved rich content still render; verify in a browser under the intended CSP. Reference: [Security topic](https://portswigger.net/web-security/cross-site-scripting/dom-based).

### WSA-030 — Data export writes attacker-authored review data into a same-origin document

**High · Supported · source-proven HTML construction, browser execution unverified.** An unauthenticated caller can create a review with the victim's email as author (WSA-008). [routes/dataExport.ts:40](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/dataExport.ts:40>) selects those reviews; lines 89–108 put the message into a JSON string. [frontend/src/app/data-export/data-export.component.ts:72](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/data-export/data-export.component.ts:72>) writes the returned string using `document.write` in a new window. JSON stringification is not HTML escaping: an HTML element/script without JSON-special characters remains HTML in the document parser.

A victim exporting their own data can therefore render attacker-controlled markup in a same-origin window. Exact script execution depends on popup behavior and effective CSP; no browser test was performed. This chain does not require the victim to create the malicious review or an attacker to control the export response wholesale.

**Fix:** export a JSON Blob/download with an appropriate content type, or insert the string into a text node; fix review author attribution. **Regression:** a forged review containing synthetic HTML remains literal text in exports and cannot execute; a valid JSON export retains all fields and encoding. Reference: [Security topic](https://portswigger.net/web-security/cross-site-scripting/dom-based).

### WSA-031 — Cookie-authenticated profile and erasure mutations lack CSRF enforcement

**Medium · Supported · source-proven missing control, browser cookie prerequisite.** [routes/updateUserProfile.ts:17](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/updateUserProfile.ts:17>), [routes/profileImageUrlUpload.ts:21](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/profileImageUrlUpload.ts:21>), and [routes/dataErasure.ts:76](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/dataErasure.ts:76>) authorize by `req.cookies.token` and accept state-changing POSTs without an anti-CSRF token or Origin/Referer policy. URL-encoded bodies are enabled ([server.ts:333](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:333>)). Cookie writes ([lib/insecurity.ts:190](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:190>), [routes/updateUserProfile.ts:42](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/updateUserProfile.ts:42>)) do not explicitly set HttpOnly/Secure/SameSite. The erasure handler ignores submitted email/securityAnswer when creating a deletion request at [routes/dataErasure.ts:83](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/dataErasure.ts:83>).

A cross-origin request that carries this cookie can change profile data or submit an erasure request. Browser-default SameSite restrictions can prevent some cross-site POSTs; same-site hostile origins and browser/configuration differences remain material prerequisites. The erasure handler creates a request and clears a cookie—it does not directly delete the account. Bearer-only endpoints are not automatically vulnerable to form CSRF.

**Fix:** require CSRF proof and validate request origin for cookie-authenticated mutations; explicitly set suitable cookie flags; require fresh identity confirmation for erasure requests. **Regression:** foreign-origin and missing/invalid-CSRF form submissions fail even when cookies are present; legitimate same-origin operations succeed. Reference: [Security topic](https://portswigger.net/web-security/csrf).

### WSA-032 — Negative quantities invert inventory and wallet arithmetic

**High · Confirmed · source-proven application-economy manipulation.** [models/basketitem.ts:39](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/basketitem.ts:39>) defines integer quantity without a positive minimum. [routes/basketItems.ts:94](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/basketItems.ts:94>) checks upper stock/per-user limits but not positivity; the update guard is also conditional on a truthy quantity. Checkout subtracts quantity from inventory ([routes/order.ts:80](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:80>)), multiplies price by it (line 93), and decrements wallet by the resulting total at line 150.

A customer can submit a negative quantity so inventory increases and sufficiently negative totals pass a wallet balance check and credit funds through a negative decrement. Delivery fees/coupons affect the exact total, so a small negative quantity is not assumed always sufficient. Client-side guest-basket minimums are not a server control. Impact is the shop's simulated balances/order integrity, not verified real-money loss.

**Fix:** validate bounded positive integer quantities at the server and database; compute totals from authoritative prices and reject nonfinite/negative amounts before any mutation. **Regression:** zero, negative, fractional and excessive quantities cannot reach checkout or alter stock/wallet; valid purchases deduct the exact nonnegative total. Reference: [Security topic](https://portswigger.net/web-security/logic-flaws).

### WSA-033 — Payment-mode branches fail open and wallet credits trust requested amounts

**Medium · Confirmed · source-proven simulated payment bypass.** [routes/deluxe.ts:24](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/deluxe.ts:24>) validates wallet mode and line 34 validates card mode, but all other/missing values skip both and reach the role upgrade at line 43. [routes/order.ts:147](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:147>) debits only when paymentId is exactly `wallet`; missing/arbitrary values still reach bonus credit at line 157 and order insertion at line 164. [routes/wallet.ts:24](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/wallet.ts:24>) checks ownership/existence of a card, then increments balance by caller `balance` at line 27 without a successful payment record or bounded positive amount.

An ordinary user can gain deluxe status or create orders/credits without the modeled payment prerequisite. This educational application does not contain an established external payment settlement integration; no actual card charge, theft or processor exploit is claimed. The owned-card lookup is a positive authorization control but is not payment confirmation.

**Fix:** validate an exhaustive payment-method enum, reject unknown/missing modes, bind an authoritative successful payment/ledger entry to each credit/upgrade/order, and validate amounts. **Regression:** unknown/missing modes and arbitrary top-up values do not change balances/roles/orders; legitimate funded wallet/card workflows apply exactly once. Reference: [Security topic](https://portswigger.net/web-security/logic-flaws).

### WSA-034 — Coupons are forgeable encodings and campaign dates are supplied by clients

**Medium · Confirmed · source-proven.** [lib/insecurity.ts:97](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:97>) encodes month/year and discount using Z85; decoding at lines 103–118 checks format but no MAC/signature, issuance record, recipient or one-use state. The regex is not a bounded numeric-policy check. Anyone who knows the format can mint a current-month discount; encoding provides no authenticity. [routes/order.ts:195](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:195>) decodes legacy couponData and compares its client-provided timestamp with a campaign timestamp at line 201 rather than the server's current time, so old campaigns remain usable with their old date.

Impact is unauthorized discounts in the simulated checkout, potentially compounding negative totals. No brute-force coupon discovery or runtime transaction was attempted.

**Fix:** use unguessable server-stored coupon records or authenticated claims with server-checked validity, maximum discount, owner and redemption count; use current server time for expiry. **Regression:** modified/unsigned/high-discount coupons, expired campaign timestamps and replays fail; an issued in-policy coupon works once for its intended subject. Reference: [Security topic](https://portswigger.net/web-security/logic-flaws).

### WSA-035 — Checkout and review-like checks are not atomic

**Medium · Supported · source-proven interleavings, concurrency unexecuted.** Checkout reads inventory and later writes a derived amount ([routes/order.ts:78](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:78>)–81); it separately reads wallet balance then decrements it ([routes/order.ts:148](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/order.ts:148>)–150). Stock effects and opening the PDF stream precede possible payment rejection. Basket deletion occurs on the PDF writer finish event, so it is not claimed to precede every payment failure. There is no transaction wrapping the sequence across SQLite, MarsDB and PDF output. An IMMEDIATE transaction default in model setup does not itself create a transaction around these operations.

[routes/likeProductReviews.ts:25](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/likeProductReviews.ts:25>) reads likedBy, checks inclusion at line 31, increments likes at line 35, sleeps 150 ms at line 41, then reads/pushes/updates again. Concurrent requests from one account can both pass the check. Supported effects are overspending/lost inventory updates, partial failed orders and duplicate likes; exact schedules were not executed.

**Fix:** conditional atomic balance/stock updates and an idempotent order state machine with compensation for cross-store/file effects; enforce one like per `(review,user)` in storage. **Regression:** barrier-synchronized requests against synthetic accounts never overspend, oversell or duplicate rewards/likes; injected payment failure preserves basket/stock/balance or produces an explicit recoverable state. Reference: [Security topic](https://portswigger.net/web-security/race-conditions).

### WSA-036 — CAPTCHA answers are exposed and challenges are reusable or optional

**Low · Confirmed · source-proven anti-automation failure.** [routes/captcha.ts:24](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/captcha.ts:24>)–31 returns the expected answer alongside the challenge; verification at lines 37–39 does not consume it or bind it to a session. [routes/imageCaptcha.ts:31](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/imageCaptcha.ts:31>) also returns its answer, and verification at line 52 proceeds when no recent CAPTCHA record exists for the user; when a recent record exists, its answer must match. The latter protects data export ([server.ts:640](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:640>)), not an authorization boundary.

Automation can read/reuse answers or avoid requesting an image challenge before export (or wait until its five-minute record window expires). The consequence is bypass of the intended human check, not a separate account-authentication bypass. Other endpoint identity requirements remain.

**Fix:** do not return answers; store short-lived one-use session-bound challenges and fail closed when required fields are missing; use rate limits independently. **Regression:** answers are absent from API responses; omitted, expired, wrong-session and reused challenges fail; one valid response succeeds once. Reference: [Security topic](https://portswigger.net/web-security/authentication/password-based).

### WSA-037 — Authentication throttling is incomplete and trusts forwarded client identity

**Medium · Supported · source-proven limiter design, edge behavior unresolved.** Login at [server.ts:616](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:616>) has no rate limiter. Reset has a 100-per-five-minute limiter ([server.ts:368](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:368>)), and MFA endpoints also have limits, but the server globally enables `trust proxy` ([server.ts:367](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:367>)). The reset key function tries an uppercase header name then falls back to `req.ip`; normal Node headers are lowercase. Without a correctly configured sanitizing edge, caller-chosen forwarding information can vary the apparent client IP and defeat per-IP limits. No per-account budget was found.

This supports online guessing/resource abuse, especially for weak knowledge answers and short OTPs. Effective ingress normalization and reachable IP behavior were not tested; this does not assert arbitrary browser header control or a successful guessed credential.

**Fix:** trust only known proxy hops/networks, strip untrusted forwarding headers at ingress, and combine per-account and per-source throttling with recovery/OTP attempt budgets. **Regression:** changing forwarding headers at an untrusted ingress cannot reset limits; distributed attempts against one synthetic account are bounded; legitimate recovery and login remain usable. Reference: [Security topic](https://portswigger.net/web-security/authentication/password-based).

### WSA-038 — LLM order tool derives identity from an unverified JWT payload

**High · Supported · source-proven identity flaw, tool invocation unverified.** `/rest/chat` is public ([server.ts:658](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:658>)). [routes/chat.ts:42](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/chat.ts:42>) calls `security.decode` without verifying the signature, expiry or session. `getOrderById` at line 157 uses that ID to fetch a user's email and compares the order against the victim's masked email at lines 161–168. This owner check therefore compares against an attacker-selected principal.

A caller can present a syntactically decodable token naming another user and request their known order ID. If the configured model invokes the tool, its return value contains that order. LLM availability/tool selection is a material assumption, so no end-to-end disclosure is claimed reproduced. WSA-009 additionally weakens the masked-email comparison even for a valid identity.

**Fix:** authenticate before constructing tools, pass an immutable validated principal to tool execution, and query by stable owner ID. Never let model input or token decode establish authority. **Regression:** invalid/unsigned/expired tokens and A requesting B's order fail at the tool boundary even when a deterministic model stub calls the tool; A's own order succeeds. Reference: [Security topic](https://portswigger.net/web-security/llm-attacks).

### WSA-039 — Coupon tool enforces business policy only in the prompt

**Medium · Supported · source-proven missing tool policy, model behavior unverified.** [routes/chat.ts:97](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/chat.ts:97>) describes damaged-order proof, rejection of a return and maximum discount in the system prompt. The executable schema at line 177 is only `z.number()`—the word “maximum” is descriptive text. The tool at lines 179–183 generates a coupon without checking the order, user eligibility, numeric bound or one-use state. Client message arrays are accepted directly (line 189), attacker-chosen usernames are interpolated into the system prompt (line 82), and untrusted reviews are retrieved as model context.

Prompt manipulation or an ordinary model error can therefore cause a financially meaningful tool action outside policy. Actual model compliance was not tested; leaking a prompt alone is not treated as a confidentiality exploit. The coupon mechanism is already forgeable independently (WSA-034).

**Fix:** encode policy in tool-side checks and bounded schemas; require a verified owned order and server-maintained eligibility/redemption state, and treat messages/reviews as data. **Regression:** a deterministic model stub requesting excessive discounts or fabricated damage is denied by code; a verified eligible customer receives only the authorized one-use amount. Reference: [Security topic](https://portswigger.net/web-security/llm-attacks).

### WSA-040 — Anonymous chat lacks per-user work and provider-spend budgets

**Medium · Supported · source-proven unmetered entry, provider effects unverified.** [server.ts:658](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:658>) exposes chat without auth/rate middleware. [routes/chat.ts:189](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/chat.ts:189>) accepts client message history and line 201 submits it to a provider using the server's key ([routes/chat.ts:109](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/chat.ts:109>)). Ten steps at line 207 and the global request-body parser are partial bounds, but there is no explicit output-token cap, per-user quota, concurrency budget or disconnect cancellation in the handler.

Repeated anonymous requests can consume the configured local model's resources or a remote provider's quota/cost. A provider/model must be configured and reachable; this source-only review made no provider calls or cost measurement.

**Fix:** authenticate or tightly budget anonymous usage; cap messages/input/output tokens, tools, duration and concurrency; cancel work on disconnect and apply server-side spend limits. **Regression:** bounded synthetic/model-stub requests cannot exceed quotas, disconnects cancel generation, and ordinary short conversations complete. Reference: [Security topic](https://portswigger.net/web-security/llm-attacks).

### WSA-041 — Chat history persists across account logout in shared browser storage

**Medium · Confirmed · source-proven local privacy boundary.** [frontend/src/app/Services/conversation-storage.service.ts:9](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/Services/conversation-storage.service.ts:9>) uses one browser-local key; getAll at line 26 and save at line 44 do not namespace by account. Logout clears token and basket state but not conversations ([frontend/src/app/navbar/navbar.component.ts:241](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/navbar/navbar.component.ts:241>), [frontend/src/app/sidenav/sidenav.component.ts:94](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/sidenav/sidenav.component.ts:94>)). [frontend/src/app/chatbot/chat-welcome-screen/chat-welcome-screen.component.ts:38](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/chatbot/chat-welcome-screen/chat-welcome-screen.component.ts:38>) displays all stored conversations to the next visitor.

A subsequent user of the same browser profile can read the previous user's conversation content, potentially including returned order data. This is local shared-device exposure, not remote access to another browser. Manual delete-all exists but is not invoked on logout.

**Fix:** clear sensitive conversation state on logout/account switch, or store it behind authenticated per-user access with an explicit persistence choice. **Regression:** A's conversation is unavailable after logout and B login; B's new history remains scoped; manual deletion works. Reference: [Security topic](https://portswigger.net/web-security/information-disclosure).

### WSA-042 — Redirect allowlist checks for a trusted substring

**Low · Confirmed · source-proven.** [routes/redirect.ts:18](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/redirect.ts:18>) redirects the `to` query value after [lib/insecurity.ts:132](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:132>) accepts any string containing a trusted URL. A URL such as `https://attacker.example.test/?next=<trusted-url>` satisfies that condition while its actual origin is attacker-controlled. No OAuth-token theft chain is established; the bounded impact is an application-origin redirect useful for deceptive navigation.

**Fix:** parse URLs and compare normalized scheme/host/port against exact permitted origins, or use server-side destination identifiers and relative paths. **Regression:** trusted URLs buried in path/query/userinfo and lookalike hosts fail; exact intended destinations pass. Reference: [Security topic](https://portswigger.net/web-security/dom-based/open-redirection).

### WSA-043 — Supplied load-balancer configuration forwards HTTP instead of redirecting it

**High · Supported · source-proven configuration, deployment use unverified.** [terraform/networking.tf:157](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/terraform/networking.tf:157>) configures the port-80 listener to forward to the application target group; HTTPS is a separate listener at line 183. The infrastructure copy follows the same pattern. Application cookies are not explicitly Secure ([lib/insecurity.ts:190](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/insecurity.ts:190>)), and the SPA sends credentials/tokens over the selected host protocol.

If deployed as supplied and a user enters via HTTP, credentials and authenticated traffic can traverse a cleartext client-to-load-balancer connection. The existence of HTTPS does not force its use. Actual deployment, DNS, HSTS at another edge and user navigation were not inspected; no traffic interception occurred.

**Fix:** redirect HTTP to HTTPS before application processing, issue only Secure cookies, and apply an appropriate HSTS policy once HTTPS coverage is established. **Regression:** HTTP requests never process credentials or mutations and redirect to the correct HTTPS origin; HTTPS sessions work with explicit cookie flags. Reference: [Security topic](https://portswigger.net/web-security/authentication).


### WSA-044 — Sensitive whoami fields can be returned as JSONP

**High · Supported · source-proven cross-origin script response, cookie delivery unverified.** [routes/currentUser.ts:17](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/currentUser.ts:17>) authenticates a token cookie and lines 27–32 copy arbitrary requested fields from the full cached user. When `callback` is present, lines 54–58 return the object as JSONP. A hostile origin can request a script response with selected sensitive fields and a callback it controls; JSONP is executable script rather than a CORS-protected JSON fetch.

If the victim's token cookie is sent on that cross-origin script request, the response can expose fields such as the password hash and TOTP seed already identified in WSA-010. Modern SameSite restrictions may block cross-site cookie delivery; same-site hostile origins or other cookie policies remain prerequisites. No browser or cookie behavior was tested, so this is Supported rather than a reproduced credential leak. The default whoami projection is narrower, but a caller-selected field list bypasses it.

**Fix:** remove JSONP from authenticated endpoints; use a fixed safe response DTO and appropriate explicit cookie policy. **Regression:** callback requests are rejected or returned as non-executable JSON without sensitive fields; cross-origin script loading cannot obtain user data; same-origin whoami still returns its public projection. Reference: [Security topic](https://portswigger.net/web-security/cross-site-scripting).

### WSA-045 — Anonymous input accumulates in unbounded persistent collections

**Medium · Confirmed · source-proven resource accumulation; exhaustion threshold unmeasured.** Public `POST /rest/web3/walletExploitAddress` ([server.ts:665](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:665>)) adds the supplied walletAddress to a module-global Set before any provider initialization/check ([routes/web3Wallet.ts:10](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/web3Wallet.ts:10>), line 16). There is no format check, maximum size, TTL or unconditional cleanup; removal requires a matching external contract event (line 28), which arbitrary submitted values need not have. The global JSON-body limit bounds one request, not the number of retained values.

Two additional persistence paths share this missing lifecycle bound: anonymous CAPTCHA requests insert rows without expiry deletion ([routes/captcha.ts:11](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/captcha.ts:11>), line 29), and public file-upload telemetry uses arbitrary client MIME strings as metric label values ([server.ts:335](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:335>), [routes/metrics.ts:77](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/metrics.ts:77>)) without a finite allowlist. Distinct values/requests accumulate until process restart or database reset. The report proves retention/growth rather than a measured crash or a specific request count.

**Fix:** validate and cap subscribed addresses with TTLs and authentication/quotas; expire/consume CAPTCHA records; map upload labels to a finite set with an `other` bucket. **Regression:** many distinct synthetic values cannot grow retained state beyond the configured budget; expired values are removed; valid event subscriptions, CAPTCHA and aggregate metrics continue working. Reference: [Security topic](https://portswigger.net/web-security/api-testing).

### WSA-046 — Password policy is enforced by forms but not by server credential writers

**Medium · Confirmed · source-proven.** The registration form requires a five-character minimum ([frontend/src/app/register/register.component.ts:64](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/register/register.component.ts:64>)), and change/reset forms perform similar client validation. Server registration checks nonempty values only when email, password **and passwordRepeat** are all present ([server.ts:431](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:431>)–441). Omitting passwordRepeat bypasses this branch; [models/user.ts:70](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/models/user.ts:70>) hashes a supplied empty string without a minimum-length validator, and [routes/login.ts:33](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/login.ts:33>) hashes an empty password for comparison. A directly registered account can therefore have an empty password. Password change/reset reject empty strings but accept any nonempty length ([routes/changePassword.ts:19](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/changePassword.ts:19>), [routes/resetPassword.ts:26](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/resetPassword.ts:26>)). The privileged-account complexity branch in the change form merely logs a warning ([frontend/src/app/change-password/change-password.component.ts:88](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/change-password/change-password.component.ts:88>)).

The boundary violation is bypass of the advertised credential policy through direct API calls. This does not alone take over an arbitrary existing account; it creates or downgrades credentials that are trivial to guess, compounding missing throttling and fast hashing.

**Fix:** apply one server-side password policy to registration, change and reset before hashing; require a minimum appropriate length and reject known-compromised/common values, with a reasonable maximum for resource safety. Do not depend on passwordRepeat or UI validation for authorization/policy. **Regression:** omitted repeat fields, blank/short/common passwords fail through all API writers; valid long passwords—including supported spaces/Unicode—round-trip correctly and obey a consistent policy. Reference: [Security topic](https://portswigger.net/web-security/authentication/password-based).

## Findings summary and repair sequencing

The findings are grouped by shared root cause where appropriate; a single item may list multiple affected handlers. Severity is qualitative and specific to this application. Supported findings are not included in confirmed totals. The final report contains 46 findings: 28 Confirmed source-proven findings (16 High, 10 Medium, 2 Low) and 18 Supported findings (1 Critical, 11 High, 6 Medium). No finding is runtime-reproduced.

1. **Immediate containment and secret rotation:** remove publicly served keys/logs/invoices/internal configuration; rotate JWT keys, exposed recovery material and affected TOTP seeds; retire derived OAuth credentials. Disable externally reachable interpreter/upload paths until repaired (WSA-001/002/010–017/019/020/024/046).
2. **Identity and authorization foundation:** one validated, revocable principal; separate MFA token purposes; a default-deny per-operation generated API policy; immutable owner IDs and stable order ownership (WSA-003–009/015/016/038).
3. **Input and rendering boundaries:** remove eval and JavaScript queries; safe parser modes; canonical filesystem containment; constrained outbound retrieval; inert export/Angular rendering; CSRF and JSONP removal (WSA-017–031/044).
4. **Business invariants and availability:** atomic quantities/balances, exhaustive payment modes, authentic coupons, one-use CAPTCHA, trustworthy throttling and LLM budgets/policy (WSA-032–040/045).
5. **Deployment and client lifecycle:** HTTPS enforcement, explicit cookie policy, account-scoped storage and exact redirect targets (WSA-041–043).

These recommendations describe how to secure a production-derived application. Preserving a deliberately vulnerable training mode would require explicit isolation and separate configuration; disabling a challenge alone should not be represented as a general security fix.

## Positive controls, bounded negative results and unresolved leads

- **Client-side path traversal rejected as a finding:** [frontend/src/app/Services/track-order.service.ts:21](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/Services/track-order.service.ts:21>) applies `encodeURIComponent` to the order ID before building the URL. The track-result component has an HTML rendering issue (WSA-029), but its request cannot be asserted to traverse into password-change merely from a query parameter. An early tentative lead was retracted after reading the complete service.
- **Owner-scoped siblings:** custom card list/read/delete and address list/read/delete constrain `UserId`; card responses mask card numbers. BasketItem foreign-key update hooks prevent general BasketId/ProductId reassignment. These controls do not fix other sibling operations (WSA-005–007).
- **CORS and framing:** [server.ts:183](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:183>) uses wildcard CORS without enabling credentialed origin reflection; that is not by itself a credential-stealing CORS vulnerability. Frameguard and no-sniff are configured at [server.ts:187](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:187>)–188. External header overrides were not available.
- **Chat rendering:** reviewed conversation HTML uses text interpolation for model/tool output; no markdown-to-HTML execution sink was found there. LLM catalog lookup uses Sequelize operators, and its review ID is converted to a number. No chat-output XSS or LLM SQL injection is asserted.
- **Known trusted data:** CAPTCHA's eval expression is built from server-chosen digits/operators, not a request string. The fixed dynamic-import Function in [lib/xml.ts:12](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/xml.ts:12>) imports fixed library names; it is not itself an attacker-controlled function constructor. Startup download URLs and Terraform local-exec variables are administrator configuration in the reviewed flow, not unauthenticated request inputs.
- **Profile CSP injection:** [routes/userProfile.ts:91](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/userProfile.ts:91>) places `profileImage` inside a CSP directive. The failed-fetch fallback at [routes/profileImageUrlUpload.ts:36](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/routes/profileImageUrlUpload.ts:36>) can preserve semicolon-containing attacker input, potentially inserting an earlier permissive script directive. This is a source-proven malformed-policy primitive, with browser execution and a victim-content path unresolved; it compounds WSA-017/031 rather than establishing independent cross-account XSS. Build a constant policy and validate image origins; regression: profile-image values cannot add directives.
- **Third-party token transmission:** the global HttpClient interceptor ([frontend/src/app/Services/request.interceptor.ts:13](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/Services/request.interceptor.ts:13>)) attaches the local bearer and email broadly, while [frontend/src/app/Services/user.service.ts:68](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/Services/user.service.ts:68>) calls external Google userinfo. If a local session exists during that call and the external service permits its preflight, the local token can be transmitted unnecessarily. The CTF notification service also passes its configured URL to HttpClient ([frontend/src/app/Services/ctf-system-wide-notification.service.ts:23](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/frontend/src/app/Services/ctf-system-wide-notification.service.ts:23>)); URL configuration is an administrator trust boundary, not a demonstrated anonymous input path. No attacker-controlled destination or actual transmission was established. Restrict credential attachment to the application API origin and test external requests carry none.
- **Legacy dependency hypotheses:** manifests pin old JWT/express-jwt/sanitize-html and a legacy js-yaml range. None was promoted to a CVE, algorithm-confusion, sanitizer-bypass or native-deserialization RCE finding on version alone. No resolved installed dependency source, active lockfile, external advisory lookup or library execution was available. Test supported algorithms, safe YAML schema and sanitizer policy against the actual resolved tree before making such claims.
- **Prototype pollution:** direct application merge/prototype searches did not establish an attacker-controlled prototype mutation to a security sink. Request spread into rendering options is WSA-028; it is not automatically prototype pollution. Transitive library behavior remains unverified.
- **Public training state:** Socket.IO ([lib/startup/registerWebsocketEvents.ts:22](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/startup/registerWebsocketEvents.ts:22>)) broadcasts global training notifications and accepts notification removal without per-user authentication. Continue/restore/snippet/hint routes also operate shared training state. A per-user/tenant isolation requirement was not established for that intentionally global state, so it is not inflated into account compromise. If multi-user isolation is desired, scope state and authenticate event mutations, then test two independent sessions.
- **Metrics/errors:** `/metrics` is public ([server.ts:696](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:696>)) and emits operational/business aggregates; no per-user secret metric was established. The always-installed development-style error handler ([server.ts:702](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:702>)) can expose diagnostic details on error paths; public parser error excerpts are already covered above. Restrict diagnostics and return generic public errors; no actual runtime stack trace was collected.
- **Account lifecycle and data-at-rest:** `isActive` has no discovered enforcement. Card numbers are stored as model data rather than processor tokens; the application models payments rather than demonstrating live settlement. Database initialization deliberately uses `sync({force:true})` ([server.ts:755](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:755>)). These require production policy/storage changes if repurposed, but are not separately scored as demonstrated account deactivation, card theft, or accidental production deletion incidents.
- **Deployment controls:** the root Dockerfile uses a non-root user; Terraform includes EFS encryption and a service security-group boundary. Docker Compose's database `expose` declarations are not host-published public database ports. No blanket “container runs as root” or “database publicly reachable” finding was made.

## Coverage ledger

States are `reviewed`, `not-applicable`, `blocked`, and `not-reviewed`. “Reviewed” means the specified source path/check was inspected, not that it is secure or that every possible exploit was excluded. Runtime testing was explicitly omitted and has no status column. Searches supplied leads; only the read handlers/groups below count as reviewed.

| Group | Topic | Source status | Evidence / boundary of review |
| --- | --- | --- | --- |
| Identity/access | Authentication | reviewed | Login, change/reset, security questions, MFA, full User model, cache and frontend OAuth/login; WSA-001/010–016/037. |
| Identity/access | Access control | reviewed | All route registrations, all models, generated CRUD matrix, sibling ownership and masked identity comparisons; WSA-003–009. |
| Identity/access | OAuth authentication | reviewed | Browser registration/login/password derivation and provider userinfo path; WSA-011. Provider deployment/tenant setup absent. |
| Identity/access | JWT attacks | reviewed | Signing key, purpose, expiry, cache, role helpers and decode-only chat; WSA-002/015/016/038. Algorithm-confusion library behavior unresolved. |
| Browser | XSS | reviewed | Every explicit trust-bypass/document-write search lead traced or marked unresolved; templates and selected components; WSA-026/029/030. |
| Browser | CSRF | reviewed | Cookie profile/erasure versus bearer APIs, body parsers and cookie writes; WSA-031. |
| Browser | CORS | reviewed | Express wildcard without credentials and Socket.IO configuration; no demonstrated credentialed CORS flaw. |
| Browser | Clickjacking | reviewed | Frameguard present; deployment overrides unavailable. |
| Browser | DOM-based vulnerabilities | reviewed | Search/tracking/export sinks, navigation, interceptor; tracking segment encoding negative control. |
| Injection | SQL injection | reviewed | Custom Sequelize raw-query construction and generated model access; WSA-001. |
| Injection | NoSQL injection | reviewed | MarsDB selectors, `$where`, update selectors, chat tool conversion; WSA-008/018. |
| Injection | Command injection | reviewed | Profile eval/B2B VM and fixed startup/deployment commands; direct JS execution WSA-017, no separate shell-input path established. |
| Injection | XXE | reviewed | Upload gate, filesystem providers, parser flags and output; WSA-019. |
| Injection | Server-side template injection | reviewed | Profile eval/source substitution, Pug and Handlebars locals/options; WSA-017/028. |
| Files/data | Path traversal | reviewed | All custom download servers, ZIP extraction, static roots, layout; WSA-020/022/023/028. |
| Files/data | File upload vulnerabilities | reviewed | Memory/disk multipart, image file and URL paths, ZIP/XML/YAML and serving; WSA-019–027. |
| Files/data | Information disclosure | reviewed | DTOs, JWT payload, memories, config, public roots, logs, exports and JSONP; WSA-002/010/012/013/024/044. |
| Files/data | Insecure deserialization | reviewed | YAML load, JSON/body parsing, duplicate JSON keys and XML; WSA-007/021. Library-native object exploit unresolved. |
| APIs/realtime | API testing | reviewed | Full custom and generated server surfaces, token purpose and property authorization; all frontend Services callers and selected components read as listed below. |
| APIs/realtime | WebSockets | reviewed | Server handlers and frontend Socket.IO service; global training-state design noted, no independent cross-account business-data channel established. |
| GraphQL | GraphQL API vulnerabilities | not-applicable | No GraphQL route/schema/resolver/client found in registration, manifests or targeted application-source search. |
| Business | Business logic vulnerabilities | reviewed | Basket/checkout/payment/coupons/captcha/recovery/tool policies; WSA-032–039. |
| Business | Race conditions | reviewed | Checkout multi-store ordering and review likes; WSA-035. No concurrency executed. |
| HTTP/infrastructure | SSRF | reviewed | URL image fetch and administrator-configured startup/provider fetches; WSA-025. |
| HTTP/infrastructure | Web cache deception | blocked | Static/dynamic route ordering reviewed, but effective proxy/cache config absent; Compose references an unavailable nginx.conf. No shared-cache exploit claimed. |
| HTTP/infrastructure | Web cache poisoning | blocked | Host use and response construction examined; shared cache keys, normalization and edge behavior unavailable. |
| HTTP/infrastructure | HTTP Host header attacks | reviewed | `req.get('host')` used in own data-export image URLs, not a discovered recovery-link authority path. Edge host validation not established. |
| HTTP/infrastructure | HTTP request smuggling | blocked | Express/proxy topology mapped; actual front/backend parsers and edge config unavailable. No protocol probes authorized. |
| Prototype | Prototype pollution | reviewed | Application merge/dynamic-object leads examined; no complete pollution-to-sink proof; dependency internals unavailable. |
| LLM | Web LLM attacks | reviewed | Chat principal, all tools, prompt/context, stream budget and UI/storage; WSA-038–041. No model requests made. |

### Supplemental checks

| Check | Source status | Evidence / limit |
| --- | --- | --- |
| Declared security fields versus enforcement | reviewed | Role accepted at registration; isActive unused; expiry skipped by cache; password optional on change; MFA type not required by generic APIs; UserId relations without authorization; quantity/discount/balance lack bounds. |
| Sibling handlers and principal transformations | reviewed | Address read/delete versus PUT; Cards scoped versus BasketItems; recycle list versus item; review create/update/like; masked-email order ownership across history/export/chat. |
| Credentials/cryptography | reviewed | RSA reuse, MD5, HMAC answers, JWT payloads, reversible coupons, deterministic OAuth password. No secret values copied. |
| SAML / enterprise SSO | not-applicable | No SAML routes, assertions, metadata or relevant integration found in mapped application source/manifests. |
| Server-side open redirects | reviewed | Substring allowlist; WSA-042. |
| Frontend framework rendering | reviewed | Escape hatches/templates and all matched dangerous rendering sites triaged; full residual frontend scope listed below. |
| Frontend runtime lifecycle | reviewed | Build/environment/index, localStorage/cookies, logout, chat persistence, interceptors; no service worker registration found in targeted source search. Vendor bundles not fully reviewed. |
| Dependencies/shared packages | blocked | Manifests and all core shared security modules read; active resolved tree/lockfiles absent, external advisory verification excluded. FTP lock backup was listed, not treated as authoritative installed dependency state. |
| Browser policy/session cookies | reviewed | Frame/no-sniff/global CSP absence, profile CSP interpolation, cookie writes and JSONP; edge/browser policy unverified. |
| Deployment/secrets/service controls | reviewed | Dockerfiles, Compose, Terraform and default/unsafe security settings; edge nginx content absent and other config profiles not fully read. |

### Generated API operation and ownership matrix

All 14 registrations at [server.ts:504](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/server.ts:504>)–528 and their pre-middleware/hooks were read. “JWT” below means the generic middleware, with purpose/lifecycle weaknesses discussed above. A row marked reviewed records inspection of the complete registration/policy, not third-party Finale implementation internals.

| Generated resource | Status | Effective application policy observed |
| --- | --- | --- |
| User | reviewed | Public create with privileged-field problem; list/item GET any JWT; PUT/DELETE denied; password/TOTP excluded only from generated responses. |
| Product | reviewed | Public read and PUT; POST any JWT; DELETE denied. |
| Feedback | reviewed | Public list/create with CAPTCHA; item GET/DELETE any JWT; PUT denied; untrusted attribution. |
| BasketItem | reviewed | JWT all; POST custom duplicate parser; PUT quantity check; no consistent owner predicate; foreign-key update hooks present. |
| Challenge | reviewed | Public list; create and item operations denied; translation and dependency inclusion reviewed. |
| Complaint | reviewed | List/create any JWT; item operations denied; create UserId not derived from principal. |
| Recycle | reviewed | List deliberately blocked; create any JWT; custom item GET unauthenticated/unowned; PUT/DELETE denied. |
| SecurityQuestion | reviewed | Public list; create/item operations denied. |
| SecurityAnswer | reviewed | Public create without binding UserId; list/item operations denied; unique UserId restricts overwrite. |
| Address | reviewed | Create derives UserId; list/read/delete owner scoped; PUT derives new owner value but does not scope target. |
| PrivacyRequest | reviewed | Create any JWT without owner assignment; list/item operations denied. |
| Card | reviewed | Create derives UserId; custom list/read/delete scoped; responses mask number; PUT denied. |
| Quantity | reviewed | Public list; item paths require accounting plus restrictive IP allowlist; create/delete denied. No claim that role alone bypasses that IP rule. |
| Hint | reviewed | Public list/PUT; create, item GET/DELETE denied; global training hints are not asserted to be per-user confidential data. |

### Custom route handler groups

Every file in `routes/*.ts` was read, including all exported handlers and internal helpers. Mounting, earlier middleware, generated resource interactions, error handling and static ordering were checked in `server.ts`. Route-file rows below are generated directly from the target's file inventory to avoid omitting low-profile handlers.
| Handler group | Status | Entry-point coverage |
| --- | --- | --- |
| `routes/2fa.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/address.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/angular.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/appConfiguration.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/appVersion.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/authenticatedUsers.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/b2bOrder.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/basket.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/basketItems.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/captcha.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/changePassword.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/chat.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/checkKeys.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/continueCode.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/countryMapping.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/coupon.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/createProductReviews.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/currentUser.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/dataErasure.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/dataExport.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/delivery.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/deluxe.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/easterEgg.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/fileServer.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/fileUpload.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/imageCaptcha.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/keyServer.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/languages.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/likeProductReviews.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/logfileServer.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/login.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/memory.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/metrics.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/nftMint.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/order.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/orderHistory.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/payment.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/premiumReward.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/privacyPolicyProof.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/profileImageFileUpload.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/profileImageUrlUpload.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/quarantineServer.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/recycles.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/redirect.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/repeatNotification.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/resetPassword.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/restoreProgress.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/saveLoginIp.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/search.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/securityQuestion.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/showProductReviews.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/trackOrder.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/updateProductReviews.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/updateUserProfile.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/userProfile.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/verify.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/videoHandler.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/vulnCodeFixes.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/vulnCodeSnippet.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/wallet.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |
| `routes/web3Wallet.ts` | reviewed | Complete file; mounting/enforcement traced in server.ts. |

### Other handler/source groups and remaining scope

| Group | Status | Read scope / residual work |
| --- | --- | --- |
| `server.ts`, `app.ts` | reviewed | Complete bootstrap, route ordering, generated resources, middleware, static files, parser/upload setup and startup. |
| `models/*.ts` | reviewed | All model files, fields, setters, hooks, associations and datastore initialization. |
| `lib/*.ts`, `lib/startup/*.ts` | reviewed | All top-level shared modules and startup modules, including security, config validation, XML, sockets, telemetry/challenge helpers and customization. `lib/scripts/lintConfig.ts` not included. |
| `views/*.pug`, `views/*.hbs`, `views/themes/themes.ts` | reviewed | All supplied server templates and static theme definitions. |
| Frontend route/guard infrastructure | reviewed | `app.routing.ts`, `app.guard.ts`, request interceptor and login/OAuth flows. |
| Frontend security-sensitive components | reviewed | Complete component TS/HTML pairs: search-result, track-result, last-login-ip, administration, about, data-export, feedback-details, welcome-banner, product, product-details, chat-conversation. Exact paths in process.md. |
| Other selected frontend TS | reviewed | Complete login, OAuth, registration, password change/reset/strength, two-factor setup/entry, privacy-security, navbar, sidenav, score-board, chat-welcome-page, chat-welcome-screen implementations; associated unlisted templates/helpers are not all reviewed. |
| Frontend API/storage services | reviewed | All non-spec TypeScript files in frontend/src/app/Services, including the interceptor and two-factor-auth-service.ts, fully read. |
| Remaining frontend components/helpers | not-reviewed | Broad sink/HTTP searches only for unlisted files; no claim of complete read of all checkout/forms, web3 UI, scoreboard subcomponents, pipes, styles, or instructor code. All server-side counterparts were read. |
| Default/unsafe configuration | reviewed | Default general/security/chat/OAuth settings and recovery-memory fields, full unsafe profile, config schema and validation. Product-catalog prose and alternate profiles not fully read. |
| Other config profiles | not-reviewed | Config files other than default/unsafe were inventoried, not fully read; effective NODE_ENV overrides not supplied. |
| Deployment | reviewed | Root/infrastructure Dockerfiles, infrastructure Compose and both Terraform main/networking/variables/outputs sets. Matching networking/variables/outputs copies verified by SHA256; main files read separately. |
| Reverse-proxy configuration | blocked | nginx.conf referenced by Compose is absent; no actual edge config, cache policy or deployed state available. |
| Data initialization | reviewed | `data/mongodb.ts`, `data/datacache.ts`, `data/staticData.ts`; selected `data/datacreator.ts` initialization and recovery linkage. Remaining seed rows are not a full credential/data audit. |
| Static assets, translations, training content | not-reviewed | Names/search matches only where relevant; no full binary/media/vendor/translation/solution-content review. FTP contents and live logs/database files were not opened. |
| Web3 backend | reviewed | checkKeys/nftMint/web3Wallet route handlers and configured upstream calls; no blockchain transactions or provider interaction. Contract correctness and frontend wallet UX remain not-reviewed. |
| Tests, build/CI and dependency internals | not-reviewed | No test suite execution or complete test/CI/vendor review. Builds and installed dependency implementations unavailable/not installed. |

## Limitations and verification

- No live requests, browser interactions, model calls, service startup, dependency install, application imports, test execution, exploits or modifications were performed. Proposed tests use synthetic fixtures and are not recorded as passing.
- “Source-proven” relies on the read application code and its declared framework/API semantics. Generated Finale behavior, ORM serialization, parser flags and browser sinks were not exercised. Where a material unresolved dependency/gate changes the security effect, confidence is Supported or the lead is explicitly unresolved.
- Challenge enablement is computed by [lib/utils.ts:153](<C:/Users/User/Projects/web-security-audit-workspace/juice-shop/lib/utils.ts:153>) from safety mode and environment flags and initialized by `data/datacreator.ts`. The default uses auto mode; unsafe disables it. No current process/environment/database was available. Findings name relevant gates rather than assuming all challenge code executes in every deployment.
- No external URLs cited as topic references were fetched. They are methodological pointers from the requested skill, not evidence of target behavior or verified current library advisories. Target source is the evidence.
- The reviewed checkout, payment, blockchain and privacy flows are educational simulations. Impact is bounded to evidenced in-application actions/data; real payment settlement, actual account deletion or on-chain asset compromise is not inferred.
- Coverage is extensive but finite. Unlisted frontend files, other configuration variants, dependency internals, static data, CI and effective edge behavior remain as recorded above; this is not a security certification.
- Report validation includes checking every referenced target path/line exists, finding identifiers are unique, and each finding includes confidence, remediation and regression guidance. Full audit elapsed time and model-token consumption were not measured; individual tool timing is not substituted for them.




