"""
Press Section & Vacuum System Formulas
Source: Formula-PT.pdf (VK Panigrahi), Uhle_Box_Sizing.pdf & TAPPI TIP 0502-17
"""
import math


# ── Press Nip ─────────────────────────────────────────────────

def press_nip_width(compression_cm, r1_cm, r2_cm):
    """Nip width 2b (cm). 2b = 2√(Δh - 2Re)
    Re = R1·R2/(R1+R2)"""
    if (r1_cm + r2_cm) == 0:
        return 0.0
    re = (r1_cm * r2_cm) / (r1_cm + r2_cm)
    val = compression_cm - 2.0 * re
    if val < 0:
        return 0.0
    return 2.0 * math.sqrt(val)


def nip_load(piston_diameter_cm, operating_pressure_kg_cm2, roll_weight_kg,
             nip_width_cm, top_loading=True):
    """Nip load (kg/cm).
    = [2×(π/4)×d²×P ± W] / LN"""
    if nip_width_cm == 0:
        return 0.0
    force = 2.0 * (math.pi / 4.0) * (piston_diameter_cm ** 2) * operating_pressure_kg_cm2
    if top_loading:
        force += roll_weight_kg
    else:
        force -= roll_weight_kg
    return force / nip_width_cm


def nip_load_with_leverage(piston_diameter_cm, operating_pressure_kg_cm2,
                            leverage_ratio, roll_weight_kg, nip_width_cm,
                            top_loading=True):
    """Nip load with lever device (kg/cm)."""
    if nip_width_cm == 0:
        return 0.0
    force = 2.0 * (math.pi / 4.0) * (piston_diameter_cm ** 2) * operating_pressure_kg_cm2 * leverage_ratio
    if top_loading:
        force += roll_weight_kg
    else:
        force -= roll_weight_kg
    return force / nip_width_cm


def press_impulse_english(press_line_load_lbf_in, nip_speed_fpm):
    """Press impulse (PSI·s). PI = 5 × PLL / Speed"""
    if nip_speed_fpm == 0:
        return 0.0
    return 5.0 * press_line_load_lbf_in / nip_speed_fpm


def press_impulse_metric(press_line_load_kn_m, nip_speed_mpm):
    """Press impulse (MPa·s). PI = 0.060 × PLL / Speed"""
    if nip_speed_mpm == 0:
        return 0.0
    return 0.060 * press_line_load_kn_m / nip_speed_mpm


def water_in_paper_leaving_press(production_ad_kg_min, dryness_after_press_pct):
    """Water in paper leaving press (kg/min)."""
    if dryness_after_press_pct == 0:
        return 0.0
    return production_ad_kg_min * ((100.0 - dryness_after_press_pct) / dryness_after_press_pct)


def water_out_of_press(production_ad_kg_min, dryness_before_pct, dryness_after_pct):
    """Water squeezed out of press (kg/min)."""
    if dryness_before_pct == 0 or dryness_after_pct == 0:
        return 0.0
    water_before = (100.0 - dryness_before_pct) / dryness_before_pct
    water_after = (100.0 - dryness_after_pct) / dryness_after_pct
    return production_ad_kg_min * (water_before - water_after)


def press_dryness_improvement_steam_savings(dryness_before_pct, dryness_after_pct,
                                             reel_dryness_pct=95.0):
    """Approximate % reduction in steam drying load from +1% press dryness."""
    m_before = (reel_dryness_pct / dryness_before_pct) - 1.0
    m_after = (reel_dryness_pct / dryness_after_pct) - 1.0
    if m_before == 0:
        return 0.0
    return ((m_before - m_after) / m_before) * 100.0


# ── Crown & Roll Correction ──────────────────────────────────

def crown_correction(nip_end_width, nip_center_width, d1, d2):
    """Change in total crown of two rolls.
    C = (Ne²-Nc²)×(D1+D2) / (2×D1×D2)"""
    if d1 == 0 or d2 == 0:
        return 0.0
    return ((nip_end_width ** 2) - (nip_center_width ** 2)) * (d1 + d2) / (2.0 * d1 * d2)


def crown_correction_equal_rolls(nip_end_width, nip_center_width, diameter):
    """Crown correction for equal diameter rolls. C = (Ne²-Nc²) / D"""
    if diameter == 0:
        return 0.0
    return ((nip_end_width ** 2) - (nip_center_width ** 2)) / diameter


