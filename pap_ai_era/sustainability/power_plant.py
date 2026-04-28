"""
Power Plant & Cogeneration (CHP) Module
For calculations related to the Turbine Generator (TG), Boiler Fuel, and Steam Generation.
"""

def boiler_thermal_efficiency(steam_energy_gj, fuel_energy_input_gj):
    """
    Evaluates the basic thermal efficiency of the Multi-Fuel or Recovery Boiler.
    Target > 80-85%.
    """
    if fuel_energy_input_gj <= 0:
        return 0.0
    return (steam_energy_gj / fuel_energy_input_gj) * 100.0

def tg_extraction_efficiency(high_pressure_flow, med_pressure_ext, low_pressure_ext, power_generated_mw):
    """
    Evaluates power generation efficiency per ton of steam dropped across the TG.
    """
    total_drop = high_pressure_flow - (med_pressure_ext + low_pressure_ext)
    if total_drop <= 0:
        return 0.0
    # MWh per ton of condensed/extracted steam
    return power_generated_mw / total_drop
