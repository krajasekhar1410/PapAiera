import json
from .engine import BleachingStage, BleachingSequence, Chemical
from .optimization import BleachingOptimizer

def ask_user_config():
    """
    Interactively prompts the user for bleaching configuration.
    """
    print("\n--- PapAiEra Bleaching Configurator ---")
    stages_data = []
    
    try:
        n = int(input("Enter number of stages: "))

        for i in range(n):
            stage_name = input(f"Enter stage {i+1} name (e.g. D0, EOP, D1): ")
            chemicals = []

            c = int(input(f"Number of chemicals in {stage_name}: "))
            for j in range(c):
                name = input(f"  Chemical {j+1} name: ")
                min_val = float(input(f"  Min dosage for {name}: "))
                max_val = float(input(f"  Max dosage for {name}: "))
                cost = float(input(f"  Cost per unit for {name}: "))

                chemicals.append({
                    "name": name,
                    "min_dosage": min_val,
                    "max_dosage": max_val,
                    "cost": cost
                })

            stages_data.append({
                "name": stage_name,
                "chemicals": chemicals
            })

        print("\n--- Set Targets ---")
        brightness = float(input("Target Brightness: "))
        kappa = float(input("Target Kappa: "))
        viscosity = float(input("Min Viscosity: "))

        return {
            "stages": stages_data,
            "targets": {
                "brightness": brightness,
                "kappa": kappa,
                "viscosity_min": viscosity
            }
        }
    except ValueError:
        print("Invalid input. Please enter numeric values where expected.")
        return None

def run_optimization_from_config(config, initial_state=None):
    """
    Takes a config dictionary and runs the optimizer.
    """
    if initial_state is None:
        initial_state = {"brightness": 35.0, "kappa": 18.0, "viscosity": 1100.0}

    stages = [BleachingStage(s["name"], s["chemicals"]) for s in config["stages"]]
    sequence = BleachingSequence(stages, config["targets"])
    optimizer = BleachingOptimizer(sequence)
    
    print("\nRunning Optimization...")
    result = optimizer.optimize_cost(initial_state)
    
    if result["success"]:
        print("\n--- Optimal Bleaching Plan Found ---")
        print(json.dumps(result["optimal_plan"], indent=4))
        print(f"Total Chemical Cost: ${result['total_cost']:.2f}")
        print("\n--- Predicted Final State ---")
        print(json.dumps(result["final_state"], indent=4))
    else:
        print(f"Optimization failed: {result['message']}")
    
    return result

if __name__ == "__main__":
    config = ask_user_config()
    if config:
        run_optimization_from_config(config)
