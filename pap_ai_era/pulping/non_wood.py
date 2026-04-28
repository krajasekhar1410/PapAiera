"""
Non-Wood Pulping Module (e.g., Bagasse, Straw, Bamboo)
Calculations specialized for non-wood fibers, which have unique characteristics
like high silica content and require specific preparation (depithing).
"""

def depithing_efficiency(pith_removed_kg, total_initial_pith_kg):
    """
    Bagasse requires depithing before pulping to reduce chemical consumption
    and improve drainage on the paper machine.
    Efficiency targets are typically > 70-80%.
    """
    if total_initial_pith_kg <= 0:
        return 0.0
    return (pith_removed_kg / total_initial_pith_kg) * 100.0

def silica_load_black_liquor(silica_in_raw_material_kg, black_liquor_volume_m3):
    """
    Non-woods (especially straw and bagasse) have high silica (SiO2).
    Silica causes severe scaling in evaporators and complicates the lime kiln operation.
    Outputs silica concentration in kg/m3.
    """
    if black_liquor_volume_m3 <= 0:
        return 0.0
    return silica_in_raw_material_kg / black_liquor_volume_m3

def non_wood_yield(dry_pulp_produced, bone_dry_depithed_bagasse):
    """
    Pulp yield for non-woods. Bagasse chemical pulping yield is typically
    around 45 - 50% based on depithed material.
    """
    if bone_dry_depithed_bagasse <= 0:
        return 0.0
    return (dry_pulp_produced / bone_dry_depithed_bagasse) * 100.0
