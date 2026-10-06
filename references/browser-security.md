# Browser security

## Cross-site scripting (XSS)

Source: [PortSwigger XSS](https://portswigger.net/web-security/cross-site-scripting).

- **Inspect:** reflected/stored values reaching HTML, attributes, URLs, inline scripts, hydration data, rich text and framework escape hatches. Include content originating from APIs, uploads and other users.
- **Validate:** first place a unique inert marker to establish context, then use a harmless local execution marker in the identified context and approved test account. Follow the actual browser parse/render path and inspect sanitizer configuration.
- **Evidence:** show executable attacker-controlled content crossing into the victim origin and identify how another user encounters it. Distinguish stored, reflected and DOM paths; limit impact to established capabilities. If rendering is proven but effective CSP or another material execution prerequisite is unknown, label the XSS finding Supported; do not label execution Confirmed.
- **Fix:** render as text by default, encode for the specific output context, validate URL schemes and use a maintained sanitizer for intentionally allowed HTML. Add CSP as an additional control.
- **Example:** `<div dangerouslySetInnerHTML={{ __html: marked(comment.body) }} />` renders other users' comments; `marked` does not sanitize, so `<img src=x onerror=alert(document.domain)>` runs for every viewer. HTML-encoding does not protect an `href`: `<a href="{{ user.website }}">` still executes `javascript:alert(1)` unless the scheme is validated.
- **Avoid false positives:** React/Vue/template interpolation commonly escapes text. Reflection, `innerHTML` presence or a string in a bundle is a lead, not proof. Inspect taint, sanitizer behavior, context and enforced browser policy.

## Cross-site request forgery (CSRF)

Source: [PortSwigger CSRF](https://portswigger.net/web-security/csrf).

- **Inspect:** state-changing requests using automatically attached credentials, including login, GraphQL mutations and alternate content types/methods. Review tokens, origin checks and cookie policy.
- **Validate:** determine what a real cross-site browser can submit and whether it includes credentials. Use a reversible synthetic change to test rejection of absent/invalid/unbound protection. Check whether GET performs a mutation and whether a same-site untrusted subdomain changes the threat model.
- **Evidence:** show an attacker-origin request that changes victim state while authenticated, with all browser/cookie prerequisites stated.
- **Fix:** enforce a session-bound anti-CSRF mechanism or an appropriate validated origin/custom-header strategy; reject unexpected request formats. Apply suitable SameSite policy as defense in depth.
- **Example:** Browsers send `application/x-www-form-urlencoded`, `multipart/form-data` and `text/plain` cross-site without a preflight, so an endpoint that parses a `text/plain` body as JSON is reachable from an ordinary HTML form. `SameSite=Lax` cookies are still sent on top-level GET navigations, so `GET /account/delete?confirm=1` remains exposed.
- **Avoid false positives:** an API requiring a bearer token explicitly set in an authorization header is not automatically vulnerable because it lacks CSRF tokens. CORS governs readable responses, not all request submission; JSON alone is not an unconditional defense.

## Cross-origin resource sharing (CORS)

Source: [PortSwigger CORS](https://portswigger.net/web-security/cors).

- **Inspect:** origin reflection, suffix/regex matching, trusted subdomains, `null` origin, credential allowance, preflight and cache variation on Origin.
- **Validate:** use an attacker-controlled test origin in a browser and request actual sensitive data with the relevant credentials. Confirm both cookie eligibility and JavaScript response readability. Inspect whether trusted-origin takeover is an assumption or established fact.
- **Evidence:** demonstrate readable protected data from an unauthorized origin; identify the accepted origin and response headers.
- **Fix:** use an exact parsed origin allowlist, minimize trusted origins/credentials and vary cached responses appropriately where origin-dependent headers are emitted.
- **Example:** The server copies any `Origin` into `Access-Control-Allow-Origin` and adds `Access-Control-Allow-Credentials: true`, so `fetch('https://api.example/me', { credentials: 'include' })` from any site reads the profile, provided the session cookie is sent cross-site (`SameSite=None` and not blocked as a third-party cookie). Origin checks like `origin.endsWith('example.com')` accept `attacker-example.com`; an unanchored regex accepts `example.com.attacker.net`.
- **Avoid false positives:** `Access-Control-Allow-Origin: *` is valid for public resources. Browsers reject wildcard origin with credentialed response access even if `Access-Control-Allow-Credentials: true` is present. Proxy-forged Origin or curl output alone cannot establish browser exploitation; cookies and preflight may prevent it.

## Clickjacking

Source: [PortSwigger Clickjacking](https://portswigger.net/web-security/clickjacking).

- **Inspect:** sensitive framed UI, enforced CSP `frame-ancestors`, X-Frame-Options, nested framing and interactions requiring user gestures. Examine response policy on the actual sensitive page.
- **Validate:** in a controlled browser page, establish whether framing succeeds and whether a meaningful action can be induced with the victim's authentication and required confirmations.
- **Evidence:** show a feasible sensitive interaction within a permitted frame and the user-interaction prerequisites.
- **Fix:** enforce an appropriate `frame-ancestors` response header; use compatible framing controls where required. Preserve explicitly supported embedding through a narrow policy.
- **Example:** An account-deletion page with a single Confirm button and no `frame-ancestors` policy is framed invisibly over an attacker's "Play" button. `Content-Security-Policy: frame-ancestors 'self'` prevents it.
- **Avoid false positives:** missing X-Frame-Options is not a bypass if an enforced applicable `frame-ancestors` policy blocks framing. Frame-busting JavaScript is insufficient by itself. Mere frameability of public content may have no material impact; a CSP meta tag cannot supply framing protection.

## DOM-based vulnerabilities

Source: [PortSwigger DOM-based vulnerabilities](https://portswigger.net/web-security/dom-based).

- **Inspect:** URL/search/hash, storage, referrer and message data flowing to HTML/script sinks, navigation, requests, cookie/storage writes or DOM-clobberable properties. Include `postMessage` sender/receiver validation.
- **Validate:** trace a specific source-to-sink path and inspect intermediate parsers. For messages, verify `event.origin`, expected `event.source` and message shape; test a controlled foreign sender. For navigation/fetch, verify destinations and sensitive content rather than only a changed URL.
- **Evidence:** demonstrate the specific DOM effect: execution, unauthorized navigation, data disclosure or security-relevant state manipulation. Document victim interaction and origin requirements.
- **Fix:** use safe DOM APIs, parsed destination allowlists, exact message origin/source checks and structured message schemas. Avoid using mutable DOM/global names as security decisions.
- **Example:** `addEventListener('message', e => { if (e.origin.includes('partner.com')) box.innerHTML = e.data.html })` accepts messages from `https://partner.com.attacker.net`. The fix is an exact comparison (`e.origin === 'https://partner.com'`), a schema check on `e.data`, and `textContent` instead of `innerHTML`.
- **Avoid false positives:** DOM XSS overlaps the XSS topic; consolidate shared causes. `postMessage` existence or target origin `*` is not sufficient without sensitive data or a dangerous receive path.
