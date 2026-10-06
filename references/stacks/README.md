# Stack hints

Stack-specific search leads that complement the stack-neutral checks in the topic references. Load only the files for stacks present in the audited scope. Each file lists entry points, enforcement locations, dangerous APIs per topic and the framework defaults that commonly explain false positives.

| Stack | File |
| --- | --- |
| Java and Kotlin (Spring, Ktor, Jakarta EE, Micronaut, Quarkus) | [java-kotlin.md](java-kotlin.md) |
| JavaScript and TypeScript on the server (Node, Express, NestJS, Fastify, Deno, Bun) | [javascript-node.md](javascript-node.md) |
| Python (Django, Flask, FastAPI) | [python.md](python.md) |
| .NET (ASP.NET Core, Blazor) | [dotnet.md](dotnet.md) |
| Go | [go.md](go.md) |
| PHP (Laravel, Symfony) | [php.md](php.md) |
| Ruby (Rails) | [ruby.md](ruby.md) |

Frontend framework escape hatches live in [frontend-frameworks.md](../frontend-frameworks.md).

Use these as leads for `rg`; adapt the patterns to the codebase. A match is a place to read, not a finding. Version-dependent defaults are called out; confirm the resolved version from the lockfile or build file before relying on them.

To add a stack, copy the shape of an existing file: entry points and enforcement, a topic table of leads, and safe defaults.
