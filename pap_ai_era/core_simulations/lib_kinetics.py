import numpy as np

def arrhenius(A, Ea, T_K):
    '''Rate constant via Arrhenius. T_K in Kelvin. Returns k (same units as A).'''
    return A * np.exp(-Ea / (8.314 * T_K))

def k_eff_lignin(T_K, OH_conc, HS_conc, params, phase='bulk'):
    '''Effective lignin rate constant at given conditions and cooking phase.
    params: dict with A, Ea, a, b per phase. Returns k_eff (1/h).'''
    k = arrhenius(params[phase]['A'], params[phase]['Ea'], T_K)
    # Adding small epsilon to avoid 0 power issues if concentrations drop to 0
    return k * ((OH_conc+1e-6) ** params[phase]['a']) * ((HS_conc+1e-6) ** params[phase]['b'])

def determine_phase(kappa, kappa_bulk_thresh=100, kappa_res_thresh=30):
    '''Return cooking phase string based on current kappa number.'''
    if kappa > kappa_bulk_thresh: return 'initial'
    elif kappa > kappa_res_thresh: return 'bulk'
    else: return 'residual'
