"""SQLite storage layer for expenses."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    category TEXT NOT NULL,
    note TEXT DEFAULT '',
    spent_on TEXT NOT NULL
);
"""


@dataclass
class Expense:
    id: int
    amount_cents: int
    category: str
    note: str
    spent_on: date

    @property
    def amount(self) -> float:
        return self.amount_cents / 100


class ExpenseStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def add(self, amount: float, category: str, note: str = "", spent_on: date | None = None) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")
        # Store money as integer cents to avoid floating point rounding errors.
        cents = round(amount * 100)
        spent_on = spent_on or date.today()
        cur = self.conn.execute(
            "INSERT INTO expenses (amount_cents, category, note, spent_on) VALUES (?, ?, ?, ?)",
            (cents, category.strip().lower(), note, spent_on.isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def delete(self, expense_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def list(self, month: str | None = None, category: str | None = None) -> list[Expense]:
        query = "SELECT id, amount_cents, category, note, spent_on FROM expenses WHERE 1=1"
        params: list = []
        if month:  # format YYYY-MM
            query += " AND substr(spent_on, 1, 7) = ?"
            params.append(month)
        if category:
            query += " AND category = ?"
            params.append(category.lower())
        query += " ORDER BY spent_on, id"
        rows = self.conn.execute(query, params).fetchall()
        return [Expense(r[0], r[1], r[2], r[3], date.fromisoformat(r[4])) for r in rows]

    def totals_by_category(self, month: str | None = None) -> dict[str, float]:
        query = "SELECT category, SUM(amount_cents) FROM expenses"
        params: list = []
        if month:
            query += " WHERE substr(spent_on, 1, 7) = ?"
            params.append(month)
        query += " GROUP BY category ORDER BY SUM(amount_cents) DESC"
        return {cat: cents / 100 for cat, cents in self.conn.execute(query, params)}
