"""
Carbon Calculation Engine for CCTS
====================================

Calculates Scope 1, Scope 2, and Scope 3 carbon emissions for any
pulp, paper, board, or packaging product based on production data
and configurable emission factors.

Follows GHG Protocol Corporate Standard methodology.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from .factors import FactorEngine
from .products import ProductMaster, ProductGrade


@dataclass
class CarbonResult:
    """Complete carbon footprint result for a production run."""
    # Identification
    product_grade: str
    production_tons: float

    # Scope 1 — Direct emissions
    scope1_fuel: float = 0.0           # tCO2e from fuel combustion
    scope1_process: float = 0.0        # tCO2e from process (lime kiln etc)
    scope1_total: float = 0.0

    # Scope 2 — Indirect (energy)
    scope2_electricity: float = 0.0    # tCO2e from grid electricity
    scope2_steam: float = 0.0         # tCO2e from purchased steam
    scope2_total: float = 0.0

    # Scope 3 — Value chain
    scope3_fiber: float = 0.0         # tCO2e from fiber sourcing
    scope3_chemicals: float = 0.0     # tCO2e from chemical manufacturing
    scope3_transport: float = 0.0     # tCO2e from logistics
    scope3_total: float = 0.0

    # Totals
    total_tco2e: float = 0.0
    co2e_per_ton: float = 0.0

    # Breakdown details
    fuel_breakdown: Dict[str, float] = field(default_factory=dict)
    chemical_breakdown: Dict[str, float] = field(default_factory=dict)
    fiber_breakdown: Dict[str, float] = field(default_factory=dict)

    # Benchmarking
    benchmark_co2_per_ton: Optional[float] = None
    deviation_from_benchmark: Optional[float] = None

    def summary(self) -> str:
        lines = [
            f"=== Carbon Footprint: {self.product_grade} ===",
            f"Production: {self.production_tons:.0f} tons",
            f"",
            f"Scope 1 (Direct):     {self.scope1_total:>10.1f} tCO2e",
            f"  Fuel combustion:    {self.scope1_fuel:>10.1f} tCO2e",
            f"  Process emissions:  {self.scope1_process:>10.1f} tCO2e",
            f"Scope 2 (Energy):     {self.scope2_total:>10.1f} tCO2e",
            f"  Electricity:        {self.scope2_electricity:>10.1f} tCO2e",
            f"  Purchased steam:    {self.scope2_steam:>10.1f} tCO2e",
            f"Scope 3 (Value chain):{self.scope3_total:>10.1f} tCO2e",
            f"  Fiber sourcing:     {self.scope3_fiber:>10.1f} tCO2e",
            f"  Chemicals:          {self.scope3_chemicals:>10.1f} tCO2e",
            f"  Transport:          {self.scope3_transport:>10.1f} tCO2e",
            f"",
            f"TOTAL:                {self.total_tco2e:>10.1f} tCO2e",
            f"Per ton of product:   {self.co2e_per_ton:>10.3f} tCO2e/ton",
        ]
        if self.benchmark_co2_per_ton is not None:
            lines.append(f"Benchmark:            {self.benchmark_co2_per_ton/1000:>10.3f} tCO2e/ton")
            lines.append(f"Deviation:            {self.deviation_from_benchmark:>+10.1f}%")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_grade': self.product_grade,
            'production_tons': self.production_tons,
            'scope1_total': round(self.scope1_total, 2),
            'scope2_total': round(self.scope2_total, 2),
            'scope3_total': round(self.scope3_total, 2),
            'total_tco2e': round(self.total_tco2e, 2),
            'co2e_per_ton': round(self.co2e_per_ton, 4),
        }


class CarbonCalculator:
    """
    Calculates carbon emissions for pulp and paper production.

    Supports Scope 1 (fuel + process), Scope 2 (electricity + steam),
    and Scope 3 (fiber + chemicals + transport) calculations per
    GHG Protocol methodology.

    Example:
        >>> from pap_ai_era.ccts import CarbonCalculator
        >>> calc = CarbonCalculator()
        >>> result = calc.calculate(
        ...     product='kraft_liner',
        ...     production_tons=1000,
        ...     fuel={'coal_bituminous': 5000, 'natural_gas': 2000},
        ...     electricity_mwh=550,
        ...     electricity_region='india_national'
        ... )
        >>> print(result.summary())
    """

    def __init__(self, factors: Optional[FactorEngine] = None,
                 products: Optional[ProductMaster] = None):
        self.factors = factors or FactorEngine()
        self.products = products or ProductMaster()

    def calculate(
        self,
        product: str,
        production_tons: float,
        fuel: Optional[Dict[str, float]] = None,
        electricity_mwh: float = 0.0,
        electricity_region: str = 'india_national',
        steam_purchased_gj: float = 0.0,
        steam_source: str = 'grid_default',
        process_emissions: Optional[Dict[str, float]] = None,
        fiber_tons: Optional[Dict[str, float]] = None,
        chemicals_tons: Optional[Dict[str, float]] = None,
        transport: Optional[List[Dict[str, float]]] = None,
    ) -> CarbonResult:
        """
        Calculate complete carbon footprint.

        Args:
            product: Product grade ID (e.g., 'kraft_liner').
            production_tons: Total production in metric tons.
            fuel: Dict of {fuel_type: GJ consumed}.
            electricity_mwh: Grid electricity consumed in MWh.
            electricity_region: Region for grid factor lookup.
            steam_purchased_gj: Purchased steam in GJ.
            steam_source: Steam source for factor lookup.
            process_emissions: Dict of {process: tons_product_affected}.
            fiber_tons: Dict of {fiber_type: ADT consumed}. If None, estimated from product.
            chemicals_tons: Dict of {chemical: tons consumed}.
            transport: List of {mode, distance_km, tons} dicts.

        Returns:
            CarbonResult with full scope breakdown.
        """
        result = CarbonResult(product_grade=product, production_tons=production_tons)

        # Get product info for benchmarking
        try:
            grade = self.products.get_grade(product)
            result.benchmark_co2_per_ton = grade.typical_co2_per_ton
        except KeyError:
            grade = None

        # === SCOPE 1: Direct Emissions ===
        # Fuel combustion
        fuel = fuel or {}
        fuel_breakdown = {}
        for fuel_type, gj in fuel.items():
            factor = self.factors.get_fuel_factor(fuel_type)
            emissions_kg = gj * factor
            emissions_t = emissions_kg / 1000.0
            fuel_breakdown[fuel_type] = round(emissions_t, 2)
            result.scope1_fuel += emissions_t

        result.fuel_breakdown = fuel_breakdown

        # Process emissions
        process_emissions = process_emissions or {}
        if grade and not process_emissions:
            # Auto-estimate lime kiln if kraft product
            if any(f.startswith('virgin') and 'kraft' in f for f in (grade.fiber_mix or {})):
                process_emissions = {'lime_kiln': production_tons}

        for process, tons_affected in process_emissions.items():
            factor = self.factors.get_process_factor(process)
            result.scope1_process += (factor * tons_affected) / 1000.0

        result.scope1_total = result.scope1_fuel + result.scope1_process

        # === SCOPE 2: Indirect Energy Emissions ===
        if electricity_mwh > 0:
            elec_factor = self.factors.get_electricity_factor(electricity_region)
            result.scope2_electricity = (electricity_mwh * elec_factor) / 1000.0

        if steam_purchased_gj > 0:
            steam_factor = self.factors.get_steam_factor(steam_source)
            result.scope2_steam = (steam_purchased_gj * steam_factor) / 1000.0

        result.scope2_total = result.scope2_electricity + result.scope2_steam

        # === SCOPE 3: Value Chain ===
        # Fiber sourcing
        fiber_breakdown = {}
        if fiber_tons is None and grade:
            fiber_tons = {}
            for fiber_type, fraction in grade.fiber_mix.items():
                fiber_tons[fiber_type] = production_tons * fraction

        fiber_tons = fiber_tons or {}
        for fiber_type, adt in fiber_tons.items():
            try:
                factor = self.factors.get_fiber_factor(fiber_type)
                emissions_t = (adt * factor) / 1000.0
                fiber_breakdown[fiber_type] = round(emissions_t, 2)
                result.scope3_fiber += emissions_t
            except KeyError:
                pass

        result.fiber_breakdown = fiber_breakdown

        # Chemicals
        chemical_breakdown = {}
        chemicals_tons = chemicals_tons or {}
        for chem, tons in chemicals_tons.items():
            factor_key = f'chemical_makeup_{chem}'
            try:
                factor = self.factors.get_process_factor(factor_key)
                emissions_t = (tons * factor) / 1000.0
                chemical_breakdown[chem] = round(emissions_t, 2)
                result.scope3_chemicals += emissions_t
            except KeyError:
                pass

        result.chemical_breakdown = chemical_breakdown

        # Transport
        transport = transport or []
        for leg in transport:
            mode = leg.get('mode', 'road')
            dist = leg.get('distance_km', 0)
            tons = leg.get('tons', production_tons)
            factor_key = f'transport_{mode}_per_ton_km'
            try:
                factor = self.factors.get_process_factor(factor_key)
                result.scope3_transport += (tons * dist * factor) / 1000.0
            except KeyError:
                pass

        result.scope3_total = result.scope3_fiber + result.scope3_chemicals + result.scope3_transport

        # === TOTALS ===
        result.total_tco2e = result.scope1_total + result.scope2_total + result.scope3_total
        result.co2e_per_ton = result.total_tco2e / production_tons if production_tons > 0 else 0.0

        # Benchmark comparison
        if result.benchmark_co2_per_ton:
            benchmark_t = result.benchmark_co2_per_ton / 1000.0
            if benchmark_t > 0:
                result.deviation_from_benchmark = (
                    (result.co2e_per_ton - benchmark_t) / benchmark_t * 100.0
                )

        return result

    def quick_estimate(self, product: str, production_tons: float,
                       electricity_region: str = 'india_national') -> CarbonResult:
        """
        Quick carbon estimate using only product defaults.

        Uses benchmark energy intensities from the product catalog
        to estimate emissions without detailed input data.
        """
        grade = self.products.get_grade(product)
        elec_mwh = grade.electricity_intensity_kwh_per_ton * production_tons / 1000.0
        steam_gj = grade.steam_intensity_gj_per_ton * production_tons

        return self.calculate(
            product=product,
            production_tons=production_tons,
            fuel={'natural_gas': steam_gj * 0.6, 'biomass_black_liquor': steam_gj * 0.4},
            electricity_mwh=elec_mwh,
            electricity_region=electricity_region,
        )
