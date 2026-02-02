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

| Tier | Name | Description |
|------|------|-------------|
| **Tier 1** | Explorer | Flat schema with 19 fields. Core metrics for quick analysis. |
| **Tier 2** | Analyst | Nested schema with 8 top-level columns. Full spot market data, scoring factors, and sentiment detail. |
| **Tier 3** | Researcher | Complete dataset with 12 columns including futures data, diagnostic flags, and multi-window sentiment. |

[Compare access tiers →](https://instrumetriq.com/access)

---

## Free Samples

Sample parquet files are available in the [`/samples`](./samples) directory. These contain one day of data for each tier, suitable for schema exploration and pipeline prototyping.

```
samples/
├── 2026-02-01_tier1.parquet
├── 2026-02-01_tier2.parquet
└── 2026-02-01_tier3.parquet
```

See [`/examples`](./examples) for Python code to load and inspect the data.

---

## Documentation

- [Schema Reference](./docs/SCHEMA.md) — Field listing and type information for all tiers
- [Data Dictionary](./docs/DATA_DICTIONARY.md) — Canonical field definitions and descriptions
- [Methodology](./docs/METHODOLOGY.md) — High-level overview of data collection and processing

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
