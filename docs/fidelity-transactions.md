# Fidelity transaction history

The only Fidelity input is `$FINANCE_DATA_DIR/fidelity/fidelityTransactions.csv`. It has the same columns as the `Accounts_History.csv` download from Fidelity's Activity & Orders tab and covers every account: the 401k plans, the Roth IRA and the individual account. Rows are newest first, the file goes back to each account's first deposit, and new downloads are pasted at the top.

**Every row in this document is made up.** Each one copies the layout of a real export row, but the names, account numbers, dates and amounts are invented (see "Data privacy" in `CLAUDE.md`).

**Status:** this describes the planned parser rewrite. `src/parsers.py` doesn't work this way yet.

## Columns

```
Run Date,Account,Account Number,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Settlement Date
```

- `Run Date` is the row's date. `Settlement Date` isn't used.
- `Commission ($)`, `Fees ($)` and `Accrued Interest ($)` have been blank in every row seen so far. Fees come as their own rows instead.
- Fields containing a comma are quoted (`"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN"`), and negative numbers often are too (`"-0.004"`). `csv.DictReader` handles both.
- A blank field is written either as nothing or as `""`. Both read as an empty string.
- `Quantity` has 3 decimal places. Don't read it with `safe_float`, which rounds to 2 and turns `-0.004` into `0`.

## Two row formats

Which format a row uses depends on its account, looked up by `Account Number` in `.env`.

| Column | 401k rows | Brokerage rows (Roth IRA, individual) |
|---|---|---|
| `Symbol` | Blank. The fund's name is in `Description` | Ticker on fund rows, blank on cash-only rows |
| `Type` | Blank | `Cash` |
| `Price ($)` | Blank | Trade price on buys and reinvestments, blank otherwise |
| `Quantity` | Shares added (+) or removed (−), 0 if none | Same |
| `Amount ($)` | Change in the fund: + money in, − money out | Change in the account's cash: + cash in, − cash spent |

`Amount ($)` is the reason the parser has to know each account's format: a 401k contribution and a brokerage buy both add shares, but their amounts have opposite signs.

## Row types

### 401k: `Contributions`

```
05/15/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,Contributions,,FUND A,,,10,,,,470,
11/13/2024,EMPLOYER B 401(K) PLAN,22222,Contributions,,FUND B,,,12.47,,,,498.8,
```

- **Meaning:** money added to a fund. It can be a paycheck contribution or a rollover from another plan (the second row). Both use the same Action.
- **Calculation:**
  - Shares += `Quantity`.
  - Cost basis += `Amount`.
  - Price = `Amount / Quantity` (470 / 10 = 47.00).
- **Used for:** fund value and cost basis. Later, the retirement contributions chart.

### 401k: `Withdrawals`

```
11/12/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,Withdrawals,,FUND A,,,"-9.976",,,,"-498.8",
```

- **Meaning:** money leaving the plan, such as a rollover to a new employer's plan.
- **Calculation:**
  - Shares += `Quantity` (negative).
  - Cost basis −= average cost per share × shares removed.
  - Price = `Amount / Quantity` (498.80 / 9.976 = 50.00).
- **Used for:** fund value and cost basis. Without it, a rolled-over plan would keep counting toward net worth on top of the new plan.

### 401k: `RECORDKEEPING FEE` and `ADVISOR / CONSULTANT FEE`

```
07/01/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,RECORDKEEPING FEE,,FUND A,,,"-0.02",,,,"-0.96",
07/02/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,ADVISOR / CONSULTANT FEE,,FUND A,,,"-0.004",,,,"-0.19",
```

- **Meaning:** plan fees, paid by selling a small number of shares of each fund.
- **Calculation:**
  - Shares += `Quantity` (negative).
  - Cost basis −= average cost per share × shares removed.
  - The price isn't taken from these rows. `Quantity` is rounded to 3 decimals, so `-0.004` could be anywhere from −0.0035 to −0.0045 shares. The implied price of 0.19 / 0.004 = 47.50 could really be anything from 42.22 to 54.29.

