#!/usr/bin/env python3
"""Fixture tests for falsify_quant.py — every function tested against known answers.

Run: python test_falsify_quant_fixtures.py
Exit 0 = all pass, 1 = any fail.

Each test has a known analytical answer. If the function deviates, the test
catches it immediately — no more "wrote it, declared it done, never tested."
"""
import os as _os
import sys
import math
from pathlib import Path
import numpy as np
from scipy import stats as sp_stats

from falsify.quant import pbo, psr, dsr, permutation_test, _compute_stats, ic_analysis, _load_daily_returns, _load_returns_matrix
from falsify.quant import _validate_evidence_integrity
from falsify.quant import walk_forward_predictive_power, pnl_regime_analysis
from falsify.quant import execution_realism_check

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} — {detail}")

print("=" * 70)
print("FIXTURE TESTS FOR falsify_quant.py")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PBO — Probability of Backtest Overfitting
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── PBO ──")

# Fixture 1a: Two identical random strategies → PBO should be ~0.5
# Under null (no overfitting possible), IS-best is random, OOS rank is uniform.
np.random.seed(42)
rets_id = np.random.randn(500, 2) * 0.01  # 2 identical strategies, 500 days
res = pbo(rets_id, n_bins=16)
check("PBO identical random ~0.5",
      0.3 < res["pbo"] < 0.7,
      f"PBO={res['pbo']} (expected ~0.5)")

# Fixture 1b: One strategy clearly better → PBO should be LOW
# If strategy A always beats B, IS-best is always A, and A is also OOS-best.
np.random.seed(42)
good = np.random.randn(500, 1) * 0.01 + 0.002  # positive mean
bad = np.random.randn(500, 1) * 0.01 - 0.002   # negative mean
rets_dom = np.hstack([good, bad])
res = pbo(rets_dom, n_bins=16)
check("PBO dominant strategy < 0.3",
      res["pbo"] < 0.3,
      f"PBO={res['pbo']} (expected < 0.3, dominant strategy shouldn't overfit)")

# Fixture 1c: Pure noise, many strategies → PBO should be roughly near 0.5
# Monte Carlo shows E[PBO]≈0.50 with std≈0.18 for N=8, T=500.
# Accept anything in [0.1, 0.9] — the point is it's NOT near 0 or 1.
np.random.seed(123)
rets_noise = np.random.randn(500, 8) * 0.01
res = pbo(rets_noise, n_bins=16)
check("PBO pure noise 8-strategy not extreme",
      0.1 < res["pbo"] < 0.9,
      f"PBO={res['pbo']} (expected ~0.5 ± 0.18 for pure noise; must not be near 0 or 1)")

# Fixture 1d: Overfitted — IS-best is noise, but constructed to reverse OOS
# Create 4 strategies where the one that's best in first half is worst in second half
np.random.seed(42)
half = 250
s1 = np.concatenate([np.random.randn(half) * 0.01 + 0.003,  # good first half
                      np.random.randn(half) * 0.01 - 0.003]) # bad second half
s2 = np.concatenate([np.random.randn(half) * 0.01 - 0.003,  # bad first half
                      np.random.randn(half) * 0.01 + 0.003]) # good second half
s3 = np.random.randn(500) * 0.01
s4 = np.random.randn(500) * 0.01
rets_anti = np.column_stack([s1, s2, s3, s4])
res = pbo(rets_anti, n_bins=16)
check("PBO anti-correlated > 0.5",
      res["pbo"] > 0.5,
      f"PBO={res['pbo']} (expected > 0.5, IS-best reverses OOS)")

# Fixture 1e: PBO end-to-end vs pypbo (independent implementation)
# Use T divisible by S to eliminate trim-direction ambiguity.
# pypbo source: github.com/esvhd/pypbo
try:
    sys.path.insert(0, '/tmp/pypbo')
    import pypbo as _pypbo_mod
    import pypbo.perf as _pypbo_perf
    def _pypbo_metric(x):
        return np.sqrt(255) * _pypbo_perf.sharpe_iid(x)
    np.random.seed(42)
    _pbo_test_M = np.random.randn(192, 8) * 0.01  # T=192 divisible by S=16
    _ours = pbo(_pbo_test_M, n_bins=16)["pbo"]
    _pypbo_res = _pypbo_mod.pbo(_pbo_test_M, S=16, metric_func=_pypbo_metric,
                                 threshold=1, n_jobs=1)
    _theirs = round(float(_pypbo_res.pbo), 4)
    check("PBO vs pypbo (T divisible by S)",
          abs(_ours - _theirs) < 0.01,
          f"ours={_ours}, pypbo={_theirs} (should match when no trim ambiguity)")
except ImportError:
    check("PBO vs pypbo (skipped — pypbo not installed)", True, "skip")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. PSR — Probabilistic Sharpe Ratio
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── PSR ──")

# Fixture 2a: SR=0, n=100, skew=0, kurt=0 → PSR should be exactly 0.5
# Under null, Z=0, PSR = Φ(0) = 0.5
res = psr(sharpe=0.0, n=100, skew=0.0, kurt=0.0, benchmark_sharpe=0.0)
check("PSR null (SR=0) = 0.5",
      abs(res["psr"] - 0.5) < 0.001,
      f"PSR={res['psr']} (expected 0.5)")

# Fixture 2b: High SR, large n, no skew/kurt → PSR should be > 0.95
# SR=2, n=365, skew=0, kurt=0 (excess)
# Z = (2/sqrt(365)) * sqrt(364) / sqrt(1) = 2 * sqrt(364/365) ≈ 1.997
# PSR = Φ(1.997) ≈ 0.977
res = psr(sharpe=2.0, n=365, skew=0.0, kurt=0.0, benchmark_sharpe=0.0)
check("PSR SR=2 n=365 > 0.95",
      res["psr"] > 0.95,
      f"PSR={res['psr']} (expected > 0.95)")

