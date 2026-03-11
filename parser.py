import csv
import os
from datetime import datetime

def parse_csv(file_path):
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def combine_and_sort_transactions(folder):
    all_transactions = []

    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder, filename)
            transactions = parse_csv(filepath)
            print(transactions)
            all_transactions.extend(transactions)

    # Sort transactions by 'Posted Date' from oldest to latest
    all_transactions.sort(key=lambda x: datetime.strptime(x['Posted Date'], '%m/%d/%Y'))

    return all_transactions

def write_to_combined_csv(transactions, output_file):
    if not transactions:
        print("No transactions to write.")
        return

    fieldnames = transactions[0].keys()
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

if __name__ == '__main__':
    folder = "finances/bofa/credit"
    output_file = "allCreditTransactions.csv"

    combined_transactions = combine_and_sort_transactions(folder)
    write_to_combined_csv(combined_transactions, output_file)
