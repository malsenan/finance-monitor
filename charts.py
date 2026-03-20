import matplotlib.pyplot as plt
from datetime import datetime
from typing import List

from models import BankTransaction, FidelityTransaction

def _annotate_points(ax, dates, values, indices):
    """
    Annotates selected data points on a matplotlib axis with a dollar value and date label.

    The label is placed slightly above the data point. The anchor x-position is shifted
    2 points to the right (when available) to avoid overlap with the line itself.

    Parameters:
    - ax: The matplotlib Axes object to annotate.
    - dates: List of datetime objects (x-axis values).
    - values: List of numeric values (y-axis values).
    - indices: List of integer indices into dates/values that should be annotated.
    """
    for i in indices:
        ax.annotate(
            f"${values[i]:,.0f}\n{dates[i].strftime('%m/%d/%y')}",
            # Shift the anchor right by 2 data points so the label doesn't cover the dot
            xy=(dates[i + 2 if i + 2 < len(dates) else i], values[i]),
            xytext=(0, 8),
            textcoords='offset points',
            fontsize=8,
        )


def plot_line_monthly_balance(series: list, graph_title: str):
    """
    Plots one or more transaction series over time as a line graph.

    Parameters:
    - series: Either a single list of transaction dicts, or a list of
              (transactions, label) tuples to plot multiple labeled lines.
    - graph_title: Title displayed on the chart.
    """
    # Normalize: if passed a plain list of dicts, wrap it as a single unlabeled series
    if series and not isinstance(series[0], tuple):
        series = [(series, None)]

    fig, ax = plt.subplots(figsize=(12, 6))

    for transactions, label in series:
        dates = []
        balances = []
        curr_balances = {}
        curr_date = None
        for t in transactions[::-1]:
            if curr_date is not None and t['date'] != curr_date:
                balances.append(round(sum(curr_balances.values()), 2))
                dates.append(datetime.strptime(curr_date, "%m/%d/%Y"))
            curr_date = t['date']
            curr_balances[t['account']] = t['balance']
        balances.append(round(sum(curr_balances.values()), 2))
        dates.append(datetime.strptime(curr_date, "%m/%d/%Y"))

        ax.plot(dates, balances, label=label)
        _annotate_points(ax, dates, balances, [i for i in range(len(dates)) if (i % (len(dates) // 7) == 0 and i < len(dates) * 0.95) or i == len(dates) - 1])

    if any(label for _, label in series):
        ax.legend()

    ax.set_title(graph_title.capitalize())
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance ($)")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()

def plot_bar_monthly_income_vs_spending(transactions: List[BankTransaction], graph_title: str, limit: float = None):
    """
    Plots total monthly income and spending as grouped bars per month.

    Positive amounts are income, negative amounts are expenses. Each bar is labeled
    with its dollar value. An optional spending limit line can be shown.

    Parameters:
    - transactions: List of transaction dicts, each containing 'date' and 'amount'.
    - limit: Optional spending limit to display as a horizontal dashed red line.
    """
    import numpy as np
    from collections import defaultdict

    monthly_income = defaultdict(float)
    monthly_spending = defaultdict(float)
    for t in transactions:
        date = datetime.strptime(t["date"], "%m/%d/%Y")
        key = date.strftime("%Y-%m")
        if t["amount"] > 0:
            monthly_income[key] += t["amount"]
        else:
            monthly_spending[key] += abs(t["amount"])

    all_months = sorted(set(monthly_income) | set(monthly_spending))
    labels = [datetime.strptime(k, "%Y-%m").strftime("%b %Y") for k in all_months]
    income_vals = [monthly_income[k] for k in all_months]
    spending_vals = [monthly_spending[k] for k in all_months]

    x = np.arange(len(labels))
    width = 0.4

    fig, ax = plt.subplots(figsize=(12, 6))
    income_bars = ax.bar(x - width / 2, income_vals, width, label='Income', color='steelblue')
    spending_bars = ax.bar(x + width / 2, spending_vals, width, label='Spending', color='tomato')

    for bar, value in zip(income_bars, income_vals):
        if value > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${value:,.0f}",
                    ha='center', va='bottom', fontsize=7)
    for bar, value in zip(spending_bars, spending_vals):
        if value > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${value:,.0f}",
                    ha='center', va='bottom', fontsize=7)

    if limit is not None:
        ax.axhline(y=limit, color='red', linestyle='--', linewidth=1, label=f'Limit (${limit:,.0f})')

    ax.set_title(graph_title)
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount ($)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plt.show()

def plot_line_fidelity_portfolio(transactions: List[FidelityTransaction], graph_title: str):
    """
    Plots a numeric field from a list of transactions over time as a line graph.

    Annotates ~7 evenly-spaced points (plus the last point) with their value and date.

    Parameters:
    - transactions: List of transaction dicts, each containing a 'date' and the target key.
    - transaction_key: The field name to plot on the y-axis (e.g. 'balance', 'net_worth').
    - graph_title: Title displayed on the chart.
    """

    # Convert date strings to datetime objects for proper x-axis spacing
    dates = [] # x-axis: time
    balances = [] #y-axis: money

    curr_balances = {} # Balance(s): {'checking': 0, 'savings': 0, 'credit': 0} or just {'checking': 0}
    curr_date = None # Sum transactions up day by day
    for t in transactions[::-1]: # Go oldest -> newest
        # If it's a new day, add the previous date and cumulative balances
        if (curr_date is not None and t['date'] != curr_date): 
            balances.append(round(sum(curr_balances.values()), 2))
            dates.append(datetime.strptime(curr_date, "%m/%d/%Y"))
        curr_date = t['date'] # Update date
        curr_balances[t['account']] = t['balance'] # Update balance
    
    # Append the final day's balance after the loop
    balances.append(round(sum(curr_balances.values()), 2))
    dates.append(datetime.strptime(curr_date, "%m/%d/%Y"))

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, balances)

    # Annotate ~7 evenly spaced points so the chart isn't cluttered but still readable
    # Don't put a point so close to the last one
    _annotate_points(ax, dates, balances, [i for i in range(len(dates)) if (i % (len(dates) // 16) == 0 and i < len(dates) * 0.95) or i == len(dates) - 1])

    ax.set_title(graph_title.capitalize())
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance ($)")

    # Rotate x-axis date labels so they don't overlap
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()


def plot_line_fidelity_portfolio(summaries: list):
    """
    Plots total investment portfolio value over time as a line chart.

    Sums ending_mkt_value across all accounts (ROTH IRA + Individual) for each statement
    date so the chart shows the combined portfolio value rather than per-account values.

    Parameters:
    - summaries: List of account summary dicts from parse_fidelity_file / aggregate_fidelity_files.
    """
     # Convert date strings to datetime objects for proper x-axis spacing
    dates = [] # x-axis: time
    balances = [] #y-axis: money

    curr_balances = {} # Balance(s): {'ROTH IRA': 0, 'Individual': 0, 'ADVANTEST': 0} or just {'checking': 0}
    curr_date = None # Sum transactions up day by day
    for t in summaries[::-1]: # Go oldest -> newest
        # If it's a new day, add the previous date and cumulative balances
        if (curr_date is not None and t['date'] != curr_date): 
            balances.append(round(sum(curr_balances.values()), 2))
            dates.append(datetime.strptime(curr_date, "%m/%d/%Y"))
        curr_date = t['date'] # Update date
        curr_balances[t['account']] = t['ending_mkt_value'] # Update balance
    
    # Append the final day's balance after the loop
    balances.append(round(sum(curr_balances.values()), 2))
    dates.append(datetime.strptime(curr_date, "%m/%d/%Y"))
    # from collections import defaultdict

    # # Sum both accounts' ending market value for each date to get total portfolio value
    # by_date = defaultdict(float)
    # for s in summaries:
    #     if s["ending_mkt_value"] is not None:
    #         by_date[s["date"]] += s["ending_mkt_value"]

    # sorted_items = sorted(by_date.items(), key=lambda x: datetime.strptime(x[0], "%m/%d/%Y"))
    # dates = [datetime.strptime(k, "%m/%d/%Y") for k, _ in sorted_items]
    # values = [v for _, v in sorted_items]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, balances)
    _annotate_points(ax, dates, balances, [i for i in range(len(dates)) if i % max(1, len(dates) // 7) == 0 or i == len(dates) - 1])
    ax.set_title("Total Portfolio Value Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value ($)")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


def plot_line_fidelity_per_account(summaries: list):
    """
    Plots investment account value over time with one line per account type.

    Each account type (e.g. ROTH IRA, Individual) gets its own series so you can
    compare their growth trajectories side-by-side.

    Parameters:
    - summaries: List of account summary dicts from parse_fidelity_file / aggregate_fidelity_files.
    """
    from collections import defaultdict

    # Group (date, value) pairs by account type
    by_account = defaultdict(list)
    for s in summaries:
        if s["ending_mkt_value"] is not None:
            by_account[s["account_type"]].append((s["date"], s["ending_mkt_value"]))

    fig, ax = plt.subplots(figsize=(12, 6))
    for account_type, pairs in sorted(by_account.items()):
        pairs.sort(key=lambda x: datetime.strptime(x[0], "%m/%d/%Y"))
        dates = [datetime.strptime(d, "%m/%d/%Y") for d, _ in pairs]
        values = [v for _, v in pairs]
        ax.plot(dates, values, label=account_type)
        _annotate_points(ax, dates, values, [i for i in range(len(dates)) if i % max(1, len(dates) // 7) == 0 or i == len(dates) - 1])

    ax.set_title("Portfolio Value Per Account Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value ($)")
    ax.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


def plot_line_fidelity_individual_holdings(holdings: list):
    """
    Plots market value and cost basis over time for each held security.

    Each symbol+account combination gets two series:
      - Solid line: current market value (ending_value)
      - Dashed line: cost basis (what was paid) — same color for easy comparison

    The gap between the two lines at any point is the unrealized gain or loss.

    Parameters:
    - holdings: List of holding dicts from parse_fidelity_file / aggregate_fidelity_files.
    """
    from collections import defaultdict

    # Group entries by "SYMBOL (Account Type)" label
    series = defaultdict(list)
    for h in holdings:
        key = f"{h['symbol']} ({h['account_type']})"
        series[key].append((h["date"], h["ending_value"], h["cost_basis"]))

    fig, ax = plt.subplots(figsize=(12, 6))
    for label, entries in sorted(series.items()):
        entries.sort(key=lambda x: datetime.strptime(x[0], "%m/%d/%Y"))
        dates = [datetime.strptime(e[0], "%m/%d/%Y") for e in entries]
        ending_values = [e[1] for e in entries if e[1] is not None]
        cost_bases = [e[2] for e in entries if e[2] is not None]
        if ending_values:
            # Plot market value as a solid line and capture its color
            line, = ax.plot(dates[:len(ending_values)], ending_values, label=f"{label} market value")
            if cost_bases:
                # Use the same color with a dashed style so the two lines are visually paired
                ax.plot(dates[:len(cost_bases)], cost_bases, linestyle="--", color=line.get_color(), label=f"{label} cost basis")

    ax.set_title("Holdings: Market Value vs Cost Basis Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value ($)")
    ax.legend(fontsize=7)
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()
