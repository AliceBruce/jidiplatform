#!/usr/bin/env python3
"""
Fig. 4 (fig_dynamics_pro.png) -- CORRECTED data pipeline.

The shipped plot_dynamics_v2.py reads exp7/exp7_dynamics.csv for BOTH panels, but the
exp7 tau column holds the earlier exploratory criterion (tau=.053-.854, ordering
inverted) and cannot have produced the shipped figure. The shipped figure's panel (a)
matches tau/tau_ge20.csv (the verified complete-subset criterion) and panel (b) matches
the exp7 Elo-convergence column. This script reads the correct sources:

  panel (a): tau_ge20.csv   -- env_id, env_name, tau, complete_subset_size
  panel (b): exp7_dynamics.csv -- env_id, elo_convergence_rho

Verified 2026-10-06: printed values match Table 3 exactly.

Usage:
    python3 plot_dynamics_v3.py \
        --tau-csv  /path/to/tau_ge20.csv \
        --exp7-csv /path/to/exp7_dynamics.csv \
        --out      /path/to/fig_dynamics_pro.png
"""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_GREEN, C_ORANGE, C_RED = '#70AD47', '#ED7D31', '#C0504D'

PRETTY = {
    'snakes_1v1': 'snakes 1v1', 'snakes_3v3': 'snakes 3v3',
    'olympics-integrated': 'olympics integrated',
    'football_11_vs_11_stochastic': 'grf 11v11',
    'reversi_1v1': 'reversi 1v1', 'gobang_1v1': 'gobang 1v1',
    'olympics-running': 'olympics running',
    'olympics-tablehockey': 'olympics table hockey',
    'football_5v5_malib': 'grf 5v5',
    'olympics-wrestling': 'olympics wrestling',
    'delivery_two_agents': 'delivery 2 agents',
    'olympics-football': 'olympics football',
    'chessandcard-leduc_holdem_v3': "leduc hold'em",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tau-csv', required=True)
    ap.add_argument('--exp7-csv', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    tau_rows = []
    with open(args.tau_csv) as f:
        for r in csv.DictReader(f):
            tau_rows.append((int(r['env_id']), r['env_name'], float(r['tau']),
                             int(r['complete_subset_size'])))
    elo = {}
    with open(args.exp7_csv) as f:
        for r in csv.DictReader(f):
            if r.get('elo_convergence_rho'):
                elo[int(r['env_id'])] = float(r['elo_convergence_rho'])

    tau_rows.sort(key=lambda x: x[2])
    print('panel (a): env  tau     n     (should match Table 3)')
    for eid, name, tau, n in tau_rows:
        print(f'  {PRETTY.get(name, name):24s} {tau:.3f}  {n:3d}')

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))

    ax = axes[0]
    names = [PRETTY.get(n, n) for _, n, _, _ in tau_rows]
    vals = [t for _, _, t, _ in tau_rows]
    colors = [C_GREEN if t < 0.2 else C_ORANGE if t < 0.6 else C_RED for t in vals]
    y = range(len(tau_rows))
    ax.barh(y, vals, color=colors, height=0.7, edgecolor='white', linewidth=0.5)
    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=7)
    ax.set_xlabel(r'Non-transitivity $\tau$')
    ax.set_title('(a) Environments ranked by $\\tau$', loc='left', fontsize=10)
    ax.set_xlim(0, 0.9)

    ax = axes[1]
    rows = sorted([(eid, elo[eid], name) for eid, name, _, _ in tau_rows if eid in elo],
                  key=lambda x: x[1])
    names2 = [PRETTY.get(n, n) for _, _, n in rows]
    vals2 = [e for _, e, _ in rows]
    colors2 = [C_GREEN if e > 0.8 else C_ORANGE if e > 0.6 else C_RED for e in vals2]
    ax.barh(range(len(rows)), vals2, color=colors2, height=0.7, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(names2, fontsize=7)
    ax.set_xlabel(r'Elo convergence $\rho$')
    ax.set_title('(b) Rating stability across periods', loc='left', fontsize=10)
    ax.set_xlim(0.3, 1.0)
    ax.axvline(x=0.8, color='gray', ls=':', lw=0.8, alpha=0.5)

    plt.rcParams.update({'font.family': 'serif', 'savefig.dpi': 300, 'savefig.bbox': 'tight'})
    plt.tight_layout()
    plt.savefig(args.out)
    print(f'saved {args.out}')


if __name__ == '__main__':
    main()
