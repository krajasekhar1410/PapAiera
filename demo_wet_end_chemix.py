from pap_ai_era.papermaking.wet_end_chemix import ChemicalDatabase, WetEndSimulator

def run_chemix_demo():
    print("=== WetEndChemix - Wet-End Chemistry Simulation ===")
    
    # 1. Setup
    db = ChemicalDatabase()
    sim = WetEndSimulator(db)

    # 2. Define Mill Condition (Newsprint or Board)
    mill_config = {
        "dosages": {
            "CPAM": 0.25,  # kg/t
            "PAC": 2.5,    # kg/t
            "STARCH": 12.0 # kg/t
        },
        "ph": 6.8,
        "temp_C": 48.0,
        "refining_energy": 80.0, # kWh/t
        "gsm": 70.0,
        "ionic_strength": 0.12 # meq/L
    }

    # 3. Run Simulation
    print("\nRunning Dosing Chain Simulation...")
    result = sim.run_simulation(**mill_config)

    print("\n--- Process State Results ---")
    print(f"Zeta Potential: {result['zeta_potential_mv']:.2f} mV")
    print(f"Charge Density: {result['charge_density_meq_l']:.4f} meq/L")
    print(f"Fiber Bonding Index (FBI): {result['fiber_bonding_index']:.2f}")
    print(f"Sizing Efficiency: {result['sizing_efficiency']:.2%}")
    print(f"Paper Break Probability: {result['break_risk_pct']:.2f}%")
    print(f"System Status: {result['status']}")

    # 4. Simulate a "Problem" scenario (High pH, high conductivity)
    print("\n--- Scenario: Upswing in Anionic Trash (pH 9.2, High Ionic Strength) ---")
    mill_config["ph"] = 9.2
    mill_config["ionic_strength"] = 0.5
    result_fail = sim.run_simulation(**mill_config)
    
    print(f"Zeta Potential: {result_fail['zeta_potential_mv']:.2f} mV")
    print(f"Paper Break Probability: {result_fail['break_risk_pct']:.2f}%")
    print(f"System Status: {result_fail['status']}")

if __name__ == "__main__":
    run_chemix_demo()
