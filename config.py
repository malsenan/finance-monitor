import os

_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _load_env_file(path: str) -> None:
    """
    Populates os.environ from a KEY=VALUE file.

    Real environment variables take precedence, so values can be overridden without
    editing the file. Blank lines and lines starting with '#' are ignored.
    """
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _require(key: str) -> str:
    """Returns the named setting, or raises if it is missing or blank."""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"Missing required setting '{key}'. Copy .env.example to .env and fill it in."
        )
    return value


_load_env_file(_ENV_PATH)

# Root directory holding the exported statement files (see README for the expected layout)
DATA_DIR = _require("FINANCE_DATA_DIR")
# Where the parsed CSVs and stats.txt are written
PARSED_DATA_DIR = os.path.join(DATA_DIR, "parsed_data")

# Filename suffix identifying the credit account's exported CSVs (ex: "_1234.csv")
CREDIT_FILE_SUFFIX = _require("CREDIT_FILE_SUFFIX")

# Account-name prefix the 401k provider uses to label employer plan rows
RETIREMENT_ACCOUNT_PREFIX = _require("RETIREMENT_ACCOUNT_PREFIX")

# Gross annual income, used as the savings rate denominator
ANNUAL_INCOME = float(_require("ANNUAL_INCOME"))

# Monthly spending limits drawn as a reference line on the income vs. spending charts
MONTHLY_SPENDING_LIMIT = float(_require("MONTHLY_SPENDING_LIMIT"))
CREDIT_SPENDING_LIMIT = float(_require("CREDIT_SPENDING_LIMIT"))
