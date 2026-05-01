from pap_ai_era.energy.boiler_optimizer import Boiler, BoilerOptimizer

# Boiler Configuration
config = {
    "boiler_type": "AFBC",
    "fuel": {
        "type": "Coal",
        "CV": 4200 # kcal/kg
    }
}

# Current disturbances (ambient conditions, load, etc.)
disturbances = {
    "feedwater_temp": 110, # Celsius
    "ambient_temp": 30
}

if __name__ == "__main__":
    print("--- PapAiEra Universal Boiler Optimizer Demo ---")
    
    # Initialize Boiler Digital Twin
    boiler = Boiler(config)
    
    # Initialize Optimizer
    optimizer = BoilerOptimizer(boiler)
    
    # Run Optimization
    print("\nFinding optimal setpoints for maximum efficiency...")
    result = optimizer.optimize(disturbances)
    
    if result["success"]:
        print("\n--- Optimal Boiler Plan Found ---")
        print(f"Optimal Fuel Flow: {result['optimal_controls']['fuel_flow']:.2f} TPH")
        print(f"Optimal Air Flow: {result['optimal_controls']['air_flow']:.2f} TPH")
        print(f"Predicted Efficiency: {result['efficiency']*100:.2f}%")
        
        print("\n--- Predicted Boiler State ---")
        state = result["state"]
        print(f"Steam Flow: {state['steam_flow']:.2f} TPH")
        print(f"Flue Gas O2: {state['o2']:.2f}%")
        print(f"Flue Gas Temp: {state['flue_temp']:.2f} °C")
    else:
        print(f"Optimization failed: {result['message']}")
