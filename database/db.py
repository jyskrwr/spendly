import os
import sqlite3

from flask import g, current_app
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        db_path = current_app.config.get(
            'DATABASE',
            os.path.join(current_app.instance_path, 'spendly.db')
        )
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(current_app.instance_path, exist_ok=True)
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title      TEXT    NOT NULL,
            amount     REAL    NOT NULL,
            category   TEXT    NOT NULL,
            date       TEXT    NOT NULL,
            notes      TEXT,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    db.commit()


def seed_db():
    try:
        db = get_db()
        cursor = db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("password123")),
        )
        user_id = cursor.lastrowid
        db.executemany(
            "INSERT INTO expenses (user_id, title, amount, category, date, notes)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [
                (user_id, "Lunch at Cafe",        450.00,  "Food & Dining", "2026-06-28", None),
                (user_id, "Metro card recharge",  200.00,  "Transport",     "2026-06-27", None),
                (user_id, "Netflix subscription", 649.00,  "Entertainment", "2026-06-25", "Monthly"),
                (user_id, "Groceries",           1200.00,  "Shopping",      "2026-06-24", None),
                (user_id, "Electricity bill",    3200.00,  "Housing",       "2026-06-20", "June bill"),
            ],
        )
        db.commit()
    except sqlite3.IntegrityError:
        pass
