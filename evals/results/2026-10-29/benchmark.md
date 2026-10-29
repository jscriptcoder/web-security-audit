# Retry scores — 2026-10-29

| Dimension | With skill | Without skill |
| --- | --- | --- |
| Juice Shop root causes | 35/40 | 33/40 |
| WebGoat platform | 12/12 | 12/12 |
| WebGoat challenges | 6.5/7 | 7/7 |
| WebGoat lesson coverage | 33/34 | 34/34 |
| WebGoat calibration | 5/6 | 5/6 |

- One fresh matched pair per target. No within-configuration variance estimate or causal claim of skill improvement.
- WebGoat platform/challenges measure detection; lesson names reveal classes and the lesson score measures coverage. Calibration is separate.
- Viewer pass rates count full hits only. Weighted scores, including rubric half credit, are listed in benchmark.md and grading.json.
- No pooled pass rate across these different dimensions is reported.
- Same retained target hashes and skill revision as October 14; upstream commit provenance and scrub limitations remain unresolved.
- A8 uses the predeclared sanitization correction in grading-policy.md. Historical scores were not recomputed.
- Exact execution model/settings and tokens unavailable. Timings are auditor-reported elapsed values, not comparable cost telemetry.
