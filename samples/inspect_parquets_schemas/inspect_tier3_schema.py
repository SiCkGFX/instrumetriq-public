"""
Instrumetriq Tier 3 (Researcher) Schema Inspector

Validates structural integrity and displays coverage statistics
for the nested 12-column Tier 3 dataset, including futures data
and 700+ price samples per record.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any

LINE_WIDTH = 70
SECTION_WIDTH = 50


def load_tier3(path: str = None) -> pd.DataFrame:
    """Load the latest Tier 3 sample parquet."""
    if path is None:
        samples_dir = Path(__file__).parent.parent
        week_folders = sorted(samples_dir.glob("week_*"), reverse=True)
        if not week_folders:
            raise FileNotFoundError("No week_* folders found in samples/")
        parquets = list(week_folders[0].glob("*_tier3.parquet"))
        if not parquets:
            raise FileNotFoundError(f"No tier3 parquet in {week_folders[0]}")
        path = parquets[0]
    return pd.read_parquet(path)


def get_nested(obj: Any, *keys, default=None) -> Any:
    """Safely extract a nested value from a dict."""
    for key in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(key, default)
    return obj


def extract_field(series: pd.Series, *keys, default=None) -> pd.Series:
    """Extract a nested field from a Series of dicts."""
    return series.apply(lambda x: get_nested(x, *keys, default=default))


def describe_dtype(series: pd.Series) -> str:
    """Return a human-readable dtype description."""
    if series.dtype != "object":
        return str(series.dtype)
    sample = series.dropna().iloc[0] if series.notna().any() else None
    if isinstance(sample, dict):
        return f"struct[{len(sample)}]"
    if isinstance(sample, (list, np.ndarray)):
        return f"array[{len(sample)}]"
    return "object"


if __name__ == "__main__":
    df = load_tier3()

    print("=" * LINE_WIDTH)
    print("INSTRUMETRIQ TIER 3 (RESEARCHER) — SCHEMA INSPECTION")
    print("=" * LINE_WIDTH)
    print()

    # 1. Basic structure
    print("1. BASIC STRUCTURE")
    print("-" * SECTION_WIDTH)
    print(f"   Records:     {len(df):,}")
    print(f"   Columns:     {len(df.columns)}")
    print(f"   Memory:      {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    print()

    # 2. Schema
    print("2. SCHEMA")
    print("-" * SECTION_WIDTH)
    for col in df.columns:
        nulls = df[col].isna().sum()
        status = f"({nulls} null)" if nulls > 0 else ""
        print(f"   {col:<32} {describe_dtype(df[col]):<18} {status}")
    print()

    # 3. Symbol coverage
    print("3. SYMBOL COVERAGE")
    print("-" * SECTION_WIDTH)
    counts = df["symbol"].value_counts()
    print(f"   Unique symbols:   {len(counts)}")
    print(f"   Records/symbol:   {counts.min()}–{counts.max()}")
    print()

    # 4. Time alignment
    print("4. TIME ALIGNMENT")
    print("-" * SECTION_WIDTH)
    ts = pd.to_datetime(df["snapshot_ts"])
    print(f"   Range:   {ts.min()} → {ts.max()}")
    print(f"   Span:    {ts.max() - ts.min()}")
    print()

    # 5. Nested struct inspection
    print("5. NESTED STRUCTS")
    print("-" * SECTION_WIDTH)

    for col in ["spot_raw", "futures_raw", "scores", "flags", "twitter_sentiment_windows"]:
        if col == "futures_raw":
            present = df[col].apply(
                lambda x: x is not None and x.get("contract") is not None
            ).sum()
        else:
            present = df[col].notna().sum()
        pct = present / len(df) * 100
        print(f"   {col}: {present}/{len(df)} ({pct:.0f}%)")
    print()

    # 6. Time series structure
    print("6. TIME SERIES (spot_prices)")
    print("-" * SECTION_WIDTH)
    price_lens = df["spot_prices"].apply(lambda x: len(x) if x is not None and len(x) > 0 else 0)
    has_prices = price_lens > 0
    print(f"   Records with prices:  {has_prices.sum()}/{len(df)}")
    print(f"   Samples per record:   {price_lens.min()}–{price_lens.max()}")
    print(f"   Total samples:        {price_lens.sum():,}")
    print()

    # 7. Correlation matrix
    print("7. CORRELATION MATRIX")
    print("-" * SECTION_WIDTH)

    corr_data = pd.DataFrame({
        "spot_mid": extract_field(df["spot_raw"], "mid"),
        "spread_bps": extract_field(df["spot_raw"], "spread_bps"),
        "score": extract_field(df["scores"], "final"),
        "posts": extract_field(df["twitter_sentiment_windows"], "last_cycle", "posts_total"),
        "sentiment": extract_field(
            df["twitter_sentiment_windows"], "last_cycle", "hybrid_decision_stats", "mean_score"
        ),
        "funding": extract_field(df["futures_raw"], "funding_now"),
    }).dropna()

    if len(corr_data) >= 10:
        print(f"   Records with all fields: {len(corr_data)}/{len(df)}")
        print()
        corr = corr_data.corr()
        cols = list(corr.columns)
        w = 10

        print("   " + " " * 12 + "".join(f"{c:>{w}}" for c in cols))
        print("   " + "-" * (12 + w * len(cols)))
        for row in cols:
            vals = "".join(f"{corr.loc[row, c]:>{w}.3f}" for c in cols)
            print(f"   {row:<12}{vals}")
    else:
        print(f"   Insufficient data ({len(corr_data)} records)")
    print()

    # 8. Completeness
    print("8. COMPLETENESS")
    print("-" * SECTION_WIDTH)
    nested_cols = [
        "spot_raw", "futures_raw", "scores", "flags",
        "twitter_sentiment_windows", "twitter_sentiment_meta", "spot_prices"
    ]
    for col in nested_cols:
        if col == "futures_raw":
            present = df[col].apply(
                lambda x: x is not None and x.get("contract") is not None
            ).sum()
        elif col == "spot_prices":
            present = df[col].apply(lambda x: x is not None and len(x) > 0).sum()
        else:
            present = df[col].notna().sum()
        pct = present / len(df) * 100
        print(f"   {col:<30} {present:>5}/{len(df)} ({pct:.0f}%)")
    print()

    print("=" * LINE_WIDTH)
    print("Inspection complete.")
    print("=" * LINE_WIDTH)
