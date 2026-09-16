# 🔐 COMP90082 W8 — Software Vulnerability & Security (VulnLab)

👋 **Welcome, Students!**

This week's lecture gives you a **fundamental understanding of web security** and helps
you spot vulnerabilities in your own software project. The code here accompanies the
*Common Web Attacks* slides.

**VulnLab** is a small teaching app with **one section per vulnerability**. Each section
has a *what is it?* explainer, an interactive demo with a **Vulnerable / Secure toggle**,
and a *what happened under the hood* reveal (for SQL injection, the actual backend query
your input produced).

> ⚠️ **Intentionally vulnerable.** Run it **only on localhost**, never deploy or expose it.
> Only use these techniques against the local targets here. For authorized, educational use.

---

## 🚀 Quick start

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app/app.py          # http://127.0.0.1:5050
```

Open **http://127.0.0.1:5050** and pick a vulnerability from the sidebar. Flip each
section's **Vulnerable / Secure** toggle to compare the exploit with the fix live — no
restart, no separate terminals.

> ℹ️ Defaults to **port 5050** because macOS reserves `:5000` for the AirPlay Receiver.
> To use `:5000`, turn AirPlay Receiver off (System Settings → General → AirDrop &
> Handoff) and run `PORT=5000 python app/app.py`.

---

## 🧪 The sections (`app/`)

| # | Section (route) | Vulnerability | Slides |
|---|---|---|---|
| 1 | `/sql-injection` | SQL injection auth bypass (with the executed query revealed) | 23–29 |
| 2 | `/access-control` | Broken access control / IDOR | 30–33 |
| 3 | `/xss` | Stored XSS → cookie theft (inline attacker log) | 34–41 |
| 4 | `/csrf` | Cross-site request forgery | new |
| 5 | `/prompt-injection` | Prompt injection in an AI agent | 42 |

Each section is self-contained; there is **no global mode flag** — the toggle is
per-section and per-request.

## 🔎 Static & dependency analysis (`static_analysis/`)
A deliberately naive analyzer (to show its blind spots), then **real tools**:

```bash
bash static_analysis/run_scans.sh   # naive vs. bandit, semgrep, pip-audit
```

## 🤖 Prompt injection, also as a CLI (`demos/prompt_injection/`)
The prompt-injection section reuses this deterministic, offline mock; the CLI version
still runs standalone (`python demos/prompt_injection/agent_unsafe.py`).

## 🌐 Optional: separate-origin attacker (`attacker/`)
The XSS section shows cookie theft inline. For a more realistic *separate-origin*
version, `attacker/evil_server.py` (port 6001) hosts a cookie-collector and a CSRF
trap page — see `attacker/payloads.md`.

---

## 🗺️ OWASP & STRIDE (for your Sprint 3 threat model)
[`docs/OWASP_STRIDE_mapping.md`](docs/OWASP_STRIDE_mapping.md) maps every section to
OWASP Top 10 (2021) and a STRIDE category. The [instructor runbook](docs/INSTRUCTOR_RUNBOOK.md)
has a timed running order. The Sprint 3 template is
[`sprint3_threat_modeling_template.markdown`](sprint3_threat_modeling_template.markdown).
