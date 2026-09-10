-- Schema only. Rows (with real password hashes) are inserted by db.py.
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password      TEXT NOT NULL,   -- VULNERABLE anti-pattern: plaintext password
    password_hash TEXT NOT NULL,   -- used by SECURE mode (werkzeug pbkdf2)
    email         TEXT NOT NULL,
    bio           TEXT
);

CREATE TABLE posts (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    body      TEXT NOT NULL,
    created   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE comments (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id  INTEGER NOT NULL,
    author   TEXT NOT NULL,
    body     TEXT NOT NULL,
    created  TEXT DEFAULT (datetime('now'))
);
