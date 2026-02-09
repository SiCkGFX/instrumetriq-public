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

Posts are captured for cryptocurrency-related terms and cashtags. Sentiment scraping operates on its own cycle (~49 minutes per complete pass through all tracked symbols). While independent of watchlist timing, the most recent sentiment cycle is assigned to a coin at admission time.

---

## Sentiment Analysis

### Model Architecture

Sentiment classification uses a custom-trained DistilBERT model fine-tuned on cryptocurrency-specific text.

**Classification scheme**: 3-class (positive, neutral, negative)

### Two-Model Scoring

Final sentiment scores are produced by a **two-model DistilBERT ensemble**:
1. **Primary model** — Best raw classification accuracy
2. **Referee model** — Best-calibrated confidence scores

The referee's confidence drives the final decision:
- If the referee is uncertain (confidence in the neutral band), the tweet is classified as neutral
- If the referee is highly confident and disagrees with the primary, the referee's label is used
- Otherwise, the primary model's label is used

This produces a 3-class output (positive, neutral, negative) from two binary classifiers, with the neutral class emerging from calibrated uncertainty rather than a dedicated training label.

---

## Observation Windows

### Session Duration

Each watchlist session runs for **~120–130 minutes**:
- Symbols are admitted based on activity scoring
- Market data is sampled every ~10 seconds throughout the session
- Sessions typically accumulate **700+ price samples** before archival

### Session Lifecycle

1. **Admission** — Symbol enters watchlist based on activity scoring
2. **Sampling** — Market data captured every ~10 seconds for the 2-hour session duration
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

**Note on positive skew**: As is common in cryptocurrency-related social media discourse, sentiment language is heavily skewed positive. The dataset preserves this property rather than normalizing it. The sentiment mean reflects narrative tone, while post volume, balance, and silence capture structural changes in discourse.

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
- Data completeness is required for admission — both market data from Binance and a sentiment cycle from the scraper must be present
- Symbols with missing fields from either source are excluded from the watchlist for that monitoring period

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
