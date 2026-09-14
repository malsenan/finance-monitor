# Fidelity transaction history

The only Fidelity input is `$FINANCE_DATA_DIR/fidelity/fidelityTransactions.csv`. It has the same columns as the `Accounts_History.csv` download from Fidelity's Activity & Orders tab and covers every account: the 401k plans, the Roth IRA and the individual account. Rows are newest first, the file goes back to each account's first deposit, and new downloads are pasted at the top.

**Every row in this document is made up.** Each one copies the layout of a real export row, but the names, account numbers, dates and amounts are invented (see "Data privacy" in `CLAUDE.md`).

**Status:** this describes the planned `parse_fidelity_transactions` (see the "Rewrite Fidelity parsing" ticket in the README). `src/parsers.py` doesn't work this way yet.

## Columns

```
Run Date,Account,Account Number,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Settlement Date
```

- `Run Date` is the row's date. `Settlement Date` isn't used.
- `Commission ($)`, `Fees ($)` and `Accrued Interest ($)` have been blank in every row seen so far. Fees come as their own rows instead.
- Fields containing a comma are quoted (`"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN"`), and negative numbers often are too (`"-0.004"`). `csv.DictReader` handles both.
- A blank field is written either as nothing or as `""`. Both read as an empty string.
- `Quantity` has 3 decimal places. Read numbers with `float`, not `safe_float`: `safe_float` rounds to 2 decimals (turning `-0.004` into `0`) and turns unreadable values into `0` without an error.

## Old layout (not supported)

Older exports wrote 401k rows differently, so `fidelityTransactions.csv` was rebuilt from fresh downloads. An old-layout row looks like this:

```
03/01/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN","11111","RECORDKEEPING FEE",,"FUND A",,-0.05,,,,,-2.35,,
```

- The share count sits under `Price ($)`, and `Quantity` is blank.
- The row has 15 fields against the 14-column header.
- Text fields are quoted and negative numbers aren't, the reverse of current exports.

The date doesn't tell the layouts apart: the same transaction comes out in either layout depending on when it was downloaded. The parser only supports the current layout.

## Two row formats

| Column | 401k rows | Brokerage rows (Roth IRA, individual) |
|---|---|---|
| `Symbol` | Blank. The fund's name is in `Description` | Ticker on fund rows, blank on cash-only rows |
| `Type` | Blank | `Cash` |
| `Price ($)` | Blank | Trade price on buys and reinvestments, blank otherwise |
| `Quantity` | Shares added (+) or removed (−), 0 if none | Same |
| `Amount ($)` | Change in the fund: + money in, − money out | Change in the account's cash: + cash in, − cash spent |

The parser doesn't need to know which format an account uses. `Amount ($)` has opposite signs in the two formats, but the rules below only use its size, and they skip the cash-only rows where its meaning differs.

## Row types

### 401k: `Contributions`

```
05/15/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,Contributions,,FUND A,,,10,,,,470,
11/13/2024,EMPLOYER B 401(K) PLAN,22222,Contributions,,FUND B,,,12.47,,,,498.8,
```

- **Meaning:** money added to a fund. It can be a paycheck contribution or a rollover from another plan (the second row). Both use the same Action.
- **Calculation:**
  - Shares += `Quantity`.
  - Cost basis += |`Amount`|.
  - Price = |`Amount / Quantity`| (470 / 10 = 47.00).
- **Used for:** fund value and cost basis. Later, the retirement contributions chart.

### 401k: `Withdrawals`

```
11/12/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,Withdrawals,,FUND A,,,"-9.976",,,,"-498.8",
```

- **Meaning:** money leaving the plan, such as a rollover to a new employer's plan.
- **Calculation:**
  - Cost basis −= average cost per share × shares removed.
  - Shares += `Quantity` (negative).
  - Price = |`Amount / Quantity`| (498.80 / 9.976 = 50.00).
- **Used for:** fund value and cost basis. Without it, a rolled-over plan would keep counting toward net worth on top of the new plan.

### 401k: `RECORDKEEPING FEE` and `ADVISOR / CONSULTANT FEE`

```
07/01/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,RECORDKEEPING FEE,,FUND A,,,"-0.02",,,,"-0.96",
07/02/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,ADVISOR / CONSULTANT FEE,,FUND A,,,"-0.004",,,,"-0.19",
```

- **Meaning:** plan fees, paid by selling a small number of shares of each fund.
- **Calculation:**
  - Cost basis −= average cost per share × shares removed.
  - Shares += `Quantity` (negative).
  - The price isn't taken from these rows. `Quantity` is rounded to 3 decimals, so `-0.004` could be anywhere from −0.0035 to −0.0045 shares. The implied price of 0.19 / 0.004 = 47.50 could really be anything from 42.22 to 54.29.

