# PapAiEra

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
