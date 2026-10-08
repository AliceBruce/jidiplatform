#!/usr/bin/env python3
"""
Verify tau definition using Hodge decomposition on raw payoff matrices.
Compare with stored tau values in exp7_dynamics.csv.
"""
import json
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / 'data'

# Stored tau values from exp7_dynamics.csv
stored_tau = {
    6: ('Snake 3v3', 0.6721722896604531),
    34: ('GRF 11v11', 0.8492804815842891),
    88: ('Olympics integrated', 0.6446047909982178),
}

def hodge_decompose(W):
    """
    Hodge decomposition of skew-symmetric payoff matrix.
    W: win-rate matrix (n x n), W[i,j] = win rate of i against j
    Returns: A (skew-symmetric payoff), A_T (transitive/potential), A_C (cyclic), tau_transitive, tau_cyclic
    """
    n = W.shape[0]
    # Payoff matrix: +1 for win, -1 for loss, 0 for draw/self
    A = 2 * W - 1
    np.fill_diagonal(A, 0)
    # Make skew-symmetric (average of A and -A.T to handle asymmetry from draws)
    A = (A - A.T) / 2
    
    # Potential/transitive component: A_T[i,j] = p_i - p_j where p_i = mean row of A
    p = A.mean(axis=1)
    A_T = p[:, None] - p[None, :]
    
    # Cyclic component
    A_C = A - A_T
    
    # Norms (Frobenius squared)
    norm_A = np.sum(A ** 2)
    norm_AT = np.sum(A_T ** 2)
    norm_AC = np.sum(A_C ** 2)
    
    tau_transitive = norm_AT / norm_A if norm_A > 0 else 0
    tau_cyclic = norm_AC / norm_A if norm_A > 0 else 0
    
    return A, A_T, A_C, tau_transitive, tau_cyclic

def cycle_triple_fraction(W):
    """Fraction of triples that are cyclic (non-transitive)."""
    n = W.shape[0]
    total = 0
    cyclic = 0
    for i in range(n):
        for j in range(i+1, n):
            for k in range(j+1, n):
                total += 1
                # Determine winner for each pair
                w_ij = W[i,j] > 0.5
                w_jk = W[j,k] > 0.5
                w_ki = W[k,i] > 0.5
                w_ji = W[j,i] > 0.5
                w_kj = W[k,j] > 0.5
                w_ik = W[i,k] > 0.5
                # Cyclic if i>j>k>i or i<j<k<i
                if (w_ij and w_jk and w_ki) or (w_ji and w_kj and w_ik):
                    cyclic += 1
    return cyclic / total if total > 0 else 0, total

print("=" * 80)
print("TAU DEFINITION VERIFICATION")
print("=" * 80)

for env_id, (name, stored) in stored_tau.items():
    f = BASE / f'raw_evaluation/env{env_id}_matrix.json'
    if not f.exists():
        print(f"\n{name}: matrix file not found")
        continue
    
    with open(f) as fh:
        data = json.load(fh)
    
    W = np.array(data['win_rate_matrix'], dtype=float)
    # Replace None/NaN with 0.5 (draw) for unplayed pairs
    W = np.where(np.isnan(W), 0.5, W)
    strategies = data.get('users', [])
    n = len(strategies)
    
    print(f"\n--- {name} (env{env_id}, n={n}) ---")
    print(f"  Stored tau (exp7): {stored:.4f}")
    
    A, A_T, A_C, tau_trans, tau_cyc = hodge_decompose(W)
    print(f"  Hodge transitive fraction (||A_T||^2/||A||^2): {tau_trans:.4f}")
    print(f"  Hodge cyclic fraction (||A_C||^2/||A||^2):     {tau_cyc:.4f}")
    print(f"  Sum check: {tau_trans + tau_cyc:.4f} (should be 1.0)")
    
    # Also compute cycle triple fraction
    cyc_frac, n_triples = cycle_triple_fraction(W)
    print(f"  Cyclic triple fraction: {cyc_frac:.4f} ({n_triples} triples)")
    
    # Compare
    print(f"\n  Comparison with stored tau={stored:.4f}:")
    print(f"    vs transitive fraction: diff={abs(stored - tau_trans):.4f}")
    print(f"    vs cyclic fraction:     diff={abs(stored - tau_cyc):.4f}")
    print(f"    vs cyclic triple frac:  diff={abs(stored - cyc_frac):.4f}")
    
    # Check if stored tau matches some other transformation
    print(f"    1 - transitive = {1-tau_trans:.4f}, diff from stored: {abs(stored - (1-tau_trans)):.4f}")
    print(f"    sqrt(cyclic) = {np.sqrt(tau_cyc):.4f}")
    print(f"    transitive^2 = {tau_trans**2:.4f}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
If stored tau ≈ transitive fraction → tau measures transitivity (high=more transitive)
  But paper calls it 'non-transitivity' and says high tau = more cyclic → INCONSISTENT

If stored tau ≈ cyclic fraction → tau measures non-transitivity (high=more cyclic)
  Paper usage is CONSISTENT

If stored tau matches neither → definition is unclear, needs collaborator clarification
""")
