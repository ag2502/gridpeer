# dashboard/

Owner: _TBD_

Orchestration loop + live outcomes dashboard. See `CLAUDE.md` in this folder for build guidance.

## Status

- [~] Orchestration loop (`orchestrator.py`) — forecasting stage wired; agents/simulation stages pending those modules
- [ ] Persistence layer (SQLite/DuckDB)
- [~] Streamlit dashboard (`app.py`) — forecast view (demand/solar/net/confidence); savings/price/volume/CO2 pending trades
- [ ] (Week 4+, optional) FastAPI + React rebuild

## Running just this module

```bash
streamlit run dashboard/app.py    # live forecast dashboard
python -m dashboard.orchestrator  # headless: run the loop, print a summary
pytest dashboard/
```
