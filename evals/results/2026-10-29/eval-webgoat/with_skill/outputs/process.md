# Audit process and coverage record

## Scope and constraints

Source-only review dated 2026-10-29 of `C:/Users/User/Projects/web-security-audit-workspace/webgoat`. No Git revision available (`git rev-parse HEAD` failed; no metadata supplied). Target treated as read-only. No application startup, build, dependency installation, tests, browser operation, network request or deployed-service interaction was performed. No agents were delegated by this audit worker. Reads were restricted to the supplied target, the named audit skill directory, and this worker's own output artifacts. No other skills, eval inputs, historical reports or external answer keys were opened.

## Tools and sequence

- Read the supplied SKILL.md and relevant methodology/reporting/Java-stack/reference/template/coverage resources. Resources used: methodology; reporting; stacks README and Java hints; identity-access; browser-security; platform-baseline; files-data; injection; http-infrastructure; api-realtime; business-logic; frontend-frameworks; frontend-runtime; assets/audit-report.md and assets/coverage-ledger.md.
- Inspected and ran the supplied `scripts/sink_inventory.py` read-only against the target; saved `inventory.json`. Its search hits and heuristic handler groups were treated as leads, then compared with manual source reading.
- Used PowerShell Get-Content and rg enumeration/search. Used a local Python helper (`read_source.py`) to emit source with original line numbers and append file requests. Later helper output omitted blank/import/package/comment-only lines for compactness; it did not rewrite target files.
- Traced platform authentication/authorization, account provisioning/reset, datasource/schema setup, mail, progress, file uploads/static serving, traces and templates; then all challenge/lesson Java handlers and helpers. Compared sibling handlers and declared security fields against enforcement. Inspected all shared templates and first-party goatApp/WebWolf JS; selected lesson JS and migrations/configuration.
- Saved an incremental evidence checkpoint and read log. Expanded into `report-final.md` drafting source and final `report.md`; retained raw inventory/helper/read-log as process artifacts. Final source-anchor existence/line bounds checked by local Python, not by starting the app.

## Tool errors and evidence limits

- Initial large combined output and a later WebAuthn batch were truncated. Follow-up smaller reads covered the affected substantive classes/handlers. The raw log records requested reads and may contain duplicates; it is not byte-coverage instrumentation. Manual review focused on executable code and relevant templates/configuration.
- A few rg calls used Windows wildcard paths or the wrong working directory and failed; searches were repeated against explicit target directories. The inventory output was UTF-16 from PowerShell redirection; an initial UTF-8 read failed and was retried correctly.
- Replacing the early report through apply_patch failed because that checkpoint used legacy Windows text encoding. A new UTF-8 draft was written and finalized successfully; no target source mutation occurred.
- No source tests were present: `src/test` does not exist and no *Test* files were found in target enumeration. All regression checks in the report are recommendations, not executed results.
- Framework defaults (including HEAD dispatch/JPA generated-ID merging/recorder redaction/parser behavior), browser cookies/HTML execution, provider identities, actual DB grants/network reach and concurrency were not validated. Findings explicitly separate these assumptions from source proof. No CVE/version-specific advisory or dependency-resolution claim is made.
- No wall-clock audit timing or model token accounting was recorded; none is reported.

## Coverage totals

- 334 / 334 Java files in `src/main/java` were included in manual source-reading batches.
- 404 distinct target files are recorded below by the line-numbered helper; `pom.xml` was additionally inspected for manifest/dependency/build configuration (selected content, not asserted byte-complete).
- 58 heuristic handler groups were reconciled; all their Java handlers were read. Group counts are inventory heuristic counts, not runtime route counts.
- 158 source anchors in the final report were checked for an existing file and in-range original line number.

## Handler-group ledger

