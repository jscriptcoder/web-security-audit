# Juice Shop grading rubric (written before reading any report)

Source: challenges.yml at commit e39a3bdb8c61295c31fa4e0a03485e68a8ca12a4, deduplicated by root cause.
Only root causes a source review can establish are graded (G). Challenges that need
runtime guessing, OSINT, the companion guide, or are game mechanics are listed as not graded (N).
A report gets credit for a G item when it names the right file/sink and the right vulnerability class.

## Graded (G) — 40 root causes

| # | Root cause | Anchor | Challenges covered |
| --- | --- | --- | --- |
| 1 | SQL injection in login (string-built query) | routes/login.ts | loginAdmin, loginBender, loginJim, ephemeralAccountant, ghostLogin |
| 2 | SQL injection in product search | routes/search.ts | dbSchema, unionSqlInjection, christmasSpecial |
| 3 | NoSQL injection in review update (operator/$where injection) | routes/updateProductReviews.ts | noSqlReviews |
| 4 | NoSQL injection in order tracking | routes/trackOrder.ts | noSqlOrders |
| 5 | NoSQL $where sleep / injection in review listing | routes/showProductReviews.ts | noSqlCommand |
| 6 | SSTI / code execution via username rendered in pug template | routes/userProfile.ts | ssti |
| 7 | Sandboxed eval of B2B order payload (RCE / DoS) | routes/b2bOrder.ts | rce, rceOccupy |
| 8 | YAML parsing of uploads (yaml bomb) | routes/fileUpload.ts | yamlBomb |
| 9 | XXE in XML upload (noent) | routes/fileUpload.ts | xxeFileDisclosure, xxeDos |
| 10 | Zip slip in zip upload handling | routes/fileUpload.ts | fileWrite |
| 11 | Upload size/type enforced client-side or after processing | routes/fileUpload.ts, frontend | uploadSize, uploadType, deprecatedInterface |
| 12 | Mass assignment on user registration (role, etc.) | server.ts finale/REST, routes/verify.ts | registerAdmin |
| 13 | Weak server-side registration validation (empty email/password, repeat check client-only) | server.ts, frontend register | emptyUserRegistration, passwordRepeat |
| 14 | Negative quantity / price manipulation in basket & order | routes/basketItems.ts, routes/order.ts | negativeOrder |
| 15 | Deluxe membership payment bypass | routes/deluxe.ts | freeDeluxe |
| 16 | Coupon codes forgeable (z85, no secret) / expiry not enforced | lib/insecurity.ts, routes/order.ts, routes/coupon.ts | forgedCoupon, manipulateClock |
| 17 | Null byte / path filter bypass and directory listing on /ftp | routes/fileServer.ts, server.ts serveIndex | nullByte, directoryListing, forgottenBackup, forgottenDevBackup, misplacedSignatureFile |
| 18 | Access logs served publicly | server.ts (/support/logs) | accessLogDisclosure |
| 19 | Admin area guarded only client-side / admin REST without role check | frontend routes, server.ts | adminSection |
| 20 | Feedback CRUD without auth or ownership (delete any, forge UserId, zero stars, captcha reuse) | server.ts Feedback REST, routes/verify.ts, routes/captcha.ts | feedback, forgedFeedback, zeroStars, captchaBypass |
| 21 | Basket read by ID without ownership check | routes/basket.ts | basketAccess |
| 22 | Basket item add with BasketId from body / duplicate key parsing | routes/basketItems.ts | basketManipulate |
| 23 | Product review author taken from body / update without author check | routes/createProductReviews.ts, routes/updateProductReviews.ts | forgedReview |
| 24 | Product PUT allowed for non-admin | server.ts Products REST | changeProduct |
| 25 | CSRF on profile update (form POST accepted cross-origin, no token) | routes/updateUserProfile.ts | csrf |
| 26 | SSRF via profile image URL fetch | routes/profileImageUrlUpload.ts | ssrf |
| 27 | Weak / hard-coded seed credentials and test accounts | data/static/users.yml, frontend | weakPassword, exposedCredentials, loginSupport, loginAmy, loginRapper |
| 28 | Password reset by security question, no rate limit, guessable answers | routes/resetPassword.ts | resetPassword* (6), geoStalking* |
| 29 | OAuth login derives password from base64(reversed email) client-side | frontend oauth component, routes/login.ts | oauthUserPassword |
| 30 | Change password skips current-password check when param absent (GET params) | routes/changePassword.ts | changePasswordBender |
| 31 | TOTP secret stored in plaintext in users table | routes/2fa.ts, models/user.ts | twoFactorAuthUnsafeSecretStorage |
| 32 | Weak crypto: MD5 password hashing, hard-coded HMAC/RSA keys | lib/insecurity.ts | weirdCrypto, passwordHashLeak (hash returned by whoami/Users) |
| 33 | JWT: alg none / RSA public key confusion accepted, legacy express-jwt | lib/insecurity.ts, package.json | jwtUnsigned, jwtForged |
| 34 | Hard-coded encryption keys and key files shipped (encryptionkeys/, ctf.key, premium reward AES key) | encryptionkeys/, lib/insecurity.ts, routes/premiumReward.ts, routes/easterEgg.ts | premiumPaywall, easterEggLevelTwo, nftUnlock (private key) |
| 35 | Prometheus /metrics unauthenticated | routes/metrics.ts, server.ts | exposedMetrics |
| 36 | Verbose error handler / stack traces in responses | server.ts errorhandler | errorHandling |
| 37 | XSS sinks: search query via bypassSecurityTrustHtml, product description innerHTML, order-id reflection, True-Client-IP stored and rendered, outdated sanitize-html, video subtitle injection into pug, CSP header built from profile image URL | frontend search/product/track-result/administration/last-login-ip, routes/saveLoginIp.ts, routes/videoHandler.ts, routes/userProfile.ts, package.json | localXss, xssBonus, reflectedXss, restfulXss, persistedXssUser, persistedXssFeedback, httpHeaderXss, videoXss, usernameXss |
| 38 | Open redirect allowlist uses substring match | lib/insecurity.ts isRedirectAllowed, routes/redirect.ts | redirect, redirectCryptoCurrency |
| 39 | JSONP whoami callback leaks email cross-origin | routes/currentUser.ts | emailLeak |
| 40 | Known-vulnerable / typosquatted dependencies pinned in manifests | package.json, frontend/package.json, Dockerfile | knownVulnerableComponent, typosquattingNpm, typosquattingAngular, supplyChainAttack, csaf, vulnerableDockerImage |

