"""Tests for grid-baseline settlement — the P2P-versus-grid-only comparison."""

from datetime import datetime

import pytest

from shared.schemas import AgentDecision, AgentRole, HouseholdProfile, OrderSide
from simulation.market import clear_tick
from simulation.settlement import settle_tick

TICK = 1
TIMESTAMP = datetime(2026, 1, 1, 8, 0)
IMPORT_TARIFF = 0.25
EXPORT_TARIFF = 0.07


def profile(household_id: str) -> HouseholdProfile:
    """A household on the standard tariffs these tests use."""
    return HouseholdProfile(
        household_id=household_id,
        role=AgentRole.PROSUMER,
        has_solar=True,
        solar_capacity_kw=3.0,
        battery_capacity_kwh=5.0,
        grid_export_tariff_eur_per_kwh=EXPORT_TARIFF,
        grid_import_tariff_eur_per_kwh=IMPORT_TARIFF,
    )


def order(
    household_id: str,
    side: OrderSide,
    quantity_kwh: float,
    limit_price_eur_per_kwh: float,
) -> AgentDecision:
    return AgentDecision(
        household_id=household_id,
        tick=TICK,
        side=side,
        quantity_kwh=quantity_kwh,
        limit_price_eur_per_kwh=limit_price_eur_per_kwh,
        strategy_name="test_fixture",
    )


def test_a_matched_trade_saves_both_sides_money():
    """The whole thesis of the project, in one tick, calculated by hand.

    hh_sell offers 2.0 kWh from 0.10, hh_buy will pay up to 0.20, so they clear at
    the 0.15 midpoint. Against the grid the buyer would have paid 0.25/kWh and the
    seller been paid only 0.07/kWh, so:

        buyer: pays 2.0 * 0.15 = 0.30 instead of 2.0 * 0.25 = 0.50  -> saves 0.20
        seller: earns 2.0 * 0.15 = 0.30 instead of 2.0 * 0.07 = 0.14 -> gains 0.16

    Both sides land inside the import/export tariff gap. That gap is the entire
    margin the marketplace exists to capture.
    """
    orders = [
        order("hh_sell", OrderSide.SELL, quantity_kwh=2.0, limit_price_eur_per_kwh=0.10),
        order("hh_buy", OrderSide.BUY, quantity_kwh=2.0, limit_price_eur_per_kwh=0.20),
    ]
    state = clear_tick(tick=TICK, timestamp=TIMESTAMP, orders=orders)

    settlements = settle_tick(
        state, {"hh_buy": profile("hh_buy"), "hh_sell": profile("hh_sell")}, orders
    )

    buyer = settlements["hh_buy"]
    assert buyer.p2p_cost_eur == pytest.approx(0.30)
    assert buyer.grid_only_cost_eur == pytest.approx(0.50)
    assert buyer.savings_eur == pytest.approx(0.20)
    assert buyer.traded_kwh == 2.0
    assert buyer.grid_fallback_kwh == 0.0

    seller = settlements["hh_sell"]
    assert seller.p2p_cost_eur == pytest.approx(-0.30)  # negative cost = revenue
    assert seller.grid_only_cost_eur == pytest.approx(-0.14)
    assert seller.savings_eur == pytest.approx(0.16)


def test_an_unmatched_order_falls_back_to_the_grid_and_saves_nothing():
    """No match means no saving — P2P and grid-only must come out identical.

    An unmatched buyer still needs the energy and imports it at the import tariff.
    Reporting any saving here would inflate the headline number with trades that
    never happened.
    """
    buy = order("hh_buy", OrderSide.BUY, quantity_kwh=1.0, limit_price_eur_per_kwh=0.08)
    sell = order("hh_sell", OrderSide.SELL, quantity_kwh=1.0, limit_price_eur_per_kwh=0.12)
    state = clear_tick(tick=TICK, timestamp=TIMESTAMP, orders=[buy, sell])
    assert state.trades == []

    settlements = settle_tick(
        state, {"hh_buy": profile("hh_buy"), "hh_sell": profile("hh_sell")}, [buy, sell]
    )

    buyer = settlements["hh_buy"]
    assert buyer.p2p_cost_eur == pytest.approx(IMPORT_TARIFF)
    assert buyer.grid_only_cost_eur == pytest.approx(IMPORT_TARIFF)
    assert buyer.savings_eur == pytest.approx(0.0)
    assert buyer.grid_fallback_kwh == 1.0
    assert buyer.traded_kwh == 0.0

    seller = settlements["hh_sell"]
    assert seller.p2p_cost_eur == pytest.approx(-EXPORT_TARIFF)
    assert seller.savings_eur == pytest.approx(0.0)


