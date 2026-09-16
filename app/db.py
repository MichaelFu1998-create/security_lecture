"""SQLite access + first-run seeding for VulnLab."""
import os
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "vulnlab.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "seed.sql")

# username, plaintext password, email, bio
SEED_USERS = [
    ("alice",   "password123", "alice@example.com", "Coffee, code, and cats."),
    ("bob",     "hunter2",     "bob@example.com",   "Weekend cyclist."),
    ("mallory", "letmein",     "mallory@evil.com",  "Totally trustworthy."),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(force=False):
    """Create + seed the DB on first run. `force=True` rebuilds it."""
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DB_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    for username, pw, email, bio in SEED_USERS:
        conn.execute(
            "INSERT INTO users (username, password, password_hash, email, bio) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, pw, generate_password_hash(pw), email, bio),
        )
    conn.commit()
    conn.close()


def reset_state():
    """Undo whatever the demos mutated: clear XSS comments, restore emails."""
    conn = get_db()
    conn.execute("DELETE FROM comments")
    for uid, (_u, _pw, email, _bio) in enumerate(SEED_USERS, start=1):
        conn.execute("UPDATE users SET email = ? WHERE id = ?", (email, uid))
    conn.commit()


if __name__ == "__main__":
    init_db(force=True)
    print("Rebuilt", DB_PATH)
