from typing import TypedDict


class Transaction(TypedDict):
    account: str
    date: str
    description: str
    amount: float
    balance: float