### 401k: `Change in Market Value`

```
07/01/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,Change in Market Value,,FUND A,,,0,,,,0.02,
```

- **Meaning:** not confirmed. It has only appeared in the old employer's plan, and in every sample it shares a date and fund with a fee or withdrawal row.
- **Calculation:** skipped. `Quantity` is always 0.

### Brokerage: `CASH CONTRIBUTION CURRENT YEAR (Cash)`

```
02/04/2025,ROTH IRA,X22222222,CASH CONTRIBUTION CURRENT YEAR (Cash),"",No Description,Cash,"",0,"","","",100,""
```

- **Meaning:** a Roth IRA contribution counted toward the current tax year. A contribution for the previous tax year (allowed until the filing deadline) hasn't appeared in a sample yet.
- **Calculation:** skipped (`Quantity` is 0). The money is counted once a buy puts it into a fund.
- **Used for:** later, Roth contributions vs. the annual limit.

### Brokerage: `Electronic Funds Transfer Received (Cash)`

```
01/06/2025,Individual,X11111111,Electronic Funds Transfer Received (Cash),"",No Description,Cash,"",0,"","","",100,""
02/04/2025,Individual,X11111111,Electronic Funds Transfer Received (Cash),"",No Description,Cash,"",0,"","","",100,""
```

- **Meaning:** a deposit from a bank account.
- **Calculation:** skipped (`Quantity` is 0). The money is counted once a buy puts it into a fund.

### Brokerage: `YOU BOUGHT PERIODIC INVESTMENT ... (FXAIX) (Cash)`

```
01/07/2025,Individual,X11111111,YOU BOUGHT PERIODIC INVESTMENT FIDELITY 500 INDEX FUND (FXAIX) (Cash),FXAIX,FIDELITY 500 INDEX FUND,Cash,250,0.4,"","","","-100",01/08/2025
02/03/2025,Individual,X11111111,YOU BOUGHT PERIODIC INVESTMENT FIDELITY 500 INDEX FUND (FXAIX) (Cash),FXAIX,FIDELITY 500 INDEX FUND,Cash,260,0.385,"","","","-100",02/04/2025
```

- **Meaning:** a scheduled automatic purchase. Its `Run Date` can be a day before the deposit that pays for it.
- **Calculation:**
  - Shares += `Quantity`.
  - Cost basis += |`Amount`|.
  - Price = `Price ($)`.

### Brokerage: `DIVIDEND RECEIVED ... (SPAXX) (Cash)`

```
01/31/2025,Individual,X11111111,DIVIDEND RECEIVED FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash),SPAXX,FIDELITY GOVERNMENT MONEY MARKET,Cash,"",0,"","","",0.25,""
```

- **Meaning:** SPAXX's monthly dividend (see "What SPAXX is" below).
- **Calculation:** skipped (`Quantity` is 0). The reinvestment row that follows adds the shares.
- **Used for:** later, the dividend income chart.

### Brokerage: `REINVESTMENT ... (SPAXX) (Cash)`

```
01/31/2025,Individual,X11111111,REINVESTMENT FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash),SPAXX,FIDELITY GOVERNMENT MONEY MARKET,Cash,1,0.25,"","","","-0.25",""
```

- **Meaning:** the dividend automatically buys more SPAXX.
- **Calculation:** same as a buy.
  - Shares += `Quantity`.
  - Cost basis += |`Amount`|.
  - Price = `Price ($)`.

### What SPAXX is

SPAXX is Fidelity's government money market fund and the default "core position": uninvested cash in the Roth IRA and individual account sits in it.
- Its price is fixed at 1.00.
- It pays a small dividend every month, which gets reinvested automatically.

Reinvested dividends show up as SPAXX shares, so they're counted. Deposited cash waiting for a buy doesn't have its own SPAXX row, so it isn't (see "Known limits").

## Rules

The same rules apply to every account. Rows are replayed oldest first, per account and fund. The fund is `Symbol`, or `Description` when `Symbol` is blank.

- A row with `Quantity` 0 is skipped.
- A row with `Quantity` > 0 adds `Quantity` to shares and |`Amount`| to cost basis.
- A row with `Quantity` < 0 removes average cost × shares removed from cost basis, then adds `Quantity` to shares.
- Price is `Price ($)` when it's filled in. Otherwise it's |`Amount / Quantity`|, taken only from `Contributions` and `Withdrawals` rows.
- A fund's value is shares × price. An account's value is the sum of its funds' values.

Every total depends on the file going back to each account's first deposit, and on no row appearing twice.

## Assumptions

The parser has no error handling. It assumes the file is well-formed and valid:
- the columns above, in the current layout
- readable numbers
- rows newest first
- every account number listed in `.env`
- only Actions whose `Quantity` and `Amount ($)` follow the rules above

