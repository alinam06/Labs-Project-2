# FIN 439 Lab 16 — Provenance Gate

## D — Question

On the day you would have traded, what did this data actually say — and how much of what you see now came later?

Decision date: **March 31, 2026**, inclusive. The input is the supplied 12-row fictional table of one-year zero-coupon bond funds rated AAA, BBB and CCC. These labels represent ratings in this exercise, not actual traded fund identifiers.

## I — Code and run command

`asof.py` uses only the Python standard library. The editable decision date and complete training table are at the top. It computes all panels, removals and signals from those inputs; the professor's answers are not embedded as computed results.

From the `project 2` folder:

```sh
python3 Lab_16_Provenance_Gate/asof.py
```

Or, from the Lab 16 folder:

```sh
python3 asof.py
```

Use `python` instead if that command is configured on your computer. No packages or downloads are required. This training version reads the embedded table; it does not accept CSV command-line options. Thursday's ALFRED ingestion is a later extension.

### Four rules, in order

1. Quarantine the missing-ticker row and retain its original row number in the funnel.
2. Remove exact duplicates by comparing ticker, measured month, publication date and price; keep the first occurrence.
3. Remove publications later than the decision date.
4. Group survivors by ticker and measured month; keep the latest publication in each group.

`load_training_table()` parses the table, `remove_duplicates()` implements rule 2, `apply_rules()` runs the four steps, and `latest_vintages()` resolves revisions. `calculate_signals()` divides the latest month's price by the preceding calendar month's price, subtracts one and multiplies by 100. Missing previous-month prices produce `N/A` rather than a fabricated return.

The naive branch starts after rules 1 and 2, bypasses the cutoff and chooses each ticker/month's latest publication. It uses the same signal function as the as-of branch.

## V — Executed March 31 validation

All removed row IDs, remaining counts, final row IDs, signal months and rounded signals were checked against the professor's supplied answers. **All match.**

```text
FIN 439 Lab 16 — Provenance Gate
Decision date: 2026-03-31 (inclusive)

ROW FUNNEL
Starting rows: 12
1. Quarantined: no ticker: removed 1 | rows 11 | remaining 11
2. Exact duplicate: removed 1 | rows 7 | remaining 10
3. Published too late: removed 3 | rows 3, 8, 10 | remaining 7
4. Older vintage replaced: removed 1 | rows 2 | remaining 6

FINAL AS-OF PANEL
Row | Ticker | Month measured | Published on | Price
  1 | AAA    | 2026-01        | 2026-02-10   | 101.0
  4 | AAA    | 2026-02        | 2026-03-25   | 103.0
  5 | BBB    | 2026-01        | 2026-02-10   | 98.0
  6 | BBB    | 2026-02        | 2026-03-10   | 97.0
  9 | CCC    | 2026-01        | 2026-02-10   | 110.0
 12 | CCC    | 2026-02        | 2026-03-10   | 111.0

SIGNALS: (latest month price / previous month price - 1) * 100
Ticker | As-of month | As-of signal | Naive month | Naive signal
AAA    | 2026-02     |       +1.98% | 2026-03     |       +5.83%
BBB    | 2026-02     |       -1.02% | 2026-03     |       -5.15%
CCC    | 2026-02     |       +0.91% | 2026-02     |       +1.82%
Naive signals use the latest vintage regardless of the decision date.
```

### Why rule 4 matters

The dictionary key is `(ticker, month)`. For each record, `latest_vintages()` saves it if that key is new or its publication date is later than the currently saved record. It then returns the selected original rows and the rows they replaced.

For AAA February, row 4 (March 25, price 103) replaces row 2 (March 10, price 104). Both are available by March 31. Keeping row 2 would incorrectly give `(104 / 101 - 1) * 100 = +2.97%` instead of the correct `+1.98%`.

For CCC February, rule 3 first removes row 10, published April 5. Rule 4 therefore retains row 12 for the March 31 panel. Resolving revisions before enforcing availability could incorrectly select a future revision and lose the valid earlier vintage.

## Swap-and-break date test — executed

The April 15 test was performed programmatically using the same functions and printed main routine, without saving a changed cutoff. All three as-of signals exactly equal the naive signals. The saved file remains at **March 31, 2026**.