| Directory | Heuristic handler files | State | Evidence |
|---|---:|---|---|
| `src/main/java/org/owasp/webgoat/container` | 3 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/container/assignments` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/container/controller` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/container/lessons` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/container/mailbox` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/container/report` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/container/service` | 9 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/container/users` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/authbypass` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/bypassrestrictions` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/challenges` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/challenges/challenge1` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2` | 4 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/challenges/challenge5` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/challenges/challenge7` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/challenges/challenge8` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/chromedevtools` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/cia` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/clientsidefiltering` | 4 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/commandinjection` | 8 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/cryptography` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/cryptography/timing` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/csrf` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/deserialization` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/hijacksession` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/htmltampering` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/httpbasics` | 4 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/httpparameterpollution` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/httpproxies` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/idor` | 6 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/insecurelogin` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/jwt` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/jwt/claimmisuse` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/lessontemplate` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/logging` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/missingac` | 4 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/openredirect` | 8 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/passwordreset` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/passwordstorage` | 6 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/pathtraversal` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/securepasswords` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/securitymisconfiguration` | 4 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/spoofcookie` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/sqlinjection/advanced` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction` | 9 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation` | 6 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/ssrf` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/vulnerablecomponents` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/webauthn` | 6 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/webgoatintroduction` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/webwolfintroduction` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/xss` | 6 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/xss/mitigation` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/xss/stored` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/lessons/xxe` | 5 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/webwolf` | 2 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/webwolf/jwt` | 1 | reviewed | All Java files in this group read; see file ledger. |
| `src/main/java/org/owasp/webgoat/webwolf/requests` | 2 | reviewed | All Java files in this group read; see file ledger. |

## Reviewed file ledger

Paths below are relative to the target root. Read denotes line-numbered source/template inspection; comments/import-only lines were suppressed in later batches. Duplicate requests are retained in `read-log.md` but deduplicated here. `pom.xml` was inspected for manifest/version/dependency/build configuration, not asserted byte-complete.