Extra credit (source-visible but subtle, listed for completeness, graded as bonus):
- B1 Race condition on review likes (routes/likeProductReviews.ts) — timingAttack
- B2 Local file read in data erasure layout param (routes/dataErasure.ts) — lfr
- B3 Data export matching other users' data (routes/dataExport.ts) — dataExport
- B4 Chatbot prompt injection / debug info to non-admins (routes/chat.ts) — chatbotPromptInjection, chatbotGreedyInjection, aiDebugging, systemPromptExtraction
- B5 Web3: reentrancy in wallet contract, NFT mint logic, sandbox route (routes/web3Wallet.ts, routes/nftMint.ts, data/static/web3-snippets) — web3Wallet, nftMint, web3Sandbox
- B6 Hidden routes reachable client-side (token sale, score board, privacy policy, IaC files under assets, extra language file, blueprint under public assets) — tokenSale, scoreBoard, misplacedIacFiles, extraLanguage, retrieveBlueprint
- B7 Hashid-based continue code forgeable (routes/restoreProgress.ts) — continueCode
- B8 SVG/HTML injection into delivery address or similar — svgInjection
- B9 Missing output encoding of image filename — missingEncoding

## Not graded (N)
privacyPolicy, privacyPolicyProof, closeNotifications, securityPolicy, hiddenImage, easterEggLevelOne, dlpPasswordSpraying, dlpPastebinDataLeak, leakedApiKey (needs OSINT or runtime), iacLeakedKey (needs the leaked file content).

## Also record per report
- False positives: traps or non-issues reported as findings above Low.
- Calibration: confidence labels, severity justification, hedging where evidence is missing.
- Coverage statement: does the report say what it did not review?
- Files/areas named as reviewed.
