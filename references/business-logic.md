# Business logic and concurrency

## Business logic vulnerabilities

Source: [PortSwigger Business logic vulnerabilities](https://portswigger.net/web-security/logic-flaws).

- **Inspect:** checkout, discounts, payments, refunds, invitations, account changes, approvals and multi-step workflows. Write the intended invariants before testing: permissible state transitions, conserved balances, authorization and single-use properties.
- **Validate:** on synthetic data, skip/reorder/repeat steps, change quantities or relevant boundary values, switch identity between steps, and compare server-derived values with client-supplied ones. Include alternate API/mobile/export paths where they share the workflow.
- **Evidence:** show a business rule violation and the server-persisted outcome, not just an optimistic UI display. State the legitimate rule's source or mark it as an unresolved product assumption.
- **Fix:** validate transitions and economic values on the server, calculate trusted totals there, bind multi-step artifacts to identity/state and apply an explicit domain model.
- **Example:** The cart posts `{"sku":"A1","qty":-3,"price":10}` and the server trusts `price` or accepts a negative quantity that reduces the total. A coupon rule that only blocks the same code twice in a row is bypassed by alternating codes A, B, A. `POST /checkout/confirm` succeeds without passing through `/checkout/payment`.
- **Avoid false positives:** a surprising permitted workflow is not a vulnerability unless it violates an established security/business rule. Discounts, rounding and cancellation policies vary. Use sandbox payment providers and simulated side effects; do not create real charges or irreversible fulfillment during an audit.

## Race conditions

Source: [PortSwigger Race conditions](https://portswigger.net/web-security/race-conditions).

- **Inspect:** check-then-act operations, single-use tokens, inventory/balance changes, idempotency, concurrent identity updates and multi-endpoint workflows. Follow transactions, uniqueness constraints, locks and shared storage across instances.
- **Validate:** establish the sequential invariant first. Prefer a deterministic local test with a synchronization barrier around the relevant window; otherwise use the smallest bounded concurrent request pair on scoped disposable state. Compare final persisted state and audit events to expected outcomes.
- **Evidence:** demonstrate duplicate effects, limit overruns or an invalid transient/final state. State concurrency, reset steps and reproducibility; one timeout is not proof.
- **Fix:** enforce atomic storage operations, transactional invariants, database constraints and idempotency tied to the intended action/identity. Ensure controls span workers/instances where needed.
- **Example:** `if (coupon.used) reject(); apply(); coupon.used = true;` lets two simultaneous requests both pass the check. An atomic `UPDATE coupons SET used = true WHERE id = ? AND used = false`, then applying the discount only when exactly one row changed, closes the window.
- **Avoid false positives:** UI debounce and an in-process mutex may not protect multiple application instances. Conversely, a visible check-then-act sequence may be safe inside a correct transaction. Lack of reproduction does not eliminate a narrow race window; record what source evidence establishes and what remains unknown.
