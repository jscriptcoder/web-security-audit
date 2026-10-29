# Completed Juice Shop and WebGoat retry — 2026-10-29

All four source-only audits completed: one fresh with-skill/without-skill pair per target. The skill scored two more Juice Shop root causes in this pair. WebGoat platform detection tied; the baseline covered more challenge and lesson mechanisms. One pair per target does not establish a repeatable skill effect.

| Dimension | With skill | Without skill |
| --- | --- | --- |
| Juice Shop root causes | **35/40** | **33/40** |
| Juice Shop bonus | **6/9** | **6/9** |
| WebGoat platform detection | **12/12** | **12/12** |
| WebGoat challenge detection | **6.5/7** | **7/7** |
| WebGoat lesson coverage | **33/34** | **34/34** |
| WebGoat calibration | **5/6** | **5/6** |

The [review viewer](review.html) presents the reports and formal grades. Its binary pass rates count full hits; the table above and per-item JSON preserve WebGoat half credit. No aggregate across detection, labelled lesson coverage and calibration is reported.

## Reports and grading evidence

| Run | Report | Process notes | Final grade |
| --- | --- | --- | --- |
| Juice Shop with skill | [Report](eval-juice-shop/with_skill/outputs/report.md) | [Process](eval-juice-shop/with_skill/outputs/process.md) | [Grade](eval-juice-shop/with_skill/grading.json) |
| Juice Shop without skill | [Report](eval-juice-shop/without_skill/outputs/report.md) | [Process](eval-juice-shop/without_skill/outputs/process.md) | [Grade](eval-juice-shop/without_skill/grading.json) |
| WebGoat with skill | [Report](eval-webgoat/with_skill/outputs/report.md) | [Process](eval-webgoat/with_skill/outputs/process.md) | [Grade](eval-webgoat/with_skill/grading.json) |
| WebGoat without skill | [Report](eval-webgoat/without_skill/outputs/report.md) | [Process](eval-webgoat/without_skill/outputs/process.md) | [Grade](eval-webgoat/without_skill/grading.json) |

The [manifest](manifest.json) retains common prompts, source/skill fingerprints, available model information, permissions, scheduling and interruption history. Per-target metadata is retained for [Juice Shop](eval-juice-shop/eval_metadata.json) and [WebGoat](eval-webgoat/eval_metadata.json). [Verification](verification.json) confirms the target copies and skill files were unchanged after the runs. [Artifact hashes](artifact-hashes.json) cover the retained evidence files; directory-local Git attributes preserve their bytes across checkouts. Auditor reports retain their original whitespace. The target trees themselves are not included.

## What differed

**Juice Shop.** Both reports earned G19–G24, including the generated-API authorization cluster missed in earlier runs. The with-skill report additionally identified server-side registration validation bypass (G13, WSA-046) and the substring-based redirect allowlist (G38). Both missed the specific complaint-upload validation issue (G11), seeded weak credentials (G27), explicit plaintext TOTP storage (G31), legacy JWT algorithm acceptance (G33), and established vulnerable/typosquatted dependencies (G40). Both reported TOTP disclosure and qualified unverified library behavior; these misses are not false-positive claims.

**WebGoat.** Both reports earned all 12 platform points, including upload traversal, public mail injection, cross-user mail deletion and the registrable `csrf-` progress-identity collision. The with-skill report named the challenge 1 PIN/image classes but omitted the embedded-byte disclosure mechanism (B1, half credit). Its lesson inventory left unsigned JWT acceptance unresolved (C7, half credit) and named the restriction-bypass lesson only at package level rather than its sink class (C23, half credit). The baseline established those mechanisms. Both failed D5's explicit training-configuration/pin-label expectation; this is not a finding that either report exaggerated lesson severity.

**Calibration and verification.** Both configurations recorded source/runtime boundaries, prerequisites and unreviewed scope. Targeted semantic checks found no confirmed false positives, but did not independently validate every claim; no zero-false-positive rate is established. Reports also contain findings outside the rubrics. Those checked by graders are identified in the grade files, separately from unverified hypotheses. No application, browser exploit or deployed-service test was run.

## Grading decisions and limits

The [grading policy](grading-policy.md) records the initial rules and subsequent adjudication. The first report's grade was saved before its counterpart was opened. Juice Shop baseline received a coordinator grade and an independent check; the other reports received independent graders, with coordinator review of ambiguities. Full execution transcripts are unavailable; process logs are self-reported.

- **Juice Shop G31:** require the plaintext-storage root cause rather than infer it from seed disclosure. Broader matching adds one core point to both configurations and leaves the two-point difference unchanged.
- **Juice Shop bonuses:** credit the explicitly listed public-IaC subcase and actual same-origin active-SVG publication under B8's “or similar” wording in both reports. A delivery-address-only interpretation removes one bonus point from each. The [baseline independent grade](eval-juice-shop/without_skill/grading-independent.json), [initial coordinator grade](eval-juice-shop/without_skill/grading-coordinator-initial.json), and [with-skill independent grade](eval-juice-shop/with_skill/grading-independent.json) retain the original decisions.
- **WebGoat A8:** the predeclared correction credits exposed metadata/detailed health, not unproven unsanitized secret values. Historical scores remain unchanged.
- **WebGoat C31:** grading revealed that `LogSpoofingTask` returns HTML feedback rather than writing a log. Both reports correctly distinguished it from `LogBleedingTask`. The source correction was applied equally and its discovery timing is recorded.
- **WebGoat baseline A5/B4:** coordinator review accepted its explicit “deliberate lesson exceptions” wording and its class/line identification of the served `.git` archive. Requiring a particular subsection or a verbatim complete URI would reject substantive evidence. The [independent grade](eval-webgoat/without_skill/grading-independent.json) retains the original half credits.

## Provenance and comparability

The audits used the unchanged skill at revision `9884636a8d31072c16f6b900df5897b365ece235` and the retained source copies from October 14. Both target hashes matched before and after the retry. Their upstream commits still cannot be certified: the original scrub removed Git history without retaining a source manifest. The known retained frontend-spec and challenge-helper/name leakage and the WebGoat comment-stripper edge case remain unresolved. These are completed comparisons on the same retained trees, not repaired or newly pinned fixtures.

Auditors started with fresh contexts and no rubric, historical findings or peer reports. Isolation was instruction-scoped, not a separate filesystem boundary. With-skill auditors could read only the assigned target and audit skill; baselines received no skill. Audit delegation was disabled. The three available worker slots required the WebGoat baseline to start after the Juice Shop baseline. Two initial Juice Shop launches were interrupted before saved outputs existed and were restarted fresh; the completed reports were not continuations of those discarded contexts.

The execution model and settings were inherited from the current Codex session; exact identifiers were not exposed. Do not label these runs as the historical GPT 6 Astra or Fable runs, or infer improvement across those model/prompt combinations. Token telemetry was unavailable. The baselines self-reported elapsed intervals of 1,354.5 seconds for Juice Shop and 2,152 seconds for WebGoat; these are not independently measured cost comparisons. No additional audit time, token or finding cap was imposed.

The skill, scanners, scrubbers, original rubrics and target applications were not changed. This artifact set records the retry and its grading; implementation work proposed in the October 14 handoff remains separate.
