# APIs and realtime channels

## API testing

Source: [PortSwigger API testing](https://portswigger.net/web-security/api-testing).

- **Inspect:** documented and implemented routes, versions, methods, accepted content types, schemas, writable fields, bulk operations and server-to-server parameter construction. Use source and observed frontend requests to reconcile the inventory.
- **Validate:** compare the expected contract with handling of extra fields, type mismatches, duplicate parameters and alternate methods/formats. On synthetic objects, test whether a field such as role, owner or tenant can be assigned outside policy. Trace backend requests for parameter pollution across parser boundaries.
- **Evidence:** show a reachable policy violation, unexpected sensitive response field or changed protected property. Record the endpoint/version and authenticated identity.
- **Fix:** enforce schemas, explicit writable-field allowlists and per-operation/object authorization; build downstream requests with structured serializers and bind trusted identity separately from user input.
- **Example:** `PATCH /api/users/me` with `{"displayName":"a","role":"admin"}` succeeds because the handler copies the request body onto the user entity. Server-side parameter pollution: a backend that builds `http://internal/users?id=${id}` from `id=7%26role%3Dadmin` lets the client append its own internal parameter.
- **Avoid false positives:** public OpenAPI documentation is not inherently a disclosure finding. Rate limits must be evaluated against meaningful operation counts and abuse scenarios; do not stress the service. An unused legacy route is a hypothesis until deployment reachability is established.

## GraphQL API vulnerabilities

GraphQL has its own reference: [GraphQL](graphql.md). It covers authorization across graph paths and data loaders, query cost, aliases and batching, schema exposure and errors, transport and CSRF, subscriptions, persisted queries and federation, and GraphQL clients.

## WebSockets

Source: [PortSwigger WebSockets](https://portswigger.net/web-security/websockets).

- **Inspect:** handshake authentication/Origin checks, per-message permission enforcement, channel subscriptions, connection expiry, reconnect paths and client rendering of messages.
- **Validate:** use a controlled foreign-origin page to check cross-site WebSocket hijacking when credentials are automatically included. Compare synthetic users on subscriptions/object messages and examine behavior after expiry/logout or a role change. Limit message replay to reversible test actions.
- **Evidence:** show unauthorized connection/message/channel access, victim-state changes or readable private messages. Distinguish client-injected display artifacts from server-delivered messages.
- **Fix:** validate browser origins against a narrow allowlist, authenticate connections, enforce permission on each action/subscription and close or reevaluate sessions when required. Apply message schemas and bounds.
- **Example:** The handshake is authenticated only by a session cookie and the server never checks `Origin`; a page on another site runs `new WebSocket('wss://app.example/ws')`, the browser attaches the cookie, and the page reads the victim's messages (cross-site WebSocket hijacking). `SameSite=Lax`/`Strict` cookies block this from cross-site pages but not from a compromised sibling subdomain.
- **Avoid false positives:** ordinary HTTP CORS headers do not govern WebSocket handshake access. A successful handshake does not prove sensitive access. Origin checking mitigates browser hijacking but is not authentication for non-browser clients that can forge the header.
