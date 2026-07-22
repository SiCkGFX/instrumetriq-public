# Social sentiment tone shows no detectable lead over short-horizon price direction

**Instrumetriq | Research Note | July 2026**

**DOI:** [10.5281/zenodo.21254205](https://doi.org/10.5281/zenodo.21254205) | **Companion note:** [10.5281/zenodo.21254201](https://doi.org/10.5281/zenodo.21254201)

## Abstract
Using 364,474 coin-sessions with observable, scored social activity, drawn from the Instrumetriq
Tier 3 archive (204 consecutive days, 2025-12-15 to 2026-07-06, 538,538 records across 278 crypto
assets; results computed 2026-07-08), we measure whether the *tone* of social sentiment on a coin - how bullish or bearish the
posts are - carries information about the coin's subsequent price direction. Across every
no-look-ahead horizon over the next one-to-two sessions (~2-8 hours) - the coin's same session
(tone is frozen at admission, the return unfolds afterward), its next session, and two sessions
ahead - the rank correlation between sentiment tone and the signed forward return does not exceed
**|IC| = 0.007** in pooled point estimate, and on the full-archive analysis set no 95% interval
edge reaches **|IC| = 0.015**. The next-session estimate is -0.001 (95% CI -0.006 to +0.003); the
two intervals that do exclude zero (same-session and two-ahead) are negligibly small and
*negatively* signed - opposite to a bullish-tone-leads-gains hypothesis. This
is a **bounded null**: over this horizon there is no detectable directional lead from sentiment
tone, with the stated caveat below that the measurement can only partially detect bearish tone. It is the direction-side complement to the companion note, which
finds that a *surge in attention* (regardless of tone) precedes higher volatility (larger moves up
and down in similar proportion).

## 1. Scope of pre-specification
The question (does tone lead direction?), the tone measures, the outcome (signed forward return),
and the +/-2-session horizon were fixed before any result was computed. The per-regime robustness
split and the free-sample within-day variant were added as robustness checks and are reported as
such. A null is only as strong as its measurement; Section 5 states the measurement's known limits plainly
and they are not incidental.

## 2. Data
- **Dataset.** Instrumetriq Tier 3 archive: **204 consecutive days, 2025-12-15 to 2026-07-06,
  538,538 records across 278 coins** - the full archive as of the computation date (2026-07-08),
  one record per coin per ~2-hour tracking session.
  Concept DOI (resolves to the current version): https://doi.org/10.5281/zenodo.18508636.
- **Analysis set.** Of the 538,538 records, **364,474** have observable social activity
  (`posts_total` > 0, not silent), a scored sentiment tone (`mean_score` present), and a valid
  price path. No other filtering is applied. This is the direction-side analysis set; the companion
  attention note additionally requires a computable attention baseline.

### Fields used (a reader can locate every input)
| Quantity | Exact dataset field | Definition |
|---|---|---|
| Sentiment tone | `twitter_sentiment_windows.last_cycle.hybrid_decision_stats.mean_score` | mean model score over the coin's scored posts in the admission cycle, on a bearish(-) to bullish(+) scale |
| Tone (robustness) | `...hybrid_decision_stats.pos_ratio` | fraction of scored posts classified positive |
| Price path | `spot_prices[].mid` | mid price time series (~700 samples/session, ~10 s apart) |
| Quality gates | `...last_cycle.posts_total` > 0; `...sentiment_activity.is_silent` = false; `...hybrid_decision_stats.mean_score` present | keep only sessions with observable, scored activity |
| Regime label | `twitter_sentiment_meta.bucket_meta.methodology_regime` | pipeline version (see Section 3) |

## 3. Method (fully specified; no external code required)
**Sentiment tone.** For each session, the tone is `mean_score` - the mean of the per-post model
scores over that session's scored posts, positive for bullish, negative for bearish. `pos_ratio`
(the positive fraction) is reported as a robustness variant. Tone is the state at admission; the
price path is what follows, so there is no look-ahead.

**Forward return.** From the session's `spot_prices` array, take the mid of every third sample
(~30 s spacing); let m0 be the first and m_last the last. The session's **signed return** is
m_last/m0 - 1. To test for a *lead*, we align each coin's sessions in time and, for horizon k,
pair a session's tone with the signed return k sessions ahead. Because tone is frozen at admission
and the price path unfolds afterward, **k = 0 is already a no-look-ahead test** - the tone versus
that same session's forward return - and it is the most direct lead alignment in the table; k = +1
and k = +2 extend it to the coin's following sessions. We also report lagged pairings (k = -1, -2),
where tone is set against returns that already happened, as a reaction check. A coin's tracking
sessions recur roughly every 2-3 hours, so k = +1 and +2 look about 2-8 hours ahead.

**Statistic.** For each tone measure and each horizon we compute the **Spearman rank correlation
(information coefficient, IC)** - the standard rank correlation, with tied values assigned average
ranks, so the result is independent of row order and reproduces under any correct implementation -
between tone and the forward signed return. A directional signal
would show a materially non-zero IC at a no-look-ahead horizon (k >= 0). Confidence intervals are
**day-level block bootstraps**: resample calendar days with replacement 1,000 times, recompute the
IC each time from the sessions pooled over the resampled days, and take the 2.5th-97.5th
percentiles. Days (not sessions) are resampled because coin-sessions are strongly cross-correlated
within a day (see the companion note).

**Free-sample variant (pre-specified here).** The cross-session lag above needs
*consecutive* sessions, which the free weekly sample (one non-contiguous Sunday per week) cannot
provide across days. Within a single Sunday, however, a coin has several same-day sessions, so the
identical test runs with the horizon-k pairing restricted to **same-day** sessions
(`groupby(symbol, day)`). This is the direction-side analog of the companion note's intraday
baseline, and it is what a reader with only the free samples should run (see Section 7).

**Methodology-regime split.** As in the companion note, the sentiment pipeline was revised in
mid-February 2026 (scoring models 2026-02-16 05:14 UTC; crypto-relevance filter 2026-02-17
06:03 UTC). We report the primary IC pooled and, as robustness, within **V1** (pre-update),
**V2 development** (2026-02-17 to 04-15), and **V2 held-out** (2026-04-16 to 07-06).

## 4. Results
Information coefficient (Spearman) between sentiment tone and the signed return at each horizon,
over the full-archive analysis set (N = 364,474). k >= 0 are no-look-ahead (forward)
alignments - k = 0 is tone versus the same session's own forward return; k < 0 are past returns, a
reaction check:

| Tone measure | k=-2 (past) | k=-1 (past) | k=0 (same-session) | k=+1 (next) | k=+2 (two-ahead) |
|---|---|---|---|---|---|
| `mean_score` | +0.004 | +0.005 | **-0.007** | **-0.001** | **-0.006** |
| `pos_ratio` | +0.004 | +0.005 | **-0.007** | **-0.001** | **-0.006** |

**The null, as a bound.** Every no-look-ahead point IC (k = 0, +1, +2) is within |IC| = 0.007, an
order of magnitude below the |IC| ~ 0.03-0.05 typical of a usable directional signal. The 95%
day-block bootstrap intervals on those three horizons:

| | k=0 (same-session) | k=+1 (next) | k=+2 (two-ahead) |
|---|---|---|---|
| `mean_score` IC [95% CI] | -0.007 [-0.012, -0.002] | -0.001 [-0.006, +0.003] | -0.006 [-0.010, -0.002] |
| `pos_ratio` IC [95% CI] | -0.007 [-0.011, -0.002] | -0.001 [-0.006, +0.003] | -0.006 [-0.010, -0.001] |

Across the three no-look-ahead horizons no 95% interval edge (pooled archive) exceeds |IC| = 0.013.
The next-session
(k=+1) interval straddles zero. The two intervals that *exclude* zero - same-session (k=0) and
two-ahead (k=+2) - are negligibly small (|IC| <= 0.007) and, tellingly, **negatively** signed: the
opposite of a "bullish tone -> gains" lead, consistent with faint crowd-chasing / mean-reversion
rather than any directional edge. There is no horizon at which more-bullish tone precedes higher
returns.

**Robustness.** Splitting by methodology regime, the next-session (k=+1) IC is V1 +0.001, V2
development -0.009, V2 held-out +0.002, and the two-ahead (k=+2) IC is V1 -0.006, V2 development
-0.010, V2 held-out -0.002 - all within |IC| ~ 0.01. The next-session values flip sign across
regimes (noise around zero); the two-ahead values stay uniformly small and negative, the same faint
mean-reversion seen pooled. Neither shows a stable directional signal.

**The null reproduces on the free sample.** The cross-session lag needs contiguous sessions, so on
the free weekly samples we run the identical test with same-day (within-Sunday) pairing (Section 3), and -
because k=0 needs no pairing (tone versus the same row's return) - the same-session horizon
reproduces directly too. The forward ICs are `mean_score`: k=0 -0.007 [-0.020, +0.006],
k=+1 -0.008 [-0.024, +0.007], k=+2 -0.005 [-0.017, +0.009]; `pos_ratio`: k=0 -0.006 [-0.019, +0.008],
k=+1 -0.007 [-0.024, +0.008], k=+2 -0.003 [-0.014, +0.011]. Every interval straddles zero - the null
reproduces on public data (see Section 7), with wider intervals (and, on this smaller sample, a k=0 that
now straddles zero rather than tightening below it) reflecting the smaller sample. These free-sample ICs
are computed on the weekly samples available at the computation date (2026-07-08). As further weekly
samples accumulate, the free-sample point estimates shift slightly and the intervals narrow; the
full-archive result and the finding are unchanged.

## 5. Robustness & limitations
- **This is a bound over a short horizon; it does not prove there is no relationship.** Across the
  no-look-ahead horizons (k = 0, +1, +2 sessions, ~2-8 h), on the full-archive analysis set every
  95% interval edge stays within |IC| = 0.013 (the smaller free-sample intervals are wider; Section 4), and
  the largest pooled point estimate is 0.007. Longer horizons, non-linear encodings of tone, or
  conditional subsets are not ruled out by this test.
- **The measurement can only partially detect bearish tone - this is the load-bearing caveat.**
  Against a held-out gold set, the sentiment pipeline's negative-tone scorer has **~64% recall**
  (86% precision), and the crypto-relevance filter drops **21.7%** of genuinely-bearish posts as
  "non-crypto" versus **8.8%** of genuinely-positive ones. These figures come from evaluation
  against held-out, independently-curated gold-labeled sets (n = 1,789 sentiment-labeled and
  n = 2,486 relevance-labeled posts); a dedicated model-audit note documenting the gold-set
  construction and full metrics is forthcoming. Aggregate `mean_score`
  therefore carries a mild optimistic bias and under-represents bearish tone. The honest reading is: *no detectable
  directional lead at this horizon, with the caveat that a weak bearish signal could be partially
  masked by incomplete negative-tone measurement.* We do not claim to have excluded a bearish-side
  effect that better tone measurement might surface.
- Intervals are clustered by calendar day; the same serial-dependence caveat as the companion note
  applies.
- The result is stable across both methodology regimes and the held-out window (Section 4).

## 6. What this does and does not mean
- **Does mean:** over the next one-to-two sessions (~2-8 h), knowing how bullish or bearish a coin's
  posts are gives no usable edge on the *direction* of its next move, at this horizon and by this
  measurement.
- **Does not mean:** that social data is uninformative. The companion note shows a *surge in
  attention* (independent of tone) precedes higher volatility (larger moves up and down in similar
  proportion) - a volatility signal that carries no directional information. Tone-null and
  attention-informative are consistent and complementary.
- **Does not mean:** that no directional relationship exists at any horizon or under any better tone
  measurement - see the recall caveat above.
- **In context:** Bollen, Mao & Zeng (2011) reported a Twitter-mood -> market link; Lachanski & Pav
  (2017) could not replicate it. Our result, on 364,474 crypto observations, lands where that
  literature settled after scrutiny - attention and volume are informative; tone-as-direction is
  not, at short horizons.

## 7. Reproduction
The method in Section 3 is specified entirely against named dataset fields and elementary arithmetic.
- **Read it (no login):** the notebook renders directly on GitHub -
  https://github.com/SiCkGFX/instrumetriq-public/blob/main/research/Sentiment_Direction_Reproduction_Colab.ipynb
- **Run it (one click, no purchase):** open the same notebook in Colab -
  https://colab.research.google.com/github/SiCkGFX/instrumetriq-public/blob/main/research/Sentiment_Direction_Reproduction_Colab.ipynb
  - it rebuilds the within-Sunday tone->return IC on the published weekly samples.
- **Script:** `research/reproduce_sentiment_direction.py` implements the Section 3 computation; on the full
  Tier 3 archive it reproduces the cross-session ICs in the Section 4 table.

## 8. References
- Bollen, J., Mao, H., & Zeng, X. (2011). *Twitter mood predicts the stock market.* Journal of
  Computational Science, 2(1), 1-8.
- Lachanski, M., & Pav, S. (2017). *Shy of the Character Limit: "Twitter Mood Predicts the Stock
  Market" Revisited.* Econ Journal Watch, 14(3), 302-345.

## 9. Data availability
Free weekly samples (one Tier 3 day per week) are mirrored across:
- Hugging Face - https://huggingface.co/datasets/Instrumetriq/crypto-market-sentiment-observations
- Kaggle - https://www.kaggle.com/datasets/madlygfx/instrumetriq-crypto-sentiment-market-data
- GitHub - https://github.com/SiCkGFX/instrumetriq-public
- Zenodo (archived, DOI) - https://doi.org/10.5281/zenodo.18508636

The **first six months** of the Tier 3 archive (2025-12-15 to 2026-06-15, 481,829 records, 278
coins) are available under a one-time commercial license ($900):
https://instrumetriq.gumroad.com/l/crypto-market-sentiment-dataset. The **current month** and
ongoing daily updates are published via Patreon; the complete archive used for this note is the two
combined, and custom exports are available on request.

The analysis uses the full Tier 3 archive as of the computation date; the free samples reproduce the
within-day variant above.
