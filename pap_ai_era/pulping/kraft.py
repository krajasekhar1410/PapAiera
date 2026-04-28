"""
Kraft Pulping Module
For calculations related to the Chemical Kraft pulping process.
"""

def kappa_number(k_permanganate_consumed):
    """
    Estimates Kappa Number based on potassium permanganate consumed by the pulp.
    Kappa number represents the residual lignin content.
    """
    return k_permanganate_consumed * 1.0  # Simplified scaling factor

def chemical_recovery_efficiency(chemicals_recovered, chemicals_charged):
    """
    Calculate the recovery efficiency of the chemical recovery cycle.
    BAT for modern Kraft mills is > 95%.
    """
    if chemicals_charged <= 0:
        return 0.0
    return (chemicals_recovered / chemicals_charged) * 100.0

def black_liquor_solids_content(solids_mass, total_mass):
    """
    Calculate the percentage of dry solids in black liquor.
    High dry solids (> 75-80%) are characteristic of modern, efficient evaporation plants (BAT).
    """
    if total_mass <= 0:
        return 0.0
    return (solids_mass / total_mass) * 100.0

def pulping_yield(dry_pulp_produced, dry_wood_charged):
    """
    Calculate the overall pulp yield (kappa dependent).
    Typically 45% - 55% for Kraft pulping.
    """
    if dry_wood_charged <= 0:
        return 0.0
    return (dry_pulp_produced / dry_wood_charged) * 100.0

def check_kraft_bat_compliance(water_consumption, steam_consumption, elec_consumption):
    """
    Verifies if specific consumption aligns with general Kraft BAT norms.
    Units: Water (m3/ADt), Steam (GJ/ADt), Electricity (MWh/ADt).
    Reference: BREF 2015.
    """
    compliance = {
        'water': water_consumption <= 50, # general unbleached/bleached range 25-50 m3/ADt
        'steam': steam_consumption <= 14, # general range 10-14 GJ/ADt
        'electricity': elec_consumption <= 0.8 # general range 0.6-0.8 MWh/ADt
    }
    return compliance