### 401k: `Change in Market Value`

```
07/01/2024,"EMPLOYER A, INC 401(K) PROFIT SHARING PLAN",11111,Change in Market Value,,FUND A,,,0,,,,0.02,
```

- **Meaning:** not confirmed. It has only appeared in the old employer's plan, and in every sample it shares a date and fund with a fee or withdrawal row.
- **Calculation:** none. `Quantity` is always 0, so it changes neither shares nor cost basis. The fund's value comes from shares × price instead.

### Brokerage: `CASH CONTRIBUTION CURRENT YEAR (Cash)`

```
02/04/2025,ROTH IRA,X22222222,CASH CONTRIBUTION CURRENT YEAR (Cash),"",No Description,Cash,"",0,"","","",100,""
```

- **Meaning:** a Roth IRA contribution counted toward the current tax year. A contribution for the previous tax year (allowed until the filing deadline) hasn't appeared in a sample yet.
- **Calculation:** cash += `Amount`.
- **Used for:** account value. Later, Roth contributions vs. the annual limit.

### Brokerage: `Electronic Funds Transfer Received (Cash)`

```
01/06/2025,Individual,X11111111,Electronic Funds Transfer Received (Cash),"",No Description,Cash,"",0,"","","",100,""
```

- **Meaning:** a deposit from a bank account.
- **Calculation:** cash += `Amount`.

### Brokerage: `YOU BOUGHT PERIODIC INVESTMENT ... (FXAIX) (Cash)`

```
02/03/2025,Individual,X11111111,YOU BOUGHT PERIODIC INVESTMENT FIDELITY 500 INDEX FUND (FXAIX) (Cash),FXAIX,FIDELITY 500 INDEX FUND,Cash,260,0.385,"","","","-100",02/04/2025
```

- **Meaning:** a scheduled automatic purchase.
- **Calculation:**
  - Shares += `Quantity`.
  - Cost basis += −`Amount`.
  - Cash += `Amount`.
  - Price = `Price ($)`.
- **Note:** the buy's `Run Date` can be a day before the deposit that pays for it, so cash dips below zero for that day (see the worked example).

### Brokerage: `DIVIDEND RECEIVED ... (SPAXX) (Cash)`

```
01/31/2025,Individual,X11111111,DIVIDEND RECEIVED FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash),SPAXX,FIDELITY GOVERNMENT MONEY MARKET,Cash,"",0,"","","",0.25,""
```

- **Meaning:** SPAXX's monthly dividend (see "What SPAXX is" below).
- **Calculation:** cash += `Amount`. `Price ($)` is blank, so the price is left as it was. It must not be set to 0.
- **Used for:** account value. Later, the dividend income chart.

### Brokerage: `REINVESTMENT ... (SPAXX) (Cash)`

```
01/31/2025,Individual,X11111111,REINVESTMENT FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash),SPAXX,FIDELITY GOVERNMENT MONEY MARKET,Cash,1,0.25,"","","","-0.25",""
```

- **Meaning:** the dividend automatically buys more SPAXX.
- **Calculation:** same as a buy.
  - Shares += `Quantity`.
  - Cost basis += −`Amount`.
  - Cash += `Amount`.
  - Price = `Price ($)`.

### What SPAXX is

SPAXX is Fidelity's government money market fund and the default "core position": uninvested cash in the Roth IRA and individual account sits in it.
- Its price is fixed at 1.00.
- It pays a small dividend every month, which gets reinvested automatically.

In these calculations, deposited cash stays "cash" and only reinvested dividends become SPAXX shares. Fidelity shows both as SPAXX, but the account total comes out the same.

## Rules

The rules only look at the signs of `Quantity` and `Amount ($)`. An Action that isn't listed here should still work as long as its signs follow the same pattern. The one exception is 401k prices, which only come from `Contributions` and `Withdrawals`.

