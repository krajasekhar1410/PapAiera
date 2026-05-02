from typing import List, Dict
from .furnish import FurnishRecord
from .digester import CookCycleRecord, ContinuousDigesterState

class AdvisorEngine:
    """Embedded intelligence layer for process recommendations."""
    
    def evaluate_cook(self, ccr: CookCycleRecord, furnish: FurnishRecord) -> List[Dict]:
        """Analyzes a cook cycle and generates recommendations."""
        recommendations = []
        
        # H-Factor analysis
        if ccr.h_factor_final < (furnish.cook_temp_C * 0.8): # Simplified check
            recommendations.append({
                "code": "ADV-H01",
                "category": "H-Factor",
                "message": f"H-factor deficit identified for {ccr.ccr_id}. Recommend extending cook hold time.",
                "priority": "WARNING"
            })
            
        # EA Residual check (if available)
        if ccr.ea_charged_pct > furnish.ea_baseline_pct * 1.2:
            recommendations.append({
                "code": "ADV-C02",
                "category": "Chemical",
                "message": f"EA charge exceeds furnish baseline by >20%. Reduce next cook by 1.2%.",
                "priority": "INFO"
            })

        # IQI Check
        if ccr.iqi_score < 70:
            recommendations.append({
                "code": "ADV-P01",
                "category": "Pre-Treatment",
                "message": f"IQI score {ccr.iqi_score:.1f} is below threshold 70. Extend impregnation.",
                "priority": "WARNING"
            })
            
        return recommendations

    def evaluate_continuous(self, state: ContinuousDigesterState, furnish: FurnishRecord) -> List[Dict]:
        """Analyzes continuous digester state."""
        recommendations = []
        if state.kappa_at_blow_pred > furnish.kappa_target_range[1]:
            recommendations.append({
                "code": "ADV-K01",
                "category": "Kappa",
                "message": f"Predicted blow kappa {state.kappa_at_blow_pred:.1f} exceeds target range. Increase EA.",
                "priority": "CRITICAL"
            })
        return recommendations
