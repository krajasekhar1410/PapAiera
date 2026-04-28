# PapAiEra

**PapAiEra** is a specialized Python library engineered for the Pulp and Paper industry. It mathematically models and solves optimization problems based on the Best Available Techniques (BAT) reference documents (EU BREF 2015).

---

## Basic Usage

The library is organized into discrete processes representing the entire mill hierarchy. You can import individual functions to check Key Performance Indicators (KPIs) or use the AI solvers.

```python
from pap_ai_era.pulping.kraft import pulping_yield
from pap_ai_era.papermaking.machine import machine_oee

# Check your Paper Machine Operational Efficiency
oee = machine_oee(availability=0.95, performance=0.98, quality=0.99)
print(f"Machine OEE is: {oee:.2f}%")
```

---

## Example Problem: The Continuous Digester Bottleneck

**The Scenario:** 
A mill utilizing a Kamyr continuous digester needs to hit a specific Kappa number (e.g., Target Kappa 16.0). However, operators are using an excessively high Liquor-to-Wood (L/W) ratio. This means they are pushing too much water through the digester, forcing the evaporators in the recovery boiler cycle to burn thousands of dollars of excessive steam just to boil that water away later.

**The Goal:** 
Find the absolute lowest Effective Alkali (%) and optimal cook temperature to hit the Target Kappa while mathematically penalizing the Liquor-to-Wood ratio to save evaporator steam costs.

### Code Implementation

You can solve this scenario out-of-the-box using PapAiEra's built-in SciPy constraint models:

```python
from pap_ai_era.optimization_models import optimize_continuous_kamyr_digester

# Target Kappa = 16.0
# The cost penalty factor for evaporating excess liquid = 5.0
result = optimize_continuous_kamyr_digester(
    target_kappa=16.0, 
    liquor_to_wood_ratio_cost_penalty=5.0
)

if result["success"]:
    print(f"Optimal Effective Alkali: {result['optimal_EA']:.2f}%")
    print(f"Optimal Liquor/Wood Ratio: {result['optimal_LW_ratio']:.2f}")
    print(f"Optimal Cook Temperature: {result['cook_temp']:.2f} °C")
else:
    print("Optimization failed to converge.")
```

### Conclusion
By treating the pulping sequence not just as isolated silos but as a continuous mathematical system, PapAiEra allows process engineers to see how turning a dial in the Digester affects the steam budget in the Recovery Boiler. This allows mill managers to automate complex thermodynamic balances to hit quality targets at the absolute minimum cost.

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
*   **Solution:** The functions have built-in zero-division catches that will return `0.0`, but ensure you stream clean, non-zero denominator readings from your DCS historians to get meaningful OEE or Yield figures.
