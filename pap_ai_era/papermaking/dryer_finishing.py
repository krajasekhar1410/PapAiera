"""
Dryer Section, Finishing, Mechanical & General Formulas
Source: Formula-PT.pdf (VK Panigrahi) & TAPPI TIP 0502-17
"""
import math


# ── Drying Rate ───────────────────────────────────────────────

def water_evap_ratio(leaving_dryness_pct, entering_dryness_pct):
    """Weight of water evaporated per unit weight of paper. M = (L/E) - 1"""
    if entering_dryness_pct == 0:
        return 0.0
    return (leaving_dryness_pct / entering_dryness_pct) - 1.0


def drying_rate_metric(speed_mpm, basis_weight_kg_m2, m_ratio, n_cylinders, diameter_m):
    """Drying rate Rw (kg/h·m²). Rw = 60×S×B×M / (N×π×D)"""
    denom = n_cylinders * math.pi * diameter_m
    if denom == 0:
        return 0.0
    return (60.0 * speed_mpm * basis_weight_kg_m2 * m_ratio) / denom


def drying_capacity(n_cylinders, diameter_m, deckle_m, wrap_angle_deg=220, drying_rate_kg_hr_m2=14):
    """Drying capacity (kg/hr).
    = (N×π×D×W×α/360) × drying_rate"""
    wrapped_area = n_cylinders * math.pi * diameter_m * deckle_m * wrap_angle_deg / 360.0
    return wrapped_area * drying_rate_kg_hr_m2


def approx_number_of_dryers(production_kg_hr, m_ratio, evap_rate, trim_ft, dryer_dia_ft):
    """Approximate number of dryers. N = (P×M) / (EV×T×D)"""
    denom = evap_rate * trim_ft * dryer_dia_ft
    if denom == 0:
        return 0.0
    return (production_kg_hr * m_ratio) / denom


def l_factor(speed_fpm, basis_weight_lb_ream, n_dryers, c_value=785.4):
    """L factor (lb paper/ft²·hr). = S×W / (C×N)
    C values: 4ft=628.3, 5ft=785.4, 6ft=942.5"""
    if c_value == 0 or n_dryers == 0:
        return 0.0
    return (speed_fpm * basis_weight_lb_ream) / (c_value * n_dryers)


def evaporative_drying_rate(t_sat_f, grade='kraft_avg'):
    """Evaporative drying rate curves Y (lb water/hr-ft²).
    Grades: tissue_avg, tissue_good, kraft_avg, kraft_good,
    newsprint_avg, newsprint_good, writing_avg, writing_good,
    board_avg, board_good, pulp_avg, pulp_good, book_avg, book_good,
    glassine_avg, glassine_good"""
    curves = {
        'tissue_avg': (1.95/100, -3.395),
        'tissue_good': (2.125/100, -3.0625),
        'kraft_avg': (2.03/100, -3.83),
        'kraft_good': (2.3/100, -3.23),
        'newsprint_avg': (3.0/100, -5.1),
        'newsprint_good': (3.0/100, -4.8),
        'writing_avg': (1.5625/100, -2.40625),
        'writing_good': (1.375/100, -1.5375),
        'board_avg': (1.40625/100, -1.878),
        'board_good': (1.5/100, -1.6),
        'pulp_avg': (1.32/100, -2.27),
        'pulp_good': (0.9375/100, -0.96875),
        'book_avg': (1.04166/100, -0.93748),
        'book_good': (1.67/100, -2.26),
        'glassine_avg': (3.33/100, -6.5),
        'glassine_good': (3.5/100, -6.45),
    }
    slope, intercept = curves.get(grade, (2.03/100, -3.83))
    return slope * t_sat_f + intercept


def rimming_speed_fpm(inside_diameter_ft, condensate_film_ft):
    """Rimming speed (ft/min) for dryers.
    = [5720 - (2160/D)] × L^(1/3)"""
    if inside_diameter_ft == 0:
        return 0.0
    return (5720.0 - (2160.0 / inside_diameter_ft)) * (condensate_film_ft ** (1.0/3.0))


# ── Steam & Heat ──────────────────────────────────────────────

def steam_requirement(od_production_mt_hr, m_ratio, steam_factor=1.5):
    """Steam requirement (mt/hr). = Q × 1.5"""
    return od_production_mt_hr * m_ratio * steam_factor


