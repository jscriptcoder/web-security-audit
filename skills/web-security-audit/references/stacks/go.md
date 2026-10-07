# Go

Covers `net/http` and routers/frameworks such as chi, gin, echo and fiber.

## Entry points and enforcement

- **Entry points:** `http.HandleFunc`/`mux.Handle`, router `GET/POST/Group` registrations, gRPC services, GraphQL resolvers (gqlgen), WebSocket upgraders and background workers.
- **Enforcement:** middleware attached to router groups; a route registered outside the protected group or before middleware is attached is public. Check per-handler ownership checks and repository-level tenant filters.

## Topic leads

| Topic | Leads | Safe defaults and notes |
| --- | --- | --- |
| SQL injection | `db.Query/Exec(fmt.Sprintf(...))` or `+` concatenation, GORM `Raw`, `Exec`, `Where(fmt.Sprintf(...))`, `Order(input)`, `Select(input)`, `Group(input)` | Placeholders (`?`, `$1`) and GORM `Where("col = ?", v)` bind values |
| XSS | `text/template` used to render HTML, `template.HTML(input)`, `template.JS`, `template.URL`, `template.HTMLAttr` conversions, `w.Write` of user data without an explicit `Content-Type` (Go sniffs the type) | `html/template` escapes by context |
| Command injection | `exec.Command("sh", "-c", ...)`, `bash -c` | `exec.Command(name, args...)` does not use a shell |
| Path traversal | `filepath.Join(base, input)` (cleans `..` but does not contain), `os.Open(input)`, `http.ServeFile(w, r, input)`, archive extraction using entry names | `http.FileServer(http.Dir(root))` contains requests; use `os.Root` (Go 1.24+) or `filepath.IsLocal` for containment |
| SSRF | `http.Get(input)`, `http.NewRequest` with user URLs; the default client follows up to 10 redirects | Validate resolved addresses in `net.Dialer.Control` and set `CheckRedirect` |
| Deserialization and mass assignment | `json.Unmarshal`/`Bind` into database model structs (writable role, owner or tenant fields) | `encoding/json` and `gob` do not instantiate arbitrary types; the risk is field binding, not gadget chains |
| XXE | | `encoding/xml` does not resolve external entities |
| CORS | `rs/cors` `AllowOriginFunc` returning `true` with `AllowCredentials`, gin-contrib/cors `AllowAllOrigins` with credentials | |
| Information disclosure | `import _ "net/http/pprof"` (registers `/debug/pprof` on the default mux), `expvar` (`/debug/vars`), panic messages returned to clients | |
| Host header and proxies | `r.Host` or `X-Forwarded-Host` in generated links, proxy middleware trusting forwarded headers from any client | |
| JWT | `golang-jwt` `Parse` with a key function that does not check `token.Method`, `ParseUnverified` for authorization | `jwt/v5` `WithValidMethods` pins algorithms |
| Race conditions | shared maps or counters across goroutines, check-then-act around database calls | `go test -race` finds data races in exercised paths |
| Dependencies | `go.mod`, `go.sum` | `govulncheck` reports reachable vulnerable symbols, which is stronger evidence than a version match |

## Starting searches

```text
Entry points: HandleFunc|\.Handle\(|\.(GET|POST|PUT|PATCH|DELETE)\(|\.Group\(|Upgrader
Interpreters: Sprintf\(.*(SELECT|INSERT|UPDATE|DELETE|WHERE)|\.Raw\(|\.Order\(|text/template|template\.(HTML|JS|URL)|exec\.Command
Outbound/config: http\.Get|NewRequest|net/http/pprof|expvar|AllowOriginFunc|ParseUnverified|X-Forwarded-Host
```
