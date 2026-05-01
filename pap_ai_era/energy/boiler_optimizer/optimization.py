import numpy as np
from scipy.optimize import differential_evolution

class BoilerOptimizer:
    def __init__(self, boiler, targets=None):
        self.boiler = boiler
        self.targets = targets or {
            "steam_pressure": (60, 68),
            "steam_temp": (470, 500),
            "o2": (2.5, 4.5),
            "flue_temp_max": 180
        }

    def optimize(self, disturbances, bounds=None):
        """
        Finds optimal fuel and air flow to maximize efficiency while respecting constraints.
        """
        if bounds is None:
            # Default search bounds: fuel (5-50 TPH), air (50-600 TPH)
            bounds = [(5, 50), (50, 600)]

        def objective(x):
            controls = {"fuel_flow": x[0], "air_flow": x[1]}
            state = self.boiler._basic_physics_simulate(controls, disturbances)
            efficiency = self.boiler.calculate_efficiency(state)
            
            # Penalties
            penalty = 0
            if state.o2 < self.targets["o2"][0] or state.o2 > self.targets["o2"][1]:
                penalty += 1000 * abs(state.o2 - np.mean(self.targets["o2"]))
            
            if state.flue_temp > self.targets["flue_temp_max"]:
                penalty += 500 * (state.flue_temp - self.targets["flue_temp_max"])
            
            # We want to maximize efficiency, so minimize -efficiency + penalty
            return -efficiency + penalty

        res = differential_evolution(objective, bounds, tol=0.01)
        
        if res.success:
            optimal_controls = {"fuel_flow": res.x[0], "air_flow": res.x[1]}
            final_state = self.boiler._basic_physics_simulate(optimal_controls, disturbances)
            return {
                "success": True,
                "optimal_controls": optimal_controls,
                "efficiency": self.boiler.calculate_efficiency(final_state),
                "state": final_state.to_dict()
            }
        return {"success": False, "message": res.message}