def steam_header_pipe_diameter(max_steam_consumption_kg_hr, steam_velocity_m_s, steam_density_kg_m3=2.62):
    """Steam header pipe internal diameter (m).
    di = √[(4×Dsc) / (π×Vs×ρs×3600)]"""
    denom = math.pi * steam_velocity_m_s * steam_density_kg_m3 * 3600.0
    if denom == 0:
        return 0.0
    return math.sqrt((4.0 * max_steam_consumption_kg_hr) / denom)


def sensible_heat(mass_kg, specific_heat, delta_temp):
    """Sensible heat (kcal). = M × C × ΔT"""
    return mass_kg * specific_heat * delta_temp


def heat_exchanger_balance(cold_water_flow, heat_coeff, t_out, t_in, steam_enthalpy, condensate_enthalpy):
    """Steam flow for heat exchanger. SF = WF×C×(To-Ti) / (H-h)"""
    denom = steam_enthalpy - condensate_enthalpy
    if denom == 0:
        return 0.0
    return (cold_water_flow * heat_coeff * (t_out - t_in)) / denom


def total_water_to_evaporate(tpd, m_ratio):
    """Kg water evaporated per hour. = (tpd×1000×M) / 24"""
    return (tpd * 1000.0 * m_ratio) / 24.0


def heat_machine_efficiency(t_high_k, t_low_k):
    """Carnot efficiency. η = 1 - Tc/Th"""
    if t_high_k == 0:
        return 0.0
    return 1.0 - (t_low_k / t_high_k)


def syphon_angle(dryer_speed_mpm, dryer_radius_m, g=9.81):
    """Syphon angle (degrees). θ = atan(g×r / v²)"""
    v_m_s = dryer_speed_mpm / 60.0
    if v_m_s == 0:
        return 90.0
    return math.degrees(math.atan((g * dryer_radius_m) / (v_m_s ** 2)))


# ── Paper Web & Draw ──────────────────────────────────────────

def paper_web_draw(speed_initial, speed_final):
    """Paper web draw (%). = (SF - SI) / SI × 100"""
    if speed_initial == 0:
        return 0.0
    return ((speed_final - speed_initial) / speed_initial) * 100.0


def tissue_crepe_method1(yankee_speed, reel_speed):
    """Tissue crepe method 1 (%). = (Yankee - Reel)/Reel × 100"""
    if reel_speed == 0:
        return 0.0
    return ((yankee_speed - reel_speed) / reel_speed) * 100.0


def tissue_crepe_method2(yankee_speed, reel_speed):
    """Tissue crepe method 2 (%). = (Yankee - Reel)/Yankee × 100"""
    if yankee_speed == 0:
        return 0.0
    return ((yankee_speed - reel_speed) / yankee_speed) * 100.0


# ── Production ────────────────────────────────────────────────

def production_mt_day(gsm, deckle_m, speed_mpm):
    """Production (mt/day). = gsm × deckle × speed × 1.44 / 1000"""
    return (gsm * deckle_m * speed_mpm * 1.44) / 1000.0


def instantaneous_production_metric(speed_mpm, basis_weight_gsm, reel_trim_m):
    """Instantaneous production rate (kg/h). P = S × BW × T × 0.06"""
    return speed_mpm * basis_weight_gsm * reel_trim_m * 0.06


def machine_speed_from_production(mt_day, gsm, deckle_m):
    """Paper machine speed (m/min) from daily production."""
    if gsm == 0 or deckle_m == 0:
        return 0.0
    return (mt_day * 1000.0 / 86400.0) / (gsm / 1000.0) / deckle_m * 60.0


def paper_caliper_mm(basis_weight_gsm, density_kg_m3):
    """Paper caliper (mm). = BW / density"""
    if density_kg_m3 == 0:
        return 0.0
    return basis_weight_gsm / density_kg_m3


def lineal_paper_on_roll_metric(od_m, id_m, caliper_m):
    """Lineal paper on roll (m). L = π×(OD²-ID²) / (4×caliper)"""
    if caliper_m == 0:
        return 0.0
    return math.pi * ((od_m ** 2) - (id_m ** 2)) / (4.0 * caliper_m)


