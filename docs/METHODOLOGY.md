# Methodology

High-level overview of Instrumetriq's data collection and processing approach.

---

## Data Sources

### Market Data

**Source**: Binance REST and WebSocket APIs

- **Spot market**: Order book snapshots, recent trades, 24-hour ticker
- **Futures market** (Tier 3): USDT-margined perpetual contracts, funding rates, open interest, trader positioning

Market data is sampled at regular intervals during each observation session.

### Social Data

**Source**: X (Twitter) public posts

Posts are captured for cryptocurrency-related terms and cashtags. Each observation window aligns with the 4-hour market session cycle.

---

## Sentiment Analysis

### Model Architecture

Sentiment classification uses a custom-trained DistilBERT model fine-tuned on cryptocurrency-specific text.

**Classification scheme**: 3-class (positive, neutral, negative)

### Hybrid Scoring

Final sentiment scores combine:
1. **AI model predictions** — DistilBERT probability outputs
2. **Lexicon signals** — Domain-specific term matching for crypto slang, FUD indicators, and hype patterns

The hybrid approach provides robustness against model edge cases while capturing crypto-native language patterns.

---

## Observation Windows

### Time Alignment

All observations are anchored to **4-hour cycles** aligned to UTC:
- 00:00–04:00
- 04:00–08:00
- 08:00–12:00
- 12:00–16:00
- 16:00–20:00
- 20:00–00:00

### Session Lifecycle

1. **Admission** — Symbol enters watchlist based on activity scoring
2. **Sampling** — Market data captured at regular intervals (typically 2-hour sessions)
3. **Archival** — Session data finalized and written to daily partition

---

## What Gets Captured

### Activity Signals
- Trading volume and trade count
- Order book depth and imbalance
- Spread dynamics and microstructure metrics
- Taker buy/sell ratios

### Silence Detection
- Symbols with no recent social mentions are flagged (`is_silent`)
- Enables filtering for "quiet" periods vs. active discussion

### Sentiment Polarity
- Post-level 3-class classification
- Aggregated counts and mean scores per observation window
- Confidence metrics from model predictions

### Volume Context
- Spot volume relative to historical norms
- Open interest changes (futures)
- Funding rate regime indicators

---

## Data Quality

### Validation Checks

Each observation undergoes validation:
- Timestamp consistency
- Numeric range checks
- Cross-field logic validation
- Source data completeness

### Quality Flags

Tier 3 includes boolean flags indicating:
- Data source availability (`spot_data_ok`, `futures_data_ok`, `twitter_data_ok`)
- Fallback calculation usage (`mom_fallback`, `vol_fallback`)
- Contract existence for futures data

---

## Coverage

### Temporal
- Daily exports since December 2025
- Continuous 24/7 collection

### Asset Universe
- All USDC-quoted pairs on Binance spot
- Corresponding USDT perpetual contracts (where available)

### Filtering
- Minimum liquidity thresholds for admission
- Activity-based scoring determines watchlist inclusion

---

## Limitations

- **Single exchange**: Market data from Binance only
- **Single platform**: Social data from X (Twitter) only
- **English-centric**: Sentiment model trained primarily on English text
- **Latency**: Data is processed in batch, not real-time

---

## Updates

Schema and methodology may evolve. Version numbers in metadata track changes:
- `schema_version` — Document structure version
- `archive_schema_version` — Version at time of archival

See [SCHEMA.md](./SCHEMA.md) for current field definitions.
