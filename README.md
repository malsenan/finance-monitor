# finance-monitor

Parses locally exported statements from Bank of America and Fidelity — no bank logins, no APIs, no data leaving your machine. Aggregates transactions across all accounts into a single timeline, computes net worth at every point in time, and outputs both a human/AI-readable text report and a set of matplotlib charts.

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

Requires `matplotlib` and `numpy`.

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

### Fidelity Individual Account Statements (needed for the monitor)
**OLD STEPS - THE STATEMENTS ARE NO LONGER DOWNLOADABLE AS CSV - NEED TO USE NEW DATA FORM OR FIND A NEW WAY TO UPDATE THIS DATA**
1. Login to [Fidelity](https://www.fidelity.com/)
2. Under 'All accounts', click on the 'Documents' tab
3. Download the target month's statement by clicking the download button on the right and 'Download as CSV'
4. Copy/paste this new .csv file into `$FINANCE_DATA_DIR/fidelity`
- Headers: Account Type,Account,Beginning mkt Value,Change in Investment,Ending mkt Value,Short Balance,Ending Net Value,Dividends This Period,Dividends Year to Date,Interest This Year,Interest Year to Date,Total This Period,Total Year to Date

### Fidelity 401k Statements (needed for the monitor)
**SKIPPED UNTIL SOLUTION FOUND TO GATHER DATA FOR INDIVIDUAL ACCOUNTS TOO**
1. Login to [NetBenefits](https://nb.fidelity.com/static/mybenefits/netbenefitslogin/#/login)
2. Click on the account (your employer's plan)
3. Under the 'Summary' tab click on 'TRANSACTION HISTORY'
4. Click on 'Transaction History'
5. Click on 'Download Transaction History'
6. Enter the date range and download as CSV
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

- **Net worth** — sum of all account balances at the most recent date
- **Per-account cash flow summary** (checking, savings, credit) for a configurable date range:
  - Total income
  - Total expenses
  - Net cash flow
- **Last N transactions** across checking, savings, and credit — side-by-side date-sorted table showing description, amount, and running balance per account
- **All transactions since a given month** — same side-by-side format, full history from that date forward
- **Top N recurring transactions per account** — grouped by (description, amount), sorted by frequency; shows count, earliest date, and latest date — useful for spotting subscriptions or suspicious charges
- **Return % per Fidelity holding** — one row per (symbol, account) using the most recent statement:
  - Unrealized return %: `(ending_value - cost_basis) / cost_basis × 100`
  - Current market value, cost basis, and gain/loss in dollars
  - As-of date

## Charts

All charts are toggled via flags at the top of `main.py`.

**Balance & Net Worth**
- Net worth over time (line chart) — rolling sum of all account balances
- Checking, savings, and credit balance over time (separate line charts)
- All account balances on one chart — checking, savings, credit, Fidelity, and net worth as labeled lines
- Fidelity market value vs. money invested over time — total portfolio value against total cost basis, showing actual gains vs. contributions

**Cash Flow**
- Monthly income vs. spending — bar chart per account (all transactions, checking, savings, credit)
- Savings rate over time — net savings as a percentage of income, month over month (line chart)

**Fidelity / Investments**
- Total Fidelity portfolio value over time (all accounts combined)
- Fidelity portfolio value per account over time (Roth IRA vs. individual vs. 401k as separate lines)
- Per-symbol holdings over time — one line per ticker, plotted separately for individual account, 401k, and combined

## Validation & CSV Exports

- **Balance validation** — verifies that running balances in checking and savings transaction files are internally consistent
- **CSV exports** — saves parsed versions of every data source to a configurable output directory:
  - Credit, checking, savings transactions
  - All transactions combined
  - Bank account summaries
  - Fidelity holdings, 401k transactions, Fidelity statement summaries

## Plan

Direction, decided 2026-09-12:
- **Final product:** undecided, but leaning towards a local, interactive dashboard for viewing my own finances. No AI analysis of financial data. Need help deciding on a final product
- **AI agents are developers only.** They work against synthetic test data and never run the tool on real exports (see `CLAUDE.md`).
- **Goals the project tracks:** retirement contributions vs. annual limits, credit utilization under 30%, spending by category, a net worth forecast, other stats that I need help brainstorming later

## TODO

Tickets are in priority order: work top to bottom, and insert new tickets wherever they belong. Mark each subtask (TODO) or (DONE).

### Cleanup
Done when a fresh clone needs only `pip install -r requirements.txt` and a filled-in `.env`, and the README matches the code.
- (TODO) Delete the stale aider files (`.aider.chat.history.md`, `.aider.input.history`, `.aider.tags.cache.v4/`)
- (TODO) `.gitignore`: drop `.aider*`, narrow `Statement*` and `finances` so test fixtures aren't ignored, and stop ignoring `.vscode/launch.json`
- (TODO) Commit `CLAUDE.md`
- (TODO) Add `requirements.txt` (`matplotlib`, `numpy`)
- (DONE) README: checking/savings file paths in the download steps
- (TODO) README: net worth scope, hardcoded report dates, chart flags, the savings rate chart, and the output directory needing to exist

### Decide Fidelity input data shapes
Fidelity statements can no longer be downloaded as CSV. Done when every Fidelity number the monitor uses comes from a file that can still be downloaded, and the download steps are updated.
- (TODO) Provide masked samples of `Accounts_History.csv` and the `Portfolio_Positions` overview file (header row, a few rows from each account type including the 401k, and any lines after the data), kept outside the repo
- (TODO) Confirm `Accounts_History.csv` includes the 401k, and find how far back its date range goes
- (TODO) Confirm the positions file includes the 401k
- (TODO) Decide the sources. Proposed: `Accounts_History.csv` for contributions, dividends, fees and trades, plus a monthly `Portfolio_Positions` overview snapshot for market value and cost basis
- (TODO) Decide how to handle the months between the last statement CSV and the first positions snapshot
- (TODO) Replace the dead Fidelity steps under "How to Update Financial Files"

### Test harness
Done when the test suite passes using fixtures alone.
- (TODO) Provide one masked sample of each remaining export type (checking, savings, credit), kept outside the repo
- (TODO) Build fully synthetic fixtures from all the samples under `tests/fixtures/`
- (TODO) Pick a test runner (`pytest` or the standard library's `unittest`)
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