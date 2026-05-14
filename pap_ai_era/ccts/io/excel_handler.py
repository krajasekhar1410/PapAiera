"""
Excel I/O Handler for CCTS
============================

Handles Excel and CSV upload/download for production data,
emission factors, and calculation results.
"""

import os
from typing import Optional, Dict, Any, List

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class ExcelHandler:
    """
    Handles Excel/CSV I/O for CCTS data.

    Supports:
    - Upload production data from Excel
    - Upload custom emission factors
    - Download results to Excel
    - Generate data collection templates

    Example:
        >>> from pap_ai_era.ccts.io import ExcelHandler
        >>> eh = ExcelHandler()
        >>> production_data = eh.read_production_data('mill_data.xlsx')
        >>> eh.export_results(results, 'carbon_report.xlsx')
    """

    def read_production_data(self, filepath: str) -> pd.DataFrame:
        """
        Read production data from Excel or CSV.

        Expected columns: product, production_tons, electricity_mwh,
        steam_gj, [fuel columns...], [chemical columns...]
        """
        if not HAS_PANDAS:
            raise ImportError("pandas is required for Excel operations. pip install pandas")

        ext = os.path.splitext(filepath)[1].lower()
        if ext in ('.xlsx', '.xls'):
            df = pd.read_excel(filepath, sheet_name=0)
        elif ext == '.csv':
            df = pd.read_csv(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        # Normalise column names
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        return df

    def read_factors(self, filepath: str) -> Dict[str, Dict[str, float]]:
        """
        Read custom emission factors from Excel.

        Expected sheets: fuel_factors, electricity_factors, etc.
        Each sheet should have columns: name, value
        """
        if not HAS_PANDAS:
            raise ImportError("pandas is required. pip install pandas")

        factors = {}
        xl = pd.ExcelFile(filepath)

        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
            if 'name' in df.columns and 'value' in df.columns:
                factors[sheet] = dict(zip(df['name'], df['value']))

        return factors

    def export_results(self, results: List[Dict[str, Any]], filepath: str,
                       sheet_name: str = 'Carbon Results'):
        """Export calculation results to Excel."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required. pip install pandas")

        df = pd.DataFrame(results)
        df.to_excel(filepath, sheet_name=sheet_name, index=False)

    def export_factors(self, factors_dict: Dict[str, Any], filepath: str):
        """Export all emission factors to Excel (one sheet per category)."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required. pip install pandas")

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for category, fdict in factors_dict.items():
                if isinstance(fdict, dict):
                    df = pd.DataFrame([
                        {'name': k, 'value': v}
                        for k, v in fdict.items()
                    ])
                    df.to_excel(writer, sheet_name=category[:31], index=False)

    def generate_template(self, filepath: str, template_type: str = 'production'):
        """
        Generate a blank Excel template for data collection.

        template_type: 'production', 'factors', or 'full'
        """
        if not HAS_PANDAS:
            raise ImportError("pandas is required. pip install pandas")

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if template_type in ('production', 'full'):
                prod_df = pd.DataFrame(columns=[
                    'product', 'production_tons', 'electricity_mwh',
                    'electricity_region', 'steam_purchased_gj', 'steam_source',
                    'coal_bituminous_gj', 'natural_gas_gj', 'fuel_oil_heavy_gj',
                    'biomass_wood_gj', 'biomass_black_liquor_gj',
                    'naoh_tons', 'clo2_tons', 'starch_tons',
                    'transport_road_km', 'transport_tons'
                ])
                prod_df.to_excel(writer, sheet_name='Production Data', index=False)

            if template_type in ('factors', 'full'):
                fuel_df = pd.DataFrame(columns=['name', 'value'])
                fuel_df.to_excel(writer, sheet_name='fuel_factors', index=False)
                elec_df = pd.DataFrame(columns=['name', 'value'])
                elec_df.to_excel(writer, sheet_name='electricity_factors', index=False)

    def read_csv_data(self, filepath: str) -> pd.DataFrame:
        """Read CSV production data."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required. pip install pandas")
        df = pd.read_csv(filepath)
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        return df
