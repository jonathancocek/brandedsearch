"""
Step 3: turn the raw Semrush files into the report tables.

From each raw row (keyword, 12-month average volume Nq, 12 trend values Td):
    monthly volume_i = Nq * 12 * Td_i / sum(Td)
i.e. the 12-month total, split across months in proportion to the trend.

Outputs (in output/):
  branded_volume.csv  one row per market, brand, keyword, month (the flat extract)
  branded_search_share.xlsx with tabs:
    share_apac          share of search per brand & month, all APAC markets summed
    share_by_market     same, per market
    share_overlap_area  share within CDN / DDoS / Zero Trust / SASE
    change_by_brand     MoM and 12-month change per brand (APAC and per market)
    qa_flags            MoM swings > threshold, and the month-calibration check
    top_keywords        top 50 keywords per brand, for the manual review
    method              notes and caveats

Run:  python analyze.py
"""
import io
from pathlib import Path

import pandas as pd

from keywords import build_keywords, load_config

RAW_DIR = Path("data/raw")
OUT_DIR = Path("output")


def month_labels(end_month, n=12):
    """12 month labels ending at end_month, oldest first, e.g. '2026-07'."""
    end = pd.Period(end_month, freq="M")
    return [str(end - i) for i in range(n - 1, -1, -1)]


def trend_to_monthly(avg_volume, trend_values):
    """Split a 12-month average volume into monthly volumes using the trend."""
    total = sum(trend_values)
    if avg_volume == 0 or total == 0:
        return [0.0] * len(trend_values)
    return [avg_volume * len(trend_values) * t / total for t in trend_values]


def read_raw(path):
    df = pd.read_csv(path, sep=";")
    df.columns = ["keyword", "avg_volume", "trend"]
    df["keyword"] = df["keyword"].str.lower().str.strip()
    return df


def load_monthly(cfg):
    months = month_labels(cfg["trend_end_month"])
    rows = []
    for path in sorted(RAW_DIR.glob("*.csv")):
        market = path.stem
        if market not in cfg["markets"]:          # skips test_*.csv
            continue
        for r in read_raw(path).itertuples():
            trend = [float(x) for x in str(r.trend).split(",")] if pd.notna(r.trend) else [0] * 12
            for month, vol in zip(months, trend_to_monthly(r.avg_volume, trend)):
                rows.append((market, r.keyword, month, vol, r.avg_volume))
    return pd.DataFrame(rows, columns=["market", "keyword", "month", "volume", "avg_volume_12m"])


def share_table(df, index):
    """Share of search: each brand's volume / total volume, per `index` group."""
    vol = df.groupby(index + ["brand"])["volume"].sum().reset_index()
    vol["share"] = vol["volume"] / vol.groupby(index)["volume"].transform("sum")
    return vol


def change_table(df, by):
    """MoM (latest month) and 12-month change (last 3 vs first 3 months avg)."""
    s = df.groupby(by + ["month"])["volume"].sum().reset_index().sort_values("month")
    out = []
    for key, g in s.groupby(by):
        v = g["volume"].tolist()
        out.append(list(key if isinstance(key, tuple) else (key,)) + [
            g["month"].iloc[-1], round(v[-1]),
            (v[-1] - v[-2]) / v[-2] if v[-2] else None,
            (sum(v[-3:]) / 3) / (sum(v[:3]) / 3) - 1 if sum(v[:3]) else None,
        ])
    return pd.DataFrame(out, columns=by + ["latest_month", "latest_volume",
                                           "mom_change", "change_12m_3mo_avg"])


def calibration_check(raw_monthly, cfg):
    """The anchor event (Cloudflare's Nov 2025 outage) should be the peak month."""
    a = cfg["anchor_event"]
    sub = raw_monthly[raw_monthly["keyword"] == a["keyword"]]
    rows = []
    for market, g in sub.groupby("market"):
        peak = g.loc[g["volume"].idxmax(), "month"]
        rows.append((market, a["keyword"], a["month"], peak,
                     "OK" if peak == a["month"] else "CHECK trend_end_month"))
    return pd.DataFrame(rows, columns=["market", "keyword", "expected_peak",
                                       "actual_peak", "status"])