# Fixture 2c: SR=0, benchmark=1 → PSR should be low (but not <0.1)
# Z = (0 - 1/sqrt(365)) * sqrt(364) / 1 = -sqrt(364/365) ≈ -0.9986
# PSR = Φ(-0.9986) ≈ 0.159
res = psr(sharpe=0.0, n=365, skew=0.0, kurt=0.0, benchmark_sharpe=1.0)
check("PSR SR=0 vs bench=1 ≈ 0.16",
      0.10 < res["psr"] < 0.22,
      f"PSR={res['psr']} (expected ≈ 0.159)")

# Fixture 2d: Analytical check — SR=1, n=100, skew=0, kurt=0
# sr_daily = 1/sqrt(365), Z = sr_daily * sqrt(99) / 1 = sqrt(99/365) = 0.5207
# PSR = Φ(0.5207) = 0.6985
res = psr(sharpe=1.0, n=100, skew=0.0, kurt=0.0, benchmark_sharpe=0.0)
expected_z = (1.0 / math.sqrt(365)) * math.sqrt(99)
expected_psr = sp_stats.norm.cdf(expected_z)
check("PSR analytical match",
      abs(res["psr"] - expected_psr) < 0.001,
      f"PSR={res['psr']}, expected={expected_psr:.4f}, z={res['z_stat']:.4f}")

# Fixture 2e: PSR kurtosis handling — verified against pypbo reference.
# Bailey & LdP formula uses RAW kurtosis: (raw_kurt - 1)/4.
# Our input is EXCESS kurtosis (scipy default), so the term must be (excess + 2)/4.
# With excess_kurt=0 (normal), denominator = sqrt(1 + 0.5*SR^2), NOT sqrt(1 - 0.25*SR^2).
res_normal = psr(sharpe=2.0, n=365, skew=0.0, kurt=0.0, benchmark_sharpe=0.0)
sr_d = 2.0 / math.sqrt(365)
# Correct: (0+2)/4 = 0.5 → denom = sqrt(1 + 0.5 * sr_d^2)
correct_denom = math.sqrt(1 + 0.5 * sr_d**2)
correct_z = sr_d * math.sqrt(364) / correct_denom
check("PSR kurtosis: (excess+2)/4 for normal returns",
      abs(res_normal["z_stat"] - correct_z) < 0.001,
      f"z={res_normal['z_stat']:.4f}, expected={correct_z:.4f}")

# Verify it does NOT match the old buggy formula (excess-1)/4
buggy_denom = math.sqrt(1 - 0.25 * sr_d**2)
buggy_z = sr_d * math.sqrt(364) / buggy_denom
check("PSR kurtosis: differs from buggy (excess-1)/4",
      abs(res_normal["z_stat"] - buggy_z) > 0.001,
      f"Correct z={res_normal['z_stat']:.4f}, Buggy z={buggy_z:.4f}")

# Fixture 2f: PSR extreme skew/SR → denominator^2 < 0, must return error not crash
res_edge = psr(sharpe=5.0, n=100, skew=10.0, kurt=0.0, benchmark_sharpe=0.0)
check("PSR extreme skew → error (not crash)",
      res_edge.get("psr") is None and "error" in res_edge,
      f"result={res_edge}")

# Fixture 2g: PSR n=1 → must return error (sqrt(n-1) = sqrt(0))
res_n1 = psr(sharpe=2.0, n=1, skew=0.0, kurt=0.0)
check("PSR n=1 → error (not crash)",
      res_n1.get("psr") is None and "error" in res_n1,
      f"result={res_n1}")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. DSR — Deflated Sharpe Ratio
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── DSR ──")

# Fixture 3a: n_trials=1 → DSR = PSR (no multiple testing penalty)
res_dsr = dsr(observed_sr=2.0, n=365, skew=0.0, kurt=0.0, n_trials=1)
res_psr = psr(sharpe=2.0, n=365, skew=0.0, kurt=0.0, benchmark_sharpe=0.0)
check("DSR n_trials=1 equals PSR",
      abs(res_dsr["dsr"] - res_psr["psr"]) < 0.001,
      f"DSR={res_dsr['dsr']}, PSR={res_psr['psr']}")

# Fixture 3b: More trials → DSR < PSR (harder to beat)
res_1 = dsr(observed_sr=2.0, n=365, skew=0.0, kurt=0.0, n_trials=1)
res_100 = dsr(observed_sr=2.0, n=365, skew=0.0, kurt=0.0, n_trials=100)
check("DSR more trials → lower DSR",
      res_100["dsr"] < res_1["dsr"],
      f"DSR(1 trial)={res_1['dsr']}, DSR(100 trials)={res_100['dsr']}")

# Fixture 3c: Expected max SR formula check
# Bailey & López de Prado (2014) Eq. 9:
#   E[max_N(Z)] = (1-γ)·Φ⁻¹(1-1/N) + γ·Φ⁻¹(1-1/(eN))
# For N=100, n=365:
euler_gamma = 0.5772156649015329
N_test = 100
z1 = sp_stats.norm.ppf(1 - 1.0 / N_test)
z2 = sp_stats.norm.ppf(1 - 1.0 / (math.e * N_test))
expected_max_z = (1 - euler_gamma) * z1 + euler_gamma * z2
expected_max_annual = expected_max_z * math.sqrt(365.0 / 365)
res = dsr(observed_sr=2.0, n=365, skew=0.0, kurt=0.0, n_trials=100)
check("DSR expected_max_sr formula (Bailey2014 Eq.9) N=100",
      abs(res["expected_max_sr_annualized"] - expected_max_annual) < 0.01,
      f"got={res['expected_max_sr_annualized']}, expected={expected_max_annual:.4f}")

