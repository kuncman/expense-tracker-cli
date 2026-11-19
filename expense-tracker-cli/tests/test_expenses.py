from datetime import date

import pytest

from expense_tracker.cli import main
from expense_tracker.db import ExpenseStore


@pytest.fixture
def store():
    return ExpenseStore(":memory:")


def test_add_and_list(store):
    store.add(12.5, "Food", "lunch", date(2026, 3, 1))
    rows = store.list()
    assert len(rows) == 1
    assert rows[0].amount == 12.5
    assert rows[0].category == "food"  # normalized to lowercase


def test_rejects_non_positive_amount(store):
    with pytest.raises(ValueError):
        store.add(0, "food")


def test_cents_avoid_float_error(store):
    store.add(0.1, "a", spent_on=date(2026, 1, 1))
    store.add(0.2, "a", spent_on=date(2026, 1, 1))
    assert store.totals_by_category()["a"] == 0.3


def test_filter_by_month(store):
    store.add(10, "food", spent_on=date(2026, 1, 15))
    store.add(20, "food", spent_on=date(2026, 2, 15))
    assert [e.amount for e in store.list(month="2026-02")] == [20]


def test_totals_sorted_desc(store):
    store.add(5, "coffee")
    store.add(50, "rent")
    assert list(store.totals_by_category()) == ["rent", "coffee"]


def test_delete(store):
    i = store.add(5, "coffee")
    assert store.delete(i) is True
    assert store.delete(i) is False


def test_cli_roundtrip(tmp_path, capsys):
    db = str(tmp_path / "t.db")
    assert main(["--db", db, "add", "9.99", "books", "-n", "novel"]) == 0
    assert main(["--db", db, "summary"]) == 0
    out = capsys.readouterr().out
    assert "books" in out and "9.99" in out