def estimated_net_weight_roll(r1_cm, r2_cm, bulk_cc_g, deckle_cm):
    """Estimated net weight of paper roll (kg).
    = π×(r1²-r2²)×(1/bulk)×deckle / 1000"""
    if bulk_cc_g == 0:
        return 0.0
    return math.pi * ((r1_cm ** 2) - (r2_cm ** 2)) * (1.0 / bulk_cc_g) * deckle_cm / 1000.0


def moisture_content_pct(original_weight, dry_weight):
    """Moisture content (%). = 100×(W-w)/W"""
    if original_weight == 0:
        return 0.0
    return 100.0 * (original_weight - dry_weight) / original_weight


# ── Rolls & Mechanical ───────────────────────────────────────

def roll_rotational_speed_metric(speed_mpm, roll_diameter_m):
    """Roll RPM. = 0.3183 × V / Do"""
    if roll_diameter_m == 0:
        return 0.0
    return 0.3183 * speed_mpm / roll_diameter_m


def roll_rotational_speed_english(speed_fpm, roll_diameter_in):
    """Roll RPM (English). = 3.82 × V / Do"""
    if roll_diameter_in == 0:
        return 0.0
    return 3.82 * speed_fpm / roll_diameter_in


def dandy_roll_rpm(wire_speed_fpm, dandy_diameter_ft):
    """Dandy roll RPM ≈ 3.142 × V / (π×D). Target 125-150 rpm."""
    if dandy_diameter_ft == 0:
        return 0.0
    return wire_speed_fpm / (math.pi * dandy_diameter_ft)


def critical_speed_calender_english(ro_in, ri_in, l_in):
    """Critical speed of calender roll (ft/min).
    CS = 4.12×10⁶ × Ro/L² × √(Ro²+Ri²)"""
    if l_in == 0:
        return 0.0
    return 4.12e6 * (ro_in / (l_in ** 2)) * math.sqrt((ro_in ** 2) + (ri_in ** 2))


def critical_speed_calender_metric(ro_m, ri_m, l_m):
    """Critical speed of calender roll (m/min).
    CS = 1.26×10⁶ × Ro/L² × √(Ro²+Ri²)"""
    if l_m == 0:
        return 0.0
    return 1.26e6 * (ro_m / (l_m ** 2)) * math.sqrt((ro_m ** 2) + (ri_m ** 2))


def approx_critical_speed(do_in, deflection_in):
    """Approximate critical speed of a roll (ft/min).
    CS = 49.12 × Do / √d9"""
    if deflection_in == 0:
        return 0.0
    return 49.12 * do_in / math.sqrt(deflection_in)


def natural_frequency_english(static_deflection_in):
    """Natural frequency (cycles/s). F = 3.127 / √d"""
    if static_deflection_in == 0:
        return 0.0
    return 3.127 / math.sqrt(static_deflection_in)


def natural_frequency_metric(static_deflection_m):
    """Natural frequency (cycles/s). F = 0.4986 / √d"""
    if static_deflection_m == 0:
        return 0.0
    return 0.4986 / math.sqrt(static_deflection_m)


def roll_inertia_english(density_lb_in3, length_in, do_in, di_in):
    """Roll inertia WR² (lbf·ft²). = 0.000682×w×L×(Do⁴-Di⁴)"""
    return 0.000682 * density_lb_in3 * length_in * ((do_in ** 4) - (di_in ** 4))


def roll_inertia_metric(density_kg_m3, length_m, do_m, di_m):
    """Roll inertia WR² (kg·m²). = 0.09817×w×L×(Do⁴-Di⁴)"""
    return 0.09817 * density_kg_m3 * length_m * ((do_m ** 4) - (di_m ** 4))


def torque(force, radius):
    """Torque = Force × Radius"""
    return force * radius


def power_hp(torque_lbf_in, speed_rpm):
    """Power (HP). = T×N / 63025"""
    return (torque_lbf_in * speed_rpm) / 63025.0


def power_watts(torque_nm, speed_rpm):
    """Power (W). = 0.1047 × T × N"""
    return 0.1047 * torque_nm * speed_rpm


def tension_power_hp(speed_fpm, tension_lbf_in, width_in):
    """Tension HP. = N×F×w / 33000"""
    return (speed_fpm * tension_lbf_in * width_in) / 33000.0


