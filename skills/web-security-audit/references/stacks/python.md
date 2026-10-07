# Python

Covers Django, Django REST Framework, Flask and FastAPI/Starlette.

## Entry points and enforcement

- **Entry points:** Django `urls.py` and views, DRF `ViewSet`/`APIView`, Flask `@app.route`/blueprints, FastAPI `@app.get/post` and `APIRouter`, Celery tasks, management commands and signal handlers.
- **Enforcement:** Django `@login_required`, `LoginRequiredMixin`, `@permission_required`; DRF `permission_classes` (the project default `DEFAULT_PERMISSION_CLASSES` is `AllowAny` unless configured) and `get_queryset` scoping; FastAPI `Depends(...)` on routes or routers; Flask `before_request` and decorators.
- **Object scoping:** `Model.objects.get(pk=pk)` in a view is a lead; scoped lookups such as `request.user.orders.get(pk=pk)` or a filtered `get_queryset` are the usual fix.

## Topic leads

| Topic | Leads | Safe defaults and notes |
| --- | --- | --- |
| SQL injection | `cursor.execute(f"...")` or `%`/`.format` into the SQL string, Django `.raw(`, `.extra(`, `RawSQL(`, SQLAlchemy `text(f"...")`, `order_by(user_input)` | ORM filters and `cursor.execute(sql, params)` bind values |
| Command injection | `os.system`, `os.popen`, `subprocess.*(..., shell=True)`, string commands passed to `subprocess` | Argument lists without `shell=True` avoid the shell |
| Insecure deserialization | `pickle.loads`/`load`, `dill`, `joblib.load`, `shelve`, `marshal`, `jsonpickle.decode`, `yaml.load(..., Loader=yaml.Loader)`/`yaml.unsafe_load`, `torch.load(..., weights_only=False)` | `yaml.safe_load`; recent PyTorch defaults to `weights_only=True` |
| SSTI | `render_template_string(user)`, `jinja2.Template(user)`, `Environment().from_string(user)` without `SandboxedEnvironment`, Django `Template(user)`, Mako | Fixed templates with context data are safe |
| XSS | Django `mark_safe`, `|safe`, `{% autoescape off %}`; Flask `Markup(user)`; a plain `jinja2.Environment` without `autoescape` | Django templates and Flask `.html` templates autoescape; `format_html` is safe |
| XXE | `lxml` parsers with `resolve_entities=True` or network access, `xml.sax` with external-entity features enabled | Prefer `defusedxml`; check the installed `lxml` defaults |
| Path traversal | `os.path.join(base, user)` (an absolute `user` discards `base`), `open(user)`, Flask `send_file(user)`, `tarfile.extractall` without `filter="data"` | Flask `send_from_directory` uses a safe join |
| SSRF | `requests.get(user)`, `httpx`, `aiohttp`, `urllib.request.urlopen` (also handles `file:`) | Check redirects and resolved-address validation |
| Mass assignment | DRF `ModelSerializer` with `fields = "__all__"`, writable `role`/`owner`/`is_staff` fields, Pydantic models shared between read and update | Separate input schemas with explicit fields |
| CSRF | `@csrf_exempt`, broad `CSRF_TRUSTED_ORIGINS`, Flask apps with cookie sessions and no CSRF extension | Django enables `CsrfViewMiddleware` by default |
| CORS | `CORS_ALLOW_ALL_ORIGINS = True` with `CORS_ALLOW_CREDENTIALS = True`, Starlette `CORSMiddleware(allow_origins=["*"], allow_credentials=True)` or a loose `allow_origin_regex` | Verify the actual response headers; some combinations echo the request origin |
| Information disclosure | `DEBUG = True`, Flask `debug=True`/Werkzeug debugger (an interactive console), hard-coded `SECRET_KEY`, `ALLOWED_HOSTS = ["*"]` | A leaked Django/Flask secret key allows session or signed-value forgery |
| Host header and proxies | `request.get_host()` with `USE_X_FORWARDED_HOST = True`, Werkzeug `ProxyFix` counts larger than the real proxy chain, `request.host_url` in reset links | |
| JWT | PyJWT `decode(..., options={"verify_signature": False})`, missing `algorithms`/`audience`/`issuer`, `python-jose` with permissive algorithms | PyJWT 2 requires `algorithms` |
| Dependencies | `requirements*.txt`, `poetry.lock`, `uv.lock`, `Pipfile.lock`, `pyproject.toml` | `pip-audit` output is a lead; check reachability |

## Starting searches

```text
Entry points: urlpatterns|path\(|@app\.route|@(app|router)\.(get|post|put|patch|delete)|ViewSet|APIView|@shared_task
Enforcement: login_required|permission_classes|DEFAULT_PERMISSION_CLASSES|Depends\(|get_queryset|csrf_exempt
Interpreters: \.raw\(|\.extra\(|RawSQL|text\(f|execute\(f|shell=True|os\.system|pickle|yaml\.load|unsafe_load|render_template_string|from_string|mark_safe
Config: DEBUG|SECRET_KEY|ALLOWED_HOSTS|CORS_|USE_X_FORWARDED_HOST|ProxyFix
```
