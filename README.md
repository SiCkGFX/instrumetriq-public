# Instrumetriq

**Crypto Market Activity & Sentiment Context Dataset**

A time-aligned dataset capturing market micro-dynamics, participation intensity, and social context around crypto assets.

---

## Overview

Instrumetriq provides structured, research-grade data combining:

- **Market microstructure** — Spot prices, spreads, depth, and liquidity metrics from Binance
- **Social sentiment** — AI-classified X (Twitter) post sentiment with engagement context
- **Temporal alignment** — All observations anchored to consistent 4-hour cycles

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

Sample parquet files are available in the [`/samples`](./samples) directory. Each tier folder contains a sample parquet file and its schema reference documentation.

```
samples/
├── tier1/
│   ├── SCHEMA_REFERENCE.md
│   └── 2026-02-01_tier1.parquet
├── tier2/
│   ├── SCHEMA_REFERENCE.md
│   └── 2026-02-01_tier2.parquet
└── tier3/
    ├── SCHEMA_REFERENCE.md
    └── 2026-02-01_tier3.parquet
```

See [`/examples`](./examples) for Python code to load and inspect the data.

---

## Documentation

Each tier's sample folder includes a comprehensive `SCHEMA_REFERENCE.md` with exhaustive field-by-field documentation.

- [Tier 1 Schema Reference](./samples/tier1/SCHEMA_REFERENCE.md) — 19 flat columns
- [Tier 2 Schema Reference](./samples/tier2/SCHEMA_REFERENCE.md) — 8 nested columns  
- [Tier 3 Schema Reference](./samples/tier3/SCHEMA_REFERENCE.md) — 12 nested columns with futures
- [Methodology](./docs/METHODOLOGY.md) — High-level overview of data collection

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
