import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.proportion import proportion_confint, proportions_ztest
from statsmodels.stats.multitest import multipletests

# step name -> (numerator column, denominator column) in funnel_by_segment
STEPS = {
    "view_to_cart":         ("n_cart", "n_view"),
    "cart_to_checkout":     ("n_checkout", "n_cart"),
    "checkout_to_purchase": ("n_purchase", "n_checkout"),
    "view_to_purchase":     ("n_purchase", "n_view"),
}

def wilson_ci(successes: int, trials: int, alpha: float = 0.05) -> tuple[float, float]:
    lo, hi = proportion_confint(successes, trials, alpha=alpha, method="wilson")
    return float(lo), float(hi)

def cohens_h(p1: float, p2: float) -> float:
    return 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))

def risk_ratio_ci(x1: int, n1: int, x0: int, n0: int, alpha: float = 0.05):
    """Ratio of rates (x1/n1) / (x0/n0) with a log-scale confidence interval."""
    rr = (x1 / n1) / (x0 / n0)
    se = np.sqrt(1 / x1 - 1 / n1 + 1 / x0 - 1 / n0)
    z = norm.ppf(1 - alpha / 2)
    return rr, rr * np.exp(-z * se), rr * np.exp(z * se)

def compare_to_baseline(seg: pd.DataFrame, dimension: str, baseline: str,
                        alpha: float = 0.05) -> pd.DataFrame:
    """Test every segment of one dimension against a baseline segment, at every funnel step."""
    d = seg[seg["dimension"] == dimension].set_index("segment")
    z = norm.ppf(1 - alpha / 2)
    rows = []
    for step, (num, den) in STEPS.items():
        b_x, b_n = int(d.loc[baseline, num]), int(d.loc[baseline, den])
        for segment, r in d.iterrows():
            if segment == baseline:
                continue
            x, n = int(r[num]), int(r[den])
            if n == 0 or b_n == 0:
                continue
            p1, p0 = x / n, b_x / b_n
            stat, p = proportions_ztest([x, b_x], [n, b_n])
            se = np.sqrt(p1 * (1 - p1) / n + p0 * (1 - p0) / b_n)
            lo, hi = wilson_ci(x, n, alpha)
            rows.append({
                "dimension": dimension, "step": step, "segment": segment, "baseline": baseline,
                "n": n, "baseline_n": b_n,
                "rate": p1, "rate_ci_low": lo, "rate_ci_high": hi, "baseline_rate": p0,
                "abs_diff": p1 - p0,
                "diff_ci_low": p1 - p0 - z * se, "diff_ci_high": p1 - p0 + z * se,
                "rel_diff": p1 / p0 - 1 if p0 > 0 else np.nan,
                "cohens_h": cohens_h(p1, p0),
                "z": stat, "p_value": p,
            })
    out = pd.DataFrame(rows)
    out["p_adj"] = multipletests(out["p_value"], method="fdr_bh")[1]
    out["significant"] = out["p_adj"] < alpha
    return out.sort_values(["step", "abs_diff"])