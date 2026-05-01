from pap_ai_era.bleaching import run_optimization_from_config

# Example Configuration: D0 -> EOP -> D1 Sequence
config = {
    "stages": [
        {
            "name": "D0",
            "chemicals": [
                {"name": "ClO2", "min_dosage": 5, "max_dosage": 30, "cost": 0.8}
            ]
        },
        {
            "name": "EOP",
            "chemicals": [
                {"name": "NaOH", "min_dosage": 5, "max_dosage": 25, "cost": 0.4},
                {"name": "H2O2", "min_dosage": 2, "max_dosage": 15, "cost": 0.6},
                {"name": "O2", "min_dosage": 1, "max_dosage": 10, "cost": 0.2}
            ]
        },
        {
            "name": "D1",
            "chemicals": [
                {"name": "ClO2", "min_dosage": 3, "max_dosage": 20, "cost": 0.8}
            ]
        }
    ],
    "targets": {
        "brightness": 90.0,
        "kappa": 2.0,
        "viscosity_min": 800.0
    }
}

# Initial pulp state after brown stock washing
initial_state = {
    "brightness": 32.0,
    "kappa": 16.5,
    "viscosity": 1050.0
}

if __name__ == "__main__":
    print("--- PapAiEra Universal Bleaching Optimizer Demo ---")
    run_optimization_from_config(config, initial_state)
