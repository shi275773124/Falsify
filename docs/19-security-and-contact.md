# Security & Contact

## Founder contact

For **design partnerships, integrations, research collaboration, or product questions**, reach **Chris Shi**:

- Email: [shi275773124@gmail.com](mailto:shi275773124@gmail.com?subject=Falsify%20inquiry)
- X / Twitter: [https://x.com/aishikejian](https://x.com/aishikejian)
- GitHub: [https://github.com/shi275773124/Falsify](https://github.com/shi275773124/Falsify)

Falsify is an open-core, local/BYOK toolchain; this contact route does not imply hosted service, managed deployment, or private infrastructure.

## Security boundary

Falsify is a local/BYOK toolchain. Treat any review input and resulting artifact as potentially sensitive: they may contain code, operational details, source links, or provider output.

- Keep provider keys in environment variables or GitHub Secrets; never commit them.
- Review and scope the files sent to a model provider. The CLI cannot make a third-party provider private by itself.
- Keep generated JSON/Markdown artifacts where your repository and retention policy permit them.
- Do not interpret PASS as authorization to deploy, merge, trade, or operate a production system. It is a scoped evidence verdict, not an execution permission.

The local Web Console binds to 127.0.0.1 by default. Do not expose it beyond your machine without first reviewing its provider configuration and network boundary.

## Reporting a security issue

**Do not open a public issue with vulnerability details, credentials, private artifacts, or an exploit reproduction.** Email [shi275773124@gmail.com](mailto:shi275773124@gmail.com?subject=Falsify%20security%20report) with the subject Falsify security report instead. Include the affected version or commit, a minimal reproduction, impact and preconditions, and whether any artifact must remain private.

## Product questions and contributions

For public bugs, documentation corrections, and template improvements, open a GitHub issue with the command, expected behavior, actual behavior, and sanitized artifacts when available. Claims about a capability should link to a reproducible command, source file, or test; this project does not treat marketing copy as proof.