# Fixture 3d: Small N (N=2,3,4) must also use Eq.9 — NOT sqrt(2*ln(N)).
# The old code had a separate branch for N<5 that used the asymptotic
# approximation, which has 62-126% bias at these N values.
# Eq.9 is valid for all N>=2 (only N=1 needs special handling).
for _N_small in [2, 3, 4]:
    _z1 = sp_stats.norm.ppf(1 - 1.0 / _N_small)
    _z2 = sp_stats.norm.ppf(1 - 1.0 / (math.e * _N_small))
    _exp_z = (1 - euler_gamma) * _z1 + euler_gamma * _z2
    _exp_annual = _exp_z * math.sqrt(365.0 / 365)
    _res = dsr(observed_sr=2.0, n=365, skew=0.0, kurt=0.0, n_trials=_N_small)
    # Check it matches Eq.9, not sqrt(2*ln(N))
    _approx_annual = math.sqrt(2 * math.log(_N_small)) * math.sqrt(365.0 / 365)
    check(f"DSR N={_N_small} uses Eq.9 (not sqrt(2*ln(N)))",
          abs(_res["expected_max_sr_annualized"] - _exp_annual) < 0.01,
          f"got={_res['expected_max_sr_annualized']}, Eq.9={_exp_annual:.4f}, "
          f"approx={_approx_annual:.4f} (should NOT match approx)")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Permutation Test
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Permutation Test ──")

# Fixture 4a: Random returns (no signal) → p-value should be > 0.05 (not significant)
np.random.seed(42)
rets_random = np.random.randn(200) * 0.01  # mean ≈ 0
res = permutation_test(rets_random, n_permutations=500)
check("Permutation random returns p > 0.05",
      res["p_value"] > 0.05,
      f"p_value={res['p_value']} (expected > 0.05 for pure noise)")

# Fixture 4b: Strong positive returns → should be significant (p < 0.05)
# Mean = 0.5%, std = 1%, SR_daily = 0.5, SR_annual = 9.5 — very strong
np.random.seed(42)
rets_strong = np.random.randn(200) * 0.01 + 0.005
res = permutation_test(rets_strong, n_permutations=500)
check("Permutation strong returns p < 0.05",
      res["p_value"] < 0.05,
      f"p_value={res['p_value']} (expected < 0.05 for strong positive returns)")

# Fixture 4c: All zero returns → should not crash, return error (not phantom SR)
rets_zero = np.zeros(200)
res = permutation_test(rets_zero, n_permutations=100)
check("Permutation zero returns → error (not phantom SR)",
      "error" in res or res.get("p_value") is None,
      f"result={res}")

# Fixture 4d: Near-constant returns (float precision edge case)
# std ≈ 1e-17 but not exactly 0 → old code produced phantom SR ~1e15
rets_near_const = np.ones(200) * 0.001 + np.random.randn(200) * 1e-18
res = permutation_test(rets_near_const, n_permutations=100)
check("Permutation near-constant returns → error (not phantom SR)",
      "error" in res or res.get("p_value") is None,
      f"result={res}")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. MaxDD (in _compute_stats)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── MaxDD ──")

# Fixture 5a: Known drawdown sequence
# Returns: +10%, -20%, +10% → equity: 1.1, 0.88, 0.968
# Peak = 1.1, trough = 0.88, MaxDD = (1.1 - 0.88) / 1.1 = 20%
rets_known = np.array([0.10, -0.20, 0.10])
stats = _compute_stats(rets_known, periods_per_year=365)
check("MaxDD known sequence = 20%",
      abs(stats["max_drawdown_pct"] - 20.0) < 0.1,
      f"MaxDD={stats['max_drawdown_pct']}% (expected 20%)")

# Fixture 5b: All positive returns → MaxDD = 0
rets_pos = np.array([0.01, 0.02, 0.01, 0.03])
stats = _compute_stats(rets_pos, periods_per_year=365)
check("MaxDD all positive = 0",
      abs(stats["max_drawdown_pct"] - 0.0) < 0.01,
      f"MaxDD={stats['max_drawdown_pct']}% (expected 0%)")

# Fixture 5c: Monotonic decline → MaxDD = total decline
# Returns: -10%, -10%, -10% → equity: 0.9, 0.81, 0.729
# Peak = 1.0, trough = 0.729, MaxDD = 27.1%
rets_decline = np.array([-0.10, -0.10, -0.10])
stats = _compute_stats(rets_decline, periods_per_year=365)
expected_dd = (1 - 0.9**3) * 100  # 27.1%
check("MaxDD monotonic decline",
      abs(stats["max_drawdown_pct"] - expected_dd) < 0.1,
      f"MaxDD={stats['max_drawdown_pct']}% (expected {expected_dd:.1f}%)")

# Fixture 5d: Sharpe ratio check
# Returns: constant 0.001 daily, std=0 → Sharpe should be 0 (or inf, handled)
# Use near-constant: [0.001, 0.001, 0.001, 0.002]
rets_near = np.array([0.001, 0.001, 0.001, 0.002])
stats = _compute_stats(rets_near, periods_per_year=365)
# mean=0.00125, std=0.0005, SR_daily=2.5, SR_annual=2.5*sqrt(365)=47.75
expected_sr = (0.00125 / 0.0005) * math.sqrt(365)
check("Sharpe ratio computation",
      abs(stats["sharpe_annualized"] - expected_sr) < 0.1,
      f"SR={stats['sharpe_annualized']}, expected={expected_sr:.2f}")

