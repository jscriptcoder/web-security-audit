# Frontend runtime: secrets, tokens, caches and third parties

Load with [frontend frameworks](frontend-frameworks.md) for a full frontend audit, or alone when the question is about build configuration, token handling, logout, service workers, third-party scripts or embedding. A rendering-only diff review does not need this file.

## Client-side secrets and build configuration

- **Inspect:** environment variables inlined at build time: `NEXT_PUBLIC_*`, `VITE_*` (and any custom Vite `envPrefix`), `REACT_APP_*`, `NUXT_PUBLIC_*`/`runtimeConfig.public`, SvelteKit `$env/static/public`, `PUBLIC_*` (Astro), `EXPO_PUBLIC_*`, Angular `environment*.ts`, webpack `DefinePlugin` passing all of `process.env`, and framework config that inlines arbitrary names (Next.js `env` in `next.config.js` exposes every listed key to the client regardless of prefix). Inspect built bundles and source maps, not just source.
- **Validate:** classify each value: public identifier (analytics ID, OAuth client ID, publishable key, Firebase config, Sentry DSN) versus secret (server API keys, signing secrets, private tokens, database URLs). For cloud keys meant to be public, check the restrictions (allowed referrers, API scope, security rules) instead of the key's presence. Check whether a module that uses a server secret is imported from a `'use client'` component or other browser-bundled code.
- **Fix:** move secrets to server code or a BFF, rotate exposed ones through the owner's process and keep build-time env injection limited to an explicit public prefix. Mark server-only modules with `import 'server-only'` where the framework supports it.
- **Avoid false positives:** a public client identifier is not a secret. A Firebase config in a bundle is expected; the finding is permissive security rules, if present.

## Tokens, sessions and logout in the browser

Sources: [OAuth 2.0 for Browser-Based Applications](https://datatracker.ietf.org/doc/draft-ietf-oauth-browser-based-apps/), [MDN Clear-Site-Data](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Clear-Site-Data).

- **Inspect:** where access and refresh tokens live (memory, `localStorage`, `sessionStorage`, IndexedDB, cookies), refresh-token rotation, PKCE and `state` handling in the SPA, tokens or OAuth codes in URLs (which leak through history, `Referer` and analytics), and logout cleanup.
- **Validate:** after logout, check whether tokens, cached API responses, IndexedDB data or service-worker caches remain usable or visible, and whether the server revokes the session or refresh token. Check whether a token is readable by any script, which matters if XSS or a compromised third-party script exists.
- **Fix:** prefer a BFF or HttpOnly session cookie for sensitive applications; otherwise keep access tokens short-lived in memory and rotate or sender-constrain refresh tokens. Revoke server-side on logout and send `Clear-Site-Data` from the logout response.
- **Avoid false positives:** `localStorage` token storage is a risk amplifier for XSS, not a vulnerability on its own; rate it by the XSS exposure and token lifetime/scope.

## GraphQL clients

Apollo Client, urql and Relay keep a normalized cache of every object the user has loaded, sometimes persisted to `localStorage`. Check that logout and user switching clear it (`client.clearStore()`), close subscription clients and drop tokens from `connectionParams`. The full checks are in [GraphQL](graphql.md#graphql-clients-in-the-frontend).

## Service workers and client caches

- **Inspect:** service-worker registration scope, the script's origin and update path, and runtime caching rules (hand-written `fetch` handlers, Workbox `registerRoute`, `NetworkFirst`, `StaleWhileRevalidate`, `CacheFirst`) that match authenticated API routes or HTML.
- **Validate:** with synthetic user A, load private data, log out, log in as user B on the same browser profile and check whether A's responses are served from the cache. Check whether the service worker can be registered from a path that serves user-controlled content.
- **Fix:** exclude authenticated responses from service-worker caches or key them by user, clear caches on logout and send `Cache-Control: no-store` on sensitive responses.
- **Avoid false positives:** caching public assets and app shell HTML is intended.

## Third-party scripts and supply chain

Source: [MDN Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity).

- **Inspect:** scripts loaded from CDNs and third parties, tag managers (who can publish to the container), chat/analytics/A-B testing widgets, `integrity` attributes, and CSP `script-src` allowances for those hosts. The 2024 polyfill.io compromise is an example of a trusted CDN domain serving malicious code after an ownership change.
- **Validate:** list every origin that can execute script in the app origin and whether it can read tokens, DOM data or form input. Check analytics calls for tokens, emails or other personal data in URLs or payloads.
- **Fix:** self-host or pin with SRI where the resource is static, restrict CSP to required hosts, govern tag manager publishing rights and scrub sensitive data from telemetry.
- **Avoid false positives:** missing SRI on a dynamically versioned vendor script (which SRI cannot cover) is a governance observation, not an exploit.

## Embedding, iframes and microfrontends

- **Inspect:** `iframe` `sandbox` values, embedded user content, microfrontend or module-federation remotes loaded from runtime URLs or manifests, `window.open` targets and `postMessage` channels between fragments.
- **Validate:** `sandbox="allow-scripts allow-same-origin"` on same-origin content lets the framed document remove its own sandbox. Check who controls each remote entry URL or manifest and whether it can be influenced by the user or environment configuration.
- **Fix:** isolate untrusted embedded content on a separate origin, keep sandbox flags minimal and pin remote entries to trusted, deployment-controlled origins.

## Trusted Types and CSP as frontend fixes

Sources: [MDN Trusted Types](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API), [PortSwigger CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy).

Recommend CSP `require-trusted-types-for 'script'` with a small set of named policies when an application has many DOM sinks; Trusted Types reached Baseline browser support in February 2026 when Firefox joined Chrome and Safari, but older browsers ignore it, so treat it as defense in depth. Prefer nonce- or hash-based CSP with `strict-dynamic` over host allowlists. Neither replaces fixing the sink.

## Starting searches

```text
Build config: NEXT_PUBLIC_|VITE_|REACT_APP_|NUXT_PUBLIC_|EXPO_PUBLIC_|\bPUBLIC_|DefinePlugin|envPrefix|runtimeConfig|^\s*env: \{
Secret-looking names in client code: (API|ACCESS|SECRET|PRIVATE|SIGNING)_?(KEY|TOKEN|SECRET)|DATABASE_URL|process\.env\.
Tokens and storage: localStorage\.(get|set)Item|sessionStorage|indexedDB|refresh_?token|access_?token|Clear-Site-Data
Service workers and caches: serviceWorker\.register|caches\.open|registerRoute|StaleWhileRevalidate|NetworkFirst|CacheFirst|clearStore|resetStore|persistCache
Third parties and embedding: <script[^>]+src=["']https?://|integrity=|googletagmanager|sandbox=|module-federation|remoteEntry
```
