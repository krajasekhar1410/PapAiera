import numpy as np
from scipy.integrate import odeint
from .lib_kinetics import k_eff_lignin, determine_phase
from .lib_hfactor import integrate_hfactor

def lignin_ode(state, t, inputs, params, t_vec, H_vec, T_vec):
    '''ODE system representing Lignin dissolution, Carbohydrate peeling, and EA consumption.'''
    L, C, EA = state
    # Ensure no negative states
    L = max(L, 1e-6)
    C = max(C, 1e-6)
    EA = max(EA, 1e-6)
    
    # Interpolate Temperature from vector
    T_C = np.interp(t, t_vec, T_vec)
    T_K = T_C + 273.15
    kappa_curr = params['kappa_factor'] * L
    
    phase = determine_phase(kappa_curr, params['kappa_bulk_thresh'], params['kappa_res_thresh'])
    
    # Approximation of OH and HS from EA (simplified assumption that HS drops marginally)
    OH_conc = EA / 40.0  # Moles/L (approximation)
    HS_conc = (inputs['sulphidity']/100.0) * OH_conc # Rough approximation for kinetics calc
    
    # Rates
    k_l = k_eff_lignin(T_K, OH_conc, HS_conc, params, phase)
    dL_dt = -k_l * L
    
    # Carbohydrate peeling
    k_c = params.get('k_C', 0.001)  # Simplified carbohydrate peeling const
    Ea_C = params.get('Ea_C', 100000)
    import math
    k_c_T = k_c * math.exp(-Ea_C / (8.314 * T_K))
    dC_dt = -k_c_T * C
    
    # EA consumption
    dEA_dt = -(params['alpha_L'] * abs(dL_dt)) - (params['alpha_C'] * abs(dC_dt))
    
    return [dL_dt, dC_dt, dEA_dt]

def cook_module(inputs, params):
    '''Full digester cooking simulation.
    inputs: dict(L0, C0, EA_conc, LWR, T_profile, sulphidity)
    params: dict(..., kappa_factor, kappa_bulk_thresh, kappa_res_thresh, alpha_L, alpha_C)
    '''
    t_vec, T_vec = inputs['T_profile']
    H_f, H_vec = integrate_hfactor(t_vec, T_vec)
    
    # Integrate ODE
    state_0 = [inputs['L0'], inputs['C0'], inputs['EA_conc']]
    # Time vector is in hours for ODE
    t_h = np.array(t_vec) / 60.0
    
    sol = odeint(lignin_ode, state_0, t_h, args=(inputs, params, t_h, H_vec, T_vec))
    
    L_f, C_f, EA_res = sol[-1]
    kappa_f = params['kappa_factor'] * L_f
    Y = (L_f + C_f) / (inputs['L0'] + inputs['C0']) * 100
    
    return {
        'kappa_f': kappa_f, 
        'Y': Y, 
        'H_f': H_f,
        'EA_res': EA_res, 
        'L_f': L_f, 
        'C_f': C_f
    }
