"""Run with: .venv/bin/python -m streamlit run asof_app.py"""

from datetime import date
from io import StringIO
import re

import pandas as pd
import requests
import streamlit as st


GOLD = "#B89B5E"


def apply_style() -> None:
    # Keep native theme colors so Streamlit's Light / Dark setting stays readable.
    st.markdown("""
    <style>
    .block-container {max-width: 1360px; padding-top: 2rem;}
    h1 {border-bottom: 3px solid #CFB991; padding-bottom: .65rem !important;}
    h1, h2, h3 {letter-spacing: -.025em;}
    [data-testid="stSidebar"] {border-right: 1px solid #CFB991;}
    </style>
    """, unsafe_allow_html=True)


SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
}


def parse_csv(text: str) -> pd.Series:
    """Both downloads have a date column and one (possibly suffixed) value column."""
    frame = pd.read_csv(StringIO(text), na_values=["."])
    if len(frame.columns) != 2:
        raise ValueError("FRED did not return a single-series CSV; check the series ID.")
    dates = pd.to_datetime(frame.iloc[:, 0], errors="coerce")
    values = pd.to_numeric(frame.iloc[:, 1], errors="coerce")
    if dates.isna().any():
        raise ValueError("FRED returned an invalid date column; check the series ID.")
    result = pd.Series(values.to_numpy(), index=pd.DatetimeIndex(dates), name="Value")
    return result.dropna().sort_index().loc[lambda s: ~s.index.duplicated(keep="last")]


@st.cache_data(ttl=3600, show_spinner=False)
def download_today(series_id: str, downloaded_on: date) -> pd.Series:
    """One public CSV request; date in the cache key prevents reuse across days."""
    response = requests.get(
        "https://fred.stlouisfed.org/graph/fredgraph.csv",
        params={"id": series_id}, timeout=30,
    )
    response.raise_for_status()
    return parse_csv(response.text)


@st.cache_data(ttl=3600, show_spinner=False)
def download_asof(series_id: str, vintage_date: date, downloaded_on: date) -> pd.Series:
    """One public ALFRED CSV request for the requested vintage."""
    response = requests.get(
        "https://alfred.stlouisfed.org/graph/alfredgraph.csv",
        params={"id": series_id, "vintage_date": vintage_date.isoformat()}, timeout=30,
    )
    response.raise_for_status()
    values = parse_csv(response.text)
    return values.loc[values.index <= pd.Timestamp(vintage_date)]


def comparison(series_id: str, current: pd.Series, vintage: pd.Series) -> dict:
    common = current.index.intersection(vintage.index)
    return {
        "Series": f"https://fred.stlouisfed.org/series/{series_id}",
        "Last measured date (as known then)": vintage.index[-1].date() if not vintage.empty else None,
        "Value (as known then)": float(vintage.iloc[-1]) if not vintage.empty else None,
        "Today's value for last date known then": float(current.get(vintage.index[-1], float("nan"))) if not vintage.empty else None,
        "Last measured date (today)": current.index[-1].date() if not current.empty else None,
        "Value (today)": float(current.iloc[-1]) if not current.empty else None,
        "Values after last date known then": int((current.index > vintage.index[-1]).sum()) if not vintage.empty else None,
        "Revised values on shared dates": int((current.loc[common] != vintage.loc[common]).sum()),
    }