def test_a_partial_fill_settles_the_traded_and_fallback_portions_separately():
    """3.0 kWh wanted, 1.0 kWh matched: 1.0 trades, 2.0 imports from the grid."""
    orders = [
        order("hh_buy", OrderSide.BUY, quantity_kwh=3.0, limit_price_eur_per_kwh=0.20),
        order("hh_sell", OrderSide.SELL, quantity_kwh=1.0, limit_price_eur_per_kwh=0.10),
    ]
    state = clear_tick(tick=TICK, timestamp=TIMESTAMP, orders=orders)

    settlements = settle_tick(
        state, {"hh_buy": profile("hh_buy"), "hh_sell": profile("hh_sell")}, orders
    )

    buyer = settlements["hh_buy"]
    assert buyer.traded_kwh == 1.0
    assert buyer.grid_fallback_kwh == 2.0
    # 1.0 kWh at the 0.15 midpoint + 2.0 kWh imported at 0.25.
    assert buyer.p2p_cost_eur == pytest.approx(0.15 + 0.50)
    # Grid-only: all 3.0 kWh imported at 0.25.
    assert buyer.grid_only_cost_eur == pytest.approx(0.75)
    assert buyer.savings_eur == pytest.approx(0.10)


def test_households_keep_their_own_tariffs():
    """Tariffs are per household, so settlement must not use a shared default."""
    cheap_importer = profile("hh_buy").model_copy(
        update={"grid_import_tariff_eur_per_kwh": 0.16}
    )
    orders = [
        order("hh_sell", OrderSide.SELL, quantity_kwh=1.0, limit_price_eur_per_kwh=0.10),
        order("hh_buy", OrderSide.BUY, quantity_kwh=1.0, limit_price_eur_per_kwh=0.20),
    ]
    state = clear_tick(tick=TICK, timestamp=TIMESTAMP, orders=orders)

    settlements = settle_tick(
        state, {"hh_buy": cheap_importer, "hh_sell": profile("hh_sell")}, orders
    )

    # This buyer's grid alternative is cheaper, so the same trade saves it less.
    assert settlements["hh_buy"].grid_only_cost_eur == pytest.approx(0.16)
    assert settlements["hh_buy"].savings_eur == pytest.approx(0.01)


def test_a_household_that_sat_out_the_tick_settles_at_zero():
    """Passing the original book keeps non-participants in the run at zero cost."""
    orders = [
        order("hh_sell", OrderSide.SELL, quantity_kwh=1.0, limit_price_eur_per_kwh=0.10),
        order("hh_buy", OrderSide.BUY, quantity_kwh=1.0, limit_price_eur_per_kwh=0.20),
    ]
    state = clear_tick(tick=TICK, timestamp=TIMESTAMP, orders=orders)
    profiles = {
        "hh_buy": profile("hh_buy"),
        "hh_sell": profile("hh_sell"),
        "hh_quiet": profile("hh_quiet"),
    }

    settlements = settle_tick(state, profiles, orders)

    assert "hh_quiet" not in settlements  # it submitted no order at all

    quiet_order = order("hh_quiet", OrderSide.BUY, quantity_kwh=1.0, limit_price_eur_per_kwh=0.01)
    with_quiet = settle_tick(state, profiles, [*orders, quiet_order])
    assert with_quiet["hh_quiet"].p2p_cost_eur == 0.0
    assert with_quiet["hh_quiet"].savings_eur == 0.0


def test_settling_without_a_profile_is_an_error():
    """A missing profile means missing tariffs — guessing them would corrupt the result."""
    orders = [
        order("hh_sell", OrderSide.SELL, quantity_kwh=1.0, limit_price_eur_per_kwh=0.10),
        order("hh_buy", OrderSide.BUY, quantity_kwh=1.0, limit_price_eur_per_kwh=0.20),
    ]
    state = clear_tick(tick=TICK, timestamp=TIMESTAMP, orders=orders)

    with pytest.raises(KeyError, match="hh_sell"):
        settle_tick(state, {"hh_buy": profile("hh_buy")}, orders)


def test_savings_never_exceed_the_tariff_gap():
    """Sanity bound: a trade can only ever capture the import/export spread.

    If this ever fails, the settlement is inventing money — the most damaging
    possible bug in this project, because it would make the headline savings
    figure indefensible.
    """
    orders = [
        order("hh_sell", OrderSide.SELL, quantity_kwh=2.0, limit_price_eur_per_kwh=EXPORT_TARIFF),
        order("hh_buy", OrderSide.BUY, quantity_kwh=2.0, limit_price_eur_per_kwh=IMPORT_TARIFF),
    ]
    state = clear_tick(tick=TICK, timestamp=TIMESTAMP, orders=orders)

    settlements = settle_tick(
        state, {"hh_buy": profile("hh_buy"), "hh_sell": profile("hh_sell")}, orders
    )

    gap_eur = 2.0 * (IMPORT_TARIFF - EXPORT_TARIFF)
    total_savings = sum(s.savings_eur for s in settlements.values())
    assert total_savings == pytest.approx(gap_eur)
    assert all(s.savings_eur >= 0 for s in settlements.values())
