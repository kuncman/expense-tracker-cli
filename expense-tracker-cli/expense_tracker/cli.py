"""Command-line interface: `expense add|list|summary|delete`."""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date
from pathlib import Path

from .db import ExpenseStore

DEFAULT_DB = Path(os.environ.get("EXPENSE_DB", Path.home() / ".expenses.db"))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="expense", description="Track your spending from the terminal.")
    p.add_argument("--db", type=Path, default=DEFAULT_DB, help="path to the SQLite database")
    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("-n", "--note", default="")
    add.add_argument("-d", "--date", type=date.fromisoformat, help="YYYY-MM-DD (default: today)")

    ls = sub.add_parser("list", help="list expenses")
    ls.add_argument("-m", "--month", help="YYYY-MM")
    ls.add_argument("-c", "--category")

    summ = sub.add_parser("summary", help="totals per category")
    summ.add_argument("-m", "--month", help="YYYY-MM")

    exp = sub.add_parser("export", help="export to CSV")
    exp.add_argument("file", type=Path)

    rm = sub.add_parser("delete", help="delete an expense by id")
    rm.add_argument("id", type=int)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = ExpenseStore(args.db)

    if args.command == "add":
        try:
            new_id = store.add(args.amount, args.category, args.note, args.date)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(f"Added expense #{new_id}: ${args.amount:.2f} ({args.category})")

    elif args.command == "list":
        rows = store.list(args.month, args.category)
        if not rows:
            print("No expenses found.")
        for e in rows:
            print(f"#{e.id:<4} {e.spent_on}  ${e.amount:>9.2f}  {e.category:<12} {e.note}")

    elif args.command == "summary":
        totals = store.totals_by_category(args.month)
        grand = sum(totals.values())
        for cat, amt in totals.items():
            bar = "#" * int(20 * amt / grand) if grand else ""
            print(f"{cat:<12} ${amt:>9.2f}  {bar}")
        print(f"{'TOTAL':<12} ${grand:>9.2f}")

    elif args.command == "export":
        with args.file.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "date", "amount", "category", "note"])
            for e in store.list():
                w.writerow([e.id, e.spent_on, f"{e.amount:.2f}", e.category, e.note])
        print(f"Exported to {args.file}")

    elif args.command == "delete":
        if not store.delete(args.id):
            print(f"No expense with id {args.id}", file=sys.stderr)
            return 1
        print(f"Deleted expense #{args.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
