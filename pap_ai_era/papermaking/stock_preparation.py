"""
Stock Preparation Formulas
Source: Formula-PT.pdf (VK Panigrahi) & TAPPI TIP 0502-17
"""
import math


# ── Fluid Mechanics ──────────────────────────────────────────

def calculate_npsh(p_atm_pa, p_vapor_pa, density_kg_m3, h_friction_m, z_height_m):
    """Net Positive Suction Head (m).
    NPSH = (pa - pv)/(ρg) - hfs - Za"""
    g = 9.81
    return ((p_atm_pa - p_vapor_pa) / (density_kg_m3 * g)) - h_friction_m - z_height_m


def reynolds_number(diameter_m, velocity_m_s, kinematic_viscosity_m2_s):
    """Reynolds Number: NRe = D·V / ν
    Laminar < 2100, Transition 2100-4000, Turbulent > 4000"""
    if kinematic_viscosity_m2_s == 0:
        return 0.0
    return (diameter_m * velocity_m_s) / kinematic_viscosity_m2_s


def pipeline_velocity_english(flow_gpm, pipe_area_in2):
    """Pipeline velocity (ft/s). V = Q × 0.321 / A"""
    if pipe_area_in2 == 0:
        return 0.0
    return (flow_gpm * 0.321) / pipe_area_in2


def pipeline_velocity_metric(flow_l_s, pipe_area_m2):
    """Pipeline velocity (m/s). V = Q × 0.001 / A"""
    if pipe_area_m2 == 0:
        return 0.0
    return (flow_l_s * 0.001) / pipe_area_m2


def viscosity_gas_temperature(mu_0, temperature_k, n=0.65):
    """Gas viscosity at temperature T. µ/µ0 = (T/273)^n
    n ≈ 0.65 for air, 0.9 for CO2, 1.1 for SO2/steam"""
    return mu_0 * ((temperature_k / 273.0) ** n)


def hydraulic_pump_power_hp(differential_pressure_psi, flow_gpm):
    """Hydraulic pump power (hp). P = H×Q / 1714"""
    return (differential_pressure_psi * flow_gpm) / 1714.0


def hydraulic_pump_power_kw(differential_pressure_kpa, flow_l_min):
    """Hydraulic pump power (kW). P = H×Q / 60000"""
    return (differential_pressure_kpa * flow_l_min) / 60000.0


# ── Jet Mixers & Entrainment ─────────────────────────────────

def jet_mixer_entrainment(q_o_m3_s, distance_m, nozzle_diameter_m):
    """Entrained volume beyond 4.3·Dj. qe = (X/(4.3·Dj) - 1)·qo"""
    threshold = 4.3 * nozzle_diameter_m
    if distance_m > threshold:
        return ((distance_m / threshold) - 1) * q_o_m3_s
    return 0.0


# ── Save-All & Fiber Loss ────────────────────────────────────

def krofta_save_all_volume(radius_m, height_m):
    """Cylindrical save-all volume (m³). V = π·r²·h"""
    return math.pi * (radius_m ** 2) * height_m


def save_all_fiber_loss_mt_year(fiber_in_effluent_kg_min, operating_days=350):
    """Annual fiber loss (mt/year)."""
    return (fiber_in_effluent_kg_min * 60 * 24 * operating_days) / 1000.0


def save_all_capital_ratio(installation_cost, fiber_loss_cost_per_year):
    """Capital cost / savings ratio. Install save-all if < 2.0"""
    if fiber_loss_cost_per_year == 0:
        return float('inf')
    return installation_cost / fiber_loss_cost_per_year


def felt_pit_consistency(fiber_out_kg_min, water_out_kg_min):
    """Felt pit consistency (%)."""
    total = fiber_out_kg_min + water_out_kg_min
    if total == 0:
        return 0.0
    return (fiber_out_kg_min / total) * 100.0


