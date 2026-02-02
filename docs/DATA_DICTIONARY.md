# Data Dictionary

Canonical field definitions for the Instrumetriq dataset.

---

## Identity Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `symbol` | string | Trading pair in BASEQUOTE format. The exchange symbol used on Binance spot market. | `"BTCUSDC"`, `"ETHUSDC"` |
| `snapshot_ts` | string | UTC timestamp marking the start of this observation session. ISO 8601 format. | `"2026-02-01T04:00:00.000Z"` |

---

## Session Metadata

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `meta.added_ts` | string | UTC timestamp when session was admitted to the active watchlist. | `"2026-02-01T04:00:12.345678Z"` |
| `meta.expires_ts` | string | UTC timestamp when session will expire (typically added_ts + 2 hours). | `"2026-02-01T06:00:12.345678Z"` |
| `meta.duration_sec` | double | Total session duration from admission to archival, in seconds. | `7200.5` |
| `meta.session_id` | string | Unique identifier for this watchlist session. | `"a1b2c3d4-..."` |
| `meta.schema_version` | int64 | Schema version number for this document structure. | `7` |
| `meta.source` | string | Identifies which data sources are present in this snapshot. | `"spot+twitter"` |

---

## Spot Market Data

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `spot_raw.bid` | double | Best bid price from order book. | `42150.50` |
| `spot_raw.ask` | double | Best ask price from order book. | `42151.00` |
| `spot_raw.mid` | double | Mid price: (bid + ask) / 2. | `42150.75` |
| `spot_raw.last` | double | Last traded price. | `42150.80` |
| `spot_raw.spread_bps` | double | Bid-ask spread in basis points: (ask - bid) / mid × 10000. | `1.19` |
| `spot_raw.depth_5bps_quote` | double | Order book depth within 5 bps of mid, in quote currency. | `125000.0` |
| `spot_raw.depth_10bps_quote` | double | Order book depth within 10 bps of mid, in quote currency. | `350000.0` |
| `spot_raw.depth_25bps_quote` | double | Order book depth within 25 bps of mid, in quote currency. | `850000.0` |
| `spot_raw.range_pct_24h` | double | 24-hour price range as percentage: (high - low) / low × 100. | `3.45` |
| `spot_raw.ticker24_chg` | double | 24-hour price change percentage from ticker. | `2.15` |
| `spot_raw.obi_5` | double | Order book imbalance at 5 bps depth. Range: -1 (all asks) to +1 (all bids). | `0.12` |
| `spot_raw.taker_buy_ratio_5m` | double | Ratio of taker buy volume to total volume over 5 minutes. | `0.55` |

---

## Futures Market Data (Tier 3)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `futures_raw.contract` | string | Perpetual contract symbol. | `"BTCUSDT"` |
| `futures_raw.funding_now` | double | Current funding rate (8-hour). Positive = longs pay shorts. | `0.0001` |
| `futures_raw.funding_24h_mean` | double | Mean funding rate over past 24 hours. | `0.00015` |
| `futures_raw.open_interest` | double | Total open interest in contracts (USDT value). | `450000000.0` |
| `futures_raw.open_interest_5m_delta_pct` | double | 5-minute change in open interest, as percentage. | `0.35` |
| `futures_raw.basis_now_bps` | double | Spot-futures basis in basis points: (futures - spot) / spot × 10000. | `5.2` |
| `futures_raw.top_long_short_accounts_5m` | double | Long/short ratio by top trader accounts. | `1.25` |
| `futures_raw.top_long_short_positions_5m` | double | Long/short ratio by top trader positions (size-weighted). | `1.18` |

---

