"""
Step 1: build the branded keyword list from config.yaml -> keywords.csv

Why build the list from config instead of running Semrush discovery reports?
Discovery (phrase_fullsearch / phrase_related / domain_organic) is charged per
row returned and would have to be repeated in all 13 APAC markets. Building the
candidates ourselves costs 0 units, and the extraction step only returns
(and charges for) keywords that actually have search volume.

Run:  python keywords.py
"""
import pandas as pd
import yaml

CONFIG_PATH = "config.yaml"
OUTPUT_PATH = "keywords.csv"


def load_config(path=CONFIG_PATH):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_keywords(cfg):
    """Return a DataFrame: brand, keyword, bucket, overlap_area, market.

    market = "all" for terms queried in every market, or a database code
    (e.g. "jp") for local-script terms queried only in that market.
    """
    rows = []
    for brand, info in cfg["brands"].items():
        for term in info["core_terms"]:
            rows.append((brand, term, "core", "", "all"))

        for market, terms in (info.get("local_terms") or {}).items():
            for term in terms:
                rows.append((brand, term, "core", "", market))

        # brand + category word, e.g. "zscaler ztna" — only for areas where
        # this brand actually competes (no "zscaler cdn"), to save units
        for area, area_info in cfg["overlap_areas"].items():
            if brand not in area_info["brands"]:
                continue
            for word in area_info["words"]:
                rows.append((brand, f"{info['combo_name']} {word}",
                             "category", area, "all"))

    df = pd.DataFrame(rows, columns=["brand", "keyword", "bucket",
                                     "overlap_area", "market"])
    df["keyword"] = df["keyword"].str.lower().str.strip()

    # Safety net: never pull noise terms
    noise = "|".join(cfg["noise_words"])
    df = df[~df["keyword"].str.contains(noise, regex=True)]

    return df.drop_duplicates(subset=["keyword", "market"]).reset_index(drop=True)


def keywords_for_market(kw, market):
    """Keywords to query in one market (shared terms + that market's local terms)."""
    return kw[kw["market"].isin(["all", market])]["keyword"].tolist()


if __name__ == "__main__":
    cfg = load_config()
    kw = build_keywords(cfg)
    kw.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(kw)} keywords to {OUTPUT_PATH}")
    print(kw.groupby(["brand", "bucket"]).size().to_string())
