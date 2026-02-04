"""
Instrumetriq Tier 2 (Analyst) Schema Inspector

Validates structural integrity and displays coverage statistics
for the nested 8-column Tier 2 dataset.
"""

import time
import pandas as pd
from pathlib import Path

LINE_WIDTH = 60
SECTION_WIDTH = 40


def load_tier2(path: str = None) -> pd.DataFrame:
    """Load the latest Tier 2 sample parquet."""
    if path is None:
        samples_dir = Path(__file__).parent.parent
        week_folders = sorted(samples_dir.glob("week_*"), reverse=True)
        if not week_folders:
            raise FileNotFoundError("No week_* folders found in samples/")
        parquets = list(week_folders[0].glob("*_tier2.parquet"))
        if not parquets:
            raise FileNotFoundError(f"No tier2 parquet in {week_folders[0]}")
        path = parquets[0]
    return pd.read_parquet(path)


def describe_dtype(series: pd.Series) -> str:
    """Return a human-readable dtype description."""
    if series.dtype != "object":
        return str(series.dtype)
    sample = series.dropna().iloc[0] if series.notna().any() else None
    if isinstance(sample, dict):
        return f"struct[{len(sample)}]"
    return "object"


if __name__ == "__main__":
    start = time.perf_counter()
    df = load_tier2()
    load_time = time.perf_counter() - start

    print("=" * LINE_WIDTH)
    print("INSTRUMETRIQ TIER 2 (ANALYST) — SCHEMA INSPECTION")
    print("=" * LINE_WIDTH)
    print()

    # 1. Basic structure
    print("1. BASIC STRUCTURE")
    print("-" * SECTION_WIDTH)
    print(f"   Records:     {len(df):,}")
    print(f"   Columns:     {len(df.columns)}")
    print(f"   Memory:      {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print()

    # 2. Schema
    print("2. SCHEMA")
    print("-" * SECTION_WIDTH)
    for col in df.columns:
        nulls = df[col].isna().sum()
        status = f"({nulls} null)" if nulls > 0 else ""
        print(f"   {col:<30} {describe_dtype(df[col]):<12} {status}")
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

    for col in ["spot_raw", "scores", "twitter_sentiment_last_cycle"]:
        present = df[col].notna().sum()
        pct = present / len(df) * 100
        print(f"   {col}: {present}/{len(df)} ({pct:.0f}%)")
        if present > 0:
            sample = df[col].dropna().iloc[0]
            fields = list(sample.keys())[:5]
            suffix = "..." if len(sample) > 5 else ""
            print(f"      fields: {fields}{suffix}")
    print()

    # 6. Completeness
    print("6. COMPLETENESS")
    print("-" * SECTION_WIDTH)
    total = len(df) * len(df.columns)
    nulls = df.isna().sum().sum()
    print(f"   Top-level cells:  {total:,}")
    print(f"   Complete:         {(total - nulls) / total * 100:.2f}%")
    print()

    print("=" * LINE_WIDTH)
    print(f"Inspection complete. Parquet loaded in {load_time:.2f}s.")
    print("=" * LINE_WIDTH)
