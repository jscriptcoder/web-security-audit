# Files, serialized data and disclosure

## Path traversal

Source: [PortSwigger Path traversal](https://portswigger.net/web-security/file-path-traversal).

- **Inspect:** download/read/write/delete paths, static handlers, archive extraction and filenames. Follow joining, decoding, canonicalization, containment and symlink handling across layers.
- **Validate:** use a temporary directory with an allowed file and an outside canary. Test relevant absolute paths, separators and encodings against the actual platform. Check that containment is enforced on the final resolved target with a directory boundary.
- **Evidence:** show access outside the permitted root to synthetic data. Include write/delete impact only when established safely.
- **Fix:** prefer opaque server-mapped identifiers; canonicalize consistently, verify containment and use filesystem APIs that address symlink/race risks where applicable.
- **Example:** Python `os.path.join('/srv/files', '/etc/passwd')` returns `/etc/passwd` because an absolute second argument discards the base. A string check `path.startsWith('/srv/files')` accepts `/srv/files-old/secret.txt`; compare resolved paths by component or with a separator-terminated base.
- **Avoid false positives:** a string prefix check can accept a sibling directory with a matching prefix. Removing one traversal sequence is not canonical containment. A rejected path or a joined path in source does not alone establish exploitability; root constraints and symlink policy matter.

## File upload vulnerabilities

Source: [PortSwigger File uploads](https://portswigger.net/web-security/file-upload).

- **Inspect:** upload and download authorization, filename handling, actual content validation, storage location, serving headers, executable handlers, converters and asynchronous scans. Include object storage and signed URLs.
- **Validate:** use harmless synthetic files; compare extension, declared MIME and inspected content. Trace whether a file becomes executable or active same-origin content and whether another test user can retrieve it. Review archive/extraction and post-processing paths.
- **Evidence:** establish an unsafe serve/execute/transform path or unauthorized file access. Upload acceptance by itself is not a vulnerability.
- **Fix:** generate server filenames, validate allowed content, isolate storage from executable routes, enforce ownership, constrain processing resources and use appropriate content type/disposition on an isolated origin where needed.
- **Example:** An avatar endpoint accepts `avatar.svg` or `avatar.html` sent as `Content-Type: image/png`, stores it under `/uploads/` on the application origin and serves it with a type derived from the extension, which is stored XSS for anyone who opens the file URL. Serving uploads from a separate domain with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff` removes the impact.
- **Avoid false positives:** extension or client MIME validation alone is weak. An uploaded script stored as inert bytes is not remote code execution. An image processor may add a separate parsing risk without making every image upload unsafe.

## Information disclosure

Source: [PortSwigger Information disclosure](https://portswigger.net/web-security/information-disclosure).

- **Inspect:** errors, debug/admin endpoints, backups, source maps, client bundles, repositories, telemetry, exports and differences exposing sensitive resource existence. Follow build-time environment-variable injection.
- **Validate:** identify the exact disclosed information and intended audience; verify exposure using the appropriate unprivileged identity. For secrets, record location/type with redacted evidence and check whether it is a real credential or public identifier without using it against unrelated services.
- **Evidence:** specify exposed data and consequential access or privacy impact. Separate information helpful to reconnaissance from direct secret/personal-data leakage.
- **Fix:** remove sensitive client/build output, restrict diagnostics, sanitize errors, redact logs, constrain exports and rotate exposed credentials through the owner's process.
- **Example:** Material: a reachable `/actuator/heapdump`, `/.git/config` served from the web root, or a bundle containing a live server API key. Usually informational: a `main.js.map` revealing internal route names, or a framework version string in a header.
- **Avoid false positives:** GraphQL queries, route names, public client IDs and source maps are not automatically secret or high severity. Their risk depends on sensitive contents and backend protections; hiding them does not repair authorization.

## Insecure deserialization

Source: [PortSwigger Insecure deserialization](https://portswigger.net/web-security/deserialization).

- **Inspect:** native object serialization in cookies, tokens, queues, caches, imports and internal APIs; object construction hooks, gadget-bearing classes and signatures before parsing.
- **Validate:** trace whether an attacker can supply bytes to the dangerous deserializer. Use a benign fixture in an isolated harness or inspect a complete code path; verify whether authenticity is checked before any object reconstruction.
- **Evidence:** show attacker-controlled object behavior, unauthorized attribute change or a reachable unsafe primitive. Document gadget/stack assumptions instead of asserting code execution from a deserializer's name.
- **Fix:** use constrained data-only formats and schemas; avoid reconstructing executable object graphs from untrusted inputs. Restrict types and exposure where immediate replacement is impractical.
- **Example:** A `rememberMe` cookie whose base64 decodes to bytes starting `rO0AB` (Java serialization) is read with `ObjectInputStream.readObject()` before any signature check. Equivalent markers: PHP `O:4:"User":...`, Python pickle data in a cache, .NET `BinaryFormatter` payloads. Code execution still depends on gadget classes on the classpath; report the reachable primitive and state the gadget assumption.
- **Avoid false positives:** JSON decoding is not inherently native object deserialization. Base64 is encoding, not integrity protection. Internal queues can be attacker-influenced through producers; a signature checked after deserialization is too late to protect the parser.
