"""
Product Master Engine for CCTS
===============================

Manages paper, board, tissue, and packaging product grades with their
fiber mix, energy intensity, and baseline emission profiles.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@dataclass
class ProductGrade:
    """Represents a single product grade."""
    grade_id: str
    name: str
    category: str
    basis_weight_range: List[int]
    typical_gsm: int
    fiber_mix: Dict[str, float]
    steam_intensity_gj_per_ton: float
    electricity_intensity_kwh_per_ton: float
    water_intensity_m3_per_ton: float
    typical_co2_per_ton: float


class ProductMaster:
    """
    Product catalog for the pulp, paper, board, and packaging industry.

    Loads a built-in catalog of 13+ grades and allows users to add,
    modify, or remove grades at runtime.

    Example:
        >>> from pap_ai_era.ccts import ProductMaster
        >>> pm = ProductMaster()
        >>> pm.list_grades()
        >>> grade = pm.get_grade('kraft_liner')
        >>> print(grade.name, grade.typical_co2_per_ton)
    """

    def __init__(self, catalog_path: Optional[str] = None):
        self._grades: Dict[str, ProductGrade] = {}
        path = catalog_path or os.path.join(_DATA_DIR, 'product_catalog.json')
        self._load_catalog(path)

    def _load_catalog(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for gid, info in data.get('grades', {}).items():
            self._grades[gid] = ProductGrade(
                grade_id=gid,
                name=info['name'],
                category=info['category'],
                basis_weight_range=info['basis_weight_range'],
                typical_gsm=info['typical_gsm'],
                fiber_mix=info['fiber_mix'],
                steam_intensity_gj_per_ton=info['steam_intensity_gj_per_ton'],
                electricity_intensity_kwh_per_ton=info['electricity_intensity_kwh_per_ton'],
                water_intensity_m3_per_ton=info['water_intensity_m3_per_ton'],
                typical_co2_per_ton=info['typical_co2_per_ton'],
            )

    def get_grade(self, grade_id: str) -> ProductGrade:
        """Returns a ProductGrade by ID. Raises KeyError if not found."""
        if grade_id not in self._grades:
            available = ', '.join(self._grades.keys())
            raise KeyError(f"Grade '{grade_id}' not found. Available: {available}")
        return self._grades[grade_id]

    def list_grades(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists all grades, optionally filtered by category."""
        result = []
        for gid, g in self._grades.items():
            if category and g.category != category:
                continue
            result.append({
                'grade_id': gid, 'name': g.name, 'category': g.category,
                'typical_gsm': g.typical_gsm,
                'typical_co2_per_ton': g.typical_co2_per_ton,
            })
        return result

    def add_grade(self, grade_id: str, **kwargs) -> ProductGrade:
        """Add a custom product grade."""
        grade = ProductGrade(grade_id=grade_id, **kwargs)
        self._grades[grade_id] = grade
        return grade

    def update_grade(self, grade_id: str, **kwargs):
        """Update fields of an existing grade."""
        grade = self.get_grade(grade_id)
        for k, v in kwargs.items():
            if hasattr(grade, k):
                setattr(grade, k, v)

    def remove_grade(self, grade_id: str):
        """Remove a grade from the catalog."""
        if grade_id in self._grades:
            del self._grades[grade_id]

    def get_categories(self) -> List[str]:
        """Returns unique categories."""
        return list(set(g.category for g in self._grades.values()))

    @property
    def grades(self) -> Dict[str, ProductGrade]:
        return self._grades
