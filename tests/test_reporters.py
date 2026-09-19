import os

from parsers import aggregate_credit_files, parse_checking_or_savings_file, parse_fidelity_transactions
from reporters import (
    log_account_stats_between,
    log_last_x_transactions,
    log_transactions_since,
    log_return_per_holding,
    log_top_aggregate_transactions,
)

# Fed from the made-up fixtures. Tests check values rather than exact lines, so layout changes don't break them
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
CHECKING = parse_checking_or_savings_file(os.path.join(FIXTURES, "checkingTransactions.csv"))
SAVINGS = parse_checking_or_savings_file(os.path.join(FIXTURES, "savingsTransactions.csv"))
CREDIT = aggregate_credit_files(os.path.join(FIXTURES, "credit"), "_0000.csv")
ACCOUNT_LABELS = {
    "11111": "EMPLOYER_A_401K",
    "22222": "EMPLOYER_B_401K",
    "X11111111": "INDIVIDUAL",
    "X22222222": "ROTH_IRA",
}


def table_rows(lines):
    # Table rows start with their date (e.g. 2026-03-20); the other lines are titles and headers
    return [line for line in lines if line[:4].isdigit()]


def test_log_account_stats_between():
    text = "\n".join(log_account_stats_between(CHECKING, 1, 2026, 2, 2026))

    # January and February only, so the March purchase is left out
    assert "Net Cash Flow: 999.25" in text
    assert "Total Expenses: -1000.75" in text
    assert "Total Income: 2000.0" in text


def test_log_last_x_transactions():
    rows = table_rows(log_last_x_transactions(CHECKING, SAVINGS, CREDIT, 3))

    # The 3 newest transactions of each account, newest first
    assert [row[:10] for row in rows] == [
        "2026-03-20", "2026-03-04", "2026-03-02", "2026-02-25", "2026-02-15", "2026-02-10", "2026-01-15",
    ]
    # All three accounts have a transaction on 02/10, so they share one row
    assert all(balance in rows[5] for balance in ["2500.0", "6000.81", "-140.0"])


def test_log_transactions_since():
    rows = table_rows(log_transactions_since(CHECKING, SAVINGS, CREDIT, 2, 2026))

    # Every transaction from February on, newest first; January is left out
    assert [row[:10] for row in rows] == [
        "2026-03-20", "2026-03-04", "2026-03-02", "2026-02-25", "2026-02-15", "2026-02-10", "2026-02-04",
    ]


def test_log_top_aggregate_transactions():
    text = "\n".join(log_top_aggregate_transactions(SAVINGS, 1))

    # The only repeated (description, amount) pair: 0.06 of interest in February and March
    assert "Interest Earned" in text and "0.06" in text and "Count: 2" in text
    assert "2026-02-04" in text and "2026-03-04" in text
    # Top 1 only, so the transfers aren't listed
    assert "transfer" not in text


def test_log_return_per_holding():
    _, holdings = parse_fidelity_transactions(os.path.join(FIXTURES, "fidelityTransactions.csv"), ACCOUNT_LABELS)
    text = "\n".join(log_return_per_holding(holdings))

    # FXAIX: 0.785 shares at 260 are worth 204.10 against 200.00 invested
    assert "+2.05%" in text and "+4.1" in text
    # FUND A was fully withdrawn, so its cost basis of 0 has no return to show
    assert "FUND A" not in text
