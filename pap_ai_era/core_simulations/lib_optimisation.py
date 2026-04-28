from scipy.optimize import minimize
from .lib_bleach_stages import D_stage, Eop_stage, P_stage

def bleach_objective_function(chemical_doses, kappa_0, B_target, visc_min, params_dict):
    '''
    Minimise total chemical cost subject to brightness and viscosity constraints across an ECF Sequence (D0-Eop-D1-P).
    chemical_doses: array [ClO2_D0, NaOH_Eop, H2O2_Eop, ClO2_D1, H2O2_P]
    '''
    c1_clo2_d0, c2_naoh_eop, c3_h2o2_eop, c4_clo2_d1, c5_h2o2_p = chemical_doses
    
    cost = (c1_clo2_d0 * params_dict['price_ClO2'] + 
            c2_naoh_eop * params_dict['price_NaOH'] + 
            c3_h2o2_eop * params_dict['price_H2O2'] + 
            c4_clo2_d1 * params_dict['price_ClO2'] + 
            c5_h2o2_p * params_dict['price_H2O2'])

    def constraint_brightness(x):
        c1, c2, c3, c4, c5 = x
        s1 = D_stage(kappa_0, 30, 1000, c1, 4.0, 70, 60, params_dict['D'])
        s2 = Eop_stage(s1['kappa'], s1['brightness'], c2, 3.0, c3, 85, 60, params_dict['Eop'])
        s3 = D_stage(s2['kappa'], s2['brightness'], s1['viscosity'], c4, 4.0, 75, 120, params_dict['D'])
        s4 = P_stage(s3['brightness'], s3['viscosity'], c5, 2.0, 0.1, 80, 120, params_dict['P'])
        return s4['brightness'] - B_target

    def constraint_viscosity(x):
        c1, c2, c3, c4, c5 = x
        s1 = D_stage(kappa_0, 30, 1000, c1, 4.0, 70, 60, params_dict['D'])
        s2 = Eop_stage(s1['kappa'], s1['brightness'], c2, 3.0, c3, 85, 60, params_dict['Eop'])
        s3 = D_stage(s2['kappa'], s2['brightness'], s1['viscosity'], c4, 4.0, 75, 120, params_dict['D'])
        s4 = P_stage(s3['brightness'], s3['viscosity'], c5, 2.0, 0.1, 80, 120, params_dict['P'])
        return s4['viscosity'] - visc_min

    con1 = {'type': 'ineq', 'fun': constraint_brightness}
    con2 = {'type': 'ineq', 'fun': constraint_viscosity}
    bnds = ((5,25), (5,20), (1,10), (5,20), (1,10))
    x0 = [10.0, 10.0, 3.0, 10.0, 3.0]
    
    def internal_cost(x):
        return (x[0]*params_dict['price_ClO2'] + x[1]*params_dict['price_NaOH'] + x[2]*params_dict['price_H2O2'] + x[3]*params_dict['price_ClO2'] + x[4]*params_dict['price_H2O2'])

    res = minimize(internal_cost, x0, bounds=bnds, constraints=[con1, con2], method='SLSQP')
    
    return {
        'success': res.success,
        'cost_minimized': res.fun,
        'optimal_doses_kg_t': res.x
    }
