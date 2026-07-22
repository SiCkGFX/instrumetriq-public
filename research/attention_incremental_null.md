# Social attention adds no predictive power for intraday move size beyond price volatility

**Instrumetriq | Research Note | July 2026**

**DOI:** [10.5281/zenodo.21468030](https://doi.org/10.5281/zenodo.21468030) | **Companion notes:** [attention_volatility.md](attention_volatility.md) (DOI [10.5281/zenodo.21254201](https://doi.org/10.5281/zenodo.21254201)) | [sentiment_direction_null.md](sentiment_direction_null.md) (DOI [10.5281/zenodo.21254205](https://doi.org/10.5281/zenodo.21254205))

## Abstract

The companion note showed that a surge in social attention on a coin precedes a larger intraday price move in either direction - a real association between attention and move size. This note asks whether attention tells you anything a plain price-volatility reading does not. It does not, and that holds however attention is measured. We measure attention four ways - distinct posting authors, engagement (likes plus retweets), reach (poster followers), and the Engagement Coefficient the Instrumetriq extension shows as a coin's chatter level - each as a spike over the coin's own baseline. On the full Tier 3 archive (380,932 coin-sessions, 2025-12-15 to 2026-07-15, ~2-hour horizon), a price-only volatility reading ranks large movers at AUC 0.77-0.83 (the chance it ranks a real large mover above a non-mover; 0.50 is a coin flip). Every attention measure ranks them at 0.50-0.54, barely above a coin flip, and adding any of them to volatility changes the out-of-sample AUC by 0.000. A positive-control feature that peeks at the answer moves that number by +0.01 to +0.14, so the test detects added value when it exists. Attention precedes larger moves only because attention and volatility rise together; once volatility is known, no measure of attention adds anything.

## 1. Two measurements that are easy to confuse

The companion note is often read as "watch attention to see big moves coming," which is only useful if attention carries information the price chart does not. Two different measurements pull apart here. **Lift** compares a rare extreme group - sessions where attention spikes to at least 6x a coin's baseline, about 1% of sessions - against normal-attention sessions; it is large (~3.6x) and real, and this note reproduces it. **Ranking skill (AUC)** asks whether attention, across all sessions, sorts coming large movers from non-movers; it is ~0.53, essentially a coin flip, because most sessions sit near baseline and even the rare spikes mostly move because they are already volatile. A strong lift in a rare tail and near-zero ranking skill overall are both true at once. What decides whether attention is a useful predictor is ranking skill, and whether any of it survives once price volatility is accounted for.

## 2. Data and fields

Instrumetriq Tier 3 archive: one record per coin per ~2-hour tracking session, with ~700 price samples per session at ~10-second spacing. This is the public dataset the two companion notes use. The analysis set is sessions with observable social activity (`posts_total` > 0, not silent), a computable attention baseline, and an admission-time volatility reading: 380,932 sessions on the full archive, 16,058 on the free weekly samples. Every input is a named field, and attention is not one field but several:

- **Attention** - all in `twitter_sentiment_windows.last_cycle`: `author_stats.distinct_authors_total` (authors), `platform_engagement.total_likes` + `total_retweets` (engagement), `author_stats.followers_count_sum` (reach), and `posts_total`. The Engagement Coefficient is `(likes + retweets) * log(1 + followers) / posts`, exactly as the extension defines it.
- **Price volatility** - `spot_raw.range_pct_24h`, the trailing 24-hour high-low price range at admission (price-only, admission-frozen, so no look-ahead).
- **Price path** - `spot_prices[].mid` (every 3rd sample, ~30s).
- **Gates** - `posts_total` > 0 and `sentiment_activity.is_silent` = false.

## 3. Method

Each attention measure is judged relative to the coin's own history: a baseline equal to the median of that measure over up to 20 strictly-prior sessions (minimum 5), and a spike ratio of the current value to that baseline. (The author-count version of this is identical to the companion note's construction.) Volatility is `range_pct_24h`, a price-only reading available at the moment attention is read. The outcome is the forward move magnitude: from the session's price path, with m0 the first sample, the largest excursion `max |mid/m0 - 1|` over the session; a large move is at least 3, 4, or 5%. Ranking skill is the AUC of a reading against that outcome. Added value is the difference between a logistic model on volatility alone and one on volatility plus an attention measure, compared out of sample (earlier days train, later days test). The positive control replaces attention with a feature equal to the outcome plus noise; a large jump there is required, proving the added-value test can see real signal.

## 4. Results

**4.1 Attention precedes larger moves (companion note reproduces).** Using the companion note's measure, the author-count spike, large-move rate spike versus normal, full archive:

| Move >= | spike | normal | lift  |
| ------- | ----- | ------ | ----- |
| 3%      | 24.3% | 9.4%   | 2.58x |
| 4%      | 16.9% | 4.7%   | 3.63x |
| 5%      | 12.7% | 2.7%   | 4.76x |

