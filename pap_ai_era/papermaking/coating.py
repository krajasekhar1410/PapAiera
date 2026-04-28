"""
Coating and Finishing Module
Focuses on paper surface treatment, coating colours, and finishing efficiency.
"""

def coating_colour_loss(colour_to_effluent_kg, total_colour_applied_kg):
    """
    Calculate the percentage of coating colour lost to effluent.
    BAT aims to minimize this loss via recovery systems (like ultrafiltration)
    to < 1-2%.
    """
    if total_colour_applied_kg <= 0:
        return 0.0
    loss_pct = (colour_to_effluent_kg / total_colour_applied_kg) * 100.0
    return {
        "loss_pct": loss_pct,
        "is_bat_compliant": loss_pct <= 2.0
    }

def coating_solids_recovery_efficiency(solids_recovered, solids_in_wash_water):
    """
    Efficiency of the ultrafiltration or settling systems recovering pigments and binders
    from coating station wash waters.
    """
    if solids_in_wash_water <= 0:
        return 0.0
    return (solids_recovered / solids_in_wash_water) * 100.0

def specific_water_coating(water_used_m3, coated_paper_produced_tonnes):
    """
    Specific fresh water used merely for the coating/kitchen section.
    """
    if coated_paper_produced_tonnes <= 0:
        return 0.0
    return water_used_m3 / coated_paper_produced_tonnes
