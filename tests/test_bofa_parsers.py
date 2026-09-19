import os

from parsers import aggregate_credit_files, parse_checking_or_savings_file

# Made-up rows in the layout of BofA's checking, savings and credit downloads
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_parse_checking_or_savings_file():
    checking = parse_checking_or_savings_file(os.path.join(FIXTURES, "checkingTransactions.csv"))
    savings = parse_checking_or_savings_file(os.path.join(FIXTURES, "savingsTransactions.csv"))

    # Newest first, with the commas stripped from amounts and balances
    assert checking == [
        {"date": "03/02/2026", "account": "checking", "description": "CAFE 03/01 PURCHASE ANYTOWN ST", "amount": -12.5, "balance": 2487.5},
        {"date": "02/10/2026", "account": "checking", "description": "Online Banking transfer to SAV 0000 Confirmation# 1111111111", "amount": -1000.0, "balance": 2500.0},
        {"date": "01/15/2026", "account": "checking", "description": "EMPLOYER A LIST:PAYROLL ID:XXXXX00000 NAME:JANE DOE CO ID:XXXXX00000 PPD", "amount": 2000.0, "balance": 3500.0},
        {"date": "01/05/2026", "account": "checking", "description": "KEEP THE CHANGE TRANSFER TO ACCT 0000 FOR 01/05/26", "amount": -0.75, "balance": 1500.0},
    ]
    # The account type comes from the file name
    assert {t["account"] for t in savings} == {"savings"}


def test_aggregate_credit_files():
    credit = aggregate_credit_files(os.path.join(FIXTURES, "credit"), "_0000.csv")

    # Both files are combined and sorted newest first, with one running balance starting from 0
    assert credit == [
        {"date": "02/25/2026", "account": "credit", "description": "PHONE BILL PAYMENT ST", "amount": -80.0, "balance": -120.0},
        {"date": "02/15/2026", "account": "credit", "description": "Online payment from CHK 0000", "amount": 100.0, "balance": -40.0},
        {"date": "02/10/2026", "account": "credit", "description": "GAS STATION ANYTOWN ST", "amount": -40.0, "balance": -140.0},
        {"date": "01/20/2026", "account": "credit", "description": "GROCERY STORE ANYTOWN ST", "amount": -60.0, "balance": -100.0},
        {"date": "01/10/2026", "account": "credit", "description": "GAS STATION ANYTOWN ST", "amount": -40.0, "balance": -40.0},
    ]
