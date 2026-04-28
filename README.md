<p align="center">
  <img src="https://raw.githubusercontent.com/krajasekhar1410/PapAiera/main/docs/pap_ai_era_logo.png" width="200" alt="PapAiEra Logo">
</p>

# PapAiEra

<p align="center">
  <img src="https://raw.githubusercontent.com/krajasekhar1410/PapAiera/main/docs/pap_ai_era_banner.png" alt="PapAiEra Banner" width="100%">
</p>

**PapAiEra** is a specialized Python library engineered for the Pulp and Paper industry. It mathematically models and solves optimization problems based on the Best Available Techniques (BAT) reference documents (EU BREF 2015).

---

## Included Processes & Modules

The library covers a massive array of metrics across the entire pulp and paper production cycle.

### 1. Pulping Modules (`pap_ai_era.pulping`)
* **Kraft (`kraft.py`)**: H-factor calculation, Digester Mass Balance, Kappa numbers, recovery efficiency, black liquor solids, yield, BAT compliance.
* **Sulphite (`sulphite.py`)**: Yields for paper/dissolving grades, SO2 and Mg/Ca base recovery.
* **Mechanical (`mechanical.py`)**: Energy intensity of SGW, PGW, TMP, and CTMP, heat recovery.
* **Recycled Fibre (`recycled.py`)**: Deinking yield, fiber loss, rejects rates.
* **Non-Wood (`non_wood.py`)**: Depithing efficiency, silica load checks (crucial for bagasse).
* **Bleaching (`bleaching.py`)**: O2 delignification drops, wash press carry-over, AOX generation.
* **Recovery Cycle (`recovery_cycle.py`)**: Causticizing efficiency, evaporator steam economy, lime kiln energy.

### 2. Papermaking Modules (`pap_ai_era.papermaking`)
* **Machine Operations (`machine.py`)**: Paper machine fiber mass balance, OEE, broke tracking, wire retention, dryer section economy.
* **Wet End Chemistry (`wet_end_chemistry.py`)**: Furnish-based dosing heuristics, physical GPL to LPH pump conversion algorithms, ash retention.
* **Coating/Finishing (`coating.py`)**: Colour recovery, ultrafiltration efficiency, specific water usage.

### 3. Sustainability (`pap_ai_era.sustainability`)
* **Emissions (`emissions.py`, `air_emissions.py`)**: BOD/COD/TSS load to water. TRS, SO2, NOx, Dust to air.
* **Wastewater & Water (`wastewater.py`, `water_energy.py`)**: Loop closure, explicit cooling-water vs contaminated-water accounting.
* **Management (EMS)**: ISO 14001 grading, solid waste footprint (Ash + Sludge + Rejects).
* **Power Plant & Cogen (`power_plant.py`)**: Boiler thermal efficiency and TG steam tracking.

### 4. Mathematical AI Solvers (`pap_ai_era.optimization_models`)
Allows for non-linear optimization using SciPy constraints to determine optimal dosing/setpoints.
* `optimize_batch_kraft_digester()`
* `optimize_continuous_kamyr_digester()`
* `optimize_bleaching_sequence_cost()`
* `optimize_sulphite_base_recovery()`
* `optimize_machine_steam_consumption()`
* `optimize_wet_end_dosing()`
* `optimize_cogeneration_tg_fuel()`

---

## Basic Usage

The library is organized into discrete processes. You can import individual functions to check Key Performance Indicators (KPIs):

```python
from pap_ai_era.pulping.kraft import pulping_yield
from pap_ai_era.papermaking.machine import machine_oee

oee = machine_oee(availability=0.95, performance=0.98, quality=0.99)
print(f"Machine OEE is: {oee:.2f}%")
```

---

## Advanced Usage Examples

Here is exactly how you can use the newly integrated mill modules to track production physics, dosages, and mass balances natively.

