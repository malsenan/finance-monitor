import heapq
import shutil
from datetime import datetime
from typing import List
from copy import deepcopy

import config
from parsers import aggregate_credit_files, parse_checking_or_savings_file, parse_fidelity_transactions
from exporters import save_to_csv
from reporters import (
    log_account_stats_between,
    log_last_x_transactions,
    log_transactions_since,
    log_top_aggregate_transactions,
    log_return_per_holding,
)
from charts import (
    plot_line_monthly_balance,
    plot_bar_monthly_income_vs_spending,
    plot_line_savings_rate,
    plot_line_fidelity_portfolio,
    plot_line_fidelity_per_account,
    plot_line_fidelity_holdings,
    plot_line_savings_by_month
)
from validator import validate_balance

if __name__ == "__main__":
    plot_balances = False
    plot_income_vs_spending = False
    plot_fidelity = False

    # Aggregate data from all CSV files in the specified directory
    credit_transactions = aggregate_credit_files(config.CREDIT_DIR, config.CREDIT_FILE_SUFFIX)

    # Parse checking and savings account transactions
    checking_transactions = parse_checking_or_savings_file(config.CHECKING_FILE)
    savings_transactions = parse_checking_or_savings_file(config.SAVINGS_FILE)

    # Parse Fidelity transactions for every account (401k plans, Roth IRA, individual)
    all_fidelity_summaries, all_fidelity_holdings = parse_fidelity_transactions(config.FIDELITY_FILE, config.FIDELITY_ACCOUNTS)

    # For Fidelity, create separate list that will also hold unrealized_gains and net_worth to save to csv
    enhanced_fidelity_holdings = deepcopy(all_fidelity_holdings)
    curr_balances = {}
    for holding in enhanced_fidelity_holdings[::-1]:
        holding['unrealized_gains'] = round(holding['ending_value'] - holding['cost_basis'], 2)
        curr_balances[holding['account']] = holding['ending_value']
        holding['net_worth'] = round(sum(curr_balances.values()), 2)
        

    # Validate all transactions are accounted for in the running balances
    validate_balance(checking_transactions)
    validate_balance(savings_transactions)

    # Grab list of individual fidelity transactions to merge into all transactions
    # Sanitize to have fields {date, account, description, amount (curr_cost_basis - prev_cost_basis), and balance ('ending_value')}
    fidelity_transactions = []
    cost_bases = []
    for i, transaction in enumerate(all_fidelity_holdings[::-1]):

        transaction_cost = transaction['cost_basis']
        # Find prev cost_basis (if exists) to subtract by and find cost of transaction
        for prev_transaction in all_fidelity_holdings[len(all_fidelity_holdings) - i:]:
            if prev_transaction['account'] == transaction['account'] and prev_transaction['symbol'] == transaction['symbol']:
                transaction_cost = round(transaction_cost - prev_transaction['cost_basis'], 2)
                break

        fidelity_transactions.insert(0,
            {
                'date': transaction['date'],
                'account': transaction['account'],
                'description': transaction['description'],
                'amount': transaction_cost,
                'balance': round(sum(t['ending_value'] for t in [holding for holding in all_fidelity_holdings if holding['date'] == transaction['date'] and holding['account'] == transaction['account']]), 2)
            }
        )
        cost_bases.insert(0, { 
            'date': transaction['date'],
            'account': transaction['account'],
            'description': transaction['description'],
            'amount': transaction_cost,
            'balance': round(sum(t['cost_basis'] for t in [holding for holding in all_fidelity_holdings if holding['date'] == transaction['date'] and holding['account'] == transaction['account']]), 2)
        })

    # Save all transactions in a single data structure
    # Use deep copies, otherwise changes to all_transactions apply to the other arrays
    all_transactions = list(
        heapq.merge(
            deepcopy(credit_transactions),
            deepcopy(checking_transactions),
            deepcopy(savings_transactions),
            deepcopy(fidelity_transactions),
            key=lambda t: datetime.strptime(t["date"], "%m/%d/%Y"),
            reverse=True
        )
    )

    # Calculate net worth on all_transactions
    curr_balances = {}
    for t in all_transactions[::-1]:
        curr_balances[t['account']] = t['balance']
        t['net_worth'] = round(sum(curr_balances.values()), 2)

    # Save the BofA data to CSV files
    save_to_csv(credit_transactions, config.PARSED_CREDIT_FILE)
    save_to_csv(checking_transactions, config.PARSED_CHECKING_FILE)
    save_to_csv(savings_transactions, config.PARSED_SAVINGS_FILE)

    # Save the Fidelity data to CSV files
    save_to_csv(fidelity_transactions, config.PARSED_FIDELITY_TRANSACTIONS_FILE)
    save_to_csv(all_fidelity_summaries, config.PARSED_FIDELITY_SUMMARIES_FILE)
    save_to_csv(enhanced_fidelity_holdings, config.PARSED_FIDELITY_HOLDINGS_FILE)
    
    # Save the all aggregated data to a CSV file
    save_to_csv(all_transactions, config.ALL_TRANSACTIONS_FILE)

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
        # Aggregate equal transactions and log by most frequent (ex: Description: COFFEE SHOP 01/18 PURCHASE | Amount: -4.25 | Count: 3)
        log_top_aggregate_transactions(checking_transactions, 10) +
        log_top_aggregate_transactions(savings_transactions, 10) +
        log_top_aggregate_transactions(credit_transactions, 10) +
        log_return_per_holding(all_fidelity_holdings)
    ]

    # Calculate net worth and put it at the top of the file
    checking_balance = checking_transactions[0]["balance"]
    savings_balance = savings_transactions[0]["balance"]
    credit_balance = credit_transactions[0]["balance"]
    lines.insert(0, f"Net worth: {round(checking_balance + savings_balance + credit_balance, 2)}\n")

    # Log the human readable data
    with open(config.STATS_FILE, 'w') as stats_file:
        stats_file.write('\n'.join(lines))

    # Back up this run's output into a folder named by when it was produced
    shutil.copytree(config.PARSED_DATA_DIR, config.BACKUP_DIR)

    if plot_balances:
        # Plot net worth over time (checking + savings - credit)
        plot_line_monthly_balance(all_transactions, graph_title='net worth over time')

        plot_line_monthly_balance(checking_transactions, graph_title='checking balance')
        plot_line_monthly_balance(savings_transactions, graph_title='savings balance')
        plot_line_monthly_balance(credit_transactions, graph_title='credit balance')
        

        # Plot balance over time on checking, savings, and credit accounts (one chart)
        plot_line_monthly_balance([
            (all_transactions, "all"),
            (checking_transactions, "checking"),
            (savings_transactions, "savings"),
            (credit_transactions, "credit"),
            (fidelity_transactions, "fidelity"),  
        ], graph_title="account balances over time")

        # Plots total fidelity balance (personal brokerage + ROTH IRA + 401k) over time against total cost basis
        plot_line_monthly_balance([(fidelity_transactions, "sum of accounts"), (cost_bases, "money invested")], graph_title="fidelity balances over time")            

    plot_line_savings_by_month(savings_transactions, fidelity_transactions, config.ANNUAL_INCOME)

    

    if plot_income_vs_spending:
        # Plot daily income vs. spending
        plot_bar_monthly_income_vs_spending(all_transactions, graph_title="Total Monthly Income vs. Spending", limit=config.MONTHLY_SPENDING_LIMIT)
        plot_bar_monthly_income_vs_spending(checking_transactions, graph_title="Checking Monthly Income vs. Spending", limit=config.MONTHLY_SPENDING_LIMIT)
        plot_bar_monthly_income_vs_spending(savings_transactions, graph_title="Savings Monthly Income vs. Spending", limit=config.MONTHLY_SPENDING_LIMIT)
        plot_bar_monthly_income_vs_spending(credit_transactions, graph_title="Credit Monthly Income vs. Spending", limit=config.CREDIT_SPENDING_LIMIT)

    # Plot Fidelity data
    if plot_fidelity:
        
        plot_line_fidelity_portfolio(all_fidelity_summaries)
        plot_line_fidelity_per_account(all_fidelity_summaries)

        #Plots each symbol (ex: FXAIX) separately
        plot_line_fidelity_holdings(all_fidelity_holdings)