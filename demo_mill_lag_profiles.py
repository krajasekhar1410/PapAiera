# -*- coding: utf-8 -*-
"""
Demo: Mill-Specific DTW Lag Profiles in PapAiEra
=================================================

Shows all 3 pre-built scenarios:
  1. Bleach Tower Inlet Brightness -> Board Brightness
  2. Tower pH -> Wet-End pH
  3. Stage-wise Viscosity -> Strength Properties (Tensile, Burst, Tear)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from pap_ai_era.papermaking.mill_lag_profiles import (
    MillScenario, run_mill_scenario, run_viscosity_strength_audit,
    simulate_mill_scenario, list_scenarios
)

print("=" * 72)
print("  PapAiEra - Mill-Specific DTW Lag Analysis Demo")
print("=" * 72)

# Show available scenarios
print("\n--- Available Mill Scenarios ---")
print(list_scenarios().to_string(index=False))

# =========================================================================
# SCENARIO 1: Bleach Tower Brightness -> Board Brightness
# =========================================================================
print("\n" + "=" * 72)
print("[1] BLEACH TOWER INLET BRIGHTNESS -> BOARD BRIGHTNESS")
print("=" * 72)

sim = simulate_mill_scenario(MillScenario.BLEACH_BRIGHTNESS, duration_hours=24.0)
print(f"    Simulated {len(sim['cause'])} data points ({24.0} hours at 1-min intervals)")
print(f"    True lag injected: {sim['true_lag_minutes']:.0f} minutes")

result1 = run_mill_scenario(
    MillScenario.BLEACH_BRIGHTNESS,
    cause=sim['cause'],
    effect=sim['effect'],
)
print(f"\n{result1.summary()}")

# =========================================================================
# SCENARIO 2: Tower pH -> Wet-End pH
# =========================================================================
print("\n" + "=" * 72)
print("[2] BLEACH TOWER pH -> WET-END pH")
print("=" * 72)

sim2 = simulate_mill_scenario(MillScenario.TOWER_PH_WETEND, duration_hours=24.0)
print(f"    Simulated {len(sim2['cause'])} data points")
print(f"    True lag injected: {sim2['true_lag_minutes']:.0f} minutes")

result2 = run_mill_scenario(
    MillScenario.TOWER_PH_WETEND,
    cause=sim2['cause'],
    effect=sim2['effect'],
)
print(f"\n{result2.summary()}")

# =========================================================================
# SCENARIO 3: Stage-wise Viscosity -> Strength Properties
# =========================================================================
print("\n" + "=" * 72)
print("[3] STAGE-WISE VISCOSITY -> STRENGTH PROPERTIES")
print("=" * 72)

sim3 = simulate_mill_scenario(
    MillScenario.VISCOSITY_STRENGTH,
    duration_hours=48.0,  # need longer data for 5-8 hour lags
    noise_level=0.08,
)
print(f"    Simulated {len(sim3['time_minutes'])} data points (48 hours)")
print(f"    True lags: D0={sim3['true_lags_minutes']['D0']:.0f} min, "
      f"EOP={sim3['true_lags_minutes']['EOP']:.0f} min, "
      f"D1={sim3['true_lags_minutes']['D1']:.0f} min")

report = run_viscosity_strength_audit(
    viscosity_signals=sim3['viscosity_signals'],
    strength_signals=sim3['strength_signals'],
)

print("\n--- Multi-Variable Summary Table ---")
print(report.summary_table.to_string(index=False))

print(f"\n--- Dominant Lag: {report.dominant_lag} samples ---")

print("\n--- Process Recommendations ---")
for rec in report.recommendations:
    print(f"  {rec}")

print("\n" + "=" * 72)
print("  All 3 mill scenarios completed successfully.")
print("=" * 72)
