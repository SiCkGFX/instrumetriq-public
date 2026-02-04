"""
Instrumetriq Tier 1 (Explorer) Schema Inspector

Validates structural integrity and displays coverage statistics
for the flat 19-column Tier 1 dataset.
"""

import pandas as pd
from pathlib import Path

LINE_WIDTH = 60
SECTION_WIDTH = 40


def load_tier1(path: str = None) -> pd.DataFrame:
    """Load the latest Tier 1 sample parquet."""
    if path is None:
        samples_dir = Path(__file__).parent.parent
        week_folders = sorted(samples_dir.glob("week_*"), reverse=True)
        if not week_folders:
            raise FileNotFoundError("No week_* folders found in samples/")
        parquets = list(week_folders[0].glob("*_tier1.parquet"))
        if not parquets:
            raise FileNotFoundError(f"No tier1 parquet in {week_folders[0]}")
        path = parquets[0]
    return pd.read_parquet(path)


if __name__ == "__main__":
    df = load_tier1()

    print("=" * LINE_WIDTH)
    print("INSTRUMETRIQ TIER 1 (EXPLORER) — SCHEMA INSPECTION")
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
        print(f"   {col:<30} {str(df[col].dtype):<12} {status}")
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

    # 5. Sentiment distribution
    print("5. SENTIMENT DISTRIBUTION")
    print("-" * SECTION_WIDTH)
    score = df["sentiment_mean_score"]
    print(f"   min:     {score.min():.4f}")
    print(f"   median:  {score.median():.4f}")
    print(f"   max:     {score.max():.4f}")
    print()

    # 6. Boolean flags
    print("6. BOOLEAN FLAGS")
    print("-" * SECTION_WIDTH)
    for col in ["sentiment_is_silent", "sentiment_score_flip"]:
        if col in df.columns:
            true_count = df[col].sum()
            print(f"   {col}: {true_count}/{len(df)} True")
    print()

    # 7. Completeness
    print("7. COMPLETENESS")
    print("-" * SECTION_WIDTH)
    total = len(df) * len(df.columns)
    nulls = df.isna().sum().sum()
    print(f"   Cells:        {total:,}")
    print(f"   Complete:     {(total - nulls) / total * 100:.2f}%")
    print()

    print("=" * LINE_WIDTH)
    print("Inspection complete.")
    print("=" * LINE_WIDTH)
