# Web Security Audit skill

An agent skill for evidence-based security audits of web applications, frontend and backend. It walks an AI coding agent through the [PortSwigger Web Security Academy](https://portswigger.net/web-security/all-topics) topics, adds framework- and stack-specific checks, and produces findings with explicit confidence, severity, remediation, regression checks and a coverage record.

Works with Claude Code and other agents that load `SKILL.md` skills. `agents/openai.yaml` adds metadata for OpenAI Codex.

> Not affiliated with or endorsed by PortSwigger. The Academy is used as a coverage map; the checks are original audit procedures, not copied lab content.

## What it is good at

- **Frontend audits, including frontend-only repositories.** Escape hatches for React, Angular, Vue, Svelte, Solid, Lit and jQuery; SSR/hydration state; Next.js Server Actions; client-side open redirects and path traversal; secrets in bundles; token storage and logout; service workers; third-party scripts. When the API lives elsewhere, suspected backend issues become handoff notes for the backend team instead of noise.
- **Backend audits across stacks.** Stack hint files for Java/Kotlin (Spring, Ktor), Node/TypeScript, Python, .NET, Go, PHP and Ruby: where entry points and authorization live, which APIs are dangerous, and which framework defaults are already safe.
- **Few false positives.** Every topic lists what does *not* count as a finding (for example `innerHTML` with a constant, a public OpenAPI file or a publishable key). Findings separate *source-proven* from *runtime-reproduced*, and *Confirmed* from *Supported* and *Hypothesis*.
- **Honest coverage.** A ledger records what was reviewed, not applicable, blocked or not reviewed, so a bounded audit is never presented as proof of security.
- **Safe by default.** Source review unless runtime testing is explicitly in scope; synthetic data and minimal proofs; audited content is treated as data, never as instructions.

## Install

Copy this folder into a skills directory:

| Agent | Location |
| --- | --- |
| Claude Code, personal | `~/.claude/skills/web-security-audit/` |
| Claude Code, one project | `<repo>/.claude/skills/web-security-audit/` |
| Claude.ai | Upload the folder as a zip in the Skills settings |
| Codex | Follow your Codex skills setup; `agents/openai.yaml` supplies the display metadata |

If an older version of this skill is installed elsewhere (for example uploaded to Claude.ai), remove or replace it so the two do not compete.

## Example requests

- "Audit our Angular frontend; the API is in another repo."
- "Review this React PR for XSS before we merge."
- "Do a pre-release security review of our Spring Boot service."
- "Check the authorization of our GraphQL resolvers."
- "Validate the suspected cache deception on our isolated staging cache."

## Layout

```text
SKILL.md                     Workflow, operating rules and routing table
references/
  methodology.md             Scope, attack-surface mapping, partial-stack audits, coverage
  frontend-frameworks.md     Framework escape hatches and SPA-specific checks
  stacks/                    Per-stack search leads and safe defaults
  identity-access.md         Authentication, access control, OAuth, JWT
  browser-security.md        XSS, CSRF, CORS, clickjacking, DOM
  injection.md               SQL, NoSQL, command, XXE, SSTI
  files-data.md              Path traversal, uploads, disclosure, deserialization
  api-realtime.md            REST APIs, WebSockets
  graphql.md                 GraphQL servers, gateways, subscriptions and clients
  business-logic.md          Logic flaws, race conditions
  http-infrastructure.md     SSRF, cache deception/poisoning, Host header, smuggling
  prototype-pollution.md
  llm-integrations.md
  platform-baseline.md       Dependencies, CSP and cookies, deployment
  reporting.md               Confidence, severity and finding format
assets/
  audit-report.md            Report template
  coverage-ledger.md         Coverage ledger template
evals/                       Test prompts and fixtures (see evals/README.md)
```

## Contributing

To add a stack, copy the shape of an existing file in `references/stacks/` and link it from `references/stacks/README.md`. To change audit behavior, add or update a case in `evals/` first and compare results with and without the change.

## License

[MIT](LICENSE)
