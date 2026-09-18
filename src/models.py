from typing import TypedDict


class BankTransaction(TypedDict):
    date: str
    account: str
    description: str
    amount: float
    balance: float

class FidelityTransaction(TypedDict):
    date: str
    account: str
    symbol: str
    description: str
    quantity: float
    price_per_share: float
    ending_value: float
    cost_basis: float
