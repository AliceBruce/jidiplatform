# Living Benchmark Artifact (Anonymous Supplement)

> **Paper**: *Platform X: A Living Benchmark for Continuous Multi-Agent Reinforcement Learning Evaluation*
> **Track**: AAMAS 2027 Research Paper Track (double-blind)

This repository contains the data and analysis scripts supporting the empirical results in the paper. All reported statistics can be independently verified from these files.

## Repository Structure

```
data/
  tau/                          Per-environment payoff matrices + Hodge τ values
    tau_ge20.csv                Main table: τ, n, Elo convergence (13 environments, Table 3)
    aging_snapshots.csv         Pool growth snapshots (GRF 9→32, Olympics +6%)
    env{N}.json                 Win-rate matrices (complete-subset criterion, ≥10 matches/pair)
  controlled_snake/             §4.2 Controlled vintage-vs-size experiment (Snake 3v3, Table 4)
    summary.json                Spearman ρ, inversion %, top-k for old vs recent pools
    method.json                 Experimental design parameters
    target_rank_shifts.csv      Per-policy rank shifts (submission 11449: #13→#7)
    opponent_leave_out_diagnostic.csv  16/16 leave-one-out checks (all favor recent)
  controlled_grf_olympics/      §4.2 Controlled experiments (GRF + Olympics, Table 4)
    matrices_{A,B,C}.json       Win-rate matrices for each cohort (gap 6/12 months)
    cohorts.json                Cohort definitions and pool compositions
    validation.json             Validation checks
    opponent_sensitivity.csv    GRF 12-mo: 16/16 leave-one-out Δρ>0
  anchor/                       §4.3 Anchor sub-study (Table 5, Fig. 5)
    summary.csv                 Strict/relaxed criterion results (+9.1 vs −5.0 pp)
    anchor_registry.csv         Per-user details (19 users, 6 environments)
    endpoint_opponents.csv      Long-lived anchor opponent definitions
  exp7/                         §4.1, Table 3 Elo convergence column
    exp7_dynamics.csv           Per-environment Elo convergence ρ
    exp7_regression_results.json  τ–complexity regression (OLS)
    exp7_power_analysis.json    Statistical power analysis
  platform_stats/               §3 Operational audit + §4 platform scale
    2_1_user_info.json          User statistics (6,314 registered, long-tailed)
    2_2_policy_info.json        Policy version statistics (34,389 versions)
    2_3_env_info.json           Environment statistics (109 environments)
    2_5_competition_info.json   Competition statistics (18 international, 361 teams)
    2_6_freshness_quarterly.csv Pool freshness F(P_t) over quarterly snapshots

code/
  recompute_tau_from_matrices.py  Independent τ reproduction from raw matrices (Table 3)
  plot_dynamics_v3.py             Fig. 3: τ and Elo convergence across 13 environments
  regen_fig5_anchor.py            Fig. 5: Anchor sub-study visualization
  analyze_raw_matrices.py         Ranking method robustness (avg WR vs Elo vs α-Rank)
  verify_tau_definition.py        τ definition sanity checks
  plot_pro_figures.py             Platform statistics figures (freshness, growth)
  plot_decay_v2.py                Decay visualization from controlled experiment data
```

## Reproduction

### Environment

```bash
pip install -r requirements.txt
# Python 3.8+ required. Tested with numpy 1.24, scipy 1.10, matplotlib 3.7.
```

### Key reproductions

**1. Recompute τ from raw matrices (Table 3)**

```bash
python3 code/recompute_tau_from_matrices.py --data-dir data/tau
```

Output: Hodge τ for each environment (two estimator variants). Variant A (win-rate payoff A=2W−1) matches the paper's Table 3 values.

**2. Regenerate Fig. 3 (τ and Elo convergence)**

```bash
python3 code/plot_dynamics_v3.py \
    --tau-csv  data/tau/tau_ge20.csv \
    --exp7-csv data/exp7/exp7_dynamics.csv \
    --out      figures/fig_dynamics_pro.png
```

Printed values should match Table 3 exactly (13 environments).

**3. Regenerate Fig. 5 (anchor sub-study)**

```bash
python3 code/regen_fig5_anchor.py \
    --summary data/anchor/summary.csv \
    --out     figures/fig_learning_pro.png
```

Key values: strict criterion 19 users / 6 envs, +9.1 vs −5.0 pp, gap +14.1 pp (p=0.004, Holm p=0.008).

**4. Verify controlled experiment (Table 4)**

Read `data/controlled_snake/summary.json` for Snake 3v3 results:
- Old pool: ρ=0.856 (16.3% inversions), Recent pool: ρ=0.933 (7.7% inversions)
- 16/16 leave-one-out checks in `opponent_leave_out_diagnostic.csv` favor the recent pool

Read `data/controlled_grf_olympics/matrices_{A,B,C}.json` for GRF and Olympics cohorts.

**5. Verify anchor study (§4.3)**

Read `data/anchor/summary.csv`:
- Strict (≥5 anchors): 19 users, 6 envs, +9.08 / −5.01 / +14.09 pp, p=0.0039, Holm p=0.0078
- Relaxed (≥3 anchors): 36 users, 11 envs, +11.77 / −1.65 / +13.42 pp, p<0.001

## Data Notes

- **Payoff matrices** (`tau/env{N}.json`): Complete-subset criterion (every pair ≥10 matches, one strategy per user, outcome-blind multistart-greedy selection). Win-rate matrix P; Hodge decomposition A=2P−1 → A=A_T+A_C → τ=‖A_C‖²_F/‖A‖²_F.
- **Subset sizes**: 20–148 strategies from 21–210 eligible users per environment. Selection skews toward more active users (caveat noted in paper §4.1).
- **Controlled experiments**: Equal-sized non-overlapping pools. Targets scored against old vs recent pool; agreement measured by Spearman ρ against an independent reference.
- **Anchor analysis**: Users with ≥90 days activity and ≥5 long-lived anchor opponents present at both endpoints. Win-rate change measured against fixed anchors vs moving pool.