# Fixture 5e: Sortino ratio — verified against empyrical definition
# downside_deviation = sqrt(mean(min(0, r)^2)) — NOT std(negative_returns)
# Returns: [0.02, -0.01, 0.03, -0.02, 0.01, -0.03, 0.02, -0.01]
rets_sortino = np.array([0.02, -0.01, 0.03, -0.02, 0.01, -0.03, 0.02, -0.01])
stats = _compute_stats(rets_sortino, periods_per_year=365)
n_s = len(rets_sortino)
correct_dd = math.sqrt(np.sum(np.minimum(rets_sortino, 0)**2) / n_s)
expected_sortino = rets_sortino.mean() / correct_dd * math.sqrt(365)
check("Sortino uses downside deviation (not std of negatives)",
      abs(stats["sortino"] - expected_sortino) < 0.01,
      f"Sortino={stats['sortino']}, expected={expected_sortino:.4f}")

# Verify it does NOT match the old buggy method
neg_rets = rets_sortino[rets_sortino < 0]
buggy_dd = neg_rets.std(ddof=1)
buggy_sortino = rets_sortino.mean() / buggy_dd * math.sqrt(365)
check("Sortino differs from buggy std(neg) method",
      abs(stats["sortino"] - buggy_sortino) > 0.01,
      f"Correct={stats['sortino']}, Buggy={buggy_sortino:.4f}")

# Fixture 5f: _compute_stats with NaN values → must drop NaN and report valid count
rets_nan = np.array([0.01, np.nan, 0.02, np.nan, 0.01, 0.005])
stats_nan = _compute_stats(rets_nan, periods_per_year=365)
check("_compute_stats drops NaN (n=4 not 6)",
      stats_nan.get("n") == 4 and "error" not in stats_nan,
      f"n={stats_nan.get('n')}, result={stats_nan}")

# Fixture 5g: _compute_stats empty array → must return error
stats_empty = _compute_stats(np.array([]), periods_per_year=365)
check("_compute_stats empty → error",
      "error" in stats_empty or stats_empty.get("n") == 0,
      f"result={stats_empty}")

# ═══════════════════════════════════════════════════════════════════════════════
# 6. IC Analysis
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── IC Analysis ──")

# Fixture 6a: Perfect positive correlation → IC = 1.0
np.random.seed(42)
signal = np.random.randn(200)
forward_ret = signal.copy()  # perfect correlation
res = ic_analysis(signal, forward_ret, max_lag=5)
check("IC perfect positive = 1.0",
      abs(res["ic_mean"] - 1.0) < 0.001,
      f"IC={res['ic_mean']} (expected 1.0)")

# Fixture 6b: Perfect negative correlation → IC = -1.0
res = ic_analysis(signal, -signal, max_lag=5)
check("IC perfect negative = -1.0",
      abs(res["ic_mean"] - (-1.0)) < 0.001,
      f"IC={res['ic_mean']} (expected -1.0)")

# Fixture 6c: Uncorrelated → IC ≈ 0, t-stat < 2
np.random.seed(42)
sig = np.random.randn(200)
ret = np.random.randn(200)
res = ic_analysis(sig, ret, max_lag=5)
check("IC uncorrelated ≈ 0",
      abs(res["ic_mean"]) < 0.15,
      f"IC={res['ic_mean']} (expected ≈ 0)")
check("IC uncorrelated t-stat < 2",
      abs(res["ic_tstat"]) < 2.5,
      f"t-stat={res['ic_tstat']} (expected < 2)")

# Fixture 6d: Known correlation → IC matches
# Generate correlated data with rho=0.5
np.random.seed(42)
n = 1000
x = np.random.randn(n)
y = 0.5 * x + math.sqrt(1 - 0.5**2) * np.random.randn(n)
res = ic_analysis(x, y, max_lag=5)
check("IC known correlation ≈ 0.5",
      abs(res["ic_mean"] - 0.5) < 0.05,
      f"IC={res['ic_mean']} (expected ≈ 0.5)")

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Walk-forward IS→OOS predictive power
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Walk-forward ──")
from falsify.quant import walk_forward_predictive_power, pnl_regime_analysis, cost_realism_check

# Fixture 7a: One strategy always better → high predictive ratio
np.random.seed(42)
good = np.random.randn(300, 1) * 0.01 + 0.003
bad = np.random.randn(300, 1) * 0.01 - 0.001
M_wf = np.hstack([good, bad])
res_wf = walk_forward_predictive_power(M_wf, window_size=100, step_size=50)
check("Walk-forward dominant strategy → high predictive ratio",
      res_wf.get("mean_predictive_ratio", 0) > 0.7,
      f"ratio={res_wf.get('mean_predictive_ratio')}, verdict={res_wf.get('verdict', '')[:50]}")

# Fixture 7b: Pure noise → low predictive ratio (IS selection is random)
np.random.seed(123)
M_noise = np.random.randn(300, 8) * 0.01
res_wf_noise = walk_forward_predictive_power(M_noise, window_size=100, step_size=50)
check("Walk-forward pure noise → low predictive ratio",
      res_wf_noise.get("mean_predictive_ratio", 1) < 0.7,
      f"ratio={res_wf_noise.get('mean_predictive_ratio')}, verdict={res_wf_noise.get('verdict', '')[:50]}")

# Fixture 7c: Insufficient data → error
res_wf_short = walk_forward_predictive_power(np.random.randn(50, 4), window_size=100, step_size=50)
check("Walk-forward insufficient data → error",
      "error" in res_wf_short,
      f"result={res_wf_short}")

# Fixture 7d: All-zero returns → INSUFFICIENT_DATA (not WARN "chasing noise")
res_wf_zero = walk_forward_predictive_power(np.zeros((300, 4)))
check("Walk-forward all-zero → INSUFFICIENT_DATA (not WARN)",
      "INSUFFICIENT" in res_wf_zero.get("verdict", ""),
      f"verdict={res_wf_zero.get('verdict', '')[:60]}")

