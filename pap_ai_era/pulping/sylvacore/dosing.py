from .furnish import FurnishRecord

class ChemDosing:
    """Cooking chemical module for EA, Sulfidity, and L/W optimization."""
    
    def calculate_optimal_dosing(self, furnish: FurnishRecord, kappa_target: float, moisture_pct: float):
        """
        Computes the optimal white liquor charge and composition.
        """
        # Step 1 - Base EA
        ea_base = furnish.ea_baseline_pct
        
        # Step 2 - Kappa correction
        # EA_adj = EA_base + α × (κ_standard – κ_target)
        alpha = 0.12 # EA sensitivity per kappa unit
        k_standard = (furnish.kappa_target_range[0] + furnish.kappa_target_range[1]) / 2.0
        ea_adj = ea_base + alpha * (k_standard - kappa_target)
        
        # Step 3 - Moisture correction
        # EA_actual = EA_adj × (1 – MC/100)⁻¹
        ea_actual = ea_adj / (1.0 - moisture_pct / 100.0)
        
        # Sulfidity recommendation
        s_range = furnish.sulfidity_optimum_range
        
        return {
            "ea_adj_pct_od": ea_adj,
            "ea_actual_pct_wet": ea_actual,
            "sulfidity_range": s_range,
            "lw_ratio_target": furnish.lw_ratio_typical
        }
