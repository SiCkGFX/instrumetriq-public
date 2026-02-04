<p align="center">
  <img src="./.assets/instrumetriq-logo-white.svg" alt="Instrumetriq" width="420">
</p>

<p align="center">
  <strong>Crypto Market Activity & Sentiment Context Dataset</strong><br>
  Time-aligned market data with social context and participation dynamics
</p>

---

## Overview

Instrumetriq provides structured, research-grade data combining:

- **Market microstructure** — Spot prices, spreads, depth, and liquidity metrics from Binance
- **Social sentiment** — AI-classified X (Twitter) post sentiment with engagement context
- **Temporal alignment** — Each asset monitored ~120–130 minutes with 10-second sampling

The dataset is designed for quantitative research, backtesting, and building contextual models around crypto asset behavior.

---

## Access Tiers

| Aspect | Tier 1 Explorer | Tier 2 Analyst | Tier 3 Researcher |
|--------|-----------------|----------------|-------------------|
| Schema | Flat (19 columns) | Nested (8 columns) | Nested (12 columns) |
| Spot data | Summary | Full | Full |
| Futures data | — | — | ✓ |
| Sentiment | Counts only | Full cycle | Multi-window |
| Scoring factors | Final only | All factors | All factors + flags |
| Price time series | — | — | ✓ (700+ samples) |

[Compare access tiers →](https://instrumetriq.com/access)

---

## Free Samples

Sample parquet files are available in the [`/samples`](./samples) directory, organized by week. New samples are added weekly.

```
samples/
├── scripts/
│   ├── inspect_tier1_schema.py
│   ├── inspect_tier2_schema.py
│   └── inspect_tier3_schema.py
├── schemas/
│   ├── tier1_schema_reference.md
│   ├── tier2_schema_reference.md
│   └── tier3_schema_reference.md
└── week_2026-02-01/
    ├── 2026-02-01_tier1.parquet
    ├── 2026-02-01_tier2.parquet
    └── 2026-02-01_tier3.parquet
```

Run any inspection script to explore the data (requires Python 3.9+):

```bash
pip install -r requirements.txt
python samples/scripts/inspect_tier1_schema.py
```

---

## Documentation

Schema documentation with field-by-field descriptions for each tier:

- [Tier 1 Schema Reference](./samples/schemas/tier1_schema_reference.md) — 19 flat columns
- [Tier 2 Schema Reference](./samples/schemas/tier2_schema_reference.md) — 8 nested columns  
- [Tier 3 Schema Reference](./samples/schemas/tier3_schema_reference.md) — 12 nested columns with futures
- [Methodology](./docs/METHODOLOGY.md) — Conceptual overview of Instrumetriq's data collection and processing approach.

### File Format

All tiers are distributed as Apache Parquet files with:
- Snappy compression
- Timestamps in ISO 8601 UTC format

---

## Links

- **Website**: [instrumetriq.com](https://instrumetriq.com)
- **Dataset**: [instrumetriq.com/dataset](https://instrumetriq.com/dataset)
- **Access**: [instrumetriq.com/access](https://instrumetriq.com/access)

---

## Citation

If you use this dataset in academic work, please cite:

```
Instrumetriq. (2026). Instrumetriq Crypto Market Activity & Sentiment Context Dataset.
https://instrumetriq.com
```

See [CITATION.cff](./CITATION.cff) for a machine-readable citation file.

---

## License

Sample data is provided for evaluation purposes. Full dataset access requires a subscription. See [LICENSE.md](./LICENSE.md) for terms.
