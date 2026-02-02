"""
Instrumetriq Tier 1 Sample Loader

Quick start script for loading and exploring the Tier 1 (Explorer) parquet file.
Tier 1 has a flat schema with 19 columns.
"""

import pandas as pd
from pathlib import Path


def load_tier1(path: str = None) -> pd.DataFrame:
    """Load Tier 1 (Explorer) sample data."""
    if path is None:
        path = Path(__file__).parent / "2026-02-01_tier1.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    df = load_tier1()

    print("=== Tier 1 Sample ===")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print()

    print("Schema:")
    print(df.dtypes)
    print()

    print("First 5 rows:")
    print(df.head())
    print()

    # Basic analysis example
    print("=== Quick Stats ===")
    print(f"Unique symbols: {df['symbol'].nunique()}")
    print(f"Date range: {df['snapshot_ts'].min()} to {df['snapshot_ts'].max()}")
    print(f"Mean sentiment score: {df['sentiment_mean_score'].mean():.3f}")
    print(f"Silent observations: {df['sentiment_is_silent'].sum()} ({df['sentiment_is_silent'].mean()*100:.1f}%)")
