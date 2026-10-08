#!/usr/bin/env python3
"""Professional academic-style figures for Platform X system paper."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import json
from pathlib import Path

# ---- Style ----
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif', 'Times New Roman'],
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'figure.dpi': 200,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Color palette (colorblind-friendly)
C_BLUE = '#4472C4'
C_ORANGE = '#ED7D31'
C_GREEN = '#70AD47'
C_RED = '#C0504D'
C_GRAY = '#A5A5A5'
C_PURPLE = '#7030A0'

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / 'data'
OUT = REPO_ROOT / 'figures'
OUT.mkdir(exist_ok=True)

# ============================================================
# Figure: Cross-environment dynamics (4-panel)
# ============================================================
def plot_dynamics():
    df = pd.read_csv(BASE / 'exp7/exp7_dynamics.csv')
    # Filter to environments with valid tau
    d = df.dropna(subset=['tau', 'complexity']).copy()
    d = d[d['tau'] > 0.01]  # exclude single-agent
    d = d.sort_values('tau', ascending=True)

    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.2))

    # (a) tau vs complexity
    ax = axes[0, 0]
    ax.scatter(d['complexity'], d['tau'], s=30, color=C_BLUE, zorder=3, edgecolors='white', linewidth=0.5)
    # regression line
    mask = d['tau'].notna() & d['complexity'].notna()
    if mask.sum() > 2:
        z = np.polyfit(d.loc[mask, 'complexity'], d.loc[mask, 'tau'], 1)
        xline = np.linspace(d['complexity'].min(), d['complexity'].max(), 50)
        ax.plot(xline, np.polyval(z, xline), '--', color=C_RED, alpha=0.7, lw=1.2, label=f'$R^2$=0.20, $p$=0.11')
    ax.set_xlabel('Complexity score')
    ax.set_ylabel(r'Non-transitivity $\tau$')
    ax.set_title('(a) Non-transitivity vs. complexity', loc='left', fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(0, 0.9)

    # (b) Elo convergence vs complexity
    ax = axes[0, 1]
    d2 = d.dropna(subset=['elo_convergence_rho'])
    ax.scatter(d2['complexity'], d2['elo_convergence_rho'], s=30, color=C_ORANGE, zorder=3, edgecolors='white', linewidth=0.5)
    ax.set_xlabel('Complexity score')
    ax.set_ylabel(r'Elo convergence $\rho$')
    ax.set_title('(b) Rating convergence vs. complexity', loc='left', fontsize=10)
    ax.set_ylim(0.3, 1.0)

    # (c) tau ranked horizontal bar
    ax = axes[1, 0]
    d_sorted = d.sort_values('tau', ascending=True)
    names = [n.replace('_', ' ') for n in d_sorted['name'].values]
    y_pos = np.arange(len(d_sorted))
    colors = [C_BLUE if t < 0.5 else C_RED for t in d_sorted['tau']]
    ax.barh(y_pos, d_sorted['tau'], color=colors, height=0.7, edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=7)
    ax.set_xlabel(r'Non-transitivity $\tau$')
    ax.set_title(r'(c) Environments ranked by $\tau$', loc='left', fontsize=10)
    ax.set_xlim(0, 0.9)

    # (d) improvement speed horizontal bar
    ax = axes[1, 1]
    d3 = d.dropna(subset=['improvement_speed']).copy()
    d3 = d3.sort_values('improvement_speed', ascending=True)
    names3 = [n.replace('_', ' ') for n in d3['name'].values]
    y_pos3 = np.arange(len(d3))
    colors3 = [C_RED if v < 0 else C_GREEN for v in d3['improvement_speed']]
    ax.barh(y_pos3, d3['improvement_speed'], color=colors3, height=0.7, edgecolor='white', linewidth=0.5)
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_yticks(y_pos3)
    ax.set_yticklabels(names3, fontsize=7)
    ax.set_xlabel('Elo improvement speed (per month)')
    ax.set_title('(d) Pool improvement rate', loc='left', fontsize=10)

    plt.tight_layout()
    plt.savefig(OUT / 'fig_dynamics_pro.png')
    plt.savefig(OUT / 'fig_dynamics_pro.pdf')
    plt.close()
    print('Saved fig_dynamics_pro')


# ============================================================
# Figure: User learning trajectories (3-panel)
# ============================================================
def plot_learning():
    df = pd.read_csv(BASE / 'exp8/exp8_user_learning_curves.csv')
    tiers = ['Low', 'Mid', 'High']
    tier_colors = {'Low': C_BLUE, 'Mid': C_ORANGE, 'High': C_GREEN}

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.8))

    # (a) Initial vs Final win rate boxplot
    ax = axes[0]
    data_init = []
    data_final = []
    for t in tiers:
        sub = df[df['paper_tier'] == t]
        data_init.append(sub['initial_winrate'].values)
        data_final.append(sub['final_winrate'].values)

    bp1 = ax.boxplot(data_init, positions=np.arange(3)-0.15, widths=0.28, patch_artist=True,
                     showfliers=False, medianprops=dict(color='black', lw=1))
    bp2 = ax.boxplot(data_final, positions=np.arange(3)+0.15, widths=0.28, patch_artist=True,
                     showfliers=False, medianprops=dict(color='black', lw=1))
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(tiers)
    for patch, c in zip(bp1['boxes'], [C_GRAY]*3):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    for patch in bp2['boxes']:
        patch.set_facecolor('#5b9bd5')
        patch.set_alpha(0.7)
    ax.set_ylabel('Win rate')
    ax.set_title('(a) Initial vs. final win rate', loc='left', fontsize=10)
    ax.set_ylim(0, 1.05)
    from matplotlib.patches import Patch
    ax.legend([Patch(facecolor=C_GRAY, alpha=0.7), Patch(facecolor='#5b9bd5', alpha=0.7)],
              ['Initial', 'Final'], frameon=False, fontsize=8, loc='upper left')

    # (b) Version count boxplot
    ax = axes[1]
    data_ver = [df[df['paper_tier'] == t]['n_versions'].values for t in tiers]
    bp = ax.boxplot(data_ver, patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', lw=1))
    ax.set_xticklabels(tiers)
    for patch, t in zip(bp['boxes'], tiers):
        patch.set_facecolor(tier_colors[t])
        patch.set_alpha(0.7)
    ax.set_ylabel('Number of submitted versions')
    ax.set_title('(b) Iteration depth', loc='left', fontsize=10)

    # (c) Best-fit model share
    ax = axes[2]
    models = ['linear', 'log', 'power']
    model_colors = [C_BLUE, C_ORANGE, C_GREEN]
    x = np.arange(len(tiers))
    width = 0.25
    for i, (m, c) in enumerate(zip(models, model_colors)):
        shares = []
        for t in tiers:
            sub = df[df['paper_tier'] == t]
            shares.append((sub['best_model'] == m).mean() * 100)
        ax.bar(x + i*width - width, shares, width, label=m, color=c, edgecolor='white', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(tiers)
    ax.set_ylabel('Share of trajectories (%)')
    ax.set_title('(c) Best-fit model', loc='left', fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc='upper right')
    ax.set_ylim(0, 60)

    plt.tight_layout()
    plt.savefig(OUT / 'fig_learning_pro.png')
    plt.savefig(OUT / 'fig_learning_pro.pdf')
    plt.close()
    print('Saved fig_learning_pro')


# ============================================================
# Figure: Competition pulse (bar chart)
# ============================================================
def plot_pulse():
    with open(BASE / 'exp6/exp6_level_summary.json') as f:
        data = json.load(f)

    tiers = ['international-top', 'national', 'university', 'other']
    tier_labels = ['International\ntop-tier', 'National', 'University', 'Other']
    subs_med = [data[t]['median_subs_multiplier'] for t in tiers]
    users_med = [data[t]['median_users_multiplier'] for t in tiers]
    subs_n = [data[t]['n_competitions'] for t in tiers]

    fig, ax = plt.subplots(figsize=(4.5, 3.0))
    x = np.arange(len(tiers))
    width = 0.35
    bars1 = ax.bar(x - width/2, subs_med, width, label='Submissions', color=C_BLUE, edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, users_med, width, label='Registrations', color=C_ORANGE, edgecolor='white', linewidth=0.5)

    ax.axhline(y=1.0, color='black', linestyle=':', linewidth=1, alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(tier_labels, fontsize=9)
    ax.set_ylabel('Median multiplier (vs. baseline)')
    ax.set_ylim(0, 7)
    ax.legend(frameon=False, fontsize=9, loc='upper right')

    # Annotate values
    for bar, val, n in zip(bars1, subs_med, subs_n):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{val:.2f}×\nn={n}', ha='center', va='bottom', fontsize=7)

    plt.tight_layout()
    plt.savefig(OUT / 'fig_pulse_pro.png')
    plt.savefig(OUT / 'fig_pulse_pro.pdf')
    plt.close()
    print('Saved fig_pulse_pro')


if __name__ == '__main__':
    plot_dynamics()
    plot_learning()
    plot_pulse()
    print('All figures done.')
