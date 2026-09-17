# From demo → OWASP Top 10 → STRIDE → your Sprint 3 threat model

Each attack in this repo maps to an industry category and to a STRIDE row you
can lift straight into `sprint3_threat_modeling_template.markdown`.

| Section (route) | OWASP Top 10 (2021) | STRIDE | The fix shown by the **Secure** toggle |
|---|---|---|---|
| SQL injection — `/sql-injection` `' OR 1=1 --` | A03: Injection | **T**ampering / **E**levation of Privilege | Parameterized query + hashed-password check |
| Broken access control — `/access-control?user_id=` | A01: Broken Access Control | **I**nformation Disclosure / **E**levation of Privilege | Identity from session; authorization check (never trust URL params) |
| Stored XSS → cookie theft — `/xss` | A03: Injection (XSS) / A05: Misconfiguration | **T**ampering / **I**nformation Disclosure | Output escaping (auto-escape) + CSP; `HttpOnly` on the session cookie |
| Prompt injection — `/prompt-injection` | LLM01 (OWASP Top 10 for LLM Apps) | **E**levation of Privilege / **I**nformation Disclosure | Keep untrusted content out of the instruction channel; tool allow-list; output filter; human-in-the-loop |
| Vulnerable dependency (`PyYAML 5.3.1`) | A06: Vulnerable & Outdated Components | **T**ampering | `pip-audit` / Dependabot; upgrade & pin |

## Why this matters for Sprint 3
The Sprint 3 deliverable asks each team to fill a STRIDE table for *their own*
project. The demos are worked examples of exactly that table: a concrete
threat, the affected component, the impact, and a validated mitigation. Point
students at the STRIDE column above and the matching rows (T1–T6) in the
template.
