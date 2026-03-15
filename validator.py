from parsers import Transaction
from typing import List

def validate_balance(transactions: List[Transaction]):
    curr_balance = transactions[-1]['balance']
    for t in transactions[-2::-1]:
        curr_balance = round(curr_balance + t['amount'], 2)
        if t['balance'] != curr_balance:
            print("MAJOR ALERT " * 50)