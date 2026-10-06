# Evals

Test cases for checking that the skill finds real issues and avoids false positives. Each fixture is a small, intentionally vulnerable application that also contains **traps**: safe code that looks dangerous. A good audit reports the planted issues and leaves the traps alone.

| Eval | Fixture | What it tests |
| --- | --- | --- |
| `frontend-only-react-audit` | `fixtures/react-shop/` | Frontend escape hatches, `postMessage`, open redirect, client-side path traversal, bundle secrets, partial-stack scope and backend handoffs |
| `spring-kotlin-backend-audit` | `fixtures/spring-orders/` | Object-level authorization, Kotlin string-template SQL injection, Actuator exposure, Java deserialization, XXE, reset-link poisoning, JWT validation, confidence labelling |
| `react-pr-diff-review` | `fixtures/pr-diff/` | Focused diff review: markdown rendering XSS, stored versus self-only impact, staying in scope |
| `graphql-monorepo-audit` | `fixtures/graphql-shop/` | Spring for GraphQL authorization across nested paths and batch loaders, alias brute force past a request-counting rate limit, cost limits, error leakage, Apollo cache persistence after logout, introspection calibration |
| `next-store-hard-audit` | `fixtures/next-store/` | Harder Next.js App Router fixture for detection: server secret inlined via `next.config.js` `env`, client-side path traversal chaining to account deletion, unscoped Server Action, sanitizer output mutated after DOMPurify, open redirect, service-worker caching of authenticated responses; traps for SameSite=Lax, escaped JSON-LD, React 19 `javascript:` hrefs and patched middleware |

`evals.json` holds the prompts and the expectations each report is graded against. The fixtures contain no comments marking the vulnerabilities, so keep the expectations out of the auditing agent's context.

## Running

With the skill-creator skill in Claude Code, ask it to run the evals in `evals/evals.json` with and without this skill. Copy the fixtures to a workspace outside the skill folder first, and tell the auditing agents not to open `evals/`, so they cannot read the expectations.

Without tooling: give each prompt to an agent with the skill installed, save the report, and check it against the eval's expectations by hand.

## Results so far

Each eval was run with the skill and without it (same model, same prompt), and the reports were graded against `evals.json`. Treat these as small samples, not benchmarks.

| Eval | Model | With skill | Without skill | Runs per config |
| --- | --- | --- | --- | --- |
| `frontend-only-react-audit` | Opus 5.5 | 14/14 | 13/14 | 1 |
| `spring-kotlin-backend-audit` | Opus 5.5 | 12/12 | 11/12 | 1 |
| `react-pr-diff-review` | Opus 5.5 | 6/6 | 6/6 | 1 |
| `graphql-monorepo-audit` | Opus 5.5 | 12/12 | 12/12 | 1 |
| `next-store-hard-audit` | Opus 4.8 | 16/16, 13/16 | 13/16, 13/16 | 2 |
| `next-store-hard-audit` | Opus 5.5 | 16, 16, 16 (current skill); 15, 16 (previous skill) | 15/16, 15/16 | 2–3 |

What the runs show:

- **The first four fixtures do not test detection.** The model found every planted bug with or without the skill. The differences were in calibration and reporting: confidence labels, severities held back where evidence was missing, backend suspicions kept as handoffs, a regression check per finding.
- **The reproducible gain on the harder fixture is calibration on look-alikes.** Across both models, every with-skill run treated the SameSite=Lax POST routes as protected; most no-skill runs reported them as a Medium CSRF finding. On Opus 4.8 the skill also stopped the React 19 `javascript:` href from being rated as XSS.
- **Detection of the client-side path traversal chain depends on the model.** On Opus 4.8 it was found in 1 of 4 runs. On Opus 5.5 it was found in all 7 runs, including both runs without the skill. The worked trace added to the skill afterwards therefore cannot be credited with the improvement; on Opus 5.5 it only shows no regression (3 of 3).
- **Some misses are noise.** The 2FA-not-enforced finding was missed in about one run in three, in every configuration.
- **Unplanted finding:** the fixture pins `next` 15.3.3 / `react` 19.1.0, which fall in the December 2025 React Server Components RCE advisory range. Most Opus 5.5 runs reported it. It is not graded because it depends on the review date.
- **Cost:** the skill used about 1.5× the tokens and 1.5–1.8× the wall time on the harder fixture.

Open work: a client-side path traversal fixture that the worked trace was not written against, and that the current model misses without the skill, to measure whether the trace helps.

## Broader testing

The fixtures are deliberately small. For larger, realistic targets, run the skill against intentionally vulnerable open-source applications in an isolated environment:

- [OWASP Juice Shop](https://github.com/juice-shop/juice-shop): Angular frontend with a Node.js backend
- [OWASP WebGoat](https://github.com/WebGoat/WebGoat): Java/Spring

Their public solution guides serve as the answer key; compare coverage and false positives rather than expecting every challenge to be found by source review.