- `Dockerfile`
- `pom.xml`
- `src/main/java/org/dummy/insecure/framework/VulnerableTaskHolder.java`
- `src/main/java/org/owasp/webgoat/container/AjaxAuthenticationEntryPoint.java`
- `src/main/java/org/owasp/webgoat/container/AsciiDoctorTemplateResolver.java`
- `src/main/java/org/owasp/webgoat/container/CurrentUser.java`
- `src/main/java/org/owasp/webgoat/container/CurrentUsername.java`
- `src/main/java/org/owasp/webgoat/container/DatabaseConfiguration.java`
- `src/main/java/org/owasp/webgoat/container/HammerHead.java`
- `src/main/java/org/owasp/webgoat/container/LessonDataSource.java`
- `src/main/java/org/owasp/webgoat/container/LessonResourceScanner.java`
- `src/main/java/org/owasp/webgoat/container/LessonTemplateResolver.java`
- `src/main/java/org/owasp/webgoat/container/MvcConfiguration.java`
- `src/main/java/org/owasp/webgoat/container/ProxyAutoConfigController.java`
- `src/main/java/org/owasp/webgoat/container/UserInterceptor.java`
- `src/main/java/org/owasp/webgoat/container/WebGoat.java`
- `src/main/java/org/owasp/webgoat/container/WebSecurityConfig.java`
- `src/main/java/org/owasp/webgoat/container/WebWolfRedirect.java`
- `src/main/java/org/owasp/webgoat/container/asciidoc/EnvironmentExposure.java`
- `src/main/java/org/owasp/webgoat/container/asciidoc/OperatingSystemMacro.java`
- `src/main/java/org/owasp/webgoat/container/asciidoc/UsernameMacro.java`
- `src/main/java/org/owasp/webgoat/container/asciidoc/WebGoatTmpDirMacro.java`
- `src/main/java/org/owasp/webgoat/container/asciidoc/WebGoatVersionMacro.java`
- `src/main/java/org/owasp/webgoat/container/asciidoc/WebWolfMacro.java`
- `src/main/java/org/owasp/webgoat/container/asciidoc/WebWolfRootMacro.java`
- `src/main/java/org/owasp/webgoat/container/assignments/AssignmentEndpoint.java`
- `src/main/java/org/owasp/webgoat/container/assignments/AssignmentHints.java`
- `src/main/java/org/owasp/webgoat/container/assignments/AttackResult.java`
- `src/main/java/org/owasp/webgoat/container/assignments/AttackResultBuilder.java`
- `src/main/java/org/owasp/webgoat/container/assignments/AttackResultMessageResponseBodyAdvice.java`
- `src/main/java/org/owasp/webgoat/container/assignments/LessonTrackerInterceptor.java`
- `src/main/java/org/owasp/webgoat/container/controller/StartLesson.java`
- `src/main/java/org/owasp/webgoat/container/controller/Welcome.java`
- `src/main/java/org/owasp/webgoat/container/i18n/Language.java`
- `src/main/java/org/owasp/webgoat/container/i18n/Messages.java`
- `src/main/java/org/owasp/webgoat/container/i18n/PluginMessages.java`
- `src/main/java/org/owasp/webgoat/container/lessons/Assignment.java`
- `src/main/java/org/owasp/webgoat/container/lessons/Category.java`
- `src/main/java/org/owasp/webgoat/container/lessons/CourseConfiguration.java`
- `src/main/java/org/owasp/webgoat/container/lessons/Hint.java`
- `src/main/java/org/owasp/webgoat/container/lessons/Initializable.java`
- `src/main/java/org/owasp/webgoat/container/lessons/Lesson.java`
- `src/main/java/org/owasp/webgoat/container/lessons/LessonConnectionInvocationHandler.java`
- `src/main/java/org/owasp/webgoat/container/lessons/LessonInfoModel.java`
- `src/main/java/org/owasp/webgoat/container/lessons/LessonMenuItem.java`
- `src/main/java/org/owasp/webgoat/container/lessons/LessonMenuItemType.java`
- `src/main/java/org/owasp/webgoat/container/lessons/LessonName.java`
- `src/main/java/org/owasp/webgoat/container/mailbox/Email.java`
- `src/main/java/org/owasp/webgoat/container/mailbox/MailboxController.java`
- `src/main/java/org/owasp/webgoat/container/mailbox/MailboxRepository.java`
- `src/main/java/org/owasp/webgoat/container/report/ReportCardController.java`
- `src/main/java/org/owasp/webgoat/container/service/EnvironmentService.java`
- `src/main/java/org/owasp/webgoat/container/service/HintService.java`
- `src/main/java/org/owasp/webgoat/container/service/LabelDebugService.java`
- `src/main/java/org/owasp/webgoat/container/service/LabelService.java`
- `src/main/java/org/owasp/webgoat/container/service/LessonInfoService.java`
- `src/main/java/org/owasp/webgoat/container/service/LessonMenuService.java`
- `src/main/java/org/owasp/webgoat/container/service/LessonProgressService.java`
- `src/main/java/org/owasp/webgoat/container/service/RestartLessonService.java`
- `src/main/java/org/owasp/webgoat/container/service/SessionService.java`
- `src/main/java/org/owasp/webgoat/container/session/Course.java`
- `src/main/java/org/owasp/webgoat/container/session/LabelDebugger.java`
- `src/main/java/org/owasp/webgoat/container/session/LessonSession.java`
- `src/main/java/org/owasp/webgoat/container/users/AdminController.java`
- `src/main/java/org/owasp/webgoat/container/users/AssignmentProgress.java`
- `src/main/java/org/owasp/webgoat/container/users/DefaultUserInitializer.java`
- `src/main/java/org/owasp/webgoat/container/users/LessonProgress.java`
- `src/main/java/org/owasp/webgoat/container/users/RegistrationController.java`
- `src/main/java/org/owasp/webgoat/container/users/UserForm.java`
- `src/main/java/org/owasp/webgoat/container/users/UserProgress.java`
- `src/main/java/org/owasp/webgoat/container/users/UserProgressRepository.java`
- `src/main/java/org/owasp/webgoat/container/users/UserRepository.java`
- `src/main/java/org/owasp/webgoat/container/users/UserService.java`
- `src/main/java/org/owasp/webgoat/container/users/UserSession.java`
- `src/main/java/org/owasp/webgoat/container/users/UserValidator.java`
- `src/main/java/org/owasp/webgoat/container/users/WebGoatUser.java`
- `src/main/java/org/owasp/webgoat/lessons/authbypass/AccountVerificationHelper.java`
- `src/main/java/org/owasp/webgoat/lessons/authbypass/AuthBypass.java`
- `src/main/java/org/owasp/webgoat/lessons/authbypass/VerifyAccount.java`
- `src/main/java/org/owasp/webgoat/lessons/bypassrestrictions/BypassRestrictions.java`
- `src/main/java/org/owasp/webgoat/lessons/bypassrestrictions/BypassRestrictionsFieldRestrictions.java`
- `src/main/java/org/owasp/webgoat/lessons/bypassrestrictions/BypassRestrictionsFrontendValidation.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/ChallengeIntro.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/Email.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/Flag.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/FlagController.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/Flags.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/SolutionConstants.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge1/Assignment1.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge1/Challenge1.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge1/ImageServlet.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/Assignment2.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/ChainedFetchService.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/ChainedXmlService.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/Challenge2.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/Challenge2State.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/FeedImportEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/InternalDiagnostic.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge2/NorthstarEndpoints.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge5/Assignment5.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge5/Challenge5.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge7/Assignment7.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge7/Challenge7.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge7/MD5.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge7/PasswordResetLink.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge8/Assignment8.java`
- `src/main/java/org/owasp/webgoat/lessons/challenges/challenge8/Challenge8.java`
- `src/main/java/org/owasp/webgoat/lessons/chromedevtools/ChromeDevTools.java`
- `src/main/java/org/owasp/webgoat/lessons/chromedevtools/NetworkDummy.java`
- `src/main/java/org/owasp/webgoat/lessons/chromedevtools/NetworkLesson.java`
- `src/main/java/org/owasp/webgoat/lessons/cia/CIA.java`
- `src/main/java/org/owasp/webgoat/lessons/cia/CIAQuiz.java`
- `src/main/java/org/owasp/webgoat/lessons/clientsidefiltering/ClientSideFiltering.java`
- `src/main/java/org/owasp/webgoat/lessons/clientsidefiltering/ClientSideFilteringAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/clientsidefiltering/ClientSideFilteringFreeAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/clientsidefiltering/Salaries.java`
- `src/main/java/org/owasp/webgoat/lessons/clientsidefiltering/ShopEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandExecutionService.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjection.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionCatService.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionSafetyGate.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionSafetyService.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask1.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask2.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask3Flag.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask3Search.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask3Service.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask4Key.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask4Search.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask4Service.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask5Evaluation.java`
- `src/main/java/org/owasp/webgoat/lessons/commandinjection/CommandInjectionTask5Service.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/CryptoUtil.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/Cryptography.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/EncodingAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/HashingAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/SecureDefaultsAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/SigningAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/XOREncodingAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/InsecureHmacValidator.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttackFirstByteAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttackMitigationAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttackNoiseAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttackOracle.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttackSessionState.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttackSupport.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttackTagAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/cryptography/timing/TimingAttacks.java`
- `src/main/java/org/owasp/webgoat/lessons/csrf/CSRF.java`
- `src/main/java/org/owasp/webgoat/lessons/csrf/CSRFConfirmFlag1.java`
- `src/main/java/org/owasp/webgoat/lessons/csrf/CSRFFeedback.java`
- `src/main/java/org/owasp/webgoat/lessons/csrf/CSRFGetFlag.java`
- `src/main/java/org/owasp/webgoat/lessons/csrf/CSRFLogin.java`
- `src/main/java/org/owasp/webgoat/lessons/csrf/ForgedReviews.java`
- `src/main/java/org/owasp/webgoat/lessons/csrf/Review.java`
- `src/main/java/org/owasp/webgoat/lessons/deserialization/InsecureDeserialization.java`
- `src/main/java/org/owasp/webgoat/lessons/deserialization/InsecureDeserializationTask.java`
- `src/main/java/org/owasp/webgoat/lessons/deserialization/SerializationHelper.java`
- `src/main/java/org/owasp/webgoat/lessons/hijacksession/HijackSession.java`
- `src/main/java/org/owasp/webgoat/lessons/hijacksession/HijackSessionAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/hijacksession/cas/Authentication.java`
- `src/main/java/org/owasp/webgoat/lessons/hijacksession/cas/AuthenticationProvider.java`
- `src/main/java/org/owasp/webgoat/lessons/hijacksession/cas/HijackSessionAuthenticationProvider.java`
- `src/main/java/org/owasp/webgoat/lessons/htmltampering/HtmlTampering.java`
- `src/main/java/org/owasp/webgoat/lessons/htmltampering/HtmlTamperingTask.java`
- `src/main/java/org/owasp/webgoat/lessons/httpbasics/HttpBasics.java`
- `src/main/java/org/owasp/webgoat/lessons/httpbasics/HttpBasicsExternal.java`
- `src/main/java/org/owasp/webgoat/lessons/httpbasics/HttpBasicsForm.java`
- `src/main/java/org/owasp/webgoat/lessons/httpbasics/HttpBasicsLesson.java`
- `src/main/java/org/owasp/webgoat/lessons/httpbasics/HttpBasicsQuiz.java`
- `src/main/java/org/owasp/webgoat/lessons/httpparameterpollution/HttpParameterPollution.java`
- `src/main/java/org/owasp/webgoat/lessons/httpparameterpollution/ParameterPollutionMitigation.java`
- `src/main/java/org/owasp/webgoat/lessons/httpparameterpollution/ParameterPollutionObservation.java`
- `src/main/java/org/owasp/webgoat/lessons/httpparameterpollution/ParameterPollutionTransfer.java`
- `src/main/java/org/owasp/webgoat/lessons/httpproxies/HttpBasicsInterceptRequest.java`
- `src/main/java/org/owasp/webgoat/lessons/httpproxies/HttpProxies.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/IDOR.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/IDORDiffAttributes.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/IDOREditOtherProfile.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/IDORLogin.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/IDORViewOtherProfile.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/IDORViewOwnProfile.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/IDORViewOwnProfileAltUrl.java`
- `src/main/java/org/owasp/webgoat/lessons/idor/UserProfile.java`
- `src/main/java/org/owasp/webgoat/lessons/insecurelogin/InsecureLogin.java`
- `src/main/java/org/owasp/webgoat/lessons/insecurelogin/InsecureLoginTask.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/JWT.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/JWTDecodeEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/JWTQuiz.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/JWTRefreshEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/JWTSecretKeyEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/JWTVotesEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/claimmisuse/JWTHeaderJKUEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/claimmisuse/JWTHeaderKIDEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/votes/Views.java`
- `src/main/java/org/owasp/webgoat/lessons/jwt/votes/Vote.java`
- `src/main/java/org/owasp/webgoat/lessons/lessontemplate/LessonTemplate.java`
- `src/main/java/org/owasp/webgoat/lessons/lessontemplate/SampleAttack.java`
- `src/main/java/org/owasp/webgoat/lessons/logging/LogBleedingTask.java`
- `src/main/java/org/owasp/webgoat/lessons/logging/LogSpoofing.java`
- `src/main/java/org/owasp/webgoat/lessons/logging/LogSpoofingTask.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/DisplayUser.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/MissingAccessControlUserRepository.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/MissingFunctionAC.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/MissingFunctionACHiddenMenus.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/MissingFunctionACUsers.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/MissingFunctionACYourHash.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/MissingFunctionACYourHashAdmin.java`
- `src/main/java/org/owasp/webgoat/lessons/missingac/User.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirect.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectMitigationCheck.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectQuiz.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectRealRedirect.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectSecureController.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectTask1.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectTask2.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectTask3.java`
- `src/main/java/org/owasp/webgoat/lessons/openredirect/OpenRedirectTask4.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/PasswordReset.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/PasswordResetEmail.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/QuestionsAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/ResetLinkAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/ResetLinkAssignmentForgotPassword.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/SecurityQuestionAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/SimpleMailAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/TriedQuestions.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordreset/resetlink/PasswordChangeForm.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/PasswordStorage.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/PasswordStorageDataController.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/PasswordStorageService.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/Stage1HashAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/Stage2SaltAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/Stage3Argon2Assignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/Stage4PepperAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/passwordstorage/Stage5DisclosureAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/pathtraversal/PathTraversal.java`
- `src/main/java/org/owasp/webgoat/lessons/pathtraversal/ProfileUpload.java`
- `src/main/java/org/owasp/webgoat/lessons/pathtraversal/ProfileUploadBase.java`
- `src/main/java/org/owasp/webgoat/lessons/pathtraversal/ProfileUploadFix.java`
- `src/main/java/org/owasp/webgoat/lessons/pathtraversal/ProfileUploadRemoveUserInput.java`
- `src/main/java/org/owasp/webgoat/lessons/pathtraversal/ProfileUploadRetrieval.java`
- `src/main/java/org/owasp/webgoat/lessons/pathtraversal/ProfileZipSlip.java`
- `src/main/java/org/owasp/webgoat/lessons/securepasswords/SecurePasswords.java`
- `src/main/java/org/owasp/webgoat/lessons/securepasswords/SecurePasswordsAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/securitymisconfiguration/ActuatorExposureTask.java`
- `src/main/java/org/owasp/webgoat/lessons/securitymisconfiguration/ConfigHardeningTask.java`
- `src/main/java/org/owasp/webgoat/lessons/securitymisconfiguration/DefaultCredentialsTask.java`
- `src/main/java/org/owasp/webgoat/lessons/securitymisconfiguration/SecurityMisconfiguration.java`
- `src/main/java/org/owasp/webgoat/lessons/securitymisconfiguration/VerboseErrorTask.java`
- `src/main/java/org/owasp/webgoat/lessons/spoofcookie/SpoofCookie.java`
- `src/main/java/org/owasp/webgoat/lessons/spoofcookie/SpoofCookieAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/spoofcookie/encoders/EncDec.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/advanced/SqlInjectionAdvanced.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/advanced/SqlInjectionChallenge.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/advanced/SqlInjectionChallengeLogin.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/advanced/SqlInjectionLesson6a.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/advanced/SqlInjectionLesson6b.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/advanced/SqlInjectionQuiz.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjection.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson10.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson2.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson3.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson4.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson5.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson5a.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson5b.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson8.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/introduction/SqlInjectionLesson9.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation/Servers.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation/SqlInjectionLesson10a.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation/SqlInjectionLesson10b.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation/SqlInjectionLesson13.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation/SqlInjectionMitigations.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation/SqlOnlyInputValidation.java`
- `src/main/java/org/owasp/webgoat/lessons/sqlinjection/mitigation/SqlOnlyInputValidationOnKeywords.java`
- `src/main/java/org/owasp/webgoat/lessons/ssrf/SSRF.java`
- `src/main/java/org/owasp/webgoat/lessons/ssrf/SSRFTask1.java`
- `src/main/java/org/owasp/webgoat/lessons/ssrf/SSRFTask2.java`
- `src/main/java/org/owasp/webgoat/lessons/vulnerablecomponents/Contact.java`
- `src/main/java/org/owasp/webgoat/lessons/vulnerablecomponents/ContactImpl.java`
- `src/main/java/org/owasp/webgoat/lessons/vulnerablecomponents/VulnerableComponents.java`
- `src/main/java/org/owasp/webgoat/lessons/vulnerablecomponents/VulnerableComponentsLesson.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/Cbor.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/GoatBankCeremonyEndpoints.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/SecurityKeyCeremonyEndpoints.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/VirtualAuthenticator.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/WebAuthn.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/WebAuthnAuthenticationAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/WebAuthnLessonState.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/WebAuthnQuiz.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/WebAuthnRegistrationAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/WebAuthnSecurityKeyAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/webauthn/WebAuthnSupport.java`
- `src/main/java/org/owasp/webgoat/lessons/webgoatintroduction/Email.java`
- `src/main/java/org/owasp/webgoat/lessons/webgoatintroduction/MailAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/webgoatintroduction/WebGoatIntroduction.java`
- `src/main/java/org/owasp/webgoat/lessons/webwolfintroduction/LandingAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/webwolfintroduction/WebWolfIntroduction.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/Comment.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/CrossSiteScripting.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/CrossSiteScriptingLesson1.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/CrossSiteScriptingLesson5a.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/CrossSiteScriptingLesson6a.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/CrossSiteScriptingQuiz.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/DOMCrossSiteScripting.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/DOMCrossSiteScriptingVerifier.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/mitigation/CrossSiteScriptingLesson3.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/mitigation/CrossSiteScriptingLesson4.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/mitigation/CrossSiteScriptingMitigation.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/stored/CrossSiteScriptingStored.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/stored/StoredCrossSiteScriptingVerifier.java`
- `src/main/java/org/owasp/webgoat/lessons/xss/stored/StoredXssComments.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/BlindSendFileAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/Comment.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/CommentsCache.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/CommentsEndpoint.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/ContentTypeAssignment.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/Ping.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/SimpleXXE.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/User.java`
- `src/main/java/org/owasp/webgoat/lessons/xxe/XXE.java`
- `src/main/java/org/owasp/webgoat/server/ParentConfig.java`
- `src/main/java/org/owasp/webgoat/server/StartWebGoat.java`
- `src/main/java/org/owasp/webgoat/webwolf/FileServer.java`
- `src/main/java/org/owasp/webgoat/webwolf/FileUploadExceptionAdvice.java`
- `src/main/java/org/owasp/webgoat/webwolf/MvcConfiguration.java`
- `src/main/java/org/owasp/webgoat/webwolf/WebSecurityConfig.java`
- `src/main/java/org/owasp/webgoat/webwolf/WebWolf.java`
- `src/main/java/org/owasp/webgoat/webwolf/jwt/JWTController.java`
- `src/main/java/org/owasp/webgoat/webwolf/jwt/JWTToken.java`
- `src/main/java/org/owasp/webgoat/webwolf/requests/LandingPage.java`
- `src/main/java/org/owasp/webgoat/webwolf/requests/Requests.java`
- `src/main/java/org/owasp/webgoat/webwolf/requests/WebWolfTraceRepository.java`
- `src/main/java/org/owasp/webgoat/webwolf/user/UserRepository.java`
- `src/main/java/org/owasp/webgoat/webwolf/user/UserService.java`
- `src/main/java/org/owasp/webgoat/webwolf/user/WebWolfUser.java`
- `src/main/resources/application-webgoat.properties`
- `src/main/resources/application-webwolf.properties`
- `src/main/resources/db/container/V1__init.sql`
- `src/main/resources/db/container/V2__email_read_flag.sql`
- `src/main/resources/db/container/V3__allow_shared_assignments.sql`
- `src/main/resources/lessons/challenges/html/Challenge6.html`
- `src/main/resources/lessons/challenges/js/challenge2.js`
- `src/main/resources/lessons/challenges/js/challenge6.js`
- `src/main/resources/lessons/challenges/js/challenge8.js`
- `src/main/resources/lessons/insecurelogin/js/credentials.js`
- `src/main/resources/lessons/openredirect/js/openredirect-task4.js`
- `src/main/resources/lessons/ssrf/js/credentials.js`
- `src/main/resources/lessons/xss/js/assignment3.js`
- `src/main/resources/lessons/xss/js/assignment4.js`
- `src/main/resources/lessons/xss/js/stored-xss.js`
- `src/main/resources/webgoat/static/js/goatApp/controller/LessonController.js`
- `src/main/resources/webgoat/static/js/goatApp/controller/MenuController.js`
- `src/main/resources/webgoat/static/js/goatApp/goatApp.js`
- `src/main/resources/webgoat/static/js/goatApp/model/AdminModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/AssignmentStatusModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/HTMLContentModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/HintCollection.js`
- `src/main/resources/webgoat/static/js/goatApp/model/HintModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/LabelDebugModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/LessonContentModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/LessonInfoModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/LessonOverviewCollection.js`
- `src/main/resources/webgoat/static/js/goatApp/model/MenuCollection.js`
- `src/main/resources/webgoat/static/js/goatApp/model/MenuData.js`
- `src/main/resources/webgoat/static/js/goatApp/model/MenuModel.js`
- `src/main/resources/webgoat/static/js/goatApp/model/ReportCardModel.js`
- `src/main/resources/webgoat/static/js/goatApp/support/CustomGoat.js`
- `src/main/resources/webgoat/static/js/goatApp/support/GoatUtils.js`
- `src/main/resources/webgoat/static/js/goatApp/support/goatAsyncErrorHandler.js`
- `src/main/resources/webgoat/static/js/goatApp/support/goatConstants.js`
- `src/main/resources/webgoat/static/js/goatApp/templates/admin_panel.html`
- `src/main/resources/webgoat/static/js/goatApp/templates/lesson_overview.html`
- `src/main/resources/webgoat/static/js/goatApp/templates/paging_controls.html`
- `src/main/resources/webgoat/static/js/goatApp/templates/report_card.html`
- `src/main/resources/webgoat/static/js/goatApp/view/AdminView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/ErrorNotificationView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/GoatRouter.js`
- `src/main/resources/webgoat/static/js/goatApp/view/HelpControlsView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/HintView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/LessonContentView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/MenuButtonView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/MenuItemView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/MenuView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/PaginationControlView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/ReportCardView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/TitleView.js`
- `src/main/resources/webgoat/static/js/goatApp/view/UserAndInfoView.js`
- `src/main/resources/webgoat/templates/about.html`
- `src/main/resources/webgoat/templates/lesson_content.html`
- `src/main/resources/webgoat/templates/login.html`
- `src/main/resources/webgoat/templates/mailbox.html`
- `src/main/resources/webgoat/templates/main_new.html`
- `src/main/resources/webgoat/templates/registration.html`
- `src/main/resources/webwolf/static/js/fileUpload.js`
- `src/main/resources/webwolf/static/js/jwt.js`
- `src/main/resources/webwolf/templates/error.html`
- `src/main/resources/webwolf/templates/files.html`
- `src/main/resources/webwolf/templates/fragments/footer.html`
- `src/main/resources/webwolf/templates/fragments/header.html`
- `src/main/resources/webwolf/templates/home.html`
- `src/main/resources/webwolf/templates/jwt.html`
- `src/main/resources/webwolf/templates/registration.html`
- `src/main/resources/webwolf/templates/requests.html`
- `src/main/resources/webwolf/templates/webwolf-login.html`

