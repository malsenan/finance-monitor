import os
import csv
from typing import List, Dict, Tuple
from datetime import datetime
import heapq
from typing import TypedDict


class Transaction(TypedDict):
    account: str
    date: str
    description: str
    amount: float
    balance: float


"""
DATA STRUCTURES:
 - Transactions: 
    {
        'account': checking/savings/credit, 
        'date': mm/dd/yyyy,
        'description': description to aggregate on,
        'amount': float,
        'balance': float
    }
"""


def get_stats_between(
    transactions: List[Transaction],
    start_month: int,
    start_year: int,
    end_month: int,
    end_year: int,
) -> None:

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
    expenses = sum([a for a in amounts if a < 0])
    income = sum([a for a in amounts if a > 0])
    net_cost = sum(amounts)
    with open("datapoints.txt", "a") as datafile:
        datafile.write("Account: " + transactions[0]["account"] + "\n")
        datafile.write("=" * 30 + "\n")
        datafile.write(
            f"- Date Range: {start_month}/{start_year} - {end_month}/{end_year}\n"
        )
        datafile.write(f"- Net Cash Flow: {round(net_cost, 2)}\n")
        datafile.write(f"- Total Expenses: {expenses}\n")
        datafile.write(f"- Total Income: {income}\n\n")


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


def parse_checking_or_savings_file(
    file_path: str,
) -> Tuple[List[Dict[str, object]], List[Transaction]]:
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
            "account": "savings" if file_path.count("Savings") > 0 else "checking",
            "description": row["Description"],
            "amount": round(float(row["Summary Amt."].replace(",", "")), 2),
        }
        for row in reader
    ]
    reader = csv.DictReader(lines[7:], fieldnames=next(csv.reader([lines[6]])))
    transactions = [
        {
            "account": "savings" if file_path.count("Savings") > 0 else "checking",
            "date": row["Date"],
            "description": row["Description"],
            "amount": round(
                float(row["Amount"].replace(",", "")) if row["Amount"] else 0, 2
            ),
            "balance": row["Running Bal."],
        }
        for row in reader
    ]

    # Sort by newest to oldest
    transactions.reverse()

    # sumOfTransactions = sum([row['amount'] for row in transactions if row['amount']])
    # print(sumOfTransactions)
    return account_summary, transactions


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

    # currentCreditBalance = sum([row['amount'] for row in transactions if row['amount']])
    # Sort the aggregated data by date in ascending order (oldest to newest)
    transactions.sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"))

    currBal = 0
    for transaction in transactions:
        transaction["balance"] = round(currBal + transaction["amount"], 2)
        currBal += transaction["amount"]

    transactions.reverse()

    # Return the sorted aggregated data
    return transactions


def save_to_csv(data: List[Dict[str, object]], output_file: str) -> None:
    """
    Saves the aggregated data to a single CSV file.

    Parameters:
    - data (List[Dict[str, object]]): The list of dictionaries containing the aggregated data.
    - output_file (str): The path to the output CSV file.
    """
    # Define the fieldnames for the output CSV file
    fieldnames = list(data)[0].keys()
    # Open the output CSV file in write mode
    with open(output_file, mode="w", newline="") as file:
        # Create a CSV writer object using DictWriter to write the file
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Write the header row to the CSV file
        writer.writeheader()
        # Iterate over each row in the aggregated data and write it to the CSV file
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":

    # Define the directory containing the credit files
    credit_directory = "finances/credit"

    # Aggregate data from all CSV files in the specified directory
    credit_transactions = aggregate_credit_files(credit_directory)

    # Parse checking and savings account transactions and summaries
    checking_summary, checking_transactions = parse_checking_or_savings_file(
        "BofaCheckingTransactions.csv"
    )
    savings_summary, savings_transactions = parse_checking_or_savings_file(
        "BofaSavingsTransactions.csv"
    )

    # Save all transactions in a single data structure
    all_transactions = []

    def date_key(t):
        return datetime.strptime(t["date"], "%m/%d/%Y")

    all_transactions = list(
        heapq.merge(
            credit_transactions,
            checking_transactions,
            savings_transactions,
            key=date_key,
        )
    )
    all_transactions.reverse()

    # # Save the aggregated data to a single CSV file
    # save_to_csv(credit_transactions, 'parsed_data/parsedCreditTransactions.csv')
    # save_to_csv(checking_transactions, 'parsed_data/parsedCheckingTransactions.csv')
    # save_to_csv(savings_transactions, 'parsed_data/parsedSavingsTransactions.csv')
    # save_to_csv(all_transactions, 'parsed_data/allParsedTransactions.csv')
    # save_to_csv(checking_summary + savings_summary, 'parsed_data/accountSummaries.csv')

    # Calculate net worth
    checking_balance = checking_summary[-1]["amount"]
    savings_balance = savings_summary[-1]["amount"]
    credit_balance = credit_transactions[0]["balance"]
    with open("datapoints.txt", "a") as datafile:
        datafile.write(
            f"Networth: {checking_balance + savings_balance + credit_balance}\n\n"
        )

    # Get last month's income, expense, and net cash flow
    get_stats_between(credit_transactions, 2, 2026, 3, 2026)
    get_stats_between(checking_transactions, 2, 2026, 3, 2026)
    get_stats_between(savings_transactions, 2, 2026, 3, 2026)

    # Format and print out last X transactions for every account
    headers = ["date", "checking", "savings", "credit"]

    # Define how many latest transactions you want to see for the accounts
    num_transactions = 2

    # Calculate col width from longest description/amount/balance
    col_width = (
        max(
            len(f"{t['description']} | {t['amount']} | {t['balance']}")
            for transactions_list in [
                checking_transactions[:num_transactions],
                savings_transactions[:num_transactions],
                credit_transactions[:num_transactions],
            ]
            for t in transactions_list
        )
        + 4
    )

    lines = []
    header = "".join(h.ljust(col_width) for h in headers)
    lines.append(header)
    lines.append("=" * len(header))

    checking_ptr, savings_ptr, credit_ptr = 0

    # While we haven't exceeded number of transactions for all ptrs, iterate all 3 transactions at the same time
    while (
        checking_ptr < num_transactions
        or savings_ptr < num_transactions
        or credit_ptr < num_transactions
    ):
        # Grab all current transaction dates
        curr_dates = (
            ([checking_transactions[checking_ptr]['date']] if checking_ptr < num_transactions else []) +
            ([savings_transactions[savings_ptr]['date']] if savings_ptr < num_transactions else []) +
            ([credit_transactions[credit_ptr]['date']] if credit_ptr < num_transactions else [])
        )

        # Get latest transaction first
        latest_date = max([datetime.strptime(d, "%m/%d/%Y") for d in curr_dates])


    #     rows = [
    #     ('Date Range', '2/2026 - 3/2026', '2/2026 - 3/2026', '2/2026 - 3/2026'),
    #     ('Net Cash Flow', '-401.94', '-366.16', '-10056.43'),
    #     ('Total Expenses', '-3199.94', '-19674.57', '-11100.0'),
    #     ('Total Income', '2798.0', '19308.41', '1043.57'),
    # ]
    # print(credit_transactions[:5])
