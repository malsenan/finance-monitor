# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Coding Guidelines

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

### 5. Ticket First

**Every coding task starts as a ticket in the README.**

The TODO list in `README.md` is the project's ticket tracker. Before changing any code:
- Add the task as a ticket in its priority position, in the format described at the top of the TODO list.
- Explain in detail why the task needs to be done, and why each of its subtasks needs to be done.
- Stop there. Start the code only after the user has reviewed the ticket and it has been pushed.

While working, mark each subtask (DONE) as it's finished.

## Project
**Some general notes:**
- **Everything under here is subject to change as the project evolves.**
- **If a better solution exists, design or otherwise, say so.**
- **If something doesn't make sense, say so.**

## Running

**Never run the code on the current .env, only read it. The unit tests (`pytest`) use synthetic fixtures only, and they're the only code you may run. If absolutely necessary, copy this code into a tmp folder and create your own sample data to run against and clean up these resources afterwards.**

- Python sources live in `src/`. Run from the repo root with `python src/main.py`; `config.py` reads `.env` from the repo root.
- Dependencies, including `pytest`, are in `requirements.txt`. Run the tests from the repo root with `pytest`; `pytest.ini` puts `src/` on the import path. Tests read fixtures from `tests/fixtures/` and must never import `config`, which reads the real `.env`. No linter config yet.
- `config.py` raises at import time if any required `.env` setting is missing, so every module that imports `config` needs a valid `.env`.
- Output goes to `$FINANCE_DATA_DIR/parsed_data/` (parsed CSVs + `stats.txt`). That directory must already exist. Right after `stats.txt` is written, `main.py` copies `parsed_data/` into a new `$FINANCE_DATA_DIR/old_parsed_data/YYYY-MM-DD_HH-MM-SS/` folder. Backups pile up until they're deleted by hand.
- Charts call `plt.show()` and block. They are toggled by the `plot_*` booleans at the top of `main.py`'s `__main__` block. `plot_line_savings_by_month` runs regardless of those flags.
- The date ranges passed to the `stats.txt` reporters (e.g. `log_account_stats_between(..., 2, 2026, 3, 2026)`) are hardcoded in `main.py` and need editing by hand.

## Data privacy

The input CSVs are real personal financial exports stored outside the repo (`FINANCE_DATA_DIR`). Every personal value (the credit account suffix, Fidelity account numbers, income, limits) lives in `.env`. Keep it that way: don't hardcode personal values, account numbers, or sample rows from real data in source, comments, or docstrings.

## Architecture

The pipeline is flat, and `main.py` is the only orchestrator: **parsers → merge/derive in main → exporters/reporters/charts**.

- `parsers.py` turns each bank's export format into lists of plain dicts (typed loosely by `models.py` `TypedDict`s):
  - Bank rows: `{date, account, description, amount, balance}`
  - Fidelity holding rows: `{date, account, symbol, description, quantity, price_per_share, ending_value, cost_basis}`, one per fund per day it changed
  - Fidelity summary rows: `{date, account, ending_mkt_value}`, one per account per day it changed
- `main.py` merges these with `heapq.merge`, then derives more series:
  - `fidelity_transactions`: holdings converted to bank-row shape. `amount` is the change in cost basis since that symbol's previous row, and `balance` is the sum of `ending_value` for that date and account.
  - `cost_bases`: the same shape, but `balance` is the cost basis.
  - `all_transactions`: all bank rows plus `fidelity_transactions`, with a `net_worth` field added.
- `reporters.py` functions return `List[str]`. `main.py` concatenates them and writes `stats.txt`, which is meant to be safe to paste into an AI model (no identifiers).
- `charts.py` holds one matplotlib function per chart type and consumes the same dict lists.
- `validator.validate_balance` checks that checking/savings running balances match the summed amounts. On a mismatch it prints `MAJOR ALERT` instead of raising.

### Conventions that span files

- **Dates are `"%m/%d/%Y"` strings**, not `datetime`s. They get parsed on demand everywhere they are sorted or compared.
- **Lists are newest-first.** Parsers reverse to this order, and `heapq.merge(..., reverse=True)` depends on it. Code that computes running values iterates `[::-1]` (oldest-first).
- **Net worth / multi-account balances** come from a `curr_balances` dict keyed by `account`: walk oldest-first, overwrite the latest balance per account, and sum. This pattern appears in `main.py` and `charts.py`. For Fidelity holding rows, `account` is `"<label> - <fund>"` (the label comes from `.env`), so each fund counts as its own "account".
- Credit balances aren't in the export. `aggregate_credit_files` computes them as a cumulative sum starting from 0.
- The `Net worth:` line at the top of `stats.txt` only covers checking + savings + credit. It excludes Fidelity.

### Parser fragility

The exports have no stable schema:

- **Checking/savings:** the parser relies on fixed row offsets: summary on rows 1–4, transaction header on row 6. Whether the account is `savings` or `checking` is inferred from the filename.
- **Fidelity (`parse_fidelity_transactions`):** reads `fidelityTransactions.csv` by column name. `docs/fidelity-transactions.md` is the spec: row meanings, rules, output and worked examples, which `tests/test_fidelity_parser.py` replays. Only the current export layout is supported, and the parser assumes valid input (no error handling). Account numbers map to labels through `FIDELITY_ACCOUNT_<LABEL>=<account number>` settings in `.env`.

If a parse breaks after a new download, suspect a change in the export layout before suspecting a logic bug.