### 1. Digester Vroom H-Factor Tracking
Calculates the integrated cooking reaction rate required to hit your Kappa target based on Digester temperatures (Arrhenius logic).
```python
from pap_ai_era.pulping.kraft import calculate_h_factor

# 165 °C cooking zone for 45 minutes
h_factor_generated = calculate_h_factor(temperature_celsius=165.0, time_minutes=45.0)
print(f"H-Factor Generated: {h_factor_generated:.2f}")
```

### 2. Pulping Mass Balance (Fiber & Liquor)
Splits bone dry wood into accepted pulp, screened rejects, and the organic mass that correctly dissolved into Black Liquor going to the recovery boiler.
```python
from pap_ai_era.pulping.kraft import calculate_pulpmill_mass_balance

mass_flow = calculate_pulpmill_mass_balance(
    wood_charged_bdmt=100.0,  # 100 Bone Dry Metric Tonnes of wood
    target_yield_pct=50.0,    # 50% target pulp yield
    rejects_pct=1.5           # 1.5% knot/screen rejects
)
print(f"Accepted Pulp Out: {mass_flow['accepted_pulp_bdmt']} BDMT")
print(f"Black Liquor Organics to Recovery: {mass_flow['dissolved_organics_to_recovery_bdmt']} BDMT")
```

### 3. Machine Fiber Delivery Balance
Calculates the net saleable paper and tracks exactly what was physically lost to the effluent (Wire loss) vs economically lost to recycling (Broke generation).
```python
from pap_ai_era.papermaking.machine import calculate_machine_fiber_balance

machine_flow = calculate_machine_fiber_balance(
    fiber_in_headbox_kg=5000.0, 
    wire_retention_pct=92.0, 
    broke_generated_pct=8.0
)
print(f"Saleable Paper Reel: {machine_flow['saleable_paper_out_kg']} kg")
print(f"Fiber strictly lost to wire water stream: {machine_flow['effluent_loss_kg']} kg")
```

### 4. Furnish-Based Machine Dosing Suggestions
Uses mill heuristics to track Anionic Trash spikes (Broke) vs Surface Area demands (Hardwood) to dynamically formulate sizing and coagulant demands.
```python
from pap_ai_era.papermaking.wet_end_chemistry import suggest_furnish_dosing

chemical_targets = suggest_furnish_dosing(
    hardwood_pct=60.0,  # Fines drive up AKD sizing limit
    softwood_pct=10.0,
    broke_pct=30.0,     # Heavily drives up PAC/Alum coagulant demand
    target_akd_sizing=True
)
print(f"Suggested Alum Dose: {chemical_targets['suggested_PAC_Alum_kg_t']:.2f} kg/t")
print(f"Warning Triggers: {chemical_targets['furnish_warnings']}")
```

### 5. Multi-Layer Machine Stage-Wise Moisture Prediction
Simulates the entire water loss journey through the Wire formers, Press Nips, and condensing Steam Dryers.
```python
from pap_ai_era.papermaking.moisture_prediction import predict_wire_drainage_and_couch_moisture, predict_press_section_moisture, predict_dryer_group_moisture

# Wire Drain
couch = predict_wire_drainage_and_couch_moisture(
    target_gsm=80, machine_speed_mpm=1200, wire_width_m=6.5,
    layer_data=[{'gsm': 40}, {'gsm': 40}], # Multi-layer boosting drain efficiency
    vacuum_boxes=[{'vacuum_kpa': 15}, {'vacuum_kpa': 35}, {'vacuum_kpa': 60}]
)
print(f"Moisture exiting Couch Roll: {couch['moisture_after_couch_pct']:.2f}%")

# Press Dewatering
presses = predict_press_section_moisture(
    presses=[{'linear_load_kn_m': 60}, {'linear_load_kn_m': 90, 'shoe_press': True}],
    inlet_moisture_pct=couch['moisture_after_couch_pct'],
    machine_speed_mpm=1200
)
print(f"Moisture after 3rd Press: {presses['final_press_moisture_pct']:.2f}%")

# Dryer Cylinder Extraction
evap = predict_dryer_group_moisture(
    dryer_groups=[{'cylinders': 12, 'steam_pressure_bar': 2.5}, {'cylinders': 16, 'steam_pressure_bar': 4.0}],
    inlet_moisture_pct=presses['final_press_moisture_pct'],
    target_gsm=80, 
    machine_speed_mpm=1200, 
    width_m=6.5
)
print(f"Final Reel Moisture: {evap['final_reel_moisture_pct']:.2f}%")
```

