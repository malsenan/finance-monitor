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
- Predicts future net worths based on historical data
- Identifies and shows repeat transactions to help detect fraud or unnecessary spending
- Provides insights into cash flow and budgeting
- Generates reports on investment performance
- Alerts for upcoming bills and reminders for financial goals

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

## Todo
- Research openclaw