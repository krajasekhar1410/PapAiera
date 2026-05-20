<p align="center">
  <img src="https://raw.githubusercontent.com/krajasekhar1410/PapAiera/main/docs/pap_ai_era_logo.png" width="200" alt="PapAiEra Logo">
</p>

# PapAiEra

[![PyPI version](https://img.shields.io/pypi/v/PapAiEra.svg)](https://pypi.org/project/PapAiEra/)
[![Python versions](https://img.shields.io/pypi/pyversions/PapAiEra.svg)](https://pypi.org/project/PapAiEra/)

**PyPI Project URL**: [https://pypi.org/project/PapAiEra/](https://pypi.org/project/PapAiEra/)

## Installation
```bash
pip install PapAiEra
```

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
* **Bleaching Engine (`bleaching/`)**: Universal, input-driven bleaching sequence optimizer.
* **Adaptive Residual Optimizer**: Kappa-less bleaching control using Brightness/Residual signals.
* **Hood Optimizer (`papermaking/`)**: Dryer hood performance and energy optimizer.
* **Bulk Prediction Model (`papermaking/`)**: ML-based multi-layer sheet bulk simulator.
* **Boiler Optimizer (`energy/`)**: Physics-aware Digital Twin and efficiency optimizer.
* **SYLVACORE (`pulping/sylvacore`)**: Advanced Kraft digestion intelligence (H-factor, Kappa, FurnishLib).
* **Recovery Cycle (`recovery_cycle.py`)**: Causticizing efficiency, evaporator steam economy, lime kiln energy.

### 2. Papermaking Modules (`pap_ai_era.papermaking`)
* **Machine Operations (`machine.py`)**: Paper machine fiber mass balance, OEE, broke tracking, wire retention, dryer section economy.
* **Wet End Chemistry (`wet_end_chemistry.py`)**: Furnish-based dosing heuristics, physical GPL to LPH pump conversion algorithms, ash retention.
* **Coating/Finishing (`coating.py`)**: Colour recovery, ultrafiltration efficiency, specific water usage.
* **WetEndChemix (`papermaking/wet_end_chemix`)**: Wet-end chemistry, Zeta potential, and fiber bonding simulator.
* **Variability Analysis (`variability_analysis.py`)**: ABB-compliant VPA engine for MDL, CD, and MDS decomposition.
* **DTW Lag Detection (`dtw_lag.py`)**: Universal Dynamic Time Warping lag calculator — finds the time delay between ANY input and output process variable.
* **Mill Lag Profiles (`mill_lag_profiles.py`)**: Pre-built lag analysis scenarios for bleach brightness, tower pH, and viscosity-strength tracking.

### 3. Sustainability & Carbon (CCTS) (`pap_ai_era.sustainability`, `pap_ai_era.ccts`)
* **Emissions (`emissions.py`, `air_emissions.py`)**: BOD/COD/TSS load to water. TRS, SO2, NOx, Dust to air.
* **Wastewater & Water (`wastewater.py`, `water_energy.py`)**: Loop closure, explicit cooling-water vs contaminated-water accounting.
* **Management (EMS)**: ISO 14001 grading, solid waste footprint (Ash + Sludge + Rejects).
* **Power Plant & Cogen (`power_plant.py`)**: Boiler thermal efficiency and TG steam tracking.
* **CCTS Platform (`ccts/`)**: Full No-Code Carbon Credit & Trading System module with Scope 1, 2, 3 carbon calculation, credit estimation, dynamic formulas, and built-in UI.

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

## Advanced Usage Examples

### 🧠 Universal Bleaching Optimizer
PapAiEra now includes a **Universal Bleaching Brain**. Engineers can define custom stages, chemicals, and costs via a simple JSON/dict configuration.

**Key Features:**
- **Dynamic Sequence Building**: Supports any number of stages (e.g., D0-EOP-D1, O-Z-P, etc.).
- **AI-Driven Simulation**: Plug-in system for Heuristic, PNN, or Regression models.
- **Global Optimization**: Uses Differential Evolution to minimize total chemical cost while hitting Brightness, Kappa, and Viscosity targets.

```python
from pap_ai_era.bleaching import run_optimization_from_config

config = {
    "stages": [
        {
            "name": "D0",
            "chemicals": [{"name": "ClO2", "min_dosage": 5, "max_dosage": 30, "cost": 0.8}]
        },
        {
            "name": "EOP",
            "chemicals": [
                {"name": "NaOH", "min_dosage": 5, "max_dosage": 25, "cost": 0.4},
                {"name": "H2O2", "min_dosage": 2, "max_dosage": 15, "cost": 0.6}
            ]
        }
    ],
    "targets": {"brightness": 90.0, "kappa": 2.0, "viscosity_min": 800}
}
result = run_optimization_from_config(config)

# Full Multi-Stage Optimization (D0-EOP-D1-D2)
config_full = {
    "stages": [
        {"name": "D0", "chemicals": [{"name": "ClO2", "min_dosage": 5, "max_dosage": 25, "cost": 0.8}]},
        {"name": "EOP", "chemicals": [{"name": "NaOH", "min_dosage": 5, "max_dosage": 20, "cost": 0.4}, {"name": "H2O2", "min_dosage": 2, "max_dosage": 10, "cost": 0.6}]},
        {"name": "D1", "chemicals": [{"name": "ClO2", "min_dosage": 2, "max_dosage": 15, "cost": 0.8}]},
        {"name": "D2", "chemicals": [{"name": "ClO2", "min_dosage": 1, "max_dosage": 10, "cost": 0.8}]}
    ],
    "targets": {"brightness": 88.5, "kappa": 1.5}
}
res_full = run_optimization_from_config(config_full)
print(f"Optimal Chemical Cost: ${res_full['best_cost']:.2f}")
```

### 📊 Variance Partition Analysis (VPA - ABB 2-Sigma)
Decomposes reel variability into Machine Direction (MDL), Cross Direction (CD), and Residual (MDS) components with automated root-cause inference.

```python
import numpy as np
from pap_ai_era.papermaking.variability_analysis import compute_vpa

# 50 scans and 600 data boxes
data = np.random.normal(loc=50, scale=1.5, size=(50, 600))
vpa_report = compute_vpa(data, process_average=50.0)

print(f"Total 2-Sigma Variability: {vpa_report.normalised['TOT']:.2f}%")
print(f"Primary Problem Detected: {vpa_report.primary_problem}")
```

### 🧪 Adaptive Residual Bleaching Optimizer (ARO)
A specialized bleaching controller that eliminates the need for expensive Kappa analyzers. It uses the **Optimum Line** concept to balance Brightness and Chemical Residual.

**Key Features:**
- **Kappa-Less Control**: Operates entirely on final-stage brightness and residual measurements.
- **Golden Section Search**: High-speed mathematical optimization to find the ideal dosage $Q$.
- **Industrial Logic**: Built-in deadband ($\epsilon$), rate-of-change limits, and safety overrides.

```python
from pap_ai_era.bleaching import AdaptiveResidualOptimizer

# Setup with target brightness and residual
opt = AdaptiveResidualOptimizer(target_brightness=80.0, target_residual=5.0)

# Detect state and optimize (with rate limiting)
result = opt.optimize(current_b=55.2, current_r=22.5, 
                      simulate_fn=my_sim_fn, current_q=15.0, max_delta=2.0)
```

### 📚 ML Bulk Prediction Model
A supervised learning framework to predict paper/board bulk ($cm^3/g$) based on layer-wise furnish, pulp properties (CSF, SW/HW ratio), and pressing conditions.

**Key Features:**
- **Layer-Wise Analysis**: Handles multi-layer structures (Top, Middle, Bottom) with independent pulp blends.
- **Physics-Aware ML**: Combines Random Forest regression with industrial heuristics for robust predictions even with limited data.
- **Process Sensitivity**: Tracks the impact of Nip Load, Number of Nips, and refining (CSF) on final sheet thickness.

```python
from pap_ai_era.papermaking import BulkModel

# Define layers and process conditions
layers = [{"gsm": 50, "sw_ratio": 0.9, "csf": 550}, {"gsm": 150, "sw_ratio": 0.1, "csf": 400}]
process = {"nip_load": 60, "n_nips": 2}

model = BulkModel(n_layers=2)
# model.train(historical_data) # Train on mill data
predicted_bulk = model.predict(layers, process)
```

### 💨 Paper Machine Hood Optimizer
Optimizes the dryer section hood by balancing evaporation load against airflow and recirculation.

**Key Features:**
- **Drying Load Calculation**: Uses production rate, speed, and moisture removal (Inlet/Outlet) to determine the exact evaporation demand.
- **Energy Minimization**: Optimizes Fan RPM and Recirculation to save steam and electrical energy.
- **Operational Safety**: Ensures the sheet reaches target dryness while minimizing heat loss to the atmosphere.

```python
from pap_ai_era.papermaking import run_hood_optimization

params = {
    "machine_speed": 1200, "gsm": 80, "width": 6.5,
    "inlet_moisture": 42.0, "target_moisture": 5.0,
    "return_temp": 85.0, "outside_temp": 30.0, "humidity": 0.15
}
best = run_hood_optimization(params)
```

### 🔥 Universal Boiler Optimizer
A physics-aware **Boiler Digital Twin** that uses hybrid modeling to maximize thermal efficiency while staying within safety and emission constraints.

**Key Features:**
- **Hybrid Modeling**: Combines first-principles energy balance with ML residuals.
- **Efficiency Maximization**: Finds the sweet spot for fuel/air ratios to minimize stack loss and unburnt fuel.
- **Constraint Safety**: Automatically respects limits for O2%, steam pressure, and flue gas temperature.

```python
from pap_ai_era.energy.boiler_optimizer import Boiler, BoilerOptimizer

config = {"boiler_type": "AFBC", "fuel": {"CV": 4200}}
boiler = Boiler(config)
optimizer = BoilerOptimizer(boiler)

# Optimize for maximum efficiency
result = optimizer.optimize(disturbances={"feedwater_temp": 110})
```

### ⚙️ Kraft Digester Vroom H-Factor
Calculates the integrated cooking reaction rate required to hit your Kappa target.
```python
from pap_ai_era.pulping.kraft import calculate_h_factor

# 165 °C cooking zone for 45 minutes
h_factor_generated = calculate_h_factor(temperature_celsius=165.0, time_minutes=45.0)
print(f"H-Factor Generated: {h_factor_generated:.2f}")
```

### 💧 Papermaking Moisture Prediction
Simulates the entire water loss journey through the Wire formers, Press Nips, and Dryers.
```python
from pap_ai_era.papermaking.moisture_prediction import predict_wire_drainage_and_couch_moisture

couch = predict_wire_drainage_and_couch_moisture(
    target_gsm=80, machine_speed_mpm=1200, wire_width_m=6.5,
    layer_data=[{'gsm': 40}, {'gsm': 40}],
    vacuum_boxes=[{'vacuum_kpa': 15}, {'vacuum_kpa': 35}, {'vacuum_kpa': 60}]
)
print(f"Moisture exiting Couch Roll: {couch['moisture_after_couch_pct']:.2f}%")
```

### 🌲 SYLVACORE - Digester Process Intelligence
A systematic framework for Kraft pulping that models furnish reactivity, dynamic H-factors, and stage-wise delignification.

**Key Features:**
- **FurnishLib**: Comprehensive reference for Softwood, Hardwood, and Non-wood species.
- **Dynamic H-Factor**: Furnish-corrected H-factor calculations ($H_{eff} = H \times R_f$).
- **Impregnation Quality (IQI)**: Real-time tracking of liquor penetration effectiveness.
- **Batch Digester Identity (BDI)**: Lifecycle tracking and vessel-specific bias correction.

```python
from pap_ai_era.pulping.sylvacore import FurnishLib, HFactorEngine, ChemDosing

flib = FurnishLib()
h_eng = HFactorEngine()
d_eng = ChemDosing()

# Optimize dosing for Eucalyptus
furnish = flib.get_furnish("HW_EUC_GLOB")
dosing = d_eng.calculate_optimal_dosing(furnish, kappa_target=16.0, moisture_pct=50.0)

# Calculate Effective H-Factor from profile
profile = [(0, 80), (60, 160), (120, 160)]
h_eff = h_eng.get_effective_h(h_eng.calculate_raw_h(profile), furnish)
```

### ⚗️ WetEndChemix - Chemistry & Bonding
A specialized simulator to "see the invisible" wet-end chemistry. It predicts charge balance, Zeta potential, and the resulting Fiber Bonding Index (FBI) to minimize paper break risks.

**Key Features:**
- **ZetaPredictor**: Hybrid Stern-Debye model for colloidal charge stability.
- **BondStrengthModel**: Predicts break probability based on chemistry, refining, and starch dosing.
- **Shop-Floor Visualizer**: Optional PyQt6-based dashboard for real-time monitoring.

```python
from pap_ai_era.papermaking.wet_end_chemix import WetEndSimulator, ChemicalDatabase

db = ChemicalDatabase()
sim = WetEndSimulator(db)

# Simulate current mill state
results = sim.run_simulation(
    dosages={"CPAM": 0.25, "STARCH": 12.0},
    ph=6.8, temp_C=48.0, 
    refining_energy=80.0, gsm=70.0
)
print(f"Break Risk: {results['break_risk_pct']:.1f}%")
```

### ⏱️ DTW Lag Detection — Universal Time Delay Finder
Finds the **time lag** between ANY input parameter and ANY output parameter using Dynamic Time Warping. Works for pulp mills, chemical plants, power plants — any process where a cause variable affects an effect variable with a delay.

**Key Features:**
- **Universal**: Works with any two time-series signals — no domain configuration needed.
- **Dynamic Time Warping**: Superior to simple cross-correlation for noisy, non-stationary signals.
- **Handles Inverse Relationships**: Detects lag even when cause and effect are inversely correlated (e.g., temperature ↑ → kappa ↓).
- **Multi-Variable Audit**: Test all input-output combinations in one call.
- **Pre-Built Mill Scenarios**: Ready-to-use configurations for common pulp & paper lag analysis.
- **Confidence Scoring**: Rates each result as HIGH, MEDIUM, or LOW confidence.

#### Use Case 1: Simple — Find lag between any two signals
```python
from pap_ai_era.papermaking import find_lag

# Any input array and output array — that's all you need
result = find_lag(
    input_signal=temperature_data,
    output_signal=viscosity_data,
    time_interval=1.0,       # 1 sample per minute
    time_unit='minutes'
)

print(f"Lag: {result['lag_time']} {result['lag_unit']}")
print(f"Confidence: {result['confidence']}")
```

#### Use Case 2: Digester cook temperature → Kappa number
```python
from pap_ai_era.papermaking import find_lag

# Real DCS historian data (1-minute intervals)
result = find_lag(
    input_signal=cook_temperature,
    output_signal=kappa_number,
    time_interval=1.0,
    time_unit='minutes',
    max_lag=80,
    input_name='Cook Temperature',
    output_name='Kappa Number'
)
print(f"Cook-to-Kappa delay: {result['lag_time']:.1f} minutes")
# Use this lag for feedforward dead-time compensation in DCS
```

#### Use Case 3: Multi-variable process audit from a DataFrame
```python
import pandas as pd
from pap_ai_era.papermaking import find_multi_lag

# Load your process historian data
df = pd.read_csv('process_data.csv')

# Test ALL input-output combinations at once
results = find_multi_lag(
    data=df,
    input_columns=['consistency', 'headbox_pressure', 'steam_flow', 'refiner_energy'],
    output_columns=['basis_weight', 'moisture', 'caliper', 'tensile_strength'],
    time_interval=1.0,
    time_unit='minutes'
)
print(results)
#          Input         Output  Lag (minutes)  Confidence  Correlation
#    consistency   basis_weight           45.0        HIGH       0.9310
#     steam_flow       moisture           83.0        HIGH       0.4158
# refiner_energy        caliper           12.0      MEDIUM       0.8500
```

#### Use Case 4: Pre-built mill scenario — Bleach tower brightness to board brightness
```python
from pap_ai_era.papermaking import MillScenario, run_mill_scenario

result = run_mill_scenario(
    MillScenario.BLEACH_BRIGHTNESS,
    cause=bleach_tower_inlet_brightness,
    effect=board_brightness_qcs
)
print(result.summary())
# === Bleach Tower Inlet Brightness to Board Brightness ===
# DTW Optimal Lag:    122.0 min
# Confidence:         HIGH
# Status: NORMAL
# Interpretation:
#   - Lag of 122.0 min is within expected range (60-240 min)
#   - Use this lag for feedforward dead-time compensation in DCS
```

#### Use Case 5: Tower pH → Wet-end pH
```python
from pap_ai_era.papermaking import MillScenario, run_mill_scenario

result = run_mill_scenario(
    MillScenario.TOWER_PH_WETEND,
    cause=bleach_tower_exit_ph,
    effect=wet_end_ph
)
print(f"pH propagation delay: {result.dtw_result.optimal_lag_seconds / 60:.0f} minutes")
```

#### Use Case 6: Stage-wise viscosity → Strength properties (tensile, burst, tear)
```python
from pap_ai_era.papermaking import run_viscosity_strength_audit

report = run_viscosity_strength_audit(
    viscosity_signals={
        'D0_viscosity': d0_visc_data,
        'EOP_viscosity': eop_visc_data,
        'D1_viscosity': d1_visc_data,
    },
    strength_signals={
        'tensile_index': tensile_data,
        'burst_index': burst_data,
        'tear_index': tear_data,
    }
)
print(report.summary_table)
# Shows which bleach stage most impacts which strength property
```

#### Use Case 7: Non-pulp example — Any chemical/industrial process
```python
from pap_ai_era.papermaking import find_lag

# Reactor feed rate → product concentration
result = find_lag(feed_rate, product_concentration,
                  time_interval=5.0, time_unit='seconds')

# Boiler fuel flow → steam header pressure
result = find_lag(fuel_flow, steam_pressure,
                  time_interval=1.0, time_unit='seconds')

# Cooling water temperature → heat exchanger outlet
result = find_lag(cw_inlet_temp, hx_outlet_temp,
                  time_interval=10.0, time_unit='seconds')
```

#### Use Case 8: List all available mill scenarios
```python
from pap_ai_era.papermaking import list_scenarios
print(list_scenarios())
#                              Scenario  Expected Lag       Process Area
#   bleach_tower_inlet_brightness_to_...   60-240 min  Bleach Plant to PM
#   bleach_tower_ph_to_wetend_ph          30-180 min   Washers to Wet-End
#   stagewise_viscosity_to_strength_...  120-480 min   Bleach to QC Lab
```

### 🌍 Carbon Credit & Trading System (CCTS)
A complete module for No-Code Carbon Calculation, Carbon Credit Estimation, and ESG reporting for Pulp, Paper, Board & Packaging mills. Features editable emission factors (IPCC/IEA/CEA), product grade baseline comparison, and a built-in Streamlit UI.

**Key Features:**
- **Full Scope Calculation**: Tracks Scope 1 (Direct), Scope 2 (Energy), and Scope 3 (Value Chain) emissions.
- **Credit Estimator**: Estimate carbon credits from fuel switching or efficiency improvements.
- **Editable Factors**: Easily update Fuel, Grid Electricity, Steam, Process, and Fiber emission factors via Python or Excel.
- **No-Code Dashboard**: Launch the built-in UI for drag-and-drop analytics.

#### Use Case 1: Carbon Calculator (Code)
```python
from pap_ai_era.ccts import CarbonCalculator
calc = CarbonCalculator()
result = calc.calculate(
    product='kraft_liner',
    production_tons=1000,
    fuel={'coal_bituminous': 5000, 'natural_gas': 2000},
    electricity_mwh=550,
    electricity_region='india_national'
)
print(result.summary())
```

#### Use Case 2: Carbon Credit Estimation
```python
from pap_ai_era.ccts import CreditEstimator
ce = CreditEstimator(price_per_ton=25.0)
result = ce.from_fuel_switch(
    project_name="Coal to Biomass Conversion",
    production_tons=50000,
    baseline_fuel={'coal_bituminous': 200000},
    proposed_fuel={'biomass_wood': 180000, 'natural_gas': 30000}
)
print(result.summary())
```

#### Use Case 3: Launching the No-Code UI
```bash
python -m pap_ai_era.ccts.ui.app
```
*This opens a browser-based Streamlit dashboard where users can upload Excel data, edit emission factors, and build custom ESG KPI dashboards without writing any code.*

---

### 🤖 CopilotPapaiera (AI Expert System)
PapAiEra now includes a fully integrated, offline **AI Expert System** containing the complete knowledge of the "Handbook of Pulping and Papermaking".

**Key Features:**
- **Zero Configuration**: The entire handbook has been pre-processed into a highly optimized BM25 search index that ships directly inside the library.
- **Offline Search**: Search the internal knowledge base instantly without an internet connection or API keys.
- **Live Troubleshooting**: Connects to your live DCS/Historian data to offer precise operational suggestions (Requires OpenAI API key).

#### Use Case 1: Pure Offline Knowledge Search
```python
from pap_ai_era.copilot import CopilotPapaiera

# Initialize the copilot
copilot = CopilotPapaiera()

# Search the internal PapAiEra knowledge base
results = copilot.search_knowledge("Why is the paper surface draggy or picking?", top_n=2)

for result in results:
    print(f"--- From Page {result['metadata']['page']} ---")
    print(result['text'])
```

#### Use Case 2: Live DCS Troubleshooting
```python
import pandas as pd
from pap_ai_era.copilot import CopilotPapaiera

copilot = CopilotPapaiera()

# Load your live DCS / Historian data averages
dcs_data = pd.read_csv("live_machine_data.csv")

# Ask the Copilot to troubleshoot a current problem using your live data
answer = copilot.ask_openai(
    query="We are experiencing picking on the center press roll. Based on my data, what should I change?",
    api_key="your-openai-api-key",
    historian_data=dcs_data
)
print(answer)
# "According to PapAiEra, press roll picking is caused by low temperature. 
# Looking at your historian data, your headbox temperature is currently 42°C (which is low). 
# Suggestion: Increase steam flow to the wire pit to reach 48°C."
```

---

## Troubleshooting Guide
**1. Optimization returns `success: False`**: Target constraints are mathematically impossible. Adjust boundaries in the `bounds` variables.
**2. Import Errors**: Ensure you run `pip install PapAiEra` in an active environment.
**3. Data Shape for VPA**: The VPA engine expects a 2D numpy array of (scans, data_boxes).
