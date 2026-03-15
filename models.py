from typing import TypedDict


class BankTransaction(TypedDict):
    account: str
    date: str
    description: str
    amount: float
    balance: float
