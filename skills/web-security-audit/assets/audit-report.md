# Web security audit — [application]

## Summary

[State the important observed risks and immediate actions. Give confirmed finding totals by severity, with supported findings and hypotheses separately.]

## Scope and method

- Target/revision/environment: [value]
- Mode: [source / runtime / combined]
- Surfaces, roles and tenants: [value]
- Runtime actions covered by the supplied scope: [value]
- Exclusions and material assumptions: [value]
- Evidence collected and tests actually run: [value]

## Findings

[Required for every finding: severity and rationale, confidence and evidence type, affected surface, attacker prerequisites, evidence or source trace, impact and limits, remediation, regression check. For Low and Informational items, the expected/observed and reproduction lines may be folded into the evidence line; do not pad them.]

### WSA-001 — [concrete problem]

- Severity and rationale: [value]
- Confidence and evidence type: [confirmed/supported; source-proven/runtime-reproduced]
- Affected surface: [route/component/service and file:line or traffic reference]
- Attacker prerequisites: [identity, access, user interaction, deployment conditions]
- Expected behavior: [security rule]
- Observed behavior: [supported result]
- Reproduction/source trace: [minimal synthetic steps; baseline and negative control]
- Evidence: [sanitized excerpt/reference; actual execution result]
- Impact and limits: [demonstrated scope; unresolved assumptions]
- Remediation: [specific control and enforcement location]
- Regression check: [unauthorized case fails; permitted case still works]
- Reference: [relevant primary source; CWE if established]

## Coverage

[Insert or link the coverage ledger. Keep source/runtime coverage distinct when both are in scope; drop a column the requested mode excluded and say so once. Explain not-applicable, blocked and not-reviewed rows.]

## Hypotheses and hardening observations

[Keep unconfirmed leads and informational improvements outside confirmed totals. State the next validation step.]

### Cross-team handoffs

[For partial-stack audits: suspected issues in code outside the reviewed scope. For each, give the owning team, the endpoint or component, the suspected rule violation, what in the reviewed code suggests it, and the exact check to perform.]

## Prioritized actions

| Priority | Action | Related finding | Verification |
| --- | --- | --- | --- |
| [value] | [value] | [value] | [value] |

## Limitations

[State inaccessible deployments, missing roles, unexecuted runtime checks and version uncertainty. Describe what this audit supports.]
