import math
from .furnish import FurnishRecord

class KappaModel:
    """Kappa number prediction and residual lignin tracking per cooking stage."""
    
    def predict_kappa(self, h_eff: float, ea_charge: float, furnish: FurnishRecord, sulfidity: float = 25.0, lw_ratio: float = 3.5) -> float:
        """
        κ_pred = κ₀ × exp(–k₁ × H_eff) × (EA / EA_ref)^(–k₂) × f(S, L/W)
        """
        k0 = furnish.lignin_content * 1.5 # Empirical conversion of lignin% to initial kappa equivalent
        ea_ref = furnish.ea_baseline_pct
        
        # Base prediction
        k1 = furnish.k_rate_k1
        k2 = furnish.k_alkali_k2
        
        kappa_base = k0 * math.exp(-k1 * h_eff) * ((ea_charge / ea_ref) ** -k2)
        
        # Correction for sulfidity and L/W (Simplified)
        s_opt = (furnish.sulfidity_optimum_range[0] + furnish.sulfidity_optimum_range[1]) / 2.0
        f_s = 1.0 - (sulfidity - s_opt) * 0.005 # Small correction
        
        lw_opt = furnish.lw_ratio_typical
        f_lw = 1.0 + (lw_ratio - lw_opt) * 0.02 # L/W effect on penetration
        
        return max(5.0, kappa_base * f_s * f_lw)

    def get_stage_kappa_profile(self, stages_h_accum: list, ea_charge: float, furnish: FurnishRecord):
        """Returns κ_predicted for each stage boundary."""
        profile = []
        for h in stages_h_accum:
            k = self.predict_kappa(h, ea_charge, furnish)
            profile.append(k)
        return profile
