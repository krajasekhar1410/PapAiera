"""
Mechanical & Chemi-Mechanical Pulping Module
Calculations for SGW, PGW, TMP, and CTMP processes.
"""

def specific_energy_refining(electricity_used_mwh, pulp_produced_tonnes, process_type="TMP"):
    """
    Specific energy consumption is the most critical KPI in mechanical pulping.
    Typical BAT ranges: TMP (1.8-3.2 MWh/t), Groundwood SGW/PGW (1.1-2.2 MWh/t), CTMP (1.5-3.0 MWh/t).
    """
    spec_energy = electricity_used_mwh / pulp_produced_tonnes
    
    bat_upper_limits = {
        "SGW": 2.2,
        "PGW": 2.2,
        "TMP": 3.2,
        "CTMP": 3.0
    }
    limit = bat_upper_limits.get(process_type.upper(), 3.0)
    
    return {
        "specific_energy_mwh_t": spec_energy,
        "is_bat_compliant": spec_energy <= limit
    }

def heat_recovery_efficiency(recovered_steam_gj, grinding_refining_energy_gj):
    """
    Calculate the percentage of refining energy recovered as useful heat.
    BAT suggests high-efficiency heat recovery, especially from TMP refiners,
    which can generate clean steam to be used in paper machine drying.
    """
    if grinding_refining_energy_gj <= 0:
        return 0.0
    return (recovered_steam_gj / grinding_refining_energy_gj) * 100.0

def mechanical_yield(dry_pulp_produced, dry_wood_charged, process_type="TMP"):
    """
    Mechanical pulping yields are very high compared to chemical pulping.
    Typical yield > 95% for TMP, ~90% for CTMP due to chemical pretreatment.
    """
    if dry_wood_charged <= 0:
        return 0.0
    calc_yield = (dry_pulp_produced / dry_wood_charged) * 100.0
    return {
        "yield_pct": calc_yield,
        "is_optimal": calc_yield > 90.0 if process_type == "CTMP" else calc_yield > 95.0
    }
