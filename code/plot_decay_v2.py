#!/usr/bin/env python3
"""
Decay figure v3: simplified.
- Circles = frozen from earliest period (main comparison)
- Only show GRF adjacent point (square) as the key finding
- Remove redundant adjacent points for Snake and Olympics
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
_data_path = REPO_ROOT / 'data' / 'controlled_snake' / 'summary.json'
with open(_data_path) as f:
    data = json.load(f)

fig, ax = plt.subplots(1, 1, figsize=(3.4, 2.8))

colors = {'Snake 3v3': '#43a047', 'GRF 11v11': '#c62828', 'Olympics': '#ef6c00'}

plotted = set()
for env, pts in data.items():
    c = colors[env]
    for p in pts:
        gap = p['time_gap_days']
        rho = p['pred_rho']
        is_frozen = (p['early_period'] == 0)

        # Skip adjacent points for Snake (near-perfect, redundant); keep Olympics
        if not is_frozen and env == 'Snake 3v3':
            continue

        if env not in plotted:
            ax.scatter(gap, rho, c=c, marker='o', s=55, zorder=5,
                      edgecolors='white', linewidth=0.8, label=env)
            plotted.add(env)
        else:
            ax.scatter(gap, rho, c=c, marker='o', s=55, zorder=5,
                      edgecolors='white', linewidth=0.8)

        # Highlight GRF adjacent point as a square
        if not is_frozen and env == 'GRF 11v11':
            ax.scatter(gap, rho, c=c, marker='s', s=70, zorder=6,
                      edgecolors='white', linewidth=1.0)
            ax.annotate('adjacent cohorts\n$\\rho=0.69$', (gap, rho),
                       textcoords="offset points", xytext=(0, 18),
                       fontsize=7, color=c, ha='center')

ax.axhline(y=0.8, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
ax.text(160, 0.81, r'$\rho=0.8$', fontsize=7, color='gray', ha='left')

ax.set_xlabel('Time gap (days)', fontsize=10)
ax.set_ylabel(r'Spearman $\rho$', fontsize=10)
ax.set_title('Ranking agreement: frozen vs living pool', fontsize=10)
ax.set_ylim(0.62, 1.02)
ax.set_xlim(150, 1050)
ax.legend(fontsize=8, loc='lower center', framealpha=0.9,
          bbox_to_anchor=(0.5, 0.02))
ax.tick_params(labelsize=8)
ax.grid(True, alpha=0.2)

plt.tight_layout()
out = str(REPO_ROOT / 'figures')
plt.savefig(f'{out}/fig_decay_pro.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig(f'{out}/fig_decay_pro.pdf', bbox_inches='tight', facecolor='white')
print("Done.")
