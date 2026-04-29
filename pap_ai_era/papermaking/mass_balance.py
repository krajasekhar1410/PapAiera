"""
Mass Balance Equations for Retention and Basis Weight
Source: MassBalanceEquationsforRetentionandBasisWeightinaPaperMachine.pdf
(Juneja et al., IEEE 2019)
"""


def headbox_consistency_mass_balance(thick_stock_cons, thick_stock_flow,
                                      thin_stock_flow, dil_water_cons):
    """Headbox thin stock consistency from thick stock mixing.
    CHB = (Qs×Cs + Qd×Cd) / Qo"""
    if thin_stock_flow == 0:
        return 0.0
    q_dil = thin_stock_flow - thick_stock_flow
    return ((thick_stock_flow * thick_stock_cons) + (q_dil * dil_water_cons)) / thin_stock_flow


def retention_from_consistencies(headbox_cons, white_water_cons):
    """First-pass retention ratio R = (CHB - Cww) / CHB"""
    if headbox_cons == 0:
        return 0.0
    return (headbox_cons - white_water_cons) / headbox_cons


def basis_weight_from_mass_balance(thick_stock_flow, thick_stock_cons,
                                    slice_width, wire_speed, retention):
    """Basis weight G (g/m²) from volume balance.
    G = (Qs × Cs × R) / (W × Vw)"""
    if slice_width == 0 or wire_speed == 0:
        return 0.0
    return (thick_stock_flow * thick_stock_cons * retention) / (slice_width * wire_speed)


def thick_stock_flow_for_grammage(grammage_gsm, wire_speed, slice_width,
                                   retention, thick_stock_cons):
    """Required thick stock volume flow rate (m³/s) for target grammage.
    Qs = G × W × Vw / (Cs × R)"""
    if thick_stock_cons == 0 or retention == 0:
        return 0.0
    return (grammage_gsm * slice_width * wire_speed) / (thick_stock_cons * retention)


def total_solids_entering(thick_stock_flow, thick_stock_cons, dil_water_flow, dil_water_cons):
    """Total solids entering forming section.
    MTin = Qs×Cs + Qd×Cd"""
    return (thick_stock_flow * thick_stock_cons) + (dil_water_flow * dil_water_cons)


def retained_solids(total_solids_in, retention):
    """Retained solids on wire. MTr = MTin × R"""
    return total_solids_in * retention


def white_water_drained_solids(total_solids_in, retention):
    """White water drained solids. MTww = MTin × (1 - R)"""
    return total_solids_in * (1.0 - retention)


def ash_retention(headbox_ash, white_water_ash):
    """Ash retention. γa = (AH - Aww) / AH"""
    if headbox_ash == 0:
        return 0.0
    return (headbox_ash - white_water_ash) / headbox_ash


def fines_retention(headbox_fines, white_water_fines):
    """Fines retention. γf = (fHB - fww) / fHB"""
    if headbox_fines == 0:
        return 0.0
    return (headbox_fines - white_water_fines) / headbox_fines


def dissolved_solids_retention(headbox_ds, white_water_ds):
    """Dissolved solids retention. γds = (DSHB - DSww) / DSHB"""
    if headbox_ds == 0:
        return 0.0
    return (headbox_ds - white_water_ds) / headbox_ds


def couch_solids(retained_solids_flow, losses_flow):
    """Couch solids = retained - losses"""
    return retained_solids_flow - losses_flow


def recirculation_volume(thin_stock_flow, recirculation_constant):
    """Recirculated volume in short loop."""
    return thin_stock_flow * recirculation_constant


def overall_fiber_balance(fiber_from_stuff_box, fiber_in_effluent,
                           fiber_in_baled_pulp, fiber_out_felt_pit):
    """Overall fiber balance check. Returns residual (should be ≈ 0).
    fiber_out_felt + fiber_baled = fiber_stuff_box + fiber_effluent"""
    lhs = fiber_out_felt_pit + fiber_in_baled_pulp
    rhs = fiber_from_stuff_box + fiber_in_effluent
    return lhs - rhs


def wire_pit_consistency(fiber_to_tray_kg_min, water_to_wire_pit_kg_min):
    """Wire pit consistency (%)."""
    total = fiber_to_tray_kg_min + water_to_wire_pit_kg_min
    if total == 0:
        return 0.0
    return (fiber_to_tray_kg_min / total) * 100.0
