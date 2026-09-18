import os

from parsers import parse_fidelity_transactions

# Made-up rows from docs/fidelity-transactions.md; expected values come from its worked examples
FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "fidelityTransactions.csv")
ACCOUNT_LABELS = {
    "11111": "EMPLOYER_A_401K",
    "22222": "EMPLOYER_B_401K",
    "X11111111": "INDIVIDUAL",
    "X22222222": "ROTH_IRA",
}


def test_401k_worked_example():
    _, holdings = parse_fidelity_transactions(FIXTURE, ACCOUNT_LABELS)

    fund_a = [(h["date"], h["quantity"], h["price_per_share"], h["cost_basis"], h["ending_value"])
              for h in holdings if h["account"] == "EMPLOYER_A_401K - FUND A"]
    # One row per day, newest first: fees don't move the price, and Change in Market Value is skipped
    assert fund_a == [
        ("11/12/2024", 0.0, 50.0, 0.0, 0.0),
        ("07/02/2024", 9.976, 47.0, 468.87, 468.87),
        ("07/01/2024", 9.98, 47.0, 469.06, 469.06),
        ("05/15/2024", 10.0, 47.0, 470.0, 470.0),
    ]


def test_individual_account_worked_example():
    summaries, holdings = parse_fidelity_transactions(FIXTURE, ACCOUNT_LABELS)

    funds = [(h["date"], h["symbol"], h["quantity"], h["price_per_share"], h["cost_basis"])
             for h in holdings if h["account"].startswith("INDIVIDUAL - ")]
    # Deposits and the dividend don't move shares, so only the buys and the reinvestment write rows
    assert funds == [
        ("02/03/2025", "FXAIX", 0.785, 260.0, 200.0),
        ("01/31/2025", "SPAXX", 0.25, 1.0, 0.25),
        ("01/07/2025", "FXAIX", 0.4, 250.0, 100.0),
    ]
    assert [(s["date"], s["ending_mkt_value"]) for s in summaries if s["account"] == "INDIVIDUAL"] == [
        ("02/03/2025", 204.35),
        ("01/31/2025", 100.25),
        ("01/07/2025", 100.0),
    ]
