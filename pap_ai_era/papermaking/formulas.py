"""
Papermaking Formulas Module
This module implements the formulas from:
1. Formula-PT.pdf
2. MassBalanceEquationsforRetentionandBasisWeightinaPaperMachine.pdf
3. Uhle_Box_Sizing.pdf
4. paper making formula.pdf (TAPPI TIP 0502-17)
"""
import math

# ==========================================
# 1. STOCK PREPARATION
# ==========================================

def calculate_npsh(p_atm, p_vapor, density, h_friction, z_height):
    """Net positive suction head (m)"""
    # NPSH = (p_atm - p_vapor)/(density * 9.81) - h_friction - z_height
    # Assuming standard gravity 9.81 m/s2
    return ((p_atm - p_vapor) / (density * 9.81)) - h_friction - z_height

def jet_mixer_entrainment(q_o, distance, nozzle_diameter):
    """Jet mixer entrained volume (qe)"""
    if distance > 4.3 * nozzle_diameter:
        return ((distance / (4.3 * nozzle_diameter)) - 1) * q_o
    return 0.0

def krofta_save_all_volume(radius, height):
    """Volume of Krofta save-all"""
    return math.pi * (radius ** 2) * height

def save_all_fiber_loss(fiber_in_effluent_kg_min, operating_days=350):
    """Fiber loss in mt/year"""
    return (fiber_in_effluent_kg_min * 60 * 24 * operating_days) / 1000

def stock_pump_throughput(capacity_l_min, consistency_pct):
    """Throughput in kg/min"""
    return (capacity_l_min * consistency_pct) / 100.0

def refining_specific_edge_load(p_total_kw, p_no_load_kw, cutting_length_km_sec):
    """Specific Edge Load (SEL) in J/m or W-s/m"""
    if cutting_length_km_sec == 0:
         return 0.0
    return (p_total_kw - p_no_load_kw) / cutting_length_km_sec

def refining_specific_energy(p_net_kw, throughput_t_h):
    """Specific energy in kWh/t"""
    if throughput_t_h == 0:
        return 0.0
    return p_net_kw / throughput_t_h

# ==========================================
# 2. WET END & HEADBOX
# ==========================================

def reynolds_number(diameter, velocity, kinematic_viscosity):
    """Reynolds number"""
    if kinematic_viscosity == 0: return 0
    return (diameter * velocity) / kinematic_viscosity

def water_per_ton_of_pulp(consistency_pct):
    """Water per ton ratio"""
    if consistency_pct == 0: return 0
    return (100 - consistency_pct) / consistency_pct

def drainage_index(b_constant, c_md_count, air_permeability_cfm):
    """Drainage Index (DI) of forming fabric"""
    return b_constant * c_md_count * air_permeability_cfm * 0.001 * 2.54

def fiber_support_index(a_constant, b_constant, m_cd_mesh, c_md_count):
    """Fiber Support Index (FSI)"""
    return (2.0 / 3.0) * ((a_constant * m_cd_mesh) + (2 * b_constant * c_md_count))

def spouting_velocity(head_ft):
    """Spouting velocity (ft/min) given head in ft"""
    return 481.5 * math.sqrt(head_ft)

def spouting_velocity_m_s(head_m):
    """Spouting velocity (m/s) given head in meters"""
    return math.sqrt(2 * 9.81 * head_m)

def wire_shake_number(frequency_strokes_min, amplitude_inch, wire_speed_fpm):
    """Fourdrinier shake number"""
    if wire_speed_fpm == 0: return 0
    return (frequency_strokes_min ** 2 * amplitude_inch) / wire_speed_fpm

def wire_shake_number_metric(frequency_strokes_min, amplitude_mm, wire_speed_mpm):
    """Fourdrinier shake number (metric)"""
    if wire_speed_mpm == 0: return 0
    return (frequency_strokes_min ** 2 * amplitude_mm) / wire_speed_mpm

def dandy_roll_speed(wire_speed_fpm, roll_diameter_ft):
    """Dandy roll rotational speed in RPM"""
    if roll_diameter_ft == 0: return 0
    return (wire_speed_fpm * 1.02) / (math.pi * roll_diameter_ft)

def drag_load_conventional(drive_volts, drive_amps, nominal_fabric_speed_fpm, fabric_width_in):
    """Drag load (lbf/in)"""
    if nominal_fabric_speed_fpm == 0 or fabric_width_in == 0: return 0
    return (drive_volts * drive_amps * 0.226) / (nominal_fabric_speed_fpm * fabric_width_in)

