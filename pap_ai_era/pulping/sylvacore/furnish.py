from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class FurnishClass(Enum):
    SOFTWOOD = "SOFTWOOD"
    HARDWOOD = "HARDWOOD"
    AGRO_RESIDUE = "AGRO_RESIDUE"
    BAMBOO = "BAMBOO"
    BLEND = "BLEND"

@dataclass
class FurnishRecord:
    furnish_id: str
    furnish_name: str
    furnish_class: FurnishClass
    basic_density: float # kg/m3
    lignin_content: float # % OD
    cellulose_content: float # % OD
    hemicellulose_content: float # % OD
    moisture_typical: float # %
    reactivity_factor_Rf: float # dimensionless
    ea_baseline_pct: float # % OD wood
    sulfidity_optimum_range: List[float] # [min, max]
    lw_ratio_typical: float # m3/ADt
    preheat_temp_max_C: float # °C
    impreg_temp_C: float # °C
    impreg_duration_min: float # minutes
    cook_temp_C: float # °C
    kappa_target_range: List[float] # [min, max]
    blend_components: Dict[str, float] = field(default_factory=dict) # {id: frac}
    
    # Regression coefficients for H-target = A * exp(-B * kappa) + C
    h_model_coeffs: Dict[str, float] = field(default_factory=lambda: {"A": 1000.0, "B": 0.05, "C": 100.0})
    
    # Kappa model coefficients
    k_rate_k1: float = 0.002 # delignification rate
    k_alkali_k2: float = 0.5 # alkali sensitivity

class FurnishLib:
    """Master reference database for all raw material types."""
    def __init__(self):
        self.library: Dict[str, FurnishRecord] = {}
        self._load_defaults()

    def _load_defaults(self):
        defaults = [
            FurnishRecord(
                "SW_PINE_LOBLOLLY", "Loblolly Pine", FurnishClass.SOFTWOOD,
                450, 28.5, 41.0, 25.0, 45.0, 1.00, 17.0, [28, 32], 3.5,
                120, 130, 45, 168, [28, 35], h_model_coeffs={"A": 15000, "B": 0.08, "C": 200}
            ),
            FurnishRecord(
                "HW_EUC_GLOB", "Eucalyptus Globulus", FurnishClass.HARDWOOD,
                520, 24.0, 48.0, 20.0, 50.0, 0.72, 14.0, [22, 26], 4.0,
                125, 135, 30, 160, [14, 18], h_model_coeffs={"A": 8000, "B": 0.12, "C": 150}
            ),
            FurnishRecord(
                "AGRO_BAGASSE", "Bagasse", FurnishClass.AGRO_RESIDUE,
                160, 20.0, 42.0, 28.0, 50.0, 0.55, 12.0, [20, 24], 5.0,
                110, 120, 20, 155, [12, 18], h_model_coeffs={"A": 5000, "B": 0.15, "C": 100}
            ),
            FurnishRecord(
                "BAMBOO_MOSO", "Bamboo (Moso)", FurnishClass.BAMBOO,
                600, 26.0, 45.0, 22.0, 40.0, 0.68, 15.0, [24, 28], 4.5,
                120, 130, 40, 162, [14, 20], h_model_coeffs={"A": 7000, "B": 0.10, "C": 120}
            )
        ]
        for f in defaults:
            self.add_furnish(f)

    def add_furnish(self, record: FurnishRecord):
        self.library[record.furnish_id] = record

    def get_furnish(self, furnish_id: str) -> Optional[FurnishRecord]:
        return self.library.get(furnish_id)

    def calculate_blend_properties(self, blend_id: str, components: Dict[str, float]) -> FurnishRecord:
        """Computes weighted properties for a blend."""
        # This is a simplified version for the initialization
        # Real implementation would interpolate all numeric fields
        total_frac = sum(components.values())
        if abs(total_frac - 1.0) > 1e-6:
             # Normalize if needed or raise error
             pass
             
        # Start with a dummy Softwood template
        base = self.get_furnish("SW_PINE_LOBLOLLY")
        
        # Calculate weighted average Rf
        weighted_rf = 0.0
        for fid, frac in components.items():
            comp = self.get_furnish(fid)
            if comp:
                weighted_rf += comp.reactivity_factor_Rf * frac
        
        return FurnishRecord(
            furnish_id=blend_id,
            furnish_name=f"Blend {blend_id}",
            furnish_class=FurnishClass.BLEND,
            basic_density=400, # Simplified
            lignin_content=25,
            cellulose_content=45,
            hemicellulose_content=20,
            moisture_typical=45,
            reactivity_factor_Rf=weighted_rf,
            ea_baseline_pct=16.0,
            sulfidity_optimum_range=[25, 30],
            lw_ratio_typical=3.7,
            preheat_temp_max_C=120,
            impreg_temp_C=130,
            impreg_duration_min=40,
            cook_temp_C=166,
            kappa_target_range=[20, 28],
            blend_components=components
        )
