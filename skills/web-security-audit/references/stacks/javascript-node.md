# JavaScript and TypeScript on the server

Covers Node.js with Express, NestJS, Fastify, Koa and Hapi, plus Deno and Bun. Meta-framework server code (Next.js, Nuxt, SvelteKit, Remix) also appears in [frontend-frameworks.md](../frontend-frameworks.md).

## Entry points and enforcement

- **Entry points:** `app.get/post/...`, `router.*`, NestJS `@Controller` with `@Get/@Post`, `@Body`, `@Param`, `@Query`, Fastify route schemas, GraphQL resolvers, `ws`/Socket.IO `on('message')` handlers, queue consumers and cron jobs.
- **Enforcement:** middleware order (a route registered before `app.use(auth)` is unprotected), NestJS `@UseGuards` and global guards with `@Public()`-style metadata, Passport strategies, per-handler ownership checks and ORM scopes.
- **Input shape:** `express.urlencoded({ extended: true })` and `qs` turn `a[b]=c` into nested objects, which feeds NoSQL operator injection and prototype pollution. NestJS `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })` strips or rejects unknown fields.

## Topic leads

| Topic | Leads | Safe defaults and notes |
| --- | --- | --- |
| SQL injection | template literals or `+` in `query(`, `sequelize.query`, `sequelize.literal`, `knex.raw`, `.whereRaw`, Prisma `$queryRawUnsafe`/`$executeRawUnsafe`/`Prisma.raw`, TypeORM `.query(` and string `.where(` | Prisma's tagged-template `$queryRaw` parameterizes; knex/TypeORM bindings (`?`, `:name`) are safe |
| NoSQL injection | `find(req.body)`, `findOne({ email: req.body.email })` where the value can be an object, `$where`, `$regex`/`$expr` built from input, `mapReduce` | Mongoose `sanitizeFilter` or explicit `String(value)` casts; schema validation before the query |
| Command injection | `child_process.exec`/`execSync`, `spawn`/`execFile` with `shell: true`, `execa` with `shell`, `shelljs.exec` | `execFile`/`spawn` with an argument array avoids the shell; option injection still applies |
| Code execution and deserialization | `eval(`, `new Function(`, `vm.runIn*` (not a security boundary), `vm2` (abandoned, known escapes), `node-serialize.unserialize`, `js-yaml` 3.x `load` | `js-yaml` 4 `load` uses a safe schema; `JSON.parse` does not instantiate classes |
| SSTI | `ejs.render(userTemplate)`, `pug.compile(`, `Handlebars.compile(`, `nunjucks.renderString(`, `_.template(` on user strings; passing all of `req.query`/`req.body` as template data (EJS option injection) | Fixed templates with data objects are safe |
| Prototype pollution | `lodash.merge`/`_.set`/`_.defaultsDeep` on older versions, `deepmerge`, `merge-deep`, custom recursive merge or path setters on request data | See [prototype-pollution.md](../prototype-pollution.md) |
| Path traversal | `path.join(root, input)` then `startsWith(root)` without a trailing separator, `fs.*` with input, `res.sendFile(input)` without `root`, `res.download`, archive extraction (`adm-zip`, `tar`) | `res.sendFile(name, { root })` and `express.static` reject traversal |
| XXE | `libxmljs` `parseXml(..., { noent: true })` | `xml2js` and `fast-xml-parser` do not resolve external entities |
| SSRF | `fetch(`, `axios(`, `got(`, `node-fetch`, `undici`, `http.request` with user URLs; image proxies and webhooks | Check redirect following and resolved-IP validation (for example in an agent `lookup` hook) |
| CORS | `cors({ origin: true, credentials: true })` (reflects any origin), origin callbacks using `includes`/`endsWith`/unanchored regex | `origin: '*'` cannot be combined with credentialed reads |
| Host header and proxies | `app.set('trust proxy', true)`, `req.hostname`/`req.protocol`/`req.headers.host` in reset or invite links | Prefer a configured canonical base URL |
| Information disclosure | Express default error handler outside `NODE_ENV=production` (stack traces), `err.stack` in responses, GraphQL `debug`, verbose `console.log` of tokens | |
| JWT | `jwt.decode(` used for authorization, `jwt.verify` without `algorithms`, `audience` and `issuer`, keys fetched from token-supplied URLs | `jsonwebtoken` 9 rejects `none` by default |
| Sessions and CSRF | `express-session` with a hard-coded `secret`, `cookie.secure: false` in production, `csurf` (deprecated) or no CSRF on cookie-authenticated mutations | |
| GraphQL | Apollo Server `introspection: true` in production, `csrfPrevention: false`, `allowBatchedHttpRequests: true`, `formatError` returning raw errors, no depth/cost plugin; Yoga/Envelop without armor plugins; resolvers reading `args.userId` instead of `context.user` | See [graphql.md](../graphql.md) |
| Dependencies | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, install scripts (`postinstall`), git or tarball dependencies | `npm audit`/`pnpm audit` output is a lead; check reachability |

## Starting searches

```text
Entry points: app\.(get|post|put|patch|delete|use)|router\.|@(Controller|Get|Post|Put|Patch|Delete)\(|resolvers|on\(['"]message
Interpreters: \$queryRawUnsafe|\.raw\(|whereRaw|sequelize\.query|child_process|exec\(|eval\(|new Function|vm\.run|\.compile\(|renderString
Data flow: req\.(body|query|params)|merge\(|_\.set|defaultsDeep|\$where|\$regex
Outbound/config: fetch\(|axios|got\(|trust proxy|cors\(|jwt\.(decode|verify)|session\(
```
