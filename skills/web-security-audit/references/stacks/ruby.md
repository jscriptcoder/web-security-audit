# Ruby

Covers Ruby on Rails, with notes that also apply to Sinatra and Rack applications.

## Entry points and enforcement

- **Entry points:** `config/routes.rb`, controller actions and `params`, ActionCable channels, ActiveJob/Sidekiq jobs, Rake tasks, Rack middleware.
- **Enforcement:** `before_action :authenticate_user!` and `skip_before_action`, Pundit `authorize`/`policy_scope` with `after_action :verify_authorized`, CanCanCan `load_and_authorize_resource`. `Model.find(params[:id])` is a lead; `current_user.models.find(params[:id])` or a policy scope is the usual fix.

## Topic leads

| Topic | Leads | Safe defaults and notes |
| --- | --- | --- |
| SQL injection | string interpolation in `where`, `find_by_sql`, `joins`, `group`, `having`, `select`, `pluck`; `order(params[:sort])`; `Arel.sql(input)` | Hash conditions and `where("col = ?", v)` bind values; recent Rails rejects raw SQL in `order`/`pluck` unless wrapped in `Arel.sql` |
| Command injection | backticks, `%x()`, `system`/`exec`/`spawn` with a single interpolated string, `Open3` with a single string, `IO.popen(string)`, `Kernel#open(input)` (a leading `|` runs a command) | Multi-argument `system("cmd", arg)` avoids the shell |
| Insecure deserialization | `Marshal.load`, `YAML.unsafe_load` or `YAML.load` on old Psych, `Oj.load` in object mode, `JSON.load` on untrusted input; cookie serializer `:marshal`/`:hybrid` with a leaked `secret_key_base` | Psych 4 (Ruby 3.1+) makes `YAML.load` safe; prefer `JSON.parse` |
| SSTI | `ERB.new(input).result`, `render inline: input` | Liquid is designed for user templates |
| XSS | `html_safe`, `raw`, `<%==`, `content_tag` with `html_safe` content, `link_to` with user URLs (`javascript:`), permissive `sanitize` allowlists | ERB escapes by default |
| Open redirect | `redirect_to params[...]`, `allow_other_host: true` | Rails 7 can raise on open redirects (`raise_on_open_redirects`) |
| Mass assignment | `params.permit!`, permitting `role`, `admin`, `owner_id` or `tenant_id` | Strong parameters |
| CSRF | `skip_before_action :verify_authenticity_token`, `protect_from_forgery with: :null_session` on cookie-authenticated routes | `ActionController::Base` protects by default |
| Path traversal | `send_file params[...]`, `File.read`/`File.open` with input, `render file:` | |
| XXE | Nokogiri parse options `noent`/`dtdload` | Nokogiri defaults do not resolve external entities |
| SSRF | `Net::HTTP`, `URI.open` (open-uri), Faraday, HTTParty with user URLs | |
| Information disclosure | `consider_all_requests_local = true` in production, missing `filter_parameters`, committed `master.key` or credentials | |
| Host header | `request.host` in mailers or links, missing `config.hosts` | |
| Dependencies | `Gemfile.lock` | `bundle audit` output is a lead |

## Starting searches

```text
Entry points: routes\.rb|params\[|params\.permit|ActionCable|perform\(
Enforcement: before_action|skip_before_action|authorize|policy_scope|load_and_authorize_resource
Interpreters: find_by_sql|where\(".*#\{|order\(params|Arel\.sql|Marshal\.load|YAML\.(unsafe_)?load|ERB\.new|render inline|html_safe|raw\(|`|%x\(|IO\.popen|open\(
```
