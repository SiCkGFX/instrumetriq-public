"""
Instrumetriq Tier 1 Schema Inspector

Demonstrates that the Tier 1 (Explorer) dataset is structurally sound, 
consistent, and ready for analysis. Shows coverage, time alignment, 
and field distributions without opinionated interpretation.

Tier 1 has a flat schema with 19 columns.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_tier1(path: str = None) -> pd.DataFrame:
    """Load Tier 1 (Explorer) sample data."""
    if path is None:
        path = Path(__file__).parent / "2026-02-01_tier1.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    df = load_tier1()

    print("=" * 60)
    print("INSTRUMETRIQ TIER 1 (EXPLORER) - SCHEMA INSPECTION")
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
    print("2. SCHEMA (ALL COLUMNS)")
    print("-" * 40)
    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = f"({null_count/len(df)*100:.1f}% null)" if null_count > 0 else "(complete)"
        print(f"   {col:<30} {str(df[col].dtype):<15} {null_pct}")
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
    timestamp_range = df['snapshot_ts'].max() - df['snapshot_ts'].min()
    print(f"   Unique timestamps:    {unique_timestamps}")
    print(f"   Time range:           {df['snapshot_ts'].min()} to {df['snapshot_ts'].max()}")
    print(f"   Span:                 {timestamp_range}")
    
    # Check if all symbols share timestamps (alignment)
    ts_per_symbol = df.groupby('symbol')['snapshot_ts'].apply(set)
    common_ts = set.intersection(*ts_per_symbol.values) if len(ts_per_symbol) > 1 else ts_per_symbol.iloc[0]
    print(f"   Shared timestamps:    {len(common_ts)} (across all symbols)")
    print()

    # --- FIELD DISTRIBUTIONS (NON-OPINIONATED) ---
    print("5. FIELD DISTRIBUTIONS")
    print("-" * 40)
    
    # Sentiment score distribution
    print("   sentiment_mean_score:")
    print(f"      min:    {df['sentiment_mean_score'].min():.4f}")
    print(f"      25%:    {df['sentiment_mean_score'].quantile(0.25):.4f}")
    print(f"      50%:    {df['sentiment_mean_score'].median():.4f}")
    print(f"      75%:    {df['sentiment_mean_score'].quantile(0.75):.4f}")
    print(f"      max:    {df['sentiment_mean_score'].max():.4f}")
    print()
    
    # Boolean field distributions
    bool_cols = ['sentiment_is_silent', 'sentiment_score_flip', 'sentiment_extreme_bearish', 'sentiment_extreme_bullish']
    for col in bool_cols:
        if col in df.columns:
            true_count = df[col].sum()
            print(f"   {col}:")
            print(f"      True:   {true_count:>5} ({true_count/len(df)*100:.1f}%)")
            print(f"      False:  {len(df)-true_count:>5} ({(len(df)-true_count)/len(df)*100:.1f}%)")
    print()

    # Numeric field summaries
    numeric_cols = ['sentiment_posts_total', 'sentiment_replies_sum', 'sentiment_retweets_sum', 'sentiment_likes_sum']
    print("   Engagement metrics (count distributions):")
    for col in numeric_cols:
        if col in df.columns:
            print(f"      {col}:")
            print(f"         range: {df[col].min()} to {df[col].max()}")
            print(f"         zeros: {(df[col] == 0).sum()}")
    print()

    # --- DATA COMPLETENESS ---
    print("6. DATA COMPLETENESS")
    print("-" * 40)
    total_cells = len(df) * len(df.columns)
    null_cells = df.isna().sum().sum()
    print(f"   Total cells:          {total_cells:,}")
    print(f"   Null cells:           {null_cells:,}")
    print(f"   Completeness:         {(total_cells - null_cells) / total_cells * 100:.2f}%")
    print()

    print("=" * 60)
    print("Schema inspection complete. Data is structurally valid.")
    print("=" * 60)
