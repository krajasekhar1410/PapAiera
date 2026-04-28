# PapAiEra API Reference
This document serves as the comprehensive list of all equations, calculations, and functions available in the PapAiEra library, based on the EU BREF 2015 Best Available Techniques (BAT) standards.

## 1. Pulping Modules (`pap_ai_era.pulping`)

### Kraft Pulping (`kraft.py`)
* `kappa_number(k_permanganate_consumed)`: Estimates Kappa Number (residual lignin).
* `chemical_recovery_efficiency(chemicals_recovered, chemicals_charged)`: Calculates chemical recovery loop efficiency (Target > 95%).
* `black_liquor_solids_content(solids_mass, total_mass)`: Percentage of dry solids in black liquor.
* `pulping_yield(dry_pulp_produced, dry_wood_charged)`: Yield of pulp from raw wood (45-55%).
* `check_kraft_bat_compliance(water_consumption, steam_consumption, elec_consumption)`: Validates Mill specific consumption against BREF standards.

### Sulphite Pulping (`sulphite.py`)
* `chemical_recovery_efficiency_sulphite(so2_recovered, so2_charged, base_recovered, base_charged)`: Mg/Ca base and SO2 recovery rates.
* `sulphite_yield(dry_pulp_produced, dry_wood_charged, is_dissolving_pulp)`: Handles varying yields for paper grade vs. viscose/dissolving pulps.
* `evaluate_sulphite_bat_compliance(water_consumption, steam_consumption, elec_consumption)`: Specific compliance metrics strictly for Sulphite.

### Mechanical Pulping (`mechanical.py`)
* `specific_energy_refining(electricity_used_mwh, pulp_produced_tonnes, process_type)`: Energy intensity of SGW, PGW, TMP, and CTMP.
* `heat_recovery_efficiency(recovered_steam_gj, grinding_refining_energy_gj)`: Measurement of steam generation derived off TMP refiners.
* `mechanical_yield(dry_pulp_produced, dry_wood_charged, process_type)`: High yield tracking (>90-95%).

### Recycled Fibre (`recycled.py`)
* `deinking_yield(ink_removed, total_ink, fibre_loss)`: Calculates both physical fiber loss and ink removal efficiency.
* `rcf_rejects_rate(rejects_mass, input_rcf_mass)`: Heavy and light rejects ratio out of the pulper.
* `specific_energy_rcf(electricity_used, pulp_produced, grade)`: Consumption benchmarking for packaging vs newsprint vs tissue RCF lines.

### Non-Wood / Bagasse (`non_wood.py`)
* `depithing_efficiency(pith_removed_kg, total_initial_pith_kg)`: Measures separation of fibers from agricultural pith (essential for bagasse).
* `silica_load_black_liquor(silica_in_raw_material_kg, black_liquor_volume_m3)`: Calculates kg/m3 of SiO2 entering the evaporators to warn against scaling.
* `non_wood_yield(dry_pulp_produced, bone_dry_depithed_bagasse)`: Yield calculations specifically modeled on depithed biomass.

### Bleaching & Delignification (`bleaching.py`)
* `oxygen_delignification_efficiency(kappa_in, kappa_out)`: Pre-bleach kappa drop.
* `theoretical_aox_generation(active_chlorine_multiple, kappa_to_bleach)`: Empirical determination of generated kg AOX based on ClO2 charge.
* `wash_press_efficiency(dissolved_solids_in, dissolved_solids_out)`: Brown stock washer displacement ratio preventing COD carry-over.

### Chemical Recovery Cycle (`recovery_cycle.py`)
* `causticizing_efficiency(naoh_conc, na2co3_conc)`: Efficiency of converting Green liquor to White liquor in the causticizing plant.
* `lime_kiln_specific_energy(fuel_energy_gj, lime_produced_tonnes)`: Checks if fuel usage stays between 5.5 and 7.5 GJ/t CaO.
* `evaporator_steam_economy(water_evaporated_tonnes, steam_used_tonnes)`: Measures the cascade efficiency (t_water / t_steam).
* `reduction_efficiency_recovery_boiler(na2s_conc, na2so4_conc)`: Lower furnace sulphate reduction calculation.

---

## 2. Papermaking Modules (`pap_ai_era.papermaking`)

### Paper Machine Operations (`machine.py`)
* `machine_oee(availability, performance, quality)`: Overall Equipment Effectiveness.
* `broke_percentage(broke_mass, total_production)`: Percentage of reel production returning to the repulper.
* `overall_retention(white_water_consistency, headbox_consistency)`: Wire section first-pass retention rate.
* `drying_efficiency(steam_used_in_dryers, water_evaporated)`: Validates specific evaporation steam economy against ~1.2 - 1.4 BAT averages.

### Coating & Finishing (`coating.py`)
* `coating_colour_loss(colour_to_effluent_kg, total_colour_applied_kg)`: Evaluates losses to the biological effluent system.
* `coating_solids_recovery_efficiency(solids_recovered, solids_in_wash_water)`: E.g., Ultrafiltration station efficiency for recycling binders and pigments.
* `specific_water_coating(water_used_m3, coated_paper_produced_tonnes)`: Water balance explicitly dedicated to the coating kitchen.

---

## 3. Sustainability Modes (`pap_ai_era.sustainability`)

### Raw Emissions (`emissions.py`)
* `specific_cod_load()`, `specific_bod_load()`, `specific_tss_load()`, `aox_emissions()`: All calculate discharge in kg per Air Dry tonne (ADt).
* `evaluate_water_effluent_bat()`: Bulk compliance validator.

### Air Emissions (`air_emissions.py`)
* `total_reduced_sulphur(recovery_boiler_trs, lime_kiln_trs, ncg_trs, production_admt)`: Captures the odorous gas sum.
* `nox_emissions_factor(nox_kg, fuel_energy_gj)`: Outputs kg/GJ specific energy boiler rates.
* `dust_emissions(flow_rate_nm3_h, dust_conc_mg_nm3, operating_hours, production_admt)`: Combines stack velocities and concentrations to kg/ADt.
* `so2_emissions_kg_adt(so2_kg, production_admt)`: Sum SO2 release.

### Wastewater Treatment Plant (WWTP) (`wastewater.py`)
* `wwtp_removal_efficiency(influent_conc, effluent_conc)`: Internal destruction rate of biological systems.
* `specific_effluent_volume(effluent_m3, cooling_water_m3, production_admt)`: Net process water strictly calculating contaminated flows, excluding cooling networks.
* `nitrogen_phosphorus_discharge(tot_n_kg, tot_p_kg, production_admt)`: Total nutrient slip.

### Water & Energy Consumption (`water_energy.py`)
* `specific_water_consumption()`, `specific_energy_consumption()`
* `process_water_recycling_rate()`: Degree of short/long loop white water closure.

### Environmental Management System (EMS) (`management.py`)
* `ems_scorecard()`: Validates mill against ISO14001, Continuous Emission Monitoring Systems (CEMS), and minimization plans.
* `calculate_total_solid_waste()`: Sludge + Rejects + Ash total to landfill score.
* `material_efficiency()`: Saleable tons over gross inputs.

---

## 4. AI/Math Tools (`pap_ai_era.optimization_models`)

### Model Example
* `optimize_kraft_digester(target_kappa, current_alkali_cost, current_wood_cost)`: Uses SciPy (`scipy.optimize.minimize`) to establish the cheapest operational point (temperature and alkali bounds) mathematically required to hit a specific Kappa number while considering linear yield drops.
