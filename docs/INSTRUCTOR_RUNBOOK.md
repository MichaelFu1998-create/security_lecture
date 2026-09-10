# Instructor runbook — W8 Common Web Attacks demo

A low-risk running order for the live demo. Everything is localhost-only.

## Setup (once, before class)
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
Two terminals:
```bash
# Terminal A — the victim app (vulnerable by default)
python app/app.py                      # http://127.0.0.1:5050
# Terminal B — the attacker's collection server
python attacker/evil_server.py         # http://127.0.0.1:6001
```
> Port 5050 avoids the macOS AirPlay Receiver (which holds `:5000`). Slides 31–32
> show `:5000`; either note the difference aloud, or disable AirPlay Receiver and
> run `PORT=5000 python app/app.py` to match them exactly.

## Running order (~15–18 min)
All payloads are in `attacker/payloads.md`.

1. **SQL injection (slides 23–29).** On `/login`, username `' OR 1=1 --`, any
   password → logged in as Alice. Show the built query printed under the form.
2. **Broken access control (slides 30–33).** Visit `/profile?user_id=1` then
   `?user_id=2` — you read Bob's private email. Same URL the slide shows.
3. **Stored XSS → cookie theft → hijack (slides 34–41).**
   - Post the `<script>...steal?c=...</script>` comment.
   - Reload the feed as a logged-in user; show the cookie land in
     `attacker/stolen.log` (Terminal B prints it too).
   - Replay it: `curl http://127.0.0.1:5050/profile --cookie "session=<value>"`
     — you are now the victim.
4. **CSRF (new).** Logged in, open `http://127.0.0.1:6001/csrf_poc.html`; the
   victim's email silently becomes `attacker@evil.com`.

5. **Flip the switch.** Stop Terminal A, restart with `SECURE=1 python app/app.py`,
   and re-run 1–4. Each now fails: invalid credentials, 403, the script shows as
   inert text, cookie unreadable, CSRF token rejected. The banner turns green.

6. **Static analysis + dependencies.**
   ```bash
   bash static_analysis/run_scans.sh
   ```
   Naive analyzer misses the f-string SQLi in `app/app.py`; bandit + semgrep
   catch it; pip-audit flags the deliberately old `PyYAML`.

7. **Prompt injection (slide 42).**
   ```bash
   python demos/prompt_injection/agent_unsafe.py     # leaks secrets.txt 💀
   python demos/prompt_injection/agent_safe.py        # defended ✅
   ```
   Land the parallel: same bug as SQLi/XSS — untrusted input reaching an
   interpreter's instruction channel.

## Reset between runs
```bash
python app/db.py            # rebuild a clean chirp.db (wipes comments/edits)
rm -f attacker/stolen.log
```

## Fallbacks
- If live cookie replay is fiddly in a browser, use the `curl --cookie` form.
- Keep a short screen-recording of steps 3–4 as backup.