def tension_power_kw(speed_mpm, tension_kn_m, width_m):
    """Tension power (kW). = N×F×w / 60"""
    return (speed_mpm * tension_kn_m * width_m) / 60.0


def doctor_load_hp(friction_coeff, load_pli):
    """Doctor load (hp/inch/100fpm). = µ×pli / 330"""
    return (friction_coeff * load_pli) / 330.0


def horse_power(torque_in_lbs, speed_fpm):
    """HP = T×N / 63000"""
    return (torque_in_lbs * speed_fpm) / 63000.0


def motor_torque(hp, motor_rpm):
    """Motor torque (lb-ft). = HP×5252 / rpm"""
    if motor_rpm == 0:
        return 0.0
    return (hp * 5252.0) / motor_rpm


def synchronous_speed(frequency_hz, num_poles):
    """Synchronous speed (rpm). = freq×120 / poles"""
    if num_poles == 0:
        return 0.0
    return (frequency_hz * 120.0) / num_poles


def winder_hp(web_tension_lbs, web_speed_fpm, full_roll_dia_in, core_dia_in):
    """Total winder HP. = T×V×Dfull / (33000×Dcore)"""
    if core_dia_in == 0:
        return 0.0
    return (web_tension_lbs * web_speed_fpm * full_roll_dia_in) / (33000.0 * core_dia_in)


def winding_tension_pli(basis_weight_lb_ream):
    """Required winding tension (lbs/inch). = BW / 20"""
    return basis_weight_lb_ream / 20.0


def overall_efficiency_pct(availability_pct, operating_days, operating_hours):
    """Overall Efficiency (%). = (avail/100)×(days/365)×(hours/24)×100"""
    return (availability_pct / 100.0) * (operating_days / 365.0) * (operating_hours / 24.0) * 100.0


def breaking_length_km(tensile_strength_kg_cm2, specific_gravity):
    """Breaking length (km). = tensile / (sp.gravity × 99.98)"""
    denom = specific_gravity * 99.98
    if denom == 0:
        return 0.0
    return tensile_strength_kg_cm2 / denom


def sheet_tension_at_calender(basis_weight_lb_ream):
    """Sheet tension at calender (pli). = (0.013 × BW)^0.3"""
    return (0.013 * basis_weight_lb_ream) ** 0.3


# ── Gas Laws ──────────────────────────────────────────────────

def ideal_gas_law(pressure, volume, n_moles, r_constant, temperature):
    """PV = nRT. Returns whichever is zero from inputs."""
    return n_moles * r_constant * temperature


def boyles_law(p1, v1, p2=None, v2=None):
    """P1×V1 = P2×V2. Provide 3 values, returns the 4th."""
    if p2 is None:
        if v2 == 0:
            return 0.0
        return (p1 * v1) / v2
    if v2 is None:
        if p2 == 0:
            return 0.0
        return (p1 * v1) / p2
    return p1 * v1


def vacuum_corrected_volume(v1_cfm, vac_at_pump_inhg, vac_at_tube_inhg):
    """Actual air volume at felt suction tube (CFM).
    = [(29.92 - vac_pump)/(29.92 - vac_tube)] × V1"""
    denom = 29.92 - vac_at_tube_inhg
    if denom == 0:
        return 0.0
    return ((29.92 - vac_at_pump_inhg) / denom) * v1_cfm


# ── Basis Weight Conversions ─────────────────────────────────

def offset_to_gsm(lb_per_3300ft2):
    """Offset (lb/3300ft²) to g/m²"""
    return lb_per_3300ft2 * 1.48


def bond_to_gsm(lb_per_1300ft2):
    """Bond (lb/1300ft²) to g/m²"""
    return lb_per_1300ft2 * 3.76


def liner_to_gsm(lb_per_1000ft2):
    """Liner (lb/1000ft²) to g/m²"""
    return lb_per_1000ft2 * 4.89


def news_tissue_to_gsm(lb_per_3000ft2):
    """News/Tissue (lb/3000ft²) to g/m²"""
    return lb_per_3000ft2 * 1.63


def market_pulp_to_gsm(lb_per_2880ft2):
    """Market Pulp (lb/2880ft²) to g/m²"""
    return lb_per_2880ft2 * 1.70
