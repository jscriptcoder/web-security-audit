# Identity, sessions and access control

## Authentication

Source: [PortSwigger Authentication](https://portswigger.net/web-security/authentication).

- **Inspect:** login, registration, verification, recovery, password change, remember-me and MFA endpoints; session creation, rotation, expiry and logout. Follow alternate routes and shared middleware.
- **Validate:** use supplied accounts to check that a pending-MFA identity cannot reach protected operations; recovery tokens are unpredictable, short-lived, single-use and bound to the account/action; password or MFA changes require appropriate reauthentication. Compare a small controlled set of valid/invalid identities for enumeration. Review per-account and per-source protections without credential spraying.
- **Evidence:** establish which identity the server accepts, what verification step is bypassed, and what protected action/data becomes available. Record session behavior, not just UI navigation.
- **Fix:** enforce a server-side authentication state machine, rotate sessions at privilege transitions, bind recovery/MFA artifacts to the user and operation, and implement appropriate limits.
- **Example:** After the password step the login response already sets a session cookie accepted by `/api/*`, so MFA only gates the UI. `POST /mfa/verify` takes `userId` from the body and checks that user's code. A reset token derived from `md5(email + timestamp)` is predictable; a token that still works after use or after a newer token is issued is replayable.
- **Avoid false positives:** a public login screen is expected. Client validation is not the enforcement boundary; centralized middleware may already enforce the missing-looking local check. An enumeration difference needs a repeatable signal and contextual impact.

## Access control

Source: [PortSwigger Access control](https://portswigger.net/web-security/access-control).

- **Inspect:** object ownership, tenant isolation, roles and state-dependent permission checks on routes, resolvers, exports, downloads, background tasks and administrative actions. Inspect policy helpers and their callers.
- **Validate:** compare owner A against non-owner B on synthetic objects; compare ordinary and privileged roles; change tenant/object identifiers, nested resources and writable properties. Include list/bulk endpoints, indirect references and alternate methods when present.
- **Evidence:** show an actual unauthorized object, field or operation with the requesting identity and expected policy. A 200 response may contain only public data or an error envelope. Verify response contents and state.
- **Fix:** enforce authorization on the server for every operation, using authenticated identity and trusted ownership/tenant context. Apply policy before retrieving or mutating sensitive data; constrain writable fields.
- **Example:** `GET /api/invoices/1043` returns another customer's invoice because the handler calls `findById(id)`; `findByIdAndOwnerId(id, currentUser.id)` or a policy check on the loaded object fixes it. Vertically: `/admin/users` is hidden in the UI, but the API only requires an authenticated user.
- **Avoid false positives:** hidden buttons, route guards, UUIDs and client-side role checks are neither proof of a vulnerability nor a replacement for backend enforcement. Trace row-level security and shared policy before concluding a check is absent.

## OAuth authentication

Source: [PortSwigger OAuth authentication](https://portswigger.net/web-security/oauth).

- **Inspect:** authorization requests, callback handlers, redirect registration, account linking, provider identity mapping and token handling. Distinguish OAuth authorization from OIDC authentication.
- **Validate:** using test identities, verify transaction binding, rejection of mismatched callback state/code, strict redirect handling, token audience/issuer checks and verified account-linking ownership. Inspect whether client-provided email/profile fields can select a different local identity independently of the provider token.
- **Evidence:** demonstrate wrong-account login/linking, code/token leakage to an in-scope receiver, or reuse accepted outside the intended transaction. State provider/client prerequisites.
- **Fix:** use supported provider libraries and enforce the transaction, redirect and identity bindings on the server.
- **Example:** A callback that does not bind `state` to the browser session lets an attacker complete their own authorization in the victim's browser and link the attacker's social account to the victim's profile. A `redirect_uri` checked by prefix (`https://app.example`) accepts `https://app.example.attacker.net/cb`. A client that posts `email` to its own backend after the token exchange, and the backend trusts it, allows signing in as anyone.
- **Avoid false positives:** missing `state` alone does not prove CSRF when a correctly bound alternative protection exists. Inspect the complete flow and provider configuration.

Apply [RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700) when recommending flow changes: favor authorization code with PKCE, exact registered redirect matching subject to the native-loopback exception, and appropriate replay/refresh-token protection. Evaluate PKCE, state and OIDC nonce according to their distinct roles and the implemented flow; do not treat them as interchangeable switches. Prefer stable issuer/subject identity over unverified email matching.

## JWT attacks

Source: [PortSwigger JWT attacks](https://portswigger.net/web-security/jwt).

- **Inspect:** verification calls versus decoding calls, accepted algorithms, key selection, signing keys, claim validation and token-to-session/role mapping. Check all services that consume the token.
- **Validate:** use a synthetic token to confirm rejection of modified claims, unsigned tokens and an unexpected algorithm/key type. Review attacker-influenced `kid`, `jku` and `jwk` handling for unsafe file/query/remote key lookup. Keep key resolution inside the supplied scope.
- **Evidence:** show acceptance of an invalid token and the resulting protected access; establish whether enforcement happens elsewhere before alleging a bypass.
- **Fix:** constrain algorithms and trusted keys, verify before using claims, and validate issuer, audience, lifetime and token purpose. Keep remote key locations fixed/trusted.
- **Example:** A gateway calls `jwt.decode(token)` instead of verifying; a library accepts `alg: none`; an RS256 service also accepts HS256 and uses the public key as the HMAC secret; a `kid` header such as `../../dev/null` is used as a file path for key lookup.
- **Avoid false positives:** decoding a token for display does not imply the backend trusts it. Readable claims are expected for a signed, unencrypted token; sensitive content is a separate exposure question.

Use [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) for algorithm/key verification, claim validation and separating validation rules for different token types. Recommend strong key material and managed rotation rather than home-grown verification.