def basis_weight_from_slice(slice_opening_mm, headbox_consistency_pct):
    """GSM estimation from headbox"""
    return slice_opening_mm * headbox_consistency_pct * 10

# ==========================================
# 3. PRESS SECTION & UHLE BOX SIZING
# ==========================================

def press_nip_width(compression_cm, roll_1_radius_cm, roll_2_radius_cm):
    """Calculates full nip width (2b) in cm"""
    if (roll_1_radius_cm + roll_2_radius_cm) == 0: return 0
    re = (roll_1_radius_cm * roll_2_radius_cm) / (roll_1_radius_cm + roll_2_radius_cm)
    val = compression_cm - (2 * re)
    if val < 0: return 0
    return 2 * math.sqrt(val)

def crown_correction(nip_ends, nip_center, d1, d2):
    """Change in total crown of two rolls"""
    # C = (Ne^2 - Nc^2)*(D1 + D2)/(2*D1*D2)
    if d1 == 0 or d2 == 0: return 0
    return ((nip_ends**2) - (nip_center**2)) * (d1 + d2) / (2 * d1 * d2)

def press_impulse(press_line_load_kn_m, nip_speed_m_min):
    """Press impulse PI in MPa-s"""
    if nip_speed_m_min == 0: return 0
    return 0.060 * press_line_load_kn_m / nip_speed_m_min

def uhle_box_dwell_time(slot_width_mm, machine_speed_mpm):
    """Dwell time over Uhle Box in milliseconds"""
    if machine_speed_mpm == 0: return 0
    return (slot_width_mm / machine_speed_mpm) * 60

def vacuum_capacity_per_slot(slot_area_m2, avg_vacuum_factor=700):
    """Vacuum capacity in m3/min"""
    return slot_area_m2 * avg_vacuum_factor

# ==========================================
# 4. DRYER SECTION
# ==========================================

def drying_rate(machine_speed_mpm, basis_weight_kg_m2, water_evap_ratio, n_cylinders, diameter_m):
    """Drying rate (Rw) in kg/h-m2"""
    # Rw = (S * B * M * 60) / (N * pi * D * A) where A = 1 m2
    if (n_cylinders * math.pi * diameter_m) == 0: return 0
    return (machine_speed_mpm * basis_weight_kg_m2 * water_evap_ratio * 60) / (n_cylinders * math.pi * diameter_m)

def rimming_speed(diameter_ft, condensate_film_thickness_ft):
    """Rimming speed for 5-ft and 6-ft dryers in ft/min"""
    if diameter_ft == 0: return 0
    return (5720 - (2160 / diameter_ft)) * (condensate_film_thickness_ft ** (1/3.0))

def paper_web_draw(speed_initial, speed_final):
    """Percent draw between sections"""
    if speed_initial == 0: return 0
    return ((speed_final - speed_initial) / speed_initial) * 100

def paper_caliper_mm(basis_weight_gsm, density_kg_m3):
    """Paper caliper in mm"""
    if density_kg_m3 == 0: return 0
    return basis_weight_gsm / density_kg_m3

def roll_rotational_speed(speed_mpm, roll_diameter_m):
    """Roll RPM"""
    if roll_diameter_m == 0: return 0
    return 0.3183 * speed_mpm / roll_diameter_m

# ==========================================
# 5. MASS BALANCE & RETENTION EQUATIONS
# ==========================================

def headbox_consistency_mass_balance(thick_stock_cons, thick_stock_flow, thin_stock_flow, dil_water_cons):
    """Calculates thin stock consistency produced by given thick stock flow/cons and dilution"""
    if thin_stock_flow == 0: return 0
    # CHB = (Qs*Cs + Qd*Cd) / Qo
    # where Qo = Qs + Qd
    return ((thick_stock_flow * thick_stock_cons) + ((thin_stock_flow - thick_stock_flow) * dil_water_cons)) / thin_stock_flow

def basis_weight_mass_balance(thick_stock_flow, thick_stock_cons, slice_width, wire_speed, retention_ratio):
    """Basis weight G based on volume balance (g/m2)"""
    # G = (Qs * Cs * R) / (W * Vw)
    if slice_width == 0 or wire_speed == 0: return 0
    return (thick_stock_flow * thick_stock_cons * retention_ratio) / (slice_width * wire_speed)

def overall_retention_from_consistencies(headbox_cons, white_water_cons):
    """Retention ratio (R)"""
    if headbox_cons == 0: return 0
    return (headbox_cons - white_water_cons) / headbox_cons

def total_stock_volume(thick_stock_flow, thin_stock_flow, recirculation_constant):
    """Volume balance of stock"""
    return thick_stock_flow + (thin_stock_flow * recirculation_constant)
