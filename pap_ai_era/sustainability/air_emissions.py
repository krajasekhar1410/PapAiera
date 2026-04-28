"""
Air Emissions Module
Detailed calculations for to-air emissions from various pulp & paper sources including
Recovery Boilers, Lime Kilns, and NCG (Non-Condensable Gases) incineration.
"""

def total_reduced_sulphur(recovery_boiler_trs, lime_kiln_trs, ncg_trs, production_admt):
    """
    Calculates Total Reduced Sulphur (TRS) emissions per ADt (Air Dry metric tonne).
    BAT heavily focuses on collecting strong and weak NCGs to minimize odorous TRS emissions.
    Target: < 0.1 - 0.2 kg S/ADt.
    """
    if production_admt <= 0:
        return 0.0
    return (recovery_boiler_trs + lime_kiln_trs + ncg_trs) / production_admt

def nox_emissions_factor(nox_kg, fuel_energy_gj):
    """
    NOx emissions relative to energy input, critical for Auxiliary and Recovery Boilers.
    Expressed in mg/Nm3 or kg/GJ. This function outputs kg/GJ.
    """
    if fuel_energy_gj <= 0:
        return 0.0
    return nox_kg / fuel_energy_gj

def dust_emissions(flow_rate_nm3_h, dust_conc_mg_nm3, operating_hours, production_admt):
    """
    Particulate/Dust emissions per tonne of product.
    Calculated using volumetric flow, concentration from electrostatic precipitators (ESP), and time.
    BAT expects < 0.2 - 0.5 kg/ADt for recovery boilers.
    """
    if production_admt <= 0:
        return 0.0
    total_dust_kg = (flow_rate_nm3_h * dust_conc_mg_nm3 * operating_hours) / 1_000_000.0
    return total_dust_kg / production_admt

def so2_emissions_kg_adt(so2_kg, production_admt):
    """
    Sulphur dioxide emissions per tonne.
    Target depends on whether it's a Kraft (lower) or Sulphite (higher, though recovered) mill.
    """
    if production_admt <= 0:
        return 0.0
    return so2_kg / production_admt
