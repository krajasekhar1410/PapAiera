"""
Kraft Pulping Module
For calculations related to the Chemical Kraft pulping process.
"""

def kappa_number(k_permanganate_consumed):
    """
    Estimates Kappa Number based on potassium permanganate consumed by the pulp.
    Kappa number represents the residual lignin content.
    """
    return k_permanganate_consumed * 1.0  # Simplified scaling factor

def chemical_recovery_efficiency(chemicals_recovered, chemicals_charged):
    """
    Calculate the recovery efficiency of the chemical recovery cycle.
    BAT for modern Kraft mills is > 95%.
    """
    if chemicals_charged <= 0:
        return 0.0
    return (chemicals_recovered / chemicals_charged) * 100.0

def black_liquor_solids_content(solids_mass, total_mass):
    """
    Calculate the percentage of dry solids in black liquor.
    High dry solids (> 75-80%) are characteristic of modern, efficient evaporation plants (BAT).
    """
    if total_mass <= 0:
        return 0.0
    return (solids_mass / total_mass) * 100.0

def pulping_yield(dry_pulp_produced, dry_wood_charged):
    """
    Calculate the overall pulp yield (kappa dependent).
    Typically 45% - 55% for Kraft pulping.
    """
    if dry_wood_charged <= 0:
        return 0.0
    return (dry_pulp_produced / dry_wood_charged) * 100.0

def check_kraft_bat_compliance(water_consumption, steam_consumption, elec_consumption):
    """
    Verifies if specific consumption aligns with general Kraft BAT norms.
    Units: Water (m3/ADt), Steam (GJ/ADt), Electricity (MWh/ADt).
    Reference: BREF 2015.
    """
    compliance = {
        'water': water_consumption <= 50, # general unbleached/bleached range 25-50 m3/ADt
        'steam': steam_consumption <= 14, # general range 10-14 GJ/ADt
        'electricity': elec_consumption <= 0.8 # general range 0.6-0.8 MWh/ADt
    }
    return compliance

def calculate_h_factor(temperature_celsius, time_minutes):
    """
    Calculates the Vroom H-factor for Kraft cooking. 
    It integrates the reaction rate relative to 100°C over time using the Arrhenius equation.
    Typically utilized to target a specific cooking degree (Kappa number).
    """
    if temperature_celsius <= 0 or time_minutes <= 0:
        return 0.0
    
    # Convert Temp to Kelvin
    temp_kelvin = temperature_celsius + 273.15
    # Vroom's established formula for relative reaction rate (k)
    import math
    reaction_rate = math.exp(43.2 - (16113.0 / temp_kelvin))
    
    # H-factor is the integral of reaction rate over time (in hours)
    h_factor = reaction_rate * (time_minutes / 60.0)
    return h_factor

def calculate_pulpmill_mass_balance(wood_charged_bdmt, target_yield_pct, rejects_pct):
    """
    Performs a high-level mass balance for the pulp mill digester block.
    Splits the incoming bone dry wood into accepted pulp, solid rejects, 
    and dissolved organics (which become black liquor solids).
    Output is in Bone Dry Metric Tonnes (BDMT).
    """
    if wood_charged_bdmt <= 0:
        return {"accepted_pulp_bdmt": 0.0, "rejects_bdmt": 0.0, "dissolved_solids_bdmt": 0.0}
        
    total_pulp = wood_charged_bdmt * (target_yield_pct / 100.0)
    rejects = wood_charged_bdmt * (rejects_pct / 100.0)
    accepted_pulp = total_pulp - rejects
    
    # Assuming standard conservative mass conservation (ignoring volatile losses like turpentine/methanol here)
    dissolved_organics = wood_charged_bdmt - total_pulp
    
    return {
        "wood_in_bdmt": wood_charged_bdmt,
        "accepted_pulp_bdmt": accepted_pulp,
        "rejects_bdmt": rejects,
        "dissolved_organics_to_recovery_bdmt": dissolved_organics
    }
