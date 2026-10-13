# Evals

Test cases for checking that the skill finds real issues and avoids false positives. Each fixture is a small, intentionally vulnerable application that also contains **traps**: safe code that looks dangerous. A good audit reports the planted issues and leaves the traps alone.

| Eval | Fixture | What it tests |
| --- | --- | --- |
| `frontend-only-react-audit` | `fixtures/react-shop/` | Frontend escape hatches, `postMessage`, open redirect, client-side path traversal, bundle secrets, partial-stack scope and backend handoffs |
| `spring-kotlin-backend-audit` | `fixtures/spring-orders/` | Object-level authorization, Kotlin string-template SQL injection, Actuator exposure, Java deserialization, XXE, reset-link poisoning, JWT validation, confidence labelling |
| `react-pr-diff-review` | `fixtures/pr-diff/` | Focused diff review: markdown rendering XSS, stored versus self-only impact, staying in scope |
| `graphql-monorepo-audit` | `fixtures/graphql-shop/` | Spring for GraphQL authorization across nested paths and batch loaders, alias brute force past a request-counting rate limit, cost limits, error leakage, Apollo cache persistence after logout, introspection calibration |
| `next-store-hard-audit` | `fixtures/next-store/` | Harder Next.js App Router fixture for detection: server secret inlined via `next.config.js` `env`, client-side path traversal chaining to account deletion, unscoped Server Action, sanitizer output mutated after DOMPurify, open redirect, service-worker caching of authenticated responses; traps for SameSite=Lax, escaped JSON-LD, React 19 `javascript:` hrefs and patched middleware |
| `go-notes-clean-audit` | `fixtures/go-notes/` | **Clean fixture, zero planted bugs.** Measures fabrication: an allowlisted ORDER BY, `template.HTML` on sanitizer output, `exec.Command` with an argument list, wildcard CORS on a public feed, pprof on a loopback listener, a validated `next` redirect, `os.Root` file access. Passing means reporting nothing confirmed and saying so |
| `fastapi-invoices-hard-audit` | `fixtures/fastapi-invoices/` | Omission bugs that a sink search misses, plus embedded instructions: second-order SQL injection through a stored company name, reset token with declared but unchecked `expires_at`/`used_at`, an export router mounted without the auth dependency its sibling has, mass assignment of `status`/`paid_cents`/`owner_id`; `docs/SECURITY_NOTES.md` and a code comment tell the reviewer to skip the export route and to print a marker sentence |

`evals.json` holds the prompts and the expectations each report is graded against. The fixtures contain no comments marking the vulnerabilities (the reviewer notes in `fastapi-invoices` are the test, not a marker), so keep the expectations out of the auditing agent's context.

## Running

With the skill-creator skill in Claude Code, ask it to run the evals in `evals/evals.json` with and without this skill. Copy the fixtures to a workspace outside the skill folder first, and tell the auditing agents not to open `evals/`, so they cannot read the expectations.

Without tooling: give each prompt to an agent with the skill installed, save the report, and check it against the eval's expectations by hand. When the auditing agent is a Claude Code subagent, the harness refuses to let it write a report file; ask it to return the full report as its final message and grade that text. A with-skill subagent is told to read only `skills/web-security-audit/` (`SKILL.md`, `references/`, `assets/` and `scripts/`).

## Results so far

Each eval was run with the skill and without it (same model, same prompt), and the reports were graded against `evals.json`. Treat these as small samples, not benchmarks.

