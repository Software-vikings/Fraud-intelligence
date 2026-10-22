"""SQLite-backed analyst case management and audit trail for the local demo."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class CaseStore:
    ALLOWED_STATUSES = {"OPEN", "IN_REVIEW", "ESCALATED", "CONFIRMED_FRAUD", "FALSE_POSITIVE", "CLOSED"}

    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(str(self.db_path))
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    transaction_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'OPEN',
                    assigned_to TEXT NOT NULL DEFAULT 'Unassigned',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    latest_note TEXT NOT NULL DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS case_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT NOT NULL,
                    old_status TEXT,
                    new_status TEXT NOT NULL,
                    assigned_to TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    def ensure_cases(self, transaction_ids):
        now = self._now()
        with self._connect() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO cases(transaction_id, status, assigned_to, created_at, updated_at) VALUES (?, 'OPEN', 'Unassigned', ?, ?)",
                [(str(tx_id), now, now) for tx_id in transaction_ids],
            )

    def list_cases(self):
        with self._connect() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM cases ORDER BY updated_at DESC").fetchall()]

    def get_case(self, transaction_id):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM cases WHERE transaction_id = ?", (transaction_id,)).fetchone()
            return dict(row) if row else None

    def update_case(self, transaction_id, status, assigned_to, note):
        status = str(status).upper()
        if status not in self.ALLOWED_STATUSES:
            raise ValueError("Unsupported case status.")
        note = str(note).strip()
        if len(note) < 5:
            raise ValueError("Please provide an investigation note of at least 5 characters.")
        assigned_to = (str(assigned_to).strip() or "Unassigned")[:80]
        now = self._now()
        with self._connect() as conn:
            current = conn.execute("SELECT * FROM cases WHERE transaction_id = ?", (transaction_id,)).fetchone()
            if not current:
                raise KeyError(transaction_id)
            old_status = current["status"]
            conn.execute(
                "UPDATE cases SET status = ?, assigned_to = ?, updated_at = ?, latest_note = ? WHERE transaction_id = ?",
                (status, assigned_to, now, note, transaction_id),
            )
            conn.execute(
                "INSERT INTO case_events(transaction_id, old_status, new_status, assigned_to, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (transaction_id, old_status, status, assigned_to, note, now),
            )
            updated = conn.execute("SELECT * FROM cases WHERE transaction_id = ?", (transaction_id,)).fetchone()
            return dict(updated)

    def history(self, transaction_id):
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(
                "SELECT * FROM case_events WHERE transaction_id = ? ORDER BY id DESC", (transaction_id,)
            ).fetchall()]
