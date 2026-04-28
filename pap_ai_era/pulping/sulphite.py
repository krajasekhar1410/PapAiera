"""
Sulphite Pulping Module
For calculations related to Sulphite pulping processes (e.g., Magnesium, Calcium base).
"""

def chemical_recovery_efficiency_sulphite(so2_recovered, so2_charged, base_recovered, base_charged):
    """
    Calculate the recovery efficiency of SO2 and the alkaline base.
    BAT for dissolved solids, SO2, and base recovery is > 95% in modern Mg-sulphite mills.
    """
    if so2_charged <= 0 or base_charged <= 0:
        return 0.0
    so2_eff = (so2_recovered / so2_charged) * 100.0
    base_eff = (base_recovered / base_charged) * 100.0
    return {"so2_recovery_pct": so2_eff, "base_recovery_pct": base_eff}

def sulphite_yield(dry_pulp_produced, dry_wood_charged, is_dissolving_pulp=False):
    """
    Calculate pulping yield.
    Yield is heavily dependent on the type of pulp. Paper-grade sulphite yield is ~45-55%, 
    but dissolving pulp (viscose) yield is lower, ~35-40%.
    """
    if dry_wood_charged <= 0:
        return 0.0
    actual_yield = (dry_pulp_produced / dry_wood_charged) * 100.0
    target_yield = 40.0 if is_dissolving_pulp else 50.0  # approximate nominal targets
    return {
        "actual_yield_pct": actual_yield,
        "delta_from_nominal_target": actual_yield - target_yield
    }

def evaluate_sulphite_bat_compliance(water_consumption, steam_consumption, elec_consumption):
    """
    Verifies if specific consumption aligns with general Sulphite BAT norms.
    Sulphite mills typically use different benchmarks than Kraft.
    """
    return {
        'water_compliant': water_consumption <= 55, # general range for pulp 30-55 m3/ADt
        'steam_compliant': steam_consumption <= 18, 
        'electricity_compliant': elec_consumption <= 0.9 
    }
