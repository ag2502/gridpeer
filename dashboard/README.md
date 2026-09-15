# dashboard/

Owner: _TBD_

Orchestration loop + live outcomes dashboard. See `CLAUDE.md` in this folder for build guidance.

## Status

- [ ] Orchestration loop (ticks the pipeline forward)
- [ ] Persistence layer (SQLite/DuckDB)
- [ ] Streamlit dashboard — savings, price, volume, CO2/peak-load headline metrics
- [ ] (Week 4+, optional) FastAPI + React rebuild

## Running just this module

```bash
streamlit run dashboard/app.py    # placeholder — update once entrypoint exists
pytest dashboard/
```
