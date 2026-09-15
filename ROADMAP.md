# Roadmap

Four weeks, four people, all skilled, all with time. This is deliberately front-loaded: the goal is a real end-to-end pipeline by the end of week 1, so weeks 2–4 are about improving real modules instead of assembling them for the first time under deadline pressure.

## Deciding roles (do this before Day 1)

Pick one owner per module. Suggested fit, not a rule:
- **Simulation & market mechanism** — whoever's strongest on algorithmic/systems thinking; this module has the least ML and the most careful logic.
- **RL agents** — whoever's most excited about RL specifically. This is the hardest module to make actually work well, and enthusiasm matters more here than anywhere else.
- **Forecasting** — whoever's strongest on classical ML / time series.
- **Orchestration & dashboard** — good seat for the person who cares most about the outcome narrative (savings %, CO2 avoided) rather than pure model metrics — often the person driving the BA/product framing.

Also settle now: **who has final say when two people disagree on a schema field.** Small decision, but it's the argument that stalls week 1 in projects like this if it's not settled up front.

## Week 1 — Contracts and an ugly end-to-end pipeline

**Day 1–2**
- [ ] Agree the shared interfaces as actual typed schemas (already scaffolded in `shared/schemas.py` — review and adjust together, don't skip this review just because it's pre-written)
- [ ] Fill in `README.md` team table with real names
- [ ] Repo pushed to GitHub, all four have push access
- [ ] `make setup && make test` passes on all four laptops
- [ ] One issue per person on the GitHub Project board, scoped to "build the skeleton of my module"

**Day 3–5**
- [ ] Each person builds a skeleton of their module that satisfies the shared contract using fake/placeholder data — simulation emits dummy trades, dashboard renders them, forecaster returns placeholder numbers, agent returns a hardcoded decision
- [ ] **Goal by end of week 1: a fully wired, end-to-end pipeline that is ugly but real.** This is the single highest-leverage milestone in the whole project — it converts "four modules that might integrate eventually" into "one working system we're now improving."

## Week 2 — Real modules

- [ ] **Simulation:** implement the actual continuous double auction market-clearing mechanism; calibrate household profiles from real CER Smart Metering Trial data (see `data/README.md`)
- [ ] **Forecasting:** real demand + solar generation forecasting per household, start with LightGBM or Prophet — boring and reliable beats fancy and unstable at this stage
- [ ] **Agents:** get the rule-based / bandit baseline trading strategy running through the *real* pipeline (not the skeleton) — this becomes the comparison baseline for everything after
- [ ] **Dashboard:** swap placeholder data for real data as the other three modules mature; start building the actual visual story (price over time, trade volume)

## Week 3 — Integration and the actual result

- [ ] Full integration of all real modules end to end
- [ ] RL agent training: reward shaping, training stability
- [ ] **The core deliverable of the whole project:** RL-agent performance vs. rule-based baseline, measured and visualised. This comparison is the entire demo story.
- [ ] Add business-impact metrics to the dashboard: household cost savings %, CO2 avoided, peak-load reduction vs. grid-only baseline
- [ ] Start writing tests and the README as you go — not saved for the end

## Week 4+ — Polish, and where "keep building for a month" pays off

Pick based on appetite, don't try to do all of them:
- [ ] Scenario simulator: heatwave, EV charging surge, grid outage — how does the market behave under stress?
- [ ] Scale to more households, check the market mechanism still clears sensibly at scale
- [ ] Dynamic pricing under grid-stress events
- [ ] Real deployment — Streamlit Cloud or a small VPS, so it's a live link, not just a repo
- [ ] Swap dashboard to FastAPI + React now that the underlying system is stable
- [ ] Write a short case-study document framed as a business outcome ("agents that learn to trade save households X% more than the naive baseline"), not just model metrics — this is what makes it read differently from a standard ML-only submission in an interview

## Definition of done for the project as a whole

You can point at a single number and defend it: "our RL agents produced X% more household savings than the rule-based baseline, on real Irish smart-meter data, over N simulated days." Everything else in the roadmap exists to make that sentence true and demonstrable.
