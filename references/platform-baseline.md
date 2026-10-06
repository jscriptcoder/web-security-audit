# Platform baseline beyond the Academy topic list

Load for broad audits or when the relevant deployment/browser/dependency configuration is in scope. These are supplemental checks; do not represent them as extra Academy topics or a complete compliance standard.

## Dependencies and shared packages

Source: [OWASP Vulnerable Dependency Management](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html).

Read lockfiles and deployment manifests to identify resolved versions, runtime versus build use, and shared/transitive consumers. Verify an advisory against the vendor's current affected versions and the application's use of the vulnerable feature. Distinguish a known vulnerable installed component from demonstrated application exploitability. Record reachability uncertainty instead of treating an unavailable scanner as a clean result. Recommend an upgrade or vendor-supported mitigation and verify the affected behavior after the change. Avoid installing or executing unfamiliar dependency tooling merely to obtain a risk score.

## Browser policy and cookies

Sources: [OWASP CSP guidance](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html), [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie).

Inspect actual HTML responses for enforced CSP, nonce/hash handling, unsafe script sources, framing policy and relevant third-party scripts. Report-only CSP does not block execution. Assess missing policy as hardening unless a concrete exploit path warrants more. A CSP supplements safe rendering; it does not fix a dangerous sink.

Inspect session-cookie `Secure`, `HttpOnly`, `SameSite`, host/domain/path scope and lifetime. Same-site and same-origin are different boundaries: an untrusted sibling subdomain can matter even when cookies use SameSite. Distinguish explicit `Lax` from permissive browser defaults for newly set cookies. `HttpOnly` prevents direct JavaScript cookie reads; it does not stop XSS from making authenticated requests. Evaluate script-readable token storage through realistic XSS and lifecycle exposure, not an automatic critical rating.

## Deployment and service controls

Source: [OWASP REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html).

Check HTTPS and certificate validation on external and backend hops; evaluate HSTS against the actual deployment. Inspect credentials/configuration exposure, error handling, security-relevant logging and sensitive data in URLs. Check authorization and input constraints at service boundaries, request/body limits, replay handling and per-identity limits. For webhooks, examine signature verification against the original bytes, timestamp/replay checks and binding to the intended tenant/event.

Verify deployment settings rather than assuming development configuration is public. Distinguish public client identifiers from secrets. Link operational fixes to application evidence, including missing logs that prevent validation. For capabilities outside the bundled checks, use current primary framework/vendor documentation and identify the added scope.
