# GraphQL

Source: [PortSwigger GraphQL API vulnerabilities](https://portswigger.net/web-security/graphql).

Load when the scope contains a GraphQL schema, resolvers, a GraphQL gateway or a GraphQL client. GraphQL changes the attack surface in three ways: one endpoint exposes a graph in which the same object can be reached through many paths, a single HTTP request can carry many operations, and authorization usually lives in resolvers and data loaders rather than in route rules. Load [identity and access](identity-access.md) alongside this file, and follow resolver arguments into the [injection](injection.md) group when they reach interpreters.

## Authorization across the graph

- **Inspect:** every way an object type can be reached: root queries, nested fields, `node(id:)`/`nodes(ids:)` lookups, union and interface members, mutation payloads, subscription events and federation `_entities`. Map which resolver, data loader or service method applies the owner, tenant and role check for each path. Check field-level rules on sensitive fields (email, address, internal notes, cost) and on mutations, including the objects returned in mutation payloads.
- **Validate:** with synthetic users A and B, request B's object through each path: the root field, a nested relation (for example `review { author { orders { ... } } }`), `node(id:)` with a global ID built from B's type and key, and the payload of a mutation that returns the object. Compare a scoped path with an unscoped one; a correct root resolver says nothing about the others. For batch loaders, check whether the loader receives the caller's identity and filters by it.
- **Evidence:** show an unauthorized object, field or mutation effect, the query used and the identity. GraphQL often returns HTTP 200 with partial `data` and an `errors` array; read both.
- **Fix:** enforce authorization in a layer every path shares: the service or repository method that loads the object, or a field-level policy that runs for the type regardless of the path. Pass the authenticated principal into data loaders. Prefer separate public types (for example `PublicProfile`) over reusing a private type that has sensitive fields.
- **Example:** `order(id:)` filters by the caller, but `Product.reviews.author` returns the full `Customer` type, and the unguarded `Customer.orders` resolver lists that customer's orders, so `product(id: 1) { reviews { author { email orders { total shippingAddress } } } }` leaks every reviewer's orders.
- **Avoid false positives:** an object visible through a nested path may be intentionally public; establish which fields of the type are meant to be visible to whom. `@PreAuthorize` or directive-based rules on a field resolver protect that field on every path, so check where the rule is attached before reporting.

## Query cost, batching and aliases

- **Inspect:** depth and complexity limits, list size limits and pagination caps, alias limits, array batching (several operations in one HTTP body), and how rate limits count work: per HTTP request, per operation or per resolver call. Look for sensitive mutations that rely on request-level rate limiting: login, MFA, coupon or gift-card redemption, password reset.
- **Validate:** read the configured limits; do not send expensive queries to a shared environment. To check whether a limit counts operations, use a small bounded case (for example 5 aliases of a harmless field) on an isolated instance and compare the rate-limit counter with 5 separate requests.
- **Evidence:** show that N attempts fit in one counted request (brute-force amplification) or that no depth, complexity or size limit exists for a reachable recursive or list-heavy query. Report availability risk from configuration, not from a load test.
- **Fix:** enforce depth, complexity and list-size limits in the GraphQL engine; limit aliases and batched operations; apply rate limits and lockouts per operation and per target object (account, code) inside the resolver or service, not per HTTP request.
- **Example:** `redeemGiftCard(code:)` is protected by a servlet filter allowing 30 requests per minute per IP. One request with 500 aliases (`a1: redeemGiftCard(code: "000001") a2: ...`) tries 500 codes, so a 6-digit code space falls in about a minute per IP.
- **Avoid false positives:** missing limits on a schema without recursion or large lists is a hardening observation. Do not demonstrate denial of service.

## Schema exposure, field suggestions and errors

- **Inspect:** introspection settings, GraphiQL/Playground/Altair availability in production, field suggestions in validation errors ("Did you mean ...?"), and error formatting: stack traces, exception messages, SQL or class names in `message` or `extensions`.
- **Validate:** confirm production configuration, not development defaults. Check whether the error handler passes raw exception text to clients.
- **Evidence:** show sensitive content (internal fields, secrets, SQL, stack traces) or a schema area that should not be discoverable and is also unprotected.
- **Fix:** mask unexpected errors with a generic message and a correlation ID; log details server-side. Disable introspection and IDEs in production where the schema is not public, and hide field suggestions where the server supports it (for example Apollo Server `hideSchemaDetailsFromClientErrors`).
- **Avoid false positives:** introspection, an enabled IDE or field suggestions are discovery aids, not vulnerabilities by themselves; rate them Informational or Low unless they expose sensitive data. Disabling them never fixes an authorization flaw.

## Transport and CSRF

- **Inspect:** whether the endpoint authenticates with cookies, which methods it accepts (GET queries, GET mutations), which content types it parses (`application/json`, `application/x-www-form-urlencoded`, `multipart/form-data` for uploads, `text/plain`), and any built-in CSRF protection.
- **Validate:** if cookies authenticate the request, determine whether a cross-site form or a GET navigation can reach a mutation; see [browser security](browser-security.md) for the browser conditions.
- **Evidence:** show a mutation executing from an attacker origin with the victim's cookies.
- **Fix:** reject mutations over GET, require `application/json` or a custom header for state-changing operations, and enable the server's CSRF protection (Apollo Server's `csrfPrevention`, on by default in current versions) including for multipart uploads.
- **Avoid false positives:** a GraphQL API authenticated only by an `Authorization` header set by script is not CSRF-exposed.

