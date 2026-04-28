"""
Bleaching & Delignification Module
Calculations for ECF/TCF bleaching sequences and washing efficiency.
"""

def oxygen_delignification_efficiency(kappa_in, kappa_out):
    """
    Reduction in Kappa number across the O2 delignification stage.
    BAT recommends extended O2 delignification to reduce bleaching chemical consumption.
    Reduction is generally 40-50% for softwoods.
    """
    if kappa_in <= 0:
        return 0.0
    return ((kappa_in - kappa_out) / kappa_in) * 100.0

def theoretical_aox_generation(active_chlorine_multiple, kappa_to_bleach):
    """
    Empirical calculation estimating AOX (kg/t) generation based on chlorine dioxide usage.
    Generally, 1 kg of ClO2 generates roughly 0.1 kg AOX before biological treatment.
    """
    # Active Chlorine Multiple (ACM) * Kappa usually gives kg active Cl / tonne
    active_cl_charge = active_chlorine_multiple * kappa_to_bleach
    return active_cl_charge * 0.1 # approximate conversion factor to AOX

def wash_press_efficiency(dissolved_solids_in, dissolved_solids_out):
    """
    Displacement or pressing efficiency in brown stock washing.
    Critical for minimizing carry-over of COD into the bleach plant.
    """
    if dissolved_solids_in <= 0:
        return 0.0
    return ((dissolved_solids_in - dissolved_solids_out) / dissolved_solids_in) * 100.0
