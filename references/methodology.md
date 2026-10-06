# Audit methodology and essential skills

## Establish the working context

Record the audit mode, targets, revision/environment, relevant roles and tenants, exclusions, and permitted runtime actions. Reuse authorization already supplied. A repository review authorizes reading that repository; it does not establish scope for testing unrelated deployed services. If runtime scope is unclear, continue source/configuration review and list the missing information.

Choose the mode from available evidence:

| Mode | Primary evidence | Practical limit |
| --- | --- | --- |
| Source review | Routes, middleware, resolvers, components, infrastructure and tests | Deployment behavior may differ; label assumptions |
| Runtime review | Scoped application, browser behavior, requests and responses, test identities | Server internals may be unknown |
| Combined | Source plus the corresponding running build | Correlate the deployed version before joining evidence |

For a monorepo, map applications, shared packages, API services and edge configuration. Trace shared security helpers into their callers; inspect all relevant consumers before calling a helper safe or unsafe. Prefer the user's specified app/diff scope over an unsolicited whole-repository review.

## Partial-stack scope

Many audits cover only one side of the application, for example a frontend repository whose API lives elsewhere. Treat this as a focused review: assess what the available code can establish, list the other side as omitted scope in one line, and do not fill the ledger with `blocked` rows for topics that belong to code you were never given.

**Frontend-only.** Client code can establish or rule out:

- XSS, DOM-based vulnerabilities, client-side template injection, `postMessage` handling and client-side prototype pollution
- Client-side open redirects and client-side path traversal ([frontend frameworks](frontend-frameworks.md))
- Secrets and sensitive data in bundles, source maps and serialized state
- The OAuth/OIDC client side: PKCE, `state`/nonce handling, redirect handling, token storage, refresh and logout
- Token exposure to scripts, service-worker caching and logout cleanup
- Framing, CSP and other headers when hosting configuration (for example `nginx.conf`, `vercel.json`, `netlify.toml`, `_headers` or CDN config) is in the repository
- CSRF prerequisites on the client side: credential mode (`credentials: 'include'`, `withCredentials`), custom headers and anti-CSRF token handling
- Rendering of WebSocket, GraphQL and LLM output; frontend dependencies and third-party scripts
- Meta-framework server code (Server Actions, route handlers, loaders), which is backend code and gets the full backend checks

Client code often reveals backend design, such as an API that accepts `ownerId`, `role` or `price` in the body, an ID-based fetch with no visible scoping, or a GraphQL mutation exposing privileged fields. These are **handoff hypotheses** for the backend owner, not findings: record the endpoint, the suspected rule and the exact server-side check to perform in the report's hypotheses section. Client-side checks such as route guards or hidden buttons are never evidence that the server enforces or omits a rule.

**Backend-only.** Server code can establish authorization, injection, file, deserialization, SSRF, cache and header behavior. Browser-facing topics depend on how a client consumes responses: assess what the server controls (response content types, CSP and framing headers, cookie attributes, CORS policy, CSRF enforcement, encoding of data in server-rendered HTML) and record client rendering of API data as a handoff hypothesis for the frontend owner.

In both cases, state the omitted side in the scope section so a reader does not mistake a partial audit for a full one.

## Build an attack-surface map

Start with manifests, route definitions, API schemas, authentication configuration and deployment files. Use `rg --files` and focused `rg -n` queries; exclude generated/vendor output unless the finding concerns deployed bundles. Search results are leads, not findings.

Identify each stack from its manifests (`package.json`, `pom.xml`, `build.gradle(.kts)`, `pyproject.toml`, `*.csproj`, `go.mod`, `composer.json`, `Gemfile`) and load the matching [stack hints](stacks/README.md) for entry points, enforcement locations, dangerous APIs and safe framework defaults. For frontend code, load [frontend frameworks](frontend-frameworks.md). If no stack file matches, derive equivalent leads from the framework's documentation using these stack-neutral categories:

```text
Entry points: route/controller/handler registration, resolvers, message and job consumers
Enforcement: authentication middleware, authorization annotations/guards/policies, tenant or owner scoping in data access
Browser sinks: raw HTML insertion, script evaluation, URL navigation, postMessage listeners
Interpreters: raw SQL/query strings, shell execution, native deserialization, template compilation, expression evaluation, XML parsers
Infrastructure: proxy/forwarded-header trust, cache rules, CORS policy, outbound HTTP clients, webhooks
```

Trace attacker-controlled sources through transformations to sensitive sinks. Include stored values, database results originating from users, uploaded documents, webhook inputs and third-party API results. Record encodings and parsing at each boundary; a validator before decoding may protect a different representation from the one ultimately consumed.

Build a compact table: surface, entry point, identity, sensitive operation, trust boundary, relevant topic, evidence location. Include background jobs, exports, downloads and realtime handlers when present.

## Essential skills

Source: [PortSwigger Essential skills](https://portswigger.net/web-security/essential-skills).

Preserve both raw and decoded requests when comparing behavior. Identify whether URL, JSON, HTML or XML decoding occurs at the browser, proxy, framework or interpreter. Test a decoding hypothesis with a small, controlled pair rather than a broad encoding spray. If Burp is available and permitted, use captured requests and targeted insertion points; manually validate scanner output. Treat response variation caused by rejected syntax as a clue until it reaches the suspected security boundary.

## Validate a hypothesis

1. State the violated rule: who may perform which operation on which object/state.
2. Locate the entry point, transformation, enforcement and sink. Search for centralized controls and framework defaults before alleging missing protection.
3. Establish a baseline. Change one relevant factor and retain a negative control.
4. Use synthetic objects and accounts. Prefer a local integration test or controlled request to expansive scanning.
5. Capture the unauthorized effect or a complete source-level path. Recheck identity, tenant, deployment, caching and response contents.
6. Separate reproduction from inference. A timing anomaly, HTTP 200, error, reflected marker or scanner alert alone rarely proves impact.

For access control, use owner A, non-owner B and a privileged account if supplied; test across tenants as well as within one tenant. For browser-origin issues, a proxy can alter headers a browser cannot: reproduce the relevant browser constraints before claiming a browser exploit.

Avoid executing repository scripts until their effects are understood. Inspect scanner options, authentication and scope before use. Stop a runtime experiment if it affects another user, writes outside test data or shows unexpected load; continue with source analysis or an isolated reproduction.

## Track coverage and resume efficiently

For a full audit, use the coverage asset linked from SKILL.md. Use these exact states:

- `reviewed`: perform the stated check and record evidence; this does not mean universally secure.
- `not-applicable`: identify why the relevant feature is absent within the inspected scope.
- `blocked`: identify an applicable check prevented by missing evidence/access or a runtime constraint.
- `not-reviewed`: identify remaining applicable or untriaged work.

Never convert lack of credentials, tooling or deployment visibility into `not-applicable`. Track source and runtime coverage separately in each row. For a focused or partial-stack review, track only the requested surfaces and name the omitted scope once; `blocked` is for applicable checks within scope that could not be completed.

For long audits, maintain a compact checkpoint in the host's normal artifact location: scope/revision, surface map, loaded resources, completed checks, evidence pointers, current hypotheses, next actions and blockers. Reopen the relevant resource when resuming; avoid copying entire references or raw traffic into the checkpoint. Reconcile findings against the current revision before finalizing.
