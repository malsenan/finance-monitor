from datetime import datetime
from collections import defaultdict
from typing import List

from models import Transaction


def log_account_stats_between(
    transactions: List[Transaction],
    start_month: int,
    start_year: int,
    end_month: int,
    end_year: int,
) -> List[str]:

    # Get spending + income by month/year
    monthly_transactions = [
        t
        for t in transactions
        if datetime.strptime(t["date"], "%m/%d/%Y").month >= start_month
        and datetime.strptime(t["date"], "%m/%d/%Y").year >= start_year
        and datetime.strptime(t["date"], "%m/%d/%Y").month <= end_month
        and datetime.strptime(t["date"], "%m/%d/%Y").year <= end_year
    ]
    amounts = [t["amount"] for t in monthly_transactions]
    expenses = round(sum([a for a in amounts if a < 0]), 2)
    income = round(sum([a for a in amounts if a > 0]), 2)
    net_cost = round(sum(amounts), 2)

    lines = [
        "Account: " + transactions[0]["account"],
        "=" * 30,
        f"- Date Range: {start_month}/{start_year} - {end_month}/{end_year}",
        f"- Net Cash Flow: {round(net_cost, 2)}",
        f"- Total Expenses: {expenses}",
        f"- Total Income: {income}\n"
    ]

    return lines


def log_last_x_transactions(checking_transactions: List[Transaction],
                            savings_transactions: List[Transaction],
                            credit_transactions: List[Transaction],
                            num_transactions: int) -> List[str]:

    col_width = 70

    # Add headers first
    headers = ["date", "checking", "savings", "credit"]
    lines = []
    header = "".join(h.ljust(col_width - 5) for h in headers)
    lines.append(f"SHOWING LAST {num_transactions} TRANSACTIONS FOR EACH ACCOUNT\n")
    lines.append(header)
    lines.append("=" * len(header))

    checking_ptr = savings_ptr = credit_ptr = 0

    # While we haven't exceeded number of transactions for all ptrs, iterate all 3 transactions at the same time
    while (
        checking_ptr < num_transactions
        or savings_ptr < num_transactions
        or credit_ptr < num_transactions
    ):
        ch_transaction = checking_transactions[checking_ptr] if checking_ptr < num_transactions else None
        s_transaction = savings_transactions[savings_ptr] if savings_ptr < num_transactions else None
        cr_transaction = credit_transactions[credit_ptr] if credit_ptr < num_transactions else None

        # Get only latest transaction(s) from the candidates
        # Ex: if curr checking and savings transaction is 3/9/2026 and credit transaction is 3/6/2026, then only grab checking and savings to print
        candidates = [t for t in [ch_transaction, s_transaction, cr_transaction] if t is not None]
        latest_date = max(datetime.strptime(t['date'], '%m/%d/%Y') for t in candidates)
        latest = [t for t in candidates if datetime.strptime(t['date'], '%m/%d/%Y') == latest_date]

        row = str(latest_date.date()).ljust(26)
        if ch_transaction and ch_transaction in latest:
            row += f"{ch_transaction['description'][:32].ljust(32)} | {str(ch_transaction['amount']).rjust(10)} | {str(ch_transaction['balance']).rjust(12)}".ljust(col_width)
        else:
            row += 'None'.center(col_width)
        if s_transaction and s_transaction in latest:
            row += f"{s_transaction['description'][:32].ljust(32)} | {str(s_transaction['amount']).rjust(10)} | {str(s_transaction['balance']).rjust(12)}".ljust(col_width)
        else:
            row += 'None'.center(col_width)
        if cr_transaction and cr_transaction in latest:
            row += f"{cr_transaction['description'][:32].ljust(32)} | {str(cr_transaction['amount']).rjust(10)} | {str(cr_transaction['balance']).rjust(12)}".ljust(col_width)
        else:
            row += 'None'.center(col_width)

        lines.append(row)

        if ch_transaction in latest:
            checking_ptr += 1
        if s_transaction in latest:
            savings_ptr += 1
        if cr_transaction in latest:
            credit_ptr += 1

    return lines