## Unreviewed scope

- Most lesson prose, translations and lesson HTML/JS beyond specifically listed files; binary archives (including challenge git.zip), keystore, images, packaged classes and database artifacts.
- Third-party/minified frontend library internals and transitive Java dependency implementations; package resolution/advisory database/container-image provenance; CI/release/deployment environment.
- Live runtime, automated/integration/browser tests, proxy/cache/TLS/session behaviors, real OAuth provider settings, actual filesystem mounts/permissions, effective database grants, external network/DNS behavior, performance/DoS thresholds and concurrency.
- NoSQL, GraphQL, WebSockets, SAML and web-LLM surfaces were not identified in the mapped first-party application. No custom HTTP proxy/parser was present to source-prove request smuggling; deployed HTTP parsing remains unreviewed.

## Unreviewed resource inventory by area

This is a file-enumeration remainder, not a claim that every omitted static file is security-relevant. The report explains topic-level applicability and limitations.

| Area | Files enumerated | Files in manual read ledger | Remaining |
|---|---:|---:|---:|
| `src/main/resources/webgoat/templates` | 6 | 6 | 0 |
| `src/main/resources/webwolf/templates` | 9 | 9 | 0 |
| `src/main/resources/webgoat/static/js/goatApp` | 37 | 37 | 0 |
| `src/main/resources/webwolf/static/js` | 2 | 2 | 0 |
| `src/main/resources/lessons` | 253 | 10 | 243 |
| `src/main/resources/db` | 3 | 3 | 0 |
| `src/main/resources` | 390 | 69 | 321 |

## Final disposition

Complete source-only report saved as `report.md` with platform findings, challenges-package findings and actual lesson sink inventory. No fixes were requested or applied. The finite source review does not certify security or runtime exploitability.
