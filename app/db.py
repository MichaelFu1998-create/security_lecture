"""SQLite access + first-run seeding for the Chirp demo app."""
import os
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "chirp.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "seed.sql")

# username, plaintext password, email, bio
SEED_USERS = [
    ("alice",   "password123", "alice@example.com",   "Coffee, code, and cats."),
    ("bob",     "hunter2",     "bob@example.com",     "Weekend cyclist."),
    ("mallory", "letmein",     "mallory@evil.com",    "Totally trustworthy."),
]

SEED_POSTS = [
    (1, "Welcome to Chirp! This is Alice's first post — leave a comment below."),
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
    for author_id, body in SEED_POSTS:
        conn.execute(
            "INSERT INTO posts (author_id, body) VALUES (?, ?)", (author_id, body)
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # `python db.py` (re)builds a fresh database.
    init_db(force=True)
    print("Rebuilt", DB_PATH)
