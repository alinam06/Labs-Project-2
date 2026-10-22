"""Interactive portfolio learning demonstration. Run with Streamlit."""

import hashlib
import io

import streamlit as st

from portfolio import (
    ASSETS, RETURNS, VOLATILITIES, CORRELATIONS, OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE, search_lowest_volatility, estimate_from_csv,
)


st.set_page_config(page_title="Lab 15: Meridian portfolio explorer", layout="wide")
st.title("Lab 15: Meridian portfolio explorer")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    objective = st.number_input("Objective return (%)", value=OBJECTIVE_RETURN * 100,
                                step=0.1, format="%.2f") / 100
    reserve_minimum = st.number_input("Reserve minimum (%)", min_value=0.0,
                                      max_value=100.0, value=3.0,
                                      step=1.0, format="%.2f") / 100
    upload = st.file_uploader("Upload prices.csv", type=["csv"])
    last_36 = st.toggle("Use last 36 months", value=False,
                        disabled=upload is None)
    st.caption("CSV: date first (YYYY-MM-DD), then one column per ticker; "
               "consecutive monthly prices, oldest first. Use adjusted prices.")

baseline = dict(assets=ASSETS, returns=RETURNS, volatilities=VOLATILITIES,
                correlations=CORRELATIONS)
scenario = baseline
source_key = "meridian"
loaded_eligible = RESERVE_ELIGIBLE
if upload is not None:
    content = upload.getvalue()
    source_key = hashlib.sha256(content).hexdigest()
    try:
        baseline = estimate_from_csv(io.BytesIO(content))
        scenario = estimate_from_csv(io.BytesIO(content), last_36_months=last_36)
    except (ValueError, UnicodeError, OverflowError) as error:
        st.error(str(error))
        st.stop()
    # Recognize the Treasury proxies used by this project's price downloader.
    loaded_eligible = tuple(asset.upper() in {"SGOV", "IEF"}
                            for asset in baseline["assets"])
    st.caption(f"CSV estimates: scenario uses {scenario['months']} monthly returns; "
               f"loaded comparison uses all {baseline['months']}. "
               "Annual estimates use mean × 12 and sample standard deviation × √12.")
else:
    st.caption("Using Meridian's supplied annual assumptions. Search step: 5 percentage points.")

# Reset editable inputs when the file or estimation window changes, while keeping
# edits when objective/reserve controls trigger a rerun.
input_key = (source_key, last_36 if upload is not None else False)
if st.session_state.get("loaded_inputs") != input_key:
    for i, value in enumerate(scenario["returns"]):
        st.session_state[f"return_{i}"] = value * 100
    for i, value in enumerate(loaded_eligible):
        st.session_state[f"eligible_{i}"] = value
    st.session_state["loaded_inputs"] = input_key

st.subheader("Edit scenario inputs")
edited_returns, edited_eligible = [], []
for i, asset in enumerate(scenario["assets"]):
    left, right = st.columns([3, 2])
    with left:
        edited_returns.append(st.number_input(
            f"{asset} expected annual return (%)", step=0.1,
            format="%.2f", key=f"return_{i}") / 100)
    with right:
        edited_eligible.append(st.checkbox(f"{asset}: reserve-eligible", key=f"eligible_{i}"))

current = search_lowest_volatility(
    edited_returns, scenario["volatilities"], scenario["correlations"],
    edited_eligible, objective, reserve_minimum)
loaded = search_lowest_volatility(
    baseline["returns"], baseline["volatilities"], baseline["correlations"],
    loaded_eligible, objective, reserve_minimum)


def show_mix(title, result):
    st.subheader(title)
    if result is None:
        st.write("no mix meets the objective")
        return
    st.table([{"Asset": asset, "Weight (%)": f"{weight * 100:.2f}"}
              for asset, weight in zip(scenario["assets"], result["weights"])])
    st.metric("Expected annual return", f"{result['expected_return']:.2%}")
    st.metric("Annual volatility", f"{result['volatility']:.2%}")
    st.metric("Reserve-eligible weight", f"{result['reserve_weight']:.2%}")


left, right = st.columns(2)
with left:
    show_mix("Lowest-risk mix · your scenario", current)
with right:
    show_mix("Lowest-risk mix · inputs as loaded", loaded)
    st.caption("Uses the same objective and reserve minimum, with the original "
               "returns and reserve flags; CSV estimates use all months. "
               "CSV reserve defaults recognize SGOV and IEF.")

if current is not None and loaded is not None:
    changes = [(a - b) * 100 for a, b in zip(current["weights"], loaded["weights"])]
    largest = max(range(len(changes)), key=lambda i: abs(changes[i]))
    st.write(f"Largest weight change: {scenario['assets'][largest]} "
             f"{changes[largest]:+.2f} percentage points "
             f"(absolute change {abs(changes[largest]):.2f} points).")
else:
    st.write("Largest weight change: unavailable unless both mixes are feasible.")
