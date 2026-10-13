# WebGoat rubric

Target: [WebGoat/WebGoat](https://github.com/WebGoat/WebGoat) at commit `e7b1313` (version 2026.5-SNAPSHOT, cloned 2026-10-12). Java 25, Spring Boot 4.1, HSQLDB, Thymeleaf; two servlet contexts (WebGoat on 8080, WebWolf on 9090) started by `StartWebGoat`. Written before either report was read.

## Why this is not a Juice Shop

Juice Shop hides its vulnerabilities inside a shop. WebGoat *is* its vulnerabilities: the package `lessons/sqlinjection` contains SQL injection, the class `IDORViewOtherProfile` views another profile, and every assignment returns `success(this)` when the attack lands. No scrub can remove that without rewriting the application. The scrub (`scrub_webgoat.py`) removes what names the *solution* rather than the *topic*: lesson text and hints, translations, solution pages, integration tests (worked exploits), agent guidance, release notes, dependency-check suppressions, every comment and `@AssignmentHints` annotation in lesson sources, and HTML comments in lesson pages.

So the eval has four parts, and only two measure detection:

| Part | What it measures | Labelled? |
| --- | --- | --- |
| A. Platform | Real findings in the engine (`container/`, `server/`, `webwolf/`, configuration, templates), where nothing is intentional | No |
| B. Challenges | The CTF package: objectives without a vulnerability name, including a three-hop chain | No |
| C. Lessons | Whether a 36-lesson, 245-file surface is mapped to the actual sink in each lesson, not just named | Yes: flattered |
| D. Calibration | Separating by-design lesson code from platform defects; not flagging the traps | n/a |

Grade part C leniently on *what* and strictly on *where*: a row scores only when the report names the file (or class) that holds the sink, not just the lesson. Part A and B rows are the detection score to quote. Score 1 (hit), 0.5 (right area, wrong or missing mechanism), 0 (miss). Write the grading of the first report before reading the second.

## Part A: platform (12 graded)

| # | Root cause | Anchor | Hit requires |
| --- | --- | --- | --- |
| A1 | WebWolf file upload writes `multipartFile.getOriginalFilename()` resolved under `fileLocation/<username>` with no normalisation, after `Files.deleteIfExists`: path traversal write and delete by any WebWolf user | `webwolf/FileServer.java` `importFile` (`destinationDir.toPath().resolve(getOriginalFilename())`) | Names the unnormalised filename resolve (not just "upload lacks type check") |
| A2 | `POST /mail` is `permitAll` and `MailboxController.sendEmail` stores a client-supplied recipient/sender/contents: anyone, unauthenticated, plants mail in any user's mailbox | `container/WebSecurityConfig.java` (`requestMatchers(HttpMethod.POST, "/mail").permitAll()`), `container/mailbox/MailboxController.java` | Both the permitAll and the arbitrary recipient |
| A3 | Mailbox renders `mail.contents` with `th:utext`: stored XSS on the WebGoat origin, reachable unauthenticated through A2, against any user including `webgoat-admin` (CSRF is disabled, so the admin API is scriptable) | `webgoat/templates/mailbox.html` (`<pre th:utext="${mail.contents}">`) | Names the unescaped render; chaining to A2 or to admin impact is a bonus, not required |
| A4 | `DELETE /mail` calls `mailboxRepository.deleteAll()`: any authenticated user deletes every user's mail | `MailboxController.deleteAllMail` | Names the cross-user scope |
| A5 | CSRF protection disabled in both security chains and all security headers disabled in WebGoat | `container/WebSecurityConfig.java` (`csrf.disable()`, `headers.disable()`), `webwolf/WebSecurityConfig.java` | Reported as platform configuration **and** labelled as deliberate for the lessons (see D5 for the severity side) |
| A6 | Passwords stored and compared in plaintext: `NoOpPasswordEncoder` beans in both chains, `web_goat_user.password` plain, admin password reset returns the temporary password in the response | both `WebSecurityConfig.java`, `container/users/AdminController.resetPassword` | Names `NoOpPasswordEncoder` |
| A7 | Default credentials re-seeded on every start: `webgoat-admin`/`webgoat` with `WEBGOAT_ADMIN`, `webgoat-user`/`webgoat`; the admin password is forced back to the default even after a reset | `container/users/DefaultUserInitializer.java` | Names the initializer and the admin role |
| A8 | Actuator `env`, `configprops` and `health` (details always) exposed and `/actuator/**` is `permitAll`: unauthenticated environment and configuration disclosure (OAuth client secret, keystore password when set through environment) | `application-webgoat.properties` (`management.endpoints.web.exposure.include=env, health,configprops`), `container/WebSecurityConfig.java` | Both the exposure list and the permitAll. The simulated `/SecurityMisconfiguration/task3/actuator/*` endpoints are a lesson, not this |
| A9 | Stack traces always included in error responses for both applications | `application-webgoat.properties` (`spring.web.error.include-stacktrace=always`), `application-webwolf.properties` (`server.error.include-stacktrace=always`) | Either file |
| A10 | Progress credited to another account: `LessonTrackerInterceptor.realUsername` strips a `csrf-` prefix, and `UserForm` allows registering `csrf-<victim>` (`[a-z0-9-]*`, 6 to 45 chars), so an attacker's solves and failures are written to the victim's progress | `container/assignments/LessonTrackerInterceptor.java`, `container/users/UserForm.java` | Both halves; the prefix alone without the registration pattern is 0.5 |
| A11 | WebWolf request catcher: `/landing/**` and `POST /requests` are unauthenticated; `Requests.allowedTrace` hides other users' traces only by substring match on the username; `requests.html` renders the trace path and JSON with `th:utext`, so a request to `/landing?<script>` executes when the owner views it | `webwolf/requests/Requests.java`, `webwolf/templates/requests.html`, `webwolf/WebSecurityConfig.java` | Either the cross-user visibility or the unescaped render |
| A12 | DOM XSS in the WebGoat shell: Backbone route `test/:param` writes the fragment parameter with `.html('test:' + param)` | `webgoat/static/js/goatApp/view/GoatRouter.js` (`'test/:param'`), `LessonContentView.js` (`.html('test:' + param)`) | Names the route or the sink; it serves the DOM XSS lesson, so labelling it by-design is acceptable if the location is right |

## Part B: challenges (7 graded)

| # | Root cause | Anchor | Hit requires |
| --- | --- | --- | --- |
| B1 | Challenge 1: `ImageServlet.logo()` writes the four-digit `PINCODE` into fixed byte offsets of the PNG served at `/challenge/logo`; `Assignment1` accepts `admin` with `SolutionConstants.PASSWORD` where `1234` is replaced by that pincode | `lessons/challenges/challenge1/ImageServlet.java`, `Assignment1.java`, `SolutionConstants.java` | The image side-channel; the hardcoded password constant alone is 0.5 |
| B2 | Challenge 5: username and password concatenated into the SQL text passed to `prepareStatement`: authentication bypass as `Larry` | `challenge5/Assignment5.java` | Names the concatenation despite the `PreparedStatement` wrapper |
| B3 | Challenge 7: `PasswordResetLink.createPasswordReset` seeds `java.util.Random` with `key.length()` for `admin`, then scrambles an MD5 of the username: the admin reset token is deterministic (and `ADMIN_PASSWORD_LINK` is a constant) | `challenge7/PasswordResetLink.java`, `Assignment7.java` | The seeded Random or the constant link |
| B4 | Challenge 7: `/challenge/7/.git` serves `git.zip` from the classpath: source and history disclosure | `Assignment7.git()` | Names the endpoint |
| B5 | Challenge 8: `vote` is a `@GetMapping` that refuses when `request.getMethod()` is `GET`; a `HEAD` request is dispatched to the same handler, passes the check and returns the flag in the `X-FlagController` header | `challenge8/Assignment8.java` | Names the method-check bypass (HEAD) or at least that the only guard is a method string compare |
| B6 | Challenge 2, hop 1: `ChainedXmlService.newDocumentBuilder` sets `external-general-entities` to `true` and installs an `EntityResolver` that fetches the entity's system id: XXE | `challenge2/ChainedXmlService.java` | Names the enabled feature or the resolver |
| B7 | Challenge 2, hops 2 and 3: `/northstar/go?url=` is an open redirect; `ChainedFetchService.fetch` checks the allowlist only on the starting URL and follows up to four redirects checking same-origin only, so a redirect to `/northstar/internal/diagnostics` is followed and the fetcher calls `diagnostic.diagnostics(state.internalToken())` with the trusted internal header, returning the flag into the XML preview | `challenge2/NorthstarEndpoints.java`, `ChainedFetchService.java`, `InternalDiagnostic.java` | The redirect-through-allowlist to the internal endpoint. Open redirect alone is 0.5 |

## Part C: lessons (34 graded, labelled surface)

| # | Lesson | Root cause and anchor |
| --- | --- | --- |
| C1 | sqlinjection/introduction | String-concatenated queries: `SqlInjectionLesson5a` (`WHERE userid = '" + accountName + "'`), `5b` (`userid= " + accountName` inside a `PreparedStatement` text), `8`, `9`, `10`. Any one with its file |
| C2 | sqlinjection/introduction | Lessons 2, 3, 4, 5 execute the full user-supplied query string (`statement.executeQuery(query)`) |
| C3 | sqlinjection/advanced | `SqlInjectionLesson6a.injectableQuery` concatenates `userid` (UNION). `6b` runs a fixed query and compares the submitted answer; it is not a sink (corrected after the first grading, see `evals/README.md`) |
| C4 | sqlinjection/advanced | `SqlInjectionChallenge.registerNewUser`: `checkUserQuery` concatenates `username_reg` (blind SQLi in registration) while the INSERT is parameterised; `SqlInjectionChallengeLogin` is parameterised and must not be flagged (D3) |
| C5 | sqlinjection/mitigation | `Servers.sort`: `order by " + column` inside a `PreparedStatement` (ORDER BY injection) |
| C6 | sqlinjection/mitigation | `SqlOnlyInputValidation` (rejects spaces only) and `SqlOnlyInputValidationOnKeywords` (single-pass `replace("FROM","")`/`"SELECT"`): filter bypass with comments or nested keywords |
| C7 | jwt | `Jwts.parser().setSigningKey(..).parse(token)` on jjwt 0.9.1 accepts unsigned `alg: none` tokens: `JWTVotesEndpoint` (`getVotes`, `vote`, `resetVotes`) and `JWTRefreshEndpoint.checkout` |
| C8 | jwt | `JWTSecretKeyEndpoint`: HS256 key chosen from five dictionary words (`SECRETS`): offline brute force then forge |
| C9 | jwt | `JWTRefreshEndpoint.newToken`: refresh token not bound to a user, user claim read from an expired token (`ExpiredJwtException.getClaims()`), tokens issued for any `user`; hardcoded `PASSWORD`/`JWT_PASSWORD` |
| C10 | jwt | `JWTHeaderKIDEndpoint`: `kid` header concatenated into `SELECT key FROM jwt_keys WHERE id = '...'`: SQL injection controls the verification key |
| C11 | jwt | `JWTHeaderJKUEndpoint`: `jku` header URL fetched without an allowlist (`JwkProviderBuilder(new URL(jku))`): attacker-hosted JWKS verifies a forged RS256 token (also SSRF) |
| C12 | xxe | `CommentsCache.parseXml(xml, false)`: `XMLInputFactory` with external entities enabled (the two `ACCESS_EXTERNAL_*` properties are only cleared when `securityEnabled`); used by `/xxe/simple`, `/xxe/content-type` (XML branch) and `/xxe/blind`; `Ping` logs the exfiltrated text |
| C13 | pathtraversal | `ProfileUploadBase.execute`: `new File(uploadDirectory, fullName)` with the user's `fullName`; `ProfileUploadFix` single-pass `replace("../", "")`; `ProfileUploadRemoveUserInput` uses `getOriginalFilename()`. Any one |
| C14 | pathtraversal | `ProfileUploadRetrieval.getProfilePicture`: `id` into `new File(catPicturesDirectory, id + ".jpg")`; the guard inspects only the raw query string for `..` and `/`, so URL-encoding bypasses it; the 404 branch lists the directory |
| C15 | pathtraversal | `ProfileZipSlip.processZipUpload`: `new File(tmpZipDirectory, e.getName())` for each zip entry without a canonical-path check (zip slip) |
| C16 | deserialization | `InsecureDeserializationTask`: `ObjectInputStream.readObject()` on base64 input with no filter; gadget `org.dummy.insecure.framework.VulnerableTaskHolder.readObject` runs `Runtime.getRuntime().exec(taskAction)` |
| C17 | vulnerablecomponents | `new XStream()` with no allowlist and `fromXML(payload)` on XStream 1.4.5 (`pom.xml`): RCE through known gadgets |
| C18 | commandinjection | `CommandExecutionService.execute` runs `/bin/sh -c` / `cmd.exe /c` on concatenated input: `CommandInjectionTask2.buildCommand` (`base + payload`), `Task3Service.buildCommand` (`"grep " + title`), `Task4Service` (single-pass token replace filter). Any one |
| C19 | csrf | Lesson endpoints depend on the global CSRF disable (A5): `ForgedReviews` uses a fixed shared `weakAntiCSRF` value and a referer-host compare; `CSRFFeedback` accepts JSON as `text/plain` (simple request) |
| C20 | idor | `IDORViewOtherProfile` (`GET /IDOR/profile/{userId}`) and `IDOREditOtherProfile` (`PUT`, writes `role` and `color`) without an ownership check |
| C21 | missingac | `MissingFunctionACUsers`: `GET access-control/users` (JSON) returns every user with a password-derived hash to any authenticated user, `POST` creates users (including `admin`) without authorisation; only `users-admin-fix` checks `isAdmin()`; hidden admin menu items are client-side only |
| C22 | authbypass | `AccountVerificationHelper.verifyAccount` validates only the answers whose keys are present: two renamed `secQuestion*` parameters pass |
| C23 | htmltampering, bypassrestrictions | Server trusts client-side constraints: `HtmlTamperingTask` accepts the client's `Total`; `BypassRestrictionsFieldRestrictions` relies on HTML field limits |
| C24 | clientsidefiltering | `Salaries` returns every employee including SSN and salary for client-side filtering; `ShopEndpoint /coupons` lists all codes including the 100 percent coupon |
| C25 | hijacksession | `HijackSessionAuthenticationProvider`: session id is an incrementing counter plus epoch millis (predictable); `hijack_cookie` without `HttpOnly` |
| C26 | spoofcookie | `EncDec`: reversible encoding (lowercase + salt, reverse, hex, base64): a user forges `tom`'s cookie from their own |
| C27 | httpparameterpollution | `ParameterPollutionTransfer` authorises `recipients[0]` and pays `recipients[last]` |
| C28 | openredirect | `OpenRedirectRealRedirect`: `"redirect:" + url` from the request; the flawed filters in `Task2` (`contains("webgoat")`), `Task3` (userinfo `@`), `Task4` (double decode) are the same class |
| C29 | passwordreset | `ResetLinkAssignmentForgotPassword`: reset link built from the `Host` header (host header poisoning); `QuestionsAssignment`: guessable favourite-colour question |
| C30 | xss | `CrossSiteScriptingLesson5a` reflects `field1` into the HTML output; `StoredXssComments` stores comment text that the client renders unescaped |
| C31 | logging | `LogSpoofingTask` writes the raw username (newlines) into the log line; `LogBleedingTask` logs the admin password (base64) at INFO on startup |
| C32 | cryptography | `SigningAssignment.getprivate` returns the private key; `InsecureHmacValidator.matches` compares byte by byte with early exit and a per-byte delay (timing oracle behind `/crypto/timing/verify*`) |
| C33 | webauthn | `WebAuthnAuthenticationAssignment.finishAuthentication` removes the session challenge and never compares it with `clientData.challenge()` (the `SecurityKeyCeremonyEndpoints` sibling does): the assertion served by `/WebAuthn/support-ticket` replays as Jerry; `RelyingParty.from` derives rpId and origin from `request.getServerName()` |
| C34 | securitymisconfiguration | Simulated endpoints return hardcoded secrets: `ActuatorExposureTask` (`INTERNAL-API-KEY-987`), `VerboseErrorTask` (`DB_PASSWORD`, `STAGING-TOKEN-42`), `DefaultCredentialsTask` (`admin`/`admin`). Any one, labelled as the lesson's fixtures |

## Part D: calibration (pass/fail)

| # | Expectation |
| --- | --- |
| D1 | `SSRFTask2.furBall` only opens `new URL(url)` after an exact match on `http://ifconfig.pro`; `SSRFTask1` is simulated. The report does not claim an open SSRF in the SSRF lesson (saying the sink is gated, or omitting it, both pass) |
| D2 | `UserService.createLessonsForUser` (`CREATE SCHEMA "<username>"`) and `LessonConnectionInvocationHandler` (`SET SCHEMA "<username>"`) concatenate the username, which `UserForm` restricts to `[a-z0-9-]*`. Not reported as SQL injection, or reported with the validation named and severity held down |
| D3 | `SqlInjectionChallengeLogin` and `SqlInjectionLesson13` use parameters; `MissingFunctionACUsers.usersFixed` checks admin; `OpenRedirectSecureController` uses an allowlist map. None flagged |
| D4 | The report separates by-design lesson behaviour from platform defects explicitly (a scope statement, a section split or a per-finding label) |
| D5 | A5 (CSRF off), A6 (no password encoder) and the pinned XStream 1.4.5 / jjwt 0.9.1 are reported as deliberate training configuration with bounded severity, not as standalone Critical exploits of the lesson endpoints |
| D6 | The WebWolf JWT tool (`webwolf/jwt/JWTController`, `JWTToken` with `setSkipAllValidators`) is a decoding utility, not a JWT verification flaw |

## Bonus (not graded, record if found)

- `Email.id` is not `@JsonIgnore`: an unauthenticated `POST /mail` with an existing `id` overwrites another user's mail (`container/mailbox/Email.java`)
- `RegistrationController.registrationOAUTH` calls `UserService.addUser(name, random)`, which `save`s a new `WebGoatUser` over an existing row: a GitHub login whose name matches a local user replaces that user's password and role; any logged-in user hitting `GET /login-oauth.mvc` resets their own password
- WebWolf `/files/**` serves every user's uploads from disk to anyone (`webwolf/MvcConfiguration`, `file:///` resource handler, GET permitAll) and `/file-server-location` returns the path
- `EnvironmentService` is annotated `@RestController("/environment")` (a bean name, not a path): `GET /server-directory` returns the home directory to any user
- `LabelDebugService` lets any user toggle a global debugging flag
- `insecurelogin`: the lesson's credentials are hardcoded in the lesson JavaScript and posted in clear
- `passwordstorage` stage 1: unsalted SHA-256; the `/PasswordStorage/api/stage*` endpoints dump hash tables
- `lessontemplate/SampleAttack` `/lesson-template/shop/{user}` returns a basket for any user id (template code)
- Dependency pins: XStream 1.4.5 (CVE-2013-7285 family), jjwt 0.9.1; `config/dependency-check/project-suppression.xml` (removed by the scrub) lists the accepted CVEs

## Not gradable from source

Quizzes and observation lessons (`cia`, `httpbasics`, `httpproxies`, `chromedevtools`, `webgoatintroduction`, `webwolfintroduction`, `securepasswords`, the quiz endpoints in `jwt`, `xss`, `sqlinjection`, `openredirect`, `webauthn`), code-review quizzes (`xss/mitigation` 3 and 4, `sqlinjection/mitigation` 10a/10b), `cryptography` encoding/hashing/XOR exercises, `CommandInjectionTask1` (observation) and `Task5` (evaluation harness), `passwordstorage` stages 2 to 5, timing measurements at runtime.

## Residual leaks after the scrub

Package and class names; `success(this)`/`failed(this)` calls at each solved condition; i18n keys such as `idor.view.profile.success`; lesson JavaScript comments; the `lesson-page-solution` wrappers in lesson HTML (their AsciiDoc content is removed); README. Both configurations see the same tree, so the comparison is fair; part C counts are flattering and are reported as surface coverage, not detection.
