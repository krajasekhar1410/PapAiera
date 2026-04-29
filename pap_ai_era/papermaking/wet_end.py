"""
Wet End & Headbox Formulas
Source: Formula-PT.pdf (VK Panigrahi) & TAPPI TIP 0502-17
"""
import math


# ── Headbox ───────────────────────────────────────────────────

def theoretical_head_english(spouting_velocity_fpm, k_constant=23.165):
    """Theoretical head. Head = (V/100)² / K
    K: 1.9304 (in H2O), 23.165 (ft H2O), 26.196 (in Hg), 53.336 (psig)"""
    return ((spouting_velocity_fpm / 100.0) ** 2) / k_constant


def theoretical_head_metric(spouting_velocity_mpm):
    """Theoretical head (m H2O). Head = V² / 70610"""
    return (spouting_velocity_mpm ** 2) / 70610.0


def spouting_velocity_english(head, k_constant=481.5):
    """Spouting velocity (ft/min). V = K × √h
    K: 139.2 (in H2O), 481.5 (ft H2O), 513.3 (in Hg), 732.3 (psig)"""
    return k_constant * math.sqrt(head)


def spouting_velocity_metric(head_m_h2o):
    """Spouting velocity (m/min). V = 265.7 × √h"""
    return 265.7 * math.sqrt(head_m_h2o)


def headbox_flow_rate_slice_english(slice_opening_in, spouting_vel_fpm, cc=0.95):
    """Headbox flow rate (gal/min/in). = S.O. × V × 0.052 × Cc
    Cc: 0.95 nozzle, 0.75 low angle, 0.70 high angle, 0.60 straight"""
    return slice_opening_in * spouting_vel_fpm * 0.052 * cc


def headbox_flow_rate_slice_metric(slice_opening_mm, spouting_vel_mpm, cc=0.95):
    """Headbox flow rate (L/min/m). = S.O. × V × Cc"""
    return slice_opening_mm * spouting_vel_mpm * cc


def headbox_flow_rate_consistency(bd_ton_per_day, tray_consistency_pct,
                                  net_consistency_pct, trim_inches):
    """Standard headbox flow rate (gpm/inch).
    = (BD ton/24hr/inch) × 16.76 × (1.5 - tray_cy) / (1.5 - net_cy)"""
    if trim_inches == 0 or (1.5 - net_consistency_pct) == 0:
        return 0.0
    bd_per_hr_per_inch = bd_ton_per_day / 24.0 / trim_inches
    return bd_per_hr_per_inch * 16.76 * (1.5 - tray_consistency_pct) / (1.5 - net_consistency_pct)


def tissue_headbox_flow_rate_english(throat_opening_in, spouting_vel_fpm):
    """Tissue headbox flow rate (gpm/inch). = T.O. × V × 0.052"""
    return throat_opening_in * spouting_vel_fpm * 0.052


def tissue_headbox_flow_rate_metric(throat_opening_mm, spouting_vel_mpm):
    """Tissue headbox flow rate (L/min/m). = T.O. × V"""
    return throat_opening_mm * spouting_vel_mpm


def headbox_volumetric_flow_rate(production_tpd, headbox_cy_pct, tray_cy_pct):
    """Head box volumetric flow rate (l/min).
    = (70 × P) / (B - A)"""
    denom = headbox_cy_pct - tray_cy_pct
    if denom == 0:
        return 0.0
    return (70.0 * production_tpd) / denom


def headbox_mass_flow_rate(dry_fiber_rate_kg_min, consistency_pct):
    """Head box mass flow rate (kg/min). = fiber_rate / cy%"""
    if consistency_pct == 0:
        return 0.0
    return dry_fiber_rate_kg_min / (consistency_pct / 100.0)


def headbox_free_jet_length(velocity_fpm, angle_deg, apron_height_in):
    """Headbox free jet length (in). Projectile equation.
    x = (cosA/g)×(V·sinA + √((V·sinA)² + 2g·h))
    Uses constant 9652.5 for English units."""
    a_rad = math.radians(angle_deg)
    v_sin = velocity_fpm * math.sin(a_rad)
    v_cos = velocity_fpm * math.cos(a_rad)
    discriminant = (v_sin ** 2) + (19304.0 * apron_height_in)
    if discriminant < 0:
        return 0.0
    return (v_cos / 9652.5) * (v_sin + math.sqrt(discriminant))


def headbox_consistency_from_slice(gsm, retention_pct, slice_opening_m):
    """Head box consistency (%). = gsm / (100 × R × slice_opening_m)"""
    if retention_pct == 0 or slice_opening_m == 0:
        return 0.0
    return gsm / (100.0 * (retention_pct / 100.0) * slice_opening_m)


def head_of_stock_behind_slice(wire_speed_mpm):
    """Head of stock behind slice (mmWC). = (V/265.7)² × 1000"""
    return ((wire_speed_mpm / 265.7) ** 2) * 1000.0


