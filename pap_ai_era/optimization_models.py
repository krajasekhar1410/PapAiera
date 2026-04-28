"""
Optimization Models using SciPy
This module demonstrates advanced optimization problems parameterized by digester types, 
bleach plant sequences, and specific chemical bases.
"""
from scipy.optimize import minimize
import numpy as np

# -----------------------------------------------------------------------------
# 1. BATCH vs CONTINUOUS KRAFT DIGESTERS
# -----------------------------------------------------------------------------

def optimize_batch_kraft_digester(target_kappa, current_alkali_cost, current_wood_cost):
    """
    Finds the optimal Active Alkali (AA) charge (%) and Max Temperature (°C) 
    to minimize total cost in a Batch Digester.
    Batch digesters are constrained by heat-up time and total cycle limits.
    """
    def objective_function(x):
        aa_charge, temp = x[0], x[1]
        cost_of_chemicals = aa_charge * current_alkali_cost
        simulated_yield = 55.0 - (aa_charge * 0.5) - ((temp - 150) * 0.1) 
        wood_cost_per_ton = current_wood_cost / (simulated_yield / 100.0) 
        return cost_of_chemicals + wood_cost_per_ton

    def kappa_constraint(x):
        return target_kappa - (100.0 - (x[0] * 2.5) - ((x[1] - 160) * 1.5))

    con1 = {'type': 'eq', 'fun': kappa_constraint}
    bnds = ((14.0, 22.0), (150.0, 175.0))
    x0 = [18.0, 160.0]
    
    solution = minimize(objective_function, x0, method='SLSQP', bounds=bnds, constraints=[con1])
    return {"success": solution.success, "optimal_AA_charge": solution.x[0], "optimal_temperature": solution.x[1], "minimized_cost": solution.fun}

def optimize_continuous_kamyr_digester(target_kappa, liquor_to_wood_ratio_cost_penalty):
    """
    Continuous digesters (Kamyr) optimize based on Liquor-to-Wood (L/W) ratio
    and specific zone temperatures (e.g., impregnation vs cooking zone).
    Variables: x[0] = EA (Effective Alkali), x[1] = L/W Ratio, x[2] = Cook Zone Temp
    """
    def objective(x):
        ea, lw, temp = x
        # High L/W costs more in evaporator steam later:
        evaporator_penalty = lw * liquor_to_wood_ratio_cost_penalty
        return ea * 1.2 + evaporator_penalty + temp * 0.05 

    def kappa_constraint(x):
        ea, lw, temp = x
        # Kamyr specific approximation model
        simulated_kappa = 110.0 - (ea * 3.0) - (lw * 1.5) - ((temp - 155) * 1.2)
        return target_kappa - simulated_kappa

    con = {'type': 'eq', 'fun': kappa_constraint}
    bnds = ((12.0, 18.0), (3.0, 5.0), (150.0, 165.0)) # EA%, L/W ratio, Temp
    
    res = minimize(objective, [15.0, 4.0, 155.0], bounds=bnds, constraints=[con])
    return {"success": res.success, "optimal_EA": res.x[0], "optimal_LW_ratio": res.x[1], "cook_temp": res.x[2]}

# -----------------------------------------------------------------------------
# 2. BLEACHING SEQUENCES (ECF vs TCF)
# -----------------------------------------------------------------------------

def optimize_bleaching_sequence_cost(sequence_type, incoming_kappa, target_brightness, chemical_costs):
    """
    Dynamically allocates chemical dosages based on the sequence block logic.
    sequence_type: 'ECF' (Elemental Chlorine Free: D-E-D-D) or 'TCF' (O-Z-P).
    chemical_costs dict expects: 'ClO2', 'NaOH', 'Ozone', 'H2O2'
    """
    if sequence_type.upper() == 'ECF':
        # Variables: x[0]=ClO2 total kg/t, x[1]=NaOH kg/t
        def ecf_cost(x):
            return x[0] * chemical_costs.get('ClO2', 1.0) + x[1] * chemical_costs.get('NaOH', 0.5)
        
        def brightness_constraint(x):
            # Empirical: Brightness = 30 + ClO2_charge*1.5 + NaOH*0.5 - (Kappa * 1.2)
            calc_bright = 30 + x[0]*1.5 + x[1]*0.5 - (incoming_kappa * 1.2)
            return calc_bright - target_brightness
            
        res = minimize(ecf_cost, [20.0, 10.0], bounds=((5, 40), (2, 20)), constraints=[{'type': 'ineq', 'fun': brightness_constraint}])
        return {"sequence": "ECF", "ClO2_kg_t": res.x[0], "NaOH_kg_t": res.x[1], "total_cost": res.fun}

    elif sequence_type.upper() == 'TCF':
        # Variables: x[0]=Ozone kg/t, x[1]=H2O2 kg/t
        def tcf_cost(x):
            return x[0] * chemical_costs.get('Ozone', 2.0) + x[1] * chemical_costs.get('H2O2', 1.5)
            
        def brightness_constraint(x):
            # TCF has harder time hitting high brightness
            calc_bright = 20 + x[0]*2.0 + x[1]*1.1 - (incoming_kappa * 1.5)
            return calc_bright - target_brightness
            
        res = minimize(tcf_cost, [5.0, 15.0], bounds=((1, 10), (5, 30)), constraints=[{'type': 'ineq', 'fun': brightness_constraint}])
        return {"sequence": "TCF", "Ozone_k_t": res.x[0], "H2O2_kg_t": res.x[1], "total_cost": res.fun}

# -----------------------------------------------------------------------------
# 3. SULPHITE / ADVANCED CHEMICAL RECOVERY
# -----------------------------------------------------------------------------

def optimize_sulphite_base_recovery(target_so2_recovery, steam_cost_gj, makeup_chemical_cost):
    """
    Optimizes the regeneration cycle for Magnesium/Calcium base Sulphite mills.
    Balancing the intense steam required for multiple-effect evaporators against 
    the cost of buying fresh make-up chemicals.
    Variables: x[0] = Evaporator Live Steam (GJ/t)
    """
    def objective(x):
        steam = x[0]
        # Higher steam boils off more water, improving recovery fire conditions
        recovery_efficiency = min(98.0, 70.0 + (steam * 2.5))
        loss = 100.0 - recovery_efficiency
        makeup_cost = loss * makeup_chemical_cost
        
        return (steam * steam_cost_gj) + makeup_cost

    def recovery_constraint(x):
        recovery_efficiency = min(98.0, 70.0 + (x[0] * 2.5))
        return recovery_efficiency - target_so2_recovery

    res = minimize(objective, [10.0], bounds=[(8.0, 20.0)], constraints=[{'type': 'ineq', 'fun': recovery_constraint}])
    return {"steam_GJ_t": res.x[0], "minimized_cycle_cost": res.fun}
