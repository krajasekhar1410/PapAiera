"""
Recycled Fibre (RCF) Module
For calculations related to recovered paper processing, with and without deinking.
"""

def deinking_yield(ink_removed, total_ink, fibre_loss):
    """
    Calculate the yield and efficiency of the deinking process (flotation/washing).
    A high-quality deinking process minimizes fiber loss while maximizing ink removal.
    """
    ink_removal_efficiency = (ink_removed / total_ink) * 100 if total_ink > 0 else 0
    return {
        "ink_removal_efficiency_pct": ink_removal_efficiency,
        "fibre_loss_pct": fibre_loss
    }

def rcf_rejects_rate(rejects_mass, input_rcf_mass):
    """
    Calculate the percentage of rejects (plastics, metals, non-fibrous materials).
    RCF processing generates significant solid waste that requires management (BAT).
    """
    if input_rcf_mass <= 0:
        return 0.0
    return (rejects_mass / input_rcf_mass) * 100.0

def specific_energy_rcf(electricity_used, pulp_produced, grade="deinked"):
    """
    Compare specific energy consumption for RCF processing against BAT.
    grade: 'packaging', 'newsprint', 'tissue'.
    """
    spec_energy = electricity_used / pulp_produced
    if grade == "packaging":
        bat_target = 0.2  # MWh/t roughly
    elif grade == "newsprint":
        bat_target = 0.4
    elif grade == "tissue":
        bat_target = 0.5
    else:
        bat_target = 0.3
        
    return {
        "specific_energy_mwh_t": spec_energy,
        "meets_bat": spec_energy <= bat_target
    }
