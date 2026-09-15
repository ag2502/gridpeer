# shared/

This is the single source of truth for how the four modules talk to each other. `schemas.py` defines every model that crosses a module boundary: `HouseholdProfile`, `ForecastOutput`, `AgentDecision`, `TradeEvent`, `MarketState`, `HouseholdOutcome`, `RunSummary`.

**Read `CONTRIBUTING.md` before changing anything in `schemas.py`.** Short version: open an issue tagged `schema-change`, get sign-off from all four people, then change it, and update every module that touches the changed model in the same PR.

## Why this exists before any module has real logic

If you agree the *shape* of the data before you agree the *logic*, all four of you can build in parallel against a contract instead of against each other's half-finished code. The simulation owner can emit fake trades that satisfy `TradeEvent` on day 2, and the dashboard owner can build a real chart against that fake data on day 2 too — nobody's blocked waiting for someone else's module to be "done enough" to integrate with.

## Reviewing the initial schema

The schemas in this file are a reasonable starting point, not gospel — review them together as a team on Day 1 before building against them. Things worth double-checking as a group:
- Does every field have the right unit, and is it named so nobody has to guess (`_kwh` vs `_kw` bugs are the most common bug class in this kind of project)?
- Is anything missing that you already know you'll need in week 2 (better to add it now than mid-sprint)?
- Does `AgentDecision.strategy_name` give the evaluation harness (week 3, RL vs. baseline comparison) enough to work with?
