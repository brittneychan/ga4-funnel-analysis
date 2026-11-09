import pandas as pd
from src.stats import compare_to_baseline, wilson_ci, risk_ratio_ci

def _seg(purchases_mobile: int) -> pd.DataFrame:
    return pd.DataFrame({
        "dimension": ["device", "device"], "segment": ["desktop", "mobile"],
        "n_view": [1000, 1000], "n_cart": [200, 200],
        "n_checkout": [100, 100], "n_purchase": [40, purchases_mobile],
    })

def test_wilson_ci_brackets_rate():
    lo, hi = wilson_ci(50, 100)
    assert 0.39 < lo < 0.5 < hi < 0.61

def test_identical_segments_not_significant():
    res = compare_to_baseline(_seg(40), "device", "desktop")
    assert not res["significant"].any()

def test_large_gap_is_significant():
    res = compare_to_baseline(_seg(10), "device", "desktop")
    row = res[res["step"] == "checkout_to_purchase"].iloc[0]
    assert row["significant"] and row["abs_diff"] < 0

def test_risk_ratio():
    rr, lo, hi = risk_ratio_ci(60, 100, 30, 100)
    assert abs(rr - 2) < 1e-9 and lo < 2 < hi