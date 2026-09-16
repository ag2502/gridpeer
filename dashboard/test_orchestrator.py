"""Tests for the orchestration loop's forecasting stage."""

import pytest

from dashboard.orchestrator import demo_households, run_forecasts
from shared.schemas import ForecastOutput


def test_demo_households_shape() -> None:
    """Demo households carry equal-length demand and solar series."""
    households = demo_households(num_households=3, days=1)
    assert len(households) == 3
    for h in households:
        assert len(h.demand_kwh) == len(h.solar_kwh) == 48  # 1 day, half-hourly


def test_run_emits_valid_forecastoutput_per_household_per_tick() -> None:
    """Stream length == households * ticks, each a contract-valid ForecastOutput."""
    households = demo_households(num_households=2, days=1)
    stream = run_forecasts(households, num_ticks=10)
    assert len(stream) == 2 * 10
    assert all(isinstance(f, ForecastOutput) for f in stream)
    assert {f.household_id for f in stream} == {"hh_000", "hh_001"}
    assert max(f.tick for f in stream) == 9


def test_net_position_is_solar_minus_demand() -> None:
    """The contract's net position stays internally consistent."""
    stream = run_forecasts(demo_households(num_households=1, days=1), num_ticks=5)
    for f in stream:
        assert f.predicted_net_position_kwh == pytest.approx(
            f.predicted_solar_generation_kwh - f.predicted_demand_kwh
        )


def test_num_ticks_capped_to_series_length() -> None:
    """Asking for more ticks than exist is capped, not an error."""
    households = demo_households(num_households=1, days=1)  # 48 ticks
    stream = run_forecasts(households, num_ticks=1000)
    assert max(f.tick for f in stream) == 47


def test_empty_households_raises() -> None:
    with pytest.raises(ValueError):
        run_forecasts([], num_ticks=5)
