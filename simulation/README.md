# simulation/

Owner: Amogh Gaikwad (@ag2502)

Market clearing mechanism (continuous double auction) + household environment. See `CLAUDE.md` in this folder for build guidance, and the root `README.md` for how this fits the overall architecture.

## Status

- [x] 2-household deterministic test case
- [ ] Household environment (real data loading)
- [x] N-household continuous double auction
- [ ] Grid-baseline fallback for unmatched orders

## Running just this module

```bash
pytest simulation/
```

## Clearing, in one paragraph

`clear_tick(tick, timestamp, orders)` takes a tick's `AgentDecision` book and returns a
`MarketState`. Buys rank by descending limit price, sells by ascending, ties broken by
arrival order in the input sequence (price-time priority). The best buy matches the best
sell while the buyer's maximum is at least the seller's minimum; each match trades the
smaller quantity at the midpoint of the two limit prices, and the larger order keeps its
remainder on the book. Unmatched orders — including a partial fill's remainder — come back
in `MarketState` for the caller to settle against grid tariffs. The tick's
`clearing_price_eur_per_kwh` is the volume-weighted average of its trades, or `None` when
nothing cleared. Clearing is deterministic: the same book always produces the same result.