def fiber_out_of_press(water_out_press_kg_min, consistency_leaving_pct):
    """Fiber leaving press (kg/min)."""
    if consistency_leaving_pct >= 100:
        return 0.0
    return (water_out_press_kg_min * consistency_leaving_pct) / (100.0 - consistency_leaving_pct)


# ── Stock Pumps & Chests ──────────────────────────────────────

def stock_pump_throughput(capacity_l_min, consistency_pct):
    """Pump throughput (kg/min)."""
    return (capacity_l_min * consistency_pct) / 100.0


def stock_pump_kwh(discharge_kg_min, head_m, consistency_pct):
    """Stock pump power (kWh)."""
    return discharge_kg_min * head_m * consistency_pct * 0.0001635


def stock_pump_lifting_kwh(lifting_kg_min, lifting_height_m, consistency_pct):
    """Stock pump lifting power (kWh)."""
    return ((lifting_kg_min * 9.81 * lifting_height_m) / 60000.0) * consistency_pct


def storage_chest_capacity_m3(ad_production_mt_hr, consistency_pct, reserve_hours=2, n_chests=5):
    """Reserve chest capacity (m³ each) for stock prep."""
    if consistency_pct == 0 or n_chests == 0:
        return 0.0
    return ((ad_production_mt_hr * reserve_hours * 100.0) / consistency_pct) / n_chests


def stock_chest_capacity_mt(volume_m3, consistency_pct):
    """Stock chest bone-dry capacity (mt)."""
    return (volume_m3 * consistency_pct) / 100.0


def tank_sizing_tons_english(lb_per_ft3, volume_ft3):
    """Tank capacity (tons). Tons = (lb/ft³ × Volume) / 2000"""
    return (lb_per_ft3 * volume_ft3) / 2000.0


def tank_sizing_metric(consistency_pct, volume_m3):
    """Tank capacity (metric tons). t = Volume × %BD / 100"""
    return (volume_m3 * consistency_pct) / 100.0


def water_requirement_for_dilution(od_pulp_mt_hr, initial_consistency_pct, final_consistency_pct):
    """Water needed (mt/hr) to dilute from consistency 1 to consistency 2."""
    if initial_consistency_pct == 0 or final_consistency_pct == 0:
        return 0.0
    water_at_initial = od_pulp_mt_hr * ((100.0 - initial_consistency_pct) / initial_consistency_pct)
    water_at_final = od_pulp_mt_hr * ((100.0 - final_consistency_pct) / final_consistency_pct)
    return water_at_final - water_at_initial


def water_per_ton_of_pulp(consistency_pct):
    """Water-to-pulp ratio. V = (100 - C%) / C%"""
    if consistency_pct == 0:
        return 0.0
    return (100.0 - consistency_pct) / consistency_pct


def consistency_percent(dry_material_kg, suspension_kg):
    """Consistency K(%) = (T/Q) × 100"""
    if suspension_kg == 0:
        return 0.0
    return (dry_material_kg / suspension_kg) * 100.0


# ── Refining ──────────────────────────────────────────────────

def refining_specific_edge_load(p_total_kw, p_no_load_kw, cutting_length_km_s):
    """SEL (J/m) = (P - Po) / Ls"""
    if cutting_length_km_s == 0:
        return 0.0
    return (p_total_kw - p_no_load_kw) / cutting_length_km_s


def refining_specific_energy(p_net_kw, throughput_t_h):
    """Specific energy (kWh/t) = Pnet / throughput"""
    if throughput_t_h == 0:
        return 0.0
    return p_net_kw / throughput_t_h


def cutting_edge_length(z_rotor, z_stator, bar_length_m, rpm):
    """CEL (m/s) = ZR × ZS × I × (n/60)"""
    return z_rotor * z_stator * bar_length_m * (rpm / 60.0)


