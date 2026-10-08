#!/usr/bin/env python3
"""
Recompute Hodge non-transitivity tau from the per-environment win-rate matrices.

Reads data/tau/env{N}.json files. Each file contains:
  - win_rate_matrix: NxN pairwise win-rate matrix
  - user_ids: list of user IDs (length N)
  - tau: pre-computed tau value (for cross-check)

Computes tau via Hodge decomposition:
  A = 2W - 1  (win-rate payoff, unplayed pairs filled with 0.5)
  A_T = transitive component (potential field)
  A_C = cyclic component
  tau = ||A_C||_F^2 / ||A||_F^2

Usage:
    python3 code/recompute_tau.py --data-dir data/tau

Cross-checks against tau_ge20.csv (paper Table 3 values).
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def hodge_tau(A):
    """Compute Hodge non-transitivity tau from skew-symmetric matrix A."""
    A = (A - A.T) / 2.0
    p = A.mean(axis=1)
    A_T = p[:, None] - p[None, :]
    A_C = A - A_T
    norm_A = np.sum(A ** 2)
    if norm_A == 0:
        return 0.0
    return float(np.sum(A_C ** 2) / norm_A)


def main():
    ap = argparse.ArgumentParser(description="Recompute tau from payoff matrices")
    ap.add_argument("--data-dir", default="data/tau",
                    help="directory containing env*.json files")
    args = ap.parse_args()
    base = Path(args.data_dir)

    # Load reference tau from tau_ge20.csv
    ref_tau = {}
    csv_path = base / "tau_ge20.csv"
    if csv_path.exists():
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                ref_tau[int(row["env_id"])] = {
                    "name": row["env_name"],
                    "n": int(row["complete_subset_size"]),
                    "tau": float(row["tau"]),
                }

    # Paper Table 3 environments (13 envs with n>=20)
    table3_envs = [1, 6, 88, 34, 10, 2, 3, 71, 72, 74, 47, 73, 86]

    print(f"{'env':>5} {'name':>22} {'n':>4} {'tau_computed':>12} {'tau_json':>10} "
          f"{'tau_ref':>10} {'match':>6}")
    print("-" * 80)

    all_pass = True
    for env_json in sorted(base.glob("env*.json")):
        env_id = int(env_json.stem.replace("env", ""))
        with open(env_json) as f:
            d = json.load(f)

        W = np.array(d["win_rate_matrix"], dtype=float)
        n = W.shape[0]
        tau_json = d.get("tau", None)

        # Compute tau: A = 2W-1, fill NaN with 0.5 (draw)
        W_filled = np.where(np.isnan(W), 0.5, W)
        A = 2 * W_filled - 1
        np.fill_diagonal(A, 0.0)
        tau_computed = hodge_tau(A)

        # Cross-check with reference
        ref = ref_tau.get(env_id, {})
        tau_ref = ref.get("tau", None)
        ref_n = ref.get("n", None)
        name = ref.get("name", env_json.stem)

        # Check match
        if tau_ref is not None:
            match = abs(tau_computed - tau_ref) < 1e-6
            mark = "PASS" if match else "FAIL"
            if not match:
                all_pass = False
        else:
            mark = "n/a"

        # Print Table 3 envs in paper order, others after
        if env_id in table3_envs:
            print(f"env{env_id:<3} {name:>22} {n:>4} {tau_computed:>12.10f} "
                  f"{tau_json if tau_json else 'N/A':>10} "
                  f"{tau_ref if tau_ref else 'N/A':>10} {mark:>6}")

    print("-" * 80)
    if all_pass:
        print("ALL CHECKS PASSED: computed tau matches tau_ge20.csv to 1e-6.")
    else:
        print("SOME CHECKS FAILED: see FAIL entries above.")

    # Print paper Table 3 formatted values (3 decimal places)
    print("\nPaper Table 3 formatted values (3 decimal places):")
    for env_id in table3_envs:
        env_json = base / f"env{env_id}.json"
        if not env_json.exists():
            continue
        with open(env_json) as f:
            d = json.load(f)
        W = np.array(d["win_rate_matrix"], dtype=float)
        n = W.shape[0]
        W_filled = np.where(np.isnan(W), 0.5, W)
        A = 2 * W_filled - 1
        np.fill_diagonal(A, 0.0)
        tau = hodge_tau(A)
        ref = ref_tau.get(env_id, {})
        name = ref.get("name", f"env{env_id}")
        print(f"  {name:>22}  tau={tau:.3f}  n={n}")


if __name__ == "__main__":
    main()