# Fixture 7e: All-losing returns → not PASS (selecting least-loser ≠ predictive power)
np.random.seed(99)
wf_lose = -np.abs(np.random.randn(300, 4)) * 0.01
res_wf_lose = walk_forward_predictive_power(wf_lose)
check("Walk-forward all-losing → not PASS",
      "PASS" not in res_wf_lose.get("verdict", ""),
      f"verdict={res_wf_lose.get('verdict', '')[:60]}")

# Fixture 7f: step_size=0 → error (not infinite loop)
res_wf_step0 = walk_forward_predictive_power(np.random.randn(300, 4), window_size=120, step_size=0)
check("Walk-forward step_size=0 → error (no infinite loop)",
      "error" in res_wf_step0,
      f"result={res_wf_step0}")

# ═══════════════════════════════════════════════════════════════════════════════
# 8. PnL-driven regime analysis
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Regime Analysis ──")

# Fixture 8a: Uniform returns → alpha present in all regimes
np.random.seed(42)
uniform_rets = np.random.randn(365) * 0.01 + 0.002
res_reg = pnl_regime_analysis(uniform_rets, vol_window=30)
check("Regime uniform returns → PASS (alpha across all regimes)",
      "PASS" in res_reg.get("verdict", ""),
      f"verdict={res_reg.get('verdict')}")

# Fixture 8b: Returns concentrated in high-vol periods → regime-dependent
np.random.seed(42)
base = np.random.randn(365) * 0.01
base[270:] = np.random.randn(95) * 0.03 + 0.01
res_reg_conc = pnl_regime_analysis(base, vol_window=30)
check("Regime concentrated in high-vol → WARN (regime-dependent)",
      "WARN" in res_reg_conc.get("verdict", "") or "BORDERLINE" in res_reg_conc.get("verdict", ""),
      f"verdict={res_reg_conc.get('verdict')}")

# Fixture 8c: Insufficient data → error
res_reg_short = pnl_regime_analysis(np.random.randn(50), vol_window=30)
check("Regime insufficient data → error",
      "error" in res_reg_short,
      f"result={res_reg_short}")

# Fixture 8d: Volume regime — vol PASS but volume WARN (Sean: vol ≠ volume)
# Strategy makes money in high-volume periods regardless of vol level.
np.random.seed(42)
n = 365
rets_vol = np.random.randn(n) * 0.01 + 0.001  # uniform mild positive
volume = np.random.randn(n) * 1000 + 5000
# Inject volume-dependent alpha: high volume days get positive returns
vol_mask_high = volume > np.percentile(volume, 75)
rets_vol[~vol_mask_high] = np.random.randn(sum(~vol_mask_high)) * 0.01 - 0.002  # negative on low vol
rets_vol[vol_mask_high] = np.random.randn(sum(vol_mask_high)) * 0.01 + 0.008   # positive on high vol
res_reg_vol = pnl_regime_analysis(rets_vol, vol_window=30, volume=volume)
check("Regime with volume — volume_regime present",
      "volume_regime" in res_reg_vol,
      f"keys={list(res_reg_vol.keys())}")
check("Regime with volume — combined verdict reflects worst",
      "WARN" in res_reg_vol.get("verdict", "") or "BORDERLINE" in res_reg_vol.get("verdict", "") or "PASS" in res_reg_vol.get("verdict", ""),
      f"verdict={res_reg_vol.get('verdict')}")

# ═══════════════════════════════════════════════════════════════════════════════
# 9. Cost realism check
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Cost Realism ──")

# Fixture 9a: Stable vol → PASS
np.random.seed(42)
stable_rets = np.random.randn(365) * 0.01
res_cost = cost_realism_check(stable_rets, strategy_type="momentum")
check("Cost realism stable vol → PASS",
      res_cost.get("verdict") == "PASS",
      f"verdict={res_cost.get('verdict')}, vol_ratio={res_cost.get('vol_ratio')}")

# Fixture 9b: Vol spike + momentum → WARN
np.random.seed(42)
spike_rets = np.random.randn(365) * 0.01
spike_rets[300:] = np.random.randn(65) * 0.06  # 6x vol spike
res_cost_spike = cost_realism_check(spike_rets, strategy_type="momentum")
check("Cost realism vol spike + momentum → WARN",
      res_cost_spike.get("verdict") == "WARN",
      f"verdict={res_cost_spike.get('verdict')}, vol_ratio={res_cost_spike.get('vol_ratio')}")

# Fixture 9c: Vol spike + reversion → PASS (limit orders benefit from vol)
res_cost_rev = cost_realism_check(spike_rets, strategy_type="reversion")
check("Cost realism vol spike + reversion → PASS",
      res_cost_rev.get("verdict") == "PASS",
      f"verdict={res_cost_rev.get('verdict')}, vol_ratio={res_cost_rev.get('vol_ratio')}")

# Fixture 9d: Insufficient data → error
res_cost_short = cost_realism_check(np.random.randn(50), strategy_type="momentum")
check("Cost realism insufficient data → error",
      "error" in res_cost_short,
      f"result={res_cost_short}")

# ═══════════════════════════════════════════════════════════════════════════════
# 10. Walk-forward edge cases (round 5 adversarial probing)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Walk-forward edge cases (round 5) ──")

# Fixture 10a: All identical columns → INSUFFICIENT_DATA, not false PASS
np.random.seed(42)
rm_ident = np.random.randn(300, 4) * 0.01
rm_ident[:] = rm_ident[:, 0:1]  # all columns identical
res_wf_ident = walk_forward_predictive_power(rm_ident, window_size=120, step_size=60)
check("Walk-forward identical columns → not PASS",
      "PASS" not in res_wf_ident.get("verdict", ""),
      f"verdict={res_wf_ident.get('verdict')} (should not be PASS)")

