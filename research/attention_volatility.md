# Social attention spikes precede larger intraday price moves, not directional ones

**Instrumetriq | Research Note | July 2026**

**DOI:** [10.5281/zenodo.21254202](https://doi.org/10.5281/zenodo.21254202) | **Companion note:** [10.5281/zenodo.21254206](https://doi.org/10.5281/zenodo.21254206)

## Abstract
Using 362,813 coin-sessions with observable social activity and a computable baseline, drawn
from the Instrumetriq Tier 3 archive (204 consecutive days, 2025-12-15 to 2026-07-06, 538,538
records across 278 crypto assets; results computed 2026-07-08), we measure whether a surge in
social attention on a coin
precedes a larger price move in the following ~2-hour window. When a coin's count of distinct
posting authors rises to at least 6x its own recent baseline, the observed rate of a large
intraday move (a price excursion of at least +/-4% in either direction) is roughly three to four
times the rate on normal-attention sessions, and this holds within every sub-period and
move-size measured. The additional movement is direction-symmetric: at a matched threshold,
attention spikes are observed alongside larger moves up and down in similar proportion. Higher
attention is observed alongside higher volatility, not higher returns.

## 1. Scope of pre-specification
The question, the attention-spike definition, the outcome window, and the development/held-out
split were fixed before any result was computed. The methodology-regime split, the alternate
move-size thresholds, and the free-sample reproduction variant were added as robustness checks
during review, after the headline was known; they are reported as such and do not alter the
primary measurement.

## 2. Data
- **Dataset.** Instrumetriq Tier 3 archive: **204 consecutive days, 2025-12-15 to 2026-07-06,
  538,538 records across 278 coins** - the full archive as of the computation date (2026-07-08),
  one record per coin per ~2-hour tracking session.
  Concept DOI (resolves to the current version): https://doi.org/10.5281/zenodo.18508636.
- **Analysis set.** Of the 538,538 records, **367,536** have observable social activity
  (`posts_total` > 0) and a valid price path; the remainder are sessions where the coin had no
  posts in the relevant cycle, or were flagged silent/incomplete. Of these, **362,813** also
  have a computable attention baseline (a coin's earliest sessions have no prior history and are
  used only to build baselines). No other filtering is applied.

### Fields used (a reader can locate every input)
| Quantity | Exact dataset field | Definition |
|---|---|---|
| Attention | `twitter_sentiment_windows.last_cycle.author_stats.distinct_authors_total` | distinct posting authors in the scrape cycle recorded at session admission |
| Price path | `spot_prices[].mid` | mid price time series (~700 samples/session, ~10 s apart) |
| Quality gates | `...last_cycle.posts_total` > 0; `...sentiment_activity.is_silent` = false | keep only sessions with observable social activity |
| Regime label | `twitter_sentiment_meta.bucket_meta.methodology_regime` | pipeline version (see Section 3) |

## 3. Method (fully specified; no external code required)
**Attention spike.** For each coin, order its sessions in time. The *baseline* for a session is
the median of `distinct_authors_total` over that coin's **up to 20 immediately preceding
sessions (minimum 5)** - strictly prior, no look-ahead. The *attention spike* is the ratio of the session's own
`distinct_authors_total` to this baseline. A session is a **spike** if the ratio >= 6, and
**normal** if the ratio is between 0.8 and 1.2. Sessions with intermediate ratios belong to
neither group and are not compared (they are 61% of the analysis set).

**Forward price move.** From the session's `spot_prices` array, take the mid price of every
third sample (~30 s spacing); let m0 be the first. Compute the maximum gain, max(mid)/m0 - 1,
and the maximum drawdown, min(mid)/m0 - 1, over the ~2 h session. The **headline event** is a
*large move*: an excursion of at least X% in either direction - maximum gain >= X% **or** maximum
drawdown <= -X%. For the direction question we also record the two one-sided events (gain >= X%;
drawdown <= -X%) at the same X, and the signed return, (last mid)/m0 - 1. Attention is the state
at admission and the price path is what follows, so there is no look-ahead.

**Statistic.** Within each group (spike, normal), the *rate* of a large move is the fraction of
sessions that show one. The **lift** is the spike rate divided by the normal rate. Confidence
intervals are **day-level block bootstraps**: resample calendar days with replacement 1,000
times, recompute the lift each time from the sessions pooled over the resampled days, and take
the 2.5th-97.5th percentiles. Days (not sessions) are resampled because coin-sessions are
strongly cross-correlated within a day - a market-wide attention surge is one event, not
hundreds of independent ones - so resampling sessions would understate uncertainty. (Known
limitation: day blocks capture same-day clustering but multi-day attention waves induce serial
dependence across adjacent days, so the intervals may be slightly narrow.)

**Methodology-regime split.** The sentiment pipeline was revised in mid-February 2026 (scoring
models on 2026-02-16 05:14 UTC; a crypto-relevance filter on 2026-02-17 06:03 UTC), which
changes how `distinct_authors_total` is counted. We report the result within **V1** (before the
model update) and **V2** (from the filter activation), exclude the ~25 h window between the two
changes, and split V2 into a development window (2026-02-17 to 04-15) and a held-out window
(2026-04-16 to 07-06). Baselines are formed within each regime and never cross the cutover.

## 4. Results
Rate of a large move (|excursion| >= 4%), spike vs normal, with 95% day-block-bootstrap intervals
on the lift, and group sizes:

| Regime | n spike / normal | large-move rate: spike vs normal | lift (95% CI) |
|---|---|---|---|
| V1 (pre-filter) | 895 / 44,792 | 22.1% vs 5.2% | 4.21x [3.09-5.68] |
| V2 development | 1,123 / 37,748 | 14.0% vs 3.6% | 3.84x [2.93-5.05] |
| V2 held-out | 2,019 / 55,040 | 16.1% vs 5.2% | 3.11x [2.47-3.77] |

Every interval is above 1. The result is not an artifact of the 4% threshold: at 3% the lifts
are 3.16 / 2.66 / 2.21x, and at 5% they are 5.37 / 5.50 / 3.95x (V1 / V2dev / V2hold), all with
intervals above 1.

**The moves are direction-symmetric.** Decomposing the large move at a matched +/-4% threshold,
spike sessions show an elevated rate of a +4% upside move and a -4% downside move in similar
proportion (V1: 11.5% up / 13.2% down; V2dev: 8.5% / 7.0%; V2hold: 8.1% / 9.5%), against ~2-3%
for normal sessions on both sides, and the mean signed return of spike sessions is approximately
zero. The measured association is with volatility, not with direction.

**The result reproduces on the free sample.** The headline uses a multi-day trailing baseline
that the free weekly sample (one non-contiguous day - Sunday - per week) cannot reproduce. Using
instead an *intraday* baseline (each coin versus its earlier same-day sessions, otherwise
identical), the |move| >= 4% lift is 1.46x [1.20-1.78] on the full archive and 2.45x [1.64-3.48]
on the published free weekly samples. Two points reconcile these: (i) the intraday baseline has
few prior same-day sessions per coin, so it is a noisier proxy that misclassifies some spikes and
attenuates the lift toward 1 - which is why the trailing-20 construction is the primary
measurement and the intraday one is only the reproducibility check; and (ii) the free samples are
Sundays only, and the effect is stronger on Sundays: restricting the archive to its own Sundays and
applying the identical intraday computation gives 2.16x [1.38-3.47], consistent with the
free-sample figure. A reader with only the free weekly samples can therefore reproduce this number
directly (see Section 7).

## 5. Robustness & limitations
- Holds within both methodology regimes (V1, V2) and out-of-sample (held-out window).
- Holds across three move-size thresholds.
- Intervals are clustered by calendar day (see Section 3), with the stated serial-dependence caveat.
- In V2, attention is measured post-filter; the ratio-to-own-baseline construction absorbs most
  of the resulting level dependence, and the per-regime split documents robustness.
- Spikes are rare by construction (~1% of the analysis set); the reported group sizes are the
  effective sample behind each interval.

## 6. What this does not mean
- This is not a directional signal. Direction-symmetric movement is not tradable as "buy the
  spiking coin"; the elevated downside is as large as the upside.
- It does not claim that social sentiment (positive vs negative tone) predicts returns - a
  separate question addressed in the companion note.
- The ~2 h horizon and the spike threshold are fixed choices; other definitions may differ.

## 7. Reproduction
The method in Section 3 is specified entirely against named dataset fields and elementary arithmetic, so
it can be re-implemented independently. A self-contained implementation and a one-click reproduction
are also provided:
- **Read it (no login):** the notebook renders directly on GitHub -
  https://github.com/SiCkGFX/instrumetriq-public/blob/main/research/Attention_Volatility_Reproduction_Colab.ipynb
  - it re-implements the method from Section 3 step by step, naming each field and showing the arithmetic.
- **Run it (one click, no purchase):** open the same notebook in Colab -
  https://colab.research.google.com/github/SiCkGFX/instrumetriq-public/blob/main/research/Attention_Volatility_Reproduction_Colab.ipynb
  - it rebuilds the analysis on the published weekly samples and prints the free-sample lift (~2.4x).
- **Script:** `research/reproduce_attention_volatility.py` in this repository implements the Section 3
  computation. On the free weekly samples (`--mode intraday`) it reproduces the free-sample lift
  reported in Section 4; on the full Tier 3 archive (`--mode trailing`) it computes the archive-wide lift.
  The per-regime figures in the Section 4 table follow from applying the Section 3 method within each regime
  window (V1, V2 development, V2 held-out).

## 8. References
- Da, Z., Engelberg, J., & Gao, P. (2011). *In Search of Attention.* Journal of Finance,
  66(5), 1461-1499. https://onlinelibrary.wiley.com/doi/epdf/10.1111/j.1540-6261.2011.01679.x

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

The analysis uses the full Tier 3 archive as of the computation date; the free samples reproduce
the intraday variant above.
