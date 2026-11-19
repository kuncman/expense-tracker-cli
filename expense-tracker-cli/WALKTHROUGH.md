# Walkthrough (interview prep, delete before pushing if you want)

**What it is:** a CLI that stores expenses in SQLite and prints summaries.

## How the code is split
- `db.py` holds all database logic in one class, `ExpenseStore`. The CLI never writes SQL itself. That separation means the storage layer can be tested on its own with an in-memory database (`":memory:"`), which is what the tests do.
- `cli.py` only parses arguments and prints. `main()` takes an optional `argv` list so tests can call it directly instead of spawning a subprocess.

## Design decisions you should be able to defend
1. **Integer cents instead of floats.** `0.1 + 0.2 != 0.3` in floating point. Storing `amount_cents INTEGER` avoids that; `test_cents_avoid_float_error` proves it.
2. **Parameterized SQL (`?` placeholders).** Never building queries with f-strings prevents SQL injection.
3. **Dates stored as ISO strings (`YYYY-MM-DD`).** They sort correctly as text, and `substr(spent_on, 1, 7)` gives the month cheaply.
4. **Categories lowercased on insert.** So "Food" and "food" are the same category.
5. **`CHECK (amount_cents > 0)`.** Validation is in the code *and* the schema, so bad data can't get in even if someone bypasses the class.
6. **Standard library only.** `argparse`, `sqlite3`, `csv`: easy to install, nothing to keep updated.

## Likely interview questions
- *How would you add budgets?* New `budgets(category, monthly_limit_cents)` table; after `add`, compare `totals_by_category(month)` against it.
- *What if the data grew huge?* Add an index on `spent_on` and `category`; SQLite handles millions of rows fine.
- *Why SQLite over a JSON file?* Atomic writes, querying/aggregation in SQL, no need to load everything into memory.

## Exercise to make it yours
Add the budgets feature above, or a `--year` filter to `summary`. Then you've written part of it yourself and can talk about it from experience.
