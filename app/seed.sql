-- Schema only. Rows (with real password hashes) are inserted by db.py.
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password      TEXT NOT NULL,   -- plaintext (anti-pattern, shown in the SQLi section)
    password_hash TEXT NOT NULL,   -- used by the secure branch (werkzeug pbkdf2)
    email         TEXT NOT NULL,
    bio           TEXT
);

CREATE TABLE comments (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    author   TEXT NOT NULL,
    body     TEXT NOT NULL,
    created  TEXT DEFAULT (datetime('now'))
);
