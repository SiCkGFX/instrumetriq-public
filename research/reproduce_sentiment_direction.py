#!/usr/bin/env python3
"""
Reproduce the Instrumetriq research note "Social sentiment tone shows no detectable
lead over short-horizon price direction".

Self-contained: reads a set of Tier 3 parquet files and computes the Spearman rank
correlation (information coefficient, IC) between sentiment tone and the signed forward
return at horizons k = 0, +1, +2 sessions, with a day-level block-bootstrap interval,
using only documented dataset fields and elementary arithmetic (no external data).

  Free weekly samples = one day per week (Sundays) -> within-day (same-day) lag pairs (default).
  Full Tier 3 archive = contiguous daily history   -> --mode sequence (cross-session lags).

Usage:
  pip install pandas pyarrow numpy
  python reproduce_sentiment_direction.py --glob "samples/week_*/*_tier3.parquet"
  python reproduce_sentiment_direction.py --glob "archive/*_tier3.parquet" --mode sequence
"""
import argparse, glob
import numpy as np, pandas as pd


def extract(files):
    """Flatten Tier 3 records to (symbol, ts, mean_score, pos_ratio, signed_return)."""
    rows = []
    for fp in files:
        df = pd.read_parquet(fp, columns=['symbol', 'snapshot_ts',
                                          'twitter_sentiment_windows', 'spot_prices'])
        for sym, ts, tsw, sp in zip(df['symbol'].values, df['snapshot_ts'].values,
                                    df['twitter_sentiment_windows'].values, df['spot_prices'].values):
            lc = tsw.get('last_cycle') if hasattr(tsw, 'get') else None
            if lc is None:
                continue
            posts = lc.get('posts_total')
            silent = (lc.get('sentiment_activity') or {}).get('is_silent')
            hds = lc.get('hybrid_decision_stats') or {}
            mean_score, pos_ratio = hds.get('mean_score'), hds.get('pos_ratio')
            if not posts or silent or mean_score is None:      # observable + scored, not silent
                continue
            if sp is None or len(sp) < 6:
                continue
            mids = [float(s['mid']) for s in sp[::3] if s.get('mid')]   # every 3rd mid ~= 30s
            if len(mids) < 5 or not mids[0]:
                continue
            sret = mids[-1] / mids[0] - 1                       # signed session return
            rows.append((sym, pd.Timestamp(ts), float(mean_score),
                         float(pos_ratio) if pos_ratio is not None else np.nan, sret))
    d = pd.DataFrame(rows, columns=['symbol', 'ts', 'mean_score', 'pos_ratio', 'sret'])
    d['ts'] = pd.to_datetime(d['ts'], utc=True)
    d['day'] = d['ts'].dt.strftime('%Y-%m-%d')
    return d.sort_values(['symbol', 'ts'])


def add_forward(d, mode):
    """Pair each session's tone with the signed return k sessions ahead (k=1,2).
    sequence = next session(s) for the coin (contiguous archive);
    intraday = next same-day session(s) for the coin (weekly Sunday samples)."""
    keys = ['symbol'] if mode == 'sequence' else ['symbol', 'day']
    g = d.groupby(keys)
    d = d.copy()
    d['fwd0'] = d['sret']            # same-session forward: tone vs this session's own return (no pairing)
    d['fwd1'] = g['sret'].shift(-1)
    d['fwd2'] = g['sret'].shift(-2)
    return d


def spearman(a, b):
    # standard Spearman: Pearson correlation of average-tied ranks (matches scipy.stats.spearmanr,
    # and unlike an ordinal-rank shortcut it is independent of row order when values tie)
    m = ~(np.isnan(a) | np.isnan(b)); a, b = a[m], b[m]
    if len(a) < 200:
        return float('nan'), 0
    ra = pd.Series(a).rank(method='average').values
    rb = pd.Series(b).rank(method='average').values
    return float(np.corrcoef(ra, rb)[0, 1]), len(a)


def ic_and_ci(d, sig, fwd, B=1000, seed=0):
    sub = d[['day', sig, fwd]].dropna()
    ic, n = spearman(sub[sig].values.astype(float), sub[fwd].values.astype(float))
    days = sub['day'].values; sv = sub[sig].values.astype(float); lv = sub[fwd].values.astype(float)
    uniq = np.array(sorted(sub['day'].unique())); idx = {u: np.where(days == u)[0] for u in uniq}
    rng = np.random.default_rng(seed); D = len(uniq); out = []
    for _ in range(B):
        pick = np.concatenate([idx[uniq[i]] for i in rng.integers(0, D, D)])
        v, _ = spearman(sv[pick], lv[pick])
        if not np.isnan(v):
            out.append(v)
    lo, hi = (np.percentile(out, 2.5), np.percentile(out, 97.5)) if out else (np.nan, np.nan)
    return ic, lo, hi, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', required=True, help='glob of Tier 3 parquet files')
    ap.add_argument('--mode', choices=['intraday', 'sequence'], default='intraday',
                    help='intraday = same-day lags (weekly samples); sequence = cross-session (archive)')
    args = ap.parse_args()

    files = sorted(glob.glob(args.glob))
    if not files:
        raise SystemExit(f'no files matched: {args.glob}')
    print(f'reading {len(files)} Tier 3 file(s)...')
    d = add_forward(extract(files), args.mode)
    lag = 'same-day' if args.mode == 'intraday' else 'next-session'
    print(f'\nSentiment tone -> signed forward return  ({lag} lags), IC with 95% day-block bootstrap')
    for sig in ['mean_score', 'pos_ratio']:
        for k, fwd in [(0, 'fwd0'), (1, 'fwd1'), (2, 'fwd2')]:
            ic, lo, hi, n = ic_and_ci(d, sig, fwd)
            print(f'  IC({sig:<10}, k=+{k}) = {ic:+.4f}   [95% {lo:+.4f}, {hi:+.4f}]   n={n:,}')
    print('\nA directional signal would show a materially non-zero IC at a no-look-ahead horizon.')


if __name__ == '__main__':
    main()
