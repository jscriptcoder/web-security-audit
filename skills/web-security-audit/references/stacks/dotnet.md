# .NET

Covers ASP.NET Core MVC, Razor Pages, minimal APIs, Blazor and legacy ASP.NET on .NET Framework.

## Entry points and enforcement

- **Entry points:** `[ApiController]`/`Controller` actions, `[HttpGet]`/`[HttpPost]`, `[FromBody]`/`[FromQuery]`/`[FromRoute]`, minimal API `app.MapGet/MapPost`, Razor Page handlers (`OnPost*`), SignalR hubs, gRPC services, hosted services and message handlers.
- **Enforcement:** `[Authorize]` and policies, `[AllowAnonymous]` (overrides `[Authorize]` higher up), a configured `FallbackPolicy`, minimal API `.RequireAuthorization()`, resource-based `IAuthorizationService.AuthorizeAsync`, EF Core global query filters for tenancy (`IgnoreQueryFilters()` is a lead).

## Topic leads

| Topic | Leads | Safe defaults and notes |
| --- | --- | --- |
| SQL injection | `FromSqlRaw($"...")`/`ExecuteSqlRaw($"...")` with interpolation or concatenation, `SqlCommand` with built strings, Dapper `Query($"...")` | `FromSql`/`FromSqlInterpolated`/`ExecuteSqlInterpolated` parameterize interpolated values; LINQ queries are parameterized |
| Insecure deserialization | `BinaryFormatter`, `SoapFormatter`, `NetDataContractSerializer`, `LosFormatter`, `ObjectStateFormatter`, Newtonsoft `TypeNameHandling` other than `None`, `JavaScriptSerializer` with `SimpleTypeResolver`, types chosen from input for `XmlSerializer`/`DataContractSerializer`; ViewState without MAC or with a leaked `machineKey` | `System.Text.Json` does not deserialize arbitrary types; `BinaryFormatter` is removed in .NET 9 |
| XXE | `XmlDocument`/`XmlTextReader` on .NET Framework before 4.5.2, `XmlReaderSettings` with `DtdProcessing.Parse` and a non-null `XmlResolver` | Modern .NET defaults are safe |
| XSS | `Html.Raw`, `HtmlString`, Blazor `MarkupString`, `@Html.Raw(Json.Serialize(...))` inside `<script>` | Razor encodes by default |
| Command injection | `Process.Start` with `cmd.exe /c`, `bash -c`, or argument strings built from input | Use `ProcessStartInfo.ArgumentList` |
| Path traversal | `Path.Combine(base, input)` (a rooted `input` discards `base`), `PhysicalFile(`, `File.ReadAll*`, `ZipFile.ExtractToDirectory` with untrusted archives | Compare `Path.GetFullPath` results with a separator-terminated base |
| SSRF | `HttpClient.GetAsync(input)`, `WebClient`, `WebRequest.Create(input)` | |
| Mass assignment | binding request bodies to EF entities, `TryUpdateModelAsync` without an include list, missing `[Bind]` | Use input DTOs |
| CSRF | MVC actions without `[ValidateAntiForgeryToken]` or global `AutoValidateAntiforgeryToken`, `[IgnoreAntiforgeryToken]`, minimal API form endpoints without antiforgery | Razor Pages validate antiforgery tokens by default |
| CORS | `SetIsOriginAllowed(_ => true)` with `AllowCredentials()` (reflects any origin), `SetIsOriginAllowedToAllowWildcardSubdomains` | `AllowAnyOrigin()` with `AllowCredentials()` is rejected |
| Information disclosure | `UseDeveloperExceptionPage` or `ASPNETCORE_ENVIRONMENT=Development` in production, `customErrors mode="Off"`, secrets in `appsettings*.json`/`web.config` | |
| Host header and proxies | `ForwardedHeadersOptions` with cleared `KnownProxies`/`KnownNetworks`, `AllowedHosts: "*"`, `Request.Host` in generated links | |
| JWT | `TokenValidationParameters` with `ValidateIssuer`, `ValidateAudience`, `ValidateLifetime` or `RequireSignedTokens` set to `false`, custom `SignatureValidator`, `IssuerSigningKeyResolver` trusting token-supplied keys | |
| Dependencies | `*.csproj` `PackageReference`, `packages.lock.json`, `Directory.Packages.props` | `dotnet list package --vulnerable` output is a lead |

## Starting searches

```text
Entry points: \[Http(Get|Post|Put|Patch|Delete)|Map(Get|Post|Put|Patch|Delete)\(|OnPost|: Hub\b
Enforcement: \[Authorize|AllowAnonymous|FallbackPolicy|RequireAuthorization|AuthorizeAsync|IgnoreQueryFilters
Interpreters: FromSqlRaw|ExecuteSqlRaw|SqlCommand|BinaryFormatter|TypeNameHandling|LosFormatter|Html\.Raw|MarkupString|Process\.Start
Config: UseDeveloperExceptionPage|ForwardedHeaders|AllowedHosts|SetIsOriginAllowed|TokenValidationParameters
```
