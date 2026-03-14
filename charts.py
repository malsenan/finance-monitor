import matplotlib.pyplot as plt
from datetime import datetime
from typing import List

from models import Transaction


def _quarterly_indices(dates):
    from datetime import timedelta
    if not dates:
        return []
    indices = [0]
    last = dates[0]
    for i in range(1, len(dates)):
        if dates[i] - last >= timedelta(days=90):
            indices.append(i)
            last = dates[i]
    if indices[-1] != len(dates) - 1:
        indices.append(len(dates) - 1)
    return indices


def _annotate_points(ax, dates, values, indices):
    for i in indices:
        ax.annotate(
            f"${values[i]:,.0f}\n{dates[i].strftime('%m/%d/%y')}",
            xy=(dates[i + 2 if i + 2 < len(dates) else i], values[i]),
            xytext=(0, 8),
            textcoords='offset points',
            fontsize=8,
            # ha='center',
            # va='bottom',
        )


def plot_running_balance(transactions: List[Transaction], balance_key: str, account: str):
    # Convert date strings to datetime objects for proper x-axis spacing
    dates = [datetime.strptime(t["date"], "%m/%d/%Y") for t in transactions]
    balances = [t[balance_key] for t in transactions]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the line
    ax.plot(dates, balances)

    notable = _quarterly_indices(dates)
    _annotate_points(ax, dates, balances, dates[::10])

    # Labels and title
    ax.set_title(f"{account.capitalize()} Running Balance")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance ($)")

    # Rotate x-axis date labels so they don't overlap
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()
    

