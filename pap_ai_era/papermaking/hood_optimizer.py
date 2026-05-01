import numpy as np

class HoodOptimizer:
    """
    Optimizes the dryer hood performance by balancing evaporation load, 
    airflow, fan RPM, and air recirculation.
    """
    def __init__(self, targets=None):
        self.targets = targets or {
            "min_dryness": 94.0 # % Target dryness after hood
        }

    @staticmethod
    def calculate_evaporation_load(gsm, speed, width, inlet_moisture, target_moisture):
        """
        Calculates the required evaporation load in kg water per minute.
        """
        production_rate_dry = (gsm * speed * width) / 1000.0  # kg dry fiber/min
        moisture_removed_ratio = (inlet_moisture - target_moisture) / 100.0
        
        # Evaporation load = production_rate_dry * (Moisture_in - Moisture_out) / (100 - Moisture_in)
        # Simplified for demo as production * moisture_drop / 100
        evaporation_load = production_rate_dry * moisture_removed_ratio
        return evaporation_load

    def simulate(self, state, rpm, airflow, recirc):
        """
        Simulates hood performance for a given set of controls.
        """
        # Fan power proportional to RPM cubed (Fan Laws)
        fan_power = (rpm / 100.0) ** 3 * 120.0 # kW (Heuristic scaling)

        # Mixed air temperature (Recirculation vs Outside Air)
        mixed_temp = (recirc * state["return_temp"]) + ((1.0 - recirc) * state["outside_temp"])

        # Evaporation Load
        evap_load = self.calculate_evaporation_load(
            state["gsm"], state["machine_speed"], state["width"], 
            state["inlet_moisture"], state["target_moisture"]
        )

        # Drying Capacity (Heuristic Model)
        # Scaled to represent a high-performance hood
        drying_capacity = (
            0.8 * mixed_temp +
            0.50 * airflow +
            0.20 * (1.0 - state["humidity"]) * 100.0
        ) * 2.0 # Efficiency boost factor

        # Resulting dryness
        dryness_ratio = drying_capacity / (evap_load + 1e-6)
        dryness = min(100.0, 80.0 + dryness_ratio * 20.0)

        # Steam Usage (Estimated)
        steam_usage = evap_load / (drying_capacity + 1e-6)

        # Heat Loss to atmosphere (1 - Recirc)
        heat_loss = airflow * (mixed_temp - state["outside_temp"]) * 0.015

        # Total energy score (Steam + Fan + Heat Loss)
        total_energy = (steam_usage * 100.0) + fan_power + heat_loss

        return {
            "dryness": dryness,
            "steam": steam_usage,
            "fan_power": fan_power,
            "heat_loss": heat_loss,
            "energy": total_energy,
            "evaporation_load": evap_load
        }

    def optimize(self, state):
        """
        Runs a grid search optimization to find the best settings.
        """
        best_solution = None
        min_energy = float("inf")

        # Search space
        rpms = range(60, 101, 5)
        airflows = np.linspace(50, 150, 10)
        recircs = np.linspace(0.3, 0.9, 10)

        for rpm in rpms:
            for airflow in airflows:
                for recirc in recircs:
                    result = self.simulate(state, rpm, airflow, recirc)

                    # Constraint: Must hit target dryness
                    if result["dryness"] >= self.targets["min_dryness"]:
                        if result["energy"] < min_energy:
                            min_energy = result["energy"]
                            best_solution = {
                                "rpm": rpm,
                                "airflow": airflow,
                                "recirc": recirc,
                                **result
                            }

        return best_solution

def run_hood_optimization(params):
    """
    Helper function to run optimization from a parameter dictionary.
    """
    optimizer = HoodOptimizer()
    return optimizer.optimize(params)
