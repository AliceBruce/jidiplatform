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
    decay_results.json          Time-gap decay analysis (frozen vs living pool comparison)
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
  exp8/                         §6.2 User learning dynamics
    exp8_user_learning_curves.csv  Per-user learning trajectories (411 trajectories, 376 users)
    exp8_retention_analysis.csv    30/60/90-day retention rates
    exp8_learning_curves.png       Low/Mid/High tier learning curve visualization
    exp8_retention.png             Retention rate bar chart
  exp6/                         §6.1 Competition ecosystem analysis
    exp6_level_summary.json     Competition level statistics
    exp6_comp_vs_baseline.json  Competition vs baseline comparison
    exp6_competition_timeline.csv  Competition timeline data
    exp6_window_stats.csv       Windowed statistics
  case_study/                   Case study visualization data
  platform_stats/               §3 Operational audit + §4 platform scale
    2_1_user_info.json          User statistics (6,314 registered, long-tailed)
    2_2_policy_info.json        Policy version statistics (34,389 versions)
    2_3_env_info.json           Environment statistics (109 environments)
    2_5_competition_info.json   Competition statistics (18 international, 361 teams)
    2_6_freshness_quarterly.csv Pool freshness F(P_t) over quarterly snapshots

code/
  recompute_tau.py              Independent τ reproduction from raw matrices (Table 3)
  plot_dynamics_v3.py           Fig. 3: τ and Elo convergence across 13 environments
  regen_fig5_anchor.py          Fig. 5: Anchor sub-study visualization
  analyze_raw_matrices.py       Ranking method robustness (avg WR vs Elo vs α-Rank)
  plot_pro_figures.py           Platform statistics figures (freshness, growth, learning)
  plot_decay_v2.py              Decay visualization from controlled experiment data
```

## Reproduction

### Requirements

```bash
pip install -r requirements.txt
```

Or with conda:
```bash
conda install numpy scipy matplotlib pandas
```

### Key numerical checks

**Table 3 (τ values):**
```bash
python3 code/recompute_tau.py --data-dir data/tau
```
Expected output: All 12 environments PASS (τ matches `tau_ge20.csv` to 1e-6).

**Fig. 3 (τ and Elo convergence):**
```bash
python3 code/plot_dynamics_v3.py --tau-csv data/tau/tau_ge20.csv \
                                  --exp7-csv data/exp7/exp7_dynamics.csv \
                                  --out figures/exp7_dynamics_v3.png
```

**Fig. 5 (anchor study):**
```bash
python3 code/regen_fig5_anchor.py --summary data/anchor/summary.csv \
                                    --out figures/anchor_study_v5.png
```

**All figures:**
```bash
python3 code/plot_pro_figures.py
python3 code/plot_decay_v2.py
```

### Key values to verify

From `data/tau/tau_ge20.csv` (paper Table 3):

| Environment | τ | n | Elo ρ |
|-------------|---|---|-------|
| snakes_1v1 | 0.125 | 148 | 0.999 |
| snakes_3v3 | 0.125 | 121 | 0.999 |
| olympics-integrated | 0.165 | 38 | 0.997 |
| football_11v11 | 0.175 | 25 | 0.998 |
| reversi_1v1 | 0.483 | 83 | 0.999 |

From `data/anchor/summary.csv` (paper Table 5):
- Strict criterion (≥5 anchors): +9.1 pp gap, p=0.004
- Relaxed criterion (≥3 anchors): +6.2 pp gap, p<0.001

From `data/controlled_snake/summary.json` (paper Table 4):
- Recent pool ρ=0.933 vs Old pool ρ=0.856
- 15/15 rank inversions favor recent pool

## Notes

- All τ values are computed via Hodge decomposition: τ = ||A_C||²_F / ||A||²_F where A = 2W-1
- Payoff matrices use the complete-subset criterion (≥10 matches per pair, ≥20 users)
- User tiers (Low/Mid/High) in exp8 are computed by terciles of final_winrate

## Anonymization

- No user IDs, submission IDs, or timestamps are included
- All data are aggregated statistics (win-rate matrices, summary statistics)
- Platform name is anonymized as "Platform X" in the paper
