#!/usr/bin/env python3
"""
Reproduce the Instrumetriq research note "Social attention spikes precede larger
intraday price moves in either direction".

Self-contained: reads a set of Tier 3 parquet files and reproduces the attention ->
large-move lift with a day-level block-bootstrap confidence interval, using only the
documented dataset fields and elementary arithmetic (no external data required).

  Free weekly samples  = one day per week (Sundays)  -> intraday baseline (default).
  Full Tier 3 archive  = contiguous daily history    -> --mode trailing (multi-day baseline).

Usage:
  pip install pandas pyarrow numpy
  python reproduce_attention_volatility.py --glob "samples/week_*/*_tier3.parquet"
  python reproduce_attention_volatility.py --glob "archive/*_tier3.parquet" --mode trailing
"""
import argparse, glob
import numpy as np, pandas as pd

# ---- spike / group definition (from the note) ----
SPIKE, NORM_LO, NORM_HI = 6.0, 0.8, 1.2
MOVE = 0.04   # a "large move" is a >= +/-4% intraday excursion in either direction


def extract(files):
    """Flatten Tier 3 records to (symbol, ts, authors, maxgain, maxdrawdown)."""
    rows = []
    for fp in files:
        df = pd.read_parquet(fp, columns=['symbol', 'snapshot_ts',
                                          'twitter_sentiment_windows', 'spot_prices'])
        for sym, ts, tsw, sp in zip(df['symbol'].values, df['snapshot_ts'].values,
                                    df['twitter_sentiment_windows'].values, df['spot_prices'].values):
            lc = tsw.get('last_cycle') if hasattr(tsw, 'get') else None
            if lc is None:
                continue
            # quality gates: observable social activity, not silent
            posts = lc.get('posts_total')
            silent = (lc.get('sentiment_activity') or {}).get('is_silent')
            authors = (lc.get('author_stats') or {}).get('distinct_authors_total')
            if not posts or silent or authors is None:
                continue
            # forward move from the ~2h price path (mid of every 3rd sample ~= 30s)
            if sp is None or len(sp) < 6:
                continue
            mids = [float(s['mid']) for s in sp[::3] if s.get('mid')]
            if len(mids) < 5 or not mids[0]:
                continue
            a = np.asarray(mids); m0 = a[0]
            rows.append((sym, pd.Timestamp(ts), float(authors),
                         a.max()/m0 - 1, a.min()/m0 - 1))
    d = pd.DataFrame(rows, columns=['symbol', 'ts', 'authors', 'maxgain', 'mdd'])
    d['ts'] = pd.to_datetime(d['ts'], utc=True)
    d['day'] = d['ts'].dt.strftime('%Y-%m-%d')
    return d.sort_values(['symbol', 'ts'])


def add_spike(d, mode):
    """Attention spike = authors / baseline. baseline is a past-only median of the coin's
    prior sessions: last 20 across days ('trailing'), or earlier same-day sessions ('intraday')."""
    if mode == 'trailing':
        base = d.groupby('symbol')['authors'].transform(
            lambda s: s.shift(1).rolling(20, min_periods=5).median())
    else:  # intraday
        base = d.groupby(['symbol', 'day'])['authors'].transform(
            lambda s: s.shift(1).expanding(min_periods=5).median())
    d = d.assign(baseline=base)
    d = d[d['baseline'] > 0].copy()
    d['spike'] = d['authors'] / d['baseline']
    return d


def lift_and_ci(d, B=1000, seed=0):
    """Large-move rate lift (spike vs normal) + 95% day-level block-bootstrap interval."""
    d = d.assign(_s=(d['spike'] >= SPIKE),
                 _n=((d['spike'] >= NORM_LO) & (d['spike'] <= NORM_HI)),
                 _h=((d['maxgain'] >= MOVE) | (d['mdd'] <= -MOVE)))   # either-direction large move
    d = d.assign(_sh=d['_s'] & d['_h'], _nh=d['_n'] & d['_h'])
    n_spike, n_norm = int(d['_s'].sum()), int(d['_n'].sum())
    rate_s = d.loc[d['_s'], '_h'].mean(); rate_n = d.loc[d['_n'], '_h'].mean()
    agg = d.groupby('day').agg(ns=('_s', 'sum'), nsh=('_sh', 'sum'), nn=('_n', 'sum'), nnh=('_nh', 'sum'))
    ns, nsh, nn, nnh = (agg[c].values.astype(float) for c in ('ns', 'nsh', 'nn', 'nnh'))
    D = len(agg); rng = np.random.default_rng(seed); lifts = []
    for _ in range(B):
        i = rng.integers(0, D, D)
        S, SH, N, NH = ns[i].sum(), nsh[i].sum(), nn[i].sum(), nnh[i].sum()
        if S and N and NH:
            lifts.append((SH/S) / (NH/N))
    lo, hi = (np.percentile(lifts, 2.5), np.percentile(lifts, 97.5)) if lifts else (np.nan, np.nan)
    return n_spike, n_norm, rate_s, rate_n, (rate_s/rate_n if rate_n else np.nan), lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', required=True, help='glob of Tier 3 parquet files')
    ap.add_argument('--mode', choices=['intraday', 'trailing'], default='intraday',
                    help='intraday = free weekly samples (Sundays); trailing = full contiguous archive')
    args = ap.parse_args()

    files = sorted(glob.glob(args.glob))
    if not files:
        raise SystemExit(f'no files matched: {args.glob}')
    print(f'reading {len(files)} Tier 3 file(s)...')
    d = extract(files)
    d = add_spike(d, args.mode)
    ns, nn, rs, rn, lift, lo, hi = lift_and_ci(d)
    print(f'\nAttention -> large-move (|excursion| >= {MOVE*100:.0f}%), {args.mode} baseline')
    print(f'  spike sessions (>=6x baseline):   {ns:,}')
    print(f'  normal sessions (0.8-1.2x):        {nn:,}')
    print(f'  large-move rate  spike vs normal:  {100*rs:.1f}%  vs  {100*rn:.1f}%')
    print(f'  LIFT: {lift:.2f}x   [95% day-block bootstrap: {lo:.2f} - {hi:.2f}]')
    print('\nNote: on the free weekly samples (Sundays), the intraday variant reproduces ~2.4x.')


if __name__ == '__main__':
    main()