def total_solids_flow_from_headbox(solids_in_paper_kg_hr, fpr_pct):
    """Total solids flow from headbox (kg/hr). = solids_in_paper / (FPR/100)"""
    if fpr_pct == 0:
        return 0.0
    return (solids_in_paper_kg_hr / fpr_pct) * 100.0


def headbox_discharge_to_wire(total_solids_from_hbox_kg_hr, headbox_cy_pct):
    """Head box discharge to wire (ltr/min)."""
    if headbox_cy_pct == 0:
        return 0.0
    return (total_solids_from_hbox_kg_hr / headbox_cy_pct) * 100.0 * (1.0 / 60.0)


def headbox_energy_balance(head_m, cq=0.88):
    """Jet velocity from energy balance. v = Cq × √(2gh)
    Cq = 0.85-0.90 tapered, 0.65-0.75 abrupt"""
    return cq * math.sqrt(2.0 * 9.81 * head_m)


def lb_ratio(bottom_lip_mm, slice_opening_mm):
    """L/b ratio of slice geometry.
    < 0.5 = pressure forming, >= 1.0 = velocity forming"""
    if slice_opening_mm == 0:
        return 0.0
    return bottom_lip_mm / slice_opening_mm


# ── Basis Weight & Slice ─────────────────────────────────────

def basis_weight_from_slice(slice_opening_mm, headbox_cy_pct):
    """GSM = slice_opening(mm) × h/box_cy(%) × 10"""
    return slice_opening_mm * headbox_cy_pct * 10.0


def slice_opening_from_gsm(gsm, headbox_cy_pct):
    """Slice opening (mm) = gsm / (10 × h/box_cy%)"""
    if headbox_cy_pct == 0:
        return 0.0
    return gsm / (10.0 * headbox_cy_pct)


# ── Retention ─────────────────────────────────────────────────

def first_pass_retention(headbox_cy_pct, tray_cy_pct):
    """First pass retention (%).
    R = (CHB - Cww) / CHB × 100"""
    if headbox_cy_pct == 0:
        return 0.0
    return ((headbox_cy_pct - tray_cy_pct) / headbox_cy_pct) * 100.0


def stock_thickness_on_wire_metric(basis_weight_gsm, consistency_frac,
                                    retention_frac, jw_ratio=1.0):
    """Stock thickness on forming fabric (cm).
    T = BW / (C × R × 10000 × J/W)"""
    denom = consistency_frac * retention_frac * 10000.0 * jw_ratio
    if denom == 0:
        return 0.0
    return basis_weight_gsm / denom


# ── Wire / Forming Section ────────────────────────────────────

def slurry_from_slice(wire_speed_mpm, slice_width_m, slice_opening_m):
    """Slurry from slice (kg/min)."""
    return wire_speed_mpm * slice_width_m * slice_opening_m * 1000.0


def water_to_wire(wire_speed_mpm, wire_width_m, slice_opening_m, gsm, retention_pct):
    """Water to wire (kg/min)."""
    return (wire_speed_mpm * wire_width_m) * (
        (slice_opening_m * 1000.0) - (gsm / (10.0 * retention_pct))
    )


def fiber_leaving_wire_in_sheet(wire_speed_mpm, wire_width_m, gsm):
    """Fiber leaving wire in paper sheet (kg/min)."""
    return (wire_speed_mpm * wire_width_m * gsm) / 1000.0


def water_leaving_wire_in_sheet(wire_speed_mpm, wire_width_m, gsm, sheet_cy_pct):
    """Water leaving wire in paper sheet (kg/min)."""
    fiber = fiber_leaving_wire_in_sheet(wire_speed_mpm, wire_width_m, gsm)
    if sheet_cy_pct == 0:
        return 0.0
    return fiber * ((100.0 - sheet_cy_pct) / sheet_cy_pct)


def fiber_delivered_to_wire(wire_speed_mpm, wire_width_m, gsm, retention_pct):
    """Fiber delivered to wire (kg/min)."""
    if retention_pct == 0:
        return 0.0
    return ((wire_speed_mpm * wire_width_m * gsm) / (retention_pct * 10.0)) * 100.0


def fiber_to_tray(wire_speed_mpm, wire_width_m, gsm, retention_pct):
    """Fiber going to tray (kg/min)."""
    delivered = fiber_delivered_to_wire(wire_speed_mpm, wire_width_m, gsm, retention_pct)
    retained = fiber_leaving_wire_in_sheet(wire_speed_mpm, wire_width_m, gsm)
    return delivered - retained


# ── Formation ─────────────────────────────────────────────────

def blade_pulse_frequency_english(wire_speed_fpm, blade_spacing_in):
    """Blade pulse frequency (cycles/sec). f = V / (5 × λ)"""
    if blade_spacing_in == 0:
        return 0.0
    return wire_speed_fpm / (5.0 * blade_spacing_in)