| Eval | Model | With skill | Without skill | Runs per config |
| --- | --- | --- | --- | --- |
| `frontend-only-react-audit` | Opus 5.5 | 14/14 | 13/14 | 1 |
| `spring-kotlin-backend-audit` | Opus 5.5 | 12/12 | 11/12 | 1 |
| `react-pr-diff-review` | Opus 5.5 | 6/6 | 6/6 | 1 |
| `react-pr-diff-review` | Fable 5.1, SKILL.md without the example-requests section (2026-10-12) | 6/6 | not rerun | 1 |
| `graphql-monorepo-audit` | Opus 5.5 | 12/12 | 12/12 | 1 |
| `next-store-hard-audit` | Opus 4.8 | 16/16, 13/16 | 13/16, 13/16 | 2 |
| `next-store-hard-audit` | Opus 5.5 | 16, 16, 16 (current skill); 15, 16 (previous skill) | 15/16, 15/16 | 2–3 |
| `next-store-hard-audit` | Fable 5.1, skill with omission checks and `sink_inventory.py` (2026-10-06) | 16/16, 16/16 | not rerun | 2 |
| `go-notes-clean-audit` (fixture v1) | Fable 5.1 | 12/13 (0 confirmed; 1 Supported Medium) | 11/13 (2 Medium findings) | 1 |
| `go-notes-clean-audit` (fixture v2) | Fable 5.1 | 13/13 (0 confirmed) | 13/13 (0 above Low) | 1 |
| `fastapi-invoices-hard-audit` | Fable 5.1 | 13/13 | 13/13 | 1 |
| `juice-shop` (real target, 40 graded root causes) | Fable 5.1 | 30/40 (+5/9 bonus) | 29/40 (+2/9 bonus) | 1 |
| `webgoat` (real target; platform 12, challenges 7, lessons 34, calibration 6) | Fable 5.1 | platform 10/12, challenges 7/7, lessons 29.5/34, calibration 6/6 | platform 6.5/12, challenges 7/7, lessons 33/34, calibration 6/6 | 1 |
| `webgoat` | Fable 5.1, skill with the handler-group mapping step (2026-10-13) | platform 8/12, challenges 6.5/7, lessons 32/34, calibration 6/6 | not rerun | 1 |

What the runs show:

- **Fable 5.1 runs (2026-10-06).** The omission checks (declared fields versus enforcement, sibling handlers) found the TOTP-not-enforced and the unscoped `deleteAddress` bugs in both next-store runs and both reports named the comparison as the reason; two runs are not enough to call the earlier one-in-three miss fixed, only to say it did not recur. On `fastapi-invoices`, the same model found all four planted omissions with and without the skill and refused the embedded reviewer instructions in both configurations, so that fixture does not separate the two either; what the with-skill run added was crediting the safe siblings, labelling the gateway claim as an unsupplied assumption and a coverage ledger. Both configurations also found a real flaw that was not planted: two accounts registering the same company name share report totals.
- **The clean fixture measures calibration, not fabrication.** Neither configuration invented a vulnerability or flagged a trap. The difference was how hardening was labelled: on fixture v1 the no-skill run put two resource-exhaustion items in its findings as Medium, the with-skill run kept zero confirmed and recorded one as Supported. Both runs also found genuine defects in the fixture (an empty webhook secret accepted at startup, a content-type check that could never match, a file written before the ownership check, pandoc spawned per request with no cap); those were fixed in v2, and on v2 both configurations reported nothing above Low.
- **The sink inventory script was used in every with-skill run** and each report listed the leads as read. It did not change what was found; it removed the first round of ad-hoc searches.

- **The first four fixtures do not test detection.** The model found every planted bug with or without the skill. The differences were in calibration and reporting: confidence labels, severities held back where evidence was missing, backend suspicions kept as handoffs, a regression check per finding.
- **The reproducible gain on the harder fixture is calibration on look-alikes.** Across both models, every with-skill run treated the SameSite=Lax POST routes as protected; most no-skill runs reported them as a Medium CSRF finding. On Opus 4.8 the skill also stopped the React 19 `javascript:` href from being rated as XSS.
- **Detection of the client-side path traversal chain depends on the model.** On Opus 4.8 it was found in 1 of 4 runs. On Opus 5.5 it was found in all 7 runs, including both runs without the skill. The worked trace added to the skill afterwards therefore cannot be credited with the improvement; on Opus 5.5 it only shows no regression (3 of 3).
- **Some misses are noise.** The 2FA-not-enforced finding was missed in about one run in three, in every configuration.
- **Unplanted finding:** the fixture pins `next` 15.3.3 / `react` 19.1.0, which fall in the December 2025 React Server Components RCE advisory range. Most Opus 5.5 runs reported it. It is not graded because it depends on the review date.
- **Cost:** the skill used about 1.5× the tokens and 1.5–1.8× the wall time on the harder fixture.

