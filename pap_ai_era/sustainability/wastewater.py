"""
Wastewater Treatment Plant (WWTP) Module
Calculations for internal water loops and external biological/physico-chemical treatment efficiency.
"""

def wwtp_removal_efficiency(influent_conc, effluent_conc):
    """
    Calculates the removal efficiency for parameters like COD, BOD, TSS, and AOX.
    BAT for Biological WWTP expects BOD reduction > 90-95% and COD > 60-80%.
    """
    if influent_conc <= 0:
        return 0.0
    return ((influent_conc - effluent_conc) / influent_conc) * 100.0

def specific_effluent_volume(effluent_m3, cooling_water_m3, production_admt):
    """
    Calculates process wastewater volume (excluding clean cooling water as per BAT guidelines).
    BAT for bleached Kraft is 25-50 m3/ADt; for non-deinked paper 10-15 m3/ADt.
    """
    if production_admt <= 0:
        return 0.0
    net_process_water = effluent_m3 - cooling_water_m3
    return max(0, net_process_water) / production_admt

def nitrogen_phosphorus_discharge(tot_n_kg, tot_p_kg, production_admt):
    """
    BAT requires monitoring and limiting nutrient discharge (N and P),
    which are often added to WWTP for biological health but must not be over-dosed.
    """
    if production_admt <= 0:
        return {"N_kg_ADt": 0.0, "P_kg_ADt": 0.0}
    return {
        "N_kg_ADt": tot_n_kg / production_admt,
        "P_kg_ADt": tot_p_kg / production_admt
    }
