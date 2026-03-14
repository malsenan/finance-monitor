import matplotlib.pyplot as plt
from datetime import datetime
from typing import List

from models import Transaction

def _annotate_points(ax, dates, values, indices):
    """Annotates selected data points on a matplotlib axis with value and date labels."""
    for i in indices:
        ax.annotate(
            f"${values[i]:,.0f}\n{dates[i].strftime('%m/%d/%y')}",
            xy=(dates[i + 2 if i + 2 < len(dates) else i], values[i]),
            xytext=(0, 8),
            textcoords='offset points',
            fontsize=8,
        )


def plot_transaction_data(transactions: List[Transaction], transaction_key: str, graph_title: str):
    """
    Plots a numeric field from a list of transactions over time as a line graph.

    Parameters:
    - transactions: List of transaction dicts, each containing a 'date' and the target key.
    - transaction_key: The field name to plot on the y-axis (e.g. 'balance', 'net_worth').
    - graph_title: Title displayed on the chart.
    """
    # Convert date strings to datetime objects for proper x-axis spacing
    dates = [datetime.strptime(t["date"], "%m/%d/%Y") for t in transactions]
    balances = [t[transaction_key] for t in transactions]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the line
    ax.plot(dates, balances)

    # Put annotate 7 points on the graph
    _annotate_points(ax, dates, balances, [i for i in range(len(dates)) if i % (len(dates) // 7) == 0 or i == len(dates) - 1])

    # Labels and title
    ax.set_title(graph_title.capitalize())
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance ($)")

    # Rotate x-axis date labels so they don't overlap
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()
    
def plot_monthly_spending(transactions: List[Transaction], limit: float = None):
    """
    Plots total monthly spending as a bar chart, with an optional spending limit line.

    Only negative amounts (expenses) are included. Each bar is labeled with its dollar value.

    Parameters:
    - transactions: List of transaction dicts, each containing 'date' and 'amount'.
    - limit: Optional spending limit to display as a horizontal dashed red line.
    """
    from collections import defaultdict

    monthly = defaultdict(float)
    for t in transactions:
        if t["amount"] < 0:
            date = datetime.strptime(t["date"], "%m/%d/%Y")
            key = date.strftime("%Y-%m")
            monthly[key] += t["amount"]
    sorted_months = sorted(monthly.items())
    labels = [datetime.strptime(k, "%Y-%m").strftime("%b %Y") for k, _ in sorted_months]
    values = [abs(v) for _, v in sorted_months]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(labels, values)

    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${value:,.0f}",
                ha='center', va='bottom', fontsize=8)

    if limit is not None:
        ax.axhline(y=limit, color='red', linestyle='--', linewidth=1, label=f'Limit (${limit:,.0f})')
        ax.legend()

    ax.set_title("Monthly Spending")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount Spent ($)")
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()
