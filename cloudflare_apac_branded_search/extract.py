"""
Step 2: pull branded search data from the Semrush API, one call per market.

Cost-saving design (see README for the numbers):
  * ONE live phrase_these call per market returns, for every keyword, the
    12-month average volume (Nq) AND a 12-value monthly trend (Td).
    analyze.py turns those into 12 monthly volumes. That is ~10 units per
    keyword per market, instead of 100 units x 12 months for historical calls.
  * Raw responses are saved to data/raw/<market>.csv. A market that already
    has a file is SKIPPED, so you never pay twice for the same data.
    Delete the file (or use --force) to re-pull it.
  * --dry-run prints the unit cost without spending anything.
  * --test pulls 3 keywords in 1 market (~30 units) to check the key works.

Usage:
  export SEMRUSH_API_KEY=...          (Windows: set SEMRUSH_API_KEY=...)
  python extract.py --dry-run
  python extract.py --test
  python extract.py                   # all markets in config.yaml
  python extract.py --markets au sg   # just some markets
"""
import argparse
import os
import sys
import time
from pathlib import Path

import requests

from keywords import build_keywords, keywords_for_market, load_config

API_URL = "https://api.semrush.com/"
BALANCE_URL = "https://www.semrush.com/users/countapiunits.html"
RAW_DIR = Path("data/raw")


def get_key():
    key = os.environ.get("SEMRUSH_API_KEY")
    if not key:
        sys.exit("SEMRUSH_API_KEY is not set. See README -> Setup.")
    return key


def units_balance(key):
    r = requests.get(BALANCE_URL, params={"key": key}, timeout=30)
    r.raise_for_status()
    return int(r.text.strip())


def pull_market(key, market, terms, snapshot_date=None):
    """One phrase_these call (max 100 keywords). Returns the raw text."""
    params = {
        "type": "phrase_these",
        "key": key,
        "database": market,
        "phrase": ";".join(terms),
        "export_columns": "Ph,Nq,Td",
    }
    if snapshot_date:                      # e.g. "2026-10-15" -> "20261015"
        params["display_date"] = snapshot_date.replace("-", "")
    r = requests.get(API_URL, params=params, timeout=120)
    r.raise_for_status()
    if r.text.startswith("ERROR"):
        raise RuntimeError(f"{market}: {r.text.strip()}")
    return r.text


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--markets", nargs="*", help="database codes, default = all in config")
    p.add_argument("--dry-run", action="store_true", help="show cost only")
    p.add_argument("--test", action="store_true", help="3 keywords, 1 market")
    p.add_argument("--force", action="store_true", help="re-pull markets already saved")
    args = p.parse_args()

    cfg = load_config()
    kw = build_keywords(cfg)
    markets = args.markets or list(cfg["markets"])
    snapshot = cfg.get("snapshot_date")
    unit_cost = cfg["units_per_row_historical" if snapshot else "units_per_row_live"]

    if args.test:
        markets = markets[:1]

    plan = []
    for m in markets:
        if m not in cfg["markets"]:
            sys.exit(f"Unknown market '{m}'. Add it to config.yaml first.")
        terms = keywords_for_market(kw, m)
        if args.test:
            terms = terms[:3]
        out = RAW_DIR / (f"test_{m}.csv" if args.test else f"{m}.csv")
        if out.exists() and not args.force:
            print(f"  skip {m}: {out} already exists (no units spent)")
            continue
        plan.append((m, terms, out))

    total = sum(len(t) for _, t, _ in plan) * unit_cost
    print(f"Plan: {len(plan)} market call(s), estimated cost {total:,} units "
          f"({'snapshot ' + snapshot if snapshot else 'live data'})")
    if args.dry_run or not plan:
        return

    key = get_key()
    balance = units_balance(key)
    print(f"Units balance before: {balance:,}")
    if balance < total:
        sys.exit(f"Not enough units ({balance:,} < {total:,}). Nothing was pulled.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for m, terms, out in plan:
        text = pull_market(key, m, terms, snapshot)
        out.write_text(text, encoding="utf-8")
        print(f"  {m}: {len(text.strip().splitlines()) - 1} keywords -> {out}")
        time.sleep(0.5)

    after = units_balance(key)
    print(f"Units balance after: {after:,}  (used {balance - after:,})")
    with open("data/units_log.csv", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M')},{','.join(m for m, _, _ in plan)},"
                f"{balance - after}\n")


if __name__ == "__main__":
    main()
