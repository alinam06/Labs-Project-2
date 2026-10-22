# Lab 15: Portfolio comparison and partner exercise

## Data and rules

Status: awaiting `prices.csv`; no historical-price results have been calculated for this exercise.

- Price file and date range: pending.
- Annual objective: 6.50% proposed; keep it fixed for both runs, including when no mix qualifies.
- Reserve minimum: 3.00% proposed; confirm the eligible tickers before running.
- Reserve-eligible assets: pending confirmation. `PREPARATION.md` specifies SGOV only for the CSV universe; the app initially ticks SGOV and IEF. Untick IEF if following that preparation rule.
- Search: fully invested, long-only weights in 5-percentage-point steps.

## All monthly returns

Not run: `prices.csv` is not present in the project folder.

Record the number of monthly returns, each asset's weight, expected annual return, annual volatility and reserve-eligible weight. If infeasible, record exactly: "no mix meets the objective".

## Last 36 monthly returns

Not run: awaiting the same price file and confirmed reserve rule.

Keep the objective and reserve rule unchanged. Switch on "Use last 36 months" and record the scenario answer, including the same metrics or "no mix meets the objective". The app's right-hand loaded-input comparison remains based on all months.

## Largest weight change

Pending both runs. If both have a mix, record the asset with the largest absolute weight difference and the change in percentage points, from all months to the last 36 months. Otherwise record that the comparison is unavailable because at least one run has no qualifying mix.

## Six-minute explanation with partner — no AI

Open `search_lowest_volatility()` in `portfolio.py`. Explain the function line by line, answer one question from your partner using the code, and swap roles.

- Partner's actual question: to be recorded after the exchange.
- My answer from the code: to be recorded after the exchange.
- A line I could not explain / my next question for AI: to be recorded if needed.

## Partner attack

Have your partner change the expected-return estimate they distrust most and read the resulting answer aloud. Keep the objective and reserve rule fixed. Record the asset, original estimate, changed estimate, estimation window and resulting mix or infeasibility.

Two-sentence response: to be written after the actual partner test. In the first sentence, report the changed estimate and resulting answer; in the second, explain what the change shows about the portfolio's sensitivity to that estimate.

Swap roles after recording the response.

## Project 2 starting-allocation decision

Provisional call — reject the app's mix as the Project 2 starting allocation for now: the CSV-based results, price-source record and actual partner attack are still missing. Change this call to pilot only after the prices are sourced and dated, the reserve rule is confirmed, both estimation windows are reported at the unchanged objective, and the partner test is documented and its allocation sensitivity is explained. This is a decision about readiness for the project, not a completed evaluation of a particular allocation.

After completing those checks, replace the provisional call with my own adopt, pilot or reject decision, naming the observed weight change and the specific evidence or condition that would change my decision. Do not use the assignment's illustrative Meridian numbers as my results.

## Estimation risk — independent learning and reflection

The assignment asks for independent learning and an explanation in my own words. Complete these prompts after examining the actual results:

1. What is estimation risk? Distinguish an estimated expected return from a known future return.
2. Why can a small expected-return change cause a large allocation change? Look at the return constraint in `search_lowest_volatility()`: how does a changed estimate affect which mixes qualify, and which qualifying mix has the lowest volatility? Remember that this engine chooses among discrete 5-point mixes.
3. Explain the effect using my largest observed weight change. Name the asset, both weights, the change in percentage points, and whether it came from changing the estimation window or a partner's return edit. Do not treat a percentage-point weight change as a percent return change.
4. Why did my lowest-risk mix move as far as it did? Explain which estimates changed and how that affected the qualifying mixes; do not claim a cause the results do not establish.
5. What would I need to see before adopting it? State a concrete check or approval and why it would address the sensitivity I observed.

My independent explanation and reflection: pending completion of the data comparison and partner exercise.

## Submission floor and GitHub checkout

- [x] Original Meridian console report remains unchanged after adding the functions.
- [x] App calls the shared portfolio engine; return and reserve edits change the scenario.
- [ ] Reproduce the assignment's two specified Meridian runs and record both inputs and results. The second run must be identified before claiming this check is complete.
- [ ] Include actual price data, provider/source, retrieval date, observation dates and adjusted-price basis. Do not claim a download that has not occurred.
- [ ] Record all-month and last-36-return answers using the same objective and reserve rule.
- [ ] Record the largest weight change when both runs are feasible.
- [ ] Complete the line-by-line explanation and actual partner question.
- [ ] Answer the actual partner attack in two sentences.
- [ ] Finalize my individual starting-allocation decision and condition for changing it.
- [ ] Complete my independent estimation-risk explanation and reflection.
- [ ] Submit individually on GitHub and verify the submitted files.

GitHub status: this project folder is not a Git repository and has no configured remote. No GitHub submission has been made. The destination repository and the course's checkout requirements are still needed.
