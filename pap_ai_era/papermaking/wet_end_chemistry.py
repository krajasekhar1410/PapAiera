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

def suggest_furnish_dosing(hardwood_pct, softwood_pct, broke_pct, target_akd_sizing=True):
    """
    Furnish-Based Chemical Dosing Intelligence.
    Adjusts standard dosing bounds dynamically based on the fiber mix.
    - Softwood (SW) gives strength but has low surface area.
    - Hardwood (HW) gives opacity/smoothness but high surface area (eats more sizing).
    - Broke introduces huge volumes of Anionic Trash, requiring elevated coagulants (PAC/Alum).
    """
    total_pct = hardwood_pct + softwood_pct + broke_pct
    if not (99.0 <= total_pct <= 101.0):
        # Allow tiny float drift, but reject completely invalid mixes
        raise ValueError("Furnish percentages must sum to 100%.")
    
    # Baseline kg/t assumptions
    base_alum_pac = 5.0 
    base_polymer_g_t = 150.0
    base_akd = 2.0 if target_akd_sizing else 0.0
    
    # 1. Anionic Trash Penalty from Broke
    # Broke carries over previous chemicals and starches, neutralizing cationic polymers
    alum_multiplier = 1.0 + (broke_pct / 100.0) * 1.5 
    
    # 2. Surface Area Penalty from Hardwood
    # SW has long thick fibers. HW has short, fine fibers. More fines = more surface area to cover with AKD sizing.
    akd_multiplier = 1.0 + (hardwood_pct / 100.0) * 0.4
    
    # 3. Retention penalty from short fibers (HW & Broke)
    poly_multiplier = 1.0 + ((hardwood_pct + broke_pct) / 100.0) * 0.5
    
    return {
        "suggested_PAC_Alum_kg_t": base_alum_pac * alum_multiplier,
        "suggested_Polymer_g_t": base_polymer_g_t * poly_multiplier,
        "suggested_AKD_kg_t": base_akd * akd_multiplier,
        "furnish_warnings": [
            "High anionic crash risk" if broke_pct > 30 else "Normal broke load",
            "High sizing demand due to fines" if hardwood_pct > 60 else "Normal sizing demand"
        ]
    }
