# Frontend frameworks and single-page applications

Load with [browser security](browser-security.md) when frontend source, client bundles or SPA code is in scope. This file covers rendering, navigation, client-built requests and meta-framework server code. Token storage, logout, service workers, bundle secrets, third-party scripts and embedding are in [frontend runtime](frontend-runtime.md); load that file for a full frontend audit, not for a rendering-only diff review. Record findings under the matching Academy topic or the supplemental frontend row of the coverage ledger.

## Framework escape hatches

Modern frameworks escape text interpolation by default, so most real XSS sits in a small set of escape hatches. Search for these first, then trace each value back to its source.

| Framework | HTML/script escape hatches | URL and attribute leads | Notes |
| --- | --- | --- | --- |
| React | `dangerouslySetInnerHTML`, `ref.current.innerHTML`, `createContextualFragment` | `href`/`src`/`action`/`formAction` from user data | React 16.9–18 only warns on `javascript:` URLs; React 19 blocks them. Confirm the installed version. |
| Next.js | as React; `<Script>` with dynamic content | `redirect()`/`router.push()` with user input | See server rendering and Server Actions below. |
| Angular | `bypassSecurityTrustHtml/Url/ResourceUrl/Script/Style`, `ElementRef.nativeElement.innerHTML`, `Renderer2.setProperty(..., 'innerHTML')` | Angular sanitizes `[innerHTML]`, `[href]` and `[src]`; a bypass call disables that | AngularJS 1.x: user content inside `ng-app` is a [client-side template injection](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection) sink through `{{ }}`. |
| Vue / Nuxt | `v-html`, `innerHTML` in render functions/JSX | `:href`/`:src` are not URL-sanitized | Mounting Vue on server-rendered HTML that contains user input turns `{{ }}` into template injection; use `v-pre` or escape server-side. |
| Svelte / SvelteKit | `{@html}` | `href={value}` is not URL-sanitized | |
| SolidJS | `innerHTML` prop | | |
| Lit / web components | `unsafeHTML`, `unsafeSVG`, direct `shadowRoot.innerHTML` | | |
| jQuery / vanilla | `.html()`, `.append(string)`, `$(userInput)`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`, `setTimeout(string)` | `location = value`, `window.open(value)` | `$(userInput)` parses HTML when the string looks like markup. |

- **Validate:** confirm the value reaching the escape hatch is attacker-influenced (URL, storage, API data originating from other users, `postMessage`) and that no sanitizer runs on the final string. For URL attributes, check whether the scheme is validated after parsing, not by prefix.
- **Fix:** remove the escape hatch where possible; otherwise sanitize immediately before the sink with a maintained sanitizer and allowlist URL schemes (`http:`, `https:`, `mailto:` as needed) on a parsed `URL`.
- **Avoid false positives:** an escape hatch fed by a build-time constant, an i18n string bundled with the app, or output of a correctly configured sanitizer is not a finding. Angular's default sanitization is effective unless bypassed.

## Rich content: markdown, SVG and sanitizers

Source: [PortSwigger XSS contexts](https://portswigger.net/web-security/cross-site-scripting/contexts).

- **Inspect:** markdown renderers (`marked` does not sanitize; `markdown-it` with `html: true`; `react-markdown` with `rehype-raw` but no `rehype-sanitize`), rich-text editors and their stored HTML, user SVG, and sanitizer configuration such as DOMPurify `ADD_TAGS`, `ADD_ATTR`, `ALLOW_UNKNOWN_PROTOCOLS`, custom hooks and `SAFE_FOR_TEMPLATES` when a client template engine re-processes output.
- **Validate:** check the order of operations. Sanitizing and then concatenating, re-parsing, decoding or passing the result through another transform can reintroduce markup (mutation XSS). A regex or string replace that runs on sanitizer output and writes captured text into a tag or attribute is the common form. Confirm user SVG is shown through `<img>` (script-inert) and not inlined, embedded with `<object>`/`<embed>` or served for direct navigation from the app origin.
- **Fix:** sanitize as the final step before insertion, keep the sanitizer current, prefer a restrictive allowlist, and serve user-uploaded active formats from an isolated origin with `Content-Disposition: attachment` where appropriate.
- **Avoid false positives:** a markdown library with raw HTML disabled and safe link handling is not vulnerable just because it renders HTML.

## Server rendering, hydration and serialized state

- **Inspect:** state embedded into HTML for hydration, such as `<script>window.__STATE__ = ${JSON.stringify(data)}</script>`, `__NEXT_DATA__`, Nuxt payloads, React Server Component payloads and Angular `TransferState`.
- **Validate:** check that serialized state escapes `<` (for example as `<`) so a value containing `</script>` cannot break out. Check what data reaches the client: Next.js `getServerSideProps` props and objects passed from Server Components to Client Components are serialized into the page, including fields the UI never displays.
- **Evidence:** show markup breakout from the serialized state, or sensitive fields (other users' data, internal flags, secrets, password hashes) present in the payload for an identity that should not see them.
- **Fix:** use the framework's serializer or a safe serializer such as `serialize-javascript`; map server objects to explicit view models before passing them to client code; mark server-only modules with `import 'server-only'` where supported.
- **Avoid false positives:** data the current user is authorized to see is not a disclosure merely because it is in the payload rather than on screen.

## Server Actions, route handlers and edge middleware

Meta-frameworks put backend code in the frontend repository. Treat it as backend code and also load [identity and access](identity-access.md). Apply the sibling-handler comparison from the [methodology](methodology.md#compare-declared-controls-with-enforced-controls) across the actions that touch one resource.

- **Inspect:** Next.js Server Actions (`'use server'`), route handlers, SvelteKit form actions and `+server` endpoints, Nuxt server routes and Remix actions/loaders. Each is a reachable HTTP endpoint independent of whether the UI shows the button.
- **Validate:** confirm every action and loader authenticates the caller and authorizes the specific object, rather than relying on the page that renders it. Check whether authorization lives only in edge middleware. Middleware-only enforcement is fragile; Next.js [CVE-2025-29927](https://nvd.nist.gov/vuln/detail/CVE-2025-29927) allowed skipping middleware with a forged `x-middleware-subrequest` header in self-hosted deployments before 12.3.5, 13.5.9, 14.2.25 and 15.2.3. Check the installed version and hosting model.
- **Fix:** enforce authentication and object authorization inside each action/loader or in a shared data-access layer they all call; keep middleware for routing and coarse checks. Review `serverActions.allowedOrigins` and framework CSRF settings.
- **Avoid false positives:** Next.js compares `Origin` and `Host` for Server Actions; do not report missing CSRF tokens without showing that the built-in check is disabled or bypassable for the deployment.

## Client-side navigation and open redirects

Source: [PortSwigger DOM-based open redirection](https://portswigger.net/web-security/dom-based/open-redirection). Server-emitted redirects are in [browser security](browser-security.md#open-redirects-server-side).

- **Inspect:** `returnUrl`, `next`, `redirect`, `continue` and similar parameters flowing to `location.href`, `location.assign/replace`, `window.open`, router navigation, `<meta http-equiv="refresh">` and post-login/logout redirects, including OAuth callback handling.
- **Validate:** test absolute (`https://other.example`), protocol-relative (`//other.example`), backslash (`/\other.example`) and `javascript:` values against the actual router. Determine whether the router treats each as in-app or external navigation.
- **Evidence:** show navigation to an attacker origin (phishing or token-leak chain) or script execution through a `javascript:` URL. Note when OAuth codes or tokens can leak through the redirect.
- **Fix:** resolve with `new URL(value, location.origin)` and require `url.origin === location.origin`, or map to an allowlist of route names.
- **Avoid false positives:** a redirect restricted to same-origin paths is intended behavior. A standalone open redirect without a chain is usually Low.

