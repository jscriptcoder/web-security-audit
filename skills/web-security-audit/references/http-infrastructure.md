# HTTP, outbound requests and caching

## Server-side request forgery (SSRF)

Source: [PortSwigger SSRF](https://portswigger.net/web-security/ssrf).

- **Inspect:** URL previews, imports, webhooks, image proxies, document converters and redirect-following HTTP clients. Trace scheme/host/port validation, DNS resolution, connection destinations and forwarded credentials.
- **Validate:** prefer an isolated server with synthetic permitted/blocked receivers. Check the actual parser, redirects, IPv4/IPv6 and resolution behavior. Use only in-scope callback destinations; do not probe cloud metadata or private networks outside the supplied scope.
- **Evidence:** show a server-initiated request crossing the intended destination boundary; determine whether the attacker reads a response or only causes a blind interaction.
- **Fix:** use explicit destination policies, validate resolved addresses and each redirect, constrain schemes/ports, avoid sending privileged credentials and apply network egress controls. Reconcile validation with the address used at connection time.
- **Example:** A webhook validator resolves `hooks.example` to a public IP and approves it, then the HTTP client resolves it again (DNS rebinding) or follows a 302 to `http://169.254.169.254/`. Blocklists also miss alternate forms such as `http://2130706433/`, `http://127.1/` and `http://[::ffff:127.0.0.1]/`.
- **Avoid false positives:** browser-originated fetches are not SSRF. An allowed external fetch may be the intended feature. String-prefix hostname checks, pre-resolution checks or checking only the initial redirect destination do not establish containment.

## Web cache deception

Source: [PortSwigger Web cache deception](https://portswigger.net/web-security/web-cache-deception).

- **Inspect:** personalized responses and cache rules based on suffixes/static prefixes; path normalization, delimiters and routing disagreements between cache and origin. Include CDN, reverse proxy and application caching.
- **Validate:** in an isolated/scoped cache namespace, establish origin behavior and whether the cache key really isolates the test; an arbitrary query parameter may be ignored. Let synthetic user A prime a candidate path, then request it without A's credentials or as user B. Verify cache-hit evidence and A-specific canary data.
- **Evidence:** show private content cached and retrievable by an unauthorized requester. A misleading extension or HIT header alone is insufficient.
- **Fix:** prevent shared caching of sensitive responses, align cache/origin path interpretation and use explicit routing/cache rules. Verify actual handling of private/no-store directives.
- **Example:** The origin routes `/account/settings/x.css` (or `/account/settings;x.css`) to the private settings page because it ignores the trailing segment or treats `;` as a delimiter, while the CDN caches everything ending in `.css`. A victim who follows the link places their page in the shared cache for the attacker to fetch.
- **Avoid false positives:** identical public content across identities is not a leak. A fresh origin response, same-user browser cache or cache key including the correct identity can explain a result. Remove scoped test entries where supported.

## Web cache poisoning

Source: [PortSwigger Web cache poisoning](https://portswigger.net/web-security/web-cache-poisoning).

- **Inspect:** response-affecting inputs omitted from the shared cache key: headers, forwarding data, parameters and normalization differences. Identify which layer emits redirects, resource URLs or content.
- **Validate:** use a scoped disposable cache entry whose isolation is demonstrated. Compare baseline, a request carrying an inert marker in a suspected unkeyed input, and a clean request without that input. Verify persistence through a cache hit and the marker's security-relevant context.
- **Evidence:** demonstrate attacker influence being served to a different legitimate requester. Distinguish response reflection from cached cross-request influence and assess whether the marker can cause meaningful harm.
- **Fix:** reject untrusted response-changing inputs, include legitimate varying inputs in cache semantics, or stop sharing the response. Align parsers and avoid trusting client forwarding metadata.
- **Example:** The application renders `<script src="https://${X-Forwarded-Host}/static/app.js">` and the CDN cache key ignores `X-Forwarded-Host`; one request carrying `X-Forwarded-Host: attacker.example` stores a page that loads attacker script for every later visitor.
- **Avoid false positives:** reflecting a header on an uncached response is not poisoning. A WAF/edge response may be a separate layer. Do not poison popular production URLs or assume a cache-buster makes testing isolated.

## HTTP Host header attacks

Source: [PortSwigger Host header attacks](https://portswigger.net/web-security/host-header).

- **Inspect:** absolute URL construction, password reset links, tenant selection, host routing, redirects and trusted-proxy handling for Host/Forwarded/X-Forwarded-Host. Trace each proxy's overwrite/validation behavior.
- **Validate:** use an approved test host and synthetic account. Inspect generated links or local delivery captures, routing results and downstream fetches; constrain host variation to the supplied infrastructure.
- **Evidence:** show poisoned sensitive links, unauthorized routing or a trusted-origin effect. Record the complete proxy path and prerequisites.
- **Fix:** configure canonical origins, allowlist routing hosts, trust forwarding headers only from known proxies that sanitize client values, and bind tenant decisions to authenticated policy.
- **Example:** A password-reset email builds its link as `https://${request.host}/reset?token=...`. Requesting a reset for the victim with `Host: attacker.example` (or `X-Forwarded-Host`) sends the victim a link that delivers their token to the attacker when clicked. A configured canonical base URL fixes it.
- **Avoid false positives:** safe relative redirects and rejection of unexpected hosts can explain reflection without impact. A local proxy spoof does not prove an internet client can influence the production header after edge rewriting. Ordinary multi-host routing is intended; establish which boundary is violated.

## HTTP request smuggling

Source: [PortSwigger HTTP request smuggling](https://portswigger.net/web-security/request-smuggling).

- **Inspect:** frontend/backend HTTP parsers, length/framing ambiguity, connection reuse, request rewriting and HTTP/2-to-HTTP/1 downgrades. Include CL/TE disagreements, zero-length/body-handling variants and browser desynchronization only where the topology supports them.
- **Validate:** begin with source/configuration and current server/vendor advisories. Active malformed-framing tests require a dedicated isolated backend connection pool or equivalent scope that excludes other users; otherwise mark runtime validation blocked and continue static review. Compare controlled requests and response sequencing within that environment.
- **Evidence:** demonstrate different request-boundary interpretation and resulting cross-request effects. A lone timeout, 400 or scanner signature is a hypothesis, not confirmation.
- **Fix:** reject ambiguous framing, align parsers, prevent unsafe downgrading/rewriting and apply vendor-supported mitigations to the actual topology.
- **Example:** The front end frames requests by `Content-Length` while the back end honors `Transfer-Encoding: chunked` (CL.TE), so the unread remainder of one request becomes the start of the next request on the shared back-end connection. HTTP/2 front ends that downgrade to HTTP/1.1 can create the same ambiguity.
- **Avoid false positives:** HTTP/2 at the public edge does not guarantee HTTP/2 end-to-end. A vulnerable version label alone does not establish reachable desynchronization; connection handling and parser configuration matter. Never use unrelated users' requests as proof.
