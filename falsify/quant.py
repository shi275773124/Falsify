#!/usr/bin/env python3
"""falsify_quant.py — Pure statistical validation library for Quant Falsify (L3).

Implements López de Prado (Advances in Financial Machine Learning, 2018):
  - PBO  (Probability of Backtest Overfitting) via CSCV
  - DSR  (Deflated Sharpe Ratio)
  - PSR  (Probabilistic Sharpe Ratio)
  - CPCV (Combinatorial Purged Cross-Validation splitter)

Also implements:
  - Permutation test (signal shuffle)
  - IC analysis with HAC (Newey-West) standard errors

This is a PURE LIBRARY. The sole verdict/exit-code path is quant_falsify_gate.py.
  from falsify_quant import pbo, dsr, psr, cpcv_split, permutation_test, ic_analysis

Dependencies: numpy, scipy, pandas (already in venv).
"""
from __future__ import annotations
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
try:
    import empyrical
except Exception as _empyrical_err:
    # [止血] empyrical missing (not in [quant] extra) OR broken (0.5.5 on
    # numpy 2.0 / py3.12). 治本 is empyrical-reloaded declared in [quant]
    # (plus pytz — empyrical-reloaded imports it but doesn't declare it).
    warnings.warn(
        f"empyrical import failed ({type(_empyrical_err).__name__}: "
        f"{_empyrical_err}); quant metrics will degrade to None "
        f"(numpy={np.__version__}, pandas={pd.__version__}, "
        f"python={sys.version_info[:3]})",
        RuntimeWarning,
        stacklevel=2,
    )
    empyrical = None

# empyrical 0.5.5 uses np.NINF which was removed in NumPy 2.0.
# Harmless when empyrical-reloaded is used; keeps 0.5.5 alive if installed.
if not hasattr(np, 'NINF'):
    np.NINF = -np.inf




# ═══════════════════════════════════════════════════════════════════════════════
# PBO — Probability of Backtest Overfitting (Bailey & López de Prado, 2014)
# ═════════════════════════════════════════════════•═════════════════════════════

