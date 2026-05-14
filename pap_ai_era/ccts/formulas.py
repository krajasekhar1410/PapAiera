"""
Dynamic Formula Engine for CCTS
=================================

Provides configurable, overridable calculation formulas for carbon
accounting KPIs. Users can register custom formulas or override
built-in ones without modifying source code.
"""

import math
from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class FormulaSpec:
    """Specification for a calculation formula."""
    name: str
    description: str
    category: str
    unit: str
    func: Callable
    parameters: List[str]


class FormulaEngine:
    """
    Dynamic formula engine for carbon KPI calculations.

    Comes with built-in formulas for common sustainability KPIs.
    Users can override any formula or register new ones.

    Example:
        >>> from pap_ai_era.ccts import FormulaEngine
        >>> fe = FormulaEngine()
        >>> fe.list_formulas()
        >>> result = fe.execute('co2_per_ton', total_co2e=500, production_tons=1000)
        >>> print(result)  # 0.5 tCO2e/ton
    """

    def __init__(self):
        self._formulas: Dict[str, FormulaSpec] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register all built-in formulas."""

        # --- Emission Intensity KPIs ---
        self.register('co2_per_ton',
            description='CO2 intensity per ton of product',
            category='emission', unit='tCO2e/ton',
            func=lambda total_co2e, production_tons: total_co2e / production_tons,
            parameters=['total_co2e', 'production_tons'])

        self.register('co2_per_gj_steam',
            description='CO2 per GJ of steam generated',
            category='emission', unit='kgCO2/GJ',
            func=lambda fuel_co2_kg, steam_gj: fuel_co2_kg / steam_gj if steam_gj > 0 else 0,
            parameters=['fuel_co2_kg', 'steam_gj'])

        self.register('scope2_per_mwh',
            description='Grid emissions per MWh consumed',
            category='emission', unit='tCO2e/MWh',
            func=lambda grid_factor, mwh: (grid_factor * mwh) / 1000.0,
            parameters=['grid_factor', 'mwh'])

        # --- Energy Intensity KPIs ---
        self.register('steam_intensity',
            description='Steam consumption per ton of product',
            category='energy', unit='GJ/ton',
            func=lambda steam_gj, production_tons: steam_gj / production_tons,
            parameters=['steam_gj', 'production_tons'])

        self.register('electricity_intensity',
            description='Electricity consumption per ton of product',
            category='energy', unit='kWh/ton',
            func=lambda electricity_kwh, production_tons: electricity_kwh / production_tons,
            parameters=['electricity_kwh', 'production_tons'])

        self.register('total_energy_intensity',
            description='Total energy (steam + electric) per ton',
            category='energy', unit='GJ/ton',
            func=lambda steam_gj, electricity_kwh, production_tons:
                (steam_gj + electricity_kwh * 3.6 / 1000.0) / production_tons,
            parameters=['steam_gj', 'electricity_kwh', 'production_tons'])

        self.register('biomass_share',
            description='Fraction of energy from biomass sources',
            category='energy', unit='%',
            func=lambda biomass_gj, total_fuel_gj: (biomass_gj / total_fuel_gj * 100.0) if total_fuel_gj > 0 else 0,
            parameters=['biomass_gj', 'total_fuel_gj'])

        # --- Water KPIs ---
        self.register('water_intensity',
            description='Water consumption per ton of product',
            category='water', unit='m3/ton',
            func=lambda water_m3, production_tons: water_m3 / production_tons,
            parameters=['water_m3', 'production_tons'])

        # --- Carbon Credit KPIs ---
        self.register('credit_potential',
            description='Carbon credit revenue potential',
            category='credit', unit='USD',
            func=lambda savings_tco2e, credit_price, discount=0.85:
                savings_tco2e * credit_price * discount,
            parameters=['savings_tco2e', 'credit_price', 'discount'])

        self.register('reduction_pct',
            description='Emission reduction percentage vs baseline',
            category='credit', unit='%',
            func=lambda baseline_co2, current_co2:
                ((baseline_co2 - current_co2) / baseline_co2 * 100.0) if baseline_co2 > 0 else 0,
            parameters=['baseline_co2', 'current_co2'])

        self.register('payback_years',
            description='Simple payback period for emission reduction project',
            category='credit', unit='years',
            func=lambda investment_usd, annual_credit_usd, annual_energy_savings_usd=0:
                investment_usd / (annual_credit_usd + annual_energy_savings_usd)
                if (annual_credit_usd + annual_energy_savings_usd) > 0 else float('inf'),
            parameters=['investment_usd', 'annual_credit_usd', 'annual_energy_savings_usd'])

        # --- ESG KPIs ---
        self.register('esg_carbon_score',
            description='Carbon performance score (0-100, higher=better)',
            category='esg', unit='score',
            func=lambda co2_per_ton, benchmark_co2_per_ton:
                max(0, min(100, 100 * (1 - co2_per_ton / benchmark_co2_per_ton)))
                if benchmark_co2_per_ton > 0 else 50,
            parameters=['co2_per_ton', 'benchmark_co2_per_ton'])

    def register(self, name: str, description: str, category: str,
                 unit: str, func: Callable, parameters: List[str]):
        """Register or override a formula."""
        self._formulas[name] = FormulaSpec(
            name=name, description=description, category=category,
            unit=unit, func=func, parameters=parameters
        )

    def execute(self, formula_name: str, **kwargs) -> float:
        """Execute a formula by name with named parameters."""
        if formula_name not in self._formulas:
            raise KeyError(f"Formula '{formula_name}' not found. Available: {list(self._formulas.keys())}")
        spec = self._formulas[formula_name]
        try:
            return spec.func(**kwargs)
        except TypeError as e:
            raise TypeError(
                f"Formula '{formula_name}' expects parameters: {spec.parameters}. Error: {e}"
            )

    def list_formulas(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """List available formulas, optionally filtered by category."""
        result = []
        for name, spec in self._formulas.items():
            if category and spec.category != category:
                continue
            result.append({
                'name': name, 'description': spec.description,
                'category': spec.category, 'unit': spec.unit,
                'parameters': spec.parameters,
            })
        return result

    def get_categories(self) -> List[str]:
        return list(set(s.category for s in self._formulas.values()))
