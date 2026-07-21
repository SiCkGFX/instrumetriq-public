#!/usr/bin/env python3
"""
Reproduce the Instrumetriq research note "Social attention adds no predictive power
for intraday move size beyond price volatility".

The companion note showed an attention spike precedes a larger intraday move. This note
asks whether attention adds anything a plain price-volatility measure does not. It does
not - and that holds no matter how "attention" is measured.

"Attention" is not just a head count. We measure it FOUR ways, each as a spike over the
coin's own baseline:
  * authors     - distinct posting authors
  * engagement  - likes + retweets
  * reach        - sum of poster followers
  * EC          - the Engagement Coefficient the Instrumetriq extension shows as a
                  coin's "chatter level": (likes + retweets) * log(1 + followers) / posts

Ranking skill is AUC (probability a reading ranks a real large-mover above a non-mover;
0.50 = a coin flip). Added value = how much an attention measure improves an
out-of-sample model that already has price volatility. A positive control (a feature
that peeks at the answer) confirms the added-value test can see real signal.

Volatility is `spot_raw.range_pct_24h` - the admission-time 24h price range, price-only,
so no look-ahead.

Usage:
  pip install pandas pyarrow numpy scikit-learn
  python reproduce_attention_incremental_null.py --glob "samples/week_*/*_tier3.parquet"
  python reproduce_attention_incremental_null.py --glob "archive/*_tier3.parquet" --mode trailing
"""
import argparse, glob
import numpy as np, pandas as pd

SPIKE, NORM_LO, NORM_HI = 6.0, 0.8, 1.2
THRESHOLDS = (0.03, 0.04, 0.05)
MEASURES = ('authors', 'engagement', 'reach', 'EC')


def extract(files):
    rows = []
    for fp in files:
        df = pd.read_parquet(fp, columns=['symbol', 'snapshot_ts',
                                          'twitter_sentiment_windows', 'spot_raw', 'spot_prices'])
        for sym, ts, tsw, sr, sp in zip(df['symbol'].values, df['snapshot_ts'].values,
                                        df['twitter_sentiment_windows'].values,
                                        df['spot_raw'].values, df['spot_prices'].values):
            lc = tsw.get('last_cycle') if hasattr(tsw, 'get') else None
            if lc is None:
                continue
            posts = lc.get('posts_total')
            silent = (lc.get('sentiment_activity') or {}).get('is_silent')
            astat = lc.get('author_stats') or {}
            eng = lc.get('platform_engagement') or {}
            authors = astat.get('distinct_authors_total')
            reach = astat.get('followers_count_sum')
            engagement = (eng.get('total_likes') or 0) + (eng.get('total_retweets') or 0)
            vol24 = sr.get('range_pct_24h') if hasattr(sr, 'get') else None
            if not posts or silent or authors is None or vol24 is None:
                continue
            if sp is None or len(sp) < 6:
                continue
            mids = [float(s['mid']) for s in sp[::3] if s.get('mid')]
            if len(mids) < 5 or not mids[0]:
                continue
            a = np.asarray(mids)
            EC = engagement * np.log1p(reach or 0) / posts      # the extension's Engagement Coefficient
            rows.append((sym, pd.Timestamp(ts), float(authors), float(engagement),
                         float(reach or 0), float(EC), float(vol24), float(np.max(np.abs(a / a[0] - 1.0)))))
    d = pd.DataFrame(rows, columns=['symbol', 'ts', 'authors', 'engagement', 'reach', 'EC', 'vol24', 'maxabs'])
    d['ts'] = pd.to_datetime(d['ts'], utc=True)
    d['day'] = d['ts'].dt.strftime('%Y-%m-%d')
    return d.sort_values(['symbol', 'ts'])


def add_spikes(d, mode):
    """Spike ratio = value / past-only baseline, for each attention measure."""
    for m in MEASURES:
        if mode == 'trailing':
            base = d.groupby('symbol')[m].transform(lambda s: s.shift(1).rolling(20, min_periods=5).median())
        else:
            base = d.groupby(['symbol', 'day'])[m].transform(lambda s: s.shift(1).expanding(min_periods=5).median())
        d[m + '_spike'] = np.where(base > 0, d[m] / base, np.nan)
    return d[np.isfinite(d['authors_spike'])].copy()


