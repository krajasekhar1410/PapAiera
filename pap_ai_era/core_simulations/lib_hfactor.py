import numpy as np

def hfactor_rate(T_K):
    '''H-factor accumulation rate at temperature T_K. Returns dH/dt (dimensionless/h).'''
    return np.exp(43.2 - 16115 / T_K)

def integrate_hfactor(t_vec, T_vec_C):
    '''Integrate H-factor over temperature profile using trapezoidal rule.
    t_vec: time in minutes (array), T_vec_C: temperature in Celsius (array).
    Returns: H (scalar), H_vec (cumulative array).'''
    T_K = np.array(T_vec_C) + 273.15
    f = np.exp(43.2 - 16115 / T_K)
    dt_h = np.diff(np.array(t_vec)) / 60.0  # convert minutes to hours
    # Calculate cumulative trapezoidal integration
    H_vec = np.concatenate([[0], np.cumsum(0.5 * (f[:-1] + f[1:]) * dt_h)])
    return H_vec[-1], H_vec

def isothermal_cook_time(H_target, T_cook_C):
    '''Compute required isothermal cook time (minutes) for target H-factor.'''
    T_K = T_cook_C + 273.15
    t_hours = H_target / np.exp(43.2 - 16115 / T_K)
    return t_hours * 60.0
