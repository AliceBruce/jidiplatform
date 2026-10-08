#!/usr/bin/env python3
"""
Regenerate the anchor sub-study figure (Fig. 5, fig_learning_pro.png) from the verified
anchor/summary.csv delivered in jidi_system_data_reply_20261006_1551.

The redrawn figure shipped in the reply matches these numbers exactly; this script
makes it reproducible. (Note: the reply's regen_fig5.py is the monthly cumulative
growth figure from an older numbering -- it does NOT draw this figure, and the reply's
plot_pro_figures.py::plot_learning still draws the exp8 learning curves.)

Usage:
    python3 regen_fig5_anchor.py --summary /path/to/anchor/summary.csv \
                                 --out /path/to/fig_learning_pro.png
"""
import argparse
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_BLUE, C_ORANGE = '#4472C4', '#ED7D31'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    rows = {}
    with open(args.summary) as f:
        for r in csv.DictReader(f):
            if r['group'] == 'all_unique_users':
                rows[r['config']] = r

    strict, relaxed = rows['a5_d90'], rows['a3_d90']
    panels = [
        ('(a) Strict criterion (≥5 anchors)\n19 users, 6 environments', strict,
         'p=0.004 (Holm 0.008)'),
        ('(b) Relaxed criterion (≥3 anchors)\n36 users, 11 environments', relaxed,
         'p<0.001'),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9))
    for ax, (title, r, plabel) in zip(axes, panels):
        vals = [float(r['mean_anchor_pp']), float(r['mean_observed_pp'])]
        bars = ax.bar(['Fixed anchors', 'Moving pool'], vals,
                      color=[C_BLUE, C_ORANGE], width=0.5, edgecolor='white')
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2,
                    v + (1.2 if v >= 0 else -2.6),
                    f'{v:+.1f} pp', ha='center', fontsize=9)
        gap = float(r['mean_paired_difference_pp'])
        ax.set_title(title, loc='left', fontsize=10)
        ax.axhline(0, color='black', lw=0.8)
        ax.set_ylabel('Win-rate change (pp)')
        ax.set_ylim(-10, 16)
        ax.text(0.5, 13.5, f'paired gap {gap:+.1f} pp, {plabel}',
                ha='center', fontsize=8, color='0.25')

    plt.rcParams.update({'font.family': 'serif', 'savefig.dpi': 300, 'savefig.bbox': 'tight'})
    plt.tight_layout()
    plt.savefig(args.out)
    print(f'saved {args.out}')


if __name__ == '__main__':
    main()
