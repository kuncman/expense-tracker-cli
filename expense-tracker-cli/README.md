# expense-tracker-cli

A lightweight command-line tool for tracking personal spending. Data is stored locally in SQLite, so there is nothing to sign up for and nothing leaves your machine.

## Features

- Add, list, filter and delete expenses
- Monthly summaries per category with a simple text bar chart
- CSV export
- Money stored as integer cents (no floating-point rounding bugs)
- Zero third-party runtime dependencies

## Install

```bash
git clone https://github.com/kuncman/expense-tracker-cli.git
cd expense-tracker-cli
pip install -e ".[dev]"
```

## Usage

```bash
expense add 12.50 food -n "lunch with team"
expense add 1200 rent -d 2026-11-01
expense list --month 2026-11
expense summary --month 2026-11
expense export expenses.csv
expense delete 3
```

Example summary output:

```
rent         $  1200.00  ###################
food         $    12.50
TOTAL        $  1212.50
```

The database defaults to `~/.expenses.db`. Override it with `--db path/to/file.db` or the `EXPENSE_DB` environment variable.

## Running tests

```bash
pytest
```

## Project structure

```
expense_tracker/
  db.py     # SQLite storage layer (ExpenseStore)
  cli.py    # argparse command-line interface
tests/
  test_expenses.py
```

## Possible next steps

- Budgets per category with over-budget warnings
- Recurring expenses
- Import from bank CSV exports

## License

MIT
