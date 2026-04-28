import math

def predict_wire_drainage_and_couch_moisture(target_gsm, machine_speed_mpm, wire_width_m, layer_data, vacuum_boxes):
    '''
    Predicts the drainage rate and exit moisture at the couch roll based on vacuum boxes.
    layer_data: list of dicts, e.g. [{'gsm': 50, 'wire_type': 'top'}, {'gsm': 100, 'wire_type': 'bottom'}]
    vacuum_boxes: list of dicts, e.g. [{'vacuum_kpa': 15}, {'vacuum_kpa': 25}, {'vacuum_kpa': 40}]
    Returns: dict with total drainage flow, before couch moisture, after couch moisture
    '''
    if target_gsm <= 0 or machine_speed_mpm <= 0:
        return {'error': 'Invalid parameters'}
        
    production_t_h = (target_gsm / 1000.0) * wire_width_m * (machine_speed_mpm * 60.0) / 1000.0
    
    # Starting consistency at headbox is usually ~0.5% (99.5% moisture)
    initial_water_mass = production_t_h * (99.5 / 0.5) 
    
    # Calculate vacuum force
    total_vacuum_kpa = sum([box.get('vacuum_kpa', 0) for box in vacuum_boxes])
    
    # Base drainage model: dependent on square root of vacuum, inversely proportional to GSM (resistance)
    drainage_efficiency = min(0.95, (math.sqrt(total_vacuum_kpa + 50) / 100.0) * (150.0 / target_gsm))
    
    # Adjust for multiple wires (top formers increase drainage)
    if len(layer_data) > 1:
        drainage_efficiency = min(0.95, drainage_efficiency * 1.15)
        
    # Before couch: normally drops to ~85% moisture
    moisture_before_couch = 99.5 - (drainage_efficiency * 14.5)
    
    # Couch roll high vacuum: pulls down to ~78-82%
    couch_vacuum = vacuum_boxes[-1].get('vacuum_kpa', 50) if vacuum_boxes else 50
    couch_drop = (couch_vacuum / 100.0) * 5.0
    moisture_after_couch = moisture_before_couch - couch_drop
    
    return {
        'total_drainage_m3_h': initial_water_mass * drainage_efficiency,
        'moisture_before_couch_pct': moisture_before_couch,
        'moisture_after_couch_pct': moisture_after_couch
    }

def predict_press_section_moisture(presses, inlet_moisture_pct, machine_speed_mpm, nip_width_mm=50):
    '''
    Calculates stage-wise moisture drop linearly across press nips based on Linear Load.
    presses: list of dicts, e.g. [{'linear_load_kn_m': 60}, {'linear_load_kn_m': 90, 'shoe_press': True}]
    '''
    current_moisture = inlet_moisture_pct
    stage_moistures = []
    
    for i, press in enumerate(presses):
        load = press.get('linear_load_kn_m', 50)
        is_shoe = press.get('shoe_press', False)
        
        # Shoe press has a wider nip, giving more dwell time (impulse = load / speed * time)
        nip_factor = 2.5 if is_shoe else 1.0
        
        # Empirical nip dewatering equation (highly simplified)
        # Moisture drop depends on impulse relative to speed resistance
        drop = (math.sqrt(load) * nip_factor * 200.0) / machine_speed_mpm
        
        # Diminishing returns: harder to remove water as sheet gets drier
        difficulty = (current_moisture - 45.0) / 50.0 
        actual_drop = drop * max(0.1, difficulty)
        
        current_moisture = max(40.0, current_moisture - actual_drop)
        stage_moistures.append({
            'press_index': i + 1,
            'exit_moisture_pct': current_moisture
        })
        
    return {
        'final_press_moisture_pct': current_moisture,
        'stage_breakdown': stage_moistures
    }

def predict_dryer_group_moisture(dryer_groups, inlet_moisture_pct, target_gsm, machine_speed_mpm, width_m):
    '''
    Estimates evaporation rates per dryer group using condensing steam logic.
    dryer_groups: list of dicts, e.g. [{'cylinders': 8, 'steam_pressure_bar': 1.5}, {'cylinders': 12, 'steam_pressure_bar': 3.0}]
    '''
    current_moisture = inlet_moisture_pct
    stage_moistures = []
    
    # Fixed parameters
    cylinder_diameter_m = 1.5
    contact_wrap_angle = 180  # degrees
    contact_area_per_cyl = math.pi * cylinder_diameter_m * width_m * (contact_wrap_angle / 360.0)
    
    # Total bone dry mass flux (kg/h)
    bd_flux_kg_h = (target_gsm / 1000.0) * width_m * (machine_speed_mpm * 60.0)
    
    for i, group in enumerate(dryer_groups):
        cyls = group.get('cylinders', 10)
        pressure = group.get('steam_pressure_bar', 2.0)
        
        # Estimate saturation temperature from pressure (bar)
        # Temp approx 100 + 20 * sqroot(pressure)
        temp_c = 100.0 + 20.0 * math.sqrt(max(0, pressure))
        
        total_group_area = cyls * contact_area_per_cyl
        
        # Heat transfer rate (kW) - assumes simplified U-value of ~250 W/m2K
        delta_t = temp_c - 80.0  # Assumed sheet temp 80C
        heat_transfer_kw = (250.0 * total_group_area * delta_t) / 1000.0
        
        # Latent heat of vaporization ~ 2260 kJ/kg = kW*s
        water_evaporated_kg_h = (heat_transfer_kw * 3600.0) / 2260.0
        
        # Current water mass entering
        water_mass_in_kg_h = bd_flux_kg_h * (current_moisture / (100.0 - current_moisture))
        
        water_mass_out_kg_h = max(0.01, water_mass_in_kg_h - water_evaporated_kg_h)
        
        # Recalculate moisture
        new_moisture = (water_mass_out_kg_h / (bd_flux_kg_h + water_mass_out_kg_h)) * 100.0
        
        # Enforce physical limit (paper rarely goes below 3-4% moisture)
        current_moisture = max(4.0, new_moisture)
        
        stage_moistures.append({
            'group_index': i + 1,
            'cylinder_temp_est_c': temp_c,
            'water_evaporated_kg_h': water_evaporated_kg_h,
            'exit_moisture_pct': current_moisture
        })
        
    return {
        'final_reel_moisture_pct': current_moisture,
        'group_breakdown': stage_moistures
    }