def main() -> None:
    st.set_page_config(page_title="Economic Observatory | FRED & ALFRED", page_icon="📈", layout="wide")
    apply_style()
    today = date.today()
    st.title("FRED · Interest rates & economic data")
    st.caption(
        f"Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded {today:%Y-%m-%d}; "
        "built with AI help, a learning demonstration, not investment advice."
    )
    with st.sidebar:
        st.header("Explore the data")
        st.caption("Select series and dates. Results update automatically.")
        selected = st.multiselect(
            "Series", options=list(SERIES), default=list(SERIES),
            format_func=lambda key: f"{key} — {SERIES[key]}",
        )
        extra = st.text_input("Add another FRED series ID", value="PAYEMS", placeholder="e.g. DGS2").strip().upper()
        start = st.date_input("Start date", value=date(2020, 1, 1), min_value=date(1776, 1, 1), max_value=today)
        asof = st.date_input("As known on", value=date(2025, 1, 15), min_value=date(1776, 1, 1), max_value=today)
        st.divider()
        if st.button("Refresh data", width="stretch"):
            download_today.clear()
            download_asof.clear()
        st.caption("Appearance: open ⋮ → Settings → Theme to choose Light or Dark.")
    if extra and extra not in selected:
        selected.append(extra)
    summary = st.container()
    st.subheader("Charts")
    rows = []
    for series_id in selected:
        name = SERIES.get(series_id, "Payroll jobs" if series_id == "PAYEMS" else "Additional indicator")
        st.subheader(f"{series_id} · {name}")
        if not re.fullmatch(r"[A-Z0-9_]+", series_id):
            st.error(f"{series_id}: enter a valid FRED series ID (letters, numbers, or underscores).")
            continue
        current = vintage = None
        with st.spinner(f"Loading {series_id}…"):
            try:
                current = download_today(series_id, today)
            except (requests.RequestException, ValueError, pd.errors.ParserError) as exc:
                st.error(f"{series_id}: today's data could not be downloaded. Check the ID or try again. {exc}")
            try:
                vintage = download_asof(series_id, asof, today)
            except (requests.RequestException, ValueError, pd.errors.ParserError) as exc:
                st.error(f"{series_id}: data as known on {asof} could not be downloaded. Check the ID or try again. {exc}")
        if current is not None:
            chart = current.loc[current.index >= pd.Timestamp(start)]
            if chart.empty:
                st.info("No measured values in the selected chart period.")
            else:
                import altair as alt

                unit = "Thousands of jobs" if series_id == "PAYEMS" else "Percent" if series_id in SERIES else "Value"
                frame = chart.rename("Value").rename_axis("Date").reset_index()
                plot = alt.Chart(frame).mark_line(color=GOLD, strokeWidth=2.5).encode(
                    x=alt.X("Date:T", title=None, axis=alt.Axis(format="%Y", grid=False)),
                    y=alt.Y("Value:Q", title=unit, scale=alt.Scale(zero=False)),
                    tooltip=[alt.Tooltip("Date:T", title="Measurement date", format="%d %b %Y"),
                             alt.Tooltip("Value:Q", title=unit, format=",.2f")],
                ).properties(height=250).configure_view(strokeWidth=0)
                st.altair_chart(plot, width="stretch", theme="streamlit")
        if vintage is not None:
            last = vintage.index[-1].strftime("%Y-%m-%d") if not vintage.empty else "No measured values available"
            st.caption(f"Last measured date in data known on {asof:%Y-%m-%d}: {last}")
        if current is not None and vintage is not None:
            rows.append(comparison(series_id, current, vintage))
        if current is not None or vintage is not None:
            with st.expander(f"View / download {series_id} data"):
                data = pd.concat({
                    "Today": current if current is not None else pd.Series(dtype=float),
                    f"As known on {asof}": vintage if vintage is not None else pd.Series(dtype=float),
                }, axis=1).rename_axis("Measurement date").sort_index(ascending=False)
                st.dataframe(data, width="stretch")
                st.download_button("Download series CSV", data.to_csv().encode("utf-8"),
                                   file_name=f"{series_id}_{asof}.csv", mime="text/csv",
                                   key=f"download_{series_id}")
                st.markdown(f"[Open FRED page](https://fred.stlouisfed.org/series/{series_id})")
        st.divider()
    if rows:
        with summary:
            render_summary(rows, asof, today)
    elif not selected:
        st.info("Select a series or enter a FRED series ID to begin.")


def render_summary(rows: list, asof: date, today: date) -> None:
    st.subheader("Then and today")
    st.caption(f"Historical vintage: {asof:%d %B %Y} · Current download: {today:%d %B %Y}")
    st.caption(
        "Comparison uses the full downloaded histories; the start date only limits charts. "
        "Missing days (.) are excluded. Revisions compare nonmissing values on shared measurement dates. "
        "When no values were known then, the later-value count is unavailable."
    )
    st.dataframe(
        pd.DataFrame(rows), hide_index=True, width="stretch",
        column_config={"Series": st.column_config.LinkColumn("Series", display_text=r"https://fred\.stlouisfed\.org/series/(.*)")},
    )
    st.download_button("Download comparison CSV", pd.DataFrame(rows).to_csv(index=False).encode("utf-8"),
                       file_name=f"fred_comparison_{asof}.csv", mime="text/csv")

if __name__ == "__main__":
    main()