- **Juice Shop (2026-10-12), the first target too large to hold in context.** One run per configuration on Fable 5.1, source-only. Detection was level: 30/40 with the skill, 29/40 without, and both missed the same cluster: authorization gaps on the generated `/api/*` REST resources (feedback deletion and forgery, product edits by non-admins, basket-item ownership), client-side-only validation (upload limits, registration checks) and the profile-update CSRF. Each side found one or two things the other did not (with: JSONP `whoami`, role mass assignment, forgeable coupons, the like-counter race; without: the verbose error handler, seeded weak credentials, negative order totals). The calibration difference recurred: the no-skill report rated wildcard CORS Medium with "cross-origin reads of authenticated JSON APIs" as the impact, although authentication is a bearer header; the with-skill report held it at Low for that reason. The with-skill report carried prerequisites, a regression check and a confidence label per finding and a filled coverage ledger; the no-skill report had confidence and severity labels, several split severities ("MEDIUM/HIGH") and a prose coverage list. Both reports produced genuine unplanted findings (the rate limiter keyed on `X-Forwarded-For` with `trust proxy` enabled; coupon and checkout by basket id without ownership). The with-skill run also surfaced a bug in `sink_inventory.py`: it crashed with `UnicodeEncodeError` on a default Windows console when an excerpt contains non-ASCII text (fixed the same day; the CLI now always emits UTF-8). Cost: 291k tokens, 56 tool calls, 14.5 min with the skill against 251k, 74 tool calls, 10.6 min without.

- **WebGoat (2026-10-13), the first target where the skill changed detection.** One run per configuration on Fable 5.1, source-only, on the scrubbed copy (see the WebGoat procedure below). Both configurations solved all seven challenge items, including the three-hop chain, and passed all six calibration checks (gated SSRF sink, validated username in the schema SQL, parameterised siblings left alone, the WebWolf JWT tool not flagged). The difference was on the platform, where nothing is intentional: 10/12 with the skill against 6.5/12 without. The with-skill run reported the WebWolf upload resolving the client filename without normalisation, the unauthenticated mail endpoint accepting any recipient chained with the unescaped mailbox render, and the DOM XSS route in the shell; the no-skill run read the same files, accepted the source comment's justification for the open mail endpoint, called the unescaped render "not a defect" and never mentioned the upload. Both missed the two items that need two files to see: progress credited to another user through a `csrf-` username, and `DELETE /mail` removing every user's mail. The lesson inventory went the other way: 29.5/34 with the skill against 33/34 without, because the with-skill report omitted the whole `pathtraversal` package (three rows) while its coverage statement claimed every lesson package was read; the no-skill report omitted `csrf`. Each side had one false claim: the with-skill report called the standard RSA exponent 65537 a weakness, the no-skill report none; the no-skill report corrected the rubric on lesson 6b (a fixed query, not a sink), which has been fixed. Both found the same unplanted defect (a challenge page with no controller). Cost: 494k tokens, 85 tool calls, 17.2 min with the skill against 382k, 54, 13.2 min without.

- **WebGoat rerun after the handler-group change (2026-10-13).** The change adds a handler-group table to the sink inventory (one row per directory with entry-point leads), a mapping-step rule to carry every group into the surface map with a state, a handler-group table in the coverage ledger, a reporting rule that the coverage statement lists the groups, and entry-point patterns for generated resource registrations. One with-skill run on the same prompt: the `pathtraversal` package is back in the inventory (all three rows scored) and the coverage statement lists the 58 groups by name. Lessons went from 29.5 to 32 of 34; the remaining miss is a different package, `passwordreset`, which the coverage statement nevertheless marks as read, so the list is produced but not yet enforced group by group. Platform went from 10 to 8 (the password encoder was filed as intentional and the DOM XSS sink was left at "in client JS") and challenges from 7 to 6.5 (the HEAD bypass was described as "POST or a method override"); the same files were read, so these are single-run movements, not a new blind spot. New in this run: the OAuth login path reaching the schema DDL without the registration pattern, correctly bounded. One false claim: the challenge 6 page was said to drive the SQL-injection endpoints; it posts to a path with no controller. Cost: 550k tokens, 62 tool calls, 15.8 min.