def roll_deflection(unit_load, face, bearing_dist, modulus_elasticity, moment_of_inertia):
    """Roll deflection over face (in or m).
    d = w×F³×(12B - 7F) / (384×E×I)"""
    denom = 384.0 * modulus_elasticity * moment_of_inertia
    if denom == 0:
        return 0.0
    return (unit_load * (face ** 3) * (12.0 * bearing_dist - 7.0 * face)) / denom


def moment_of_inertia(outside_diameter, inside_diameter):
    """Moment of inertia (in⁴ or m⁴). I = 0.0491 × (Do⁴ - Di⁴)"""
    return 0.0491 * ((outside_diameter ** 4) - (inside_diameter ** 4))


# ── Vacuum Component ─────────────────────────────────────────

def vacuum_component_line_load_english(vacuum_box_width_in, vacuum_in_hg):
    """Vacuum component line load (lbf/in). = box_width × vacuum / 3"""
    return (vacuum_box_width_in * vacuum_in_hg) / 3.0


def vacuum_component_line_load_metric(vacuum_box_width_m, vacuum_kpa):
    """Vacuum component line load (kN/m). = box_width × vacuum / 1.5"""
    return (vacuum_box_width_m * vacuum_kpa) / 1.5


# ── Felt & Press Fabric ──────────────────────────────────────

def felt_tension_simple(total_weight_lbs, clothing_width_in):
    """Felt tension (pli) for equal diameter pulleys. T = W / (2×width)"""
    if clothing_width_in == 0:
        return 0.0
    return total_weight_lbs / (2.0 * clothing_width_in)


def felt_tension_different_pulleys(total_weight_lbs, outer_dia_in,
                                    clothing_width_in, inner_dia_in):
    """Felt tension (pli) for different diameter pulleys.
    T = (W × Do) / (2 × width × Di)"""
    if clothing_width_in == 0 or inner_dia_in == 0:
        return 0.0
    return (total_weight_lbs * outer_dia_in) / (2.0 * clothing_width_in * inner_dia_in)


def dryer_felt_tension_english(weight_lbf, d2, felt_width_in, d1):
    """Dryer felt tension hanging weight (lbf/in).
    T = W×D2 / (2×FW×D1)"""
    if felt_width_in == 0 or d1 == 0:
        return 0.0
    return (weight_lbf * d2) / (2.0 * felt_width_in * d1)


def dryer_felt_tension_metric(mass_kg, d2_m, felt_width_m, d1_m):
    """Dryer felt tension hanging weight (kN/m).
    T = 0.00981×W×D2 / (2×FW×D1)"""
    if felt_width_m == 0 or d1_m == 0:
        return 0.0
    return (0.00981 * mass_kg * d2_m) / (2.0 * felt_width_m * d1_m)


def press_felt_unit_area_weight(felt_weight_lbs, felt_length_ft, felt_width_in):
    """Press felt unit area weight (gsm). Zt = M×58590 / (L×W)"""
    if felt_length_ft == 0 or felt_width_in == 0:
        return 0.0
    return (felt_weight_lbs * 58590.0) / (felt_length_ft * felt_width_in)


def coefficient_of_friction(tension_f, tension_w, wrap_angle_rad):
    """Coefficient of friction. F/W = e^(µ×A) → µ = ln(F/W)/A"""
    if wrap_angle_rad == 0 or tension_w == 0:
        return 0.0
    return math.log(tension_f / tension_w) / wrap_angle_rad


# ── Uhle Box / Suction / Vacuum ──────────────────────────────

def uhle_box_dwell_time_ms(slot_width_mm, machine_speed_mpm):
    """Dwell time over Uhle Box (milliseconds).
    Required: 2-4 ms for successful water removal."""
    if machine_speed_mpm == 0:
        return 0.0
    return (slot_width_mm / machine_speed_mpm) * 60.0


def vacuum_capacity_per_slot(slot_area_m2, vacuum_factor=700):
    """Vacuum capacity (m³/min). Factor 660-970 m³/min/m²."""
    return slot_area_m2 * vacuum_factor


def suction_roll_vacuum_tension(friction_coeff, vacuum_mmh2o, box_width_mm):
    """Suction roll vacuum tension Tv (kg/m).
    Tv = 10⁻³ × µ × v × w"""
    return 0.001 * friction_coeff * vacuum_mmh2o * box_width_mm


