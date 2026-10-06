# Evidence, severity and reporting

## Classify the evidence

Keep confidence separate from severity:

| Confidence | Required support |
| --- | --- |
| Confirmed | Controlled reproduction of a security effect, or a complete source-level proof with reachable input, enforcement and sink established |
| Supported | Concrete code/configuration path with a material deployment or behavior assumption still unresolved |
| Hypothesis | A plausible lead requiring additional evidence; exclude from confirmed totals |

Explicitly label `source-proven` versus `runtime-reproduced`; do not imply requests were executed when they were only proposed. Give each finding one confidence classification. A source-proven primitive is not automatically a confirmed exploit: if the security effect depends on an unresolved material control or prerequisite, classify the finding as Supported and describe the proven path separately. For example, unsafe HTML insertion can be source-proven while script execution remains unverified because effective browser policy is unknown. Distinguish an observation about hardening from an exploitable vulnerability. Record known positive controls when they explain a false positive.

Before publishing a finding, check:

1. Is the entry point reachable by the stated attacker?
2. Is the input controllable in the actual browser/protocol/runtime?
3. Is an existing control applied before the sensitive operation?
4. Does the evidence show a security rule violation rather than only unexpected behavior?
5. Are the prerequisites, uncertainty and actual impact stated?

## Assign severity

Use application-specific impact and feasible prerequisites. Prefer these qualitative levels unless the user requires a formal score:

| Level | Typical rationale; adapt to the application |
| --- | --- |
| Critical | Broad compromise, major privileged execution or systemic sensitive-data access with few practical barriers |
| High | Meaningful account takeover, unauthorized sensitive access or privileged actions with realistic prerequisites |
| Medium | Material but constrained confidentiality, integrity or availability impact |
| Low | Limited impact requiring substantial constraints or a small security weakness |
| Informational | Hardening or useful context without a demonstrated security violation |

Do not inherit the Academy topic's possible maximum impact or a scanner's severity. Explain what this application's evidence supports. State a separate remediation priority where exposure, breadth or fix dependencies change ordering. If CVSS is requested, use the requested version, provide the vector and justify each metric; verify current official definitions before scoring.

## Write actionable findings

Use stable identifiers, such as `WSA-001`. Each finding needs title, severity/rationale, confidence, affected surface, evidence type, attacker prerequisites, reproduction or source trace, observed/expected behavior, bounded impact, remediation and a regression check. Add a relevant Academy/primary source link. Include CWE only when the mapping is clear; do not invent identifiers.

Point to exact source files and lines or sanitized request/response excerpts. Include revision and environment. Redact cookies, credentials, tokens, private keys and personal data; retain enough structure to reproduce with synthetic values. Do not put real secrets into URLs, browser tools, external scanners or reports. If a secret is found, record its type/location and recommend rotation without printing its value.

Group duplicate manifestations by shared root cause and list affected consumers. Describe an exploit chain only when each link is evidenced; separate the demonstrated chain from plausible extensions. Credit backend controls even if the frontend looks permissive.

Recommend fixes at the enforcement boundary: server authorization, parameter binding, safe rendering, canonical parsing or cache policy. UI hiding, opaque identifiers, disabled introspection or a WAF may reduce exposure but rarely repair the underlying rule. Give a concrete regression check that fails before the fix and passes after it.

## Deliver the audit

Use the report asset linked from SKILL.md for a full report. Adapt detail to the request; for a small diff review, a concise finding list and coverage statement may suffice. Lead with the meaningful findings, then the evidence, fixes, coverage and limitations. Include a prioritized next-action list and unresolved hypotheses without inflating confirmed counts.

When no issues are found, say which surfaces, roles and checks were reviewed and which remain blocked. Do not claim the application is secure or certify compliance from a limited audit. If remediation was requested, report the changes and targeted regression results separately from the original finding.