**4.2 But no measure of attention adds anything to price volatility.** Out of sample, 109,543 held-out sessions, move >= 4%. Price volatility ranks large movers at AUC 0.805; each attention measure, spiked over its own baseline:

| attention measure           | ranking skill (AUC) | added over volatility |
| --------------------------- | ------------------- | --------------------- |
| distinct authors            | 0.535               | +0.000                |
| engagement (likes+retweets) | 0.504               | +0.000                |
| reach (follower sum)        | 0.542               | -0.000                |
| Engagement Coefficient      | 0.499               | +0.000                |

Every measure - including the Engagement Coefficient the extension presents as a coin's chatter level - ranks large movers near a coin flip and leaves the model's out-of-sample AUC unchanged. Volatility already contains whatever attention knows.

**4.3 The test has power.** Swapping attention for a feature that peeks at the answer, added value jumps to +0.143 (light noise) and +0.012 (heavy noise), versus 0.000 for attention. The null is a property of the data, not a blind test.

## 5. Full archive versus free samples

The same reproduction runs on both. The added value of every attention measure is ~0 in each:

| added over volatility (move >= 4%) | full archive | free samples |
| ---------------------------------- | ------------ | ------------ |
| distinct authors                   | +0.000       | -0.010       |
| engagement                         | +0.000       | -0.000       |
| reach                              | -0.000       | -0.001       |
| Engagement Coefficient             | +0.000       | -0.000       |

Volatility's ranking skill (AUC 0.80 versus 0.79), the author-spike lift (3.63x versus 2.38x), and the positive control (+0.14 in both) also line up. The full archive gives more precise and more robust numbers: narrower estimates from far more sessions, the proper multi-day attention baseline, and confirmation separately within each methodology regime. The free weekly samples are one non-contiguous day per week, so they can only use a noisier same-day baseline, which is why the raw author-spike lift is the one figure that comes out lower there. The direction and size of the finding are the same in both.

**Computation date and figure drift.** This analysis was run on 2026-07-17. The full-archive figures use the Tier 3 archive through 2026-07-15; the free-sample figures use the 29 weekly samples through 2026-07-12 (16,058 sessions). The free-sample reproduction ranks with an out-of-sample split, an earlier 70% of days for training and a later 30% for testing, so every weekly sample added after 2026-07-12 shifts that split and moves the descriptive digits slightly: with one further week the free-sample volatility AUC reads about 0.81 rather than 0.79, and the author-spike lift about 2.6x rather than 2.4x. Every added-value result stays at ~0 and the positive control still fires, so the finding is unchanged; only the descriptive figures track the growing sample. A reader running the reproduction on the current free samples should expect these small differences.

## 6. Robustness

Beyond the four attention measures above, the null holds pooled and separately within both methodology regimes (before and after the February 2026 sentiment-pipeline change), against a second independent volatility reading (a coin's prior-session realized volatility rather than its 24-hour range), and across all three move thresholds, out of sample. The horizon is the ~2-hour session; other horizons are not addressed by Tier 3.

## 7. What this means, and how it fits the companion notes

This refines the attention_volatility note without contradicting it: that note's claim - attention spikes precede 3-4x larger-move rates, symmetric in sign - stands and is reproduced in Section 4.1. The addition is the conditional result it did not test, that the association is not incremental to price. The earlier note already observed "higher attention is observed alongside higher volatility"; this note quantifies that, for predicting move size, the overlap is total. It does not mean the attention effect is spurious - attention genuinely precedes larger moves - only that a reader who already has price volatility has the information. Nor does it diminish attention as awareness: knowing what is being discussed, and when unusually so, is a real use; it is simply not an incremental predictor of near-term move size. Move magnitude is predictable and useful; the finding is about the source, which is price. Together the three notes say: tone gives no direction, attention gives no incremental magnitude, and price volatility gives the magnitude.

## 8. Reproduction

The method is specified against named fields and elementary arithmetic. The script `reproduce_attention_incremental_null.py` builds all four attention measures and reports their ranking skill and added value; it runs on the free weekly samples (`--glob "samples/week_*/*_tier3.parquet"`) and reproduces the free-sample column, and on the full contiguous archive (`--mode trailing`) it reproduces the full-archive column. The notebook `Attention_Incremental_Null_Reproduction_Colab.ipynb` walks through every step, including building the Engagement Coefficient from its fields.

## 9. References

Da, Z., Engelberg, J., & Gao, P. (2011). *In Search of Attention.* Journal of Finance, 66(5), 1461-1499.

## 10. Data availability

Free weekly samples are mirrored across [Hugging Face](https://huggingface.co/datasets/Instrumetriq/crypto-market-sentiment-observations), [Kaggle](https://www.kaggle.com/datasets/madlygfx/instrumetriq-crypto-sentiment-market-data), [GitHub](https://github.com/SiCkGFX/instrumetriq-public), and [Zenodo](https://doi.org/10.5281/zenodo.18508636). Full archive: [instrumetriq.com](https://instrumetriq.com). Fixed-scope data and automation builds: [instrumetriq.com/services](https://instrumetriq.com/services).
