"""
Emission Factor Engine for CCTS
================================

Manages all emission factors (fuel, electricity, steam, process, fiber, GWP).
All factors are editable at runtime. Users can override defaults, save custom
factor sets, and load from JSON or Excel.
"""

import json
import os
import copy
from typing import Optional, Dict, Any, List


_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class FactorEngine:
    """
    Central emission factor manager.

    Loads IPCC/IEA/CEA default factors and allows full runtime editing.
    Every factor can be changed via set methods or bulk-loaded from files.

    Example:
        >>> from pap_ai_era.ccts import FactorEngine
        >>> fe = FactorEngine()
        >>> fe.get_fuel_factor('coal_bituminous')
        94.6
        >>> fe.set_fuel_factor('coal_bituminous', 95.0)
        >>> fe.get_electricity_factor('india_national')
        720
    """

    def __init__(self, factors_path: Optional[str] = None):
        path = factors_path or os.path.join(_DATA_DIR, 'default_factors.json')
        with open(path, 'r', encoding='utf-8') as f:
            self._raw = json.load(f)
        self._fuel = dict(self._raw.get('fuel_factors', {}))
        self._electricity = dict(self._raw.get('electricity_factors', {}))
        self._steam = dict(self._raw.get('steam_factors', {}))
        self._process = dict(self._raw.get('process_factors', {}))
        self._fiber = dict(self._raw.get('fiber_factors', {}))
        self._gwp = dict(self._raw.get('gwp_factors', {}))
        # Remove description keys
        for d in [self._fuel, self._electricity, self._steam,
                  self._process, self._fiber]:
            d.pop('_description', None)
            d.pop('_unit', None)

    # --- Fuel Factors ---
    def get_fuel_factor(self, fuel_type: str) -> float:
        """Get fuel emission factor in kg CO2/GJ."""
        if fuel_type not in self._fuel:
            raise KeyError(f"Fuel '{fuel_type}' not found. Available: {list(self._fuel.keys())}")
        return self._fuel[fuel_type]

    def set_fuel_factor(self, fuel_type: str, value: float):
        """Set or override a fuel emission factor."""
        self._fuel[fuel_type] = value

    def list_fuel_factors(self) -> Dict[str, float]:
        return dict(self._fuel)

    # --- Electricity Factors ---
    def get_electricity_factor(self, region: str) -> float:
        """Get grid emission factor in kg CO2/MWh."""
        if region not in self._electricity:
            raise KeyError(f"Region '{region}' not found. Available: {list(self._electricity.keys())}")
        return self._electricity[region]

    def set_electricity_factor(self, region: str, value: float):
        """Set or override a grid emission factor."""
        self._electricity[region] = value

    def list_electricity_factors(self) -> Dict[str, float]:
        return dict(self._electricity)

    # --- Steam Factors ---
    def get_steam_factor(self, source: str) -> float:
        """Get steam emission factor in kg CO2/GJ."""
        if source not in self._steam:
            raise KeyError(f"Steam source '{source}' not found.")
        return self._steam[source]

    def set_steam_factor(self, source: str, value: float):
        self._steam[source] = value

    def list_steam_factors(self) -> Dict[str, float]:
        return dict(self._steam)

    # --- Process Factors ---
    def get_process_factor(self, process: str) -> float:
        """Get process emission factor in kg CO2/ton."""
        if process not in self._process:
            raise KeyError(f"Process '{process}' not found.")
        return self._process[process]

    def set_process_factor(self, process: str, value: float):
        self._process[process] = value

    def list_process_factors(self) -> Dict[str, float]:
        return dict(self._process)

    # --- Fiber Factors ---
    def get_fiber_factor(self, fiber_type: str) -> float:
        """Get fiber emission factor in kg CO2/ADT."""
        if fiber_type not in self._fiber:
            raise KeyError(f"Fiber '{fiber_type}' not found.")
        return self._fiber[fiber_type]

    def set_fiber_factor(self, fiber_type: str, value: float):
        self._fiber[fiber_type] = value

    def list_fiber_factors(self) -> Dict[str, float]:
        return dict(self._fiber)

    # --- GWP ---
    def get_gwp(self, gas: str = 'co2') -> int:
        return self._gwp.get(gas, 1)

    # --- Bulk Operations ---
    def export_all(self) -> Dict[str, Any]:
        """Export all factors as a dictionary."""
        return {
            'fuel_factors': self.list_fuel_factors(),
            'electricity_factors': self.list_electricity_factors(),
            'steam_factors': self.list_steam_factors(),
            'process_factors': self.list_process_factors(),
            'fiber_factors': self.list_fiber_factors(),
            'gwp_factors': dict(self._gwp),
        }

    def save_to_json(self, path: str):
        """Save current factors to a JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.export_all(), f, indent=2)

    def load_from_dict(self, data: Dict[str, Any]):
        """Bulk-load factors from a dictionary (e.g., from Excel parsing)."""
        if 'fuel_factors' in data:
            self._fuel.update(data['fuel_factors'])
        if 'electricity_factors' in data:
            self._electricity.update(data['electricity_factors'])
        if 'steam_factors' in data:
            self._steam.update(data['steam_factors'])
        if 'process_factors' in data:
            self._process.update(data['process_factors'])
        if 'fiber_factors' in data:
            self._fiber.update(data['fiber_factors'])

    def reset_to_defaults(self):
        """Reload all factors from built-in defaults."""
        self.__init__()
