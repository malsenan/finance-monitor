# finance-monitor
Monitor all your finances in one place.
Making sure you max out your retirement plans and stay under your credit limit by 30%.

## How It Works

Drop in your statements and finance-monitor parses them locally — no bank logins, no APIs, no data leaving your machine.

- **Bank of America** — parses exported PDF statements
- **Fidelity** — parses exported CSV statements

Aggregates balances, spending, and transaction history across both.

## Display
- Outputs a human and AI readable `.txt` summary file — no sensitive information (no account numbers, no names)
- The file can be fed directly into an AI model to get financial advice and feedback
- Optional GUI dashboard with charts and summaries

## Features
- Shows current net worth
- Aggregate transactions by address/payee on a dashboard, sort by  (ex: Claude - $20.19 x13 since Feb. 2026, $50 x1 since Nov. 2025)
- Predicts future net worths based on historical data
- Identifies and shows repeat transactions to help detect fraud or unnecessary spending
- Provides insights into cash flow and budgeting
- Generates reports on investment performance
- Alerts for upcoming bills and reminders for financial goals
- Calculates and displays monthly average spending
- Shows the percentage of income spent on essentials (e.g., housing, food)
- Identifies high-interest debt and suggests strategies to pay it off faster
- Provides a breakdown of spending by category (e.g., groceries, entertainment, transportation)
- Generates alerts for potential tax deductions or credits
- Offers personalized financial advice based on user goals and risk tolerance
- The analyzer/AI can pick up on repeat or suspicious purchases

## Startup
Runs automatically on login via a systemd service or login hook so your financial snapshot is ready when you sit down.

## AI Health Check (Planned)
- Offline, local AI model analyzes your parsed data
- Flags overspending, low balances, retirement contribution gaps, high credit utilization, and other trends
- Nothing leaves your machine

## Roadmap
- [ ] BofA PDF statement parser
- [ ] Fidelity CSV statement parser
- [ ] Balance & spending aggregation
- [ ] AI-readable `.txt` summary output (no sensitive info)
- [ ] GUI dashboard
- [ ] Startup on login
- [ ] Local AI financial health analysis
- [ ] Pick up on repeat or suspicious purchases

# 📊 Finance Charts TODO

## Per Account
- [ ] Running balance over time (line chart)
- [ ] Monthly spending vs income (bar chart)
- [ ] Spending by category (pie chart)
- [ ] Spending by category (bar chart)
- [ ] Largest single transactions (horizontal bar chart)
- [ ] Daily spend rate (line chart)
- [ ] Cumulative spend over month (line chart)

## Cross-Account
- [ ] Net worth over time (line chart)
- [ ] Side-by-side monthly spend per account (grouped bar chart)
- [ ] Account balance comparison over time (multi-line chart)
- [ ] Monthly cash flow trend — net income/expense per month (line chart)

## Recurring / Aggregate Transactions
- [ ] Top N recurring transactions by count (horizontal bar chart)
- [ ] Recurring transaction frequency over time (Gantt-style scatter plot)
- [ ] Average amount per recurring transaction (bar chart)

## Trends & Insights
- [ ] Month-over-month spending change % (bar chart)
- [ ] Rolling 30-day average spend (line chart)
- [ ] Spending heatmap by day of week vs week of month (heatmap)
- [ ] Savings rate over time — savings delta / income (line chart)
- [ ] Credit utilization over time (line chart)

## FIDELITY TODO

### Transaction / Holdings Data
- [ ] Plot `ending_value` over time per account and combined (portfolio growth)
- [ ] Calculate and display unrealized gains/losses (`ending_value - cost_basis`)
- [ ] Calculate return % per holding (`(ending_value - cost_basis) / cost_basis * 100`)
- [ ] Pie/bar chart of portfolio split by account type (Roth IRA vs Individual)
- [ ] Side-by-side bar chart of cost basis vs current market value
- [ ] Holdings concentration chart by symbol (if multiple symbols)

### Account Summary Data
- [ ] Plot `ending_mkt_value` over time per account and combined
- [ ] Track contributions/withdrawals over time via `change_in_investment`
- [ ] Plot dividend income over time (`dividends_period`) and cumulative (`dividends_ytd`)
- [ ] Trend `total_period` and `total_ytd` returns over time
- [ ] Side-by-side account comparison (Roth vs Individual growth)

### Combined Insights
- [ ] Cross-reference holdings cost basis with summary returns for actual return analysis
- [ ] Calculate dividend yield relative to portfolio value
- [ ] Separate gains from contributions using `change_in_investment`

=======================================================
 FIELD REFERENCE
=======================================================

 ACCOUNT SUMMARY
 -------------------------------------------------------
 beginning_mkt_value  Total market value at start of period
 change_in_investment Net cash flow in/out (deposits - withdrawals, no gains)
 ending_mkt_value     Total market value at end of period
 dividends_period     Dividends earned this period
 dividends_ytd        Dividends earned YTD (cumulative)
 total_period         Total return this period (gains + dividends)
 total_ytd            Total return YTD (cumulative)

 HOLDINGS
 -------------------------------------------------------
 quantity             Number of shares owned
 price                Price per share at end of period
 beginning_value      Market value at start of period (quantity x price at open)
 ending_value         Market value at end of period (quantity x price at close)
 cost_basis           Total amount paid for shares (used to calculate gains/losses)

=======================================================
 NOTE: cost_basis vs beginning_value
   cost_basis      = what you originally paid (historical)
   beginning_value = what it was worth at start of this period (recent)
=======================================================