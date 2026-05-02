import math
from .furnish import FurnishRecord

class PreTreatment:
    """Pre-heating & Impregnation module."""
    
    def calculate_iqi(self, duration_min: float, temp_C: float, pressure_kPa: float, furnish: FurnishRecord) -> float:
        """
        Impregnation Quality Index (IQI) = 100 × [1 – exp(–τ / τ_ref)] × P_factor × T_factor
        """
        tau_ref = furnish.impreg_duration_min
        p_ref = 500.0 # Design pressure kPa
        t_ref = furnish.impreg_temp_C
        
        # Time factor
        f_tau = 1.0 - math.exp(-duration_min / tau_ref)
        
        # Pressure factor
        f_p = pressure_kPa / p_ref
        
        # Temperature factor (Arrhenius style or linear)
        f_t = temp_C / t_ref
        
        iqi = 100.0 * f_tau * f_p * f_t
        return min(100.0, max(0.0, iqi))

    def get_recommendations(self, furnish: FurnishRecord):
        """Returns target pre-treatment parameters."""
        return {
            "preheat_max_temp": furnish.preheat_temp_max_C,
            "impreg_temp": furnish.impreg_temp_C,
            "impreg_duration_min": furnish.impreg_duration_min
        }
