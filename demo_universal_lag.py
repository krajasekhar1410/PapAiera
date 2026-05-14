# -*- coding: utf-8 -*-
"""
Demo: Universal Lag Detection — ANY Input to ANY Output
=======================================================

Shows that PapAiEra's find_lag() works for ANY process parameters,
not just pulp mill specific variables.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
from pap_ai_era.papermaking.dtw_lag import find_lag, find_multi_lag

np.random.seed(42)

print("=" * 70)
print("  PapAiEra - Universal Lag Detection Tool")
print("  Works for ANY input parameter to ANY output parameter")
print("=" * 70)

# =====================================================================
# EXAMPLE 1: Digester Temperature -> Kappa Number (inverse relationship)
# =====================================================================
print("\n[1] Digester Cook Temperature -> Kappa Number")
n = 800
t = np.arange(n)
TRUE_LAG = 35  # minutes

cook_temp = 165.0 + 3.0 * np.sin(0.03 * t) + 0.5 * np.random.randn(n)
# Inverse relationship: higher temp -> lower kappa, with lag
kappa = 28.0 - 2.0 * np.sin(0.03 * (t - TRUE_LAG)) + 0.3 * np.random.randn(n)

result = find_lag(cook_temp, kappa, time_interval=1.0, time_unit='minutes',
                  max_lag=80,
                  input_name='Cook Temperature', output_name='Kappa Number')

print(f"    True lag: {TRUE_LAG} min")
print(f"    Found:    {result['lag_time']:.1f} {result['lag_unit']}  "
      f"[Confidence: {result['confidence']}]")

# =====================================================================
# EXAMPLE 2: Refiner Energy -> Freeness (inverse: more energy = lower CSF)
# =====================================================================
print("\n[2] Refiner Specific Energy -> Freeness (CSF)")
TRUE_LAG = 12

refiner_energy = 120 + 15 * np.sin(0.05 * t) + 2 * np.random.randn(n)
freeness = 450 - 20 * np.sin(0.05 * (t - TRUE_LAG)) + 3 * np.random.randn(n)

result = find_lag(refiner_energy, freeness, time_interval=1.0, time_unit='minutes',
                  max_lag=50,
                  input_name='Refiner Energy', output_name='CSF Freeness')

print(f"    True lag: {TRUE_LAG} min")
print(f"    Found:    {result['lag_time']:.1f} {result['lag_unit']}  "
      f"[Confidence: {result['confidence']}]")

# =====================================================================
# EXAMPLE 3: Steam Pressure -> Dryer Surface Temperature (direct)
# =====================================================================
print("\n[3] Steam Pressure -> Dryer Surface Temperature")
TRUE_LAG = 8

steam_pressure = 4.5 + 0.3 * np.sin(0.08 * t) + 0.05 * np.random.randn(n)
dryer_temp = 130 + 5.0 * np.sin(0.08 * (t - TRUE_LAG)) + 0.5 * np.random.randn(n)

result = find_lag(steam_pressure, dryer_temp, time_interval=30.0, time_unit='seconds',
                  max_lag=40,
                  input_name='Steam Pressure', output_name='Dryer Temp')

print(f"    True lag: {TRUE_LAG * 30} seconds ({TRUE_LAG} samples)")
print(f"    Found:    {result['lag_time']:.0f} {result['lag_unit']}  "
      f"[Confidence: {result['confidence']}]")

# =====================================================================
# EXAMPLE 4: Chemical Dosing -> Retention (Wet-End)
# =====================================================================
print("\n[4] PAC Dosing -> First Pass Retention")
TRUE_LAG = 5

pac_dose = 6.0 + 1.5 * np.sin(0.1 * t) + 0.2 * np.random.randn(n)
retention = 82 + 3.0 * np.sin(0.1 * (t - TRUE_LAG)) + 0.3 * np.random.randn(n)

result = find_lag(pac_dose, retention, time_interval=1.0, time_unit='minutes',
                  max_lag=30,
                  input_name='PAC Dose', output_name='First Pass Retention')

print(f"    True lag: {TRUE_LAG} min")
print(f"    Found:    {result['lag_time']:.1f} {result['lag_unit']}  "
      f"[Confidence: {result['confidence']}]")

# =====================================================================
# EXAMPLE 5: Feed Flow Rate -> Reactor Outlet Concentration
# =====================================================================
print("\n[5] Feed Flow -> Reactor Outlet Concentration (non-pulp example)")
TRUE_LAG = 22

feed_flow = 50 + 5 * np.sin(0.04 * t) + 0.8 * np.random.randn(n)
outlet_conc = 320 + 15 * np.sin(0.04 * (t - TRUE_LAG)) + 2 * np.random.randn(n)

result = find_lag(feed_flow, outlet_conc, time_interval=1.0, time_unit='minutes',
                  max_lag=60,
                  input_name='Feed Flow', output_name='Reactor Outlet Conc')

print(f"    True lag: {TRUE_LAG} min")
print(f"    Found:    {result['lag_time']:.1f} {result['lag_unit']}  "
      f"[Confidence: {result['confidence']}]")

# =====================================================================
# EXAMPLE 6: Multi-Variable — Full Process Audit
# =====================================================================
print("\n" + "=" * 70)
print("[6] MULTI-VARIABLE: Any Process DataFrame")
print("=" * 70)

df = pd.DataFrame({
    'steam_pressure': steam_pressure,
    'pac_dosing': pac_dose,
    'feed_flow': feed_flow,
    'dryer_temperature': dryer_temp,
    'retention_pct': retention,
    'outlet_conc': outlet_conc,
})

results = find_multi_lag(
    data=df,
    input_columns=['steam_pressure', 'pac_dosing', 'feed_flow'],
    output_columns=['dryer_temperature', 'retention_pct', 'outlet_conc'],
    time_interval=1.0,
    time_unit='minutes',
    max_lag=60,
)

print("\n--- Full Lag Matrix ---")
print(results.to_string(index=False))

# =====================================================================
# EXAMPLE 7: Simplest possible usage — just 2 arrays
# =====================================================================
print("\n" + "=" * 70)
print("[7] SIMPLEST USAGE: Just pass two arrays")
print("=" * 70)
print("    >>> from pap_ai_era.papermaking import find_lag")
print("    >>> result = find_lag(my_input, my_output)")

signal_a = np.sin(0.04 * t) + 0.1 * np.random.randn(n)
signal_b = np.sin(0.04 * (t - 25)) + 0.1 * np.random.randn(n)

result = find_lag(signal_a, signal_b, max_lag=60)
print(f"\n    True lag: 25 samples")
print(f"    Found:    {result['lag_samples']} samples  "
      f"[Confidence: {result['confidence']}]")

print("\n" + "=" * 70)
print("  Universal lag detection works for ANY process!")
print("=" * 70)
