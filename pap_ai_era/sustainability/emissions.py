"""
Emissions & Sustainability Module
Emissions to Air and Water based on BREF standards.
"""

def specific_cod_load(cod_mass_kg, product_mass_tonnes):
    """
    Calculate Chemical Oxygen Demand (COD) load per air-dry tonne of product.
    BAT aims for 8 - 20 kg COD/ADt for bleached Kraft, lower for other grades.
    """
    if product_mass_tonnes <= 0:
        return 0.0
    return cod_mass_kg / product_mass_tonnes

def specific_bod_load(bod_mass_kg, product_mass_tonnes):
    """
    Calculate Biological Oxygen Demand (BOD) load per air-dry tonne of product.
    BAT targets are typically < 0.5 - 1.5 kg BOD5/ADt.
    """
    if product_mass_tonnes <= 0:
        return 0.0
    return bod_mass_kg / product_mass_tonnes

def specific_tss_load(tss_mass_kg, product_mass_tonnes):
    """
    Calculate Total Suspended Solids (TSS) load per air-dry tonne of product.
    BAT targets < 0.5 - 1.5 kg TSS/ADt.
    """
    if product_mass_tonnes <= 0:
        return 0.0
    return tss_mass_kg / product_mass_tonnes

def aox_emissions(aox_kg, bleached_pulp_tonnes):
    """
    Adsorbable Organically bound Halogens (AOX) for ECF/TCF bleaching.
    BAT for ECF (Elemental Chlorine Free) is <= 0.2 kg AOX/ADt.
    """
    if bleached_pulp_tonnes <= 0:
        return 0.0
    return aox_kg / bleached_pulp_tonnes

def evaluate_water_effluent_bat(cod_spec, bod_spec, tss_spec, aox_spec=None):
    """
    Returns a dictionary of boolean compliance flags for water emissions.
    Standardized roughly around Bleached Kraft BAT limits.
    """
    return {
        "COD_compliant": cod_spec <= 20.0,
        "BOD_compliant": bod_spec <= 1.5,
        "TSS_compliant": tss_spec <= 1.5,
        "AOX_compliant": True if aox_spec is None else aox_spec <= 0.2
    }
