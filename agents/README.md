# agents/

Owner: _TBD_

Baseline + RL trading strategies. See `CLAUDE.md` in this folder for build guidance.

## Status

- [ ] Rule-based/bandit baseline, wired through real pipeline
- [ ] PettingZoo-style multi-agent environment wrapper
- [ ] PPO training (Stable-Baselines3)
- [ ] Evaluation harness producing `RunSummary` (baseline vs. RL)

## Running just this module

```bash
python -m agents.run_baseline    # placeholder — update once entrypoint exists
python -m agents.train_rl
pytest agents/
```