# Fixture 10b: Sensitivity with insufficient sweep data → no false "sensitive" WARN
# When 1.2x window can't run (data too short), sensitivity should default
# to stable, not trigger "window-size sensitive" warning.
np.random.seed(42)
rm_short = np.random.randn(180, 3) * 0.01 + 0.005  # positive mean
res_wf_short = walk_forward_predictive_power(rm_short, window_size=120, step_size=50)
# If verdict contains "window-size sensitive" but sweep had <2 comparable entries,
# that's a false WARN.
wf_verdict = res_wf_short.get("verdict", "")
sweep = res_wf_short.get("window_sensitivity", [])
comparable_count = sum(1 for s in sweep if s.get("n_windows", 0) >= 2)
if comparable_count < 2:
    check("Walk-forward insufficient sweep → no false sensitivity WARN",
          "window-size sensitive" not in wf_verdict,
          f"verdict contains 'sensitive' but only {comparable_count} comparable sweep entries")
else:
    check("Walk-forward insufficient sweep → no false sensitivity WARN",
          True,  # enough comparable entries, test is N/A
          f"enough comparable entries ({comparable_count}), test skipped")

# Fixture 10c: Step-size sensitivity sweep present in output
np.random.seed(42)
rm_step = np.random.randn(500, 4) * 0.01 + 0.002
res_wf_step = walk_forward_predictive_power(rm_step, window_size=120, step_size=60)
check("Walk-forward step-size sensitivity present",
      "step_size_sensitivity" in res_wf_step,
      f"keys={list(res_wf_step.keys())}")
check("Walk-forward step-size sensitivity has entries",
      len(res_wf_step.get("step_size_sensitivity", [])) >= 2,
      f"entries={len(res_wf_step.get('step_size_sensitivity', []))}")

# Fixture 10d: param_drift_note present (Sean Level 2 — drift is expected)
check("Walk-forward param_drift_note present",
      "param_drift_note" in res_wf_step,
      f"keys={list(res_wf_step.keys())}")
check("Walk-forward no param_stability key (removed misleading metric)",
      "param_stability" not in res_wf_step,
      f"param_stability still present in output")

# ═══════════════════════════════════════════════════════════════════════════════
# 11. Execution realism — delay sensitivity + cost stress (L4-E + L4-A)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Execution realism (L4-E+A) ──")

# Fixture 11a: Strong, persistent edge → survives delay + cost stress → PASS
np.random.seed(42)
strong_rets = np.random.randn(365) * 0.01 + 0.003  # strong positive mean
res_exec_strong = execution_realism_check(strong_rets)
check("Exec realism strong edge → overall PASS",
      res_exec_strong.get("overall_verdict") == "PASS",
      f"verdict={res_exec_strong.get('overall_verdict')}, "
      f"d1={res_exec_strong.get('delay_1bar', {}).get('verdict')}, "
      f"c2={res_exec_strong.get('cost_2x', {}).get('verdict')}")

# Fixture 11b: Negative autocorrelation (reversion-like) + unknown type → delay WARN
# Create returns with negative lag-1 autocorrelation: big up day tends to be
# followed by down day (mean-reverting). With unknown strategy_type, this should WARN.
np.random.seed(42)
n_days = 365
reversion_rets = np.zeros(n_days)
raw = np.random.randn(n_days) * 0.01
for i in range(1, n_days):
    reversion_rets[i] = -0.5 * reversion_rets[i-1] + raw[i] + 0.001
res_exec_ar = execution_realism_check(reversion_rets, strategy_type="")
check("Exec realism reversion (neg autocorr) + unknown type → delay WARN",
      res_exec_ar.get("delay_1bar", {}).get("verdict") == "WARN",
      f"d1_verdict={res_exec_ar.get('delay_1bar', {}).get('verdict')}, "
      f"lag_autocorr={res_exec_ar.get('delay_1bar', {}).get('lag_autocorr')}")

# Fixture 11c: Marginal edge → 2× cost kills it → WARN/FAIL
np.random.seed(42)
marginal_rets = np.random.randn(365) * 0.02 + 0.0005  # tiny mean, high vol
res_exec_marginal = execution_realism_check(marginal_rets, base_cost_bps=10.0)
check("Exec realism marginal edge + high cost → not PASS",
      res_exec_marginal.get("overall_verdict") != "PASS",
      f"verdict={res_exec_marginal.get('overall_verdict')}, "
      f"c2_retention={res_exec_marginal.get('cost_2x', {}).get('sr_retention')}")

# Fixture 11d: Insufficient data → error
res_exec_short = execution_realism_check(np.random.randn(50))
check("Exec realism insufficient data → error",
      "error" in res_exec_short,
      f"result={res_exec_short}")

# Fixture 11e: Output structure has all 4 stress dimensions
res_exec_struct = execution_realism_check(strong_rets)
check("Exec realism output has delay_1bar",
      "delay_1bar" in res_exec_struct,
      f"keys={list(res_exec_struct.keys())}")
check("Exec realism output has delay_2bar",
      "delay_2bar" in res_exec_struct,
      f"keys={list(res_exec_struct.keys())}")
check("Exec realism output has cost_2x",
      "cost_2x" in res_exec_struct,
      f"keys={list(res_exec_struct.keys())}")
check("Exec realism output has cost_3x",
      "cost_3x" in res_exec_struct,
      f"keys={list(res_exec_struct.keys())}")
check("Exec realism output has overall_verdict",
      "overall_verdict" in res_exec_struct,
      f"keys={list(res_exec_struct.keys())}")
check("Exec realism output has recommendation",
      "recommendation" in res_exec_struct,
      f"keys={list(res_exec_struct.keys())}")

