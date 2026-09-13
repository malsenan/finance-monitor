# finance-monitor

Parses locally exported statements from Bank of America and Fidelity — no bank logins, no APIs, no data leaving your machine. Aggregates transactions across all accounts into a single timeline, computes net worth at every point in time, and outputs both a human/AI-readable text report and a set of matplotlib charts.

## Quick start

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # run this if .env doesn't already exist, then fill in your values (see Setup)
python src/main.py
```

After the first time, you only need `source .venv/bin/activate` and `python src/main.py`.

## Setup

All machine-specific and personal values live in a `.env` file, which is gitignored.

```sh
cp .env.example .env
```

Then edit `.env` and fill in your own values — the data directory, the filename suffix
identifying your credit account's exports, your 401k plan's account-name prefix, your
annual income, and your monthly spending limits. Every setting is documented inline in
`.env.example`. Real environment variables override the file, so nothing personal needs
to be written to disk if you would rather export them in your shell.

Before the first run, create a `parsed_data` folder inside your `FINANCE_DATA_DIR`. The tool writes its output there and doesn't create the folder itself.

## Data Sources

- **BofA Checking** — transaction history CSV
- **BofA Savings** — transaction history CSV
- **BofA Credit** — one or more transaction CSVs aggregated from a directory
- **Fidelity Individual / Roth IRA** — monthly statement CSVs aggregated from a directory (holdings: symbol, quantity, price, beginning value, ending value, cost basis)
- **Fidelity 401k** — transaction history CSV (via NetBenefits)

# How to Update Financial Files

Note: Some of the strings in the headers don't render properly in markdown view due to the '$' character I think, so it's better to read this as plain text

### BofA Checking & Savings Accounts (needed for the monitor)
**Latest update to files: 9/12/2026**
1. Login to the [BofA website](https://www.bankofamerica.com/)
2. Click on the account (Banking or Savings) and make sure you are on the 'Activity' tab and under 'Currently viewing' it says "Transaction history"
4. Click on 'Download'
5. Set timeframe and download as Excel format
6. Copy/paste the new csv's *contents* to the **bottom** of the existing .csv transactions file in `$FINANCE_DATA_DIR/bofa/(debit or savings)`
- Headers: Date,Description,Amount,Running Bal.

### BofA Credit Account (needed for the monitor)
**Latest update to files: 9/12/2026**
1. Login to the [BofA website](https://www.bankofamerica.com/)
2. Click on the credit card account and make sure you are on the 'Activity' tab
3. Click on 'Download'
4. Set transaction period and download as Excel format
5. Copy/paste this new .csv file into `$FINANCE_DATA_DIR/bofa/credit`
- Headers: Posted Date,Reference Number,Payee,Address,Amount

### Fidelity Transactions (needed for the monitor)
1. Login to [Fidelity](https://www.fidelity.com/)
2) Go to portfolio (skip this step if page says `All Accounts`) 
3. Go to the `Activity & Orders` tab
4. Use the dropdown under the search bar that says "Past 30 days" and set the custom date range
5. Click on the download button and download as CSV
7. Copy/paste the new csv's *contents* to the **top** of the existing csv file `$FINANCE_DATA_DIR/fidelity/fidelityTransactions.csv`
- Headers: Run Date,Account,Account Number,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Settlement Date

### Extra files I found on Fidelity - trying to replace the old steps that no longer fetch csv formatted data and see what new data I can get and analyze instead

**Goal: To find out if any of these new sources of data (especially Accounts_History.csv) is an easier source to download and use for the monitor, i.e. it contains sufficient data to replace the "Fidelity 401k Statements" and the outdated "Fidelity Individual Account Statements". This decision should be based on what the code already supports and what kind of data analysis is requested. Ideally it would just follow old implementation.**

- **Portfolio_Positions_Sep-13-2026_overview.csv** - Snapshot of all positions of all accounts, i.e. shows my details about my holdings in every stock on every acccount
    - Download method: 1) Login to Fidelity, 2) (might not be needed, should say All Accounts) go to portfolio, 3) go to the positions tab, 4) make sure the dropdown is on `Overview`, 5) click on the three dots 6) click on download
    - Headers: Account number,Account name,Symbol,Description,Quantity,Last price,Last price change,Current value,Today's gain/loss dollar,Today's gain/loss percent,Total gain/loss dollar,Total gain/loss percent,Percent of account,Cost basis total,Average cost basis,Type

- **Portfolio_Positions_Sep-13-2026_myview.csv** - Even more detailed snapshot of all poisions on all accounts, using "My View" which I manually edited to enable every stat/column
    - Download method: 1) Login to Fidelity, 2) (might not be needed, should say All Accounts) go to portfolio, 3) go to the positions tab, 4) make sure the dropdown is on `My View`, 5) click on the three dots 6) click on download
    - Headers (many are unpopulated): Account number,Account name,Symbol,Description,Current value,% of account,Quantity,Cost basis total, Average cost basis,Average cost basis,Cost basis total,Account type,Loaned,Hard to borrow,Today's gain/loss $,Today's gain/loss %,Today's gain/loss $, Today's gain/loss %,Total gain/loss $,Total gain/loss %,Total gain/loss $, Total gain/loss %,CUSIP,Last price,Last Price, Change $,Change $,Change %,Change $, Change %,Volume,52-week high date,52-week low date,Bid,Bid size,Ask,Ask size,Opening price,Previous close,Previous close date,Analyst ratings,Analyst ratings date,News,10-day avg. volume,90-day avg. volume,Market cap,Earnings announcement date,P/E ratio,Shares outstanding,Short %,Shares short,Days to cover,Prior shares short,Prior days to cover,Currency,Ex-date,Amount per share,Pay date,Payment frequency,Dist. rate, Distribution rate as of,SEC yield, SEC yield as of,Est. annual income,YTD,1 year,3 year,5 year,10 year,Exp ratio (net),Exp ratio (gross),Morningstar overall rating,Morningstar category,Sector,Industry,Industry group,Sub industry,Security type,Security subtype,10-day volatility,30-day volatility,60-day volatility,90-day volatility,120-day volatility,250-day volatility

- **Accounts_History.csv** - I think it's a history of all my transactions on all accounts
    - Download method: 1) Login to Fidelity, 2) (skip this step if page says All Accounts) go to portfolio, 3) go to the `Activity & Orders` tab, 4) use the dropdown under the search bar that says "Past 30 days" and set the custom date range, 4) click on the download button and download as CSV
    - Headers: Run Date,Account,Account Number,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Settlement Date
    - Caution: This contains some weird data that might interfere (just ask the agent if this data is even usable)
        - Ex: Fees like consultant fee and bookkeeping fees
        - Ex: In the transactions, it looks like my individual contributions are transferred in as cash then used to buy stocks, which looks weird surace level
        - If I end up using this data, does it capture all the data I need? Is it missing anything?

- **History_for_Account_#####.csv** - A transaction history for a specific account of my choosing 
    - Download method: 1) Login to Fidelity, 2) (skip this step if page says All Accounts) go to portfolio, 3) choose a specific account on the left sidebar 4) go to the `Activity & Orders` tab, 5) use the dropdown under the search bar that says "Past 30 days" and set the custom date range, 6) click on the download button and download as CSV
    - Headers for individual accounts (brokerage and IRA): Run Date,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Cash Balance ($),Settlement Date
    - Headers for employer accounts (401k): Date,Investment,Transaction Type,Shares/Unit,Amount ($)
    - Should this be used over Accounts_History.csv? Should I generate this file separately for every account?

## Text Report (`stats.txt`)

Generated on every run. Safe to feed directly into an AI model — contains no account numbers or personal identifiers.

- **Net worth** — checking + savings + credit balances at the most recent date. Fidelity accounts are not included
- **Per-account cash flow summary** (checking, savings, credit) for a month range typed into `src/main.py` (edit those numbers by hand to change it):
  - Total income
  - Total expenses
  - Net cash flow
- **Last N transactions** across checking, savings, and credit — side-by-side date-sorted table showing description, amount, and running balance per account
- **All transactions since a given month** — same side-by-side format, from a start month typed into `src/main.py`
- **Top N recurring transactions per account** — grouped by (description, amount), sorted by frequency; shows count, earliest date, and latest date — useful for spotting subscriptions or suspicious charges
- **Return % per Fidelity holding** — one row per (symbol, account) using the most recent statement:
  - Unrealized return %: `(ending_value - cost_basis) / cost_basis × 100`
  - Current market value, cost basis, and gain/loss in dollars
  - As-of date

## Charts

Charts open in pop-up windows. Most are switched on by the `plot_balances`, `plot_income_vs_spending` and `plot_fidelity` flags at the top of `src/main.py`'s `__main__` block, which are all off by default. The monthly savings rate chart is the exception: it always runs.

**Balance & Net Worth**
- Net worth over time (line chart) — rolling sum of all account balances
- Checking, savings, and credit balance over time (separate line charts)
- All account balances on one chart — checking, savings, credit, Fidelity, and net worth as labeled lines
- Fidelity market value vs. money invested over time — total portfolio value against total cost basis, showing actual gains vs. contributions

**Cash Flow**
- Monthly income vs. spending — bar chart per account (all transactions, checking, savings, credit)
- Monthly savings rate (always shown) — each month's change in savings + Fidelity balances (including market gains), divided by `ANNUAL_INCOME` from `.env` (line chart)

**Fidelity / Investments**
- Total Fidelity portfolio value over time (all accounts combined)
- Fidelity portfolio value per account over time (Roth IRA vs. individual vs. 401k as separate lines)
- Per-symbol holdings over time — one line per ticker, plotted separately for individual account, 401k, and combined

## CSV Exports

Saves parsed versions of every data source to `$FINANCE_DATA_DIR/parsed_data/`, which must already exist:
- Credit, checking, savings transactions
- All transactions combined
- Bank account summaries
- Fidelity holdings, 401k transactions, Fidelity statement summaries

## Validation & Testing

Every check that confirms the tool's numbers, current and planned. Add new suites and harnesses here.

- **Balance validation** (runs every time) — `validate_balance` in `src/validator.py` starts from the oldest checking and savings balance, adds each transaction's amount, and checks the result against each row's running balance. On a mismatch it prints `MAJOR ALERT` instead of stopping.
- **Unit tests** (planned) — run against synthetic fixtures only, never real data. See the "Test harness" ticket.
- **Fidelity parser tests** (planned) — replay the made-up rows in `docs/fidelity-transactions.md` and expect the numbers in its worked examples. See the "Rewrite Fidelity parsing" ticket.
- **Fidelity balances vs. real balances** (manual, planned) — after everything's been implemented, my ultimate validation test for Fidelity will be seeing the calculated net balances match the actual net balances when I run the tool on my actual data.

## Plan

Direction, decided 2026-09-12:
- **Final product:** undecided, but leaning towards a local, interactive dashboard for viewing my own finances. No AI analysis of financial data. Need help deciding on a final product
- **AI agents are developers only.** They work against synthetic test data and never run the tool on real exports (see `CLAUDE.md`).
- **Goals the project tracks:** retirement contributions vs. annual limits, credit utilization under 30%, spending by category, a net worth forecast, other stats that I need help brainstorming later

## TODO

Tickets are in priority order: work top to bottom, and insert new tickets wherever they belong. Mark each subtask (TODO) or (DONE). Every new ticket explains why the task is needed, and each of its subtasks says why that step is needed.

### Cleanup
Done when a fresh clone needs only `pip install -r requirements.txt` and a filled-in `.env`, and the README matches the code.
- (DONE) Delete the stale aider files (`.aider.chat.history.md`, `.aider.input.history`, `.aider.tags.cache.v4/`)
- (DONE) `.gitignore`: drop `.aider*`, narrow `Statement*` and `finances` so test fixtures aren't ignored, and stop ignoring `.vscode/launch.json`
- (DONE) Commit `CLAUDE.md`
- (DONE) Add `requirements.txt` (`matplotlib`, `numpy`)
- (DONE) Move the Python sources into `src/`
- (DONE) Point `.vscode/launch.json` at `src/main.py`
- (DONE) README: checking/savings file paths in the download steps
- (DONE) README: net worth scope, hardcoded report dates, chart flags, the savings rate chart, and the output directory needing to exist

### Decide Fidelity input data shapes
Certain Fidelity statements can no longer be downloaded as CSV. Done when every Fidelity number the monitor uses comes from a file that can still be downloaded, and the download steps are updated.
- (DONE) Provide masked samples of the transaction history. They're documented with made-up values in `docs/fidelity-transactions.md`
- (DONE) Confirm the transaction history includes the 401k and goes back far enough. It covers every account, and `fidelityTransactions.csv` goes back to each account's first deposit
- (DONE) Decide the sources: `fidelityTransactions.csv` only, rebuilt once from fresh `Accounts_History.csv` downloads (see the rewrite ticket below), with new downloads pasted at the top. `Portfolio_Positions` isn't needed for now (moved to the backlog), so the positions-file and gap-months subtasks were dropped
- (TODO) Replace the dead Fidelity steps under "How to Update Financial Files"

### Rewrite Fidelity parsing for `fidelityTransactions.csv`
**Why:** The Roth IRA and individual account are parsed from statement CSVs, which can't be downloaded anymore. `fidelityTransactions.csv` holds every Fidelity account's full history, but in an older export layout, and `parse_fidelity_401k` can't read current downloads correctly:
- it reads share counts from `Price ($)`, where the old export put them, but current downloads put them under `Quantity`
- it ignores every row except `Contributions`
- it finds plans by a single account-name prefix that can't match two employers

Row meanings and calculation rules are in `docs/fidelity-transactions.md`.

Done when `fidelityTransactions.csv` is rebuilt in the current layout, both parsers read it, their tests pass, the statement parser is gone, and the Fidelity balance check under "Validation & Testing" passes.

Not changing: `models.py`, `charts.py`, `reporters.py`, `exporters.py`, `validator.py`, and everything in `main.py` after the parser calls.

- (DONE) Rebuild `fidelityTransactions.csv` from fresh `Accounts_History.csv` downloads (three one-year windows), and keep the old file as a backup under a different name (you)
  - Why: the old file uses an older, broken layout. On 401k rows the share count sits under `Price ($)` with `Quantity` blank, and each row has 15 fields against a 14-column header. Pasting new downloads on top would mix two layouts in one file, and the dates can't tell them apart: a 01/02/2024 row comes out differently depending on when it was downloaded. After a one-time rebuild, the parser only has to understand the current layout.
  - How: put the rows newest first under a single header, with no disclaimer lines and no dates repeated where the windows meet.
- (DONE) Check that the rebuilt file reaches each account's first deposit, by comparing its oldest row per account with the old file's (you)
  - Why: every running total starts from each account's oldest row. If the download can't reach that far back, the older rows would have to be converted from the old file instead, which first needs samples of old brokerage rows to see how they're laid out.
- (TODO) Send one masked row for each Action that isn't in `docs/fidelity-transactions.md`, taken from the rebuilt file (you)
  - Why: the parsers work out what a row does from the signs of `Quantity` and `Amount ($)`, not from its Action text. An Action that breaks that pattern would be counted wrong without any error.
- (TODO) Pick a test runner, moved here from "Test harness" (proposed: `pytest`)
  - Why: tests on made-up rows are the only way to check the parsers without real data. `pytest` needs one `pip install` and uses plain `assert`s.
- (DONE) Decide whether to print a warning when `fidelityTransactions.csv` has an account number that isn't in `.env`, and add it if so
  - Why: those rows get skipped, so a new account you forget to add would silently drop out of net worth.
  - Answer: if errors were to ever occur, I want loud and verbose failures telling the user where the failure was and why
- (TODO) `src/config.py`: remove `RETIREMENT_ACCOUNT_PREFIX`
  - Why: one account-name prefix can't match both employers' plans.
- (TODO) `src/config.py`: read the account map from `.env` keys starting with `FIDELITY_401K_` or `FIDELITY_BROKERAGE_` (e.g. `FIDELITY_401K_EMPLOYER_1=<account number>`)
  - Why a prefix: a new account or employer only needs a new `.env` line, not a code change.
  - Why two prefixes: 401k rows and brokerage rows use `Amount ($)` with opposite signs, so the parser has to know which format each account uses.
  - Why labels: outputs show the label (`EMPLOYER_1`) instead of Fidelity's account name, so `stats.txt` stops printing the employer's plan name (`src/reporters.py:239`).
- (TODO) `.env.example`: replace `RETIREMENT_ACCOUNT_PREFIX` with example account map lines
  - Why: `.env.example` documents every setting a fresh clone needs.
- (TODO) Your `.env`: add your real account numbers and remove `RETIREMENT_ACCOUNT_PREFIX` (you)
  - Why: the new config reads accounts from `.env`, and real account numbers stay out of the repo.
- (TODO) `parse_fidelity_401k`: select rows by account number from the 401k map
  - Why: it currently matches an account-name prefix (`src/parsers.py:150`).
- (TODO) `parse_fidelity_401k`: read shares from `Quantity`, without `safe_float`
  - Why: it reads shares from `Price ($)` (`src/parsers.py:153`), which is blank on 401k rows in current downloads, and then divides by it (`src/parsers.py:154`). `safe_float` rounds to 2 decimals, which turns a `-0.004` share fee into 0.
- (TODO) `parse_fidelity_401k`: apply every row that moves shares, and take prices only from `Contributions` and `Withdrawals`
  - Why: only `Contributions` count today (`src/parsers.py:150`), so fees never reduce shares and a rolled-over plan would keep counting on top of the new one. Fee rows are too rounded to give a reliable price.
- (TODO) `parse_fidelity_401k`: track each fund per plan
  - Why: funds are tracked by name alone (`src/parsers.py:151`), so the same fund held in two plans would merge.
- (TODO) Add `parse_fidelity_brokerage(file_path, accounts)`: cash plus funds per account, returning the same two lists the statement parser returns
  - Why: it replaces the statement CSVs for the Roth IRA and individual account. Matching the return shape keeps the rest of `main.py` unchanged.
- (TODO) Both parsers: name holdings rows `<label> - <fund>`, and write one summary row per account
  - Why: `src/main.py:96` adds up every holding with the same date and account, so per-fund names keep that sum correct without writing every fund on every date. Per-account summaries make the per-account chart show accounts instead of funds.
- (TODO) Delete `parse_fidelity_statement` and `aggregate_fidelity_individual_statements`, plus any imports only they use
  - Why: their input can't be downloaded anymore.
- (TODO) Tests for both parsers, using the rows and worked examples in `docs/fidelity-transactions.md`
  - Why: the worked examples are hand-checked expected values, so tests catch mistakes without real data.
- (TODO) `src/main.py`: switch the import (line 8) and the two parser calls (lines 41 and 44) to the new parsers, both reading `fidelityTransactions.csv`
  - Why: every later step (merges, derived series, exports, report, charts) receives the same variables and row shapes, so nothing else in `main.py` changes.
- (TODO) Run `python src/main.py` on your real data and compare the Fidelity balances with Fidelity's website (you)
  - Why: it's the final check under "Validation & Testing", and Claude never runs the tool on real data.
- (TODO) `CLAUDE.md`: update "Parser fragility" and "Data privacy"
  - Why: they describe the statement layout, the `Price ($)` column and the employer prefix, all of which go away.
- (TODO) README: update "Setup", "Data Sources", the return % line under "Text Report", and "CSV Exports"
  - Why: they still describe statement CSVs and the account-name prefix.
- (TODO) `docs/fidelity-transactions.md`: describe the old layout and say that only the current layout is supported
  - Why: the doc currently implies any file with this header works, and old-layout rows from a backup would be read with 0 shares and no error.

### Test harness
Done when the test suite passes using fixtures alone.
- (TODO) Provide one masked sample of each remaining export type (checking, savings, credit), kept outside the repo
- (TODO) Build fully synthetic fixtures from all the samples under `tests/fixtures/`
- (TODO) Unit tests for parsers, reporters, validator, and exporters. None of these need a `.env`
- (TODO) Only then investigate suspected bugs, each starting from a failing test

### Final product
Done when the chosen product runs locally on real data.
- (TODO) Decide the final product (leaning towards a local, interactive dashboard)
- (TODO) Choose a stack that keeps data local (e.g. Streamlit, or a static HTML page generated by `main.py`)
- (TODO) Move the merge/derive logic out of `main.py`'s `__main__` block into importable functions, so the product and `stats.txt` share it
- (TODO) Decide what it shows: net worth, cash flow, spending by category, credit utilization, retirement contributions, holdings, data freshness
- (TODO) Decide whether `stats.txt` and the matplotlib windows stay once the product covers them

### Features
- (TODO) Spending categories, using keyword rules kept in a gitignored local file
- (TODO) Retirement contributions vs. annual limits (401k, Roth IRA)
- (TODO) Credit utilization vs. the 30% target (needs a credit limit setting)
- (TODO) Net worth forecast
- (TODO) Brainstorm other stats worth tracking

### Nice to have
- (TODO) Flag recurring charges that changed price, and newly appearing subscriptions
- (TODO) Data freshness: latest record per source, flagging a missing download
- (TODO) Emergency runway: months of spending covered by cash
- (TODO) Hide-amounts toggle for screen sharing

### Chart backlog
Trimmed from the old Charts TODO list.
- (TODO) Spending by category
- (TODO) Credit utilization over time
- (TODO) Monthly net cash flow trend
- (TODO) Cost basis vs. market value
- (TODO) Dividend income over time

### Backlog: Portfolio_Positions snapshots
**Why:** `fidelityTransactions.csv` only prices a fund when a row trades it, so a fund's value can go stale between trades (see "Known limits" in `docs/fidelity-transactions.md`). A `Portfolio_Positions` download has Fidelity's own current price, value and cost basis for every holding, but only as of the day it was downloaded.

Done when the tool can use a positions snapshot as the latest value of each holding.

- (TODO) Decide whether stale values matter enough to add a download step
  - Why: the extra download is only worth it if you hold a fund you don't buy regularly, or want an exact current value.
- (TODO) Provide a masked sample of the overview file
  - Why: its layout hasn't been checked against real rows. Use the overview file rather than My View, because My View repeats column names such as `Cost basis total`, and `csv.DictReader` keeps only the last column with a given name.
- (TODO) Parse each snapshot into holdings rows
  - Why: `Current value` and `Cost basis total` map straight onto `ending_value` and `cost_basis`, so snapshots fit the row shape the rest of the tool already uses.

Dropped: the offline local-AI health check, startup on login, and the rest of the old Charts TODO list.

## Field Reference

### General Transactions (bank and fidelity)
- Objects: `credit_transactions`, `checking_transactions`, `savings_transactions`, `fidelity_transactions`, `cost_bases`, `all_transactions`
| Field         | Description
|---------------|-------------
| `date`        | Date of transaction
| `account`     | Account tied to transaction
| `description` | Description of the transaction
| `amount`      | Transaction amount
| `balance`     | Running balance of the account

### Fidelity Holdings
- Objects: `fidelity_401k_holdings`, `fidelity_individual_holdings`, `all_fidelity_holdings`
| Field         | Description
|---------------|-------------
| `date`            | Date of transaction
| `account`         | Account tied to transaction
| `symbol`          | Stock symbol
| `description`     | Description of the transaction
| `quantity`        | Number of shares owned
| `price_per_share` | Current price per share at time of transaction
| `beginning_value` | Value of all shares at start of period
| `ending_value`    | Value of all shares at end of period
| `cost_basis`      | Total cash paid for all shares