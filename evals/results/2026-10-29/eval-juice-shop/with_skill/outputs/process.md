# Audit process

Source-only review of Juice Shop 20.3.0. Target is read-only; no app execution, network requests, dependency installs, tests or deployments authorized/performed. Only target source and requested skill resources are read. Started 2026-10-29 (wall clock not yet measured). Revision not supplied; package version is not a commit identity.

## Initial checkpoint
Read skill SKILL.md, methodology, reporting, stack README and javascript-node, audit report and coverage assets, sink_inventory.py; ran inspected inventory script once. Read package.json; enumerated root, routes, models and lib. Inventory search matches are leads, not reviewed handlers.

Next: read complete server route/middleware registration and models/security helpers; inventory generated API controls; read each route; trace frontend sinks and configuration.

## Checkpoint: identity, generated routes and major handlers
Read server.ts in full (first broad output truncated; lines 1-480 reread completely). Read lib/insecurity.ts; models/user.ts; routes login, 2fa, changePassword, resetPassword, address, payment, basket, basketItems, recycles, dataExport, dataErasure, orderHistory, order, coupon, deluxe, wallet, likeProductReviews, updateProductReviews, showProductReviews, createProductReviews, search, trackOrder, b2bOrder, fileUpload, fileServer, keyServer, logfileServer, quarantineServer, profileImageFileUpload, profileImageUrlUpload, memory, userProfile, updateUserProfile, videoHandler, chat, authenticatedUsers, currentUser, securityQuestion, captcha, imageCaptcha, saveLoginIp, redirect, appConfiguration. Read lib/xml.ts and lib/startup/registerWebsocketEvents.ts. References loaded: identity-access, api-realtime, business-logic, injection, files-data, browser-security, frontend-frameworks, frontend-runtime, http-infrastructure.

Evidence candidates: login/search raw SQL; generated role assignment and unowned Address PUT; basket reads/checkouts/coupons and item CRUD; duplicate BasketId parse; masked-email identity collision; review mass operator update; hardcoded JWT key; cached tokens without expiry/revocation and isActive not checked; sensitive full User serialization in memories/JWT; unauthenticated ZIP overwrite within app tree, XXE, YAML unsafe loader; username eval; image URL SSRF/active SVG; profile CSRF; weak coupon/payment/captcha controls; chat decode-only identity and prompt-only coupon policy. No payloads executed. Next: remaining handlers/models, utility gating and config, frontend and deployment review.

