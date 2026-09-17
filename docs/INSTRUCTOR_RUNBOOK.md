# Instructor runbook — W8 Common Web Attacks (VulnLab)

A low-risk running order for the live demo. Everything is localhost-only, one server.

## Setup (once, before class)
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app/app.py                      # http://127.0.0.1:5050
```
> Port 5050 avoids the macOS AirPlay Receiver (which holds `:5000`). To use `:5000`,
> disable AirPlay Receiver and run `PORT=5000 python app/app.py`.

Open the browser at **http://127.0.0.1:5050** and keep it on screen. Introduce each
vulnerability, then open the matching section and demo it. Every section
has a **Vulnerable / Secure** toggle — show the attack, then flip to the fix.

## Running order (~15–18 min)
1. **SQL Injection** (`/sql-injection`). Click *insert payload* (`' OR 1=1 --`),
   any password, **login** → "authenticated (bypassed)". Show the **under the hood** panel:
   the concrete query your input produced. Flip to **secure** → login fails; the query now
   uses bound parameters.
2. **Broken Access Control** (`/access-control`). Click `user_id=2` in vuln →
   you read Bob's record; flip to **secure** → 403.
3. **Stored XSS → cookie theft** (`/xss`). Click *insert cookie-stealing
   payload*, **post** → the **🕵️ attacker log** fills with the stolen `vl_demo_session`
   cookie. Flip to **secure** → the comment shows as inert text and nothing is captured.
   Use *reset* to clear.
4. **Prompt Injection** (`/prompt-injection`). Choose the *poisoned ticket*,
   **run agent** in vuln → the agent leaks the secret; flip to **secure** → treated as data.
   Land the parallel: same bug class as SQLi/XSS.

## Static analysis + dependencies (optional, ~2 min)
```bash
bash static_analysis/run_scans.sh
```
Naive analyzer misses the f-string SQLi in `app/app.py`; bandit + semgrep catch it;
pip-audit flags the deliberately old `PyYAML`.

## Reset between runs
```bash
python app/db.py            # rebuild a clean vulnlab.db
```
(Or use each section's in-page *reset*.)

## Fallbacks
- Everything is deterministic and offline — no API keys, no second server needed.
- The optional separate-origin attacker (`attacker/evil_server.py`) is available if you
  want to show real cross-origin exfiltration; see `attacker/payloads.md`.
