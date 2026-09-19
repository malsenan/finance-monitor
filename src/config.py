import os
from datetime import datetime

from dotenv import load_dotenv


def _require(key: str) -> str:
    """Returns the named setting, or raises if it is missing or blank."""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"Missing required setting '{key}'. Copy .env.example to .env and fill it in."
        )
    return value


# Finds .env in src/ or the repo root. Real environment variables take precedence over it
load_dotenv()

# Root directory holding the exported statement files (see README for the expected layout)
DATA_DIR = _require("FINANCE_DATA_DIR")
CREDIT_DIR = os.path.join(DATA_DIR, "bofa", "credit")
CHECKING_FILE = os.path.join(DATA_DIR, "bofa", "debit", "checkingTransactions.csv")
SAVINGS_FILE = os.path.join(DATA_DIR, "bofa", "savings", "savingsTransactions.csv")
FIDELITY_FILE = os.path.join(DATA_DIR, "fidelity", "fidelityTransactions.csv")

# Where the parsed CSVs and stats.txt are written
PARSED_DATA_DIR = os.path.join(DATA_DIR, "parsed_data")
PARSED_CREDIT_FILE = os.path.join(PARSED_DATA_DIR, "parsedCreditTransactions.csv")
PARSED_CHECKING_FILE = os.path.join(PARSED_DATA_DIR, "parsedCheckingTransactions.csv")
PARSED_SAVINGS_FILE = os.path.join(PARSED_DATA_DIR, "parsedSavingsTransactions.csv")
BANK_SUMMARIES_FILE = os.path.join(PARSED_DATA_DIR, "bankAccountSummaries.csv")
PARSED_FIDELITY_TRANSACTIONS_FILE = os.path.join(PARSED_DATA_DIR, "parsedFidelityTransactions.csv")
PARSED_FIDELITY_SUMMARIES_FILE = os.path.join(PARSED_DATA_DIR, "parsedFidelitySummaries.csv")
PARSED_FIDELITY_HOLDINGS_FILE = os.path.join(PARSED_DATA_DIR, "parsedFidelityHoldings.csv")
ALL_TRANSACTIONS_FILE = os.path.join(PARSED_DATA_DIR, "allParsedTransactions.csv")
STATS_FILE = os.path.join(PARSED_DATA_DIR, "stats.txt")

# Where each run's output is copied, into a new YYYY-MM-DD_HH-MM-SS folder per run
OLD_PARSED_DATA_DIR = os.path.join(DATA_DIR, "old_parsed_data")
# This run's backup folder, named by when the run started
BACKUP_DIR = os.path.join(OLD_PARSED_DATA_DIR, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# Filename suffix identifying the credit account's exported CSVs (ex: "_1234.csv")
CREDIT_FILE_SUFFIX = _require("CREDIT_FILE_SUFFIX")

# Fidelity account number -> label, from every FIDELITY_ACCOUNT_<LABEL>=<account number> setting
FIDELITY_ACCOUNTS = {number: key.removeprefix("FIDELITY_ACCOUNT_") for key, number in os.environ.items() if key.startswith("FIDELITY_ACCOUNT_")}

# Gross annual income, used as the savings rate denominator
ANNUAL_INCOME = float(_require("ANNUAL_INCOME"))

# Monthly spending limits drawn as a reference line on the income vs. spending charts
MONTHLY_SPENDING_LIMIT = float(_require("MONTHLY_SPENDING_LIMIT"))
CREDIT_SPENDING_LIMIT = float(_require("CREDIT_SPENDING_LIMIT"))
