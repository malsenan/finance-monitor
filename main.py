import heapq
from datetime import datetime
from typing import List

from parsers import aggregate_credit_files, parse_checking_or_savings_file, parse_fidelity_401k, aggregate_fidelity_statements
from exporters import save_to_csv
from reporters import (
    log_account_stats_between,
    log_last_x_transactions,
    log_transactions_since,
    log_top_aggregate_transactions,
)
from charts import (
    plot_line_monthly_balance, 
    plot_bar_monthly_income_vs_spending,
    plot_line_fidelity_portfolio, 
    plot_line_fidelity_per_account, 
    plot_line_fidelity_holdings
)
from validator import validate_balance

if __name__ == "__main__":

    # Aggregate data from all CSV files in the specified directory
    credit_transactions = aggregate_credit_files('/home/malsenan/Documents/finances/bofa/credit')

    # Parse checking and savings account transactions and summaries
    checking_summary, checking_transactions = parse_checking_or_savings_file("/home/malsenan/Documents/finances/bofa/debit/checkingTransactions.csv")
    savings_summary, savings_transactions = parse_checking_or_savings_file("/home/malsenan/Documents/finances/bofa/savings/savingsTransactions.csv")

    # Parse Fidelity 401k transactions
    fidelity_401k_transactions = parse_fidelity_401k("/home/malsenan/Documents/finances/fidelity/fidelityTransactions.csv")

    # Parse Fidelity investment statements
    fidelity_summaries, fidelity_holdings = aggregate_fidelity_statements('/home/malsenan/Documents/finances/fidelity')

    # Aggregate 401k and individual fidelity data
    all_fidelity_transactions = list(
        heapq.merge(
            fidelity_401k_transactions,
            fidelity_holdings,
            key=lambda t: datetime.strptime(t["date"], "%m/%d/%Y"),
            reverse=True
        )
    )

    # Validate all transactions are accounted for in the running balances
    validate_balance(checking_transactions)
    validate_balance(savings_transactions)

    # Grab list of individual fidelity transactions to merge into all transactions
    # Sanitize to have fields {date, account, description, amount (curr_cost_basis - prev_cost_basis), and balance ('ending_value')}
    fidelity_statements = []
    cost_bases = []
    for i, transaction in enumerate(all_fidelity_transactions[::-1]):

        transaction_cost = transaction['cost_basis']
        # Find prev cost_basis (if exists) to subtract by and find cost of transaction
        for prev_transaction in all_fidelity_transactions[len(all_fidelity_transactions) - i:]:
            if prev_transaction['account'] == transaction['account'] and prev_transaction['symbol'] == transaction['symbol']:
                transaction_cost = round(transaction_cost - prev_transaction['cost_basis'], 2)
                break

        fidelity_statements.insert(0,
            {
                'date': transaction['date'],
                'account': transaction['account'],
                'description': transaction['description'],
                'amount': transaction_cost,
                'balance': round(sum(t['ending_value'] for t in [holding for holding in all_fidelity_transactions if holding['date'] == transaction['date'] and holding['account'] == transaction['account']]), 2)
            }
        )
        cost_bases.insert(0, { 
            'date': transaction['date'],
            'account': transaction['account'],
            'description': transaction['description'],
            'amount': transaction_cost,
            'balance': round(sum(t['cost_basis'] for t in [holding for holding in all_fidelity_transactions if holding['date'] == transaction['date'] and holding['account'] == transaction['account']]), 2)
        })

    # Save all transactions in a single data structure
    all_transactions = list(
        heapq.merge(
            credit_transactions,
            checking_transactions,
            savings_transactions,
            fidelity_statements,
            key=lambda t: datetime.strptime(t["date"], "%m/%d/%Y"),
            reverse=True
        )
    )

    # Save the parsed data to CSV files
    save_to_csv(credit_transactions, '/home/malsenan/Documents/finances/parsed_data/parsedCreditTransactions.csv')
    save_to_csv(checking_transactions, '/home/malsenan/Documents/finances/parsed_data/parsedCheckingTransactions.csv')
    save_to_csv(savings_transactions, '/home/malsenan/Documents/finances/parsed_data/parsedSavingsTransactions.csv')
    save_to_csv(fidelity_summaries, '/home/malsenan/Documents/finances/parsed_data/fidelitySummaries.csv')
    save_to_csv(fidelity_holdings, '/home/malsenan/Documents/finances/parsed_data/parsedFidelityHoldings.csv')
    save_to_csv(fidelity_401k_transactions, '/home/malsenan/Documents/finances/parsed_data/parsedFidelity401k.csv')
    
    curr_balances = {}
    curr_date = None
    for t in all_transactions[::-1]:
        curr_date = t['date']
        curr_balances[t['account']] = t['balance']
        t['net_worth'] = round(sum(curr_balances.values()), 2)

    # Save the parsed data to CSV files
    save_to_csv(all_transactions, '/home/malsenan/Documents/finances/parsed_data/allParsedTransactions.csv')
    save_to_csv(checking_summary + savings_summary, '/home/malsenan/Documents/finances/parsed_data/bankAccountSummaries.csv')

    # Log human readable statistics and transaction stuff
    lines: List[str] = [line for line in
        # Get last month's income, expense, and net cash flow
        log_account_stats_between(credit_transactions, 2, 2026, 3, 2026) +
        log_account_stats_between(checking_transactions, 2, 2026, 3, 2026) +
        log_account_stats_between(savings_transactions, 2, 2026, 3, 2026) +
        # Format and print out last X transactions for every account
        log_last_x_transactions(checking_transactions, savings_transactions, credit_transactions, 10) +
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
        stats_file.write('\n'.join(lines))

    # Plot net worth over time (checking + savings - credit)
    plot_line_monthly_balance(all_transactions, graph_title='net worth over time')

    '''
    plot_line_monthly_balance(checking_transactions, graph_title='checking balance')
    plot_line_monthly_balance(savings_transactions, graph_title='savings balance')
    plot_line_monthly_balance(credit_transactions, graph_title='credit balance')
    '''

    # Plot balance over time on checking, savings, and credit accounts (one chart)
    plot_line_monthly_balance([
        (all_transactions, "all"),
        (checking_transactions, "checking"),
        (savings_transactions, "savings"),
        (credit_transactions, "credit"),
    ], graph_title="account balances over time")

    plot_line_monthly_balance([(fidelity_statements, "sum of accounts"), (cost_bases, "money invested")], graph_title="fidelity balances over time")

    # # Plot daily income vs. spending
    plot_bar_monthly_income_vs_spending(all_transactions, graph_title="Total Monthly Income vs. Spending", limit=1000)
    # plot_bar_monthly_income_vs_spending(checking_transactions, graph_title="Checking Monthly Income vs. Spending", limit=1000)
    # plot_bar_monthly_income_vs_spending(savings_transactions, graph_title="Savings Monthly Income vs. Spending", limit=1000)
    # plot_bar_monthly_income_vs_spending(credit_transactions, graph_title="Credit Monthly Income vs. Spending", limit=284)


    # Plot Fidelity investment statements
    # plot_line_fidelity_portfolio(fidelity_summaries)
    # plot_line_fidelity_per_account(fidelity_summaries)
    # plot_line_fidelity_holdings(fidelity_holdings)
    
