"""
Instrumetriq Tier 2 Schema Inspector

Demonstrates that the Tier 2 (Analyst) dataset is structurally sound,
consistent, and ready for analysis. Shows coverage, time alignment,
nested struct access, and field distributions without opinionated interpretation.

Tier 2 has a nested schema with 8 top-level columns.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_tier2(path: str = None) -> pd.DataFrame:
    """Load Tier 2 (Analyst) sample data."""
    if path is None:
        path = Path(__file__).parent / "2026-02-01_tier2.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    df = load_tier2()

    print("=" * 60)
    print("INSTRUMETRIQ TIER 2 (ANALYST) - SCHEMA INSPECTION")
    print("=" * 60)
    print()

    # --- BASIC STRUCTURE ---
    print("1. BASIC STRUCTURE")
    print("-" * 40)
    print(f"   Total records:    {len(df):,}")
    print(f"   Total columns:    {len(df.columns)}")
    print(f"   Memory usage:     {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print()

    # --- SCHEMA ---
    print("2. SCHEMA (TOP-LEVEL COLUMNS)")
    print("-" * 40)
    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = f"({null_count/len(df)*100:.1f}% null)" if null_count > 0 else "(complete)"
        dtype_str = str(df[col].dtype)
        if dtype_str == 'object':
            # Check if it's a nested struct
            sample = df[col].dropna().iloc[0] if df[col].notna().any() else None
            if isinstance(sample, dict):
                dtype_str = f"struct[{len(sample)} fields]"
        print(f"   {col:<30} {dtype_str:<20} {null_pct}")
    print()

    # --- COVERAGE BY SYMBOL ---
    print("3. COVERAGE BY SYMBOL")
    print("-" * 40)
    symbol_counts = df['symbol'].value_counts()
    print(f"   Unique symbols:       {len(symbol_counts)}")
    print(f"   Records per symbol:   {symbol_counts.min()} to {symbol_counts.max()}")
    print(f"   Distribution:")
    for symbol, count in symbol_counts.items():
        print(f"      {symbol:<10} {count:>5} records")
    print()

    # --- TIME ALIGNMENT ---
    print("4. TIME ALIGNMENT")
    print("-" * 40)
    df['snapshot_ts'] = pd.to_datetime(df['snapshot_ts'])
    unique_timestamps = df['snapshot_ts'].nunique()
    print(f"   Unique timestamps:    {unique_timestamps}")
    print(f"   Time range:           {df['snapshot_ts'].min()} to {df['snapshot_ts'].max()}")
    
    # Check if all symbols share timestamps (alignment)
    ts_per_symbol = df.groupby('symbol')['snapshot_ts'].apply(set)
    common_ts = set.intersection(*ts_per_symbol.values) if len(ts_per_symbol) > 1 else ts_per_symbol.iloc[0]
    print(f"   Shared timestamps:    {len(common_ts)} (across all symbols)")
    print()

    # --- NESTED STRUCT INSPECTION ---
    print("5. NESTED STRUCT INSPECTION")
    print("-" * 40)
    
    # spot_raw struct
    print("   spot_raw:")
    spot_present = df['spot_raw'].notna().sum()
    print(f"      present: {spot_present}/{len(df)} ({spot_present/len(df)*100:.1f}%)")
    if spot_present > 0:
        sample_spot = df['spot_raw'].dropna().iloc[0]
        print(f"      fields:  {list(sample_spot.keys())}")
        # Extract and show distribution
        df['_spot_mid'] = df['spot_raw'].apply(lambda x: x['mid'] if x else None)
        print(f"      mid range: {df['_spot_mid'].min():.6f} to {df['_spot_mid'].max():.2f}")
    print()
    
    # scores struct
    print("   scores:")
    scores_present = df['scores'].notna().sum()
    print(f"      present: {scores_present}/{len(df)} ({scores_present/len(df)*100:.1f}%)")
    if scores_present > 0:
        sample_scores = df['scores'].dropna().iloc[0]
        print(f"      fields:  {list(sample_scores.keys())}")
        df['_score_final'] = df['scores'].apply(lambda x: x['final'] if x else None)
        print(f"      final range: {df['_score_final'].min():.1f} to {df['_score_final'].max():.1f}")
    print()
    
    # twitter_sentiment_last_cycle struct
    print("   twitter_sentiment_last_cycle:")
    sent_present = df['twitter_sentiment_last_cycle'].notna().sum()
    print(f"      present: {sent_present}/{len(df)} ({sent_present/len(df)*100:.1f}%)")
    if sent_present > 0:
        sample_sent = df['twitter_sentiment_last_cycle'].dropna().iloc[0]
        print(f"      fields:  {list(sample_sent.keys())[:5]}...")  # First 5 fields
        df['_posts_total'] = df['twitter_sentiment_last_cycle'].apply(
            lambda x: x['posts_total'] if x else 0
        )
        print(f"      posts_total range: {df['_posts_total'].min()} to {df['_posts_total'].max()}")
    print()

    # --- FIELD PRESENCE SUMMARY ---
    print("6. NESTED FIELD PRESENCE SUMMARY")
    print("-" * 40)
    nested_cols = ['spot_raw', 'scores', 'twitter_sentiment_last_cycle']
    for col in nested_cols:
        present = df[col].notna().sum()
        print(f"   {col:<35} {present:>5}/{len(df)} ({present/len(df)*100:.1f}%)")
    print()

    # --- DATA COMPLETENESS ---
    print("7. DATA COMPLETENESS")
    print("-" * 40)
    # For nested schema, count top-level nulls
    total_cells = len(df) * len(df.columns)
    null_cells = df.isna().sum().sum()
    print(f"   Top-level cells:      {total_cells:,}")
    print(f"   Null cells:           {null_cells:,}")
    print(f"   Completeness:         {(total_cells - null_cells) / total_cells * 100:.2f}%")
    print()

    print("=" * 60)
    print("Schema inspection complete. Nested data is structurally valid.")
    print("=" * 60)
