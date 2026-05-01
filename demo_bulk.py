from pap_ai_era.papermaking.bulk_model import BulkModel
import pandas as pd
import numpy as np

def run_demo():
    print("--- PapAiEra Bulk Prediction Model Demo ---")
    
    # 1. Initialize the model (3-layer board machine)
    bulk_engine = BulkModel(n_layers=3)
    
    # 2. Simulate some training data (Phase 1: ML Training)
    # In a real mill, this would come from the lab/DCS
    print("\nSimulating ML model training on historical mill data...")
    train_data = []
    for _ in range(100):
        # Random inputs
        layers = [
            {"gsm": np.random.uniform(40, 60), "sw_ratio": 0.8, "csf": np.random.uniform(400, 600)}, # Top
            {"gsm": np.random.uniform(100, 200), "sw_ratio": 0.1, "csf": np.random.uniform(300, 500)}, # Middle
            {"gsm": np.random.uniform(40, 60), "sw_ratio": 0.6, "csf": np.random.uniform(400, 600)}, # Bottom
        ]
        process = {"nip_load": np.random.uniform(30, 80), "n_nips": 2}
        
        # Get heuristic bulk as "ground truth" for simulation
        true_bulk = bulk_engine._heuristic_predict(layers, process) + np.random.normal(0, 0.02)
        
        # Flatten for ML
        row = bulk_engine.flatten_layer_data(layers, process)
        row["bulk"] = true_bulk
        train_data.append(row)
    
    df_train = pd.DataFrame(train_data)
    bulk_engine.train(df_train)
    print("Model trained successfully.")

    # 3. Predict Bulk for a new furnish configuration
    new_layers = [
        {"gsm": 50, "sw_ratio": 0.9, "hw_ratio": 0.1, "csf": 550}, # Top (High SW for strength/bulk)
        {"gsm": 150, "sw_ratio": 0.0, "hw_ratio": 0.2, "csf": 400}, # Middle (Filler/Recycled)
        {"gsm": 50, "sw_ratio": 0.7, "hw_ratio": 0.2, "csf": 500}, # Bottom
    ]
    new_process = {"nip_load": 60, "n_nips": 2}

    predicted_bulk = bulk_engine.predict(new_layers, new_process)
    
    print("\n--- FURNISH CONFIGURATION ---")
    for i, l in enumerate(new_layers):
        print(f"Layer {i+1}: {l['gsm']} gsm, {l['sw_ratio']*100}% SW, {l['csf']} CSF")
    
    print(f"\nPredicted Sheet Bulk: {predicted_bulk:.3f} cm3/g")

if __name__ == "__main__":
    run_demo()