## Client-side path traversal (CSPT)

Source: [Doyensec CSPT2CSRF research](https://blog.doyensec.com/2024/07/02/cspt2csrf.html).

- **Inspect:** user-controlled values interpolated into API paths, such as ``fetch(`/api/orders/${params.id}`)`` or `axios.get('/api/files/' + name)`, where the frontend attaches credentials, an `Authorization` header or a CSRF token. Sources include route params, search params, the hash, storage and data returned by other users.
- **Validate:** follow the trace below for every such sink. Do not stop at the endpoint the code intends to call: that endpoint's own authorization says nothing about the endpoint the request can be redirected to.
- **Evidence:** show the request reaching an unintended endpoint with the victim's credentials and the resulting effect or response handling, such as attacker-chosen JSON rendered unsafely.
- **Fix:** apply `encodeURIComponent` to every path segment and validate identifier format (for example UUID or numeric) before building the URL.
- **Avoid false positives:** the sink is safe when every interpolated segment goes through `encodeURIComponent` or a strict format check before the URL is built. A traversal that only reaches GET endpoints returning the user's own data has little impact; record it as hardening unless a chain is evidenced.

### Worked trace

Take this component, reached at `/projects/archive?project=<value>`:

```tsx
const project = useSearchParams().get('project') ?? '';
await fetch(`/api/projects/${encodeURI(project)}/archive`, { method: 'PUT', body: JSON.stringify({ reason }) });
```

1. **Encoding.** `encodeURI` leaves `/`, `?`, `#` and `.` unencoded, so it does not confine the value to one path segment. Treat no encoding, string concatenation and `encodeURI` the same way. React Router and Next.js decode route params, so `%2F` in a route param also arrives as `/`.
2. **Resolve the final URL.** Pick a value with dot segments and a `?` or `#` that cuts off the fixed suffix, and resolve it the way the browser does: `new URL(path, origin)`. With `project=../team/members/7/remove?`, the path `/api/projects/../team/members/7/remove?/archive` resolves to `/api/team/members/7/remove` with the query `?/archive`. Check the arithmetic: each `..` removes one segment, and the `?` moves the suffix out of the path.
3. **List what the request can reach.** Collect the same-origin routes that accept this method (here `PUT`) and authenticate with credentials the browser or the app attaches automatically: cookies, or an `Authorization` header added by the API client. Rank them by impact: deletion, ownership or membership changes, email or password changes, payments.
4. **Ignore the intended route's checks.** An ownership check in `/api/projects/[id]/archive` does not protect `/api/team/...`. What matters is whether the reached route accepts an authenticated request with this method and an empty or attacker-shaped body.
5. **Ignore SameSite and CSRF tokens.** The request is same-origin and sent by the application, so SameSite cookies, Origin checks and tokens the client attaches all pass.
6. **Rate it** by the reached route's impact and the interaction needed (opening a link, clicking a button on the page). A link plus one click that removes a team member, deletes an account or changes an email address is a real finding, not a Low encoding nit.

## Scriptless injection

Source: [PortSwigger Dangling markup injection](https://portswigger.net/web-security/cross-site-scripting/dangling-markup).

- **Inspect:** HTML injection points where CSP or sanitization blocks script but allows tags, attributes or styles: unclosed `<img src='//attacker/?`, `<base>` tags, `<form action>`, `<meta>` refresh and CSS attribute-selector exfiltration of tokens or values.
- **Evidence:** show sensitive page content (a CSRF token, personal data) leaving to an attacker-controlled destination, or a form/base hijack that changes where data is sent.
- **Fix:** fix the injection rather than relying on CSP; add CSP `base-uri`, `form-action` and restrictive `img-src`/`style-src` as defense in depth.

## Starting searches

```text
Browser sinks: dangerouslySetInnerHTML|\.innerHTML|bypassSecurityTrust|v-html|\{@html|unsafeHTML|unsafeSVG|insertAdjacentHTML|document\.write|\.html\(|createContextualFragment|\beval\(|new Function\(
Rich content: marked\(|marked\.parse|markdown-it|MarkdownIt|rehype-raw|DOMPurify|sanitize\(
Navigation: location\.(href|assign|replace)|window\.open\(|router\.(push|replace)|redirect\(|returnUrl|returnTo|\bnext\b.*searchParams|searchParams.*\bnext\b
Client requests: fetch\(`|axios\.(get|post|put|patch|delete)\(|encodeURI\(|credentials: ?['"]include|withCredentials
Messages and storage: addEventListener\(['"]message|onmessage|postMessage\(|localStorage|sessionStorage|serviceWorker\.register
Server code in the frontend repo: ['"]use server['"]|['"]server-only['"]|export (async )?function (GET|POST|PUT|PATCH|DELETE)|\+server\.|defineEventHandler|export const (action|loader)
```
