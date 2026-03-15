import os
import csv
from typing import List, Dict, Tuple
from datetime import datetime

from models import BankTransaction

def parse_checking_or_savings_file(file_path: str) -> Tuple[List[Dict[str, object]], List[BankTransaction]]:
    """
    Parses a checking or savings transactions CSV file and returns the processed data.

    BofA CSV layout:
      Row 0:   Account summary header
      Rows 1-4: Account summary entries (beginning balance, deposits, etc.)
      Row 5:   Blank
      Row 6:   BankTransaction header
      Rows 7+: Individual transactions (oldest to newest in file)

    Parameters:
    - file_path (str): The path to the checking or savings CSV file.

    Returns:
    - (account_summary, transactions): account_summary is a list of balance/summary dicts;
      transactions is a list of individual transaction dicts sorted newest to oldest.
    """

    # Read all lines so we can slice by row index for the two sections
    with open(file_path, newline="") as f:
        lines = f.readlines()

    # Rows 1-4: account summary entries (row 0 is the header)
    reader = csv.DictReader(lines[1:5], fieldnames=next(csv.reader([lines[0]])))
    account_summary = [
        {
            # Detect account type from the filename (BofA files include "savings" or not)
            "account": "savings" if file_path.lower().count("savings") > 0 else "checking",
            "description": row["Description"],
            "amount": round(float(row["Summary Amt."].replace(",", "")), 2),
        }
        for row in reader
    ]

    # Rows 7+: individual transactions (row 6 is the header)
    reader = csv.DictReader(lines[7:], fieldnames=next(csv.reader([lines[6]])))
    transactions = [
        {
            "date": transaction["Date"],
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

    return account_summary, transactions

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

def aggregate_credit_files(directory: str) -> List[BankTransaction]:
    """
    Aggregates data from all credit CSV files in a specified directory.

    Only files ending in "_3653.csv" are processed (BofA credit account identifier).
    After aggregating, a running balance is computed chronologically and the list
    is reversed so the caller receives newest-first order.

    Parameters:
    - directory (str): The path to the directory containing the credit CSV files.

    Returns:
    - List[Dict[str, object]]: A list of transaction dicts sorted newest to oldest,
      each containing a computed 'balance' field.
    """
    transactions = []
    for filename in os.listdir(directory):
        # Only process files for the target credit account (identified by last 4 digits)
        if filename.endswith("_3653.csv"):
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

def parse_fidelity_file(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Parses a Fidelity investment statement CSV file.

    Fidelity CSV layout (one file per statement date, named Statement<MMDDYYYY>.csv):
      Row 0:   Account summary header
      Rows 1-2: One row per account (ROTH IRA, Individual)
      Rows 3-4: Blank
      Row 5:   Holdings header (Symbol/CUSIP, Description, Quantity, Price, ...)
      Row 6:   Blank / junk
      Row 7:   Blank
      Rows 8+: Holdings data, interleaved with:
                 - Account number rows  (e.g. "XXXXXXX") — marks start of a new account's block
                 - Category rows        (e.g. "Mutual Funds") — ignored
                 - Subtotal rows        (start with "Subtotal of") — ignored
                 - Fund/security rows   (Symbol in col 0, data in remaining cols)

    Parameters:
    - file_path: Path to a Statement<MMDDYYYY>.csv file.

    Returns:
    - (account_summaries, holdings): two lists of dicts, both keyed by date and account_type.
    """
    # Extract statement date from filename: Statement10312024.csv → "10/31/2024"
    date_str = os.path.splitext(os.path.basename(file_path))[0].replace("Statement", "")
    date = datetime.strptime(date_str, "%m%d%Y").strftime("%m/%d/%Y")

    with open(file_path, newline="") as f:
        lines = f.readlines()

    def safe_float(v: str):
        """Convert a possibly-empty, possibly-comma-formatted string to float, or None."""
        return round(float(v.replace(",", "")), 2) if v and v.strip() and v.strip().replace('.','').isnumeric() else 0

    # --- Account summaries (rows 1-2, using row 0 as the header) ---
    summary_fieldnames = next(csv.reader([lines[0]]))
    reader = csv.DictReader(lines[1:3], fieldnames=summary_fieldnames)
    account_summaries = []

    # Map account number to map account type to later grab account types for transactions 
    account_number_to_type_map = {}
    for row in reader:
        account_number_to_type_map[row["Account"]] = row["Account Type"]
        account_summaries.append({
            "date": date,
            "account_type": row["Account Type"].strip(),
            "beginning_mkt_value": safe_float(row["Beginning mkt Value"]),
            "change_in_investment": safe_float(row["Change in Investment"]),
            "ending_mkt_value": safe_float(row["Ending mkt Value"]),
            "dividends_period": safe_float(row["Dividends This Period"]),
            "dividends_ytd": safe_float(row["Dividends Year to Date"]),
            "total_period": safe_float(row["Total This Period"]),
            "total_ytd": safe_float(row["Total Year to Date"]),
        })

    # --- Holdings section (rows 7+, 0-indexed) ---
    holdings = []
    # Tracks which account block we're currently inside (-1 = before first account row)
    # current_account_idx = -1

    line_num = 10 
    holdings_fieldnames = next(csv.reader([lines[5]]))
    while line_num < len(lines):
        # reader = dict(Symbol/CUSIP,Description,Quantity,Price,Beginning Value,Ending Value,Cost Basis)
        transaction = next(csv.DictReader([lines[line_num]], fieldnames=holdings_fieldnames))
        holdings.append({
            "date": date,
            "account_type": account_number_to_type_map[lines[line_num - 2].strip()],
            "symbol": transaction["Symbol/CUSIP"],
            "description": transaction["Description"],
            "quantity": safe_float(transaction["Quantity"]),
            "price": safe_float(transaction["Price"]),
            "beginning_value": safe_float(transaction["Beginning Value"]),
            "ending_value": transaction["Ending Value"],
            "cost_basis": transaction["Cost Basis"],
            # Unrealized gain/loss = current market value minus what was paid for the shares
            # unrealized = round(ending_value - cost_basis, 2) if ending_value is not None and cost_basis is not None else None
        })
        line_num += 5
        # parsed_lines.append(csv.DictReader(f"{account_number_to_type_map[lines[line_num - 2]]}," + lines[line_num], filednames=['AccountType'] + lines[5]))

    # for line in lines[7:]:
    #     row = next(csv.reader([line]))
    #     # Ensure at least 7 columns so index access below is always safe
    #     while len(row) < 7:
    #         row.append("")
    #     non_empty = [c for c in row if c.strip()]
    #     if not non_empty:
    #         continue  # blank line
    #     first = row[0].strip()
    #     if not first:
    #         continue  # row with empty first cell (can happen with trailing commas)
    #     if first.startswith("Subtotal"):
    #         continue  # subtotal summary rows, e.g. "Subtotal of Mutual Funds"
    #     if first in known_categories:
    #         continue  # category header rows, e.g. "Mutual Funds"

    #     # Account number row: only the first cell is non-empty (the account number string)
    #     # Each such row starts a new account block; we map it to the next account_type in order
    #     if len(non_empty) == 1:
    #         current_account_idx += 1
    #         continue

    #     # Everything else with data in multiple columns is an actual fund/security row
    #     if current_account_idx < 0 or current_account_idx >= len(account_type_order):
    #         continue  # guard: skip any data rows that appear before the first account marker

    #     ending_value = safe_float(row[5])
    #     cost_basis = safe_float(row[6])
    #     # Unrealized gain/loss = current market value minus what was paid for the shares
    #     unrealized = round(ending_value - cost_basis, 2) if ending_value is not None and cost_basis is not None else None
    #     holdings.append({
    #         "date": date,
    #         "account_type": account_type_order[current_account_idx],
    #         "symbol": first,
    #         "description": row[1].strip(),
    #         "quantity": safe_float(row[2]),
    #         "price": safe_float(row[3]),
    #         "beginning_value": safe_float(row[4]),
    #         "ending_value": ending_value,
    #         "cost_basis": cost_basis,
    #         "unrealized_gain_loss": unrealized,
    #     })

    return account_summaries, holdings


def aggregate_fidelity_files(directory: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Aggregates data from all Fidelity statement CSVs in a directory.

    Looks for files matching the pattern Statement<MMDDYYYY>.csv and calls
    parse_fidelity_file on each one.

    Parameters:
    - directory: Path to directory containing Statement<MMDDYYYY>.csv files.

    Returns:
    - (all_summaries, all_holdings): both sorted by date ascending (oldest first)
    """
    all_summaries, all_holdings = [], []
    for filename in os.listdir(directory):
        if filename.startswith("Statement") and filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            summaries, holdings = parse_fidelity_file(file_path)
            all_summaries.extend(summaries)
            all_holdings.extend(holdings)
    all_summaries.sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"), reverse=True)
    all_holdings.sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"), reverse=True)
    return all_summaries, all_holdings