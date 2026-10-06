# Identity, sessions and access control

## Authentication

Source: [PortSwigger Authentication](https://portswigger.net/web-security/authentication).

- **Inspect:** login, registration, verification, recovery, password change, remember-me and MFA endpoints; session creation, rotation, expiry and logout. Follow alternate routes and shared middleware.
- **Validate:** use supplied accounts to check that a pending-MFA identity cannot reach protected operations; recovery tokens are unpredictable, short-lived, single-use and bound to the account/action; password or MFA changes require appropriate reauthentication. Compare a small controlled set of valid/invalid identities for enumeration. Review per-account and per-source protections without credential spraying.
- **Evidence:** establish which identity the server accepts, what verification step is bypassed, and what protected action/data becomes available. Record session behavior, not just UI navigation.
- **Fix:** enforce a server-side authentication state machine, rotate sessions at privilege transitions, bind recovery/MFA artifacts to the user and operation, and implement appropriate limits.
- **Example:** After the password step the login response already sets a session cookie accepted by `/api/*`, so MFA only gates the UI. `POST /mfa/verify` takes `userId` from the body and checks that user's code. A reset token derived from `md5(email + timestamp)` is predictable; a token that still works after use or after a newer token is issued is replayable.
- **Avoid false positives:** a public login screen is expected. Client validation is not the enforcement boundary; centralized middleware may already enforce the missing-looking local check. An enumeration difference needs a repeatable signal and contextual impact.

Apply the schema-versus-enforcement comparison from the [methodology](methodology.md#compare-declared-controls-with-enforced-controls) here first: every MFA, verification, lockout, expiry and single-use field the data model declares needs a reader on the login, recovery or token path.

For passkeys and WebAuthn, check that the server generates and stores the challenge per ceremony and consumes it once, verifies the origin and RP ID against configuration rather than the request, checks the user-presence/verification flags the policy requires, binds the credential to the account that started the ceremony, and treats a signature counter that does not increase as a cloned-authenticator signal. Use a maintained library; home-grown attestation parsing is a lead.

## Credentials and cryptography

Sources: [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [OWASP Cryptographic Storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html).

- **Inspect:** password hashing (algorithm, work factor, salt, pepper handling), comparison of secrets and tokens, generation of tokens, codes, invitation links and API keys, encryption of stored sensitive fields (mode, IV/nonce handling, authentication), and where keys and secrets live (source, config, environment, a manager).
- **Validate:** confirm the hash is a password hash (Argon2id, scrypt, bcrypt, PBKDF2 with a current cost), not a fast digest (`md5`, `sha1`, `sha256`, with or without a salt). Confirm secrets are compared in constant time where an attacker can measure (`hmac.compare_digest`, `crypto.timingSafeEqual`, `MessageDigest.isEqual`, `hash_equals`, `subtle.ConstantTimeCompare`). Confirm random values come from a CSPRNG (`secrets`, `crypto.randomBytes`/`randomUUID`, `SecureRandom`, `RandomNumberGenerator`, `crypto/rand`, `random_bytes`, `SecureRandom`) rather than `Math.random`, `random.random`, `java.util.Random`, `rand()` or a timestamp. For encryption, check for ECB, a static or reused IV/nonce with CTR/GCM, unauthenticated CBC where the ciphertext is attacker-supplied (padding oracle), and keys derived directly from a password without a KDF.
- **Evidence:** name the algorithm and parameters from code or configuration, the data they protect and the attacker who can obtain the hash, ciphertext or timing signal. Report an exposed secret by type and location; never print its value.
- **Fix:** adopt a password hash with current parameters and a migration on next login; use constant-time comparison for secrets; generate tokens with 128 bits or more of CSPRNG entropy and store a hash of long-lived ones; use an AEAD (AES-GCM, ChaCha20-Poly1305) with a unique nonce per message; keep keys in a secret manager with rotation.
- **Example:** `users.password = sha256(salt + password)` lets anyone with a database dump test billions of guesses per second. `if (token == stored)` on a reset token is a timing side channel only when the attacker can measure the comparison; over a network with a 256-bit token it is usually hardening. `Math.random().toString(36)` for an invitation token is predictable from a few observed values.
- **Avoid false positives:** a fast digest is fine for integrity of non-secret data (ETags, cache keys, deduplication). `==` on an unpredictable 256-bit token is Low or Informational unless a measurable timing channel exists. A per-user salt does not rescue a fast hash. Do not call a configuration insecure from the algorithm name alone when a library applies safe parameters by default (bcrypt cost 10 to 12, Argon2id library defaults).

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

## SAML and enterprise SSO

Source: [OWASP SAML Security](https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html).

- **Inspect:** the service-provider library and version, signature validation settings (which element must be signed: the `Response`, the `Assertion` or both), the trusted IdP certificate source and rotation, `Audience`, `Recipient`, `Destination`, `NotBefore`/`NotOnOrAfter` and `InResponseTo` checks, assertion replay tracking, the attribute used to map the local account (NameID, email, employee ID), just-in-time provisioning and role/group mapping from attributes, single-logout handling, and the IdP-initiated flow if enabled.
- **Validate:** confirm the library rejects an unsigned assertion inside a signed response and an assertion whose signature references a different element (XML signature wrapping); confirm the signing certificate is pinned to the configured IdP rather than taken from the message; confirm the audience is this SP and the assertion ID has not been seen. Check whether a multi-tenant SP binds the IdP to the tenant, so IdP A cannot assert a user of tenant B. Parse the assertion with the same hardened XML settings as any other XML input ([XXE](injection.md#xxe-injection)).
- **Evidence:** show a modified or re-signed assertion accepted, an assertion from one tenant's IdP mapped into another tenant, or a role elevated through an attacker-controlled attribute. State which party (IdP admin, any IdP user, unauthenticated) can supply the input.
- **Fix:** require signatures on the assertion with the library's strict validation, pin IdP certificates per tenant, validate audience, recipient and time window, store assertion IDs for the validity window, map accounts by a stable immutable identifier and derive roles from local policy rather than trusting attributes for privileged roles.
- **Example:** The SP validates the signature on `Response` but reads the user from an `Assertion` the attacker inserted before the signed one. A multi-tenant SP looks up the IdP by the `Issuer` in the message, so a tenant that controls its own IdP can issue an assertion with another tenant's email and log in there.
- **Avoid false positives:** metadata URLs, entity IDs and an unencrypted assertion over TLS are normal. A library with current defaults (`wantAssertionsSigned`, strict mode) is likely safe; the leads are explicit downgrades, custom XML handling and the account-mapping and tenant-binding logic around the library.

## JWT attacks

Source: [PortSwigger JWT attacks](https://portswigger.net/web-security/jwt).

- **Inspect:** verification calls versus decoding calls, accepted algorithms, key selection, signing keys, claim validation and token-to-session/role mapping. Check all services that consume the token.
- **Validate:** use a synthetic token to confirm rejection of modified claims, unsigned tokens and an unexpected algorithm/key type. Review attacker-influenced `kid`, `jku` and `jwk` handling for unsafe file/query/remote key lookup. Keep key resolution inside the supplied scope.
- **Evidence:** show acceptance of an invalid token and the resulting protected access; establish whether enforcement happens elsewhere before alleging a bypass.
- **Fix:** constrain algorithms and trusted keys, verify before using claims, and validate issuer, audience, lifetime and token purpose. Keep remote key locations fixed/trusted.
- **Example:** A gateway calls `jwt.decode(token)` instead of verifying; a library accepts `alg: none`; an RS256 service also accepts HS256 and uses the public key as the HMAC secret; a `kid` header such as `../../dev/null` is used as a file path for key lookup.
- **Avoid false positives:** decoding a token for display does not imply the backend trusts it. Readable claims are expected for a signed, unencrypted token; sensitive content is a separate exposure question.

Use [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) for algorithm/key verification, claim validation and separating validation rules for different token types. Recommend strong key material and managed rotation rather than home-grown verification.
