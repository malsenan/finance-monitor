import os
import csv
from typing import List, Dict, Tuple
from datetime import datetime
from itertools import groupby

from models import BankTransaction, FidelityTransaction

def parse_checking_or_savings_file(file_path: str) -> List[BankTransaction]:
    """
    Parses a checking or savings transactions CSV file and returns the processed data.

    BofA CSV has a Date,Description,Amount,Running Bal. header row followed by one
    transaction per row (oldest to newest in file).

    Parameters:
    - file_path (str): The path to the checking or savings CSV file.

    Returns:
    - List[Dict[str, object]]: A list of transaction dicts sorted newest to oldest.
    """
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        transactions = [
            {
                "date": transaction["Date"],
                # Detect account type from the filename (BofA files include "savings" or not)
                "account": "savings" if file_path.lower().count("savings") > 0 else "checking",
                "description": transaction["Description"],
                # Amount may be blank for certain rows; default to 0 to avoid conversion errors
                "amount": round(float(transaction["Amount"].replace(",", "")) if transaction["Amount"] else 0, 2),
                "balance": round(float(transaction["Running Bal."].replace(',', '')), 2),
            }
            for transaction in reader
        ]

    # BofA exports oldest-first; reverse so callers receive newest-first
    transactions.reverse()

    return transactions

def parse_credit_file(file_path: str) -> List[BankTransaction]:
    """
    Parses a single credit transactions CSV file and returns the processed data.

    BofA credit CSV has a standard header row followed by one transaction per row.

    Parameters:
    - file_path (str): The path to the credit CSV file.

    Returns:
    - List[Dict[str, object]]: A list of transaction dicts (no particular sort order from this function).
    """
    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        transactions = [
            {
                "date": transaction["Posted Date"],
                "account": "credit",
                "description": transaction["Payee"],
                "amount": round(float(transaction["Amount"]), 2),
            }
            for transaction in reader
        ]

    return transactions

def aggregate_credit_files(directory: str, file_suffix: str) -> List[BankTransaction]:
    """
    Aggregates data from all credit CSV files in a specified directory.

    Only files ending in file_suffix are processed, which identifies the target
    credit account. After aggregating, a running balance is computed chronologically
    and the list is reversed so the caller receives newest-first order.

    Parameters:
    - directory (str): The path to the directory containing the credit CSV files.
    - file_suffix (str): Filename suffix identifying the target credit account's exports.

    Returns:
    - List[Dict[str, object]]: A list of transaction dicts sorted newest to oldest,
      each containing a computed 'balance' field.
    """
    transactions = []
    for filename in os.listdir(directory):
        # Only process files for the target credit account (identified by last 4 digits)
        if filename.endswith(file_suffix):
            file_path = os.path.join(directory, filename)
            parsed_data = parse_credit_file(file_path)
            transactions.extend(parsed_data)

    # Sort oldest-first so we can compute a running balance in chronological order
    transactions.sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"))

    # Compute a cumulative running balance across all transactions
    curr_bal = 0
    for transaction in transactions:
        transaction["balance"] = round(curr_bal + transaction["amount"], 2)
        curr_bal += transaction["amount"]

    # Reverse to newest-first for display and reporting
    transactions.reverse()

    return transactions

def parse_fidelity_transactions(file_path: str, account_labels: Dict[str, str]) -> Tuple[List[Dict], List[FidelityTransaction]]:
    """
    Parses Fidelity's transaction history for every account (401k plans, Roth IRA, individual).

    Replays rows oldest first and tracks shares, cost basis and price per account and fund.
    Rows with a Quantity of 0 (deposits, dividends, Change in Market Value) are skipped.
    The rules and worked examples are in docs/fidelity-transactions.md.

    Parameters:
    - file_path (str): Path to fidelityTransactions.csv (Accounts_History.csv layout, newest row first).
    - account_labels (Dict[str, str]): Fidelity account number -> label used in the output.

    Returns:
    - (summaries, holdings), both newest first: one summary row per account and one holdings
      row per fund, for each day that account or fund changed.
    """
    with open(file_path, newline="") as f:
        rows = list(csv.DictReader(f))

    funds = {}  # (account number, fund) -> running shares, cost basis and price
    summaries = []
    holdings = []
    # Rows are newest first, so replay them reversed, one day at a time
    for date, day_rows in groupby(reversed(rows), key=lambda row: row["Run Date"]):
        changed = {}  # (account number, fund) -> the day's last Action for that fund
        for row in day_rows:
            quantity = float(row["Quantity"])
            if quantity == 0:
                continue
            key = (row["Account Number"], row["Symbol"] or row["Description"])
            fund = funds.setdefault(key, {"shares": 0.0, "cost_basis": 0.0, "price": 0.0})
            amount = abs(float(row["Amount ($)"]))
            if quantity > 0:
                fund["cost_basis"] += amount
            else:
                # Remove the average cost of the shares that left
                fund["cost_basis"] -= fund["cost_basis"] / fund["shares"] * -quantity
            fund["shares"] += quantity
            # 401k rows have no Price, and fee rows are too rounded to derive one from
            if row["Price ($)"]:
                fund["price"] = float(row["Price ($)"])
            elif row["Action"] in ("Contributions", "Withdrawals"):
                fund["price"] = amount / abs(quantity)
            changed[key] = row["Action"]

        # One row per changed fund and account, so main.py's per-date sums count each fund once
        for (number, name), action in changed.items():
            fund = funds[(number, name)]
            holdings.append({
                "date": date,
                "account": f"{account_labels[number]} - {name}",
                "symbol": name,
                "description": action,
                "quantity": round(fund["shares"], 3),
                "price_per_share": round(fund["price"], 2),
                "ending_value": round(fund["shares"] * fund["price"], 2),
                "cost_basis": round(fund["cost_basis"], 2),
            })
        for number in dict.fromkeys(number for number, _ in changed):
            summaries.append({
                "date": date,
                "account": account_labels[number],
                "ending_mkt_value": round(sum(f["shares"] * f["price"] for (n, _), f in funds.items() if n == number), 2),
            })

    holdings.reverse()
    summaries.reverse()
    return summaries, holdings
