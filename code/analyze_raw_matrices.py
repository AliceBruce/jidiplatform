#!/usr/bin/env python3
"""
Deep analysis of raw payoff matrices:
1. Ranking method robustness (avg winrate vs Elo vs alpha-Rank)
2. Strategy lineage / clustering
3. Non-transitive cycle detection
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import itertools

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / 'data' / 'tau'
OUT = REPO_ROOT / 'output'
OUT.mkdir(exist_ok=True)

ENVS = {
    6: 'Snake 3v3',
    34: 'GRF 11v11',
    88: 'Olympics',
}

def load_matrix(env_id):
    with open(BASE / f'env{env_id}.json') as f:
        d = json.load(f)
    users = d['user_ids']
    W = np.array(d['win_rate_matrix'], dtype=float)
    # Replace NaN/inf with 0.5
    W = np.nan_to_num(W, nan=0.5, posinf=1.0, neginf=0.0)
    # Symmetrize: W[i,j] = win rate of i against j
    # If matrix has both directions, average; if only one direction, use 1-W[j,i]
    n = len(users)
    for i in range(n):
        for j in range(n):
            if i == j:
                W[i,j] = 0.5
            elif W[i,j] == 0 and W[j,i] > 0:
                W[i,j] = 1.0 - W[j,i]
            elif W[j,i] == 0 and W[i,j] > 0:
                W[j,i] = 1.0 - W[i,j]
    return users, W

def rank_avg_winrate(W):
    """Average win rate against all opponents."""
    n = W.shape[0]
    scores = np.array([np.mean([W[i,j] for j in range(n) if j != i]) for i in range(n)])
    return stats.rankdata(-scores)  # higher score = better = lower rank number

def rank_elo(W, k=32, iterations=1000):
    """Simple Elo from payoff matrix."""
    n = W.shape[0]
    elo = np.ones(n) * 1000.0
    for _ in range(iterations):
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                expected = 1.0 / (1.0 + 10.0 ** ((elo[j] - elo[i]) / 400.0))
                actual = W[i,j]
                elo[i] += k * (actual - expected)
    return stats.rankdata(-elo)

def rank_alpha_rank(W, alpha=0.1, iterations=10000):
    """
    Simplified alpha-Rank: evolutionary dynamics on payoff matrix.
    Uses the response graph / Markov chain approach.
    """
    n = W.shape[0]
    # Payoff matrix for row player
    # Compute fixation probabilities via simplified evolutionary process
    # Use the "response graph" approach: from state i, transition to j if j has higher payoff against i
    rho = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # Payoff of j against i's population
            # Simplified: if W[j,i] > 0.5, j can invade i
            rho[i,j] = max(0, W[j,i] - 0.5)
    # Normalize rows to form transition matrix
    row_sums = rho.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    P = rho / row_sums
    # Stationary distribution
    # Power iteration
    pi = np.ones(n) / n
    for _ in range(iterations):
        pi = pi @ P
        pi = pi / pi.sum()
    return stats.rankdata(-pi)

def compute_tau(W):
    """Non-transitivity index: fraction of triples that are non-transitive."""
    n = W.shape[0]
    if n < 3:
        return 0.0, 0
    total = 0
    cyclic = 0
    for i, j, k in itertools.combinations(range(n), 3):
        # Determine pairwise winners
        ij = W[i,j] > 0.5  # i beats j
        jk = W[j,k] > 0.5  # j beats k
        ki = W[k,i] > 0.5  # k beats i
        ji = W[j,i] > 0.5
        kj = W[k,j] > 0.5
        ik = W[i,k] > 0.5
        # Check for cycles: i>j>k>i or i>k>j>i
        if (ij and jk and ki) or (ik and kj and ji):
            cyclic += 1
        total += 1
    return cyclic / total if total > 0 else 0.0, total

def find_cycles(W, max_len=4):
    """Find explicit non-transitive cycles."""
    n = W.shape[0]
    cycles = []
    for length in range(3, max_len + 1):
        for combo in itertools.combinations(range(n), length):
            # Check all permutations for a directed cycle
            for perm in itertools.permutations(combo):
                is_cycle = True
                for idx in range(length):
                    a = perm[idx]
                    b = perm[(idx + 1) % length]
                    if W[a,b] <= 0.5:  # a doesn't beat b
                        is_cycle = False
                        break
                if is_cycle:
                    cycles.append(perm)
                    break  # one cycle per combo is enough
    return cycles

def strategy_clustering(W, n_clusters=3):
    """Hierarchical clustering of strategies based on win-rate profile similarity."""
    n = W.shape[0]
    # Distance = 1 - correlation of win-rate profiles
    corr = np.corrcoef(W)
    corr = np.nan_to_num(corr, nan=0.0)
    dist = 1 - corr
    np.fill_diagonal(dist, 0)
    dist = (dist + dist.T) / 2  # ensure symmetric
    condensed = squareform(dist, checks=False)
    Z = linkage(condensed, method='average')
    labels = fcluster(Z, n_clusters, criterion='maxclust')
    return labels, Z

def main():
    results = {}
    
    for env_id, env_name in ENVS.items():
        print(f"\n{'='*60}")
        print(f"Environment: {env_name} (id={env_id})")
        print(f"{'='*60}")
        
        users, W = load_matrix(env_id)
        n = len(users)
        print(f"Number of strategies: {n}")
        print(f"Matrix shape: {W.shape}")
        
        # 1. Non-transitivity
        tau, n_triples = compute_tau(W)
        print(f"\nNon-transitivity tau: {tau:.4f} ({n_triples} triples)")
        
        # 2. Ranking methods
        r_avg = rank_avg_winrate(W)
        r_elo = rank_elo(W)
        r_alpha = rank_alpha_rank(W)
        
        # Spearman correlations between rankings
        rho_avg_elo, _ = stats.spearmanr(r_avg, r_elo)
        rho_avg_alpha, _ = stats.spearmanr(r_avg, r_alpha)
        rho_elo_alpha, _ = stats.spearmanr(r_elo, r_alpha)
        
        print(f"\nRanking method agreement (Spearman rho):")
        print(f"  Avg winrate vs Elo:      {rho_avg_elo:.4f}")
        print(f"  Avg winrate vs alpha-Rank: {rho_avg_alpha:.4f}")
        print(f"  Elo vs alpha-Rank:       {rho_elo_alpha:.4f}")
        
        # Top-10 overlap
        top10_avg = set(np.argsort(r_avg)[:10])
        top10_elo = set(np.argsort(r_elo)[:10])
        top10_alpha = set(np.argsort(r_alpha)[:10])
        print(f"\nTop-10 overlap:")
        print(f"  Avg vs Elo:      {len(top10_avg & top10_elo)}/10")
        print(f"  Avg vs alpha:    {len(top10_avg & top10_alpha)}/10")
        print(f"  Elo vs alpha:    {len(top10_elo & top10_alpha)}/10")
        
        # 3. Strategy clustering
        labels, Z = strategy_clustering(W, n_clusters=3)
        cluster_sizes = [np.sum(labels == c) for c in range(1, 4)]
        print(f"\nStrategy clusters (k=3): sizes = {cluster_sizes}")
        
        # Average win rate between clusters
        for c1 in range(1, 4):
            for c2 in range(c1+1, 4):
                idx1 = np.where(labels == c1)[0]
                idx2 = np.where(labels == c2)[0]
                if len(idx1) > 0 and len(idx2) > 0:
                    cross_wr = np.mean([W[i,j] for i in idx1 for j in idx2])
                    print(f"  Cluster {c1} vs {c2}: avg WR of c1 over c2 = {cross_wr:.3f}")
        
        # 4. Find cycles (sample for large n)
        if n <= 30:
            cycles = find_cycles(W, max_len=3)
            print(f"\n3-cycles found: {len(cycles)}")
            if cycles:
                # Show a few
                for c in cycles[:3]:
                    names = [users[i][:8] for i in c]
                    print(f"  {' -> '.join(names)} -> {names[0]}")
        else:
            # Sample random triples
            np.random.seed(42)
            n_sample = 5000
            cyclic_count = 0
            for _ in range(n_sample):
                triple = np.random.choice(n, 3, replace=False)
                i, j, k = triple
                ij = W[i,j] > 0.5
                jk = W[j,k] > 0.5
                ki = W[k,i] > 0.5
                ji = W[j,i] > 0.5
                kj = W[k,j] > 0.5
                ik = W[i,k] > 0.5
                if (ij and jk and ki) or (ik and kj and ji):
                    cyclic_count += 1
            print(f"\nSampled 3-cycles: {cyclic_count}/{n_sample} = {cyclic_count/n_sample:.4f}")
        
        results[env_name] = {
            'n_strategies': n,
            'tau': tau,
            'rho_avg_elo': rho_avg_elo,
            'rho_avg_alpha': rho_avg_alpha,
            'rho_elo_alpha': rho_elo_alpha,
            'top10_avg_elo': len(top10_avg & top10_elo),
            'top10_avg_alpha': len(top10_avg & top10_alpha),
            'top10_elo_alpha': len(top10_elo & top10_alpha),
            'cluster_sizes': cluster_sizes,
        }
    
    # Save results
    with open(OUT / 'ranking_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, r in results.items():
        print(f"\n{name}:")
        print(f"  n={r['n_strategies']}, tau={r['tau']:.4f}")
        print(f"  Ranking agreement: avg-elo={r['rho_avg_elo']:.3f}, avg-alpha={r['rho_avg_alpha']:.3f}, elo-alpha={r['rho_elo_alpha']:.3f}")
        print(f"  Top-10 overlap: avg-elo={r['top10_avg_elo']}, avg-alpha={r['top10_avg_alpha']}, elo-alpha={r['top10_elo_alpha']}")

if __name__ == '__main__':
    main()
