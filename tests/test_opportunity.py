import pandas as pd
import pytest
from src.opportunity import benchmark_rate, opportunity

SEG = pd.DataFrame({
    "dimension": ["device", "device"], "segment": ["desktop", "mobile"],
    "n_view": [1000, 1000], "n_cart": [200, 150],
    "n_checkout": [100, 80], "n_purchase": [40, 20],
    "aov_usd": [100.0, 80.0],
})

def test_benchmark_is_pooled_rate():
    # (40 + 20) / (100 + 80)
    assert benchmark_rate(SEG, "device", "checkout_to_purchase") == pytest.approx(1 / 3)

def test_checkout_gap():
    # gap = 1/3 - 20/80 = 0.0833; x 80 checkouts x 0.5 closure = 3.33 orders; x 80 AOV = 266.67
    bench = benchmark_rate(SEG, "device", "checkout_to_purchase")
    o = opportunity(SEG, "device", "mobile", "checkout_to_purchase", bench, closure=0.5)
    assert o["extra_orders"] == pytest.approx(10 / 3)
    assert o["revenue_window_usd"] == pytest.approx(800 / 3)

def test_upstream_gap_uses_downstream_rate():
    # bench = 350/2000 = 0.175; gap = 0.025; x 1000 x 0.5 = 12.5 carts; x 20/150 = 1.667 orders; x 80 = 133.33
    bench = benchmark_rate(SEG, "device", "view_to_cart")
    o = opportunity(SEG, "device", "mobile", "view_to_cart", bench, closure=0.5)
    assert o["revenue_window_usd"] == pytest.approx(400 / 3)

def test_no_opportunity_when_above_benchmark():
    bench = benchmark_rate(SEG, "device", "checkout_to_purchase")
    o = opportunity(SEG, "device", "desktop", "checkout_to_purchase", bench)
    assert o["revenue_window_usd"] == 0