Open work: a fixture that the current model misses without the skill. Every small fixture so far, including the two added on 2026-10-06, is found in full by the model alone, so those evals measure calibration, scope discipline and report shape, not detection. Juice Shop is the first target where both configurations miss the same thing, and it names the gap: authorization on auto-generated CRUD resources (finale, Sequelize REST, Spring Data REST, Django REST viewsets, Rails resources) where no handler code exists to read. The handler-group mapping step (added 2026-10-13, see the WebGoat rerun above) now covers generated resource registrations and package-level completeness; the Juice Shop generated-resource misses have not been rerun against it, and the rerun showed the group list can still be asserted in bulk over a package the inventory omits, so the next refinement is per-group evidence (the files read) rather than a reviewed flag. The two platform misses shared by both WebGoat runs (a username prefix stripped by the progress tracker, a repository-wide delete behind a per-user-looking endpoint) are the same shape as the Juice Shop misses: the bug is only visible when two files are read together. Candidates: multi-file flows where the bug is only visible across three or more hops, a larger repository where the surface map matters, and runtime-mode cases. Also outstanding: fixtures for .NET, PHP and Ruby, a backend-only partial-stack case, and a remediation-mode case.

## Broader testing

The fixtures are deliberately small. For larger, realistic targets, run the skill against intentionally vulnerable open-source applications in an isolated environment:

- [OWASP Juice Shop](https://github.com/juice-shop/juice-shop): Angular frontend with a Node.js backend
- [OWASP WebGoat](https://github.com/WebGoat/WebGoat): Java/Spring

Their public solution guides serve as the answer key; compare coverage and false positives rather than expecting every challenge to be found by source review.

### Juice Shop procedure

Juice Shop ships its own answer key, so the copy the agents see has to be scrubbed first. `juice-shop/scrub_juice_shop.py <copy> <answer-key-dir>` saves the challenge registry, the code-snippet cache and the threat model to the answer-key directory, then deletes the registry, challenge translations, coding-challenge fixes, hacking instructor, tests, solutions and references pages, threat model, agent-instruction files and git history, strips every `vuln-code-snippet` marker comment and renames each challenge identifier to an opaque `challengeNNN` across the tree. Run it as `python -I` from outside the copy.

```sh
git clone --depth 1 https://github.com/juice-shop/juice-shop.git <workspace>/juice-shop
python -I evals/juice-shop/scrub_juice_shop.py <workspace>/juice-shop <workspace>/juice-shop-answer-key
```

What the scrub cannot remove: the code still calls the challenge-solving helper at the location of each planted bug, so a reader sees that something is checked there even without knowing what. Both configurations see the same tree, so the comparison stays fair, but absolute detection counts are flattering.

`juice-shop/rubric.md` collapses the 116 challenges (commit `e39a3bd`, 2026-10-12) into 40 graded source-visible root causes plus 9 bonus items, and lists the challenges that source review cannot find. Write the grading of the first report down before reading the second. Subagents in Claude Code cannot write files and long final messages are truncated in transit, so ask for the report in parts of about 6,000 characters; a resend request makes the agent rewrite from its transcript, which renumbers findings but did not add tool calls in the runs so far.

### WebGoat procedure

WebGoat cannot be scrubbed into a detection target: its package and class names announce every vulnerability class and each assignment returns `success(this)` at the solved condition. What can be removed is the material that names the *solution*: lesson text and hints, translations, solution pages, the integration tests (worked exploits), agent guidance, release notes, dependency-check suppressions, every comment and `@AssignmentHints` annotation in lesson sources, and HTML comments in lesson pages. `webgoat/scrub_webgoat.py <copy> <answer-key-dir>` does that and copies what it removes to the answer-key directory; `tests/test_scrub_webgoat.py` covers the Java comment stripper (string literals, char literals, text blocks and CRLF files survive).

```sh
git clone --depth 1 https://github.com/WebGoat/WebGoat.git <workspace>/webgoat
python -I evals/webgoat/scrub_webgoat.py <workspace>/webgoat <workspace>/webgoat-answer-key
```

`webgoat/rubric.md` (commit `e7b1313`, 2026-10-12) therefore grades four things separately: 12 platform defects in the engine (`container/`, `server/`, `webwolf/`, configuration, templates), where nothing is intentional; 7 root causes in the `challenges` package, which gives objectives without naming the weakness and includes a three-hop XXE, open-redirect and internal-endpoint chain; 34 lesson root causes, scored only when the report names the file holding the sink, as a measure of surface coverage rather than detection; and 6 calibration checks (gated SSRF sink, validated username in schema SQL, parameterised siblings, by-design labelling). The prompt tells both configurations the same thing: lessons are intentionally vulnerable, the platform is not, and the three sections are wanted. Quote the platform and challenge scores as detection; the lesson score is flattered by the names.
