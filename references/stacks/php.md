# PHP

Covers plain PHP, Laravel and Symfony.

## Entry points and enforcement

- **Entry points:** `$_GET`, `$_POST`, `$_REQUEST`, `$_COOKIE`, `$_FILES`, `$_SERVER`, `php://input`, Laravel `routes/*.php` and `$request->input/all()`, Symfony `#[Route]` controllers, queued jobs and console commands.
- **Enforcement:** Laravel `auth` middleware, `Gate`, policies and `$this->authorize()`; Symfony `access_control` rules (evaluated in order), `#[IsGranted]` and voters.

## Topic leads

| Topic | Leads | Safe defaults and notes |
| --- | --- | --- |
| SQL injection | `mysqli_query`/`$pdo->query` with interpolation or concatenation, Laravel `DB::raw`, `whereRaw`, `orderByRaw`, `selectRaw`, `DB::statement`, `orderBy($request->sort)`, Doctrine DQL built from strings | Prepared statements, Eloquent/query-builder bindings and Doctrine parameters |
| Command injection | `system`, `exec`, `shell_exec`, backticks, `passthru`, `popen`, `proc_open`, `mail()` fifth argument | `escapeshellcmd` still permits argument injection; prefer `escapeshellarg` per argument or Symfony `Process` with an array |
| File inclusion and path traversal | `include`/`require` with input, `file_get_contents`, `fopen`, `readfile` with input, `allow_url_include` | Use `realpath` and compare with a separator-terminated base |
| Insecure deserialization | `unserialize($input)`, `phar://` paths reaching filesystem functions on PHP < 8 | `unserialize($x, ['allowed_classes' => false])` or JSON |
| SSTI | Twig `createTemplate($input)`, Smarty `fetch('string:' . $input)`, Blade compiled from user strings | |
| XSS | `echo` of request data, Blade `{!! !!}`, Twig `|raw` or `autoescape false` | Blade `{{ }}` and Twig autoescape by default |
| XXE | `LIBXML_NOENT`, `LIBXML_DTDLOAD` flags | libxml2 2.9+ does not load external entities by default |
| Type juggling | `==` on tokens, hashes or passwords (`"0e123" == "0e456"`), `strcmp`/`in_array` without strict mode | Use `hash_equals` and `===` |
| Mass assignment | Eloquent `$guarded = []`, `create/fill/update($request->all())`, `forceFill` | Use `$request->validated()` or explicit `$fillable` |
| CSRF | Laravel CSRF exceptions (`$except` or `validateCsrfTokens(except: ...)`), Symfony forms with `csrf_protection: false` | Laravel web routes verify CSRF by default |
| SSRF | `file_get_contents($url)`, `curl_exec`, Guzzle with user URLs; wrappers such as `php://`, `file://` and `gopher://` | |
| Information disclosure | `APP_DEBUG=true`, `phpinfo()`, `display_errors=On`, `.env` reachable from the web root, Symfony profiler (`/_profiler`) in production | |
| Host header and proxies | `$_SERVER['HTTP_HOST']` in links, Laravel `TrustProxies` with `'*'`, missing `TrustHosts`, Symfony `trusted_proxies`/`trusted_hosts` | |
| Sessions | missing `session_regenerate_id(true)` after login | |
| Dependencies | `composer.lock` | `composer audit` output is a lead |

## Starting searches

```text
Entry points: \$_(GET|POST|REQUEST|COOKIE|FILES|SERVER)|php://input|Route::|#\[Route
Interpreters: DB::raw|whereRaw|orderByRaw|->query\(|system\(|shell_exec|passthru|proc_open|unserialize|createTemplate|\{!!|\|raw
Config/data: \$guarded|->all\(\)|APP_DEBUG|TrustProxies|trusted_|==\s*\$|include\s*\(?\$
```
