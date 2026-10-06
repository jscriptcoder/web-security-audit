# Web security audit coverage

Scope/revision/environment: [value]
States: `reviewed`, `not-applicable`, `blocked`, `not-reviewed`.
Keep rows at `not-reviewed` until triaged. In Evidence/reason, name the inspected surface and check, the absence establishing non-applicability, or the blocker. A reviewed row records a bounded check, not a guarantee.

Anything the requested scope excludes gets no state. Delete a status column the mode excludes (for example the Runtime status column in a source-only review) and say so once in the omitted-scope line. For a partial-stack or focused review, keep only the rows in scope. `blocked` means in scope but prevented; `not-reviewed` means in scope but not yet done. See the methodology for the full rule.

Rows follow the resource groups in SKILL.md so each block can be completed with one reference loaded. Essential skills is methodology, not a vulnerability class, so it has no row.

| Group | Academy topic | Source status | Runtime status | Evidence/reason |
| --- | --- | --- | --- | --- |
| Identity and access | Authentication | not-reviewed | not-reviewed | |
| Identity and access | Access control | not-reviewed | not-reviewed | |
| Identity and access | OAuth authentication | not-reviewed | not-reviewed | |
| Identity and access | JWT attacks | not-reviewed | not-reviewed | |
| Browser security | Cross-site scripting (XSS) | not-reviewed | not-reviewed | |
| Browser security | Cross-site request forgery (CSRF) | not-reviewed | not-reviewed | |
| Browser security | Cross-origin resource sharing (CORS) | not-reviewed | not-reviewed | |
| Browser security | Clickjacking | not-reviewed | not-reviewed | |
| Browser security | DOM-based vulnerabilities | not-reviewed | not-reviewed | |
| Injection | SQL injection | not-reviewed | not-reviewed | |
| Injection | NoSQL injection | not-reviewed | not-reviewed | |
| Injection | Command injection | not-reviewed | not-reviewed | |
| Injection | XXE injection | not-reviewed | not-reviewed | |
| Injection | Server-side template injection | not-reviewed | not-reviewed | |
| Files and data | Path traversal | not-reviewed | not-reviewed | |
| Files and data | File upload vulnerabilities | not-reviewed | not-reviewed | |
| Files and data | Information disclosure | not-reviewed | not-reviewed | |
| Files and data | Insecure deserialization | not-reviewed | not-reviewed | |
| APIs and realtime | API testing | not-reviewed | not-reviewed | |
| APIs and realtime | WebSockets | not-reviewed | not-reviewed | |
| GraphQL | GraphQL API vulnerabilities | not-reviewed | not-reviewed | |
| Business logic | Business logic vulnerabilities | not-reviewed | not-reviewed | |
| Business logic | Race conditions | not-reviewed | not-reviewed | |
| HTTP infrastructure | Server-side request forgery (SSRF) | not-reviewed | not-reviewed | |
| HTTP infrastructure | Web cache deception | not-reviewed | not-reviewed | |
| HTTP infrastructure | Web cache poisoning | not-reviewed | not-reviewed | |
| HTTP infrastructure | HTTP Host header attacks | not-reviewed | not-reviewed | |
| HTTP infrastructure | HTTP request smuggling | not-reviewed | not-reviewed | |
| Prototype pollution | Prototype pollution | not-reviewed | not-reviewed | |
| LLM integrations | Web LLM attacks | not-reviewed | not-reviewed | |

Omitted scope (excluded dimensions such as runtime testing, the other side of a partial-stack review, or surfaces outside a focused review): [value]

## Supplemental platform checks

| Check | Source status | Runtime status | Evidence/reason |
| --- | --- | --- | --- |
| Declared security fields versus enforcement; sibling handlers compared | not-reviewed | not-reviewed | |
| Credentials and cryptography (password hashing, token generation, comparisons, encryption) | not-reviewed | not-reviewed | |
| SAML / enterprise SSO | not-reviewed | not-reviewed | |
| Server-side open redirects | not-reviewed | not-reviewed | |
| Frontend framework and SPA rendering checks | not-reviewed | not-reviewed | |
| Frontend runtime: bundle secrets, tokens and logout, service workers, third-party scripts | not-reviewed | not-reviewed | |
| Dependencies and shared packages | not-reviewed | not-reviewed | |
| Browser policy and session cookies | not-reviewed | not-reviewed | |
| Deployment, secrets and service controls | not-reviewed | not-reviewed | |
