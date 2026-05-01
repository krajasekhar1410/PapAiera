# PapAiEra API Reference

**PyPI URL**: [https://pypi.org/project/PapAiEra/](https://pypi.org/project/PapAiEra/) | **Install**: `pip install PapAiEra`

This document serves as the comprehensive list of all equations, calculations, and functions available in the PapAiEra library, based on the EU BREF 2015 Best Available Techniques (BAT) standards.

## 1. Pulping Modules (`pap_ai_era.pulping`)

### Kraft Pulping (`kraft.py`)
* `kappa_number(k_permanganate_consumed)`: Estimates Kappa Number (residual lignin).
* `chemical_recovery_efficiency(chemicals_recovered, chemicals_charged)`: Calculates chemical recovery loop efficiency (Target > 95%).
* `black_liquor_solids_content(solids_mass, total_mass)`: Percentage of dry solids in black liquor.
* `pulping_yield(dry_pulp_produced, dry_wood_charged)`: Yield of pulp from raw wood (45-55%).
* `check_kraft_bat_compliance(water_consumption, steam_consumption, elec_consumption)`: Validates Mill specific consumption against BREF standards.
* `calculate_h_factor(temperature_celsius, time_minutes)`: Integrates Arrhenius reaction rate targeting specific digester cooking curves.
* `calculate_pulpmill_mass_balance(wood_charged_bdmt, target_yield_pct, rejects_pct)`: Tracks mass conservation of accepted fiber, lost rejects, and dissolved black liquor organics.

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

### Bleaching Engine (`pap_ai_era.bleaching`)
The new bleaching engine provides a universal optimization framework.
* `Chemical(name, min_dosage, max_dosage, cost)`: Class representing a bleaching chemical.
* `BleachingStage(name, chemicals, model)`: Class for a single stage in a sequence.
* `BleachingSequence(stages, targets)`: Class for a full multi-stage sequence.
* `BleachingOptimizer(sequence)`: Cost optimization engine using Differential Evolution.
* `run_optimization_from_config(config, initial_state)`: High-level helper to run optimization from a JSON-like config.
* `ask_user_config()`: Interactive CLI tool for building bleaching models.

### Legacy Bleaching Utilities (`pap_ai_era.pulping.bleaching`)
* `oxygen_delignification_efficiency(kappa_in, kappa_out)`: Pre-bleach kappa drop.
* `theoretical_aox_generation(active_chlorine_multiple, kappa_to_bleach)`: Empirical determination of generated kg AOX based on ClO2 charge.
* `wash_press_efficiency(dissolved_solids_in, dissolved_solids_out)`: Brown stock washer displacement ratio preventing COD carry-over.

### Boiler Optimizer (`pap_ai_era.energy`)
The boiler optimizer provides a Digital Twin framework for efficiency control.
* `Boiler(config)`: Digital Twin class for a specific boiler type and fuel.
* `BoilerState(fuel, air, fw_temp, ...)`: Class representing a physical state.
* `BoilerOptimizer(boiler)`: Engine to find optimal setpoints (fuel/air) for max efficiency.

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
* `calculate_machine_fiber_balance(fiber_in_headbox_kg, wire_retention_pct, broke_generated_pct)`: Estimates net saleable paper by accounting for broke loops and effluent wire losses.
* `run_hood_optimization(params)`: High-level entry for dryer hood energy optimization.
* `HoodOptimizer`: Class managing evaporation load, fan power, and air recirculation tradeoffs.
* `BulkModel(n_layers)`: ML framework for predicting sheet bulk based on layer furnish and press conditions.

### Wet End Chemistry (`wet_end_chemistry.py`)
* `calculate_pump_flow_rate_lph(target_dose_kg_t, machine_production_t_h, concentration_gpl)`: Sets physical dosing pump targets from chemical concentration (GPL).
* `ash_retention_efficiency(headbox_ash_consistency, white_water_ash_consistency)`: Dedicated filler accounting.
* `suggest_furnish_dosing(hardwood_pct, softwood_pct, broke_pct, target_akd_sizing)`: Heuristic dosing ratios dynamically balancing Hardwood surface fines and Broke anionic trash.

### Moisture Prediction Models (`moisture_prediction.py`)
* `predict_wire_drainage_and_couch_moisture(target_gsm, machine_speed_mpm, wire_width_m, layer_data, vacuum_boxes)`: Empirically predicts drainage capabilities based on linear vacuum strengths.
* `predict_press_section_moisture(presses, inlet_moisture_pct, machine_speed_mpm)`: Nip dwell time linear load solver (incorporating Shoe Press configurations).
* `predict_dryer_group_moisture(dryer_groups, inlet_moisture_pct, target_gsm, machine_speed_mpm, width_m)`: Heat transfer extraction converting operating bar steam pressure to cylinder latency exchange efficiency.

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

### Digester Optimization
* `optimize_batch_kraft_digester(target_kappa, current_alkali_cost, current_wood_cost)`: Solves for optimal Active Alkali and Cook Temperature specifically bounded by Batch digester cycles and chemical economy.
* `optimize_continuous_kamyr_digester(target_kappa, liquor_to_wood_ratio_cost_penalty)`: Balances the required Impregnation/Cooking Liquor-to-Wood (L/W) ratio against the penalty of having to evaporate that excess water later in the cycle.

### Bleaching Sequence Solvers
* `optimize_bleaching_sequence_cost(sequence_type, incoming_kappa, target_brightness, chemical_costs)`: Non-linear allocation to reach a target ISO Brightness. Dynamically shifts matrix between **ECF** (Chlorine Dioxide $+$ NaOH) and **TCF** (Ozone $+$ Hydrogen Peroxide) rulesets based on individual chemical pricing.

### Chemical Recovery Control
* `optimize_sulphite_base_recovery(target_so2_recovery, steam_cost_gj, makeup_chemical_cost)`: Balances the use of live steam in the evaporators (which drives up recovery boiler efficiency) against the physical cost of buying fresh Mg/Ca makeup chemicals for the Sulphite cycle.

---

## 5. Supplementary Papermaking Formulas (`pap_ai_era.papermaking.formulas`)

### Stock Preparation
* `calculate_npsh(p_atm, p_vapor, density, h_friction, z_height)`: Net positive suction head.
* `jet_mixer_entrainment(q_o, distance, nozzle_diameter)`: Jet mixer entrained volume.
* `krofta_save_all_volume(radius, height)`: Volume of Krofta save-all.
* `save_all_fiber_loss(fiber_in_effluent_kg_min, operating_days)`: Fiber loss in mt/year.
* `stock_pump_throughput(capacity_l_min, consistency_pct)`: Throughput in kg/min.
* `refining_specific_edge_load(p_total_kw, p_no_load_kw, cutting_length_km_sec)`: Specific Edge Load (SEL).
* `refining_specific_energy(p_net_kw, throughput_t_h)`: Specific energy in kWh/t.

### Wet End & Headbox
* `reynolds_number(diameter, velocity, kinematic_viscosity)`: Fluid flow Reynolds number.
* `water_per_ton_of_pulp(consistency_pct)`: Water ratio per ton.
* `drainage_index(b_constant, c_md_count, air_permeability_cfm)`: Drainage Index (DI).
* `fiber_support_index(a_constant, b_constant, m_cd_mesh, c_md_count)`: Fiber Support Index (FSI).
* `spouting_velocity(head_ft)` / `spouting_velocity_m_s(head_m)`: Spouting velocity.
* `wire_shake_number(frequency_strokes_min, amplitude_inch, wire_speed_fpm)`: Fourdrinier shake number.
* `dandy_roll_speed(wire_speed_fpm, roll_diameter_ft)`: Dandy roll RPM.
* `drag_load_conventional(drive_volts, drive_amps, nominal_fabric_speed_fpm, fabric_width_in)`: Drag load.
* `basis_weight_from_slice(slice_opening_mm, headbox_consistency_pct)`: GSM estimation from headbox.

### Press Section & Uhle Box Sizing
* `press_nip_width(compression_cm, roll_1_radius_cm, roll_2_radius_cm)`: Nip width (2b) in cm.
* `crown_correction(nip_ends, nip_center, d1, d2)`: Change in total crown of two rolls.
* `press_impulse(press_line_load_kn_m, nip_speed_m_min)`: Press impulse.
* `uhle_box_dwell_time(slot_width_mm, machine_speed_mpm)`: Dwell time over Uhle Box.
* `vacuum_capacity_per_slot(slot_area_m2, avg_vacuum_factor)`: Vacuum capacity in m3/min.

### Dryer Section
* `drying_rate(machine_speed_mpm, basis_weight_kg_m2, water_evap_ratio, n_cylinders, diameter_m)`: Drying rate (Rw) in kg/h-m2.
* `rimming_speed(diameter_ft, condensate_film_thickness_ft)`: Rimming speed for dryers.
* `paper_web_draw(speed_initial, speed_final)`: Percent draw between sections.
* `paper_caliper_mm(basis_weight_gsm, density_kg_m3)`: Paper caliper in mm.
* `roll_rotational_speed(speed_mpm, roll_diameter_m)`: Roll RPM.

### Mass Balance Equations
* `headbox_consistency_mass_balance(thick_stock_cons, thick_stock_flow, thin_stock_flow, dil_water_cons)`: Thin stock consistency.
* `basis_weight_mass_balance(thick_stock_flow, thick_stock_cons, slice_width, wire_speed, retention_ratio)`: Basis weight G based on volume balance.
* `overall_retention_from_consistencies(headbox_cons, white_water_cons)`: Retention ratio (R).
* `total_stock_volume(thick_stock_flow, thin_stock_flow, recirculation_constant)`: Volume balance of stock.

## 4. Variability Analysis (`pap_ai_era.papermaking.variability_analysis`)

### Variance Partition Analysis (VPA)
* `compute_vpa(data, scan_col, box_col, value_col, process_average, goals, thresholds, sigma_convention)`: 
  Decomposes total variability (2-sigma) into:
  - **MDL**: Machine Direction Long-term (Scan Average trend)
  - **CD**: Cross Direction (Average Profile)
  - **MDS**: Machine Direction Short-term (Residual noise)
  Returns a `VPAResult` with normalisation, threshold status, and root-cause inferences.
