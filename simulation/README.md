# simulation/

Owner: _TBD_

Market clearing mechanism (continuous double auction) + household environment. See `CLAUDE.md` in this folder for build guidance, and the root `README.md` for how this fits the overall architecture.

## Status

- [ ] 2-household deterministic test case
- [ ] Household environment (real data loading)
- [ ] N-household continuous double auction
- [ ] Grid-baseline fallback for unmatched orders

## Running just this module

```bash
python -m simulation.run_demo   # placeholder — update once entrypoint exists
pytest simulation/
```
