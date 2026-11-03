"""Run with:  python -m pytest"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from analyze import month_labels, trend_to_monthly


def test_trend_to_monthly_keeps_12_month_total():
    monthly = trend_to_monthly(1000, [0.5] * 6 + [1.0] * 6)
    assert round(sum(monthly)) == 12000          # 12 x average
    assert monthly[-1] == 2 * monthly[0]          # follows the trend shape


def test_zero_volume_or_trend():
    assert trend_to_monthly(0, [1] * 12) == [0.0] * 12
    assert trend_to_monthly(500, [0] * 12) == [0.0] * 12


def test_month_labels():
    labels = month_labels("2026-07")
    assert labels[0] == "2025-08" and labels[-1] == "2026-07" and len(labels) == 12
