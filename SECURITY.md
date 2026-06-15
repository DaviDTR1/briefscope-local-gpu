# Security Policy

Thanks for helping keep BriefScope safe for its users.

BriefScope is a plugin (module) for the [QueAI](https://github.com/queai-project/QueAI)
kernel. This policy covers the **BriefScope LOCAL GPU** plugin only. For
vulnerabilities in the kernel itself, report them to the QueAI project.

## Supported versions

| Version | Security support |
|---|---|
| `1.x` (`main` branch) | ✅ actively maintained |
| `< 1.0` (pre-releases) | no retroactive guarantee — please upgrade to the latest tag |

## How to report a vulnerability

**Do not open a public issue** for security vulnerabilities.

Use GitHub Private Vulnerability Reporting on this plugin's repository, or
contact the repository owner directly.

Please include at least:

- Plugin version (`manifest.json` → `version`) and kernel version.
- Reproduction steps.
- Observed or expected impact (unauthorized read/write, RCE, privilege
  escalation, etc.).
- Your availability to coordinate disclosure.

## What to expect

- **Acknowledgement within 72 h** of submission.
- **Triage within 7 days**: we confirm whether it's an issue, its estimated
  severity and a target fix date.
- **Coordinated disclosure**: we work on a private fix and credit you when
  publishing the advisory and the patched version, unless you prefer to stay
  anonymous.

## In-scope

- Vulnerabilities in the plugin backend (`app/`) — RAG, agents, file
  generation, configuration and the REST API under `/api/briefscope_local_gpu`.
- Path traversal or unauthorized access through the document upload and the
  `/files` download route.

## Out-of-scope

- Vulnerabilities in the QueAI kernel (report to the kernel project).
- Vulnerabilities in third-party dependencies (including the NVIDIA Container
  Toolkit) that have no exploit path through this plugin (report upstream; we
  will bump the pin once a fix is available).
- Issues requiring physical access to the host or valid kernel operator
  credentials.

## Notes specific to the LOCAL GPU variant

This variant runs **fully offline**: the LLM runs in a bundled Ollama container
accelerated by an NVIDIA GPU, and embeddings run in-process via
sentence-transformers. By default it needs **no API keys and no outbound
internet** once the model and embedding weights have been downloaded.

- It requires the **NVIDIA Container Toolkit** on the host and exposes the GPU
  to the Ollama container. Treat GPU passthrough as part of your host's trust
  boundary.
- Models are pulled from the Ollama registry on first use; embedding weights are
  downloaded from the Hugging Face hub on first use. After that, operation is
  offline.
- The variant *also* allows pointing the LLM at a cloud provider from the
  Settings UI; if you do that, the cloud notes from the CLOUD variants apply
  (an API key is stored in `data/config.json` and outbound traffic is enabled).

## Bug bounty

This project does not offer monetary rewards. It does offer public credit in
the changelog and the published advisory, unless you prefer to remain anonymous.
