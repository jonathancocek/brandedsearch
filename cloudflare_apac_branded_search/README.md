# Branded Search Share: Cloudflare vs. Competitors (APAC)

A low-cost Semrush pull of branded search volume for **Cloudflare, Akamai, Zscaler and Palo Alto Networks** across **13 APAC markets**. It covers the latest 12 months Semrush has, and is used as a proxy for brand recall.

Adapted from the Darktrace competitor-intelligence repo (`jonathancocek/brandedsearch`). It keeps the Semrush approach and drops the dashboard and Snowflake parts. Snowflake can come back if John Massey wants this to run monthly.

## Status (3 Nov 2026)

| Market | Data |
|---|---|
| Australia (`au`) | ✅ pulled, results in `output/` |
| nz, sg, hk, jp, kr, in, id, my, ph, th, vn, tw | ⏳ not pulled: **Semrush API units balance hit zero** |

To finish, top up the units, then run `python extract.py` followed by `python analyze.py`. Australia is skipped automatically, so it isn't paid for twice.

## What it costs

| | Units |
|---|---|
| This project, all 13 markets (live data) | **~8,000** (61–65 keywords × 10 units × 13 markets) |
| Remaining 12 markets | **~7,400** (`python extract.py --dry-run` shows the exact figure) |
| Already spent (calibration + Australia) | 1,050 |
| Original method (12 historical calls per keyword) | ~970,000 |

Semrush rates as measured on 3 Nov 2026: a live `phrase_these` row costs **10 units**, and a historical row (`display_date`) costs **100 units**. Zero-volume rows are charged too.

## How the method changed from the original guide, and why

1. **One live call per market instead of 12 historical calls.** Each `phrase_these` row includes `Nq` (Semrush's 12-month average volume) and `Td` (12 monthly trend values). The monthly volume is calculated as:

   `monthly volume = Nq × 12 × Td(month) / sum(Td)`

2. **Historical calls give the wrong number for this job.** With `display_date`, `Nq` is still a 12-month average, not that month's volume. The Jul 2026 and Oct 2026 snapshots for "cloudflare" (AU) both return 49,500. Summing 12 of those calls would have cost 10x as much and smoothed the monthly trend away.

3. **The window is Aug 2025 – Jul 2026, not Nov 2025 – Oct 2026.** Semrush's live data ends in Jul 2026. The month labels are anchored on Cloudflare's global outage of 18 Nov 2025, which is the peak month in every snapshot. `analyze.py` re-checks this in each market (tab `qa_month_calibration`). If Semrush updates its data, change `trend_end_month` in `config.yaml`.

4. **No paid discovery reports.** The keyword list is built from `config.yaml`: brand names, product names, and brand + category word. That costs 0 units. Running `phrase_fullsearch`/`domain_organic` in 13 markets would cost far more. Noise terms (login, status, outage…) are never pulled, and ambiguous terms (*palo alto*, *cortex*, *prisma*) are left out.

## Files

| File | What it does |
|---|---|
| `config.yaml` | Brands, product terms, markets, overlap areas, time window. **Edit this, not the code.** |
| `keywords.py` | Builds `keywords.csv` (brand, keyword, bucket, overlap_area, market) |
| `extract.py` | Calls the Semrush API, saves `data/raw/<market>.csv`, logs units used |
| `analyze.py` | Builds `output/branded_volume.csv` and `output/branded_search_share.xlsx` |
| `tests/` | Small checks of the volume maths (`python -m pytest`) |

Tabs in the Excel file: `share_apac`, `share_by_market`, `share_overlap_area`, `change_by_brand` (MoM and 12-month change), `qa_mom_flags` (swings over 25%), `qa_month_calibration`, `top_keywords` (for the manual review), `method`.

## Setup (first time)

```bash
python -m venv venv
```

On Mac/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

Set the Transmission Semrush key in your terminal. Never paste it into code or commit it.

On Mac/Linux:
```bash
export SEMRUSH_API_KEY=your_key_here
```

On Windows:
```bash
set SEMRUSH_API_KEY=your_key_here
```

## Run

```bash
python keywords.py
```

```bash
python extract.py --dry-run
```

```bash
python extract.py --test
```

```bash
python extract.py
```

```bash
python analyze.py
```

- `--dry-run` prints the cost without spending anything.
- `--test` uses about 30 units to check that the key works.
- The full run checks your unit balance first and stops if it isn't enough.
- `--markets au sg` limits a run to the markets you name.

## Keyword buckets

- **core**: brand or product name only (e.g. `zscaler`, `prisma access`, `cloudflare workers`)
- **category**: brand + overlap word. These are only built where the brand competes:

| Overlap area | Brands | Words |
|---|---|---|
| CDN | Cloudflare, Akamai | cdn |
| DDoS and app security | Cloudflare, Akamai | ddos, waf |
| Zero Trust | all four | zero trust, ztna |
| SASE / SSE | Cloudflare, Zscaler, Palo Alto | sase, sse |

- **noise**: login, status, down, outage, support, careers, stock… These are never pulled.
- **local**: Japanese and Korean brand names, queried only in `jp` / `kr`.

## QA checklist

- [ ] Review `top_keywords` by hand. Move misclassified terms out of `config.yaml`.
- [ ] Spot-check 3 months per brand in the Semrush UI (Keyword Overview → Trend).
- [ ] Review `qa_mom_flags` (outages, launches, Semrush updates).
- [ ] Check `qa_month_calibration` shows OK in every market.
- [ ] Units used are logged in `data/units_log.csv`.

## Caveats

- Semrush volumes are rounded estimates, and Semrush rounds the trend values too.
- Keywords at 10–20 searches often have a flat trend and add little signal.
- The plain term "cloudflare" is inflated by outage searches and consumer use (1.1.1.1, WARP). Look at Cloudflare's share with and without the Nov–Dec 2025 outage months.
- Akamai's total includes "linode" (an Akamai product). Remove it from `config.yaml` if it shouldn't count.
- Report shares and trends, not absolute volumes. Search share is a recall proxy, not a survey measure.

## Open questions for John Massey

- [ ] Cadence: one-time pull, or monthly? A monthly run costs ~8,000 units. If monthly, should it load into Snowflake (the Darktrace repo has the loader pattern)?
- [ ] Markets: confirm the 13 Tier-1 APAC markets. Tier 2 (pk, bd, lk, np, kh, mn, bn) is listed in `config.yaml` but not pulled.
