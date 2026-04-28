"""
Wet End Chemistry Module
Controls chemical dosing targets, GPL (grams per liter), and dosing points.
"""

def calculate_pump_flow_rate_lph(target_dose_kg_t, machine_production_t_h, concentration_gpl):
    """
    Converts a mill target dose (kg/ton) and chemical concentration (grams per liter)
    into a pump flow rate (Liters per hour).
    Critical for accurately setting DCS dosing pump speeds.
    """
    if concentration_gpl <= 0:
        return 0.0
    # Target dose (kg/h) = kg/t * t/h
    target_kg_h = target_dose_kg_t * machine_production_t_h
    # flow (L/h) = target (g/h) / gpl
    flow_lph = (target_kg_h * 1000.0) / concentration_gpl
    return flow_lph

def ash_retention_efficiency(headbox_ash_consistency, white_water_ash_consistency):
    """
    Specifically measures ash/filler retention across the wire, 
    independent of fiber retention.
    """
    if headbox_ash_consistency <= 0:
        return 0.0
    return ((headbox_ash_consistency - white_water_ash_consistency) / headbox_ash_consistency) * 100.0
