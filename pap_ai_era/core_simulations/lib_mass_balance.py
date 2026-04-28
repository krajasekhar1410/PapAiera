import numpy as np

def digester_mass_balance(m_chips_BD, Y, EA_conc, LWR, sulphidity):
    '''Overall digester mass balance. Returns dict with BL flows, WL charge, soda balance.'''
    V_WL = m_chips_BD * LWR  # litres
    m_WL = V_WL / 1000  # tonnes (approx density = 1 kg/L for dilute liquor)
    m_pulp_BD = m_chips_BD * Y / 100
    m_dissolved = m_chips_BD - m_pulp_BD
    EA_total = EA_conc * V_WL / 1000  # kg as NaOH
    EA_pct = EA_total / m_chips_BD * 100
    return {
        'm_pulp_BD': m_pulp_BD, 
        'm_dissolved': m_dissolved,
        'EA_total_kg': EA_total, 
        'EA_pct': EA_pct, 
        'V_WL_L': V_WL
    }

def washing_balance(m_pulp, DS_in, DS_out_target, wash_water_vol, stages=3):
    '''Counter-current washing balance. Returns soda loss and filtrate composition.'''
    # Simplified Multi-stage countercurrent model
    E_wash = 1 - (DS_out_target / DS_in) if DS_in > 0 else 0
    soda_loss = (1 - E_wash) * DS_in * m_pulp * 0.2  # Approx 20% of DS is sodium
    return {
        'washing_efficiency': E_wash, 
        'soda_loss_kg': soda_loss
    }
