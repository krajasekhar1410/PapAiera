import numpy as np

def D_stage(kappa_in, B_in, visc_in, ClO2_charge, pH, T_C, tau_min, params):
    '''Chlorine Dioxide Bleaching Stage'''
    # Kappa reduction
    kappa_out = kappa_in * np.exp(-params['k_D'] * (ClO2_charge**params['n_D']) / kappa_in)
    
    # Brightness development
    B_max = params['B_max_D']
    k_B = params['k_B_D']
    B_out = B_max - (B_max - B_in) * np.exp(-k_B * ClO2_charge * (tau_min/60.0))
    
    # Viscosity drop
    visc_out = visc_in - params['k_v_D'] * ClO2_charge * (tau_min / 60.0)
    
    # Rough estimate of chemical consumption
    ClO2_consumed = kappa_in * 0.19 - kappa_out * 0.05  
    
    return {
        'kappa': kappa_out, 
        'brightness': B_out,
        'viscosity': visc_out, 
        'ClO2_consumed': ClO2_consumed
    }

def Eop_stage(kappa_in, B_in, NaOH, O2_pressure, H2O2, T_C, tau_min, params):
    '''Oxidative Extraction Stage with Peroxide'''
    X = (params['a_E'] + params['b_E']*NaOH + params['c_E']*O2_pressure + params['d_E']*H2O2) / 100.0
    X = min(X, 0.65)  # cap at 65% extraction efficiency
    kappa_out = kappa_in * (1 - X)
    
    NaOH_cons = NaOH * 0.7  # ~70% NaOH consumed experimentally
    H2O2_cons = H2O2 * 0.8  # ~80% H2O2 consumed experimentally
    
    return {
        'kappa': kappa_out, 
        'brightness': B_in + 15.0, # Approximate baseline jump from extraction
        'NaOH_consumed': NaOH_cons, 
        'H2O2_consumed': H2O2_cons
    }

def P_stage(B_in, visc_in, H2O2, NaOH, Mn_conc, T_C, tau_min, params):
    '''Hydrogen Peroxide Stage'''
    # Decomposition from Manganese
    H2O2_decomp = params['k_d'] * Mn_conc * H2O2 * (tau_min / 60.0)
    H2O2_eff = max(0, H2O2 - H2O2_decomp)
    
    # Brightness leap
    B_max = params['B_max_P']
    k_P = params['k_P']
    B_out = B_max - (B_max - B_in) * np.exp(-k_P * H2O2_eff * (tau_min/60.0))
    
    visc_out = visc_in - params['k_v_P'] * NaOH * (tau_min / 60.0)
    H2O2_cons = (B_out - B_in) / params['k_B_H2O2'] + H2O2_decomp
    
    return {
        'brightness': B_out, 
        'viscosity': visc_out, 
        'H2O2_consumed': H2O2_cons
    }
