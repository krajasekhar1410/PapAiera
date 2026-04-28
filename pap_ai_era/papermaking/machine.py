"""
Papermaking Module
Calculations for Paper Machine operations, efficiency, and retention.
"""

def machine_oee(availability, performance, quality):
    """
    Calculates Overall Equipment Effectiveness (OEE) for the Paper Machine.
    availability: Operating time / Planned operating time
    performance: Actual speed / Design speed
    quality: Good saleable paper / Total paper rolled
    """
    return availability * performance * quality * 100.0

def broke_percentage(broke_mass, total_production):
    """
    Calculate the amount of broke (off-spec or broke paper returned to the pulper)
    as a percentage of total production. 
    BAT minimizes broke generation.
    """
    if total_production <= 0:
        return 0.0
    return (broke_mass / total_production) * 100.0

def overall_retention(white_water_consistency, headbox_consistency):
    """
    First-pass retention (FPR) on the wire section.
    BAT requires optimizing retention to reduce solids load in the white water system.
    """
    if headbox_consistency <= 0:
        return 0.0
    return ((headbox_consistency - white_water_consistency) / headbox_consistency) * 100.0

def drying_efficiency(steam_used_in_dryers, water_evaporated):
    """
    Calculate specific steam consumption in the dryer section.
    Target: kg steam / kg water evaporated. BAT is ~1.2 - 1.4.
    """
    if water_evaporated <= 0:
        return 0.0
    return steam_used_in_dryers / water_evaporated

def calculate_machine_fiber_balance(fiber_in_headbox_kg, wire_retention_pct, broke_generated_pct, miscellaneous_loss_pct=1.0):
    """
    Performs a localized mass balance around the paper machine.
    Calculates the gross paper rolled onto the reel, the saleable paper minus broke,
    and the actual white water solids lost to the effluent system.
    """
    if fiber_in_headbox_kg <= 0:
         return {"saleable_paper_out_kg": 0.0, "broke_recycled_kg": 0.0, "effluent_loss_kg": 0.0}
    
    # Amount of fiber actually staying on the wire to become paper sheet
    sheet_formed = fiber_in_headbox_kg * (wire_retention_pct / 100.0)
    
    # Amount lost through the wire into the short/long loop
    white_water_loss = fiber_in_headbox_kg - sheet_formed
    
    # Miscellaneous minor losses (evaporation volatiles, dust shedding, press section carry-over)
    misc_loss = sheet_formed * (miscellaneous_loss_pct / 100.0)
    
    gross_reel = sheet_formed - misc_loss
    
    # Off-spec paper returned as broke
    broke_recycled = gross_reel * (broke_generated_pct / 100.0)
    
    # What goes out the door
    saleable_paper = gross_reel - broke_recycled
    
    return {
        "fiber_in_kg": fiber_in_headbox_kg,
        "saleable_paper_out_kg": saleable_paper,
        "broke_recycled_kg": broke_recycled,
        "effluent_loss_kg": white_water_loss, 
        "unaccounted_misc_loss_kg": misc_loss
    }
