import math
import numpy as np
from typing import List, Tuple, Dict
from .furnish import FurnishRecord

class HFactorEngine:
    """Dynamic H-factor computation based on furnish reactivity and target kappa."""
    
    @staticmethod
    def calculate_raw_h(temperature_profile: List[Tuple[float, float]]) -> float:
        """
        Calculates classical H-factor from a temperature profile.
        temperature_profile: List of (time_min, temp_C)
        H = ∫ exp[ 43.2 – (16113 / T(K)) ] dt (t in hours)
        """
        h_total = 0.0
        for i in range(len(temperature_profile) - 1):
            t1, temp1 = temperature_profile[i]
            t2, temp2 = temperature_profile[i+1]
            
            dt_hours = (t2 - t1) / 60.0
            avg_temp_C = (temp1 + temp2) / 2.0
            temp_K = avg_temp_C + 273.15
            
            # Reaction rate relative to 100°C
            # rate = exp(43.185 - 16113 / T)
            if temp_K > 373.15: # Only integrate above 100°C
                rate = math.exp(43.185 - (16113.0 / temp_K))
                h_total += rate * dt_hours
                
        return h_total

    def get_effective_h(self, raw_h: float, furnish: FurnishRecord) -> float:
        """H_eff = H_classical × Rf"""
        return raw_h * furnish.reactivity_factor_Rf

    def calculate_target_h(self, kappa_target: float, furnish: FurnishRecord) -> float:
        """H_target = A × exp(–B × κ_target) + C"""
        coeffs = furnish.h_model_coeffs
        return coeffs["A"] * math.exp(-coeffs["B"] * kappa_target) + coeffs["C"]

    def predict_kappa(self, h_eff: float, ea_charge: float, furnish: FurnishRecord) -> float:
        """
        Reverse of H_target formula for quick estimate.
        In reality, uses KappaModel.
        """
        coeffs = furnish.h_model_coeffs
        # H = A * exp(-B * K) + C  => (H-C)/A = exp(-B*K) => ln((H-C)/A) = -B*K => K = -ln((H-C)/A) / B
        val = (h_eff - coeffs["C"]) / coeffs["A"]
        if val <= 0:
            return furnish.kappa_target_range[1] # Max kappa if H is too low
        return -math.log(val) / coeffs["B"]