def blade_pulse_frequency_metric(wire_speed_mpm, blade_spacing_m):
    """Blade pulse frequency (cycles/sec). f = V / (60 × λ)"""
    if blade_spacing_m == 0:
        return 0.0
    return wire_speed_mpm / (60.0 * blade_spacing_m)


def fourdrinier_shake_number_english(frequency, amplitude_in, wire_speed_fpm):
    """Shake number (English). S = f² × a / V. Target > 30, ideal 50-60."""
    if wire_speed_fpm == 0:
        return 0.0
    return (frequency ** 2 * amplitude_in) / wire_speed_fpm


def fourdrinier_shake_number_metric(frequency, amplitude_mm, wire_speed_mpm):
    """Shake number (metric). S = f² × a / V. Target > 2500, ideal 4200-5000."""
    if wire_speed_mpm == 0:
        return 0.0
    return (frequency ** 2 * amplitude_mm) / wire_speed_mpm


def fourdrinier_forming_length_speed(forming_length_ft, dwell_factor=40):
    """Machine speed potential (fpm) from forming length.
    dwell_factor: 40 (1.5s), 30 (2.0s), 60 (1.0s), 48 (1.25s)"""
    return forming_length_ft * dwell_factor


# ── Forming Fabric ────────────────────────────────────────────

def drainage_index(b_constant, c_md_count, air_perm_cfm):
    """Drainage Index (DI). = b × c × v × 10⁻³ × 2.54"""
    return b_constant * c_md_count * air_perm_cfm * 0.001 * 2.54


def fiber_support_index(a_constant, b_constant, m_cd_mesh, c_md_count):
    """Fiber Support Index (FSI). = ⅔(aM + 2bc)"""
    return (2.0 / 3.0) * ((a_constant * m_cd_mesh) + (2.0 * b_constant * c_md_count))


def fabric_wear_pct(initial_thickness, worn_thickness):
    """Fabric wear (%). = [(C-A) / (0.58×C)] × 100"""
    if initial_thickness == 0:
        return 0.0
    return ((initial_thickness - worn_thickness) / (0.58 * initial_thickness)) * 100.0


def fabric_revolutions(machine_speed_mpm, fabric_length_m, days):
    """Total fabric revolutions over a run."""
    if fabric_length_m == 0:
        return 0.0
    return (machine_speed_mpm / fabric_length_m) * 1440.0 * days


def wire_length_m(dist_breast_to_couch_mm, breast_roll_dia_mm, couch_roll_dia_mm):
    """Wire length (m).
    = [(2×dist) + (π/2)×(breast_dia + couch_dia) + 130] / 1000"""
    return ((2 * dist_breast_to_couch_mm) +
            (math.pi / 2.0) * (breast_roll_dia_mm + couch_roll_dia_mm) +
            130.0) / 1000.0


def drag_load_fabric(volts, total_amps, wire_speed_mpm, fabric_width_mm):
    """Drag load in fabric (kg/cm)."""
    if wire_speed_mpm == 0 or fabric_width_mm == 0:
        return 0.0
    return (volts * total_amps * 49.0) / (wire_speed_mpm * fabric_width_mm)


def drag_load_conventional_english(drive_volts, drive_amps, speed_fpm, width_in):
    """Conventional drag load (lbf/in). = Σ(V×A) × 0.226 / (v × S × 0.8)"""
    if speed_fpm == 0 or width_in == 0:
        return 0.0
    return (drive_volts * drive_amps * 0.226) / (speed_fpm * width_in * 0.8)


def drag_load_conventional_metric(drive_volts, drive_amps, speed_mpm, width_m):
    """Conventional drag load (kN/m). = Σ(V×A) × 0.06 / (v × S × 0.8)"""
    if speed_mpm == 0 or width_m == 0:
        return 0.0
    return (drive_volts * drive_amps * 0.06) / (speed_mpm * width_m * 0.8)


def component_drag_load(vn_speed, vs_slack_speed, elastic_modulus, slack_tension):
    """Component drag load (wet end). DL = (Vn/Vs - 1)(EM - Ts)"""
    if vs_slack_speed == 0:
        return 0.0
    return ((vn_speed / vs_slack_speed) - 1.0) * (elastic_modulus - slack_tension)


def fabric_life_days(fabric_tension_pli):
    """Estimated fabric life (days). = 1.23×10⁶ × tension^(-2.55)"""
    if fabric_tension_pli == 0:
        return 0.0
    return 1.23e6 * (fabric_tension_pli ** (-2.55))


def shower_oscillation_speed(machine_speed_mpm, jet_mm, fabric_length_m):
    """Shower traversing speed (mm/min)."""
    if fabric_length_m == 0:
        return 0.0
    return (machine_speed_mpm * jet_mm) / fabric_length_m
