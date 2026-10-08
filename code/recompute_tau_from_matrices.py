#!/usr/bin/env python3
"""
Recompute Hodge non-transitivity tau from the raw round-robin win-rate matrices.

Motivation (2026-10-06 audit): the tau/n columns in Table 3 of main.tex do not
trace to any script or data file in either handoff package. This script is the
verified reference recomputation on the best available data: the per-user
round-robin evaluation matrices shipped in jidi_system_plot_data_20260926.zip
under data/raw_evaluation/env{6,34,88}_matrix.json
(sources: snakes3v3 / football11v11 / olympics winrate data, 10/5 eps per pair).

Usage:
    python3 recompute_tau_from_matrices.py --data-dir /path/to/plot_data/data

Outputs both estimator variants:
  A. win-rate payoff  A = 2W - 1           (exp7's definition, continuous)
  B. majority vote    A_ij = sign(W_ij-.5) (the paper's stated definition, +-1)

Verified results (2026-10-06, matrices n=206/61/111 unique users):
  env6  Snake 3v3        cyclic A=.1774  B=.3334   (paper claims .125, n=121)
  env34 GRF 11v11        cyclic A=.3066  B=.4423   (paper claims .175, n=25)
  env88 Olympics Int.    cyclic A=.3362  B=.5164   (paper claims .165, n=38)
None reproduce the paper's values or the paper's n. The traceable
exp7_dynamics.csv (match-log pools) instead gives .672/.849/.645 -- also not
the paper's numbers. See ../AUDIT.md.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def hodge_fractions(A):
    """Return (transitive_frac, cyclic_frac) for skew-symmetric A."""
    A = (A - A.T) / 2.0
    p = A.mean(axis=1)
    A_T = p[:, None] - p[None, :]
    A_C = A - A_T
    norm_A = np.sum(A ** 2)
    if norm_A == 0:
        return 0.0, 0.0
    return float(np.sum(A_T ** 2) / norm_A), float(np.sum(A_C ** 2) / norm_A)


def load_matrix(path):
    with open(path) as f:
        d = json.load(f)
    W = np.array(d["win_rate_matrix"], dtype=float)
    np.fill_diagonal(W, np.nan)
    n = W.shape[0]
    users = d.get("users", [])
    assert len(set(users)) == n, "matrix users are not unique"
    return W, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True,
                    help="directory containing raw_evaluation/env*_matrix.json")
    args = ap.parse_args()
    base = Path(args.data_dir) / "raw_evaluation"

    print(f"{'env':>5} {'n':>4} {'A: trans':>9} {'A: cyclic':>9} "
          f"{'B: trans':>9} {'B: cyclic':>9}")
    for env, name in [(6, "Snake 3v3"), (34, "GRF 11v11"), (88, "Olympics Int.")]:
        f = base / f"env{env}_matrix.json"
        if not f.exists():
            print(f"env{env}: missing {f}")
            continue
        W, n = load_matrix(f)

        # A: win-rate payoff, unplayed -> draw (0.5)
        W_a = np.where(np.isnan(W), 0.5, W)
        A_a = 2 * W_a - 1
        np.fill_diagonal(A_a, 0.0)
        ta, ca = hodge_fractions(A_a)

        # B: majority vote +-1, unplayed -> 0 (paper's stated definition)
        A_b = np.where(np.isnan(W), 0.0, np.sign(W - 0.5))
        np.fill_diagonal(A_b, 0.0)
        tb, cb = hodge_fractions(A_b)

        print(f"env{env:<3} {n:>4} {ta:>9.4f} {ca:>9.4f} {tb:>9.4f} {cb:>9.4f}   {name}")


if __name__ == "__main__":
    main()
