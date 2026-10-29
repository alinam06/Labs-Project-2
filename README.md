# FRED / ALFRED Economic Data Explorer

A Streamlit app for comparing current economic observations with the data available on a historical date. Uses public FRED and ALFRED CSV downloads; no API key required.

## Run locally

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run asof_app.py
```

Open http://localhost:8501. Select series and dates in the sidebar. View the comparison table, inspect charts, or download CSV files. Use Streamlit's Settings menu to change between light and dark themes.

The current starting configuration includes PAYEMS and a historical date of January 15, 2025 for inspecting payroll revisions. These controls can be changed at any time.

## Edit later

Edit `asof_app.py`, save it, and refresh the app to review the changes. Commit and push updates to GitHub to save a new version; earlier commits remain available in the repository history. You can also edit files directly on GitHub with the pencil button and commit the changes.

For a local Git checkout, publish only the app files:

```bash
git add asof_app.py check_asof.py requirements.txt README.md .gitignore
git commit -m "Update economic data explorer"
git push
```

## Live verification

```bash
python check_asof.py
```

Checks the supplied October 5, 2026 interest-rate expectations and January 15, 2025 PAYEMS vintage probe against live downloads. Network access is required. The expected observations are verification criteria, not substitute data for the app.

## Data

- Current: https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES
- Historical: https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=SERIES&vintage_date=YYYY-MM-DD

Downloads are cached for one hour. Refresh data clears the app's download caches. Missing observations are excluded. Charts use the selected start date; comparisons use the full downloaded histories. Revision counts compare nonmissing values on shared measurement dates.

Data from FRED and ALFRED, Federal Reserve Bank of St. Louis. Built with AI help as a learning demonstration; not investment advice. Purdue-inspired styling does not imply university affiliation or endorsement.
