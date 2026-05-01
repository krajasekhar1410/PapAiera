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
* **Hood Optimizer (`papermaking/`)**: Dryer hood performance and energy optimizer.
* **Bulk Prediction Model (`papermaking/`)**: ML-based multi-layer sheet bulk simulator.
* **Boiler Optimizer (`energy/`)**: Physics-aware Digital Twin and efficiency optimizer.
* **Recovery Cycle (`recovery_cycle.py`)**: Causticizing efficiency, evaporator steam economy, lime kiln energy.

### 2. Papermaking Modules (`pap_ai_era.papermaking`)
* **Machine Operations (`machine.py`)**: Paper machine fiber mass balance, OEE, broke tracking, wire retention, dryer section economy.
* **Wet End Chemistry (`wet_end_chemistry.py`)**: Furnish-based dosing heuristics, physical GPL to LPH pump conversion algorithms, ash retention.
* **Coating/Finishing (`coating.py`)**: Colour recovery, ultrafiltration efficiency, specific water usage.
* **Variability Analysis (`variability_analysis.py`)**: ABB-compliant VPA engine for MDL, CD, and MDS decomposition.

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

---

## Troubleshooting Guide
**1. Optimization returns `success: False`**: Target constraints are mathematically impossible. Adjust boundaries in the `bounds` variables.
**2. Import Errors**: Ensure you run `pip install PapAiEra` in an active environment.
**3. Data Shape for VPA**: The VPA engine expects a 2D numpy array of (scans, data_boxes).
