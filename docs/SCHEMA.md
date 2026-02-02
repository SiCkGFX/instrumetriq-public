# Schema Reference

This document describes the schema for each access tier of the Instrumetriq dataset.

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

---

## Tier 1: Explorer

Flat schema with 19 columns. All nested structures are flattened for simple analysis.

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

---

## Tier 2: Analyst

Nested schema with 8 top-level columns providing full spot market detail and sentiment breakdown.

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

### meta (Tier 2)

| Field | Type |
|-------|------|
| `added_ts` | string |
| `archive_schema_version` | int64 |
| `duration_sec` | double |
| `expires_ts` | string |
| `schema_version` | int64 |
| `session_id` | string |
| `source` | string |
| `universe_snapshot_ts` | string |

### spot_raw (Tier 2)

| Field | Type |
|-------|------|
| `ask` | double |
| `bid` | double |
| `mid` | double |
| `last` | double |
| `spread_bps` | double |
| `depth_5bps_quote` | double |
| `depth_10bps_quote` | double |
| `depth_25bps_quote` | double |
| `range_pct_24h` | double |
| `ticker24_chg` | double |
| `obi_5` | double |
| `taker_buy_ratio_5m` | double |

### scores (Tier 2)

| Field | Type |
|-------|------|
| `final` | double |
| `liq` | double |
| `spread` | double |
| `depth` | double |
| `flow` | double |
| `mom` | double |
| `vol` | double |
| `taker` | double |
| `microstruct` | double |

---

## Tier 3: Researcher

Complete nested schema with 12 top-level columns including futures data, diagnostics, and multi-window sentiment.

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
| `spot_prices` | list | Time series of spot price samples |

### futures_raw (Tier 3 only)

| Field | Type | Description |
|-------|------|-------------|
| `contract` | string | Perpetual contract symbol |
| `funding_now` | double | Current funding rate |
| `funding_24h_mean` | double | 24-hour mean funding rate |
| `open_interest` | double | Open interest in contracts |
| `open_interest_5m_delta_pct` | double | 5-minute change in open interest |
| `basis_now_bps` | double | Spot-futures basis in basis points |
| `top_long_short_accounts_5m` | double | Long/short ratio by accounts |
| `top_long_short_positions_5m` | double | Long/short ratio by positions |

### flags (Tier 3 only)

| Field | Type | Description |
|-------|------|-------------|
| `spot_data_ok` | bool | Spot data passed validation |
| `futures_data_ok` | bool | Futures data passed validation |
| `futures_contract_exists` | bool | Perpetual contract available |
| `twitter_data_ok` | bool | Sentiment data passed validation |
| `compression_enabled` | bool | Compression scoring enabled |
| `mom_fallback` | bool | Momentum used fallback calculation |
| `vol_fallback` | bool | Volume used fallback calculation |
| `spread_fallback` | bool | Spread used fallback calculation |

### twitter_sentiment_windows (Tier 3 only)

Contains two sub-structures:
- `last_cycle` — Sentiment from most recent 4-hour cycle
- `last_2_cycles` — Aggregated sentiment from past 8 hours

Each includes:
- `posts_total`, `posts_pos`, `posts_neu`, `posts_neg`
- `ai_sentiment` — Model predictions and confidence
- `hybrid_decision_stats` — Combined scoring metrics
- `author_stats` — Follower counts and verification status
- `platform_engagement` — Likes, retweets, views
- `category_counts` — Lexicon category matches
- `top_terms` — Frequent terms by category

---

## File Format

All tiers are distributed as Apache Parquet files with:
- Snappy compression
- Row group size: ~50,000 rows
- Timestamps in ISO 8601 UTC format

See [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) for detailed field definitions.