def auc(score, label):
    score = np.asarray(score, float); label = np.asarray(label, float)
    ok = ~np.isnan(score); score, label = score[ok], label[ok]
    n1, n = label.sum(), len(label)
    if n1 == 0 or n1 == n or n < 30:
        return None
    order = np.argsort(score, kind='mergesort'); ranks = np.empty(n); ranks[order] = np.arange(1, n + 1)
    return float((ranks[label == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (n - n1)))


def oos_auc(X, y, train, test):
    from sklearn.linear_model import LogisticRegression
    Xtr, Xte, ytr, yte = X[train], X[test], y[train], y[test]
    if ytr.sum() < 10 or yte.sum() < 10:
        return None
    med = np.nanmedian(Xtr, 0)
    Xtr = np.where(np.isnan(Xtr), med, Xtr); Xte = np.where(np.isnan(Xte), med, Xte)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    m = LogisticRegression(max_iter=2000, class_weight='balanced').fit((Xtr - mu) / sd, ytr)
    return auc(m.predict_proba((Xte - mu) / sd)[:, 1], yte)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', required=True)
    ap.add_argument('--mode', choices=['intraday', 'trailing'], default='intraday')
    args = ap.parse_args()
    files = sorted(glob.glob(args.glob))
    if not files:
        raise SystemExit(f'no files matched: {args.glob}')
    print(f'reading {len(files)} Tier 3 file(s)...')
    d = add_spikes(extract(files), args.mode)
    days = np.sort(d['day'].unique())
    cut = days[int(len(days) * 0.70)] if len(days) > 3 else days[len(days) // 2]
    train = d['day'].values < cut; test = d['day'].values >= cut
    vol = d['vol24'].values
    print(f'\n{len(d):,} sessions | train {train.sum():,} (< {cut}) | test {test.sum():,} (>= {cut})')

    # (0) reproduce the companion note's lift, using ITS measure (author-count spike)
    print("\n(0) Attention lift (author-count spike, reproduces the companion note):")
    for thr in THRESHOLDS:
        h = d['maxabs'].values >= thr
        s = d['authors_spike'].values >= SPIKE
        n = (d['authors_spike'].values >= NORM_LO) & (d['authors_spike'].values <= NORM_HI)
        print(f'    |move|>={thr:.0%}: spike {h[s].mean():5.1%} vs normal {h[n].mean():5.1%}  lift={h[s].mean()/h[n].mean():.2f}x')

    # (A) ranking skill + added value over volatility, for EACH attention measure
    y = (d['maxabs'].values >= 0.04).astype(float)          # large move = |move| >= 4%
    a_vol = oos_auc(vol[:, None], y, train, test)
    print(f'\n(A) Move size >= 4%. Price volatility ranks movers at AUC {a_vol:.3f}. Each attention measure:')
    print(f'    {"attention measure":20s} {"ranking skill (AUC)":>19}  {"added over volatility":>21}')
    for m in MEASURES:
        sp = d[m + '_spike'].values
        a_s = auc(sp[test], y[test])
        a_va = oos_auc(np.column_stack([vol, np.log1p(d[m].values), sp]), y, train, test)
        print(f'    {m:20s} {a_s:>19.3f}  {a_va - a_vol:>+21.3f}')

    # positive control
    print('\n(control) swap attention for a feature that peeks at the answer (must jump):')
    g = np.random.default_rng(0)
    for noise in (0.5, 2.0):
        cheat = y + g.normal(0, noise, len(y))
        a_vc = oos_auc(np.column_stack([vol, cheat]), y, train, test)
        print(f'    noise={noise}: volatility {a_vol:.3f} -> volatility+cheat {a_vc:.3f}   = {a_vc - a_vol:+.3f}')

    print('\nReading: every attention measure ranks movers near a coin flip and adds ~0 to'
          '\nvolatility, while the cheat feature adds a lot. Attention (by any measure) is a'
          '\nshadow of volatility, not an independent predictor of move size.')


if __name__ == '__main__':
    main()
