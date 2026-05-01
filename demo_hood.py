from pap_ai_era.papermaking.hood_optimizer import run_hood_optimization

# Machine and Hood State
params = {
    "machine_speed": 1200, # m/min
    "gsm": 80,             # g/m2
    "width": 6.5,          # m
    "inlet_moisture": 42.0, # % (from press section)
    "target_moisture": 5.0, # % (at reel)
    "return_temp": 85.0,    # Celsius
    "outside_temp": 30.0,   # Celsius
    "humidity": 0.15,       # 15% RH
    "current_rpm": 850
}

if __name__ == "__main__":
    print("--- PapAiEra Hood Optimizer Demo ---")
    print(f"Initial Evaporation Load needed for {params['gsm']} gsm @ {params['machine_speed']} mpm...")
    
    best = run_hood_optimization(params)
    
    if best:
        print("\n--- OPTIMAL HOOD SETTINGS ---")
        print(f"RPM: {best['rpm']}")
        print(f"Airflow: {best['airflow']:.2f} %")
        print(f"Recirculation: {best['recirc']:.2f} (Ratio)")

        print("\n--- PERFORMANCE SUMMARY ---")
        print(f"Dryness Achieved: {best['dryness']:.2f}%")
        print(f"Evaporation Load: {best['evaporation_load']:.2f} kg water/min")
        print(f"Fan Power Consumption: {best['fan_power']:.2f} kW")
        print(f"Heat Loss to Atmosphere: {best['heat_loss']:.2f} Energy Units")
        print(f"Total Energy Score: {best['energy']:.2f} (Lower is better)")
    else:
        print("\n[!] No feasible solution found. Adjust constraints or targets.")
