"""
Carbon Credit Estimator for CCTS
==================================

Estimates carbon credits generated from emission reduction projects,
fuel switching, energy efficiency improvements, and process optimization.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from .carbon import CarbonResult


@dataclass
class CreditResult:
    """Result of a carbon credit estimation."""
    project_name: str
    baseline_tco2e: float
    current_tco2e: float
    savings_tco2e: float
    credit_tons: float
    credit_value_usd: float
    price_per_ton_usd: float
    reduction_pct: float
    project_type: str
    methodology: str
    details: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        return "\n".join([
            f"=== Carbon Credit Estimate: {self.project_name} ===",
            f"Project Type:      {self.project_type}",
            f"Methodology:       {self.methodology}",
            f"Baseline:          {self.baseline_tco2e:,.1f} tCO2e",
            f"Current/Proposed:  {self.current_tco2e:,.1f} tCO2e",
            f"Savings:           {self.savings_tco2e:,.1f} tCO2e",
            f"Reduction:         {self.reduction_pct:.1f}%",
            f"Credits Generated: {self.credit_tons:,.1f} tons",
            f"Credit Price:      ${self.price_per_ton_usd:.2f}/ton",
            f"Total Value:       ${self.credit_value_usd:,.2f}",
        ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_name': self.project_name,
            'baseline_tco2e': round(self.baseline_tco2e, 2),
            'current_tco2e': round(self.current_tco2e, 2),
            'savings_tco2e': round(self.savings_tco2e, 2),
            'credit_tons': round(self.credit_tons, 2),
            'credit_value_usd': round(self.credit_value_usd, 2),
            'reduction_pct': round(self.reduction_pct, 2),
        }


class CreditEstimator:
    """
    Estimates carbon credits from emission reduction activities.

    Supports common project types in pulp & paper:
    - Fuel switching (coal to gas, fossil to biomass)
    - Energy efficiency improvements
    - Process optimization
    - Custom baseline vs actual comparison

    Example:
        >>> from pap_ai_era.ccts import CreditEstimator
        >>> ce = CreditEstimator(price_per_ton=25.0)
        >>> result = ce.from_fuel_switch(
        ...     project_name="Coal to Biomass",
        ...     production_tons=50000,
        ...     baseline_fuel={'coal_bituminous': 200000},
        ...     proposed_fuel={'biomass_wood': 180000, 'natural_gas': 30000}
        ... )
        >>> print(result.summary())
    """

    # Default carbon credit prices (USD/ton CO2e)
    PRICE_RANGES = {
        'voluntary_market': 15.0,
        'eu_ets': 65.0,
        'india_ccts': 10.0,
        'gold_standard': 25.0,
        'verra_vcs': 18.0,
    }

    def __init__(self, price_per_ton: float = 15.0, discount_factor: float = 0.85):
        """
        Args:
            price_per_ton: Credit price in USD per ton CO2e.
            discount_factor: Conservative discount (0.85 = 15% buffer for leakage/uncertainty).
        """
        self.price = price_per_ton
        self.discount = discount_factor

    def from_results(self, project_name: str,
                     baseline: CarbonResult, current: CarbonResult,
                     project_type: str = 'general') -> CreditResult:
        """Estimate credits from two CarbonResult objects (baseline vs current)."""
        savings = baseline.total_tco2e - current.total_tco2e
        return self._build_result(project_name, baseline.total_tco2e,
                                  current.total_tco2e, savings, project_type,
                                  'Baseline-vs-Actual')

    def from_fuel_switch(self, project_name: str, production_tons: float,
                         baseline_fuel: Dict[str, float],
                         proposed_fuel: Dict[str, float]) -> CreditResult:
        """
        Estimate credits from fuel switching.

        Args:
            baseline_fuel: {fuel_type: GJ} for current/baseline scenario.
            proposed_fuel: {fuel_type: GJ} for proposed scenario.
        """
        from .factors import FactorEngine
        fe = FactorEngine()

        baseline_co2 = sum(gj * fe.get_fuel_factor(f) / 1000.0
                           for f, gj in baseline_fuel.items())
        proposed_co2 = sum(gj * fe.get_fuel_factor(f) / 1000.0
                           for f, gj in proposed_fuel.items())
        savings = baseline_co2 - proposed_co2

        return self._build_result(project_name, baseline_co2, proposed_co2,
                                  savings, 'fuel_switch', 'Fuel Switching Methodology')

    def from_efficiency(self, project_name: str,
                        baseline_co2e: float, efficiency_gain_pct: float) -> CreditResult:
        """
        Estimate credits from energy efficiency improvement.

        Args:
            baseline_co2e: Current annual emissions in tCO2e.
            efficiency_gain_pct: Expected efficiency gain (e.g., 15 for 15%).
        """
        reduction = baseline_co2e * (efficiency_gain_pct / 100.0)
        current = baseline_co2e - reduction
        return self._build_result(project_name, baseline_co2e, current,
                                  reduction, 'energy_efficiency',
                                  'Energy Efficiency Improvement')

    def from_custom(self, project_name: str,
                    baseline_tco2e: float, proposed_tco2e: float,
                    project_type: str = 'custom') -> CreditResult:
        """Direct baseline vs proposed comparison."""
        savings = baseline_tco2e - proposed_tco2e
        return self._build_result(project_name, baseline_tco2e, proposed_tco2e,
                                  savings, project_type, 'Custom Methodology')

    def estimate_portfolio(self, projects: List[CreditResult]) -> Dict[str, Any]:
        """Aggregate multiple credit projects into a portfolio summary."""
        total_savings = sum(p.savings_tco2e for p in projects)
        total_credits = sum(p.credit_tons for p in projects)
        total_value = sum(p.credit_value_usd for p in projects)
        return {
            'num_projects': len(projects),
            'total_savings_tco2e': round(total_savings, 1),
            'total_credits_tons': round(total_credits, 1),
            'total_value_usd': round(total_value, 2),
            'projects': [p.to_dict() for p in projects],
        }

    def _build_result(self, name, baseline, current, savings,
                      proj_type, methodology) -> CreditResult:
        credits = max(0, savings * self.discount)
        value = credits * self.price
        reduction_pct = (savings / baseline * 100.0) if baseline > 0 else 0.0

        return CreditResult(
            project_name=name,
            baseline_tco2e=round(baseline, 2),
            current_tco2e=round(current, 2),
            savings_tco2e=round(savings, 2),
            credit_tons=round(credits, 2),
            credit_value_usd=round(value, 2),
            price_per_ton_usd=self.price,
            reduction_pct=round(reduction_pct, 2),
            project_type=proj_type,
            methodology=methodology,
        )
