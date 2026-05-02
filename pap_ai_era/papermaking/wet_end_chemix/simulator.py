from typing import Dict, List, Optional
from .chemicals import ChemicalDatabase, ChemicalCategory
from .models import ZetaPredictor, BondStrengthModel

class WetEndSimulator:
    """Orchestrates the dosing chain simulation and calculates final properties."""
    
    def __init__(self, chem_db: ChemicalDatabase):
        self.db = chem_db
        self.zeta_predictor = ZetaPredictor()
        self.bond_model = BondStrengthModel()

    def run_simulation(self, 
                       dosages: Dict[str, float], 
                       ph: float, 
                       temp_C: float, 
                       refining_energy: float, 
                       gsm: float,
                       ionic_strength: float = 0.05):
        """
        Simulates the wet-end state.
        dosages: {chem_id: kg/t}
        """
        # 1. Charge and Zeta Calculation
        charge = self.zeta_predictor.calculate_charge_density(dosages, self.db, ionic_strength)
        zeta = self.zeta_predictor.predict_zeta_potential(charge, ph)
        
        # 2. Temperature and pH efficiency effects
        sizing_efficiency = self._calculate_sizing_efficiency(dosages, ph, temp_C)
        
        # 3. Fiber Bonding and Break Risk
        starch_dosage = dosages.get("STARCH", 0.0)
        fbi = self.bond_model.calculate_fbi(zeta, starch_dosage, gsm, refining_energy)
        break_risk = self.bond_model.predict_break_probability(fbi)
        
        return {
            "zeta_potential_mv": zeta,
            "charge_density_meq_l": charge,
            "fiber_bonding_index": fbi,
            "break_risk_pct": break_risk * 100.0,
            "sizing_efficiency": sizing_efficiency,
            "status": self._get_status_string(zeta, break_risk)
        }

    def _calculate_sizing_efficiency(self, dosages: Dict[str, float], ph: float, temp_C: float) -> float:
        """Calculates sizing performance based on hydrolysis and pH windows."""
        eff = 1.0
        if "AKD" in dosages:
            # AKD hydrolysis: k = A·exp(-Ea/RT) × 10^(pH-pH_opt)
            # Optimal pH 8.0, Temp < 40C
            ph_penalty = 10 ** (abs(ph - 8.0) - 1.0) if ph < 7.0 or ph > 9.0 else 0.0
            temp_penalty = max(0, (temp_C - 45.0) / 10.0)
            eff *= max(0, 1.0 - (ph_penalty * 0.1 + temp_penalty * 0.2))
        return eff

    def _get_status_string(self, zeta: float, break_risk: float) -> str:
        if break_risk > 0.15: # 15% risk
            return "CRITICAL: High Break Risk"
        if abs(zeta) > 15.0:
            return "WARNING: Unstable Charge"
        if -5.0 < zeta < 5.0:
            return "OPTIMAL: Stable Wet-End"
        return "STABLE"

class LayeredSimulator:
    """Extends simulation to multi-layer board machines."""
    def __init__(self, chem_db: ChemicalDatabase):
        self.simulator = WetEndSimulator(chem_db)
        
    def simulate_layers(self, layer_configs: List[Dict]):
        """
        layer_configs: List of dicts with 'dosages', 'ph', etc.
        """
        results = []
        for config in layer_configs:
            res = self.simulator.run_simulation(**config)
            results.append(res)
        return results
