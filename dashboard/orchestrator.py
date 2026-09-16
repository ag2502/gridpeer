"""Orchestration loop: ticks the pipeline forward, one stage at a time.

Right now only the forecasting stage is wired — agents/ and simulation/ are
still skeletons owned by other modules. As those land, this loop grows:

    tick -> forecasting (ForecastOutput)   [wired]
         -> agents      (AgentDecision)    [TODO: consume ForecastOutput]
         -> simulation  (TradeEvent/MarketState)  [TODO: consume AgentDecision]
         -> persist + display

The loop only ever exchanges shared contracts with each module — it never
reaches into their internals. Demo households + series below stand in for the
data/ module (synthetic/CER loader), which is a separate task; when that lands,
only `demo_households` is replaced, not the loop.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from forecasting.baseline import NaiveForecaster
from shared.schemas import AgentRole, ForecastOutput, HouseholdProfile

TICK_MINUTES = 30
_EPOCH = datetime(2026, 1, 1, 0, 0)


def _timestamp(tick: int) -> datetime:
    """Wall-clock time for a tick, at half-hour (CER) resolution."""
    return _EPOCH + timedelta(minutes=TICK_MINUTES * tick)


@dataclass(frozen=True)
class HouseholdSeries:
    """A household's identity plus its actual demand/solar series (kWh).

    The series are the ground truth the orchestrator feeds to the forecaster as
    history, tick by tick. Stand-in for real CER/PVGIS data.
    """

    profile: HouseholdProfile
    demand_kwh: list[float]
    solar_kwh: list[float]


def _series_for(
    role: AgentRole, solar_capacity_kw: float, days: int, seed: int
) -> tuple[list[float], list[float]]:
    """Placeholder half-hourly demand + solar for one household (shape, not truth)."""
    ticks_per_day = 24 * 60 // TICK_MINUTES  # 48
    demand: list[float] = []
    solar: list[float] = []
    for tick in range(days * ticks_per_day):
        hour = (tick % ticks_per_day) * TICK_MINUTES / 60.0
        jitter = ((tick * 2654435761 + seed) % 1000) / 1000.0 * 0.2
        morning = math.exp(-((hour - 8) ** 2) / 2.0)
        evening = math.exp(-((hour - 19) ** 2) / 2.0)
        base = 0.15 if role == AgentRole.PURE_PRODUCER else 0.3
        peaks = 0.0 if role == AgentRole.PURE_PRODUCER else 1.2 * (morning + evening)
        demand.append(base + peaks + jitter)
        if solar_capacity_kw > 0 and 6 <= hour <= 20:
            midday = math.exp(-((hour - 13) ** 2) / 8.0)
            solar.append(max(0.0, solar_capacity_kw * 0.5 * midday))
        else:
            solar.append(0.0)
    return demand, solar


def demo_households(num_households: int = 4, days: int = 2) -> list[HouseholdSeries]:
    """Build a small mixed set of households with placeholder series.

    Replaced wholesale by the data/ loader later — the loop does not change.
    """
    roles = [
        AgentRole.PROSUMER,
        AgentRole.PURE_CONSUMER,
        AgentRole.PROSUMER,
        AgentRole.PURE_PRODUCER,
    ]
    out: list[HouseholdSeries] = []
    for i in range(num_households):
        role = roles[i % len(roles)]
        has_solar = role in (AgentRole.PROSUMER, AgentRole.PURE_PRODUCER)
        solar_capacity = 3.0 if has_solar else 0.0
        profile = HouseholdProfile(
            household_id=f"hh_{i:03d}",
            role=role,
            has_solar=has_solar,
            solar_capacity_kw=solar_capacity,
            battery_capacity_kwh=5.0 if has_solar else 0.0,
            grid_export_tariff_eur_per_kwh=0.07,
            grid_import_tariff_eur_per_kwh=0.25,
        )
        demand, solar = _series_for(role, solar_capacity, days, seed=i)
        out.append(HouseholdSeries(profile=profile, demand_kwh=demand, solar_kwh=solar))
    return out


def run_forecasts(
    households: list[HouseholdSeries],
    num_ticks: int | None = None,
    window: int = 4,
) -> list[ForecastOutput]:
    """Tick the forecasting stage forward and collect ForecastOutput.

    At each tick every household is forecast from its own history up to that
    tick only (no peeking ahead). Returns the full stream the dashboard renders
    and, later, the agents module consumes. ``num_ticks`` defaults to the full
    length of the (equal-length) demo series.
    """
    if not households:
        raise ValueError("no households to run")
    available = min(len(h.demand_kwh) for h in households)
    ticks = available if num_ticks is None else min(num_ticks, available)

    forecaster = NaiveForecaster(window=window)
    stream: list[ForecastOutput] = []
    for tick in range(ticks):
        timestamp = _timestamp(tick)
        for household in households:
            stream.append(
                forecaster.forecast(
                    household_id=household.profile.household_id,
                    tick=tick,
                    timestamp=timestamp,
                    demand_history_kwh=household.demand_kwh[:tick],
                    solar_history_kwh=household.solar_kwh[:tick],
                )
            )
    return stream


def main() -> None:
    """Run the forecasting stage on demo households and print a short summary."""
    households = demo_households()
    stream = run_forecasts(households)
    ticks = len({f.tick for f in stream})
    print(
        f"Orchestrator: {len(households)} households x {ticks} ticks "
        f"= {len(stream)} ForecastOutput"
    )
    for forecast in stream[: len(households)]:
        print(
            f"  tick {forecast.tick} {forecast.household_id}: "
            f"demand={forecast.predicted_demand_kwh:.2f} kWh  "
            f"solar={forecast.predicted_solar_generation_kwh:.2f} kWh  "
            f"net={forecast.predicted_net_position_kwh:+.2f} kWh"
        )
    print("agents/ + simulation/ stages: pending those modules (see module TODOs).")


if __name__ == "__main__":
    main()
