"""
Chirp — a deliberately vulnerable mini social app for the COMP90082 W8
"Common Web Attacks" lecture.

⚠️  INTENTIONALLY INSECURE. Run only on localhost, never deploy or expose it.

One app hosts the whole lecture. Every flaw has a `SECURE`-gated fix in the
SAME place, so you can run an attack, set SECURE=1, and watch it fail on the
same URL.

    python app.py                 # vulnerable (default)
    SECURE=1 python app.py        # every mitigation on

Routes / lessons:
    POST /login            SQL injection auth bypass          (slides 23-29)
    GET  /profile?user_id  Broken access control / IDOR       (slides 30-33)
    /  (comments)          Stored XSS -> cookie theft         (slides 34-41)
    /change_email          CSRF                               (new)
"""
import os
import secrets
import sqlite3

# Optional .env support (no hard dependency).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from flask import (Flask, request, redirect, url_for, session, render_template,
                   abort)
from werkzeug.security import check_password_hash

from config import Config, SECURE, ATTACKER_URL
import db

app = Flask(__name__)
app.config.from_object(Config)
app.teardown_appcontext(db.close_db)


@app.before_request
def _ensure_db():
    db.init_db()


# --- helpers -------------------------------------------------------------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def csrf_token():
    tok = session.get("csrf_token")
    if not tok:
        tok = secrets.token_hex(16)
        session["csrf_token"] = tok
    return tok


def _do_login(row):
    session.clear()
    session["user_id"] = row["id"]
    session["csrf_token"] = secrets.token_hex(16)


@app.context_processor
def inject_globals():
    return {
        "SECURE": SECURE,
        "ATTACKER_URL": ATTACKER_URL,
        "csrf_token": csrf_token,
        "me": current_user(),
    }


# --- feed + stored XSS (slides 34-41) ------------------------------------
@app.route("/", methods=["GET", "POST"])
def feed():
    conn = db.get_db()
    post = conn.execute("SELECT * FROM posts ORDER BY id LIMIT 1").fetchone()
    if request.method == "POST":
        author = request.form.get("author") or "Anonymous"
        body = request.form.get("body", "")
        conn.execute(
            "INSERT INTO comments (post_id, author, body) VALUES (?, ?, ?)",
            (post["id"], author, body),
        )
        conn.commit()
        return redirect(url_for("feed"))
    comments = conn.execute("SELECT * FROM comments ORDER BY id").fetchall()
    # The XSS lives in feed.html: comment bodies are rendered with |safe unless
    # SECURE, in which case Jinja auto-escapes them.
    return render_template("feed.html", post=post, comments=comments)


# --- login + SQL injection (slides 23-29) --------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    query = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = db.get_db()
        if SECURE:
            # SECURE: parameterized query + hashed-password check.
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            if row and check_password_hash(row["password_hash"], password):
                _do_login(row)
                return redirect(url_for("feed"))
            error = "Invalid credentials"
        else:
            # VULNERABLE: SQL built by string interpolation, plaintext password.
            #   Try username:   ' OR 1=1 --      (any password)
            query = ("SELECT * FROM users WHERE username = '%s' AND password = '%s'"
                     % (username, password))
            try:
                row = conn.execute(query).fetchone()
            except sqlite3.Error as exc:
                row, error = None, "SQL error: %s" % exc
            if row:
                _do_login(row)
                return redirect(url_for("feed"))
            error = error or "Invalid credentials"
    return render_template("login.html", error=error, query=query)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("feed"))


# --- profile + broken access control / IDOR (slides 30-33) ---------------
@app.route("/profile")
def profile():
    user_id = int(request.args.get("user_id", session.get("user_id") or 0))
    if SECURE:
        # SECURE: a URL parameter is never trusted for access control; you may
        # only view your own profile (identity comes from the session).
        if session.get("user_id") != user_id:
            abort(403)
    row = db.get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        abort(404)
    return render_template("profile.html", user=row)


# --- change email + CSRF (new) -------------------------------------------
@app.route("/change_email", methods=["GET", "POST"])
def change_email():
    user = current_user()
    if not user:
        abort(401)
    if SECURE:
        # SECURE: state change must be POST and carry the per-session CSRF token.
        # (On localhost SameSite can't tell :5050 from :6001 — same host — so the
        #  token is the defense that actually works here.)
        if request.method != "POST":
            abort(405)
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(403, "CSRF token missing or invalid")
    # VULNERABLE: no token, accepts GET or POST, trusts the ambient session cookie.
    new_email = request.values.get("new_email", "")
    if new_email:
        conn = db.get_db()
        conn.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user["id"]))
        conn.commit()
    return redirect(url_for("profile", user_id=user["id"]))


if __name__ == "__main__":
    banner = "SECURE ✅" if SECURE else "VULNERABLE ⚠️"
    # Default 5050: macOS reserves :5000 for the AirPlay Receiver. Override with PORT.
    port = int(os.environ.get("PORT", 5050))
    print("Starting Chirp in %s mode on http://127.0.0.1:%d" % (banner, port))
    app.run(host="127.0.0.1", port=port, debug=True)
