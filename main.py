import heapq
from datetime import datetime
from typing import List

from parsers import aggregate_credit_files, parse_checking_or_savings_file
from exporters import save_to_csv
from reporters import (
    log_account_stats_between,
    log_last_x_transactions,
    log_transactions_since,
    log_top_aggregate_transactions,
)
from charts import plot_running_balance

if __name__ == "__main__":

    # Aggregate data from all CSV files in the specified directory
    credit_transactions = aggregate_credit_files('/home/malsenan/Documents/finances/bofa/credit')

    # Parse checking and savings account transactions and summaries
    checking_summary, checking_transactions = parse_checking_or_savings_file("/home/malsenan/Documents/finances/bofa/debit/checkingTransactions.csv")
    savings_summary, savings_transactions = parse_checking_or_savings_file("/home/malsenan/Documents/finances/bofa/savings/savingsTransactions.csv")

    # Save all transactions in a single data structure
    all_transactions = list(
        heapq.merge(
            credit_transactions,
            checking_transactions,
            savings_transactions,
            key=lambda t: datetime.strptime(t["date"], "%m/%d/%Y"),
            reverse=True
        )
    )
    
    curr_balances = {'checking': 0, 'savings': 0, 'credit': 0}
    for t in all_transactions[::-1]:
        curr_balances[t['account']] = t['balance']
        t['net_worth'] = round(sum(curr_balances.values(), 2))

    # Save the parsed data to CSV files
    save_to_csv(credit_transactions, '/home/malsenan/Documents/finances/parsed_data/parsedCreditTransactions.csv')
    save_to_csv(checking_transactions, '/home/malsenan/Documents/finances/parsed_data/parsedCheckingTransactions.csv')
    save_to_csv(savings_transactions, '/home/malsenan/Documents/finances/parsed_data/parsedSavingsTransactions.csv')
    save_to_csv(all_transactions, '/home/malsenan/Documents/finances/parsed_data/allParsedTransactions.csv')
    save_to_csv(checking_summary + savings_summary, '/home/malsenan/Documents/finances/parsed_data/accountSummaries.csv')

    # Log human readable statistics and transaction stuff
    lines: List[str] = [line for line in
        # Get last month's income, expense, and net cash flow
        log_account_stats_between(credit_transactions, 2, 2026, 3, 2026) +
        log_account_stats_between(checking_transactions, 2, 2026, 3, 2026) +
        log_account_stats_between(savings_transactions, 2, 2026, 3, 2026) +
        # Format and print out last X transactions for every account
        log_last_x_transactions(checking_transactions, savings_transactions, checking_transactions, 10) +
        # Format and print out all transactions since mm/yyyy
        log_transactions_since(checking_transactions, savings_transactions, credit_transactions, 2, 2026) +
        # Aggregate equal transactions and log by most frequent (ex: Description: METRO 01/18 MOBILE PURCHASE WASH | Amount: -2.5 | Count: 3)
        log_top_aggregate_transactions(checking_transactions, 10) +
        log_top_aggregate_transactions(savings_transactions, 10) +
        log_top_aggregate_transactions(credit_transactions, 10)
    ]

    # Calculate net worth and put it at the top of the file
    checking_balance = checking_summary[-1]["amount"]
    savings_balance = savings_summary[-1]["amount"]
    credit_balance = credit_transactions[0]["balance"]
    lines.insert(0, f"Net worth: {round(checking_balance + savings_balance + credit_balance, 2)}\n")

    # Log the human readable data
    with open('/home/malsenan/Documents/finances/parsed_data/stats.txt', 'w') as stats_file:
        stats_file.writelines('\n'.join(lines))

    # Usage
    # plot_running_balance(checking_transactions, balance_key='balance', account="checking")
    # plot_running_balance(savings_transactions, balance_key='balance', account="savings")
    # plot_running_balance(credit_transactions, balance_key='balance', account="credit")
    plot_running_balance(all_transactions, balance_key='net_worth', account='net worth over time')