**401k, per plan and fund**
- Shares: running total of `Quantity`.
- Cost basis: a row with `Quantity` > 0 adds `Amount`. A row with `Quantity` < 0 removes average cost × shares removed.
- Price: `Amount / Quantity` from the latest `Contributions` or `Withdrawals` row.
- Value: shares × price. A plan's value is the sum of its funds' values.

**Brokerage, per account**
- Cash: running total of `Amount` over every row in the account.
- For each `Symbol`:
  - Shares: running total of `Quantity`.
  - Cost basis: a row with `Quantity` > 0 adds −`Amount`. A row with `Quantity` < 0 removes average cost × shares removed.
  - Price: the latest non-blank `Price ($)`.
- Value: cash + the sum of shares × price.

Every total depends on the file going back to each account's first deposit, and on no row appearing twice.

## Worked examples

Rows are replayed oldest first, using the sample rows above.

**401k: FUND A in EMPLOYER A's plan**

| Run Date | Row | Shares | Price | Cost basis | Value |
|---|---|---|---|---|---|
| 05/15/2024 | Contributions: 10 shares for 470 | 10.000 | 47.00 | 470.00 | 470.00 |
| 07/01/2024 | RECORDKEEPING FEE: −0.02 shares, −0.96 | 9.980 | 47.00 | 469.06 | 469.06 |
| 07/01/2024 | Change in Market Value: 0.02 | 9.980 | 47.00 | 469.06 | 469.06 |
| 07/02/2024 | ADVISOR / CONSULTANT FEE: −0.004 shares, −0.19 | 9.976 | 47.00 | 468.87 | 468.87 |
| 11/12/2024 | Withdrawals: −9.976 shares, −498.80 | 0.000 | 50.00 | 0.00 | 0.00 |

The price stays at 47.00 from May to November because none of the rows in between is a contribution or withdrawal. Just before the withdrawal the fund was really worth 498.80, but the table shows 468.87.

**Individual account**

| Run Date | Row | Cash | FXAIX shares | FXAIX price | SPAXX shares | Account value |
|---|---|---|---|---|---|---|
| 01/06/2025 | Deposit 100 | 100.00 | 0.000 | – | 0.00 | 100.00 |
| 01/07/2025 | Bought 0.4 FXAIX at 250 | 0.00 | 0.400 | 250.00 | 0.00 | 100.00 |
| 01/31/2025 | SPAXX dividend 0.25 | 0.25 | 0.400 | 250.00 | 0.00 | 100.25 |
| 01/31/2025 | Reinvested 0.25 into SPAXX at 1 | 0.00 | 0.400 | 250.00 | 0.25 | 100.25 |
| 02/03/2025 | Bought 0.385 FXAIX at 260 | −100.00 | 0.785 | 260.00 | 0.25 | 104.35 |
| 02/04/2025 | Deposit 100 | 0.00 | 0.785 | 260.00 | 0.25 | 204.35 |

At the end, FXAIX's cost basis is 200.00 and SPAXX's is 0.25. The 104.35 on 02/03 is the one-day dip: the buy ran before its deposit arrived.

## Known limits

- A fund's value only changes when a row gives it a new price:
  - FXAIX gets one on every periodic buy, and SPAXX is always 1.00, so the Roth IRA and individual account stay close to their real value.
  - A 401k fund gets one on every paycheck contribution. A plan that stops receiving contributions keeps its last price until a withdrawal.
- Cash can go negative for a day when a buy runs before its deposit.
- A row pasted twice, for example from overlapping download date ranges, is counted twice.

## Not known yet

- Action types not covered here, such as sells, exchanges between 401k funds, 401k dividends, or transfers between accounts.
- What `Change in Market Value` measures.
- How an IRA contribution for the previous tax year is labeled.

## Where the numbers go

Each fund's value and cost basis become the `ending_value` and `cost_basis` of the holdings rows described under "Fidelity Holdings" in the README's Field Reference. From there they feed:
- the Fidelity balances included in net worth over time
- the monthly savings rate chart
- the Fidelity charts
- the return % per holding section of `stats.txt`

Contributions and dividends will feed the planned retirement contributions and dividend income charts (see the README's TODO list).
