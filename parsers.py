import os
import csv
from typing import List, Dict, Tuple
from datetime import datetime

from models import Transaction

def parse_checking_or_savings_file(file_path: str) -> Tuple[List[Dict[str, object]], List[Transaction]]:
    """
    Parses a checking or savings transactions CSV file and returns the processed data.

    Parameters:
    - file_path (str): The path to the checking or savings CSV file.

    Returns:
    - List[List[Dict[str, object]]]: 2 lists of dictionaries, one containing account summary and one containing all transactions
    """

    # Open the CSV file
    with open(file_path, newline="") as f:
        lines = f.readlines()

    reader = csv.DictReader(lines[1:5], fieldnames=next(csv.reader([lines[0]])))
    account_summary = [
        {
            "account": "savings" if file_path.lower().count("savings") > 0 else "checking",
            "description": row["Description"],
            "amount": round(float(row["Summary Amt."].replace(",", "")), 2),
        }
        for row in reader
    ]
    reader = csv.DictReader(lines[7:], fieldnames=next(csv.reader([lines[6]])))
    transactions = [
        {
            "account": "savings" if file_path.lower().count("savings") > 0 else "checking",
            "date": row["Date"],
            "description": row["Description"],
            "amount": round(float(row["Amount"].replace(",", "")) if row["Amount"] else 0, 2),
            "balance": round(float(row["Running Bal."].replace(',', '')), 2),
        }
        for row in reader
    ]

    # Sort by newest to oldest
    transactions.reverse()

    return account_summary, transactions

def parse_credit_file(file_path: str) -> List[Transaction]:
    """
    Parses a single credit transactions CSV file and returns the processed data.

    Parameters:
    - file_path (str): The path to the credit CSV file.

    Returns:
    - List[Dict[str, object]]: A list of dictionaries containing the parsed data.
    """
    # Open the CSV file in read mode
    with open(file_path, mode="r", newline="") as file:
        # Create a CSV reader object using DictReader to read the file
        reader = csv.DictReader(file)
        # Initialize an empty list to store processed rows
        transactions = []
        # Iterate over each row in the CSV file
        for row in reader:
            # Process each row by extracting relevant fields and converting 'Amount' to float
            transaction = {
                "account": "credit",
                "date": row["Posted Date"],
                "description": row["Payee"],
                "amount": round(float(row["Amount"]), 2),
            }
            # Append the processed row to the parsed_data list
            transactions.append(transaction)

    # Return the list of processed rows
    return transactions

def aggregate_credit_files(directory: str) -> List[Transaction]:
    """
    Aggregates data from all credit CSV files in a specified directory.

    Parameters:
    - directory (str): The path to the directory containing the credit CSV files.

    Returns:
    - List[Dict[str, object]]: A list of dictionaries containing the aggregated data.
    """
    # Initialize an empty list to store aggregated data
    transactions = []
    # Iterate over each file in the specified directory
    for filename in os.listdir(directory):
        # Check if the file is a CSV file for my credit account
        if filename.endswith("_3653.csv"):
            # Construct the full path to the file
            file_path = os.path.join(directory, filename)
            # Parse the credit file and get the processed data
            parsed_data = parse_credit_file(file_path)
            # Extend the aggregated data list with the parsed data
            transactions.extend(parsed_data)

    # Sort the aggregated data by date in ascending order (oldest to newest)
    transactions.sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"))

    currBal = 0
    for transaction in transactions:
        transaction["balance"] = round(currBal + transaction["amount"], 2)
        currBal += transaction["amount"]

    transactions.reverse()

    # Return the sorted aggregated data
    return transactions
