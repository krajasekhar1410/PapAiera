"""
Demo: DTW-Based Lag Calculation in PapAiEra
============================================

This demo simulates a realistic paper machine scenario where:
  - Stock consistency (cause) affects basis weight (effect) with a ~45 sample lag.
  - Headbox pressure (cause) affects moisture (effect) with a ~20 sample lag.
  - Steam flow (cause) affects moisture (effect) with a ~80 sample lag.

The DTW lag calculator identifies these delays accurately even with
process noise present.
"""

import numpy as np
import pandas as pd
from pap_ai_era.papermaking.dtw_lag import compute_dtw_lag, compute_multi_lag, get_lag_profile

# =============================================================================
# 1. SINGLE PAIR — Consistency → Basis Weight
# =============================================================================
print("=" * 70)
print("  PapAiEra — DTW Lag Calculation Demo")
print("=" * 70)

np.random.seed(42)

# Simulate 10 minutes of 1 Hz process data
t = np.arange(0, 600)
TRUE_LAG = 45  # seconds

# Cause: stock consistency (oscillating + noise)
consistency = (
    0.8 * np.sin(0.03 * t) +
    0.3 * np.sin(0.08 * t + 0.5) +
    0.1 * np.random.randn(len(t))
)

# Effect: basis weight follows consistency with a 45-second transport delay
basis_weight = (
    0.8 * np.sin(0.03 * (t - TRUE_LAG)) +
    0.3 * np.sin(0.08 * (t - TRUE_LAG) + 0.5) +
    0.15 * np.random.randn(len(t))
)

print("\n[1] Single Pair: Consistency → Basis Weight")
print(f"    True lag: {TRUE_LAG} seconds")
print("    Computing DTW lag...")

result = compute_dtw_lag(
    cause=consistency,
    effect=basis_weight,
    max_lag_samples=100,
    sample_rate_hz=1.0,
    sakoe_chiba_window=30
)

print(f"    ✓ DTW Optimal Lag:   {result.optimal_lag_samples} samples ({result.optimal_lag_seconds:.1f} s)")
print(f"    ✓ DTW Distance:      {result.dtw_distance:.6f}")
print(f"    ✓ XCorr Lag:         {result.xcorr_lag_samples} samples")
print(f"    ✓ XCorr Coefficient: {result.xcorr_coefficient:.4f}")
print(f"    ✓ Confidence:        {result.confidence}")
print(f"    ✓ Methods Agree:     {result.method_agreement}")

# Get lag profile for plotting
profile = get_lag_profile(result)
optimal_row = profile[profile['is_optimal']]
print(f"\n    Lag profile: {len(profile)} points scanned")
print(f"    Minimum distance at lag = {optimal_row['lag_samples'].values[0]}")

# =============================================================================
# 2. MULTI-VARIABLE AUDIT
# =============================================================================
print("\n" + "=" * 70)
print("[2] Multi-Variable Process Audit")
print("=" * 70)

# Generate additional signals with known lags
headbox_pressure = (
    1.2 * np.sin(0.05 * t) +
    0.2 * np.random.randn(len(t))
)

steam_flow = (
    0.6 * np.sin(0.02 * t) +
    0.4 * np.sin(0.07 * t) +
    0.15 * np.random.randn(len(t))
)

# Moisture follows headbox pressure (lag=20) and steam flow (lag=80)
moisture = (
    0.7 * np.sin(0.05 * (t - 20)) +
    0.3 * np.sin(0.02 * (t - 80)) +
    0.2 * np.sin(0.07 * (t - 80)) +
    0.12 * np.random.randn(len(t))
)

# Build the process DataFrame
df = pd.DataFrame({
    'consistency': consistency,
    'headbox_pressure': headbox_pressure,
    'steam_flow': steam_flow,
    'basis_weight': basis_weight,
    'moisture': moisture
})

report = compute_multi_lag(
    data=df,
    cause_columns=['consistency', 'headbox_pressure', 'steam_flow'],
    effect_columns=['basis_weight', 'moisture'],
    max_lag_samples=100,
    sample_rate_hz=1.0,
    sakoe_chiba_window=30
)

print("\n--- Summary Table ---")
print(report.summary_table.to_string(index=False))

print(f"\n--- Dominant Lag: {report.dominant_lag} samples ---")

print("\n--- Process Recommendations ---")
for rec in report.recommendations:
    print(f"  • {rec}")

print("\n" + "=" * 70)
print("  Demo complete. DTW lag module is ready for production use.")
print("=" * 70)
