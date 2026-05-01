import numpy as np
from scipy.optimize import minimize, differential_evolution
from .engine import BleachingSequence

class BleachingOptimizer:
    def __init__(self, sequence: BleachingSequence):
        self.sequence = sequence

    def optimize_cost(self, initial_state, method="differential_evolution"):
        """
        Optimizes chemical dosages to minimize cost while meeting targets.
        """
        # Flatten the bounds for all chemicals in all stages
        bounds = []
        param_map = [] # To map flattened x back to (stage_idx, chem_name)
        
        for i, stage in enumerate(self.sequence.stages):
            for chem in stage.chemicals:
                bounds.append((chem.min_dosage, chem.max_dosage))
                param_map.append((i, chem.name))

        def objective(x):
            dosages_per_stage = self._unflatten_x(x, param_map)
            result = self.sequence.run_sequence(initial_state, dosages_per_stage)
            
            # Penalty for missing targets
            penalty = 0
            final_state = result["final_state"]
            
            if final_state["brightness"] < self.sequence.targets["brightness"]:
                penalty += (self.sequence.targets["brightness"] - final_state["brightness"]) * 1000
            
            if final_state["kappa"] > self.sequence.targets["kappa"]:
                penalty += (final_state["kappa"] - self.sequence.targets["kappa"]) * 1000
                
            if final_state["viscosity"] < self.sequence.targets.get("viscosity_min", 0):
                penalty += (self.sequence.targets["viscosity_min"] - final_state["viscosity"]) * 1000

            return result["total_cost"] + penalty

        if method == "differential_evolution":
            res = differential_evolution(objective, bounds, tol=0.01)
        else:
            # Simple local search
            x0 = [ (b[0] + b[1])/2 for b in bounds ]
            res = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')

        if res.success or res.fun < 1e6: # If it found a feasible solution
            best_dosages = self._unflatten_x(res.x, param_map)
            final_result = self.sequence.run_sequence(initial_state, best_dosages)
            return {
                "success": True,
                "optimal_plan": {self.sequence.stages[i].name: best_dosages[i] for i in range(len(self.sequence.stages))},
                "total_cost": final_result["total_cost"],
                "final_state": final_result["final_state"],
                "message": res.message
            }
        else:
            return {"success": False, "message": "Optimization failed to find a valid solution."}

    def _unflatten_x(self, x, param_map):
        dosages_per_stage = [{} for _ in range(len(self.sequence.stages))]
        for val, (stage_idx, chem_name) in zip(x, param_map):
            dosages_per_stage[stage_idx][chem_name] = val
        return dosages_per_stage
