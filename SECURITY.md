# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

---

## Reporting a Vulnerability

If you discover a security vulnerability in File Solver, **please do not open
a public GitHub Issue**.

Instead, email the maintainers privately (add your contact email here) or use
GitHub's [private security advisory](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
feature.

We will acknowledge your report within 48 hours and aim to release a fix
within 14 days for critical issues.

---

## Security Design

### API Keys

- API keys are **never** hardcoded.
- API keys are **never** printed to the terminal (even in debug mode).
- API keys are **never** written to output `.solved` files.
- The `.env` file and `*.solved` files are excluded from version control via `.gitignore`.
- Users are expected to use **their own API keys** — no shared/public key exists.

### File Processing

File Solver treats all uploaded files as **untrusted input**:

- Files are **only read**, never executed.
- No shell commands, scripts, macros, or embedded code from within files are
  ever executed.
- Large files are rejected before processing (configurable via `MAX_FILE_SIZE`).
- Encrypted PDFs are rejected (they cannot be read without a password).

### Dependencies

- Dependencies are pinned via `pyproject.toml`.
- We recommend users install File Solver in an isolated virtual environment.
- Keep dependencies up to date to receive security patches.

### No Cloud Storage

- File Solver runs **entirely locally** in its default CLI mode.
- Input files and output files remain on your machine.
- Only the **extracted text** from your file is sent to the OpenAI API for
  solving. The original file is never uploaded.

### Responsible Use

This tool uses a third-party AI API (OpenAI by default).  Please review
[OpenAI's usage policies](https://openai.com/policies/usage-policies) to
ensure your use case is permitted.

---

## Scope

The following are **in scope** for security reports:

- API key leakage
- Arbitrary code execution from file content
- Path traversal / directory escape in output file writing
- Dependency vulnerabilities with a known CVE

The following are **out of scope**:

- AI model hallucinations (not a security issue)
- Rate-limit exhaustion of your own API key
