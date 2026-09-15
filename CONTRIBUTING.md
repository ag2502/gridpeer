# Contributing

## Branching

- `main` is protected — no direct pushes, everything goes through a PR.
- Branch naming: `feature/<module>-<short-description>`, e.g. `feature/agents-baseline-bidder`, `feature/sim-double-auction`.
- One PR per logical change. Small PRs review faster and are far easier to unblock than one giant weekly merge.

## Commits

Conventional Commits format:

```
feat: add continuous double auction clearing logic
fix: correct kWh/kW unit mismatch in HouseholdProfile
docs: update simulation module README with run instructions
refactor: extract order matching into its own function
test: add contract test for AgentDecision serialization
```

## Pull requests

- At least one reviewer required before merge. Rotate who reviews — don't let the same person become the bottleneck.
- **PR description must state which files in `shared/` were touched, if any.** If the answer is "none," say so explicitly — it tells the reviewer they don't need to check for a breaking contract change.
- CI (lint + tests) must pass before merge — see `.github/workflows/ci.yml`.

## Changing a shared schema (`shared/schemas.py`)

This is the one process worth being disciplined about, because a careless change here breaks a module owned by someone who isn't in the room.

1. Open a GitHub issue tagged `schema-change` describing the proposed change and why the current contract doesn't cover the case.
2. Get an explicit thumbs-up from all four people in the issue thread — not just the two whose modules are directly affected. A field you don't currently use might be one you're about to need.
3. Only then open the PR. Bump the version comment at the top of `shared/schemas.py`.
4. In the same PR, update every module that constructs or consumes the changed model. Don't leave that for a follow-up PR — a half-migrated schema is worse than not changing it yet.

## Local dev setup

```bash
git clone <repo-url>
cd gridpeer
make setup     # creates venv, installs all module dependencies
make test      # should pass on a clean clone before you write anything
```

## Task tracking

Use the GitHub Projects board, not a side WhatsApp thread, for anything that isn't a 2-minute question — the point is that all four of you can see what's in flight without asking.
