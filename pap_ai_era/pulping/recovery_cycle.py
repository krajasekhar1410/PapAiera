"""
Chemical Recovery Cycle Module
Advanced parameters for the Kraft/Sulphite chemical recovery loop.
"""

def causticizing_efficiency(naoh_conc, na2co3_conc):
    """
    Measures the efficiency of converting Sodium Carbonate (green liquor) 
    back to Sodium Hydroxide (white liquor) using lime.
    Target is typically ~80-85%.
    Concentrations should be based on Na2O equivalent.
    """
    total_alkali = naoh_conc + na2co3_conc
    if total_alkali <= 0:
        return 0.0
    return (naoh_conc / total_alkali) * 100.0

def lime_kiln_specific_energy(fuel_energy_gj, lime_produced_tonnes):
    """
    Energy consumed in the lime kiln per tonne of reburned lime (CaO).
    BAT is typically between 5.5 to 7.5 GJ/t of lime.
    """
    if lime_produced_tonnes <= 0:
        return 0.0
    return fuel_energy_gj / lime_produced_tonnes

def evaporator_steam_economy(water_evaporated_tonnes, steam_used_tonnes):
    """
    Multiple-effect evaporators steam economy.
    Modern 6- or 7-effect evaporators achieve economies of 5.0 to 6.5 t_water/t_steam.
    """
    if steam_used_tonnes <= 0:
        return 0.0
    return water_evaporated_tonnes / steam_used_tonnes

def reduction_efficiency_recovery_boiler(na2s_conc, na2so4_conc):
    """
    Efficiency of the lower furnace in the recovery boiler converting sulphate back to sulphide.
    Target > 90-95%. Concentrations based on Na2O or molar equivalents.
    """
    total_sulphur_salt = na2s_conc + na2so4_conc
    if total_sulphur_salt <= 0:
        return 0.0
    return (na2s_conc / total_sulphur_salt) * 100.0
