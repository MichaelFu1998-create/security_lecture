"""
VulnLab — a deliberately vulnerable web-security teaching lab for the COMP90082
W8 "Common Web Attacks" lecture.

⚠️  INTENTIONALLY INSECURE. Run only on localhost, never deploy or expose it.

One section per vulnerability, each self-contained: a "what is it?" explainer,
an interactive demo with an inline Vulnerable/Secure toggle, and a "what
happened under the hood" reveal. Nothing to chain together — open a section,
show the attack, flip the toggle, show the fix.

    python app.py            # http://127.0.0.1:5050  (override with PORT=)

Sections:
    /sql-injection     SQL injection auth bypass
    /access-control    Broken access control / IDOR
    /xss               Stored XSS -> cookie theft
    /prompt-injection  Prompt injection in an agent
"""
import os
import sqlite3

from flask import (Flask, request, redirect, url_for, render_template,
                   abort, make_response, jsonify)
from werkzeug.security import check_password_hash

import db
import agents

app = Flask(__name__)
app.teardown_appcontext(db.close_db)

# (id, label, url-slug) — drives the sidebar menu.
SECTIONS = [
    ("sql_injection",   "SQL Injection",           "sql-injection"),
    ("access_control",  "Broken Access Control",   "access-control"),
    ("xss",             "Stored XSS + Cookie Theft", "xss"),
    ("prompt_injection", "Prompt Injection",       "prompt-injection"),
]

# In-memory "attacker log" for the XSS section (cookies beaconed by the payload).
_xss_loot = {"captured": None}


@app.before_request
def _ensure_db():
    db.init_db()


@app.context_processor
def inject_globals():
    return {"SECTIONS": SECTIONS}


def _mode():
    """Per-request vulnerable/secure choice (default vulnerable)."""
    return "secure" if (request.values.get("mode", "vuln").lower() == "secure") else "vuln"


# --- Home ----------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html", section="home", mode="")


# --- 1. SQL injection -------------------------------------
@app.route("/sql-injection", methods=["GET", "POST"])
def sql_injection():
    mode = _mode()
    result = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = db.get_db()
        if mode == "secure":
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            ok = bool(row and check_password_hash(row["password_hash"], password))
            result = {
                "mode": "secure", "ok": ok,
                "user": row["username"] if (ok and row) else None,
                "executed": 'cursor.execute("SELECT * FROM users WHERE username = ?", (username,))',
                "params": [username, "<hash-checked separately>"],
            }
        else:
            query = ("SELECT * FROM users WHERE username = '%s' AND password = '%s'"
                     % (username, password))
            try:
                row, err = conn.execute(query).fetchone(), None
            except sqlite3.Error as exc:
                row, err = None, str(exc)
            result = {
                "mode": "vuln", "ok": bool(row),
                "user": row["username"] if row else None,
                "executed": query, "username": username, "password": password,
                "error": err,
            }
    return render_template("sql_injection.html", section="sql_injection",
                           mode=mode, result=result)


# --- 2. Broken access control / IDOR ----------------------
@app.route("/access-control")
def access_control():
    mode = _mode()
    current_id = 1  # "you are logged in as alice (#1)"
    result = None
    raw = request.args.get("user_id")
    if raw is not None:
        try:
            uid = int(raw)
        except ValueError:
            uid = 0
        denied = (mode == "secure" and uid != current_id)
        row = None
        if not denied:
            row = db.get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        result = {"uid": uid, "denied": denied, "user": row,
                  "other": bool(row) and uid != current_id}
    return render_template("access_control.html", section="access_control",
                           mode=mode, current_id=current_id, result=result)


# --- 3. Stored XSS + cookie theft -------------------------
@app.route("/xss", methods=["GET", "POST"])
def xss():
    mode = _mode()
    conn = db.get_db()
    if request.method == "POST":
        conn.execute("INSERT INTO comments (author, body) VALUES (?, ?)",
                     (request.form.get("author") or "anon", request.form.get("body", "")))
        conn.commit()
        return redirect(url_for("xss", mode=mode))
    # In secure mode nothing can be stolen (escaped output + HttpOnly cookie),
    # so clear any loot captured during an earlier vulnerable run — otherwise a
    # stale value would make secure mode look like it leaked.
    if mode == "secure":
        _xss_loot["captured"] = None
    comments = conn.execute("SELECT * FROM comments ORDER BY id").fetchall()
    resp = make_response(render_template("xss.html", section="xss", mode=mode,
                                         comments=comments, loot=_xss_loot["captured"]))
    # Demo cookie: readable by JS in vuln (no HttpOnly); protected in secure.
    resp.set_cookie("vl_demo_session", "alice-session-abc123",
                    httponly=(mode == "secure"), samesite="Lax")
    return resp


@app.route("/xss/collect")
def xss_collect():
    c = request.args.get("c", "")
    if c:
        _xss_loot["captured"] = c
    return ("", 204)


@app.route("/xss/loot")
def xss_loot():
    return jsonify(captured=_xss_loot["captured"])


@app.route("/xss/reset")
def xss_reset():
    conn = db.get_db()
    conn.execute("DELETE FROM comments")
    conn.commit()
    _xss_loot["captured"] = None
    return redirect(url_for("xss", mode=_mode()))


# --- 4. Prompt injection --------------------------------------
@app.route("/prompt-injection")
def prompt_injection():
    mode = _mode()
    kind = "benign" if request.args.get("ticket") == "benign" else "poisoned"
    ticket = agents.BENIGN_TICKET if kind == "benign" else agents.POISONED_TICKET
    outcome = None
    if request.args.get("run"):
        steps, reply, leaked = agents.run_agent(ticket, mode)
        outcome = {"steps": steps, "reply": reply, "leaked": leaked}
    return render_template("prompt_injection.html", section="prompt_injection",
                           mode=mode, ticket=ticket, kind=kind,
                           system=agents.SYSTEM_PROMPT, outcome=outcome)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print("VulnLab on http://127.0.0.1:%d" % port)
    app.run(host="127.0.0.1", port=port, debug=True)
