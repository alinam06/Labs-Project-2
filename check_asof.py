"""Live acceptance checks: .venv/bin/python check_asof.py

Uses actual FRED / ALFRED downloads, never substitute observations.
"""
from datetime import date
import math

import pandas as pd

from asof_app import comparison, download_asof, download_today


def main():
    today = date.today()
    expected = {
        "BAA": ("2026-09-01", 6.47),
        "FEDFUNDS": ("2026-09-01", 3.75),
        "DGS10": ("2026-10-02", 5.28),
        "MORTGAGE30US": ("2026-10-01", 7.28),
    }
    failures = []
    for series_id, (last_date, value) in expected.items():
        try:
            vintage = download_asof(series_id, date(2026, 10, 5), today)
            actual = (vintage.index[-1].strftime("%Y-%m-%d"), float(vintage.iloc[-1]))
            passed = actual[0] == last_date and math.isclose(actual[1], value, abs_tol=1e-9)
            print(f'{"PASS" if passed else "FAIL"} {series_id}: {actual}; expected {(last_date, value)}')
            if not passed:
                failures.append(series_id)
        except Exception as exc:
            print(f"ERROR {series_id}: {exc}")
            failures.append(series_id)
    try:
        vintage = download_asof("PAYEMS", date(2025, 1, 15), today)
        current = download_today("PAYEMS", today)
        december = pd.Timestamp("2024-12-01")
        revisions = comparison("PAYEMS", current, vintage)["Revised values on shared dates"]
        print(f"PAYEMS: last date {vintage.index[-1].date()}, value {vintage.iloc[-1]:,.0f}; "
              f"December 2024 today {current.loc[december]:,.0f}; revised dates {revisions:,}")
        passed = (vintage.index[-1] == december
                  and vintage.iloc[-1] == 159536
                  and current.loc[december] < vintage.loc[december]
                  and revisions > 10)
        print(f'{"PASS" if passed else "FAIL"} PAYEMS vintage and revisions probe')
        if not passed:
            failures.append("PAYEMS")
    except Exception as exc:
        print(f"ERROR PAYEMS: {exc}")
        failures.append("PAYEMS")
    if failures:
        raise SystemExit("Not verified: " + ", ".join(failures))
    print("All live acceptance checks passed.")


if __name__ == "__main__":
    main()
