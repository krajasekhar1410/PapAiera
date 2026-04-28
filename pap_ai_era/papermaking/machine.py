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