## Derived Metrics

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `derived.liq_global_pct` | double | Global liquidity percentile rank (0-100). Higher = more liquid vs. universe. | `85.5` |
| `derived.liq_self_pct` | double | Self-relative liquidity percentile vs. symbol's history. | `72.3` |
| `derived.spread_bps` | double | Derived spread in basis points (may differ from raw during session). | `1.25` |
| `derived.depth_imbalance` | double | Order book depth imbalance metric. | `0.08` |
| `derived.depth_skew` | double | Asymmetry between bid and ask depth. | `-0.05` |
| `derived.flow` | double | Net order flow indicator. | `0.15` |

---

## Scoring Factors

Scores are normalized values from 0-100 used for ranking and admission decisions.

| Field | Type | Description |
|-------|------|-------------|
| `scores.final` | double | Final composite score combining all factors. |
| `scores.liq` | double | Liquidity factor score. |
| `scores.spread` | double | Spread tightness score (higher = tighter). |
| `scores.depth` | double | Order book depth score. |
| `scores.flow` | double | Order flow score. |
| `scores.mom` | double | Momentum score. |
| `scores.vol` | double | Volume score. |
| `scores.taker` | double | Taker activity score. |
| `scores.microstruct` | double | Microstructure quality score. |

---

## Sentiment Data

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `sentiment.posts_total` | int64 | Total X (Twitter) posts captured in this cycle. | `47` |
| `sentiment.posts_pos` | int64 | Posts classified as positive sentiment. | `18` |
| `sentiment.posts_neu` | int64 | Posts classified as neutral sentiment. | `22` |
| `sentiment.posts_neg` | int64 | Posts classified as negative sentiment. | `7` |
| `sentiment.mean_score` | double | Mean hybrid sentiment score (-1 to +1). | `0.23` |
| `sentiment.is_silent` | bool | True if no recent posts found for this symbol. | `false` |

### AI Sentiment (Tier 2+)

| Field | Type | Description |
|-------|------|-------------|
| `ai_sentiment.label_3class_mean` | double | Mean 3-class label (-1, 0, +1). |
| `ai_sentiment.prob_mean` | double | Mean prediction probability. |
| `ai_sentiment.prob_std` | double | Standard deviation of prediction probabilities. |
| `ai_sentiment.posts_scored` | int64 | Number of posts scored by AI model. |

### Engagement Metrics (Tier 2+)

| Field | Type | Description |
|-------|------|-------------|
| `platform_engagement.total_likes` | int64 | Total likes across all posts. |
| `platform_engagement.total_retweets` | int64 | Total retweets across all posts. |
| `platform_engagement.total_views` | int64 | Total views across all posts. |
| `platform_engagement.avg_likes` | double | Average likes per post. |
| `platform_engagement.avg_retweets` | double | Average retweets per post. |

### Author Statistics (Tier 2+)

| Field | Type | Description |
|-------|------|-------------|
| `author_stats.distinct_authors_total` | int64 | Unique authors posting about this symbol. |
| `author_stats.distinct_authors_verified` | int64 | Verified account authors. |
| `author_stats.followers_count_sum` | int64 | Total follower reach. |
| `author_stats.followers_count_mean` | double | Mean followers per author. |

---

## Quality Flags (Tier 3)

| Field | Type | Description |
|-------|------|-------------|
| `flags.spot_data_ok` | bool | Spot market data passed validation checks. |
| `flags.futures_data_ok` | bool | Futures data passed validation checks. |
| `flags.futures_contract_exists` | bool | Perpetual contract exists for this symbol. |
| `flags.twitter_data_ok` | bool | Sentiment data passed validation checks. |
| `flags.compression_enabled` | bool | Compression scoring was enabled for this session. |
| `flags.mom_fallback` | bool | Momentum calculation used fallback method. |
| `flags.vol_fallback` | bool | Volume calculation used fallback method. |
| `flags.spread_fallback` | bool | Spread calculation used fallback method. |

---

## Timestamps

All timestamps in the dataset use ISO 8601 format with UTC timezone:

- Standard precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- High precision: `YYYY-MM-DDTHH:MM:SS.ssssssZ`

Example: `2026-02-01T04:00:00.000Z`
