from pap_ai_era.bleaching import AdaptiveResidualOptimizer, BleachingSimulator

def run_demo():
    print("--- PapAiEra Adaptive Residual Bleaching Optimizer Demo ---")
    
    # 1. Setup Optimizer (Target Brightness 80, Target Residual 5)
    opt = AdaptiveResidualOptimizer(target_brightness=80.0, target_residual=5.0)
    
    # 2. Setup Simulator (Kappa 15)
    sim = BleachingSimulator(kappa=15)
    
    # 3. Simulate a sequence of adjustments
    current_q = 12.0 # Starting dosage
    print(f"\nInitial Dosage: {current_q} kg/t")
    
    for i in range(3):
        print(f"\nStep {i+1}:")
        b, r = sim.simulate(current_q)
        print(f"  Current Brightness: {b:.2f}, Residual: {r:.2f}")
        
        result = opt.optimize(b, r, sim.simulate, current_q=current_q, max_delta=3.0)
        
        print(f"  Status: {result['status']}")
        print(f"  Action: {result['action']}")
        print(f"  New Dosage: {result['optimal_dosage']:.2f} kg/t")
        
        current_q = result['optimal_dosage']

    # Final check
    b, r = sim.simulate(current_q)
    print(f"\nFinal State reached:")
    print(f"  Brightness: {b:.2f}, Residual: {r:.2f}")

if __name__ == "__main__":
    run_demo()
