# Server-side injection

## SQL injection

Source: [PortSwigger SQL injection](https://portswigger.net/web-security/sql-injection).

- **Inspect:** raw SQL, ORM escape hatches, dynamic sort/table/column construction and stored values later reused in queries. Trace the entire query construction.
- **Validate:** prefer inspecting generated SQL and bound parameters or an isolated integration test. For scoped runtime checks, use narrowly targeted paired inputs and controls. Do not assume a boolean probe is read-only: input can feed a second UPDATE/DELETE query.
- **Evidence:** establish attacker control over query syntax or a repeatable unauthorized query result; distinguish validation errors and unrelated latency from interpreter behavior.
- **Fix:** bind data values; map dynamic identifiers/directions through a fixed allowlist. Apply the same rule to stored input and background jobs. Constrain database privileges.
- **Example:** `"SELECT * FROM products WHERE category = '" + cat + "'"` with `cat = "' OR 1=1--"`. `ORDER BY ${sort}` cannot be parameterized; map `sort` through a fixed table such as `{price: "price", name: "name"}`.
- **Avoid false positives:** using an ORM does not make raw fragments safe, while normal ORM parameterization can eliminate an apparent concatenation concern. Escaping and WAF filtering are not equivalent to parameter binding.

## Command injection

Source: [PortSwigger Command injection](https://portswigger.net/web-security/os-command-injection).

- **Inspect:** shell execution, command strings, wrappers for converters/archives/media and arguments constructed from filenames or URLs. Distinguish shell syntax injection from dangerous executable options.
- **Validate:** inspect the invoked executable and argument boundaries; use a mocked process runner or disposable local harness with an inert marker. Limit approved runtime proof to harmless observable behavior.
- **Evidence:** show attacker input changing command/argument semantics and a relevant effect. Establish whether the invocation actually uses a shell and whether supplied values can become options.
- **Fix:** use a library API or fixed executable with an argument array, disable shell evaluation, validate argument semantics and separate options from data where supported.
- **Example:** `exec("convert " + filename + " out.png")` with `filename = "a.png; id"` runs a second command. Without any shell, `spawn("git", ["clone", url])` with `url = "--upload-pack=..."` is option injection; pass `--` before user-supplied arguments.
- **Avoid false positives:** an argument array prevents shell interpretation but can still permit option injection. The name `exec` varies across libraries; confirm semantics rather than flagging every occurrence. Do not run destructive commands or persistence payloads to establish impact.

## XXE injection

Source: [PortSwigger XXE](https://portswigger.net/web-security/xxe).

- **Inspect:** XML, SOAP, document/image conversion, SVG, office formats, XInclude and alternate content-type parsers. Identify the actual parser and external-resource settings.
- **Validate:** verify library/version defaults and application overrides. In isolation, use a local fixture or scoped callback marker to determine whether external entities/resources resolve; retain a negative control. Do not read real system files or trigger entity-expansion load tests.
- **Evidence:** demonstrate unauthorized external resolution, file access to a synthetic canary or a scoped network request from the parser.
- **Fix:** disable DTD/external entity/resource resolution and unneeded XInclude; use hardened parsers and processing limits.
- **Example:** An XML import echoes element text, so `<!DOCTYPE x [<!ENTITY e SYSTEM "file:///tmp/canary.txt">]><x>&e;</x>` returns the canary file. DOCX, XLSX and SVG uploads are XML too and reach the same parsers.
- **Avoid false positives:** accepting XML is not sufficient. Secure parser defaults and configuration can prevent resolution. JSON parsing alone is not XXE, but downstream file processors or alternate formats may introduce an XML path.

## NoSQL injection

Source: [PortSwigger NoSQL injection](https://portswigger.net/web-security/nosql-injection).

- **Inspect:** client objects merged into filters, operator-bearing fields, server-side JavaScript/query expressions and dynamic field paths. Trace nested JSON and stored input.
- **Validate:** compare an expected scalar with a controlled object/operator input on synthetic records. Inspect the query emitted to the datastore and whether schema validation rejects the input first.
- **Evidence:** show unintended predicate semantics or unauthorized results. A changed error response alone does not establish an injected query.
- **Fix:** enforce input types and explicit permitted fields; build query operators server-side; avoid evaluating user strings as query expressions. Bind authorization/tenant constraints independently of client filters.
- **Example:** `users.findOne({ user: body.user, pass: body.pass })` with a JSON body `{"user":"admin","pass":{"$ne":null}}` logs in without the password; a form body `pass[$ne]=x` does the same through an extended query-string parser.
- **Avoid false positives:** structured query APIs are safe when untrusted data remains a validated scalar. Do not transfer SQL payloads mechanically to another datastore. A blacklist of `$` keys may miss alternate syntax or later parsing and does not replace schema validation.

## Server-side template injection

Source: [PortSwigger SSTI](https://portswigger.net/web-security/server-side-template-injection).

- **Inspect:** user content compiled as templates, dynamic template names, custom email/document generators and privileged editing features. Distinguish template source from template data.
- **Validate:** determine engine and context from source/configuration before testing. Use paired harmless expression markers in an isolated renderer or approved test flow; rule out browser/client interpolation.
- **Evidence:** demonstrate server-side interpretation of attacker-controlled template syntax and identify accessible capabilities. Expression evaluation alone does not prove remote code execution.
- **Fix:** keep template code fixed and pass untrusted values as data. For deliberately user-authored templates, use a constrained language, minimal exposed objects and a separately isolated renderer.
- **Example:** A user-editable email template `Hello {{name}}` is compiled by Jinja2 or FreeMarker on the server, and `{{7*7}}` arrives in the sent email as `49`. The same `49` appearing only in an AngularJS page is client-side template injection (an XSS issue), not SSTI.
- **Avoid false positives:** displaying template-looking text or safely substituting a value is expected. HTML escaping can prevent XSS while leaving template evaluation unsafe. Engine sandbox claims require examining the actual engine/version/configuration.
