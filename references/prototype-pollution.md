# Prototype pollution

Source: [PortSwigger Prototype pollution](https://portswigger.net/web-security/prototype-pollution).

- **Inspect:** recursive merges, path setters, query/JSON parsers and inherited-property lookups in frontend and backend JavaScript. Trace attacker-controlled keys through `__proto__` and `constructor.prototype` paths to a downstream gadget such as policy, template or process configuration.
- **Validate:** in a fresh disposable process/page, merge a synthetic nested value and inspect whether a previously unrelated object inherits the canary. Trace the altered inherited property to a relevant security decision. Recreate/terminate the isolated environment to remove global contamination.
- **Evidence:** establish prototype modification rather than an ordinary own property, then show the reachable gadget/effect. Separate pollution alone from an evidenced escalation; do not assume arbitrary code execution.
- **Fix:** use schemas and safe merge/setter libraries, constrain dangerous keys at all depths, use own-property checks and null-prototype dictionaries where appropriate, and avoid inherited defaults for security decisions.
- **Example:** A naive recursive merge of `JSON.parse('{"__proto__":{"isAdmin":true}}')` makes `({}).isAdmin === true` for the whole process. Client-side: `?__proto__[transport_url]=data:,alert(1)` parsed by a query-string library pollutes the prototype, and a script that reads `config.transport_url` with no own value loads it. Server-side gadgets include `shell` or `env` options read by `child_process.spawn`.
- **Avoid false positives:** parsing a `__proto__` JSON key alone does not necessarily mutate a prototype. A vulnerable library needs a reachable input path and relevant operation. Freezing one prototype or blocking one key spelling may leave other paths; verify the exact library/version and downstream gadget.