def main():
    cfg = load_config()
    kw = build_keywords(cfg)
    raw = load_monthly(cfg)
    if raw.empty:
        raise SystemExit("No raw files in data/raw. Run extract.py first.")

    # keywords.csv rows with market="jp" only join to jp data
    df = raw.merge(kw.drop(columns="market"), on="keyword", how="left")
    df = df.dropna(subset=["brand"])
    OUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUT_DIR / "branded_volume.csv", index=False)

    share_apac = share_table(df, ["month"])
    share_mkt = share_table(df, ["market", "month"])

    area_frames = []
    for area, info in cfg["overlap_areas"].items():
        sub = df[(df["overlap_area"] == area) & df["brand"].isin(info["brands"])]
        if not sub.empty:
            t = share_table(sub, ["month"])
            t.insert(0, "overlap_area", area)
            area_frames.append(t)
    share_area = pd.concat(area_frames) if area_frames else pd.DataFrame()

    change = pd.concat([
        change_table(df, ["brand"]).assign(market="APAC total"),
        change_table(df, ["market", "brand"]),
    ])

    # QA: MoM swings above threshold, per market & brand
    thr = cfg["mom_flag_threshold"]
    s = df.groupby(["market", "brand", "month"])["volume"].sum().reset_index()
    s = s.sort_values("month")
    s["mom"] = s.groupby(["market", "brand"])["volume"].pct_change()
    flags = s[s["mom"].abs() > thr]

    top = (df.groupby(["brand", "keyword", "bucket"])["volume"].sum()
             .reset_index().sort_values("volume", ascending=False)
             .groupby("brand").head(50))

    calib = calibration_check(raw, cfg)
    months = sorted(df["month"].unique())
    method = pd.DataFrame({"note": [
        f"Window: {months[0]} to {months[-1]} (latest 12 months available in Semrush).",
        f"Markets with data: {', '.join(sorted(df['market'].unique()))}.",
        "Monthly volume = Semrush 12-month avg volume x 12 x trend share of that month.",
        "Share = brand volume / total volume of the 4 brands (core + category keywords).",
        "Overlap-area share uses category-qualified keywords and only the brands in that area.",
        "12-month change = avg of last 3 months / avg of first 3 months - 1.",
        "Semrush volumes are rounded estimates; report shares and trends, not absolutes.",
        "Low-volume keywords (10-20) often have a flat trend; they add little signal.",
        "Search share is a recall proxy, not a survey measure.",
    ]})

    with pd.ExcelWriter(OUT_DIR / "branded_search_share.xlsx") as xl:
        share_apac.to_excel(xl, sheet_name="share_apac", index=False)
        share_mkt.to_excel(xl, sheet_name="share_by_market", index=False)
        share_area.to_excel(xl, sheet_name="share_overlap_area", index=False)
        change.to_excel(xl, sheet_name="change_by_brand", index=False)
        flags.to_excel(xl, sheet_name="qa_mom_flags", index=False)
        calib.to_excel(xl, sheet_name="qa_month_calibration", index=False)
        top.to_excel(xl, sheet_name="top_keywords", index=False)
        method.to_excel(xl, sheet_name="method", index=False)

    # Console summary
    pd.set_option("display.width", 140)
    print(f"Window {months[0]} .. {months[-1]} | markets: {sorted(df['market'].unique())}")
    summary = df.groupby("brand")["volume"].sum() / df["volume"].sum()
    print("\nShare of branded search, full 12 months, all markets:")
    print((summary.sort_values(ascending=False) * 100).round(1).astype(str) + "%")
    print("\nMonth calibration check:")
    print(calib.to_string(index=False))
    print(f"\nWrote {OUT_DIR/'branded_volume.csv'} and {OUT_DIR/'branded_search_share.xlsx'}")


if __name__ == "__main__":
    main()
