import math
import numpy as np
from typing import Dict, List

class ZetaPredictor:
    """Hybrid Stern-Debye model for Charge and Zeta Potential prediction."""
    
    def __init__(self, k_constants=None):
        # k1..k3: mill-specific constants
        self.k = k_constants or {"k1": 0.8, "k2": 0.15, "k3": 0.05}

    def calculate_charge_density(self, dosages: Dict[str, float], chem_db, ionic_strength: float = 0.01) -> float:
        """
        q = Σ (dosage_i * charge_i) / (1 + k2 * I + k3 * I^0.5)
        Where dosages is {chem_id: kg/t}
        """
        net_charge = 0.0
        for chem_id, dosage in dosages.items():
            chem = chem_db.get_chemical(chem_id)
            if chem:
                net_charge += dosage * chem.charge_density
        
        # Denominator accounts for ionic strength (shielding effect)
        denominator = 1.0 + self.k["k2"] * ionic_strength + self.k["k3"] * math.sqrt(ionic_strength)
        # Scaled to produce meq/L in typical mill range (0.01 to 0.5)
        q = (self.k["k1"] * net_charge * 0.01) / denominator
        return q

    def predict_zeta_potential(self, charge_density: float, ph: float) -> float:
        """
        Empirical mapping from charge density to Zeta Potential (mV)
        """
        # Typically -30 to +20 mV
        ph_shift = (ph - 7.0) * 1.5
        zeta = charge_density * 2.0 - 15.0 - ph_shift
        return zeta

class BondStrengthModel:
    """Predicts Fiber Bonding Index (FBI) and Paper Break Probability."""
    
    def __init__(self, constants=None):
        # α..η: empirical constants
        self.c = constants or {"alpha": 1.5, "beta": 0.4, "gamma": 0.3, "fbi_crit": 12.0}

    def calculate_fbi(self, zeta_potential: float, starch_dosage: float, gsm: float, refining_energy: float) -> float:
        """
        FBI = α * log(Refining) + β * Starch + γ * (1 - abs(ζ/20))
        """
        # Advantageous to be near zero zeta (0 to +5 mV)
        zeta_factor = 1.0 - abs(zeta_potential - 2.5) / 30.0
        
        fbi = (self.c["alpha"] * math.log(refining_energy + 1) + 
               self.c["beta"] * starch_dosage * 0.5 + 
               self.c["gamma"] * zeta_factor * 20.0)
        return fbi

    def predict_break_probability(self, fbi: float) -> float:
        """
        P_break = 1 / (1 + exp(κ * (FBI - FBI_crit)))
        """
        kappa = 0.5 # sensitivity constant
        fbi_crit = self.c["fbi_crit"]
        
        prob = 1.0 / (1.0 + math.exp(kappa * (fbi - fbi_crit)))
        return prob
