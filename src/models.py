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
    price: float 
    beginning_value: float
    ending_value: float
    cost_basis: float
