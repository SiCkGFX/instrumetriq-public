"""
Instrumetriq Tier 2 Sample Loader

Quick start script for loading and exploring the Tier 2 (Analyst) parquet file.
Tier 2 has a nested schema with 8 top-level columns.
"""

import pandas as pd
from pathlib import Path


def load_tier2(path: str = None) -> pd.DataFrame:
    """Load Tier 2 (Analyst) sample data."""
    if path is None:
        path = Path(__file__).parent / "2026-02-01_tier2.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    df = load_tier2()

    print("=== Tier 2 Sample ===")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print()

    print("Top-level columns:")
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")
    print()

    print("First 3 rows (symbol + snapshot_ts):")
    print(df[['symbol', 'snapshot_ts']].head(3))
    print()

    # Accessing nested data
    print("=== Accessing Nested Data ===")
    
    # Extract spot mid price from spot_raw struct
    df['spot_mid'] = df['spot_raw'].apply(lambda x: x['mid'] if x else None)
    print(f"Spot mid price range: {df['spot_mid'].min():.6f} to {df['spot_mid'].max():.2f}")
    
    # Extract final score from scores struct
    df['score_final'] = df['scores'].apply(lambda x: x['final'] if x else None)
    print(f"Score final range: {df['score_final'].min():.1f} to {df['score_final'].max():.1f}")
    
    # Extract sentiment from twitter_sentiment_last_cycle struct
    df['posts_total'] = df['twitter_sentiment_last_cycle'].apply(
        lambda x: x['posts_total'] if x else 0
    )
    df['mean_score'] = df['twitter_sentiment_last_cycle'].apply(
        lambda x: x['hybrid_decision_stats']['mean_score'] if x and x.get('hybrid_decision_stats') else None
    )
    print(f"Total posts range: {df['posts_total'].min()} to {df['posts_total'].max()}")
    print(f"Mean sentiment score: {df['mean_score'].mean():.3f}")
    print()

    print("=== Quick Stats ===")
    print(f"Unique symbols: {df['symbol'].nunique()}")
    print(f"Date range: {df['snapshot_ts'].min()} to {df['snapshot_ts'].max()}")
