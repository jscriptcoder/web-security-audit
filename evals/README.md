# Evals

Test cases for checking that the skill finds real issues and avoids false positives. Each fixture is a small, intentionally vulnerable application that also contains **traps**: safe code that looks dangerous. A good audit reports the planted issues and leaves the traps alone.

| Eval | Fixture | What it tests |
| --- | --- | --- |
| `frontend-only-react-audit` | `fixtures/react-shop/` | Frontend escape hatches, `postMessage`, open redirect, client-side path traversal, bundle secrets, partial-stack scope and backend handoffs |
| `spring-kotlin-backend-audit` | `fixtures/spring-orders/` | Object-level authorization, Kotlin string-template SQL injection, Actuator exposure, Java deserialization, XXE, reset-link poisoning, JWT validation, confidence labelling |
| `react-pr-diff-review` | `fixtures/pr-diff/` | Focused diff review: markdown rendering XSS, stored versus self-only impact, staying in scope |
| `graphql-monorepo-audit` | `fixtures/graphql-shop/` | Spring for GraphQL authorization across nested paths and batch loaders, alias brute force past a request-counting rate limit, cost limits, error leakage, Apollo cache persistence after logout, introspection calibration |

`evals.json` holds the prompts and the expectations each report is graded against. The fixtures contain no comments marking the vulnerabilities, so keep the expectations out of the auditing agent's context.

## Running

With the skill-creator skill in Claude Code, ask it to run the evals in `evals/evals.json` with and without this skill. Copy the fixtures to a workspace outside the skill folder first, and tell the auditing agents not to open `evals/`, so they cannot read the expectations.

Without tooling: give each prompt to an agent with the skill installed, save the report, and check it against the eval's expectations by hand.

## Broader testing

The fixtures are deliberately small. For larger, realistic targets, run the skill against intentionally vulnerable open-source applications in an isolated environment:

- [OWASP Juice Shop](https://github.com/juice-shop/juice-shop): Angular frontend with a Node.js backend
- [OWASP WebGoat](https://github.com/WebGoat/WebGoat): Java/Spring

Their public solution guides serve as the answer key; compare coverage and false positives rather than expecting every challenge to be found by source review.