### 5. Bleaching Cost Sequencing (ECF)
Minimises total chemical cost subject to physical constraints (Target brightness and minimum viscosity drops) traversing dynamically through the D0, Eop, D1, and P stages.
```python
from pap_ai_era.core_simulations.lib_optimisation import bleach_objective_function

params_dict = {
    'price_ClO2': 1.20, 'price_NaOH': 0.40, 'price_H2O2': 0.80, # Costs
    'D': {'k_D': 0.20, 'n_D': 0.90, 'B_max_D': 88, 'k_B_D': 0.05, 'k_v_D': 0.1},
    'Eop': {'a_E': 10, 'b_E': 2.5, 'c_E': 1.5, 'd_E': 3.0},
    'P': {'k_d': 0.01, 'B_max_P': 92, 'k_P': 0.08, 'k_v_P': 0.05, 'k_B_H2O2': 0.8}
}

result = bleach_objective_function(
    chemical_doses=[12.0, 10.0, 3.0, 8.0, 4.0], 
    kappa_0=30.0, 
    B_target=88.0, 
    visc_min=700.0, 
    params_dict=params_dict
)
if result['success']:
    print(f"Minimized Sequence Cost: ${result['cost_minimized']:.2f}")
    print(f"Optimal Dosing Vectors [D0, Eop, pEop, D1, P]: {result['optimal_doses_kg_t']}")
```

### 6. Full Digester Kinetics Integration
Numerically integrates Lignin dissolution, Carbohydrate peeling, and Effective Alkali consumption across specific chip time-temperature vectors using SciPy ODEs to predict exact blow Kappa.
```python
from pap_ai_era.core_simulations.lib_cook_module import cook_module

inputs = {
    'L0': 0.25, 'C0': 0.70, 'EA_conc': 45.0, 'LWR': 4.0, 'sulphidity': 30.0,
    'T_profile': ([0, 30, 90, 150], [90, 150, 165, 165]) # Minutes vs Celsius T_vec
}
params = {
    'kappa_factor': 6.57, 'kappa_bulk_thresh': 50, 'kappa_res_thresh': 20,
    'alpha_L': 0.4, 'alpha_C': 0.15, 'k_C': 0.002, 'Ea_C': 130000,
    'initial': {'A': 1e7, 'Ea': 100000, 'a': 0.5, 'b': 0.3},
    'bulk': {'A': 3.2e10, 'Ea': 134000, 'a': 1.0, 'b': 0.4},
    'residual': {'A': 1.8e8, 'Ea': 125000, 'a': 0.5, 'b': 0.3}
}

simulation = cook_module(inputs, params)
print(f"Final Kappa Predict: {simulation['kappa_f']:.2f}")
print(f"Final Estimated Yield: {simulation['Y']:.2f}%")
print(f"Generated H-Factor: {simulation['H_f']:.1f}")
```

---

## Example Optimization: The Continuous Digester Bottleneck

Find the lowest Effective Alkali (%) and optimal cook temperature to hit the Target Kappa while mathematically penalizing the Kamyr Liquor-to-Wood ratio to save steam costs.

```python
from pap_ai_era.optimization_models import optimize_continuous_kamyr_digester

result = optimize_continuous_kamyr_digester(target_kappa=16.0, liquor_to_wood_ratio_cost_penalty=5.0)

if result["success"]:
    print(f"Optimal Effective Alkali: {result['optimal_EA']:.2f}%")
```

---

## Troubleshooting Guide
**1. Optimization returns `success: False`**: Target constraints are mathematically impossible (e.g., high Brightness with no chemicals). Adjust boundaries in the `bounds` variables.
**2. Import Errors**: Ensure you run `pip install PapAiEra` in an active environment.