def suction_couch_cfm(speed_fpm, face_width_ft, hole_depth_ft,
                       open_area_pct, ambient_pressure_inhg, suction_vac_inhg):
    """Suction couch vacuum (CFM).
    CFM = V×b×s×E×M; M = (P2/P1)^0.9 - 1"""
    if suction_vac_inhg == 0:
        return 0.0
    expansion = ((ambient_pressure_inhg / suction_vac_inhg) ** 0.9) - 1.0
    return speed_fpm * face_width_ft * hole_depth_ft * (open_area_pct / 100.0) * expansion


def suction_couch_wasted_volume(drilled_area_pct, drilled_width_m,
                                 speed_mpm, shell_thickness_cm,
                                 vacuum_mmhg, p_atm_mmhg=760):
    """Suction couch wasted volume (m³/sec)."""
    if p_atm_mmhg == 0:
        return 0.0
    return (drilled_area_pct / 100.0) * drilled_width_m * speed_mpm * (shell_thickness_cm / 100.0) * (vacuum_mmhg / p_atm_mmhg)


def uhle_box_pipe_diameter_mm(air_flow_m3_hr):
    """Uhle box minimum pipe diameter (mm). = √(Q × 19.89)"""
    return math.sqrt(air_flow_m3_hr * 19.89)


def separator_to_vacuum_pump_diameter_mm(air_flow_m3_hr):
    """Pre-separator to vacuum pump pipe diameter (mm). = √(Q × 12.53)"""
    return math.sqrt(air_flow_m3_hr * 12.53)


def separator_diameter_mm(air_flow_m3_hr):
    """Separator diameter (mm). = √(Q × 92.83)"""
    return math.sqrt(air_flow_m3_hr * 92.83)


def separator_height_mm(separator_dia_mm):
    """Separator height (mm) = 2 × separator diameter"""
    return 2.0 * separator_dia_mm


def barometric_leg_diameter_mm(air_flow_m3_hr):
    """Barometric leg minimum diameter (mm). = √(Q × 8.7)"""
    return math.sqrt(air_flow_m3_hr * 8.7)


def barometric_leg_length_m(vacuum_reading_mmhg):
    """Barometric leg minimum length (m). = 0.0136 × vac + 0.9"""
    return 0.0136 * vacuum_reading_mmhg + 0.9


def flat_box_water_removed(incoming_cy_pct, outgoing_cy_pct):
    """Water removed per kg of stock (liter/kg).
    = 100 × [(1/Cin) - (1/Cout)]"""
    if incoming_cy_pct == 0 or outgoing_cy_pct == 0:
        return 0.0
    return 100.0 * ((1.0 / incoming_cy_pct) - (1.0 / outgoing_cy_pct))


def flat_box_air_removed(water_removed_l_kg):
    """Air removed per kg of paper (liter/kg). Air:Water = 10:1"""
    return water_removed_l_kg * 10.0


def flat_box_air_per_m2(water_removed_l_kg, gsm):
    """Air per m² of paper (liter/m²)."""
    return (water_removed_l_kg * 10.0 * gsm) / 1000.0


def air_flow_for_felt_dewatering(p_sp_inhg, dwell_ms, felt_perm_cfm_ft2, moisture_in):
    """Specific air flow through felt at suction tube (scfm/m²).
    V1 = [0.069 × Psp^0.476 × td^0.110 × V*^0.916] / Mp1^0.628"""
    if moisture_in == 0:
        return 0.0
    return (0.069 * (p_sp_inhg ** 0.476) * (dwell_ms ** 0.110) * (felt_perm_cfm_ft2 ** 0.916)) / (moisture_in ** 0.628)


def felt_moisture_leaving(moisture_in, v1, p_sp, td):
    """Felt moisture content leaving suction tube (lb H2O/lb felt).
    Mp2 = 1.23 × Mp1^0.819 / (V1^0.024 × Psp^0.124 × td^0.096)"""
    denom = (v1 ** 0.024) * (p_sp ** 0.124) * (td ** 0.096)
    if denom == 0:
        return 0.0
    return (1.23 * (moisture_in ** 0.819)) / denom


def fan_pump_power_kw(flow_m3_s, pressure_kpa, pump_efficiency_pct):
    """Fan pump electrical power (kW). P = Q × Δp × (100/η) × K3
    K3 = 1/138.54"""
    if pump_efficiency_pct == 0:
        return 0.0
    return flow_m3_s * pressure_kpa * (100.0 / pump_efficiency_pct) * (1.0 / 138.54)
