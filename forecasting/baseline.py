"""Naive baseline forecaster: rolling-average demand + solar prediction.

Build-order step 1 (see forecasting/CLAUDE.md): the boring sanity-check model
that stays in the codebase as a fallback once smarter models (LightGBM/Prophet)
arrive behind the same ForecastOutput contract. It predicts the next tick as the
mean of the most recent observations, falling back to a flat value when no
history exists yet — enough to make the end-to-end pipeline real in week 1.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from shared.schemas import ForecastOutput


class NaiveForecaster:
    """Rolling-average forecaster for one household's demand and solar output.

    Predicts each quantity as the mean of the last ``window`` observations.
    Not accurate — it is the reference point every real model must beat.
    """

    def __init__(self, window: int = 4, flat_demand_kwh: float = 0.5) -> None:
        """window: how many recent observations to average (half-hour ticks).
        flat_demand_kwh: fallback demand when no history is available yet.
        """
        if window < 1:
            raise ValueError("window must be >= 1")
        if flat_demand_kwh < 0:
            raise ValueError("flat_demand_kwh must be >= 0")
        self.window = window
        self.flat_demand_kwh = flat_demand_kwh

    def _rolling_mean(self, history_kwh: Sequence[float], fallback_kwh: float) -> float:
        """Mean of the last ``window`` values in kWh; fallback if history empty."""
        if not history_kwh:
            return fallback_kwh
        recent = history_kwh[-self.window :]
        return sum(recent) / len(recent)

    def _confidence(self, history_kwh: Sequence[float]) -> float:
        """Placeholder confidence in [0, 1]: rises as more history accrues.

        Day-1 stand-in for the real normalised-recent-error metric (build-order
        step 4). Consumed by agents/ and dashboard/ for display only.
        """
        return min(len(history_kwh), self.window) / self.window

    def forecast(
        self,
        household_id: str,
        tick: int,
        timestamp: datetime,
        demand_history_kwh: Sequence[float],
        solar_history_kwh: Sequence[float],
    ) -> ForecastOutput:
        """Predict one household's next-tick demand and solar generation (kWh).

        History sequences are past observations in chronological order. Returns a
        ForecastOutput satisfying the shared contract — the only thing agents/ and
        dashboard/ consume from this module.
        """
        predicted_demand = self._rolling_mean(demand_history_kwh, self.flat_demand_kwh)
        predicted_solar = self._rolling_mean(solar_history_kwh, 0.0)
        confidence = min(
            self._confidence(demand_history_kwh),
            self._confidence(solar_history_kwh),
        )
        return ForecastOutput(
            household_id=household_id,
            tick=tick,
            timestamp=timestamp,
            predicted_demand_kwh=predicted_demand,
            predicted_solar_generation_kwh=predicted_solar,
            predicted_net_position_kwh=predicted_solar - predicted_demand,
            confidence=confidence,
        )
