# Instrumetriq - Research Notes

Observational research notes on the
[Instrumetriq crypto market activity & sentiment dataset](https://doi.org/10.5281/zenodo.18508636).
Each note states a measured result, names the exact dataset fields and arithmetic behind it, and
includes a self-contained reproduction that runs on the free weekly samples - no purchase required.

The notes are computed on the full Tier 3 archive as of their stated computation date. The free
weekly samples reproduce the free-sample figures reported in each note.

---

## 1. Social attention spikes precede larger intraday price moves in either direction

When a coin's count of distinct posting authors rises to at least 6x its own recent baseline, the
observed rate of a large intraday move (a price excursion of at least +/-4% in either direction, over
the following ~2 hours) is roughly three to four times the rate on normal-attention sessions. The
result holds within every methodology regime and out-of-sample, and across move-size thresholds. The
larger moves are symmetric in sign - up and down in similar proportion - so attention is observed
alongside higher volatility and carries no directional information. Measured on 362,813
coin-sessions across 278 assets (2025-12-15 to 2026-07-06).

- **Note:** [attention_volatility.md](attention_volatility.md) - DOI [10.5281/zenodo.21254201](https://doi.org/10.5281/zenodo.21254201)
- **Run the reproduction:** [Open in Colab](https://colab.research.google.com/drive/1ugq_0ngrGpq2z-nglOfA_Ts_4394clDq?usp=sharing)
- **Code:** [reproduce_attention_volatility.py](reproduce_attention_volatility.py) | [notebook](Attention_Volatility_Reproduction_Colab.ipynb)

## 2. Social sentiment tone shows no detectable lead over short-horizon price direction

Across every no-look-ahead horizon up to ~2-8 hours, the rank correlation (information coefficient)
between sentiment tone - how bullish or bearish the posts are - and the signed forward return stays
within |IC| = 0.007 in pooled point estimate, and no 95% interval reaches |IC| = 0.015. We report
this as a bounded null rather than proof of no relationship, and document the caveat that the
sentiment pipeline's negative-tone channel is only partially complete, so a weak bearish signal
could be partially masked. Measured on 364,474 coin-sessions. This is the direction-side complement
to note 1.

- **Note:** [sentiment_direction_null.md](sentiment_direction_null.md) - DOI [10.5281/zenodo.21254205](https://doi.org/10.5281/zenodo.21254205)
- **Run the reproduction:** [Open in Colab](https://colab.research.google.com/drive/1V3owwQ-cLJf8RRqK3M7Kib3pQdSb52cM?usp=sharing)
- **Code:** [reproduce_sentiment_direction.py](reproduce_sentiment_direction.py) | [notebook](Sentiment_Direction_Reproduction_Colab.ipynb)

## 3. Social attention adds no predictive power for intraday move size beyond price volatility

Attention spikes precede larger moves (note 1), but that is because attention and price volatility rise
together. Judged as a predictor - does it rank which coins will make a large move? - attention scores barely
above a coin flip (AUC ~0.53), while a price-only volatility reading (the 24-hour price range at admission)
ranks movers well (~0.80). Adding attention on top of volatility changes the out-of-sample ranking by 0.000,
and a positive control confirms the test would detect real added value if attention had any. Attention is a
shadow of volatility, not an independent predictor of move size. This is the magnitude-side complement to
notes 1 and 2. Measured on 380,932 coin-sessions (2025-12-15 to 2026-07-15); reproduces on the free weekly
samples.

- **Note:** [attention_incremental_null.md](attention_incremental_null.md) - DOI [10.5281/zenodo.21468030](https://doi.org/10.5281/zenodo.21468030)
- **Run the reproduction:** [Open in Colab](https://colab.research.google.com/github/SiCkGFX/instrumetriq-public/blob/main/research/Attention_Incremental_Null_Reproduction_Colab.ipynb)
- **Code:** [reproduce_attention_incremental_null.py](reproduce_attention_incremental_null.py) | [notebook](Attention_Incremental_Null_Reproduction_Colab.ipynb)

---

## Reproduction

Each note's method is specified against named dataset fields and elementary arithmetic. The scripts
and notebooks read the free weekly samples in [`../samples`](../samples) and reproduce the
free-sample figures reported in each note. The full-archive figures use the complete Tier 3 archive
as of the computation date.

## Data

Free weekly samples are mirrored across
[GitHub](https://github.com/SiCkGFX/instrumetriq-public),
[Hugging Face](https://huggingface.co/datasets/Instrumetriq/crypto-market-sentiment-observations),
[Kaggle](https://www.kaggle.com/datasets/madlygfx/instrumetriq-crypto-sentiment-market-data), and
[Zenodo](https://doi.org/10.5281/zenodo.18508636). Full archive: [instrumetriq.com](https://instrumetriq.com).
