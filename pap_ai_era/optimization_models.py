"""
Optimization Models using SciPy
This module demonstrates how to use the PapAiEra library to solve production optimization problems.
"""
from scipy.optimize import minimize
from .pulping.kraft import pulping_yield

def optimize_kraft_digester(target_kappa, current_alkali_cost, current_wood_cost):
    """
    Example Optimization: 
    Find the optimal Active Alkali (AA) charge and Temperature to minimize total cost
    while achieving a Target Kappa number.
    
    Variables: x[0] = Active Alkali charge (%), x[1] = Max Temperature (°C)
    """
    
    # 1. Define the Objective Function (Cost to minimize)
    def objective_function(x):
        aa_charge = x[0]
        # simplified cost model
        cost_of_chemicals = aa_charge * current_alkali_cost
        
        # higher alkali & temp linearly reduces yield in this toy model
        simulated_yield = 55.0 - (aa_charge * 0.5) - ((x[1] - 150) * 0.1) 
        wood_cost_per_ton_pulp = current_wood_cost / (simulated_yield / 100.0) 
        
        return cost_of_chemicals + wood_cost_per_ton_pulp

    # 2. Define Constraints
    def kappa_constraint(x):
        # Pretend formula: Kappa = 100 - (AA * 2.5) - (Temp - 150) * 1.5
        simulated_kappa = 100.0 - (x[0] * 2.5) - ((x[1] - 160) * 1.5)
        # We want (simulated_kappa - target_kappa) == 0, so inequality:
        return target_kappa - simulated_kappa

    # Target kappa must be exactly met 
    con1 = {'type': 'eq', 'fun': kappa_constraint}
    
    # 3. Bounds (AA between 14-22%, Temp between 150-170C)
    bnds = ((14.0, 22.0), (150.0, 170.0))
    
    # Initial guess
    x0 = [18.0, 160.0]
    
    # Run the solver
    solution = minimize(objective_function, x0, method='SLSQP', bounds=bnds, constraints=[con1])
    
    return {
        "success": solution.success,
        "optimal_AA_charge": solution.x[0],
        "optimal_temperature": solution.x[1],
        "minimized_cost": solution.fun
    }
