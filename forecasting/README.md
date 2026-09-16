# forecasting/

Owner: _TBD_

Per-household demand + solar generation forecasting. See `CLAUDE.md` in this folder for build guidance.

## Status

- [x] Naive baseline forecaster (`baseline.NaiveForecaster`, rolling average + flat fallback)
- [ ] LightGBM/Prophet demand model
- [ ] Solar generation forecaster
- [ ] Backtest report (MAE/MAPE per household)

## Running just this module

```bash
python -m forecasting.backtest    # placeholder — update once entrypoint exists
pytest forecasting/
```
