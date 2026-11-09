import numpy as np
import pandas as pd
from src.stats import STEPS

WINDOW_DAYS = 92  # Nov 1, 2020 – Jan 31, 2021

# after passing a step, what share of sessions go on to purchase?
DOWNSTREAM = {
    "view_to_cart":         ("n_purchase", "n_cart"),
    "cart_to_checkout":     ("n_purchase", "n_checkout"),
    "checkout_to_purchase": None,
}

def _rate(row, num: str, den: str) -> float:
    return row[num] / row[den] if row[den] else np.nan

def benchmark_rate(seg: pd.DataFrame, dimension: str, step: str) -> float:
    """Overall rate for a step, pooled across every segment of the dimension."""
    d = seg[seg["dimension"] == dimension]
    num, den = STEPS[step]
    return d[num].sum() / d[den].sum()

def opportunity(seg: pd.DataFrame, dimension: str, segment: str, step: str,
                benchmark: float, closure: float = 0.5) -> dict:
    r = seg[seg["dimension"] == dimension].set_index("segment").loc[segment]
    num, den = STEPS[step]
    current = _rate(r, num, den)
    gap = max(benchmark - current, 0.0)
    downstream = 1.0 if DOWNSTREAM[step] is None else _rate(r, *DOWNSTREAM[step])
    extra_orders = r[den] * gap * closure * downstream
    revenue = extra_orders * r["aov_usd"]
    return {
        "dimension": dimension, "segment": segment, "step": step,
        "sessions_entering_step": int(r[den]),
        "current_rate": current, "benchmark_rate": benchmark, "gap_pts": gap * 100,
        "closure": closure, "extra_orders": extra_orders, "aov_usd": r["aov_usd"],
        "revenue_window_usd": revenue,
        "revenue_annualized_usd": revenue * 365 / WINDOW_DAYS,
    }

def scenarios(seg, dimension, segment, step, benchmark, closures=(0.25, 0.5, 1.0)) -> pd.DataFrame:
    """Low / base / high estimates for one gap."""
    return pd.DataFrame([opportunity(seg, dimension, segment, step, benchmark, c) for c in closures])