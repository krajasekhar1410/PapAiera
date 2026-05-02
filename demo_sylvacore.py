from datetime import datetime
from pap_ai_era.pulping.sylvacore import (
    FurnishLib, HFactorEngine, KappaModel, ChemDosing, 
    PreTreatment, DigesterManager, BatchDigesterIdentity, AdvisorEngine
)

def run_sylvacore_demo():
    print("=== SYLVACORE Process Intelligence Demo ===")
    
    # 1. Setup Library
    flib = FurnishLib()
    h_eng = HFactorEngine()
    k_mod = KappaModel()
    d_eng = ChemDosing()
    p_mod = PreTreatment()
    mgr = DigesterManager()
    advisor = AdvisorEngine()

    # 2. Select Furnish
    furnish = flib.get_furnish("SW_PINE_LOBLOLLY")
    print(f"\nActive Furnish: {furnish.furnish_name} (Rf: {furnish.reactivity_factor_Rf})")

    # 3. Optimize Dosing
    dosing = d_eng.calculate_optimal_dosing(furnish, kappa_target=30.0, moisture_pct=45.0)
    print("\n--- Chemical Dosing Optimization ---")
    print(f"Target EA (OD basis): {dosing['ea_adj_pct_od']:.2f}%")
    print(f"Actual EA (Wet basis): {dosing['ea_actual_pct_wet']:.2f}%")
    print(f"Recommended L/W Ratio: {dosing['lw_ratio_target']}")

    # 4. Batch Digester Operations
    vessel_id = "BD-M04"
    mgr.register_batch_digester(BatchDigesterIdentity(
        bdi_code=vessel_id,
        vessel_name="Digester 4 North",
        commissioned_date=datetime(2020, 1, 1),
        vessel_volume_m3=160,
        design_pressure_kPa=1200,
        lining_material="Stainless Steel"
    ))
    
    cook = mgr.start_cook(vessel_id, furnish.furnish_id, kappa_target=30.0)
    print(f"\n--- Started Cook Cycle: {cook.ccr_id} ---")

    # 5. Simulate Cook Progress
    # Temperature Profile: [time_min, temp_C]
    profile = [
        (0, 80), (30, 130), (60, 130), (120, 168), (180, 168)
    ]
    
    raw_h = h_eng.calculate_raw_h(profile)
    eff_h = h_eng.get_effective_h(raw_h, furnish)
    target_h = h_eng.calculate_target_h(30.0, furnish)
    
    cook.h_factor_final = eff_h
    cook.ea_charged_pct = dosing['ea_adj_pct_od']
    cook.iqi_score = p_mod.calculate_iqi(duration_min=45, temp_C=130, pressure_kPa=450, furnish=furnish)
    
    predicted_kappa = k_mod.predict_kappa(eff_h, cook.ea_charged_pct, furnish)
    
    print("\n--- Process Results ---")
    print(f"Classical H-Factor: {raw_h:.1f}")
    print(f"Effective H-Factor: {eff_h:.1f} (Target: {target_h:.1f})")
    print(f"Impregnation Quality Index (IQI): {cook.iqi_score:.1f}")
    print(f"Predicted Kappa: {predicted_kappa:.2f}")

    # 6. Advisor Recommendations
    recs = advisor.evaluate_cook(cook, furnish)
    print("\n--- Advisor Intelligence ---")
    if recs:
        for r in recs:
            print(f"[{r['priority']}] {r['code']}: {r['message']}")
    else:
        print("Process optimal. No warnings.")

if __name__ == "__main__":
    run_sylvacore_demo()