```text
FIN 439 Lab 16 — Provenance Gate
Decision date: 2026-04-15 (inclusive)

ROW FUNNEL
Starting rows: 12
1. Quarantined: no ticker: removed 1 | rows 11 | remaining 11
2. Exact duplicate: removed 1 | rows 7 | remaining 10
3. Published too late: removed 0 | rows none | remaining 10
4. Older vintage replaced: removed 2 | rows 2, 12 | remaining 8

FINAL AS-OF PANEL
Row | Ticker | Month measured | Published on | Price
  1 | AAA    | 2026-01        | 2026-02-10   | 101.0
  3 | AAA    | 2026-03        | 2026-04-10   | 109.0
  4 | AAA    | 2026-02        | 2026-03-25   | 103.0
  5 | BBB    | 2026-01        | 2026-02-10   | 98.0
  6 | BBB    | 2026-02        | 2026-03-10   | 97.0
  8 | BBB    | 2026-03        | 2026-04-10   | 92.0
  9 | CCC    | 2026-01        | 2026-02-10   | 110.0
 10 | CCC    | 2026-02        | 2026-04-05   | 112.0

SIGNALS: (latest month price / previous month price - 1) * 100
Ticker | As-of month | As-of signal | Naive month | Naive signal
AAA    | 2026-03     |       +5.83% | 2026-03     |       +5.83%
BBB    | 2026-03     |       -5.15% | 2026-03     |       -5.15%
CCC    | 2026-02     |       +1.82% | 2026-02     |       +1.82%
Naive signals use the latest vintage regardless of the decision date.
```

This verifies code behavior; it does not claim that the required partner swap has taken place. With a partner, edit the top-level date to `date(2026, 4, 15)`, run the file, observe equality, then undo the edit.

## Sanity check — separate from the four provenance rules

For the assignment's one-year zero-coupon funds, yield in percent is `(100 / price - 1) * 100`. These figures were independently calculated from the six retained prices and match the supplied hand-check answers. Recalculate them by hand for the classroom exercise.

| Row | Rating | Month | Price | Yield | Breaks |
| --- | --- | --- | --- | --- | --- |
| 1 | AAA | 2026-01 | 101.0 | -0.99% | negative yield |
| 4 | AAA | 2026-02 | 103.0 | -2.91% | negative yield |
| 5 | BBB | 2026-01 | 98.0 | +2.04% | nothing |
| 6 | BBB | 2026-02 | 97.0 | +3.09% | nothing |
| 9 | CCC | 2026-01 | 110.0 | -9.09% | negative yield; priced above AAA and BBB |
| 12 | CCC | 2026-02 | 111.0 | -9.91% | negative yield; priced above AAA and BBB |

The gate establishes timing, not economic plausibility. AAA and CCC prices exceed the maturity payment of 100, implying negative yields. CCC is also priced above both higher-rated funds, reversing the assignment's expected same-maturity credit-risk ordering.

A proposed fifth rule for this exercise would quarantine any price above 100 for review, catching rows 1, 4, 9 and 12. A separate same-month rating-order check would also flag CCC. These checks are intentionally **not** added to the four-rule panel: doing so would change the required known answer. Negative yields are a review flag under this exercise's assumptions, not proof that every negative-yield observation in real markets is false.

## Explain, learn and reflect — complete with partner

The assignment requires independent explanations and a real partner exchange. The following are prompts, not claims of completed participation:

- Explain the measured month versus publication date without a screen; swap roles.
- Explain `latest_vintages()` line by line. Record your partner's question and your answer from the code.
- Run your partner's script at March 31 and April 15; restore the original date.
- Explain look-ahead bias in your own words using event time, publication time and revisions.
- Use AAA to explain why the naive March signal was unavailable on March 31. Distinguish a different measurement window from a same-month revision.
- Choose which excluded or replaced row mattered most and justify your choice. Explain what a backtest using the naive column would assume it knew.
- Explain the proposed fifth sanity rule and why timing checks alone did not catch the planted prices.

Partner's actual question and my answer: **pending**.

My independent reflection: **pending**.

### AI quiz — answer before asking for an explanation

In `latest_vintages()`, why is the dictionary key `(record["ticker"], record["month"])` rather than just `record["ticker"]`? What would be lost if the month were omitted?

If another line is less clear, identify it and request a quiz about that line instead.

## Checkout

- [x] Standard-library script with editable inputs and preserved original row IDs.
- [x] Four-rule funnel and final panel match every known answer.
- [x] As-of and naive signal values and months match every known answer.
- [x] April 15 code check makes as-of equal naive, ticker for ticker; saved date is March 31.
- [x] Sanity-check calculations match the six supplied yields.
- [ ] Complete the actual partner explanation, question and swap-and-break exercise.
- [ ] Complete independent learning and reflection in my own words.
- [ ] Submit individually and supply actual GitHub links to `asof.py` and `LAB16.md`.

GitHub Python link: **pending publication**.

GitHub Markdown link: **pending publication**.

Only the Lab 16 files were changed for this update. Earlier labs and Netflix Project 1 files were not modified. This document records technical verification, not a claim of full classroom or GitHub completion.
