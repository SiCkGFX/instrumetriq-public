"""
Instrumetriq Sample Data Loader

Quick start script for loading and exploring the sample parquet files.
"""

import pandas as pd


def load_tier1():
    """Load Tier 1 (Explorer) sample data."""
    df = pd.read_parquet("samples/2026-02-01_tier1.parquet")
    return df


def load_tier2():
    """Load Tier 2 (Analyst) sample data."""
    df = pd.read_parquet("samples/2026-02-01_tier2.parquet")
    return df


def load_tier3():
    """Load Tier 3 (Researcher) sample data."""
    df = pd.read_parquet("samples/2026-02-01_tier3.parquet")
    return df


if __name__ == "__main__":
    # Load Tier 1 sample
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
