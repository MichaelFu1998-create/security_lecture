# From demo → OWASP Top 10 → STRIDE → your Sprint 3 threat model

Each attack in this repo maps to an industry category and to a STRIDE row you
can lift straight into `sprint3_threat_modeling_template.markdown`.

| Demo (route) | Slides | OWASP Top 10 (2021) | STRIDE | The fix shown under `SECURE=1` |
|---|---|---|---|---|
| SQL injection — `/login` `' OR 1=1 --` | 23–29 | A03: Injection | **T**ampering / **E**levation of Privilege | Parameterized query + hashed-password check |
| Broken access control — `/profile?user_id=` | 30–33 | A01: Broken Access Control | **I**nformation Disclosure / **E**levation of Privilege | Identity from session; authorization check (never trust URL params) |
| Stored XSS — comment `<script>` | 34–37 | A03: Injection (XSS) | **T**ampering | Output escaping (Jinja auto-escape) + CSP |
| Cookie theft → session hijack | 38–41 | A05: Security Misconfiguration / A07: Auth Failures | **S**poofing / **I**nformation Disclosure | `HttpOnly` + `SameSite`; HTTPS `Secure` in prod |
| CSRF — `/change_email` | (new) | A01: Broken Access Control (CSRF) | **T**ampering / **S**poofing | Per-session CSRF token; POST-only; `SameSite` |
| Plaintext passwords | (new) | A02: Cryptographic Failures | **I**nformation Disclosure | `generate_password_hash` / `check_password_hash` |
| Hardcoded secret key | (new) | A05: Security Misconfiguration | **S**poofing (forged sessions) | Load secret from environment/secret store |
| Vulnerable dependency (`PyYAML 5.3.1`) | (new) | A06: Vulnerable & Outdated Components | **T**ampering | `pip-audit` / Dependabot; upgrade & pin |
| Prompt injection — agent obeys injected text | 42 | (LLM01, OWASP Top 10 for LLM Apps) | **E**levation of Privilege / **I**nformation Disclosure | Keep untrusted content out of the instruction channel; tool allow-list; output filter; human-in-the-loop |

## Why this matters for Sprint 3
The Sprint 3 deliverable asks each team to fill a STRIDE table for *their own*
project. The demos are worked examples of exactly that table: a concrete
threat, the affected component, the impact, and a validated mitigation. Point
students at the STRIDE column above and the matching rows (T1–T6) in the
template.
