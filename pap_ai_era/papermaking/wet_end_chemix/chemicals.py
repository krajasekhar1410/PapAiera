from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class ChemicalCategory(Enum):
    RETENTION = "RETENTION"
    SIZING = "SIZING"
    FIXATIVE = "FIXATIVE"
    PH_CONTROL = "PH_CONTROL"
    DYE = "DYE"
    STRENGTH = "STRENGTH"
    DEFOAMER = "DEFOAMER"

@dataclass
class Chemical:
    id: str
    name: str
    category: ChemicalCategory
    charge_density: float # meq/g
    active_solids_pct: float
    unit_cost: float
    optimal_ph_range: List[float]
    optimal_temp_range: List[float]
    hydrolysis_rate_constant: float = 0.0 # for AKD/ASA
    interaction_map: Dict[str, float] = field(default_factory=dict) # {target_category: impact_factor}

class ChemicalDatabase:
    """Built-in database of common paper chemicals."""
    def __init__(self):
        self.chemicals: Dict[str, Chemical] = {}
        self._load_defaults()

    def _load_defaults(self):
        defaults = [
            Chemical("CPAM", "Cationic Polyacrylamide", ChemicalCategory.RETENTION, 
                     2.5, 40.0, 3.5, [4.5, 8.5], [10, 60]),
            Chemical("AKD", "Alkyl Ketene Dimer", ChemicalCategory.SIZING, 
                     0.1, 15.0, 2.2, [6.5, 8.5], [20, 50], hydrolysis_rate_constant=0.01),
            Chemical("ASA", "Alkenyl Succinic Anhydride", ChemicalCategory.SIZING, 
                     -0.2, 100.0, 1.8, [6.0, 7.5], [20, 45], hydrolysis_rate_constant=0.05),
            Chemical("PAC", "Poly-Aluminium Chloride", ChemicalCategory.FIXATIVE, 
                     5.0, 30.0, 0.8, [4.5, 7.0], [5, 60]),
            Chemical("STARCH", "Cationic Starch", ChemicalCategory.STRENGTH, 
                     0.4, 25.0, 0.6, [4.5, 9.0], [40, 70]),
            Chemical("ALUM", "Aluminium Sulphate", ChemicalCategory.FIXATIVE, 
                     4.0, 50.0, 0.4, [4.0, 5.5], [5, 60]),
        ]
        for c in defaults:
            self.add_chemical(c)

    def add_chemical(self, chemical: Chemical):
        self.chemicals[chemical.id] = chemical

    def get_chemical(self, chemical_id: str) -> Optional[Chemical]:
        return self.chemicals.get(chemical_id)
