# data/

Real data sources for household demand and solar generation, plus a synthetic fallback so the team isn't blocked waiting on data access approval during week 1.

## 1. Household demand: CER Smart Metering Trial (Ireland)

The Commission for Energy Regulation ran a large-scale smart metering trial across Irish homes and small businesses (Electricity Customer Behaviour Trial, 2009–2010; ~4,600+ cleaned meters, half-hourly resolution, in kW — convert to kWh by dividing by 2 since each reading is a 30-minute interval). This is the standard open dataset used in Irish/EU smart-grid research, and it's what gives this project a credible, citable regional story instead of a synthetic-only one.

**Access:** distributed via the Irish Social Science Data Archive (ISSDA) at UCD:
`https://www.ucd.ie/issda/data/commissionforenergyregulationcer/`

This requires submitting a data request form through ISSDA — it's a standard academic-use request, not usually a long process, but **don't assume instant access.** Submit the request on Day 1, in parallel with building the skeleton pipeline against synthetic data (see below), so nobody is blocked waiting for approval.

## 2. Solar generation: PVGIS

The EU Joint Research Centre's PVGIS tool (`https://re.jrc.ec.europa.eu/pvg_tools/en/`) gives free, no-signup hourly solar generation estimates for any location in Ireland (and most of the world) given panel capacity and orientation. Simpler and faster to get running than requesting another restricted dataset — use this for solar generation rather than chasing a second data-access request.

## 3. Synthetic fallback (use this for week 1, regardless of ISSDA approval status)

Don't wait on real data access to get the end-to-end pipeline working. Generate synthetic household profiles for the skeleton pipeline:

- Demand: a simple daily pattern (morning + evening peaks, lower overnight) with household-level noise, matching the shape (not the exact values) of typical residential load curves.
- Solar: a clean daylight-hours bell curve scaled by panel capacity, with a few cloudy-day multipliers thrown in for realism.

This can live in `data/synthetic.py` as a small generator function that produces data in the same shape the real CER/PVGIS data will eventually be loaded into — so swapping synthetic for real data later is a one-file change, not a pipeline rewrite.

## Data hygiene

- Do not commit raw CER data files to the repo — they're not yours to redistribute, and it bloats the repo. Add the extracted data directory to `.gitignore` and document the exact ISSDA file/folder names each teammate needs in this file once you have access.
- Any derived/aggregated dataset that's safe to share (e.g. summary statistics, synthetic data) can be committed under `data/samples/`.