def log_transactions_since(checking_transactions: List[Transaction],
                            savings_transactions: List[Transaction],
                            credit_transactions: List[Transaction],
                            month: int,
                            year: int) -> List[str]:
    col_width = 70

    # Add headers first
    headers = ["date", "checking", "savings", "credit"]
    lines = []
    header = "".join(h.ljust(col_width - 5) for h in headers)
    lines.append(f"\n\nSHOWING TRANSACTIONS SINCE {month}/{year}\n")
    lines.append(header)
    lines.append("=" * len(header))

    checking_ptr = savings_ptr = credit_ptr = 0

    # While we haven't exceeded number of transactions for all ptrs, iterate all 3 transactions at the same time
    while (
        checking_ptr < len(checking_transactions) or
        savings_ptr < len(savings_transactions) or
        credit_ptr < len(credit_transactions)
    ):
        ch_transaction = checking_transactions[checking_ptr] if checking_ptr < len(checking_transactions) else None
        s_transaction = savings_transactions[savings_ptr] if savings_ptr < len(savings_transactions) else None
        cr_transaction = credit_transactions[credit_ptr] if credit_ptr < len(credit_transactions) else None

        if (
            datetime.strptime(ch_transaction['date'], '%m/%d/%Y').year < year or (datetime.strptime(ch_transaction['date'], '%m/%d/%Y').year == year and datetime.strptime(ch_transaction['date'], '%m/%d/%Y').month < month)) and (
                datetime.strptime(ch_transaction['date'], '%m/%d/%Y').year < year or (datetime.strptime(ch_transaction['date'], '%m/%d/%Y').year == year and datetime.strptime(ch_transaction['date'], '%m/%d/%Y').month < month)) and (
                    datetime.strptime(ch_transaction['date'], '%m/%d/%Y').year < year or (datetime.strptime(ch_transaction['date'], '%m/%d/%Y').year == year and datetime.strptime(ch_transaction['date'], '%m/%d/%Y').month < month)):
            break

        # Get only latest transaction(s) from the candidates
        # Ex: if curr checking and savings transaction is 3/9/2026 and credit transaction is 3/6/2026, then only grab checking and savings to print
        candidates = [t for t in [ch_transaction, s_transaction, cr_transaction] if t is not None]
        latest_date = max(datetime.strptime(t['date'], '%m/%d/%Y') for t in candidates)
        latest = [t for t in candidates if datetime.strptime(t['date'], '%m/%d/%Y') == latest_date]

        row = latest_date.date().__str__().ljust(26)
        if ch_transaction and ch_transaction in latest:
            row += f"{ch_transaction['description'][:32].ljust(32)} | {str(ch_transaction['amount']).rjust(10)} | {str(ch_transaction['balance']).rjust(12)}".ljust(col_width)
        else:
            row += 'None'.center(col_width)
        if s_transaction and s_transaction in latest:
            row += f"{s_transaction['description'][:32].ljust(32)} | {str(s_transaction['amount']).rjust(10)} | {str(s_transaction['balance']).rjust(12)}".ljust(col_width)
        else:
            row += 'None'.center(col_width)
        if cr_transaction and cr_transaction in latest:
            row += f"{cr_transaction['description'][:32].ljust(32)} | {str(cr_transaction['amount']).rjust(10)} | {str(cr_transaction['balance']).rjust(12)}".ljust(col_width)
        else:
            row += 'None'.center(col_width)

        lines.append(row)

        if ch_transaction in latest:
            checking_ptr += 1
        if s_transaction in latest:
            savings_ptr += 1
        if cr_transaction in latest:
            credit_ptr += 1

    return lines


def log_top_aggregate_transactions(transactions: List[Transaction], num_transactions: int) -> List[str]:
    # Default dictionary where every entry (key = tuple(transaction, amount) has a default value as a dictionary with count, earliest_date, and latest_date
    aggregated_transactions = defaultdict(lambda: {"count": 0, "earliest_date": None, "latest_date": None})

    for transaction in transactions:
        transaction_key = (transaction["description"], transaction["amount"])
        aggregate_data = aggregated_transactions[transaction_key]
        date = transaction["date"]

        aggregate_data["count"] += 1
        aggregate_data["earliest_date"] = min(datetime.strptime(date, "%m/%d/%Y"), aggregate_data["earliest_date"]) if aggregate_data["earliest_date"] else datetime.strptime(date, "%m/%d/%Y")
        aggregate_data["latest_date"] = max(datetime.strptime(date, "%m/%d/%Y"), aggregate_data["latest_date"]) if aggregate_data["latest_date"] else datetime.strptime(date, "%m/%d/%Y")

    lines = []
    lines.append(f"\n\nSHOWING AGGREGATE TRANSACTIONS FOR {transactions[0]['account'].upper()} ACCOUNT\n")
    lines.append("Transactions")
    lines.append("=" * 30)
    counter = 0
    for (desc, amt), t in sorted(aggregated_transactions.items(), key=lambda x: x[1]["count"], reverse=True):
        if counter == num_transactions:
            break
        lines.append(f"Description: {(desc[:32] + (' ' * 30))[:32]} | Amount: {(str(amt) + (' ' * 10))[:10]} | Count: {t['count']} | Earliest Date: {t['earliest_date']} | Latest Date: {t['latest_date']}")
        counter += 1

    return lines
