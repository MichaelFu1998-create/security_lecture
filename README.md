# 🔐 COMP90082 Software Project — Software Vulnerability & Security (Week 8)

👋 **Welcome, Students!**

This week's lecture gives you a **fundamental understanding of cybersecurity**
and helps you spot vulnerabilities in your own software project. The code here
accompanies the *Common Web Attacks* slides.

> ⚠️ **These apps are intentionally vulnerable.** Run them **only on your own
> machine (localhost)**. Never deploy or expose them, and only use the attack
> techniques against the local targets provided here. This is for authorized,
> educational use.

---

## 🚀 Quick start

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Run the **one unified demo app** and the **attacker server** side by side:

```bash
# Terminal A — the victim app (vulnerable by default)
python app/app.py                 # http://127.0.0.1:5050

# Terminal B — the attacker's collection server
python attacker/evil_server.py    # http://127.0.0.1:6001
```

> ℹ️ The app defaults to **port 5050** because macOS reserves `:5000` for the
> AirPlay Receiver. To match the slides' `:5000` URLs exactly, turn AirPlay
> Receiver off (System Settings → General → AirDrop & Handoff) and run
> `PORT=5000 python app/app.py`.

Then walk the attacks in [`attacker/payloads.md`](attacker/payloads.md), or
follow the timed [`docs/INSTRUCTOR_RUNBOOK.md`](docs/INSTRUCTOR_RUNBOOK.md).

**One switch flips the whole app from vulnerable to secured** — run an attack,
then re-run with mitigations on and watch it fail on the *same* URL:

```bash
SECURE=1 python app/app.py
```

---

## 🧪 What's inside

### `app/` — the unified vulnerable app ("Chirp")
A small social app (login, profiles, posts/comments) where a *chain* of real
flaws leads to account takeover. Each flaw has its `SECURE`-gated fix in the
same file:

| Attack | Route | Slides |
|---|---|---|
| SQL injection (auth bypass) | `POST /login` | 23–29 |
| Broken access control / IDOR | `GET /profile?user_id=` | 30–33 |
| Stored XSS → cookie theft → session hijack | `/` comments | 34–41 |
| CSRF (forced email change) | `/change_email` | new |
| Plaintext passwords, hardcoded secret | (throughout) | new |

### `attacker/` — the "evil.com" server
Receives stolen cookies (`/steal`) and hosts a CSRF trap (`/csrf_poc.html`), so
cookie theft is shown **end to end** rather than as a `console.log`.

### `demos/prompt_injection/` — prompt injection (slide 42)
A deterministic, **offline** demo showing an LLM agent hijacked by injected
instructions — the same class of bug as SQL injection and XSS.

```bash
python demos/prompt_injection/agent_unsafe.py   # secret exfiltrated 💀
python demos/prompt_injection/agent_safe.py     # defended ✅
```

### `static_analysis/` — finding bugs before attackers do
A deliberately naive analyzer (to show its blind spots), then **real tools**:

```bash
bash static_analysis/run_scans.sh   # naive vs. bandit, semgrep, pip-audit
```

---

## 🗺️ Mapping to OWASP & STRIDE (for your Sprint 3 threat model)
[`docs/OWASP_STRIDE_mapping.md`](docs/OWASP_STRIDE_mapping.md) maps every demo
to OWASP Top 10 (2021), a STRIDE category, and the matching rows in the
threat-modeling template.

## ⚠️ Sprint 3 threat-modeling template
Available in [`sprint3_threat_modeling_template.markdown`](sprint3_threat_modeling_template.markdown).
