# finance-monitor

Parses locally exported statements from Bank of America and Fidelity — no bank logins, no APIs, no data leaving your machine. Aggregates transactions across all accounts into a single timeline, computes net worth at every point in time, and outputs both a human/AI-readable text report and a set of matplotlib charts.

## Data Sources

- **BofA Checking** — transaction history CSV
- **BofA Savings** — transaction history CSV
- **BofA Credit** — one or more transaction CSVs aggregated from a directory
- **Fidelity Individual / Roth IRA** — monthly statement CSVs aggregated from a directory (holdings: symbol, quantity, price, beginning value, ending value, cost basis)
- **Fidelity 401k** — transaction history CSV (via NetBenefits)

## How to Download Required Files

### BofA Checking & Savings Accounts
Current data is 9/20/2024 - 3/19/2026
1. Login to the [BofA website](https://www.bankofamerica.com/)
2. Click on the account (Banking or Savings) and make sure you are on the 'Activity' tab and under 'Currently viewing' it says "Transaction history"
4. Click on 'Download'
5. Set timeframe and download as Excel format
6. Copy/paste the new csv's *contents* to the bottom of the existing .csv transactions file in `/home/malsenan/Documents/finances/bofa/(credit or debit)`

### BofA Credit Account
Current data is 5/2025 - 2/2026
1. Login to the [BofA website](https://www.bankofamerica.com/)
2. Click on the account (Customized Cash Rewards) and make sure you are on the 'Activity' tab
3. Click on 'Download'
4. Set transaction period and download as Excel format
5. Copy/paste this new .csv file into `/home/malsenan/Documents/finances/bofa/credit`

### Fidelity Individual Account Statements
Current data is 4/30/2024 - 2/28/2026
1. Login to [Fidelity](https://www.fidelity.com/)
2. Under 'All accounts', click on the 'Documents' tab
3. Download the target month's statement by clicking the download button on the right and 'Download as CSV'
4. Copy/paste this new .csv file into `/home/malsenan/Documents/finances/fidelity`

### Fidelity 401k Statements
Current data is 1/2/2024 - 3/11/2026
1. Login to [NetBenefits](https://nb.fidelity.com/static/mybenefits/netbenefitslogin/#/login)
2. Click on the account (Advantest)
3. Under the 'Summary' tab click on 'TRANSACTION HISTORY'
4. Click on 'Transaction History'
5. Click on 'Download Transaction History'
6. Enter the date range and download as CSV
7. Copy/paste the new csv's *contents* to the top of the existing csv file `/home/malsenan/Documents/finances/fidelity/fidelityTransactions.csv`

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

## Roadmap

- [ ] Local AI financial health check — offline model flags overspending, low balances, retirement contribution gaps, high credit utilization
- [ ] Startup on login via systemd service

## Charts TODO

### Per Account
- [ ] Spending by category (pie/bar chart)
- [ ] Largest single transactions (horizontal bar chart)
- [ ] Daily spend rate (line chart)
- [ ] Cumulative spend over month (line chart)

### Cross-Account
- [ ] Side-by-side monthly spend per account (grouped bar chart)
- [ ] Monthly cash flow trend — net income/expense per month (line chart)

### Recurring / Aggregate Transactions
- [ ] Top N recurring transactions by count (horizontal bar chart)
- [ ] Recurring transaction frequency over time (Gantt-style scatter plot)
- [ ] Average amount per recurring transaction (bar chart)

### Trends & Insights
- [ ] Month-over-month spending change % (bar chart)
- [ ] Rolling 30-day average spend (line chart)
- [ ] Spending heatmap by day of week vs week of month
- [ ] Credit utilization over time (line chart)

### Fidelity
- [ ] Pie/bar chart of portfolio split by account type (Roth IRA vs Individual)
- [ ] Side-by-side bar chart of cost basis vs current market value
- [ ] Holdings concentration chart by symbol
- [ ] Contributions/withdrawals over time (`change_in_investment`)
- [ ] Dividend income over time (`dividends_period`) and cumulative (`dividends_ytd`)
- [ ] Period and YTD total return trends (`total_period`, `total_ytd`)
- [ ] Dividend yield relative to portfolio value

## Field Reference

### General Transactions (bank and fidelity)
- Objects: `credit_transactions`, `checking_transactions`, `savings_transactions`, `fidelity_statements`, `cost_bases`
| Field         | Description
|---------------|-------------
| `date`        | Date of transaction
| `account`     | Account tied to transaction
| `description` | Description of the transaction
| `amount`      | Transaction amount
| `balance`     | Running balance of the account


### Fidelity Holdings
- Objects: `fidelity_401k_holdings`, `fidelity_individual_holdings`
| Field         | Description
|---------------|-------------
| `date`        | Date of transaction
| `account`     | Account tied to transaction
| `symbol` | Stock symbol
| `description` | Description of the transaction
| `quantity`      | Transaction amount
| `balance`     | Running balance of the account



### Account Summary
| Field | Description |
|---|---|
| `beginning_mkt_value` | Total market value at the start of the period |
| `change_in_investment` | Net cash flow in/out during the period (deposits − withdrawals, excludes gains) |
| `ending_mkt_value` | Total market value at the end of the period |
| `dividends_period` | Dividends earned during this specific period |
| `dividends_ytd` | Dividends earned from Jan 1st through end of period (cumulative) |
| `total_period` | Total return for this period (gains + dividends) |
| `total_ytd` | Total return from Jan 1st through end of period (cumulative) |

### Holdings
| Field | Description |
|---|---|
| `quantity` | Number of shares owned |
| `price` | Price per share at end of period |
| `beginning_value` | Market value at start of period (`quantity × price` at open) |
| `ending_value` | Market value at end of period (`quantity × price` at close) |
| `cost_basis` | Total amount originally paid for shares — used to calculate gains/losses |

> **Note:** `cost_basis` is what you *paid* historically, while `beginning_value` is what it was *worth* at the start of the current period.