## Subscriptions

- **Inspect:** authentication of the WebSocket connection (`connection_init` payload or handshake cookie), Origin checks on the handshake, authorization per subscription and per event, and behaviour when the token expires or the user logs out during a long-lived subscription. Protocols: `graphql-ws` and the older `subscriptions-transport-ws`.
- **Validate:** subscribe as user B to an event stream filtered by an argument such as `orderId` belonging to user A, and check whether events arrive.
- **Fix:** authenticate at connection time, authorize each subscription and filter each event for the subscriber, and re-check or close subscriptions when credentials expire. See [WebSockets](api-realtime.md) for handshake hijacking.

## Persisted queries, gateways and federation

- **Inspect:** automatic persisted queries (APQ), trusted documents or operation safelists; gateway versus subgraph authorization; whether subgraphs are reachable directly; the federation `_entities` and `_service` fields.
- **Validate:** check whether the server accepts arbitrary query text or only registered operations. Check whether a subgraph enforces authorization itself or trusts headers set by the gateway (for example a user ID header) that a direct caller could send.
- **Fix:** treat APQ as a cache, not an allowlist; use a trusted-documents safelist when only first-party clients should run operations. Keep subgraphs on a private network, authenticate gateway-to-subgraph calls, and enforce object authorization in subgraphs too.
- **Avoid false positives:** APQ hashes in the client are not a weakness; a safelist reduces exposure but never replaces resolver authorization.

## Inputs and mutations

- **Inspect:** input types that include server-owned fields (`role`, `ownerId`, `price`, `status`), resolvers that pass arguments to SQL, NoSQL, shell, template, URL fetchers or file paths, and custom scalars (JSON, URL, Upload) that skip validation.
- **Fix:** keep input types to client-owned fields, validate custom scalars, and treat resolver arguments like any other untrusted input. Apply the [injection](injection.md), [SSRF](http-infrastructure.md) and [files](files-data.md) checks to the paths they reach.

## GraphQL clients in the frontend

- **Inspect:** Apollo Client, urql or Relay setup: how the auth token reaches the link or exchange, `credentials: 'include'` with cookie sessions, the normalized cache and any cache persistence (`apollo3-cache-persist`, localStorage), logout handling, subscription `connectionParams`, and rendering of GraphQL data into HTML or URL sinks.
- **Validate:** log in as A, load private data, log out, log in as B in the same tab and check whether A's cached objects render before refetching. Check that logout calls `client.clearStore()` (or `resetStore()`), clears persisted caches and closes the subscription client.
- **Fix:** clear the client cache and persisted cache on logout and on user switch; close and recreate the WebSocket client with the new credentials; render fields as text unless sanitized.
- **Avoid false positives:** queries and fragments in the bundle are expected; the backend must authorize them regardless. Field names visible in client code are not a disclosure finding.

## Server library leads

| Library | Authorization hooks | Limits and exposure settings | Notes |
| --- | --- | --- | --- |
| Spring for GraphQL (Java/Kotlin) | `@QueryMapping`, `@MutationMapping`, `@SchemaMapping`, `@BatchMapping`, `@SubscriptionMapping` with `@PreAuthorize` (needs `@EnableMethodSecurity`), `@AuthenticationPrincipal` | `spring.graphql.schema.introspection.enabled` (on by default), `spring.graphql.graphiql.enabled` (off by default), graphql-java `Instrumentation` beans such as `MaxQueryDepthInstrumentation` and `MaxQueryComplexityInstrumentation` | `@BatchMapping` and `DataLoader` methods receive parent objects, not the principal, unless you pass it; custom `DataFetcherExceptionResolver` implementations decide what error text leaks |
| Netflix DGS (Java/Kotlin) | `@DgsQuery`, `@DgsMutation`, `@DgsData`, `@DgsDataLoader` with Spring Security | graphql-java instrumentation beans | Same data-loader and nested-path concerns as above |
| Apollo Server (Node) | resolver context, schema directives, plugins | `introspection` (off when `NODE_ENV=production`), `csrfPrevention`, `allowBatchedHttpRequests` (off by default), `hideSchemaDetailsFromClientErrors`, `formatError` | Depth and cost limits need a plugin or validation rule |
| GraphQL Yoga / Envelop (Node) | context, plugins, `graphql-shield` | plugins for depth, cost, alias and token limits and for disabling introspection and suggestions | |
| Strawberry / Graphene (Python) | Strawberry `permission_classes`, Graphene resolver checks | Strawberry `QueryDepthLimiter` extension; disable introspection by validation rule | |
| Hot Chocolate (.NET) | `[Authorize]` on types and fields | execution depth and cost analysis options; introspection rules | |
| gqlgen (Go) | resolvers and directives | `handler` extensions such as `FixedComplexityLimit`; introspection is enabled by the default server | |

Confirm defaults against the installed version; several libraries have changed defaults between major releases.
