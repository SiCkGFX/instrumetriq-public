"""
Instrumetriq Tier 3 Sample Loader

Quick start script for loading and exploring the Tier 3 (Researcher) parquet file.
Tier 3 has a nested schema with 12 top-level columns including futures data.
"""

import pandas as pd
from pathlib import Path


def load_tier3(path: str = None) -> pd.DataFrame:
    """Load Tier 3 (Researcher) sample data."""
    if path is None:
        path = Path(__file__).parent / "2026-02-01_tier3.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    df = load_tier3()

    print("=== Tier 3 Sample ===")
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
    
    # Extract spot mid price
    df['spot_mid'] = df['spot_raw'].apply(lambda x: x['mid'] if x else None)
    print(f"Spot mid price range: {df['spot_mid'].min():.6f} to {df['spot_mid'].max():.2f}")
    
    # Extract futures data (Tier 3 exclusive)
    df['has_futures'] = df['futures_raw'].apply(lambda x: x is not None and x.get('contract') is not None)
    df['funding_rate'] = df['futures_raw'].apply(lambda x: x['funding_now'] if x and x.get('funding_now') else None)
    futures_count = df['has_futures'].sum()
    print(f"Entries with futures data: {futures_count} ({futures_count/len(df)*100:.1f}%)")
    if futures_count > 0:
        print(f"Funding rate range: {df['funding_rate'].min():.6f} to {df['funding_rate'].max():.6f}")
    
    # Extract quality flags (Tier 3 exclusive)
    df['spot_ok'] = df['flags'].apply(lambda x: x['spot_data_ok'] if x else None)
    df['twitter_ok'] = df['flags'].apply(lambda x: x['twitter_data_ok'] if x else None)
    print(f"Spot data OK: {df['spot_ok'].sum()} / {len(df)}")
    print(f"Twitter data OK: {df['twitter_ok'].sum()} / {len(df)}")
    
    # Extract multi-window sentiment (Tier 3 exclusive)
    df['posts_last_cycle'] = df['twitter_sentiment_windows'].apply(
        lambda x: x['last_cycle']['posts_total'] if x and x.get('last_cycle') else 0
    )
    df['posts_last_2_cycles'] = df['twitter_sentiment_windows'].apply(
        lambda x: x['last_2_cycles']['posts_total'] if x and x.get('last_2_cycles') else 0
    )
    print(f"Posts (last cycle): {df['posts_last_cycle'].sum()}")
    print(f"Posts (last 2 cycles): {df['posts_last_2_cycles'].sum()}")
    print()

    # Spot prices time series (Tier 3 exclusive)
    print("=== Price Time Series ===")
    df['price_samples'] = df['spot_prices'].apply(lambda x: len(x) if x is not None and len(x) > 0 else 0)
    print(f"Price samples per entry: {df['price_samples'].min()} to {df['price_samples'].max()}")
    
    # Example: extract price series for first entry
    first_prices = df.iloc[0]['spot_prices']
    if first_prices is not None and len(first_prices) > 0:
        print(f"First entry has {len(first_prices)} price samples")
        print(f"  First sample: ts={first_prices[0]['ts']}, mid={first_prices[0]['mid']:.4f}")
        print(f"  Last sample:  ts={first_prices[-1]['ts']}, mid={first_prices[-1]['mid']:.4f}")
    print()

    print("=== Quick Stats ===")
    print(f"Unique symbols: {df['symbol'].nunique()}")
    print(f"Date range: {df['snapshot_ts'].min()} to {df['snapshot_ts'].max()}")
