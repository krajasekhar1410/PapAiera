from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from .furnish import FurnishRecord

@dataclass
class ZoneState:
    name: str
    temp_C: float
    residence_time_min: float
    h_accum: float = 0.0
    ea_gpl: float = 0.0
    kappa_exit_pred: float = 0.0

@dataclass
class ContinuousDigesterState:
    digester_id: str
    furnish_active: str
    zone_states: List[ZoneState] = field(default_factory=list)
    h_total_cumulative: float = 0.0
    kappa_at_blow_pred: float = 0.0
    throughput_ADt_h: float = 0.0
    advisor_flags: List[str] = field(default_factory=list)

@dataclass
class BatchDigesterIdentity:
    bdi_code: str
    vessel_name: str
    commissioned_date: datetime
    vessel_volume_m3: float
    design_pressure_kPa: float
    lining_material: str
    total_cook_cycles: int = 0
    status: str = "ACTIVE"
    kappa_bias_correction: float = 0.0
    heat_up_curve_id: str = "DEFAULT"

@dataclass
class CookCycleRecord:
    ccr_id: str
    bdi_code: str
    cook_number: int
    furnish_id: str
    chip_charge_OD_kg: float
    ea_charged_pct: float
    sulfidity_pct: float
    h_factor_final: float = 0.0
    kappa_target: float = 0.0
    kappa_actual: Optional[float] = None
    iqi_score: float = 0.0
    yield_pct: float = 0.0
    anomaly_flags: List[str] = field(default_factory=list)

class DigesterManager:
    """Manages Batch and Continuous digester operations."""
    def __init__(self):
        self.batch_vessels: Dict[str, BatchDigesterIdentity] = {}
        self.cook_history: List[CookCycleRecord] = []
        self.continuous_units: Dict[str, ContinuousDigesterState] = {}

    def register_batch_digester(self, identity: BatchDigesterIdentity):
        self.batch_vessels[identity.bdi_code] = identity

    def start_cook(self, bdi_code: str, furnish_id: str, kappa_target: float) -> CookCycleRecord:
        vessel = self.batch_vessels.get(bdi_code)
        if not vessel:
            raise ValueError(f"Batch Digester {bdi_code} not registered.")
        
        vessel.total_cook_cycles += 1
        ccr_id = f"{bdi_code}-{datetime.now().strftime('%Y%m%d')}-{vessel.total_cook_cycles:03d}"
        
        record = CookCycleRecord(
            ccr_id=ccr_id,
            bdi_code=bdi_code,
            cook_number=vessel.total_cook_cycles,
            furnish_id=furnish_id,
            chip_charge_OD_kg=0.0,
            ea_charged_pct=0.0,
            sulfidity_pct=0.0,
            kappa_target=kappa_target
        )
        self.cook_history.append(record)
        return record