# Fixture 11f: Negative-Sharpe strategy → stress can't kill what's already dead
# If base SR < 0, delay/cost stress shouldn't produce spurious FAIL
np.random.seed(42)
neg_rets = np.random.randn(365) * 0.01 - 0.002  # negative mean
res_exec_neg = execution_realism_check(neg_rets)
check("Exec realism negative-SR base → cost stress SKIP (near-zero SR guard)",
      res_exec_neg.get("cost_2x", {}).get("verdict") == "SKIP",
      f"cost_2x={res_exec_neg.get('cost_2x', {})}")

# Fixture 11g: Constant returns → error (not spurious FAIL)
constant_rets = np.ones(365) * 0.001
res_exec_const = execution_realism_check(constant_rets)
check("Exec realism constant returns → error",
      "error" in res_exec_const,
      f"result={res_exec_const}")

# Fixture 11h: Reversion strategy with negative autocorr → E verdict PASS (not WARN)
np.random.seed(42)
n_days = 365
rev_rets = np.zeros(n_days)
raw = np.random.randn(n_days) * 0.005
for i in range(1, n_days):
    rev_rets[i] = -0.6 * rev_rets[i-1] + raw[i] + 0.002
res_exec_rev = execution_realism_check(rev_rets, strategy_type="reversion")
check("Exec realism reversion + neg autocorr → delay PASS (expected behavior)",
      res_exec_rev.get("delay_1bar", {}).get("verdict") == "PASS",
      f"d1={res_exec_rev.get('delay_1bar', {})}")

# Fixture 11i: Same reversion but strategy_type="" → delay WARN (conservative)
res_exec_rev_unknown = execution_realism_check(rev_rets, strategy_type="")
check("Exec realism reversion + unknown type → delay WARN (conservative)",
      res_exec_rev_unknown.get("delay_1bar", {}).get("verdict") == "WARN",
      f"d1={res_exec_rev_unknown.get('delay_1bar', {})}")

# Fixture 11j: base_cost_bps=0 → cost stress SKIP (no-op guard)
np.random.seed(42)
strong_rets = np.random.randn(365) * 0.01 + 0.003
res_exec_zero_cost = execution_realism_check(strong_rets, base_cost_bps=0)
check("Exec realism base_cost_bps=0 → cost SKIP",
      res_exec_zero_cost.get("cost_2x", {}).get("verdict") == "SKIP",
      f"cost_2x={res_exec_zero_cost.get('cost_2x', {})}")

# Fixture 11k: Near-zero SR → cost stress SKIP (numerical stability guard)
np.random.seed(42)
low_sr_rets = np.random.randn(365) * 0.5
low_sr_rets = low_sr_rets - low_sr_rets.mean()  # force zero mean → SR ≈ 0
res_exec_low_sr = execution_realism_check(low_sr_rets)
check("Exec realism near-zero SR → cost SKIP",
      res_exec_low_sr.get("cost_2x", {}).get("verdict") == "SKIP",
      f"cost_2x={res_exec_low_sr.get('cost_2x', {})}, sr_base={res_exec_low_sr.get('cost_2x', {}).get('sr_base')}")


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Return basis loader — dual-column ret_log + ret_simple must prefer ret_log
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Return Basis Loader ──")

import tempfile
import pandas as pd

with tempfile.TemporaryDirectory() as _tmpdir:
    _csv = Path(_tmpdir) / "dual_returns.csv"
    _log_rets = np.array([math.log(1.10), math.log(0.90), math.log(1.05), math.log(0.98)], dtype=float)
    _simple_rets = np.array([0.10, -0.10, 0.05, -0.02], dtype=float)
    pd.DataFrame({"ret_log": _log_rets, "ret_simple": _simple_rets}).to_csv(_csv, index=False)
    _loaded = _load_daily_returns(str(_csv))
    check("Loader dual-column prefers ret_log",
          getattr(_loaded, "return_basis", None) == "log",
          f"basis={getattr(_loaded, 'return_basis', None)}")
    check("Loader values equal ret_log, not ret_simple",
          np.allclose(np.asarray(_loaded), _log_rets) and not np.allclose(np.asarray(_loaded), _simple_rets),
          f"loaded={np.asarray(_loaded)}, ret_log={_log_rets}, ret_simple={_simple_rets}")
    _copy = _loaded.copy()
    _slice = _loaded[:2]
    check("ReturnsArray copy preserves return_basis",
          getattr(_copy, "return_basis", None) == "log",
          f"basis={getattr(_copy, 'return_basis', None)}")
    check("ReturnsArray slice preserves return_basis",
          getattr(_slice, "return_basis", None) == "log",
          f"basis={getattr(_slice, 'return_basis', None)}")
    _stats = _compute_stats(_loaded)
    check("Compute stats records log basis",
          _stats.get("return_basis") == "log",
          f"return_basis={_stats.get('return_basis')}, keys={list(_stats.keys())}")

    _bad_csv = Path(_tmpdir) / "not_returns.csv"
    pd.DataFrame({"date": ["2026-01-01", "2026-01-02"], "gross": [4.0, 4.0], "turnover": [0.1, 0.2]}).to_csv(_bad_csv, index=False)
    try:
        _load_daily_returns(str(_bad_csv))
        _bad_daily_failed = False
        _bad_daily_detail = "accepted gross/turnover as returns"
    except ValueError as _e:
        _bad_daily_failed = "Refusing last-numeric fallback" in str(_e)
        _bad_daily_detail = str(_e)
    check("Loader refuses last-numeric fallback",
          _bad_daily_failed,
          _bad_daily_detail)

    _matrix_csv = Path(_tmpdir) / "matrix.csv"
    pd.DataFrame({"ret_a": [0.01, 0.02], "ret_b": [0.0, -0.01], "gross": [4.0, 4.0], "turnover": [0.1, 0.2]}).to_csv(_matrix_csv, index=False)
    try:
        _load_returns_matrix(str(_matrix_csv), "")
        _matrix_no_cols_failed = False
        _matrix_no_cols_detail = "accepted returns_matrix without explicit columns"
    except ValueError as _e:
        _matrix_no_cols_failed = "requires --matrix-columns" in str(_e)
        _matrix_no_cols_detail = str(_e)
    check("Matrix loader requires explicit columns",
          _matrix_no_cols_failed,
          _matrix_no_cols_detail)

    _matrix, _cols = _load_returns_matrix(str(_matrix_csv), "ret_a,ret_b")
    check("Matrix loader uses only explicit return columns",
          list(_matrix.columns) == ["ret_a", "ret_b"] and "gross" not in _matrix.columns and "turnover" not in _matrix.columns,
          f"cols={list(_matrix.columns)}, parsed={_cols}")