Input that breaks these shows up as an ordinary Python error or as wrong numbers. When a new Action appears, it gets added under "Row types" with a sample row once its effect on shares has been checked.

## Output

After each day's rows, the parser writes:

- **One holdings row per fund that changed that day:** `date`, `account` (`<label> - <fund>`), `symbol` (the fund), `description` (the day's last Action for that fund), `quantity`, `price_per_share`, `ending_value`, `cost_basis`.
- **One summary row per account that changed that day:** `date`, `account` (the label), `ending_mkt_value` (the account's value).

Values are rounded on output: 2 decimals for money and prices, 3 for shares. Both lists are newest first. Labels come from `.env`: `FIDELITY_ACCOUNT_<LABEL>=<account number>`, so outputs never show Fidelity's account names or numbers.

**Why one row per fund per day:** `src/main.py` sets each Fidelity balance to the sum of `ending_value` over every holdings row with the same date and account. A second row for a fund on the same day, like two fees or two contributions on one payday, would count that fund twice.

## Worked examples

Rows are replayed oldest first, using the sample rows above.

**401k: FUND A in EMPLOYER A's plan**

| Run Date | Row | Shares | Price | Cost basis | Value |
|---|---|---|---|---|---|
| 05/15/2024 | Contributions: 10 shares for 470 | 10.000 | 47.00 | 470.00 | 470.00 |
| 07/01/2024 | RECORDKEEPING FEE: −0.02 shares, −0.96 | 9.980 | 47.00 | 469.06 | 469.06 |
| 07/01/2024 | Change in Market Value: 0.02 (skipped) | 9.980 | 47.00 | 469.06 | 469.06 |
| 07/02/2024 | ADVISOR / CONSULTANT FEE: −0.004 shares, −0.19 | 9.976 | 47.00 | 468.87 | 468.87 |
| 11/12/2024 | Withdrawals: −9.976 shares, −498.80 | 0.000 | 50.00 | 0.00 | 0.00 |

The output has one row per day: 05/15, 07/01, 07/02 and 11/12. The price stays at 47.00 from May to November because none of the rows in between is a contribution or withdrawal. Just before the withdrawal the fund was really worth 498.80, but the table shows 468.87.

**Individual account**

| Run Date | Row | FXAIX shares | FXAIX price | FXAIX cost basis | SPAXX shares | Account value |
|---|---|---|---|---|---|---|
| 01/06/2025 | Deposit 100 (skipped) | 0.000 | – | 0.00 | 0.00 | 0.00 |
| 01/07/2025 | Bought 0.4 FXAIX at 250 for 100 | 0.400 | 250.00 | 100.00 | 0.00 | 100.00 |
| 01/31/2025 | SPAXX dividend 0.25 (skipped) | 0.400 | 250.00 | 100.00 | 0.00 | 100.00 |
| 01/31/2025 | Reinvested 0.25 into SPAXX at 1 | 0.400 | 250.00 | 100.00 | 0.25 | 100.25 |
| 02/03/2025 | Bought 0.385 FXAIX at 260 for 100 | 0.785 | 260.00 | 200.00 | 0.25 | 204.35 |
| 02/04/2025 | Deposit 100 (skipped) | 0.785 | 260.00 | 200.00 | 0.25 | 204.35 |

The summary rows are 01/07 (100.00), 01/31 (100.25) and 02/03 (204.35). SPAXX's cost basis ends at 0.25. On 01/06 the account really held the 100 deposit, but it shows 0 until the buy on 01/07.

## Known limits

- A fund's value only changes when a row gives it a new price:
  - FXAIX gets one on every periodic buy, and SPAXX is always 1.00, so the Roth IRA and individual account stay close to their real value.
  - A 401k fund gets one on every paycheck contribution. A plan that stops receiving contributions keeps its last price until a withdrawal.
- Money that isn't in a fund isn't counted: a deposit until its buy runs, or sale proceeds until they're reinvested.
- A row pasted twice, for example from overlapping download date ranges, is counted twice.

## Not known yet

- Action types not covered here, such as sells, exchanges between 401k funds, 401k dividends, or transfers between accounts. The rules would apply to them through the signs of `Quantity` and `Amount ($)`, but that hasn't been checked against real rows.
- What `Change in Market Value` measures.
- How an IRA contribution for the previous tax year is labeled.

## Where the numbers go

The holdings rows' `ending_value` and `cost_basis` feed:
- the Fidelity balances included in net worth over time
- the monthly savings rate chart
- the Fidelity charts
- the return % per holding section of `stats.txt`

The summary rows' `ending_mkt_value` feeds the total and per-account portfolio charts. Contributions and dividends will feed the planned retirement contributions and dividend income charts (see the README's TODO list).
