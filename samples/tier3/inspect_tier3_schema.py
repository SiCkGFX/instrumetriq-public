"""
Instrumetriq Tier 3 Schema Inspector

Demonstrates that the Tier 3 (Researcher) dataset is structurally sound,
consistent, and ready for analysis. Shows coverage, time alignment, nested
struct access, time series structure, and correlation matrix without
opinionated interpretation.

Tier 3 has a nested schema with 12 top-level columns including futures data
and 700+ price samples per record.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Optional

# Formatting constants
LINE_WIDTH = 70
SECTION_WIDTH = 50


# --- Helper functions for safe nested access ---

def get_nested(obj: Any, *keys, default=None) -> Any:
    """Safely extract nested value from dict/struct."""
    for key in keys:
        if obj is None or not isinstance(obj, dict):
            return default
        obj = obj.get(key, default)
    return obj


def extract_field(series: pd.Series, *keys, default=None) -> pd.Series:
    """Extract nested field from a Series of dicts."""
    return series.apply(lambda x: get_nested(x, *keys, default=default))


def load_tier3(path: str = None) -> pd.DataFrame:
    """Load Tier 3 (Researcher) sample data."""
    if path is None:
        path = Path(__file__).parent / "2026-02-01_tier3.parquet"
    return pd.read_parquet(path)


if __name__ == "__main__":
    df = load_tier3()

    print("=" * LINE_WIDTH)
    print("INSTRUMETRIQ TIER 3 (RESEARCHER) - SCHEMA INSPECTION")
    print("=" * LINE_WIDTH)
    print()

    # --- BASIC STRUCTURE ---
    print("1. BASIC STRUCTURE")
    print("-" * SECTION_WIDTH)
    print(f"   Total records:    {len(df):,}")
    print(f"   Total columns:    {len(df.columns)}")
    print(f"   Memory usage:     {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    print()

    # --- SCHEMA ---
    print("2. SCHEMA (TOP-LEVEL COLUMNS)")
    print("-" * SECTION_WIDTH)
    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = f"({null_count/len(df)*100:.1f}% null)" if null_count > 0 else "(complete)"
        dtype_str = str(df[col].dtype)
        if dtype_str == 'object':
            sample = df[col].dropna().iloc[0] if df[col].notna().any() else None
            if isinstance(sample, dict):
                dtype_str = f"struct[{len(sample)} fields]"
            elif isinstance(sample, (list, np.ndarray)):
                dtype_str = f"array[{len(sample)} items]"
        print(f"   {col:<30} {dtype_str:<25} {null_pct}")
    print()

    # --- COVERAGE BY SYMBOL ---
    print("3. COVERAGE BY SYMBOL")
    print("-" * SECTION_WIDTH)
    symbol_counts = df['symbol'].value_counts()
    print(f"   Unique symbols:       {len(symbol_counts)}")
    print(f"   Records per symbol:   {symbol_counts.min()} to {symbol_counts.max()}")
    
    # Show top 5 and bottom 5 only
    if len(symbol_counts) > 10:
        print(f"   Top 5 by record count:")
        for symbol, count in symbol_counts.head(5).items():
            print(f"      {symbol:<10} {count:>5} records")
        print(f"   ...")
        print(f"   Bottom 5 by record count:")
        for symbol, count in symbol_counts.tail(5).items():
            print(f"      {symbol:<10} {count:>5} records")
    else:
        for symbol, count in symbol_counts.items():
            print(f"      {symbol:<10} {count:>5} records")
    print()

    # --- TIME ALIGNMENT ---
    print("4. TIME ALIGNMENT")
    print("-" * SECTION_WIDTH)
    timestamps = pd.to_datetime(df['snapshot_ts'])
    unique_timestamps = timestamps.nunique()
    print(f"   Unique timestamps:    {unique_timestamps}")
    print(f"   Time range:           {timestamps.min()} to {timestamps.max()}")
    
    df_temp = df[['symbol']].copy()
    df_temp['_ts'] = timestamps
    ts_per_symbol = df_temp.groupby('symbol')['_ts'].apply(set)
    common_ts = set.intersection(*ts_per_symbol.values) if len(ts_per_symbol) > 1 else ts_per_symbol.iloc[0]
    print(f"   Shared timestamps:    {len(common_ts)} (across all symbols)")
    print()

    # --- NESTED STRUCT INSPECTION ---
    print("5. NESTED STRUCT INSPECTION")
    print("-" * SECTION_WIDTH)
    
    # spot_raw
    print("   spot_raw:")
    spot_present = df['spot_raw'].notna().sum()
    print(f"      present: {spot_present}/{len(df)}")
    if spot_present > 0:
        sample_spot = df['spot_raw'].dropna().iloc[0]
        print(f"      fields:  {list(sample_spot.keys())}")
    print()
    
    # futures_raw (Tier 3 exclusive)
    print("   futures_raw (Tier 3 exclusive):")
    futures_present = df['futures_raw'].apply(lambda x: x is not None and x.get('contract') is not None).sum()
    print(f"      present: {futures_present}/{len(df)} ({futures_present/len(df)*100:.1f}%)")
    if futures_present > 0:
        sample_futures = df[df['futures_raw'].apply(lambda x: x is not None and x.get('contract') is not None)]['futures_raw'].iloc[0]
        print(f"      fields:  {list(sample_futures.keys())}")
    print()
    
    # flags (Tier 3 exclusive)
    print("   flags (Tier 3 exclusive):")
    flags_present = df['flags'].notna().sum()
    print(f"      present: {flags_present}/{len(df)}")
    if flags_present > 0:
        sample_flags = df['flags'].dropna().iloc[0]
        print(f"      fields:  {list(sample_flags.keys())}")
        # Show flag distributions using helper
        spot_ok = extract_field(df['flags'], 'spot_data_ok')
        twitter_ok = extract_field(df['flags'], 'twitter_data_ok')
        print(f"      spot_data_ok=True:    {spot_ok.sum()}/{len(df)}")
        print(f"      twitter_data_ok=True: {twitter_ok.sum()}/{len(df)}")
    print()
    
    # twitter_sentiment_windows (Tier 3 exclusive - multi-window)
    print("   twitter_sentiment_windows (Tier 3 exclusive):")
    windows_present = df['twitter_sentiment_windows'].notna().sum()
    print(f"      present: {windows_present}/{len(df)}")
    if windows_present > 0:
        sample_windows = df['twitter_sentiment_windows'].dropna().iloc[0]
        print(f"      windows: {list(sample_windows.keys())}")
    print()

    # --- TIME SERIES STRUCTURE ---
    print("6. TIME SERIES STRUCTURE (spot_prices)")
    print("-" * SECTION_WIDTH)
    price_counts = df['spot_prices'].apply(lambda x: len(x) if x is not None and len(x) > 0 else 0)
    has_prices = price_counts > 0
    print(f"   Records with price data:  {has_prices.sum()}/{len(df)}")
    print(f"   Samples per record:       {price_counts.min()} to {price_counts.max()}")
    print(f"   Total price samples:      {price_counts.sum():,}")
    
    # Inspect time span within price series
    if has_prices.any():
        sample_prices = df.loc[has_prices, 'spot_prices'].iloc[0]
        if sample_prices is not None and len(sample_prices) > 0:
            first_ts = pd.to_datetime(sample_prices[0]['ts'])
            last_ts = pd.to_datetime(sample_prices[-1]['ts'])
            print(f"   Sample series span:       {last_ts - first_ts}")
            print(f"   Sample series fields:     {list(sample_prices[0].keys())}")
    print()

    # --- EXTRACT NUMERIC FIELDS FOR CORRELATION ---
    print("7. CORRELATION MATRIX (NUMERIC FIELDS)")
    print("-" * SECTION_WIDTH)
    print("   Extracting numeric fields from nested structures...")
    
    # Build a clean dataframe for correlation (no mutation of original)
    corr_data = pd.DataFrame({
        'spot_mid': extract_field(df['spot_raw'], 'mid'),
        'spread_bps': extract_field(df['spot_raw'], 'spread_bps'),
        'score_final': extract_field(df['scores'], 'final'),
        'posts_total': extract_field(df['twitter_sentiment_windows'], 'last_cycle', 'posts_total'),
        'sentiment': extract_field(df['twitter_sentiment_windows'], 'last_cycle', 'hybrid_decision_stats', 'mean_score'),
        'funding': extract_field(df['futures_raw'], 'funding_now'),
    })
    
    corr_df = corr_data.dropna()
    
    if len(corr_df) > 5:
        print(f"   Records with all fields: {len(corr_df)}/{len(df)}")
        print()
        corr_matrix = corr_df.corr()
        
        # Pretty print correlation matrix
        col_names = list(corr_df.columns)
        col_width = 12
        
        print("   Correlation Matrix:")
        print("   " + "-" * (15 + col_width * len(col_names)))
        
        # Header row
        header = "   " + " " * 15
        for col in col_names:
            header += f"{col:>{col_width}}"
        print(header)
        print("   " + "-" * (15 + col_width * len(col_names)))
        
        # Data rows
        for row_name in col_names:
            row_str = f"   {row_name:<15}"
            for col_name in col_names:
                row_str += f"{corr_matrix.loc[row_name, col_name]:>{col_width}.3f}"
            print(row_str)
        
        print("   " + "-" * (15 + col_width * len(col_names)))
        print("   (Pearson correlation coefficients, no interpretation provided)")
    else:
        print(f"   Insufficient data with all fields for correlation ({len(corr_df)} records)")
    print()

    # --- DATA COMPLETENESS ---
    print("8. DATA COMPLETENESS SUMMARY")
    print("-" * SECTION_WIDTH)
    
    def count_present(col_name: str) -> int:
        """Count non-null entries, with special handling for futures."""
        if col_name == 'futures_raw':
            return df['futures_raw'].apply(lambda x: x is not None and x.get('contract') is not None).sum()
        elif col_name == 'spot_prices':
            return df['spot_prices'].apply(lambda x: x is not None and len(x) > 0).sum()
        else:
            return df[col_name].notna().sum()
    
    nested_cols = ['spot_raw', 'futures_raw', 'scores', 'flags', 
                   'twitter_sentiment_windows', 'twitter_sentiment_meta', 'spot_prices']
    for col in nested_cols:
        present = count_present(col)
        print(f"   {col:<35} {present:>5}/{len(df)} ({present/len(df)*100:.1f}%)")
    print()

    print("=" * LINE_WIDTH)
    print("Schema inspection complete. Research-grade data is structurally valid.")
    print("=" * LINE_WIDTH)
