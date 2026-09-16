"""GridPeer dashboard (Streamlit) — live view of the forecasting stage.

Week-1 scope: prove real data flows through real contracts. This renders the
ForecastOutput stream the orchestrator produces — predicted demand, solar, and
net position per household over time. The outcomes narrative (savings, CO2,
peak-load; HouseholdOutcome / RunSummary) arrives once agents/ and simulation/
feed trades into the loop.

Run:  streamlit run dashboard/app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.orchestrator import demo_households, run_forecasts
from shared.schemas import ForecastOutput


def _to_frame(stream: list[ForecastOutput]) -> pd.DataFrame:
    """Flatten the ForecastOutput stream into a tidy DataFrame for charting."""
    return pd.DataFrame(
        {
            "tick": f.tick,
            "household_id": f.household_id,
            "predicted_demand_kwh": f.predicted_demand_kwh,
            "predicted_solar_generation_kwh": f.predicted_solar_generation_kwh,
            "predicted_net_position_kwh": f.predicted_net_position_kwh,
            "confidence": f.confidence,
        }
        for f in stream
    )


def _pivot(frame: pd.DataFrame, value: str) -> pd.DataFrame:
    """Wide frame indexed by tick, one column per household, for st.line_chart."""
    return frame.pivot(index="tick", columns="household_id", values=value)


def main() -> None:
    st.set_page_config(page_title="GridPeer", page_icon="⚡", layout="wide")
    st.title("⚡ GridPeer — forecasting pipeline")
    st.caption(
        "Real ForecastOutput contracts flowing from forecasting/ through the "
        "orchestrator. Trades, savings and CO2 land once agents/ + simulation/ wire in."
    )

    with st.sidebar:
        st.header("Controls")
        num_households = st.slider("Households", 1, 4, 4)
        days = st.slider("Days of series", 1, 3, 2)
        window = st.slider("Forecaster window (ticks)", 1, 8, 4)
        st.caption("Naive baseline: rolling average over the last *window* half-hour ticks.")

    households = demo_households(num_households=num_households, days=days)
    stream = run_forecasts(households, window=window)
    frame = _to_frame(stream)

    ticks = frame["tick"].nunique()
    col1, col2, col3 = st.columns(3)
    col1.metric("Households", num_households)
    col2.metric("Ticks (half-hourly)", ticks)
    col3.metric("ForecastOutput emitted", len(stream))

    st.subheader("Predicted demand (kWh)")
    st.line_chart(_pivot(frame, "predicted_demand_kwh"))

    st.subheader("Predicted solar generation (kWh)")
    st.line_chart(_pivot(frame, "predicted_solar_generation_kwh"))

    st.subheader("Predicted net position (kWh)  —  + surplus (can sell) / − deficit (needs to buy)")
    st.line_chart(_pivot(frame, "predicted_net_position_kwh"))

    st.subheader("Forecast confidence")
    st.line_chart(_pivot(frame, "confidence"))

    with st.expander("Raw ForecastOutput stream"):
        st.dataframe(frame, use_container_width=True)


if __name__ == "__main__":
    main()
