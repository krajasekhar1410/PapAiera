"""
Water and Energy Module
Tracking input and output water and energy flows in the mill.
"""

def specific_water_consumption(water_intake_m3, production_tonnes):
    """
    Calculate specific freshwater consumption in m3 / ADt.
    BAT values vary widely depending on grade, generally 25-50 m3/ADt for Kraft, 10-15 m3/ADt for non-deinked paper.
    """
    if production_tonnes <= 0:
        return 0.0
    return water_intake_m3 / production_tonnes

def specific_energy_consumption(electricity_mwh, steam_gj, production_tonnes):
    """
    Calculate specific energy (thermal and electrical) per tonne of product.
    """
    if production_tonnes <= 0:
        return {"electricity_MWh_t": 0.0, "steam_GJ_t": 0.0}
        
    return {
        "electricity_MWh_t": electricity_mwh / production_tonnes,
        "steam_GJ_t": steam_gj / production_tonnes
    }

def process_water_recycling_rate(recycled_water_volume, total_water_used):
    """
    Calculate the recycling rate of process water (White water loop closure).
    BAT recommends high closure of water loops to minimize freshwater intake.
    """
    if total_water_used <= 0:
        return 0.0
    return (recycled_water_volume / total_water_used) * 100.0
