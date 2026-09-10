"""
Central switch for the whole demo.

Set the environment variable SECURE=1 to turn every mitigation ON at once
(so you can run an attack, flip the switch, and re-run it on the SAME URL).
With SECURE unset/0 the app is deliberately vulnerable.
"""
import os


def is_secure():
    return os.environ.get("SECURE", "0").lower() in ("1", "true", "yes", "on")


SECURE = is_secure()

# Where the stored-XSS payload ships stolen cookies (see attacker/evil_server.py)
ATTACKER_URL = "http://127.0.0.1:6001"


class Config:
    SECURE = SECURE

    # --- Secret key ------------------------------------------------------
    # VULNERABLE: a secret hardcoded in source control. Anyone who can read
    # the repo can forge or tamper with session cookies. (This is exactly the
    # anti-pattern the old demo shipped: secret_key = 'supersecretkey'.)
    # SECURE: read it from the environment; fall back to a random per-boot key.
    if SECURE:
        SECRET_KEY = os.environ.get("APP_SECRET_KEY") or os.urandom(32).hex()
    else:
        SECRET_KEY = "supersecretkey"

    # --- Session cookie flags -------------------------------------------
    # VULNERABLE: HttpOnly OFF => document.cookie can read the session id,
    #   so a stored-XSS payload can exfiltrate it (slides 38-41).
    # SECURE: HttpOnly ON => JavaScript cannot read it; SameSite adds
    #   defense-in-depth.
    # NOTE: Secure/HTTPS is intentionally left off so the cookie is actually
    #   stored over http://127.0.0.1 during the lecture. Turn it on in prod.
    SESSION_COOKIE_HTTPONLY = SECURE
    SESSION_COOKIE_SAMESITE = "Strict" if SECURE else None