def cutting_length_ddr(n_rpm, z_bars, d1_mm, d2_mm, bar_angle_deg=0):
    """Cutting length for DDR (km/sec).
    Ls = (n/60) × Z × (d1-d2) / cos(α)"""
    cos_a = math.cos(math.radians(bar_angle_deg)) if bar_angle_deg != 0 else 1.0
    if cos_a == 0:
        return 0.0
    return (n_rpm / 60.0) * z_bars * ((d1_mm - d2_mm) / 1000.0) / cos_a


def cutting_length_conical(n_rpm, z_rotor, z_a, l2_mm, z_b, l1_mm):
    """Cutting length for conical refiner (km/sec).
    Ls = (n/60) × (Zw/2) × [(Za)l2 + (Zb)l1]"""
    return (n_rpm / 60.0) * (z_rotor / 2.0) * ((z_a * l2_mm + z_b * l1_mm) / 1e6)


def cutting_capacity_ddr(cutting_length_km_s, throughput_t_h):
    """Cutting capacity Zcut (km/ton) = Ls / (Q × 1000)"""
    if throughput_t_h == 0:
        return 0.0
    return cutting_length_km_s / (throughput_t_h * 1000.0)


def three_phase_power(voltage_kv, current_amp, power_factor=0.8):
    """3-phase power (kW) = √3 × V × I × cos(φ)"""
    return math.sqrt(3) * voltage_kv * current_amp * power_factor


# ── Weir Flow ─────────────────────────────────────────────────

def rectangular_weir_flow_english(weir_length_ft, head_ft):
    """Rectangular weir flow (ft³/s). Q = 3.33 × (L - 0.2H) × H^1.5"""
    return 3.33 * (weir_length_ft - 0.2 * head_ft) * (head_ft ** 1.5)


def rectangular_weir_flow_metric(weir_length_m, head_m):
    """Rectangular weir flow (m³/s). Q = 1.837 × (L - 0.2H) × H^1.5"""
    return 1.837 * (weir_length_m - 0.2 * head_m) * (head_m ** 1.5)


def triangular_notch_weir_90(head_ft):
    """90° V-notch weir flow (ft³/s). Q = 2.4381 × H^2.5"""
    return 2.4381 * (head_ft ** 2.5)


def triangular_notch_weir_90_metric(head_m):
    """90° V-notch weir flow (m³/s). Q = 1.3466 × H^2.5"""
    return 1.3466 * (head_m ** 2.5)


def triangular_notch_weir_60(head_ft):
    """60° V-notch weir flow (ft³/s). Q = 1.4076 × H^2.5"""
    return 1.4076 * (head_ft ** 2.5)


def v_notch_flow_rate(cd, theta_deg, head_ft, g=32.174):
    """General V-notch: Q = (8/15)×Cd×√(2g)×tan(θ/2)×H^(5/2)"""
    return (8.0 / 15.0) * cd * math.sqrt(2 * g) * math.tan(math.radians(theta_deg / 2.0)) * (head_ft ** 2.5)


# ── Flow in Pipe/Jet ──────────────────────────────────────────

def flow_rate_low_nappe(diameter_m, discharge_height_m):
    """Low nappe flow (m³/s). Q = 5.47 × D^1.25 × H^1.35"""
    return 5.47 * (diameter_m ** 1.25) * (discharge_height_m ** 1.35)


def flow_rate_jet(diameter_m, discharge_height_m):
    """Jet flow (m³/s). Q = 3.15 × D^1.99 × H^0.53"""
    return 3.15 * (diameter_m ** 1.99) * (discharge_height_m ** 0.53)


def gpm_pressure_relationship(gpm1, psi1, psi2):
    """gpm1/gpm2 = √psi1/√psi2 → gpm2"""
    if psi2 == 0:
        return 0.0
    return gpm1 * math.sqrt(psi2) / math.sqrt(psi1)


def flow_tons_consistency(consistency_pct, flow_gpm, k_factor=16.76):
    """Tons/day = C × Q / K. K varies with temperature."""
    if k_factor == 0:
        return 0.0
    return (consistency_pct * flow_gpm) / k_factor