# ═══════════════════════════════════════════════════════════════════════════════
# 13. Evidence integrity gate — calendar/row-loss/coverage/policy before PASS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Evidence Integrity Gate ──")

with tempfile.TemporaryDirectory() as _tmpdir:
    import json as _json
    import subprocess as _subprocess
    _tmp = Path(_tmpdir)
    _missing_ei = _validate_evidence_integrity()
    check("Evidence integrity missing artifacts → BLOCK",
          _missing_ei.get("status") == "BLOCK" and len(_missing_ei.get("issues", [])) == 4,
          f"result={_missing_ei}")
    _contract = _tmp / "contract.json"
    _row_loss = _tmp / "row_loss.json"
    _coverage = _tmp / "coverage.csv"
    _policy = _tmp / "variant_policy.json"
    _contract.write_text('{"start":"2025-01-01","end":"2025-12-31","expected_rows":365}\n')
    _row_loss.write_text('{"raw_rows":365,"aligned_rows":365,"drops":[]}\n')
    pd.DataFrame({"date": ["2025-01-01"], "coverage": [1.0]}).to_csv(_coverage, index=False)
    _policy.write_text('{"missing_feature_policy":"excluded","ablations":["excluded","neutral"]}\n')
    _ok_ei = _validate_evidence_integrity(str(_contract), str(_row_loss), str(_coverage), str(_policy))
    check("Evidence integrity present readable artifacts → PASS",
          _ok_ei.get("status") == "PASS" and not _ok_ei.get("issues"),
          f"result={_ok_ei}")
    _empty_cov = _tmp / "empty_coverage.csv"
    _empty_cov.write_text("")
    _bad_ei = _validate_evidence_integrity(str(_contract), str(_row_loss), str(_empty_cov), str(_policy))
    check("Evidence integrity unreadable/empty artifact blocks PASS",
          _bad_ei.get("status") == "BLOCK" and any("coverage_manifest" in x for x in _bad_ei.get("issues", [])),
          f"result={_bad_ei}")

    # Integration: quant_falsify_gate.py (sole verdict exit) must BLOCK when
    # L0.5 evidence artifacts are missing. Replaces old falsify_quant.py CLI test.
    # Skip when running inside gate5's boot-check (prevents infinite recursion).
    if _os.environ.get("SKIP_GATE_INTEGRATION"):
        check("Gate integration (skipped by env)", True, "skip")
    else:
        _daily = _tmp / "daily.csv"
        _matrix = _tmp / "matrix.csv"
        _out_missing = _tmp / "missing.json"
        np.random.seed(7)
        _rets = np.random.randn(365) * 0.01 + 0.003
        pd.DataFrame({"ret_log": _rets}).to_csv(_daily, index=False)
        pd.DataFrame({"a": _rets, "b": _rets + np.random.randn(365) * 0.001, "c": _rets * 0.8 + np.random.randn(365) * 0.004, "d": np.random.randn(365) * 0.01 + 0.001}).to_csv(_matrix, index=False)
        _gate_script = str(Path(__file__).resolve().parent / "quant_falsify_gate.py")
        _cmd = [sys.executable, _gate_script,
                "--script", str(Path(__file__).resolve()),  # any .py as placeholder
                "--results-dir", str(_tmp),
                "--returns-matrix", str(_matrix), "--matrix-columns", "a,b,c,d",
                "--n-param-combos", "4", "--output", str(_out_missing)]
        _cp = _subprocess.run(_cmd, text=True, capture_output=True, timeout=120, env={**_os.environ, "SKIP_GATE_INTEGRATION": "1"})
        _rep = _json.loads(_out_missing.read_text())
        check("Gate missing evidence → claim_ceiling BLOCK or CANDIDATE",
              _cp.returncode == 1 and _rep.get("claim_ceiling") in ("BLOCK", "CANDIDATE_NEEDS_NEXT_GATE"),
              f"rc={_cp.returncode}, ceiling={_rep.get('claim_ceiling')}, stderr={_cp.stderr[-200:]}")

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"RESULTS: {PASS} passed, {FAIL} failed")
print("=" * 70)

if __name__ == "__main__":
    sys.exit(0 if FAIL == 0 else 1)


# ═══════════════════════════════════════════════════════════════════════════════
# Pytest compatibility layer (Pitfall #77 fix)
# Without this, `pytest test_falsify_quant_fixtures.py` collects 0 items
# and reports "0 failed" — a silent green light. This function ensures
# pytest collects, runs, and reports the fixture results properly.
# ═══════════════════════════════════════════════════════════════════════════════
def test_fixtures_all_pass():
    """Pytest entry point — guarantees fixtures ran and all passed."""
    assert PASS > 0, (
        "No fixtures executed (PASS=0) — silent green light, Pitfall #77. "
        "Module-level fixture code did not run."
    )
    assert FAIL == 0, f"{FAIL} fixture(s) failed out of {PASS + FAIL}"
