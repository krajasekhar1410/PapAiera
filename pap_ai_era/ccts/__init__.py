"""
PapAiEra CCTS — Carbon Credit & Trading System
=================================================

A complete carbon calculation, credit estimation, and sustainability
analytics module for the pulp, paper, board, and packaging industry.

Quick Start (Library):
    >>> from pap_ai_era.ccts import CarbonCalculator, FactorEngine, CreditEstimator
    >>> calc = CarbonCalculator()
    >>> result = calc.calculate(product='kraft_liner', production_tons=1000, ...)
    >>> print(result.summary())

Quick Start (No-Code UI):
    $ python -m pap_ai_era.ccts.ui.app
"""

from .products import ProductMaster, ProductGrade
from .factors import FactorEngine
from .carbon import CarbonCalculator, CarbonResult
from .credits import CreditEstimator, CreditResult
from .formulas import FormulaEngine
from .io import ExcelHandler, DatabaseHandler

__all__ = [
    'ProductMaster', 'ProductGrade',
    'FactorEngine',
    'CarbonCalculator', 'CarbonResult',
    'CreditEstimator', 'CreditResult',
    'FormulaEngine',
    'ExcelHandler', 'DatabaseHandler',
]
