"""
Environmental Management System (EMS) Module
General BAT conclusions applicable to all pulp and paper mills.
"""

def ems_scorecard(has_iso14001, continuous_monitoring_water, continuous_monitoring_air, waste_minimization_plan, energy_efficiency_plan):
    """
    Evaluates the basic EMS setup of the mill against generalized BAT conclusions for management.
    BAT 1 essentially requires an EMS, continuous monitoring of key pollutants, and reduction plans.
    """
    factors = [
        has_iso14001,
        continuous_monitoring_water,
        continuous_monitoring_air,
        waste_minimization_plan,
        energy_efficiency_plan
    ]
    
    score = sum([1 for f in factors if f])
    total = len(factors)
    
    return {
        "score": score,
        "total": total,
        "is_bat_compliant": score == total,
        "missing_components": [
            name for name, val in zip(
                ["ISO 14001", "Water Monitoring", "Air Monitoring", "Waste Plan", "Energy Plan"],
                factors
            ) if not val
        ]
    }

def calculate_total_solid_waste(boiler_ash_tonnes, rejects_tonnes, sludge_tonnes, production_tonnes):
    """
    Total solid waste directed to landfill per ADt.
    BAT strongly encourages minimizing landfilling by reusing ash, combusting rejects,
    and using sludge in agriculture or energy recovery.
    """
    if production_tonnes <= 0:
        return 0.0
    return (boiler_ash_tonnes + rejects_tonnes + sludge_tonnes) / production_tonnes

def material_efficiency(saleable_product, total_raw_materials):
    """
    General material efficiency of the plant.
    """
    if total_raw_materials <= 0:
        return 0.0
    return (saleable_product / total_raw_materials) * 100.0
