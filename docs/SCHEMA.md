# Schema Reference

This document provides an overview of the schema for each access tier. For exhaustive field-by-field documentation, see the detailed references below.

---

## Detailed Schema References

- [Tier 1 Schema Reference](../samples/tier1/SCHEMA_REFERENCE.md) — 19 flat columns
- [Tier 2 Schema Reference](../samples/tier2/SCHEMA_REFERENCE.md) — 8 nested columns
- [Tier 3 Schema Reference](../samples/tier3/SCHEMA_REFERENCE.md) — 12 nested columns with futures data

---

## Tier Comparison

| Aspect | Tier 1 Explorer | Tier 2 Analyst | Tier 3 Researcher |
|--------|-----------------|----------------|-------------------|
| Schema | Flat | Nested | Nested |
| Columns | 19 | 8 | 12 |
| Spot data | Summary | Full | Full |
| Futures data | — | — | ✓ |
| Sentiment | Counts only | Full cycle | Multi-window |
| Scoring factors | Final only | All factors | All factors + flags |
| Diagnostics | — | — | ✓ |
| Price time series | — | — | ✓ (700+ samples) |

---

## Quick Column Overview

### Tier 1: Explorer (19 columns)

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | string | Trading pair symbol (e.g., "BTCUSDC") |
| `snapshot_ts` | string | Observation timestamp (ISO 8601) |
| `meta_added_ts` | string | When session was admitted to watchlist |
| `meta_expires_ts` | string | Session expiration time |
| `meta_duration_sec` | double | Total session duration in seconds |
| `meta_archive_schema_version` | int64 | Schema version at archival time |
| `spot_mid` | double | Mid price from order book |
| `spot_spread_bps` | double | Bid-ask spread in basis points |
| `spot_range_pct_24h` | double | 24-hour price range as percentage |
| `spot_ticker24_chg` | double | 24-hour price change percentage |
| `derived_liq_global_pct` | double | Global liquidity percentile rank |
| `derived_spread_bps` | double | Derived spread in basis points |
| `score_final` | double | Final composite admission score |
| `sentiment_posts_total` | int64 | Total X (Twitter) posts in cycle |
| `sentiment_posts_pos` | int64 | Positive sentiment posts count |
| `sentiment_posts_neu` | int64 | Neutral sentiment posts count |
| `sentiment_posts_neg` | int64 | Negative sentiment posts count |
| `sentiment_mean_score` | double | Mean hybrid sentiment score |
| `sentiment_is_silent` | bool | No recent posts for this symbol |

### Tier 2: Analyst (8 columns)

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | string | Trading pair symbol |
| `snapshot_ts` | string | Observation timestamp |
| `meta` | struct | Session metadata (timestamps, schema version, universe linkage) |
| `spot_raw` | struct | Raw spot market data (prices, spreads, depth, microstructure) |
| `derived` | struct | Computed metrics (liquidity percentiles, depth imbalance) |
| `scores` | struct | Scoring factors (liquidity, spread, momentum, flow, etc.) |
| `twitter_sentiment_meta` | struct | Sentiment capture metadata |
| `twitter_sentiment_last_cycle` | struct | Full sentiment data for most recent cycle |

### Tier 3: Researcher (12 columns)

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | string | Trading pair symbol |
| `snapshot_ts` | string | Observation timestamp |
| `meta` | struct | Session metadata |
| `spot_raw` | struct | Raw spot market data |
| `futures_raw` | struct | USDT-margined perpetual futures data |
| `derived` | struct | Computed metrics |
| `scores` | struct | All scoring factors |
| `flags` | struct | Data quality and feature flags |
| `diag` | struct | Diagnostic metadata |
| `twitter_sentiment_windows` | struct | Multi-window sentiment (last_cycle, last_2_cycles) |
| `twitter_sentiment_meta` | struct | Sentiment capture metadata |
| `spot_prices` | list | Time series of spot price samples (700+) |

---

## File Format

All tiers are distributed as Apache Parquet files with:
- Snappy compression
- Row group size: ~50,000 rows
- Timestamps in ISO 8601 UTC format

---

## See Also

- [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) — Canonical field definitions
- [METHODOLOGY.md](./METHODOLOGY.md) — Data collection overview