## Checkpoint: frontend, LLM, deployment and negative controls
All routes/*.ts have now been read, including generated API hooks and verify.ts (challenge callbacks observed to call next rather than enforce security). All models have been read; a truncated tail of challenge.ts is scheduled for reread. BasketItem ProductId/BasketId update hooks restrict reassignment, so findings will not claim those foreign keys are generally editable on PUT. Address ownership has no corresponding hook. Public memories include the whole User association with no default exclusion.

Frontend reads: oauth, login, request.interceptor, user.service, app.guard, conversation-storage.service; search-result TS/HTML, track-result TS/HTML, data-export TS, last-login-ip TS/HTML, administration TS/HTML, about TS, chat-conversation TS/HTML, chat.service, chat-welcome-page TS; frontend package.json, angular.json, environments, index.html. Track-order service fully read on follow-up: encodeURIComponent protects its path segment. Earlier tentative CSPT commentary was retracted; do not report this lead. Chat display uses text interpolation; no chat output XSS asserted.

Read app.ts; Dockerfile, infrastructure Dockerfile/compose, terraform main/networking/variables/outputs and infrastructure copies (some combined output truncated; tails to reconcile); config unsafe and default security-related sections. Read data/mongodb, data/staticData, data/datacache, datacreator 1-220 plus matched security-field lines; lib utils, XML, challengeUtils, accuracy, codingChallenges, noUpdate, terraformCustomization, webhook, platform detection. Loaded LLM/prototype/platform references. No external advisory verification; lockfiles/vendor dependencies absent from initial listings. Secrets encountered are not copied into report.

Additional leads: deterministic OAuth password; MFA temporary/setup tokens usable by signature-only generated endpoints; public config includes recovery answers used by datacreator; unbounded preauthentication disk upload; shared-browser chat history persists across logout; built-in HTTP terraform listener forwards credentials without HTTPS redirect. Deployment use and generated third-party library behavior are source-inferred rather than runtime-tested.

## Final evidence and artifact checkpoint

The substantive report was saved incrementally: findings 001–016, then 017–031, then 032–043, followed by 044 and 045, coverage tables and residual scope. No arbitrary finding cap was applied. Root causes were consolidated where multiple handlers shared one defect. Current confidence breakdown is in report.md; hypotheses/hardening observations are not counted as Confirmed.

Corrections made during validation:

- The inventory contains **61** route TypeScript files and **23** model TypeScript files. Earlier conversational “60 routes” was a counting error, not an omitted route; all listed route files were read.
- Tracking requests encode the ID with encodeURIComponent: no CSPT finding. Returned tracking IDs can still reach a trust-bypassed HTML sink.
- The CAPTCHA export bypass requires absence of a recent CAPTCHA record, rather than merely absence of an answer when a record exists.
- Checkout inventory updates occur before possible payment failure; basket deletion is in the PDF writer finish callback, not assumed to happen before every payment failure.
- The busy-wait helper is in showProductReviews.ts, not trackOrder.ts.
- Static private-key equality was verified without printing key bytes. Initial string comparisons were false because escaped newline notation was normalized in only one file; after normalizing both files, exact normalized PEM equality was true.
- Terraform networking/variables/outputs copies have matching SHA256 values; main.tf differs and was read separately. This reconciles previously truncated combined output without claiming unread tails were reviewed.
- Supported classifications retained for deployment gates, browser script/cookie behavior, Handlebars layout resolution, MarsDB expression behavior, concurrency and LLM execution. No dependency-version-only CVE claims made.

Tool use: functions.exec orchestrating local exec_command/PowerShell reads (`Get-Content` with line numbers/ranges), `rg`/`rg --files`, filename enumeration, local string/regex analysis, SHA256 comparison, and writes only to this output directory. The inspected skill sink_inventory.py was executed once with JSON output saved as inventory.json; it performs static searches and its results were treated as leads. Python/PowerShell document operations did not import or run the target application. No browsing, CUA, network tools, dependency installation, tests, build/start commands or delegation were used.

Tool limitations/errors: some broad source batches exceeded output limits and were reread in smaller ranges; one targeted rg call initially used the wrong working directory and failed, then was rerun in the target; one overlong report-append command failed before process creation (Windows command length), then was split into successful smaller writes; one optional redaction command had a PowerShell quoting parse error and was corrected before reading. These failures did not modify the target or support findings. No total tool-call count or full audit wall-clock/token count was measured.

Only the requested skill directory, target application, and this audit's own output files were accessed. No evaluator material, parent README, historical report, answer key or other skill/output directory was opened. Route files that implement coding exercises were read as application handlers; underlying fix/solution content was not used as audit evidence.

## Exact source read ledger

Paths below are relative to `C:\Users\User\Projects\web-security-audit-workspace\juice-shop`. “Complete” refers to the file contents read; source review is not execution. Search-only matches in other files are not counted as complete reads. The route/model/lib lists are expanded from the enumerated files whose contents were reviewed, rather than representing all searched files.
| File | Read extent |
| --- | --- |
| `app.ts` | Complete |
| `config/unsafe.yml` | Complete |
| `data/datacache.ts` | Complete |
| `data/mongodb.ts` | Complete |
| `data/staticData.ts` | Complete |
| `Dockerfile` | Complete |
| `frontend/angular.json` | Complete |
| `frontend/package.json` | Complete |
| `frontend/src/app/about/about.component.html` | Complete |
| `frontend/src/app/about/about.component.ts` | Complete |
| `frontend/src/app/administration/administration.component.html` | Complete |
| `frontend/src/app/administration/administration.component.ts` | Complete |
| `frontend/src/app/app.guard.ts` | Complete |
| `frontend/src/app/app.routing.ts` | Complete |
| `frontend/src/app/chatbot/chat-conversation/chat-conversation.component.html` | Complete |
| `frontend/src/app/chatbot/chat-conversation/chat-conversation.component.ts` | Complete |
| `frontend/src/app/chatbot/chat-welcome-page/chat-welcome-page.component.ts` | Complete |
| `frontend/src/app/chatbot/chat-welcome-screen/chat-welcome-screen.component.ts` | Complete |
| `frontend/src/app/data-export/data-export.component.html` | Complete |
| `frontend/src/app/data-export/data-export.component.ts` | Complete |
| `frontend/src/app/feedback-details/feedback-details.component.html` | Complete |
| `frontend/src/app/feedback-details/feedback-details.component.ts` | Complete |
| `frontend/src/app/last-login-ip/last-login-ip.component.html` | Complete |
| `frontend/src/app/last-login-ip/last-login-ip.component.ts` | Complete |
| `frontend/src/app/login/login.component.ts` | Complete |
| `frontend/src/app/navbar/navbar.component.ts` | Complete |
| `frontend/src/app/oauth/oauth.component.ts` | Complete |
| `frontend/src/app/product/product.component.html` | Complete |
| `frontend/src/app/product/product.component.ts` | Complete |
| `frontend/src/app/product-details/product-details.component.html` | Complete |
| `frontend/src/app/product-details/product-details.component.ts` | Complete |
| `frontend/src/app/score-board/score-board.component.ts` | Complete |
| `frontend/src/app/search-result/search-result.component.html` | Complete |
| `frontend/src/app/search-result/search-result.component.ts` | Complete |
| `frontend/src/app/Services/address.service.ts` | Complete |
| `frontend/src/app/Services/basket.service.ts` | Complete |
| `frontend/src/app/Services/chat.service.ts` | Complete |
| `frontend/src/app/Services/configuration.service.ts` | Complete |
| `frontend/src/app/Services/conversation-storage.service.ts` | Complete |
| `frontend/src/app/Services/data-subject.service.ts` | Complete |
| `frontend/src/app/Services/local-backup.service.ts` | Complete |
| `frontend/src/app/Services/order-history.service.ts` | Complete |
| `frontend/src/app/Services/payment.service.ts` | Complete |
| `frontend/src/app/Services/photo-wall.service.ts` | Complete |
| `frontend/src/app/Services/product.service.ts` | Complete |
| `frontend/src/app/Services/product-review.service.ts` | Complete |
| `frontend/src/app/Services/request.interceptor.ts` | Complete |
| `frontend/src/app/Services/security-answer.service.ts` | Complete |
| `frontend/src/app/Services/socket-io.service.ts` | Complete |
| `frontend/src/app/Services/track-order.service.ts` | Complete |
| `frontend/src/app/Services/two-factor-auth-service.ts` | Complete |
| `frontend/src/app/Services/user.service.ts` | Complete |
| `frontend/src/app/sidenav/sidenav.component.ts` | Complete |
| `frontend/src/app/track-result/track-result.component.html` | Complete |
| `frontend/src/app/track-result/track-result.component.ts` | Complete |
| `frontend/src/app/welcome-banner/welcome-banner.component.html` | Complete |
| `frontend/src/app/welcome-banner/welcome-banner.component.ts` | Complete |
| `frontend/src/environments/environment.prod.ts` | Complete |
| `frontend/src/environments/environment.ts` | Complete |
| `frontend/src/index.html` | Complete |
| `infrastructure/docker-compose.yml` | Complete |
| `infrastructure/Dockerfile` | Complete |
| `infrastructure/terraform/main.tf` | Complete |
| `infrastructure/terraform/networking.tf` | Complete |
| `infrastructure/terraform/outputs.tf` | Complete |
| `infrastructure/terraform/variables.tf` | Complete |
| `lib/accuracy.ts` | Complete |
| `lib/antiCheat.ts` | Complete |
| `lib/challengeUtils.ts` | Complete |
| `lib/codingChallenges.ts` | Complete |
| `lib/config.schema.ts` | Complete |
| `lib/insecurity.ts` | Complete |
| `lib/is-docker.ts` | Complete |
| `lib/is-heroku.ts` | Complete |
| `lib/is-windows.ts` | Complete |
| `lib/logger.ts` | Complete |
| `lib/noUpdate.ts` | Complete |
| `lib/startup/cleanupFtpFolder.ts` | Complete |
| `lib/startup/customizeApplication.ts` | Complete |
| `lib/startup/customizeEasterEgg.ts` | Complete |
| `lib/startup/registerWebsocketEvents.ts` | Complete |
| `lib/startup/restoreOverwrittenFilesWithOriginals.ts` | Complete |
| `lib/startup/validateConfig.ts` | Complete |
| `lib/startup/validateDependencies.ts` | Complete |
| `lib/startup/validateDependenciesBasic.ts` | Complete |
| `lib/startup/validatePreconditions.ts` | Complete |
| `lib/terraformCustomization.ts` | Complete |
| `lib/utils.ts` | Complete |
| `lib/webhook.ts` | Complete |
| `lib/xml.ts` | Complete |
| `models/address.ts` | Complete |
| `models/basket.ts` | Complete |
| `models/basketitem.ts` | Complete |
| `models/captcha.ts` | Complete |
| `models/card.ts` | Complete |
| `models/challenge.ts` | Complete |
| `models/challengeDependency.ts` | Complete |
| `models/complaint.ts` | Complete |
| `models/delivery.ts` | Complete |
| `models/feedback.ts` | Complete |
| `models/hint.ts` | Complete |
| `models/imageCaptcha.ts` | Complete |
| `models/index.ts` | Complete |
| `models/memory.ts` | Complete |
| `models/privacyRequests.ts` | Complete |
| `models/product.ts` | Complete |
| `models/quantity.ts` | Complete |
| `models/recycle.ts` | Complete |
| `models/relations.ts` | Complete |
| `models/securityAnswer.ts` | Complete |
| `models/securityQuestion.ts` | Complete |
| `models/user.ts` | Complete |
| `models/wallet.ts` | Complete |
| `package.json` | Complete |
| `routes/2fa.ts` | Complete |
| `routes/address.ts` | Complete |
| `routes/angular.ts` | Complete |
| `routes/appConfiguration.ts` | Complete |
| `routes/appVersion.ts` | Complete |
| `routes/authenticatedUsers.ts` | Complete |
| `routes/b2bOrder.ts` | Complete |
| `routes/basket.ts` | Complete |
| `routes/basketItems.ts` | Complete |
| `routes/captcha.ts` | Complete |
| `routes/changePassword.ts` | Complete |
| `routes/chat.ts` | Complete |
| `routes/checkKeys.ts` | Complete |
| `routes/continueCode.ts` | Complete |
| `routes/countryMapping.ts` | Complete |
| `routes/coupon.ts` | Complete |
| `routes/createProductReviews.ts` | Complete |
| `routes/currentUser.ts` | Complete |
| `routes/dataErasure.ts` | Complete |
| `routes/dataExport.ts` | Complete |
| `routes/delivery.ts` | Complete |
| `routes/deluxe.ts` | Complete |
| `routes/easterEgg.ts` | Complete |
| `routes/fileServer.ts` | Complete |
| `routes/fileUpload.ts` | Complete |
| `routes/imageCaptcha.ts` | Complete |
| `routes/keyServer.ts` | Complete |
| `routes/languages.ts` | Complete |
| `routes/likeProductReviews.ts` | Complete |
| `routes/logfileServer.ts` | Complete |
| `routes/login.ts` | Complete |
| `routes/memory.ts` | Complete |
| `routes/metrics.ts` | Complete |
| `routes/nftMint.ts` | Complete |
| `routes/order.ts` | Complete |
| `routes/orderHistory.ts` | Complete |
| `routes/payment.ts` | Complete |
| `routes/premiumReward.ts` | Complete |
| `routes/privacyPolicyProof.ts` | Complete |
| `routes/profileImageFileUpload.ts` | Complete |
| `routes/profileImageUrlUpload.ts` | Complete |
| `routes/quarantineServer.ts` | Complete |
| `routes/recycles.ts` | Complete |
| `routes/redirect.ts` | Complete |
| `routes/repeatNotification.ts` | Complete |
| `routes/resetPassword.ts` | Complete |
| `routes/restoreProgress.ts` | Complete |
| `routes/saveLoginIp.ts` | Complete |
| `routes/search.ts` | Complete |
| `routes/securityQuestion.ts` | Complete |
| `routes/showProductReviews.ts` | Complete |
| `routes/trackOrder.ts` | Complete |
| `routes/updateProductReviews.ts` | Complete |
| `routes/updateUserProfile.ts` | Complete |
| `routes/userProfile.ts` | Complete |
| `routes/verify.ts` | Complete |
| `routes/videoHandler.ts` | Complete |
| `routes/vulnCodeFixes.ts` | Complete |
| `routes/vulnCodeSnippet.ts` | Complete |
| `routes/wallet.ts` | Complete |
| `routes/web3Wallet.ts` | Complete |
| `server.ts` | Complete |
| `terraform/main.tf` | Complete |
| `terraform/networking.tf` | Complete |
| `terraform/outputs.tf` | Complete |
| `terraform/variables.tf` | Complete |
| `views/dataErasureForm.hbs` | Complete |
| `views/dataErasureResult.hbs` | Complete |
| `views/promotionVideo.pug` | Complete |
| `views/themes/themes.ts` | Complete |
| `views/userProfile.pug` | Complete |
| `config/default.yml` | General/security/chat/OAuth settings (first 120 lines), safety-mode and recovery-memory fields (matched lines, including 1052–1058); remaining catalog prose not fully read. |
| `data/datacreator.ts` | Lines 1–390 plus security-field/gating matches; remaining seed initialization not fully read. |

## Skill resources actually read

All paths relative to the requested `skills/web-security-audit` directory:

- SKILL.md (reread once after context recovery).
- references/methodology.md; references/reporting.md.
- references/stacks/README.md; references/stacks/javascript-node.md.
- references/identity-access.md; references/api-realtime.md; references/business-logic.md.
- references/injection.md; references/files-data.md; references/browser-security.md.
- references/frontend-frameworks.md; references/frontend-runtime.md.
- references/http-infrastructure.md; references/llm-integrations.md.
- references/prototype-pollution.md; references/platform-baseline.md.
- assets/audit-report.md; assets/coverage-ledger.md.
- scripts/sink_inventory.py (inspected before execution).

The GraphQL reference was not loaded because route/manifest/search mapping found no GraphQL surface. No other skill was applied.

## Search-only and excluded/residual scope

Static inventory and targeted rg searches covered route registrations, raw queries/eval/templates, auth/role/ownership fields, upload/path/fetch sinks, browser trust bypasses/storage/navigation, and GraphQL/SAML/service-worker/prototype indicators. Search results may include tests/vendor assets/training data; a match was not treated as proof without a handler/source trace. Remaining frontend files, nested scoreboard/instructor helpers, alternate config profiles, translations/static content, smart-contract implementation, CI/build/test logic, dependency internals and generated builds were not completely read. Filename enumeration of FTP did not open its contents. Effective nginx/cache/proxy configuration is unavailable. Runtime dimensions were excluded by instruction, not reported as failed tests.

Target source was not changed. Output artifacts are report.md, process.md and the supplemental static inventory.json. Recommendations are observational; no fixes or deployments were attempted.

## Final frontend follow-through

Read every remaining non-spec file in frontend/src/app/Services and the registration/password/MFA component implementations. This closes the API-service-directory read scope; unrelated visual component/helpers remain as documented. The registration/change/reset form policies were compared with server writers, producing WSA-046. The CTF notification service corroborates the broad credential interceptor concern but still requires administrator-controlled external configuration; it is recorded as a bounded observation. No runtime actions were added.

Additional complete reads after the earlier ledger:

| File | Read extent |
| --- | --- |
| `frontend/src/app/Services/administration.service.ts` | Complete |
| `frontend/src/app/Services/captcha.service.ts` | Complete |
| `frontend/src/app/Services/challenge.service.ts` | Complete |
| `frontend/src/app/Services/code-fixes.service.ts` | Complete |
| `frontend/src/app/Services/code-snippet.service.ts` | Complete |
| `frontend/src/app/Services/complaint.service.ts` | Complete |
| `frontend/src/app/Services/country-mapping.service.ts` | Complete |
| `frontend/src/app/Services/ctf-system-wide-notification.service.ts` | Complete |
| `frontend/src/app/Services/delivery.service.ts` | Complete |
| `frontend/src/app/Services/feedback.service.ts` | Complete |
| `frontend/src/app/Services/hint.service.ts` | Complete |
| `frontend/src/app/Services/image-captcha.service.ts` | Complete |
| `frontend/src/app/Services/keys.service.ts` | Complete |
| `frontend/src/app/Services/languages.service.ts` | Complete |
| `frontend/src/app/Services/quantity.service.ts` | Complete |
| `frontend/src/app/Services/recycle.service.ts` | Complete |
| `frontend/src/app/Services/security-question.service.ts` | Complete |
| `frontend/src/app/Services/snack-bar-helper.service.ts` | Complete |
| `frontend/src/app/Services/vuln-lines.service.ts` | Complete |
| `frontend/src/app/Services/wallet.service.ts` | Complete |
| `frontend/src/app/Services/window-ref.service.ts` | Complete |
| `frontend/src/app/register/register.component.ts` | Complete |
| `frontend/src/app/change-password/change-password.component.ts` | Complete |
| `frontend/src/app/forgot-password/forgot-password.component.ts` | Complete |
| `frontend/src/app/two-factor-auth/two-factor-auth.component.ts` | Complete |
| `frontend/src/app/two-factor-auth-enter/two-factor-auth-enter.component.ts` | Complete |
| `frontend/src/app/privacy-security/privacy-security.component.ts` | Complete |
| `frontend/src/app/password-strength/password-strength.component.ts` | Complete |
| `frontend/src/app/password-strength-info/password-strength-info.component.ts` | Complete |

## Completion and validation

Completed source-only review and report. Final report has **46 findings**: **28 Confirmed/source-proven** (16 High, 10 Medium, 2 Low) and **18 Supported** (1 Critical, 11 High, 6 Medium). No runtime-reproduced finding. All findings contain source evidence, prerequisites/impact bounds, remediation and a regression check. Hypotheses and hardening observations are explicitly separate. Both topic and handler coverage ledgers record reviewed, not-applicable, blocked and not-reviewed scope.

Validation performed on the saved artifacts:

- All **201** explicit source file/line references resolve to existing target files and valid line numbers; converted to clickable absolute Markdown links.
- Finding IDs are unique and sequential; required fix/regression/reference fields present.
- All 61 route files and 14 generated resources appear in the handler ledger; all 23 model files appear in the read ledger. The complete-read ledger now contains 214 unique paths; partial default/config/seed reads are separately labeled.
- The report contains no private-key PEM blocks and no unfinished template placeholders. Raw inventory source excerpts were removed from the saved inventory.json to avoid retaining credentials or embedded training-answer literals; category/path/line metadata remains. No key bytes, tokens or recovery answers are copied into report.md or process.md.
- No application/security regression test was executed; recommended checks are not claimed to pass. Source target remained read-only; only own output artifacts were written.

Elapsed audit time and model-token counts are not available from a measured audit-wide counter and are intentionally not reported. Individual shell-call durations are not meaningful substitutes. This completion records the review's actual finite coverage and limitations, not a guarantee that every vulnerability has been found.
