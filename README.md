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
* **Coating/Finishing (`coating.py`)**: Colour recovery, ultrafiltration efficiency, specific water usage.

### 3. Sustainability (`pap_ai_era.sustainability`)
* **Emissions (`emissions.py`, `air_emissions.py`)**: BOD/COD/TSS load to water. TRS, SO2, NOx, Dust to air.
* **Wastewater & Water (`wastewater.py`, `water_energy.py`)**: Loop closure, explicit cooling-water vs contaminated-water accounting.
* **Management (EMS)**: ISO 14001 grading, solid waste footprint (Ash + Sludge + Rejects).

### 4. Mathematical AI Solvers (`pap_ai_era.optimization_models`)
Allows for non-linear optimization using SciPy constraints to determine optimal dosing/setpoints.
* `optimize_batch_kraft_digester()`
* `optimize_continuous_kamyr_digester()`
* `optimize_bleaching_sequence_cost()`
* `optimize_sulphite_base_recovery()`

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

## Example Problem: The Continuous Digester Bottleneck

**The Scenario:** 
A mill utilizing a Kamyr continuous digester needs to hit a specific Kappa number (e.g., Target Kappa 16.0). However, operators are using an excessively high Liquor-to-Wood (L/W) ratio. This means they are pushing too much water through the digester, forcing the evaporators in the recovery boiler cycle to burn thousands of dollars of excessive steam just to boil that water away later.

**The Goal:** 
Find the lowest Effective Alkali (%) and optimal cook temperature to hit the Target Kappa while mathematically penalizing the Liquor-to-Wood ratio to save evaporator steam costs.

### Code Implementation

```python
from pap_ai_era.optimization_models import optimize_continuous_kamyr_digester

result = optimize_continuous_kamyr_digester(
    target_kappa=16.0, 
    liquor_to_wood_ratio_cost_penalty=5.0
)

if result["success"]:
    print(f"Optimal Effective Alkali: {result['optimal_EA']:.2f}%")
    print(f"Optimal Liquor/Wood Ratio: {result['optimal_LW_ratio']:.2f}")
    print(f"Optimal Cook Temperature: {result['cook_temp']:.2f} °C")
```

### Conclusion
By treating the pulping sequence not just as isolated silos but as a continuous mathematical system, PapAiEra allows process engineers to see how turning a dial in the Digester affects the steam budget in the Recovery Boiler.

---

## Troubleshooting Guide

**1. Optimization returns `success: False`**
*   **Cause:** Your `target_kappa` or `target_brightness` is physically impossible given the bounding constraints (e.g., trying to achieve 90 ISO Brightness with only 5 kg/t of ClO2).
*   **Solution:** Check the boundaries defined in `optimization_models.py`. Ensure your targets are realistic for the fibre type.

**2. Import Errors (`ModuleNotFoundError`)**
*   **Cause:** Python cannot find the package. 
*   **Solution:** Ensure you are working in the active virtual environment where the package was installed, or run `pip install PapAiEra` globally.

**3. Math Errors (Division by Zero)**
*   **Cause:** Passing `total_production = 0` to efficiency equations.
*   **Solution:** The functions have built-in zero-division catches, but ensure you stream clean, non-zero denominator readings from your DCS historians.