def pbo(returns_matrix: np.ndarray, n_bins: int = 16) -> dict:
    """Compute Probability of Backtest Overfitting via CSCV.

    Args:
        returns_matrix: shape (T, N) — T time steps, N parameter combinations.
                        Each column is the daily returns of one parameter combo.
        n_bins: number of sub-samples to split the timeline into (default 16).

    Returns:
        dict with:
          pbo: float in [0, 1] — probability that IS-best is OOS-below-median
          logit: float — PBO in logit space
          is_best_oos_ranks: list of OOS ranks of IS-best for each bin combination
          lambda_matrix: the CSCV lambda matrix
    """
    T, N = returns_matrix.shape
    if T < n_bins * 4:
        return {"pbo": None, "error": f"Insufficient data: T={T} < n_bins*4={n_bins*4}"}
    if N < 2:
        return {"pbo": None, "error": f"Need >=2 parameter combos, got N={N}"}

    # Step 1: NO normalization. Sharpe = mean/std is already scale-invariant.
    # Normalizing by full-sample sigma is lookahead (uses OOS data to scale IS).
    # Normalizing by mean destroys alpha signal. Use raw returns directly.
    R = returns_matrix.copy()

    # Step 2: Split into n_bins sub-samples
    bin_size = T // n_bins
    # Trim excess
    R = R[:bin_size * n_bins]
    bins = [R[i * bin_size:(i + 1) * bin_size] for i in range(n_bins)]

    # Step 3: For each combination of bins as IS (half) vs OOS (half),
    # find IS-best strategy, check its OOS rank.
    # To keep computation tractable, we use leave-one-block-out style:
    # split bins into IS group (first half) and OOS group (second half),
    # then rotate. Full combinatorial is C(n_bins, n_bins//2) which can be huge.
    # We use the standard CSCV approach: all possible n_bins//2 selections.

    from itertools import combinations
    half = n_bins // 2
    oos_ranks_of_is_best = []

    for is_indices in combinations(range(n_bins), half):
        oos_indices = [i for i in range(n_bins) if i not in is_indices]

        # IS returns: concatenate IS bins
        is_returns = np.vstack([bins[i] for i in is_indices])
        # OOS returns: concatenate OOS bins
        oos_returns = np.vstack([bins[i] for i in oos_indices])

        # IS Sharpe for each strategy
        is_sr = is_returns.mean(axis=0) / (is_returns.std(axis=0, ddof=1) + 1e-10)
        # IS-best strategy index
        is_best_idx = np.argmax(is_sr)

        # OOS Sharpe for each strategy
        oos_sr = oos_returns.mean(axis=0) / (oos_returns.std(axis=0, ddof=1) + 1e-10)
        # OOS rank of IS-best (0 = worst, N-1 = best)
        oos_rank = sp_stats.rankdata(oos_sr)[is_best_idx] - 1  # 0-indexed
        oos_ranks_of_is_best.append(oos_rank)

    oos_ranks = np.array(oos_ranks_of_is_best)
    n_total = len(oos_ranks)

    # PBO = fraction where IS-best ranks below median OOS
    median_rank = (N - 1) / 2.0
    pbo_value = np.mean(oos_ranks <= median_rank)

    # Logit
    omega = pbo_value
    if omega >= 1.0:
        logit = 999.0   # sentinel for +inf (JSON-serializable)
    elif omega <= 0.0:
        logit = -999.0  # sentinel for -inf
    else:
        logit = math.log(omega / (1 - omega))

    return {
        "pbo": round(float(pbo_value), 4),
        "logit": round(float(logit), 4),
        "n_combinations": n_total,
        "n_strategies": N,
        "n_bins": n_bins,
        "oos_ranks_distribution": {
            "mean": round(float(oos_ranks.mean()), 2),
            "std": round(float(oos_ranks.std()), 2),
            "median": round(float(np.median(oos_ranks)), 2),
            "pct_below_median": round(float(np.mean(oos_ranks <= median_rank)) * 100, 2),
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PSR — Probabilistic Sharpe Ratio (Bailey & López de Prado, 2012)
# ═══════════════════════════════════════════════════════════════════════════════

def psr(sharpe: float, n: int, skew: float, kurt: float,
        benchmark_sharpe: float = 0.0, periods_per_year: int = 365) -> dict:
    """Compute Probabilistic Sharpe Ratio.

    PSR answers: what is the probability that the true Sharpe > benchmark?

    Args:
        sharpe: observed annualized Sharpe ratio
        n: number of return observations
        skew: skewness of returns
        kurt: kurtosis of returns (excess, i.e. scipy's default)
        benchmark_sharpe: threshold Sharpe to beat (default 0)
        periods_per_year: annualization factor

    Returns:
        dict with psr, z_stat, p_value, benchmark
    """
    # De-annualize
    sr_daily = sharpe / math.sqrt(periods_per_year)
    sr_bench_daily = benchmark_sharpe / math.sqrt(periods_per_year)

    # PSR formula (Bailey & López de Prado 2012)
    # Z = [(SR - SR_bench) * sqrt(n-1)] / sqrt(1 - skew*SR + (kurt-1)/4 * SR^2)
    # where kurt = RAW kurtosis (not excess). Our input kurt is excess (scipy default),
    # so (kurt-1)/4 in terms of raw = (excess+3-1)/4 = (excess+2)/4.
    # Verified against pypbo reference implementation (esvhd/pypbo on GitHub).
    diff = sr_daily - sr_bench_daily
    # Guard against negative sqrt argument (high skew + high SR can make this negative)
    denom_sq = 1 - skew * sr_daily + (kurt + 2) / 4 * sr_daily ** 2
    if denom_sq <= 0:
        return {"psr": None, "error": f"denominator^2 = {denom_sq:.4f} <= 0 (skew={skew}, kurt={kurt}, SR_daily={sr_daily:.4f}) — PSR undefined for these parameters"}
    denom = math.sqrt(denom_sq)
    if n < 2:
        return {"psr": None, "error": f"n={n} < 2, insufficient for PSR (sqrt(n-1) requires n>=2)"}
    z_stat = diff * math.sqrt(n - 1) / denom
    psr_value = sp_stats.norm.cdf(z_stat)

    return {
        "psr": round(float(psr_value), 4),
        "z_stat": round(float(z_stat), 4),
        "p_value": round(float(1 - psr_value), 4),
        "benchmark_sharpe": benchmark_sharpe,
        "n": n,
        "skew": round(float(skew), 4),
        "kurt": round(float(kurt), 4),
        "interpretation": (
            "PSR > 0.95: strong evidence SR > benchmark"
            if psr_value > 0.95 else
            "PSR > 0.90: moderate evidence"
            if psr_value > 0.90 else
            "PSR <= 0.90: insufficient evidence SR > benchmark"
        )
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Effective Trials — correlation-adjusted trial count for DSR
# ═══════════════════════════════════════════════════════════════════════════════

def compute_effective_trials(returns_matrix: np.ndarray, method: str = "liji") -> dict:
    """Compute effective number of independent trials from returns matrix correlation.

    When multiple strategies are highly correlated (e.g. parameter variations of
    the same signal), using raw column count N as n_trials for DSR is overly
    conservative. This function estimates the effective number of independent
    trials using eigenvalue-based methods from statistical genetics.

    Methods:
      - 'liji': Li & Ji (2005) — count eigenvalues >= 1.0 of correlation matrix.
        Established in genetics (GEC software). Permutation-validated FPR < 8%.
      - 'pr': Participation ratio = tr(C)^2 / tr(C^2).
        Physics/RMT concept. More aggressive (lower M_eff). Permutation-validated
        FPR can exceed 10% — use with caution.
      - 'galwey': Galwey (2009) — (sum sqrt(lambda))^2 / sum(lambda).
        Intermediate between liji and pr.

    Args:
        returns_matrix: (n_days, n_strategies) array of returns
        method: 'liji', 'pr', or 'galwey'

    Returns:
        dict with m_eff, method, n_raw, eigenvalues, and note
    """
    df = pd.DataFrame(returns_matrix)
    C = df.corr().values
    C = np.nan_to_num(C, nan=0.0)
    np.fill_diagonal(C, 1.0)

    N = C.shape[0]
    eigenvalues = np.linalg.eigvalsh(C)
    eigenvalues = np.sort(eigenvalues)[::-1]

    if method == "liji":
        m_eff = max(1, int(np.sum(eigenvalues >= 1.0)))
    elif method == "pr":
        tr_C = np.trace(C)
        tr_C2 = np.trace(C @ C)
        m_eff = max(1, int(round(tr_C ** 2 / tr_C2))) if tr_C2 > 0 else N
    elif method == "galwey":
        pos = eigenvalues[eigenvalues > 0]
        if len(pos) > 0 and np.sum(pos) > 0:
            m_eff = max(1, int(round(float(np.sum(np.sqrt(pos)) ** 2 / np.sum(pos)))))
        else:
            m_eff = N
    else:
        raise ValueError(f"Unknown effective trials method: {method}")

    return {
        "m_eff": m_eff,
        "method": method,
        "n_raw": int(N),
        "eigenvalues_top5": [round(float(x), 4) for x in eigenvalues[:5]],
        "n_eigenvalues_above_1": int(np.sum(eigenvalues >= 1.0)),
        "note": (
            "Li & Ji (2005) eigenvalue-based effective trials. "
            "Permutation-validated: FPR < 8% at DSR>0.90 threshold. "
            "Cite: Li & Ji, Heredity 2005, DOI 10.1038/sj.hdy.6800717"
            if method == "liji" else
            f"Method={method}. See falsify_quant.py docstring for caveats."
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DSR — Deflated Sharpe Ratio (Bailey & López de Prado, 2014)
# ═══════════════════════════════════════════════════════════════════════════════

def dsr(observed_sr: float, n: int, skew: float, kurt: float,
        n_trials: int = 1, periods_per_year: int = 365) -> dict:
    """Compute Deflated Sharpe Ratio.

    DSR adjusts PSR for multiple testing: if you tried N strategies,
    the best one's SR needs to be judged against the expected maximum SR
    of N random strategies, not against 0.

    Args:
        observed_sr: observed annualized Sharpe ratio (the best one from N trials)
        n: number of return observations
        skew: return skewness
        kurt: return kurtosis (excess)
        n_trials: number of strategies tried (for multiple testing correction)
        periods_per_year: annualization factor

    Returns:
        dict with dsr, psr_adjusted, haircut, expected_max_sr, n_trials
    """
    if n_trials < 1:
        n_trials = 1

    # Expected maximum Sharpe of N independent trials under null (SR=0)
    # Bailey & López de Prado (2014), Eq. 9:
    #   E[max_N(Z)] = (1-γ)·Φ⁻¹(1-1/N) + γ·Φ⁻¹(1-1/(eN))
    # where γ = Euler-Mascheroni constant ≈ 0.5772, Z ~ N(0,1).
    # This is the EXACT expected max of N standard normal order statistics,
    # NOT the sqrt(2*ln(N)) large-N approximation (which overestimates by ~40% at N=8).
    # Match pypbo's expected_max() exactly for cross-validation.
    if n_trials <= 1:
        expected_max_sr = 0.0
    else:
        # Bailey & López de Prado (2014), Eq. 9 — valid for ALL N >= 2.
        # Do NOT fall back to sqrt(2*ln(N)) for small N: that approximation
        # has 62-126% bias at N=2..4 (worse than the 40% at N=8 we already fixed).
        euler_gamma = 0.5772156649015329
        z1 = sp_stats.norm.ppf(1 - 1.0 / n_trials)
        z2 = sp_stats.norm.ppf(1 - 1.0 / (math.e * n_trials))
        expected_max_z = (1 - euler_gamma) * z1 + euler_gamma * z2
        # Scale from standardized (daily, unit-variance) to annualized
        sigma_sr_annual = math.sqrt(periods_per_year / n)
        expected_max_sr = expected_max_z * sigma_sr_annual

    # De-annualize observed SR
    sr_daily = observed_sr / math.sqrt(periods_per_year)
    expected_max_sr_daily = expected_max_sr / math.sqrt(periods_per_year)

    # DSR = PSR with benchmark = expected_max_sr
    result = psr(observed_sr, n, skew, kurt,
                 benchmark_sharpe=expected_max_sr, periods_per_year=periods_per_year)
    result["dsr"] = result.pop("psr")
    result["expected_max_sr_annualized"] = round(float(expected_max_sr), 4)
    result["n_trials"] = n_trials
    result["haircut_pct"] = round(float((1 - result["dsr"]) * 100
                                        if result["dsr"] is not None else 100), 2)

    result["interpretation"] = (
        "DSR > 0.95: SR survives multiple testing correction"
        if result["dsr"] and result["dsr"] > 0.95 else
        "DSR > 0.90: borderline; more trials needed to be sure"
        if result["dsr"] and result["dsr"] > 0.90 else
        "DSR <= 0.90: SR likely inflated by selection bias"
        if result["dsr"] else "DSR: computation error"
    )

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CPCV — Combinatorial Purged Cross-Validation Splitter
# ═══════════════════════════════════════════════════════════════════════════════

def cpcv_split(n_samples: int, n_groups: int, n_test_groups: int,
               purge: int = 0, embargo: int = 0) -> list:
    """Generate CPCV train/test splits.

    Args:
        n_samples: total number of time-ordered samples
        n_groups: number of groups to divide data into
        n_test_groups: number of groups in test set per split
        purge: number of samples to remove between train and test
        embargo: number of samples to remove after test set

    Returns:
        list of (train_indices, test_indices) tuples
    """
    from itertools import combinations

    group_size = n_samples // n_groups
    if group_size == 0:
        return []

    groups = [list(range(i * group_size, min((i + 1) * group_size, n_samples)))
              for i in range(n_groups)]

    splits = []
    for test_combo in combinations(range(n_groups), n_test_groups):
        test_indices = set()
        for g in test_combo:
            test_indices.update(groups[g])

        train_indices = set(range(n_samples)) - test_indices

        # Purge: remove samples adjacent to test boundaries
        if purge > 0:
            purge_set = set()
            for idx in sorted(test_indices):
                for p in range(1, purge + 1):
                    if idx - p >= 0:
                        purge_set.add(idx - p)
                    if idx + p < n_samples:
                        purge_set.add(idx + p)
            train_indices -= purge_set

        # Embargo: remove samples after test set ends
        if embargo > 0:
            max_test = max(test_indices)
            embargo_set = set(range(max_test + 1, min(max_test + 1 + embargo, n_samples)))
            train_indices -= embargo_set

        splits.append((sorted(train_indices), sorted(test_indices)))

    return splits


# ═════════════════════════════════════════════════════════════════════════•═════
# Permutation Test — signal shuffle
# ═══════════════════════════════════════════════════════════════════════════════

def permutation_test(returns: np.ndarray, n_permutations: int = 1000,
                     seed: int = 42) -> dict:
    """Bootstrap test for Sharpe ratio significance under null H0: mean=0.

    Shuffling the order of returns does NOT change SR (mean/std are permutation
    invariant). The correct test is a bootstrap under the null: center returns
    to zero mean, resample with replacement, compute SR for each bootstrap
    sample. If the observed SR is extreme relative to this null distribution,
    the mean is unlikely to be zero.

    Args:
        returns: 1D array of daily returns
        n_permutations: number of bootstrap resamples
        seed: random seed for reproducibility

    Returns:
        dict with observed_sr, boot_sr_mean, boot_sr_p95, p_value, significant
    """
    rng = np.random.default_rng(seed)
    returns = np.asarray(returns, dtype=float)
    n = len(returns)
    if n < 10:
        return {"p_value": None, "error": "insufficient data (<10 observations)"}

    # Observed SR (daily)
    obs_mean = returns.mean()
    obs_std = returns.std(ddof=1)
    # Guard against near-zero std (floating point: constant returns can produce
    # std ≈ 1e-17 instead of exactly 0, yielding phantom SR ~1e15)
    if obs_std < 1e-10:
        return {"p_value": None, "error": f"near-zero std ({obs_std:.2e}) — returns are effectively constant, SR undefined"}
    obs_sr = obs_mean / obs_std

    # Bootstrap under null H0: mean = 0
    # Center returns to remove the mean, then resample with replacement
    returns_centered = returns - obs_mean

    boot_srs = np.zeros(n_permutations)
    for i in range(n_permutations):
        sample = rng.choice(returns_centered, size=n, replace=True)
        s = sample.std(ddof=1)
        boot_srs[i] = sample.mean() / s if s > 0 else 0

    # One-sided p-value: fraction of bootstrap SRs >= observed
    p_value = np.mean(boot_srs >= obs_sr)

    return {
        "observed_sr_daily": round(float(obs_sr), 4),
        "boot_sr_mean": round(float(boot_srs.mean()), 4),
        "boot_sr_p95": round(float(np.percentile(boot_srs, 95)), 4),
        "p_value": round(float(p_value), 4),
        "n_permutations": n_permutations,
        "significant_at_5pct": bool(p_value < 0.05),
        "interpretation": (
            "p < 0.05: SR unlikely due to chance (mean significantly > 0)"
            if p_value < 0.05 else
            "p >= 0.05: SR could be explained by chance (not significant)"
        )
    }


# ═══════════════════════════════════════════════════════════════════════════════
# IC Analysis with Newey-West (HAC) standard errors
# ═══════════════════════════════════════════════════════════════════════════════

def ic_analysis(signal: np.ndarray, forward_returns: np.ndarray,
                max_lag: int = 5) -> dict:
    """Compute Information Coefficient with HAC (Newey-West) standard errors.

    Args:
        signal: 1D array of signal values at time t
        forward_returns: 1D array of forward returns at time t (return from t to t+1)
        max_lag: max lag for Newey-West HAC variance

    Returns:
        dict with ic_mean, ic_std_hac, ic_tstat, ic_ir, rank_ic, interpretation
    """
    signal = np.asarray(signal, dtype=float)
    forward_returns = np.asarray(forward_returns, dtype=float)
    n = len(signal)
    if n < 20:
        return {"ic_mean": None, "error": "insufficient data (<20 obs)"}

    # Drop NaN
    mask = ~(np.isnan(signal) | np.isnan(forward_returns))
    signal = signal[mask]
    forward_returns = forward_returns[mask]
    n = len(signal)
    if n < 20:
        return {"ic_mean": None, "error": "insufficient non-NaN data"}

    # Pearson IC
    ic_series = pd.Series(signal).rolling(1).corr(pd.Series(forward_returns))  # point IC
    ic = np.corrcoef(signal, forward_returns)[0, 1]
    # Rank IC (Spearman)
    rank_ic = sp_stats.spearmanr(signal, forward_returns).statistic

    # Newey-West HAC standard error for the mean of IC series
    # We compute IC as a time series (rolling) then compute HAC SE of its mean
    # For simplicity and robustness, compute cross-sectional IC per period if 2D,
    # but for 1D we compute the single IC and use bootstrap for SE.
    # Here we use the analytical NW formula on the demeaned product series.

    # IC = corr(s, r) = cov(s,r) / (std_s * std_r)
    # For HAC SE of correlation, use the delta method approximation:
    # SE(corr) ≈ (1 - corr^2) / sqrt(n) * correction factor
    # With HAC: SE_HAC = (1-r^2) * sqrt(Omega/n) where Omega accounts for autocorr

    # Demeaned product
    s_demean = signal - signal.mean()
    r_demean = forward_returns - forward_returns.mean()
    product = s_demean * r_demean
    product_mean = product.mean()
    var_s = np.var(signal, ddof=1)
    var_r = np.var(forward_returns, ddof=1)

    if var_s == 0 or var_r == 0:
        return {"ic_mean": None, "error": "zero variance in signal or returns"}

    # Newey-West HAC variance of the mean of `product`
    max_lag = min(max_lag, n - 1)
    gamma_0 = np.var(product, ddof=1)
    omega = gamma_0
    for lag in range(1, max_lag + 1):
        weight = 1 - lag / (max_lag + 1)
        gamma_lag = np.mean((product[:-lag] - product_mean) *
                            (product[lag:] - product_mean))
        omega += 2 * weight * gamma_lag

    # Delta method: SE(corr) ≈ omega_se / (var_s * var_r * n)
    # Simplified: use (1 - ic^2) / sqrt(n_eff) with n_eff adjusted for autocorr
    n_eff = n * gamma_0 / omega if omega > 0 else n
    se_ic = (1 - ic ** 2) / math.sqrt(n_eff) if n_eff > 0 else float('inf')
    t_stat = ic / se_ic if se_ic > 0 else 0

    # IC Information Ratio = mean(IC) / std(IC) — for single period, use ic/se
    ic_ir = ic / se_ic if se_ic > 0 else 0

    return {
        "ic_mean": round(float(ic), 4),
        "rank_ic": round(float(rank_ic), 4),
        "ic_std_hac": round(float(se_ic), 4),
        "ic_tstat": round(float(t_stat), 4),
        "ic_ir": round(float(ic_ir), 4),
        "n": n,
        "n_eff": round(float(n_eff), 1),
        "p_value": round(float(2 * (1 - sp_stats.norm.cdf(abs(t_stat)))), 4),
        "interpretation": (
            "IC t-stat > 2: significant predictive power"
            if abs(t_stat) > 2 else
            "IC t-stat 1-2: weak, borderline"
            if abs(t_stat) > 1 else
            "IC t-stat < 1: no significant predictive power"
        )
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Utility functions
# ═══════════════════════════════════════════════════════════════════════════════

class _ReturnsArray(np.ndarray):
    """ndarray carrying return-basis metadata from CSV loading."""

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.return_basis = getattr(obj, 'return_basis', 'simple')


def _as_returns_array(values, basis: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float).view(_ReturnsArray)
    arr.return_basis = basis
    return arr


def _load_daily_returns(path: str, return_column: str | None = None) -> np.ndarray:
    """Load daily returns from CSV with fail-closed column selection.

    Quant mode must never silently fall back to the "last numeric column": in
    real backtests that column is often gross/turnover/equity/n_legs.  If an
    explicit return_column is supplied it must exist and must be one of the
    accepted return-basis columns.  Otherwise we auto-detect only from the
    canonical names below, with ret_log priority.
    """
    df = pd.read_csv(path)
    allowed = ['ret_log', 'ret_simple', 'ret', 'returns', 'daily_ret', 'pnl']
    if return_column:
        if return_column not in df.columns:
            raise ValueError(f"Explicit return column {return_column!r} not found in {path}. Columns: {list(df.columns)}")
        if return_column not in allowed:
            raise ValueError(f"Explicit return column {return_column!r} is not an accepted return column name {allowed}; rename it or extend the allowlist explicitly.")
        basis = 'log' if return_column == 'ret_log' else 'simple'
        return _as_returns_array(df[return_column].dropna().values, basis)
    for col in allowed:
        if col in df.columns:
            basis = 'log' if col == 'ret_log' else 'simple'
            return _as_returns_array(df[col].dropna().values, basis)
    raise ValueError(f"No canonical return column found in {path}. Required one of {allowed}. Refusing last-numeric fallback. Columns: {list(df.columns)}")


def _parse_csv_list(value: str) -> list[str]:
    """Parse comma-separated CLI column list."""
    return [x.strip() for x in value.split(',') if x.strip()]


def _load_returns_matrix(path: str, columns_csv: str) -> tuple[pd.DataFrame, list[str]]:
    """Load a returns matrix using explicit return columns only."""
    if not columns_csv:
        raise ValueError("--returns-matrix requires --matrix-columns. Refusing select_dtypes(all numeric) because it can ingest gross/turnover/equity as fake strategies.")
    df = pd.read_csv(path)
    cols = _parse_csv_list(columns_csv)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Matrix columns missing from {path}: {missing}. Available columns: {list(df.columns)}")
    rm = df[cols].apply(pd.to_numeric, errors='coerce').dropna()
    if rm.shape[1] < 2:
        raise ValueError(f"Need >=2 explicit matrix return columns, got {rm.shape[1]}: {cols}")
    return rm, cols


def _count_trial_ledger(path: str) -> int | None:
    """Best-effort declared-trial count from json/jsonl/csv/text ledger."""
    if not path:
        return None
    ledger = Path(path)
    if not ledger.exists():
        raise ValueError(f"trial ledger not found: {path}")
    if ledger.suffix.lower() == '.json':
        obj = json.loads(ledger.read_text())
        if isinstance(obj, list):
            return len(obj)
        if isinstance(obj, dict):
            for key in ('n_trials', 'trial_count', 'declared_trials'):
                if key in obj:
                    return int(obj[key])
            for key in ('trials', 'trial_ledger', 'items'):
                if isinstance(obj.get(key), list):
                    return len(obj[key])
        raise ValueError(f"Cannot infer trial count from json ledger: {path}")
    if ledger.suffix.lower() == '.jsonl':
        return sum(1 for line in ledger.read_text().splitlines() if line.strip())
    if ledger.suffix.lower() == '.csv':
        return int(len(pd.read_csv(ledger)))
    return sum(1 for line in ledger.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#'))


def _evidence_file_readable(path: str, label: str) -> list[str]:
    """Return evidence-integrity issues for one required artifact path."""
    issues = []
    if not path:
        return [f"{label} missing"]
    p = Path(path)
    if not p.exists():
        return [f"{label} not found: {path}"]
    try:
        if p.suffix.lower() == '.json':
            obj = json.loads(p.read_text(encoding='utf-8'))
            if obj in ({}, [], None):
                issues.append(f"{label} is empty json: {path}")
        elif p.suffix.lower() == '.csv':
            df = pd.read_csv(p)
            if len(df) == 0 or len(df.columns) == 0:
                issues.append(f"{label} is empty csv: {path}")
        elif p.suffix.lower() in ('.yaml', '.yml'):
            text = p.read_text(encoding='utf-8')
            if not text.strip():
                issues.append(f"{label} is empty yaml: {path}")
            else:
                try:
                    import yaml
                    obj = yaml.safe_load(text)
                    if obj in ({}, [], None):
                        issues.append(f"{label} is empty yaml: {path}")
                except ImportError:
                    pass
        else:
            if not p.read_text(encoding='utf-8').strip():
                issues.append(f"{label} is empty text: {path}")
    except Exception as e:
        issues.append(f"{label} unreadable: {path}: {type(e).__name__}: {str(e)[:120]}")
    return issues



def _validate_evidence_integrity(calendar_contract: str = '', row_loss_audit: str = '',
                                 coverage_manifest: str = '', variant_policy: str = '') -> dict:
    """L0.5 evidence integrity gate for PASS-capable Quant Falsify."""
    required = {
        'calendar_contract': calendar_contract,
        'row_loss_audit': row_loss_audit,
        'coverage_manifest': coverage_manifest,
        'variant_policy': variant_policy,
    }
    issues = []
    for label, path in required.items():
        issues.extend(_evidence_file_readable(path, label))
    return {'status': 'PASS' if not issues else 'BLOCK',
            'artifacts': required, 'issues': issues}


def _compute_stats(returns: np.ndarray, periods_per_year: int = 365) -> dict:
    """Compute basic return statistics.

    CSV-loaded ret_log arrays are treated as log returns for SR/skew/kurtosis.
    Metrics that require compounding or downside paths (cum return, MaxDD,
    Sortino) use simple returns derived via expm1(log_return). Plain ndarray
    inputs and CSV columns without ret_log are treated as simple returns to keep
    legacy fixtures/backward compatibility intact.
    """
    # Drop NaN — report actual valid count, not array length
    input_basis = getattr(returns, 'return_basis', 'simple')
    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    n = len(returns)
    if n == 0:
        return {"n": 0, "error": "no valid (non-NaN) return observations"}
    if n < 2:
        return {"n": n, "error": f"only {n} valid observation(s), need >= 2 for statistics"}
    rets_series = pd.Series(returns)
    simple_returns = np.expm1(returns) if input_basis == 'log' else returns
    simple_series = pd.Series(simple_returns)
    mean = float(returns.mean())
    std = float(returns.std(ddof=1))
    skew = float(sp_stats.skew(returns))
    kurt = float(sp_stats.kurtosis(returns))  # excess kurtosis
    cum = float(np.expm1(returns.sum())) if input_basis == 'log' else float((1 + rets_series).prod() - 1)

    # Sharpe — use the native return basis (log for ret_log, simple otherwise)
    sr = float(returns.mean() / returns.std(ddof=1) * math.sqrt(periods_per_year))

    # [止血] empyrical missing — MaxDD/Sortino degrade to None instead of crashing.
    # 治本 is a working empyrical install (empyrical-reloaded in [quant] extra).
    if empyrical is None:
        max_dd = None
        sortino = None
    else:
        # MaxDD — empyrical returns negative fraction, convert to positive %
        emp_dd = float(empyrical.max_drawdown(simple_series))
        max_dd = abs(emp_dd) if not math.isnan(emp_dd) else 0.0

        # Sortino — empyrical on simple returns for downside compounding semantics
        emp_sortino = float(empyrical.sortino_ratio(simple_series, period='daily', annualization=periods_per_year))
        sortino = emp_sortino if not math.isnan(emp_sortino) else None

    return {
        "n": n,
        "return_basis": input_basis,
        "mean_daily": round(mean, 6),
        "std_daily": round(std, 6),
        "sharpe_annualized": round(sr, 4),
        "sortino": round(sortino, 4) if sortino is not None else None,
        "skew": round(skew, 4),
        "kurtosis_excess": round(kurt, 4),
        "cum_return_pct": round(cum * 100, 2),
        "max_drawdown_pct": round(max_dd * 100, 2) if max_dd is not None else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# L4 Robustness: Walk-forward IS→OOS predictive power
# ═══════════════════════════════════════════════════════════════════════════════

def _wf_validate(returns_matrix: np.ndarray, window_size: int, step_size: int) -> tuple | dict:
    """Validate walk-forward inputs. Returns (T, N, cleaned_matrix) or error dict."""
    T, N = returns_matrix.shape
    if window_size <= 0 or step_size <= 0:
        return {"error": f"window_size and step_size must be > 0 (got {window_size}, {step_size})"}
    if T < window_size + step_size:
        return {"error": f"Insufficient data: T={T} < window+step={window_size+step_size}"}
    if N < 2:
        return {"error": f"Need >=2 parameter combos for walk-forward, got N={N}"}
    returns_matrix = np.asarray(returns_matrix, dtype=float)
    valid_mask = ~np.isnan(returns_matrix).any(axis=1)
    returns_matrix = returns_matrix[valid_mask]
    T = len(returns_matrix)
    if T < window_size + step_size:
        return {"error": f"Insufficient non-NaN data: T={T} < window+step={window_size+step_size}"}
    return (T, N, returns_matrix)


def _wf_sr(returns, periods_per_year: int = 365) -> float:
    """Annualized Sharpe for a 1D return array."""
    if len(returns) < 2:
        return 0.0
    s = returns.std(ddof=1)
    if s < 1e-10:
        return 0.0
    return returns.mean() / s * math.sqrt(periods_per_year)


def _wf_roll_one(returns_matrix: np.ndarray, start: int, window_size: int,
                  step_size: int, N: int, periods_per_year: int) -> dict:
    """Roll one IS→OOS window. Returns roll result dict."""
    is_returns = returns_matrix[start:start + window_size]
    oos_returns = returns_matrix[start + window_size:start + window_size + step_size]
    is_srs = np.array([_wf_sr(is_returns[:, j], periods_per_year) for j in range(N)])
    oos_srs = np.array([_wf_sr(oos_returns[:, j], periods_per_year) for j in range(N)])
    is_best_idx = int(np.argmax(is_srs))
    oos_perf_of_is_best = oos_srs[is_best_idx]
    oos_optimal = np.max(oos_srs)
    oos_median = np.median(oos_srs)
    if oos_optimal > 1e-10:
        ratio = oos_perf_of_is_best / oos_optimal
    else:
        ratio = None
    return {
        "start": start,
        "is_best_param": is_best_idx,
        "is_sr": round(float(is_srs[is_best_idx]), 4),
        "oos_sr_of_is_best": round(float(oos_perf_of_is_best), 4),
        "oos_optimal_sr": round(float(oos_optimal), 4),
        "oos_median_sr": round(float(oos_median), 4),
        "predictive_ratio": round(float(ratio), 4) if ratio is not None else None,
    }


def _wf_sweep(returns_matrix: np.ndarray, T: int, N: int,
              window_size: int, step_size: int, periods_per_year: int,
              sweep_what: str = "window") -> list:
    """Sensitivity sweep over window-size (±20%) or step-size (±20%).
    Returns list of {window_size|step_size, mean_predictive_ratio, n_windows}."""
    results = []
    multipliers = [0.8, 1.0, 1.2]
    for mult in multipliers:
        if sweep_what == "window":
            w = int(window_size * mult)
            s = step_size
        else:
            w = window_size
            s = max(int(step_size * mult), 1)
        if T < w + s:
            continue
        start = 0
        sweep_ratios = []
        while start + w + s <= T:
            is_r = returns_matrix[start:start + w]
            oos_r = returns_matrix[start + w:start + w + s]
            is_srs = np.array([_wf_sr(is_r[:, j], periods_per_year) for j in range(N)])
            oos_srs = np.array([_wf_sr(oos_r[:, j], periods_per_year) for j in range(N)])
            best = int(np.argmax(is_srs))
            oos_best = oos_srs[best]
            oos_opt = np.max(oos_srs)
            if oos_opt > 1e-10:
                sweep_ratios.append(oos_best / oos_opt)
            start += s
        if sweep_ratios:
            key = "window_size" if sweep_what == "window" else "step_size"
            results.append({
                key: w if sweep_what == "window" else s,
                "mean_predictive_ratio": round(float(np.mean(sweep_ratios)), 4),
                "n_windows": len(sweep_ratios),
            })
    return results


def _wf_sweep_stable(sweep_results: list, mean_ratio: float | None) -> bool:
    """Check if sweep results are stable (±0.2 of mean_ratio)."""
    if not sweep_results:
        return True
    comparable = [sr for sr in sweep_results if sr.get("n_windows", 0) >= 2]
    if len(comparable) < 2:
        return True
    return all(
        abs(sr["mean_predictive_ratio"] - (mean_ratio or 0)) < 0.2
        for sr in comparable
    )


def _wf_identical_columns(returns_matrix: np.ndarray, N: int) -> dict | None:
    """Check if all columns are identical (false PASS guard). Returns error dict or None."""
    if N < 2:
        return None
    max_col_diff = 0.0
    for j in range(1, N):
        d = float(np.abs(returns_matrix[:, j] - returns_matrix[:, 0]).max())
        if d > max_col_diff:
            max_col_diff = d
    if max_col_diff < 1e-15:
        return {
            "error": "All columns are identical — no parameter selection is occurring. "
                     "Walk-forward ratio is trivially 1.0 but meaningless.",
            "mean_predictive_ratio": None,
            "verdict": "INSUFFICIENT_DATA — identical columns; cannot assess predictive power",
        }
    return None


def _wf_verdict(mean_ratio: float | None, sensitivity_stable: bool,
                step_sensitivity_stable: bool) -> str:
    """Build the verdict string from results."""
    if mean_ratio is None:
        verdict = "INSUFFICIENT_DATA — OOS optimal SR <= 0 for all windows; cannot assess predictive power"
    elif mean_ratio > 0.7:
        verdict = "PASS — IS selection has predictive power for OOS"
    elif mean_ratio < 0.3:
        verdict = "WARN — IS selection is chasing noise (low OOS predictive power)"
    else:
        verdict = "BORDERLINE — IS selection has weak OOS predictive power"
    if mean_ratio is not None and not sensitivity_stable:
        verdict += "; WARN: window-size sensitive (result may be artifact of chosen window)"
    if mean_ratio is not None and not step_sensitivity_stable:
        verdict += "; WARN: step-size sensitive (result may be artifact of chosen roll cadence)"
    return verdict


def walk_forward_predictive_power(returns_matrix: np.ndarray,
                                   window_size: int = 120,
                                   step_size: int = 60,
                                   periods_per_year: int = 365) -> dict:
    """Test whether IS parameter selection has predictive power for OOS.

    Not "do parameters stay stable?" but "does the IS-selected parameter
    also perform well in the immediately following OOS period?"

    Sean's framework (podcast 2026-06):
    - Level 1: parameter never changes (ideal, e.g. arbitrage)
    - Level 2: parameter changes, but IS-selected is also OOS-good (acceptable)
    - Level 3: parameter changes and IS-selected is OOS-bad (chasing noise)

    For each rolling window:
      1. IS period = first `window_size` rows
      2. OOS period = next `step_size` rows
      3. Find IS-best column (highest SR)
      4. Record OOS SR of IS-best vs OOS-optimal SR
      5. Roll forward by `step_size`

    Also runs a window-size sensitivity sweep (±20%).

    Args:
        returns_matrix: (T, N) — T time steps, N parameter combinations
        window_size: IS window size in rows (default 120 ≈ 4 months daily)
        step_size: OOS window + roll step (default 60 ≈ 2 months)
        periods_per_year: annualization factor

    Returns:
        dict with predictive_ratio (OOS_perf_of_IS_selected / OOS_optimal),
        parameter drift sequence, window sensitivity, verdict
    """
    validated = _wf_validate(returns_matrix, window_size, step_size)
    if isinstance(validated, dict):
        return validated
    T, N, returns_matrix = validated

    # Identical columns guard (false PASS)
    identical_err = _wf_identical_columns(returns_matrix, N)
    if identical_err:
        return identical_err

    # Main rolling loop
    roll_results = []
    param_sequence = []
    start = 0
    while start + window_size + step_size <= T:
        result = _wf_roll_one(returns_matrix, start, window_size, step_size, N, periods_per_year)
        roll_results.append(result)
        param_sequence.append(result["is_best_param"])
        start += step_size

    # Aggregate
    ratios = [r["predictive_ratio"] for r in roll_results if r["predictive_ratio"] is not None]
    mean_ratio = float(np.mean(ratios)) if ratios else None

    param_changes = sum(1 for i in range(1, len(param_sequence))
                        if param_sequence[i] != param_sequence[i-1])

    # Sensitivity sweeps
    sensitivity_results = _wf_sweep(returns_matrix, T, N, window_size, step_size,
                                     periods_per_year, sweep_what="window")
    step_sensitivity_results = _wf_sweep(returns_matrix, T, N, window_size, step_size,
                                          periods_per_year, sweep_what="step")
    sensitivity_stable = _wf_sweep_stable(sensitivity_results, mean_ratio)
    step_sensitivity_stable = _wf_sweep_stable(step_sensitivity_results, mean_ratio)

    verdict = _wf_verdict(mean_ratio, sensitivity_stable, step_sensitivity_stable)

    return {
        "mean_predictive_ratio": round(mean_ratio, 4) if mean_ratio is not None else None,
        "param_drift_count": param_changes,
        "param_drift_note": (
            "Parameters drift across windows — this is EXPECTED and acceptable per Sean's "
            "Level 2 framework. The test is IS→OOS predictive power, NOT parameter stability. "
            "Do NOT reject a strategy because parameters change; reject only if predictive_ratio is low."
        ),
        "n_rolls": len(roll_results),
        "param_sequence": param_sequence,
        "roll_details": roll_results,
        "window_sensitivity": sensitivity_results,
        "sensitivity_stable": sensitivity_stable,
        "step_size_sensitivity": step_sensitivity_results,
        "step_size_sensitivity_stable": step_sensitivity_stable,
        "verdict": verdict,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# L4 Robustness: PnL-driven regime analysis
# ═══════════════════════════════════════════════════════════════════════════════

def pnl_regime_analysis(returns: np.ndarray, vol_window: int = 30,
                         periods_per_year: int = 365,
                         volume: np.ndarray = None) -> dict:
    """PnL-driven regime detection: start from PnL, find separating variable.

    Calvin's framework (podcast 2026-06): don't pick indicators first and
    slice by them. Look at when the strategy makes vs loses money, then
    find what variable separates those states.

    Sean (podcast 2026-06): vol and volume are NOT correlated. "可以橫盤
    reversion 但成交很高." Must test multiple candidate variables, not just vol.

    Implementation: compute rolling realized vol, bucket daily returns by
    vol quartile AND (if volume provided) volume quartile. If SR is
    concentrated in one quartile of ANY variable, alpha is regime-dependent.

    Args:
        returns: 1D array of daily returns
        vol_window: rolling window for realized vol computation (default 30d)
        periods_per_year: annualization factor
        volume: optional 1D array of trading volume (same length as returns).
                If provided, also tests volume-quartile regime analysis.

    Returns:
        dict with per-variable quartile SRs, concentration ratio, verdict
    """
    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    n = len(returns)
    if n < vol_window * 4:
        return {"error": f"Insufficient data: n={n} < vol_window*4={vol_window*4}"}

    # Rolling realized vol (std of returns over window)
    rolling_vol = np.array([
        returns[max(0, i - vol_window):i].std(ddof=1) if i >= 2 else 0.0
        for i in range(n)
    ])
    # First vol_window entries are warmup — use what's available
    valid = rolling_vol > 0
    if valid.sum() < n // 2:
        return {"error": "Too many zero-vol periods for regime analysis"}

    def _quartile_regime_test(regime_var: np.ndarray, rets: np.ndarray,
                               labels: list, var_name: str) -> dict:
        """Bucket returns by quartile of regime_var, compute SR per quartile."""
        edges = np.percentile(regime_var, [25, 50, 75])
        quartile_srs = {}
        for qi in range(4):
            if qi == 0:
                mask = regime_var <= edges[0]
            elif qi == 3:
                mask = regime_var > edges[2]
            else:
                mask = (regime_var > edges[qi-1]) & (regime_var <= edges[qi])
            q_rets = rets[mask]
            if len(q_rets) < 5:
                quartile_srs[labels[qi]] = {"sr": None, "n": len(q_rets)}
                continue
            q_std = q_rets.std(ddof=1)
            q_sr = q_rets.mean() / q_std * math.sqrt(periods_per_year) if q_std > 1e-10 else 0.0
            quartile_srs[labels[qi]] = {
                "sr": round(float(q_sr), 4),
                "n": len(q_rets),
                "mean_daily": round(float(q_rets.mean()), 6),
            }
        srs = [v["sr"] for v in quartile_srs.values() if v["sr"] is not None]
        if len(srs) < 2:
            return {"quartile_srs": quartile_srs, "verdict": "INSUFFICIENT_DATA",
                    "verdict_detail": f"Not enough non-null quartiles for {var_name}"}
        max_sr = max(srs)
        min_sr = min(srs)
        sr_spread = abs(max_sr - min_sr)
        sr_ratio = abs(max_sr) / max(abs(min_sr), 0.01)
        positive_quartiles = sum(1 for s in srs if s > 0)
        total_sr = sum(abs(s) for s in srs)
        top_quartile_share = abs(max_sr) / total_sr if total_sr > 0 else 0

        if top_quartile_share > 0.6 and sr_ratio > 3.0:
            v = "WARN — Alpha is regime-dependent (concentrated in one {} quartile)".format(var_name)
            best_q = labels[srs.index(max_sr)]
            vd = f"SR concentrated in {best_q} (SR={max_sr:.2f}), other quartiles SR≈{min_sr:.2f}"
        elif positive_quartiles < 4 and sr_spread > 4.0:
            v = "WARN — Alpha is regime-dependent (large SR spread across {} regimes)".format(var_name)
            vd = f"SR spread {sr_spread:.2f} across quartiles, range [{min_sr:.2f}, {max_sr:.2f}]"
        elif positive_quartiles == 4:
            v = "PASS — Alpha is present across all {} regimes".format(var_name)
            vd = f"All quartiles positive, SR range [{min_sr:.2f}, {max_sr:.2f}]"
        else:
            v = "BORDERLINE — Alpha present in some but not all {} regimes".format(var_name)
            vd = f"{positive_quartiles}/4 quartiles positive, SR range [{min_sr:.2f}, {max_sr:.2f}]"

        return {
            "quartile_srs": quartile_srs,
            "quartile_edges": [round(float(e), 6) for e in edges],
            "sr_spread": round(float(sr_spread), 4),
            "top_quartile_share": round(float(top_quartile_share), 4),
            "verdict": v,
            "verdict_detail": vd,
        }

    # ── Vol-quartile regime test ──
    vol_valid = rolling_vol[valid]
    rets_valid = returns[valid]
    vol_labels = ["Q1_low_vol", "Q2", "Q3", "Q4_high_vol"]
    vol_result = _quartile_regime_test(vol_valid, rets_valid, vol_labels, "vol")

    # ── Volume-quartile regime test (if volume provided) ──
    # Sean podcast L561-573: "volatility和volume不一定相关，可以横盘reversion但成交很高"
    volume_result = None
    if volume is not None:
        volume = np.asarray(volume, dtype=float)
        volume = volume[~np.isnan(volume)]
        if len(volume) == n:
            # Use rolling mean volume aligned with vol window
            rolling_vol_volume = np.array([
                volume[max(0, i - vol_window):i].mean() if i >= 2 else 0.0
                for i in range(n)
            ])
            vol_mask = (rolling_vol > 0) & (rolling_vol_volume > 0)
            if vol_mask.sum() >= n // 2:
                vol_valid_2 = rolling_vol_volume[vol_mask]
                rets_valid_2 = returns[vol_mask]
                vol_labels_2 = ["Q1_low_volume", "Q2", "Q3", "Q4_high_volume"]
                volume_result = _quartile_regime_test(
                    vol_valid_2, rets_valid_2, vol_labels_2, "volume")

    # Aggregate verdict: WARN if ANY variable shows regime dependence
    combined_verdict = vol_result.get("verdict", "INSUFFICIENT_DATA")
    combined_detail = f"[vol] {vol_result.get('verdict_detail', '')}"
    if volume_result is not None:
        vol_v = vol_result.get("verdict", "")
        vol_d = volume_result.get("verdict", "")
        if "WARN" in vol_v and "WARN" in vol_d:
            combined_verdict = "WARN — Alpha is regime-dependent across BOTH vol and volume"
        elif "WARN" in vol_v:
            combined_verdict = vol_v
        elif "WARN" in vol_d:
            combined_verdict = vol_d
        elif "PASS" in vol_v and "PASS" in vol_d:
            combined_verdict = "PASS — Alpha present across all vol AND volume regimes"
        elif "PASS" in vol_v or "PASS" in vol_d:
            combined_verdict = "BORDERLINE — Mixed results across regime variables"
        combined_detail = f"[vol] {vol_result.get('verdict_detail', '')} | [volume] {volume_result.get('verdict_detail', '')}"

    result = {
        "vol_regime": vol_result,
        "verdict": combined_verdict,
        "verdict_detail": combined_detail,
    }
    if volume_result is not None:
        result["volume_regime"] = volume_result
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# L4 Robustness: Cost realism check
# ═══════════════════════════════════════════════════════════════════════════════

def cost_realism_check(returns: np.ndarray, strategy_type: str = "",
                        vol_window: int = 30) -> dict:
    """Check whether fixed-bps cost model is realistic for this strategy.

    Market makers widen spreads when vol rises, so true slippage scales
    with vol. For momentum strategies (which chase price), high-vol periods
    have disproportionately higher slippage. For reversion strategies
    (which post limit orders), high-vol periods may actually help.

    Calvin (podcast 2026-06): "market makers use vol to set spreads,
    so your cost model must too."

    Args:
        returns: 1D array of daily returns
        strategy_type: "momentum", "reversion", or "" (unknown)
        vol_window: rolling window for realized vol

    Returns:
        dict with vol_ratio, strategy_type, verdict, recommendation
    """
    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    n = len(returns)
    if n < vol_window * 3:
        return {"error": f"Insufficient data: n={n} < vol_window*3={vol_window*3}"}

    # Rolling realized vol
    rolling_vol = np.array([
        returns[max(0, i - vol_window):i].std(ddof=1) if i >= 2 else 0.0
        for i in range(n)
    ])
    valid_vol = rolling_vol[rolling_vol > 0]
    if len(valid_vol) < 10:
        return {"error": "Too many zero-vol periods"}

    median_vol = float(np.median(valid_vol))
    max_vol = float(np.max(valid_vol))
    vol_ratio = max_vol / median_vol if median_vol > 0 else 0.0

    # Verdict depends on strategy type
    if strategy_type.lower() == "momentum":
        if vol_ratio > 3.0:
            verdict = "WARN"
            recommendation = (f"Vol ratio {vol_ratio:.1f}x: fixed bps underestimates cost in high-vol periods. "
                              f"Consider vol-adjusted: slippage = base_bps * (realized_vol / median_vol). "
                              f"Momentum chases price → high-vol = high slippage.")
        else:
            verdict = "PASS"
            recommendation = f"Vol ratio {vol_ratio:.1f}x: vol is stable enough for fixed bps."
    elif strategy_type.lower() == "reversion":
        verdict = "PASS"
        recommendation = (f"Vol ratio {vol_ratio:.1f}x: reversion posts limit orders, "
                          f"high vol may actually help fill rates. Fixed bps is conservative.")
    else:
        if vol_ratio > 5.0:
            verdict = "WARN"
            recommendation = (f"Vol ratio {vol_ratio:.1f}x is very high. If strategy is momentum-type, "
                              f"fixed bps underestimates cost. Verify strategy type and consider vol-adjusted cost.")
        else:
            verdict = "PASS"
            recommendation = f"Vol ratio {vol_ratio:.1f}x: acceptable for unknown strategy type."

    return {
        "vol_ratio": round(vol_ratio, 2),
        "median_vol": round(median_vol, 6),
        "max_vol": round(max_vol, 6),
        "strategy_type": strategy_type or "unknown",
        "verdict": verdict,
        "recommendation": recommendation,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# L4-E: Execution realism — delay sensitivity + cost stress test
# ═══════════════════════════════════════════════════════════════════════════════

def _exec_lag_autocorr(arr: np.ndarray, lag: int) -> float | None:
    """Lag-N autocorrelation of a return series."""
    if len(arr) <= lag + 2:
        return None
    r1 = arr[:-lag]
    r2 = arr[lag:]
    if np.std(r1) < 1e-12 or np.std(r2) < 1e-12:
        return 0.0
    return float(np.corrcoef(r1, r2)[0, 1])


def _exec_sharpe(arr, periods_per_year: int = 365) -> float | None:
    """Sharpe via empyrical, with NaN guard."""
    arr = np.asarray(arr, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 30:
        return None
    if empyrical is None:  # [止血] empyrical missing — caller must handle None
        return None
    sr = float(empyrical.sharpe_ratio(
        pd.Series(arr), period='daily', annualization=periods_per_year))
    return sr if not math.isnan(sr) else 0.0


def _exec_retention(sr_before: float | None, sr_after: float | None) -> float | None:
    """How much Sharpe survives the stress."""
    if sr_before is None or sr_after is None:
        return None
    if abs(sr_before) < 1e-8:
        return 0.0 if abs(sr_after) < 1e-8 else float('inf')
    return sr_after / sr_before


def _exec_delay_test(returns: np.ndarray, n: int, strategy_type: str) -> dict:
    """E dimension: delay sensitivity via lag-N autocorrelation."""
    delay_results = {}
    for delay_bars, label in [(1, "delay_1bar"), (2, "delay_2bar")]:
        if n <= delay_bars + 30:
            delay_results[label] = {"error": f"Insufficient data for {delay_bars}-bar delay"}
            continue
        ac = _exec_lag_autocorr(returns, delay_bars)
        if ac is None:
            verdict = "SKIP"
        elif ac < -0.2:
            if strategy_type.lower() == "reversion":
                verdict = "PASS"
            else:
                verdict = "WARN"
        else:
            verdict = "PASS"
        delay_results[label] = {
            "lag_autocorr": round(ac, 4) if ac is not None else None,
            "verdict": verdict,
        }
    return delay_results


def _exec_cost_stress(returns: np.ndarray, sr_base: float, base_cost_bps: float,
                       periods_per_year: int) -> dict:
    """A dimension: cost stress test at 2x and 3x base cost."""
    COST_STRESS_MIN_SR = 0.1
    if sr_base < COST_STRESS_MIN_SR or base_cost_bps <= 0:
        cost_results = {}
        skip_reason = []
        if sr_base < COST_STRESS_MIN_SR:
            skip_reason.append(f"SR={sr_base:.3f} < {COST_STRESS_MIN_SR}")
        if base_cost_bps <= 0:
            skip_reason.append(f"base_cost_bps={base_cost_bps} <= 0")
        for label in ["cost_2x", "cost_3x"]:
            cost_results[label] = {"verdict": "SKIP", "skip_reason": "; ".join(skip_reason)}
        return cost_results

    daily_vol = float(np.std(returns, ddof=1))
    median_vol = float(np.median(np.abs(returns))) if np.any(returns != 0) else daily_vol
    if median_vol < 1e-10:
        median_vol = daily_vol if daily_vol > 1e-10 else 1e-10
    base_cost_daily = base_cost_bps / 10000.0

    cost_results = {}
    for stress_factor, label in [(2.0, "cost_2x"), (3.0, "cost_3x")]:
        extra_cost = (stress_factor - 1.0) * base_cost_daily
        vol_ratio_series = np.abs(returns) / median_vol
        vol_ratio_series = np.clip(vol_ratio_series, 0, 10)
        stressed = returns - extra_cost * vol_ratio_series
        sr_stressed = _exec_sharpe(stressed, periods_per_year)
        retention = _exec_retention(sr_base, sr_stressed)
        if sr_stressed is None:
            verdict = "SKIP"
        elif sr_base > 0 and sr_stressed <= 0:
            verdict = "FAIL"
        elif sr_base > 0 and retention is not None and retention < 0.5:
            verdict = "WARN"
        else:
            verdict = "PASS"
        cost_results[label] = {
            "sr_base": round(sr_base, 4),
            "sr_stressed": round(sr_stressed, 4) if sr_stressed is not None else None,
            "sr_retention": round(retention, 4) if retention is not None else None,
            "extra_cost_bps": round(extra_cost * 10000, 2),
            "verdict": verdict,
        }
    return cost_results


def _exec_overall_verdict(delay_results: dict, cost_results: dict) -> tuple:
    """Aggregate overall verdict + recommendation. Returns (overall, recommendation)."""
    all_verdicts = (
        [v["verdict"] for v in delay_results.values()] +
        [v["verdict"] for v in cost_results.values()]
    )
    testable = [v for v in all_verdicts if v != "SKIP"]
    if any(v == "FAIL" for v in testable):
        overall = "FAIL"
    elif any(v == "WARN" for v in testable):
        overall = "WARN"
    elif not testable:
        overall = "SKIP"
    else:
        overall = "PASS"

    rec_parts = []
    d1 = delay_results.get("delay_1bar", {})
    if d1.get("verdict") in ("WARN", "FAIL"):
        rec_parts.append(
            f"1-bar delay risk (lag_autocorr={d1.get('lag_autocorr')}): "
            f"negative autocorrelation means delay inverts the edge. "
            f"Reversion-type edges are timing-sensitive."
        )
    c2 = cost_results.get("cost_2x", {})
    c3 = cost_results.get("cost_3x", {})
    if c2.get("verdict") in ("WARN", "FAIL") or c3.get("verdict") in ("WARN", "FAIL"):
        worst = c3 if c3.get("verdict") in ("WARN", "FAIL") else c2
        rec_parts.append(
            f"Cost stress kills Sharpe (retention={worst.get('sr_retention')}): "
            f"base cost assumption is too optimistic, check real fee+funding."
        )
    return overall, rec_parts


def execution_realism_check(returns: np.ndarray,
                            strategy_type: str = "",
                            periods_per_year: int = 365,
                            base_cost_bps: float = 5.0) -> dict:
    """Stress-test strategy PnL under execution delay and inflated cost.

    REAL framework:
      E (Execution realism): does the edge survive when fills are delayed by
         1 bar / 2 bars?  Many intraday/momentum edges evaporate when you can't
         fill at the signal bar's close.
      A (Account for cost): does the edge survive when cost is doubled /
         tripled?  Backtests often use optimistic bps; real fee + funding +
         slippage can be 2-3× higher, especially for perp strategies.

    Philosophy (Calvin podcast 2026-06):
      "If your backtest passes but dies the moment you add a 1-bar delay or
       double the cost, you don't have a strategy — you have a latency arb
       that you can't capture."

    The check does NOT recompute fills from raw order book data (that's the
    job of a full execution simulator).  Instead it applies a conservative
    proxy: lag-N autocorrelation for delay sensitivity, and vol-scaled cost
    inflation for cost stress.

    **Known limitation (P2, acknowledged):**
    Autocorrelation cannot detect same-bar timing edges (e.g. strategies that
    must fill at the signal bar's close).  A PASS on E dimension does NOT
    guarantee the edge survives delay — it only means no reversion-like
    structure was detected.  Full execution delay simulation requires
    signal/position data, which is not available from returns alone.

    Args:
        returns: 1D array of daily returns (already net of base cost).
        strategy_type: "momentum", "reversion", or "" (unknown).
        periods_per_year: annualization factor (365 for crypto daily).
        base_cost_bps: assumed base cost per trade in basis points.
            Must be > 0; if 0, A dimension is skipped (no-op guard).

    Returns:
        dict with:
          - delay_1bar: {lag_autocorr, verdict}
          - delay_2bar: same structure
          - cost_2x: {sr_base, sr_stressed, sr_retention, extra_cost_bps, verdict}
          - cost_3x: same structure
          - overall_verdict: PASS / WARN / FAIL / SKIP
          - recommendation: actionable text
    """
    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    n = len(returns)
    if n < 90:
        return {"error": f"Insufficient data: n={n} < 90"}

    returns_std = float(np.std(returns, ddof=1))
    if returns_std < 1e-10:
        return {"error": f"Near-zero variance (std={returns_std:.2e}): "
                "Sharpe is undefined, cost stress is not meaningful."}

    rets_series = pd.Series(returns)
    if empyrical is None:  # [止血] empyrical missing — sr_base=0 triggers cost SKIP
        sr_base = 0.0
    else:
        sr_base = float(empyrical.sharpe_ratio(
            rets_series, period='daily', annualization=periods_per_year))
        if math.isnan(sr_base):
            sr_base = 0.0

    # E: Delay sensitivity
    delay_results = _exec_delay_test(returns, n, strategy_type)

    # A: Cost stress test
    cost_results = _exec_cost_stress(returns, sr_base, base_cost_bps, periods_per_year)

    # Overall verdict
    overall, rec_parts = _exec_overall_verdict(delay_results, cost_results)
    if not rec_parts:
        rec_parts.append(
            f"Edge survives delay + cost stress (base SR={sr_base:.2f}). "
            f"Execution realism is acceptable."
        )

    return {
        "delay_1bar": delay_results.get("delay_1bar", {}),
        "delay_2bar": delay_results.get("delay_2bar", {}),
        "cost_2x": cost_results.get("cost_2x", {}),
        "cost_3x": cost_results.get("cost_3x", {}),
        "overall_verdict": overall,
        "recommendation": " ".join(rec_parts),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Multi-objective PBO + Calmar (Balaena #1) and per-trade edge-vs-cost (Balaena #7)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_calmar(returns: np.ndarray, periods_per_year: int = 365) -> float:
    """Calmar ratio = annualized return / |max drawdown|.

    A single-metric PBO gate misses drawdown fragility — a strategy can have
    stable Sharpe but deep drawdowns. Calvin (Balaena podcast): combine Sharpe
    and Calmar as co-gates rather than swapping one for the other.
    """
    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    if len(returns) < 2:
        return 0.0
    annualized_return = float(np.mean(returns) * periods_per_year)
    cumulative = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_dd = float(drawdown.min())
    if max_dd >= 0:
        return float('inf') if annualized_return > 0 else 0.0
    return annualized_return / abs(max_dd)


def multi_objective_pbo_calmar(returns_matrix: np.ndarray, n_bins: int = 16,
                                calmar_floor: float = 0.3,
                                periods_per_year: int = 365) -> dict:
    """PBO AND median-OOS-Calmar dual gate (Balaena #1).

    Runs the same CSCV IS/OOS splits as pbo(), but for each split also computes
    Calmar on the IS-best column's OOS returns. Pass requires BOTH:
      - PBO < 0.5 (Sharpe-robust)
      - median(OOS Calmar) >= calmar_floor (drawdown-robust)
    """
    from itertools import combinations
    T, N = returns_matrix.shape
    if T < n_bins * 4:
        return {"pbo": None, "error": f"Insufficient data: T={T} < n_bins*4={n_bins*4}"}
    if N < 2:
        return {"pbo": None, "error": f"Need >=2 parameter combos, got N={N}"}

    R = returns_matrix.copy()
    bin_size = T // n_bins
    R = R[:bin_size * n_bins]
    bins = [R[i * bin_size:(i + 1) * bin_size] for i in range(n_bins)]

    half = n_bins // 2
    oos_ranks_of_is_best = []
    oos_calmars_of_is_best = []

    for is_indices in combinations(range(n_bins), half):
        oos_indices = [i for i in range(n_bins) if i not in is_indices]
        is_returns = np.vstack([bins[i] for i in is_indices])
        oos_returns = np.vstack([bins[i] for i in oos_indices])

        is_sr = is_returns.mean(axis=0) / (is_returns.std(axis=0, ddof=1) + 1e-10)
        is_best_idx = np.argmax(is_sr)

        oos_sr = oos_returns.mean(axis=0) / (oos_returns.std(axis=0, ddof=1) + 1e-10)
        oos_rank = sp_stats.rankdata(oos_sr)[is_best_idx] - 1
        oos_ranks_of_is_best.append(oos_rank)

        oos_best_returns = oos_returns[:, is_best_idx]
        oos_calmars_of_is_best.append(compute_calmar(oos_best_returns, periods_per_year))

    oos_ranks = np.array(oos_ranks_of_is_best)
    median_rank = (N - 1) / 2.0
    pbo_value = np.mean(oos_ranks <= median_rank)

    oos_calmars = np.array(oos_calmars_of_is_best)
    median_calmar = float(np.median(oos_calmars))

    pbo_pass = pbo_value < 0.5
    calmar_pass = median_calmar >= calmar_floor
    overall_pass = pbo_pass and calmar_pass

    if pbo_pass and not calmar_pass:
        verdict = "BLOCK"
        reason = f"Sharpe-robust but drawdown-fragile (Calmar={median_calmar:.3f} < floor={calmar_floor})"
    elif not pbo_pass:
        verdict = "BLOCK"
        reason = f"PBO={pbo_value:.4f} >= 0.5 (Sharpe overfit)"
    else:
        verdict = "PASS"
        reason = f"PBO={pbo_value:.4f}, Calmar={median_calmar:.3f}"

    return {
        "pbo": round(float(pbo_value), 4),
        "median_oos_calmar": round(median_calmar, 4),
        "calmar_floor": calmar_floor,
        "pbo_pass": pbo_pass,
        "calmar_pass": calmar_pass,
        "verdict": verdict,
        "reason": reason,
        "n_combinations": len(oos_ranks),
        "oos_calmar_distribution": {
            "min": round(float(oos_calmars.min()), 4),
            "max": round(float(oos_calmars.max()), 4),
            "std": round(float(oos_calmars.std()), 4),
        },
    }


def per_trade_edge_vs_cost(expected_edge_bps, realized_cost_bps,
                            threshold: float = 1.5, min_trades: int = 30) -> dict:
    """Per-trade edge vs cost gate for high-turnover strategies (Balaena #7).

    Calvin: "频率越高回报越高，但前提是每笔 edge > 滑点"
    Anson (QTS EP3): "要能维持赚钱的高换手才算数"

    Pass requires median(edge_bps) > threshold * median(cost_bps) with enough
    trades for statistical significance. Without this, a high-turnover strategy
    can pass aggregate Sharpe checks while burning money per trade.
    """
    expected_edge_bps = np.asarray(expected_edge_bps, dtype=float)
    realized_cost_bps = np.asarray(realized_cost_bps, dtype=float)
    expected_edge_bps = expected_edge_bps[~np.isnan(expected_edge_bps)]
    realized_cost_bps = realized_cost_bps[~np.isnan(realized_cost_bps)]

    n_trades = min(len(expected_edge_bps), len(realized_cost_bps))
    if n_trades < min_trades:
        return {"pass": False, "reason": f"insufficient trades ({n_trades} < {min_trades})",
                "n_trades": n_trades}

    median_edge = float(np.median(expected_edge_bps))
    median_cost = float(np.median(realized_cost_bps))
    ratio = median_edge / median_cost if median_cost > 0 else float('inf')
    passed = ratio > threshold

    return {
        "pass": passed,
        "median_edge_bps": round(median_edge, 4),
        "median_cost_bps": round(median_cost, 4),
        "ratio": round(ratio, 4),
        "threshold": threshold,
        "n_trades": n_trades,
        "reason": "pass" if passed else f"edge/cost ratio {ratio:.3f} <= threshold {threshold}",
    }


# falsify_quant.py is a pure library. The sole verdict/exit-code path is
# quant_falsify_gate.py main(). Import this module for functions only.
