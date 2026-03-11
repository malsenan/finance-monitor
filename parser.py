import csv
import os
from datetime import datetime

def parse_csv(file_path):
    """
    Parses a CSV file and returns its contents as a list of dictionaries.
    
    :param file_path: Path to the CSV file.
    :return: List of dictionaries, where each dictionary represents a row in the CSV.
    """
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def combine_and_sort_transactions(folder):
    """
    Combines all transactions from CSV files in a given folder and sorts them by 'Posted Date' from oldest to latest.
    
    :param folder: Path to the folder containing CSV transaction files.
    :return: List of combined and sorted transactions.
    """
    all_transactions = []

    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder, filename)
            transactions = parse_csv(filepath)
            print(transactions)  # Debugging: Print each file's transactions
            all_transactions.extend(transactions)

    # Sort transactions by 'Posted Date' from oldest to latest
    all_transactions.sort(key=lambda x: datetime.strptime(x['Posted Date'], '%m/%d/%Y'))

    return all_transactions

def aggregate_transactions(transactions):
    """
    Aggregates transactions by payee, address, and amount.
    
    :param transactions: List of transaction dictionaries.
    :return: Sorted list of aggregated transactions.
    """
    aggregated_data = {}

    for transaction in transactions:
        key = (transaction['Payee'], transaction['Address'], transaction['Amount'])
        if key not in aggregated_data:
            aggregated_data[key] = {
                'count': 0,
                'dates': []
            }
        aggregated_data[key]['count'] += 1
        aggregated_data[key]['dates'].append(transaction['Posted Date'])

    # Sort by frequency (most frequent to least frequent) and then by date (most recent to least recent)
    sorted_aggregated_data = sorted(
        aggregated_data.items(),
        key=lambda x: (-x[1]['count'], max(datetime.strptime(date, '%m/%d/%Y') for date in x[1]['dates']))
    )

    return sorted_aggregated_data

def write_to_combined_csv(transactions, output_file):
    """
    Writes a list of transactions to a CSV file.
    
    :param transactions: List of transaction dictionaries or aggregated transaction tuples.
    :param output_file: Path to the output CSV file.
    """
    if not transactions:
        print("No transactions to write.")
        return

    fieldnames = ['Payee', 'Address', 'Amount', 'Count', 'Most Recent Date']
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for (payee, address, amount), data in transactions:
            most_recent_date = max(data['dates'], key=lambda x: datetime.strptime(x, '%m/%d/%Y'))
            writer.writerow({
                'Payee': payee,
                'Address': address,
                'Amount': amount,
                'Count': data['count'],
                'Most Recent Date': most_recent_date
            })

if __name__ == '__main__':
    folder = "finances/bofa/credit"
    output_file = "allCreditTransactions.csv"
    aggregated_output_file = "aggregatedCredit.csv"

    # Combine and sort transactions from the specified folder
    combined_transactions = combine_and_sort_transactions(folder)
    
    # Write combined transactions to a CSV file
    write_to_combined_csv(combined_transactions, output_file)

    # Aggregate transactions by payee, address, and amount
    aggregated_transactions = aggregate_transactions(combined_transactions)
    
    # Write aggregated transactions to a separate CSV file
    write_to_combined_csv(aggregated_transactions, aggregated_output_file)
