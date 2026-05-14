"""
Database Handler for CCTS
==========================

SQLite persistence layer for factors, products, results, and audit trails.
Zero configuration — creates database automatically on first use.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List


class DatabaseHandler:
    """
    SQLite database handler for CCTS.

    Provides persistence for:
    - Custom emission factors
    - Calculation results history
    - Audit trail
    - User configurations

    Example:
        >>> from pap_ai_era.ccts.io import DatabaseHandler
        >>> db = DatabaseHandler('my_mill.db')
        >>> db.save_result(carbon_result.to_dict())
        >>> history = db.get_results_history(limit=50)
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(os.path.expanduser('~'), '.papaiera_ccts.db')
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS carbon_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                product_grade TEXT,
                production_tons REAL,
                scope1_total REAL,
                scope2_total REAL,
                scope3_total REAL,
                total_tco2e REAL,
                co2e_per_ton REAL,
                details_json TEXT
            );

            CREATE TABLE IF NOT EXISTS credit_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project_name TEXT,
                baseline_tco2e REAL,
                current_tco2e REAL,
                savings_tco2e REAL,
                credit_tons REAL,
                credit_value_usd REAL,
                details_json TEXT
            );

            CREATE TABLE IF NOT EXISTS custom_factors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                factor_name TEXT NOT NULL,
                factor_value REAL NOT NULL,
                source TEXT,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                entity TEXT,
                details TEXT
            );
        """)
        self.conn.commit()

    # --- Carbon Results ---
    def save_result(self, result: Dict[str, Any]):
        """Save a carbon calculation result."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO carbon_results
            (timestamp, product_grade, production_tons, scope1_total,
             scope2_total, scope3_total, total_tco2e, co2e_per_ton, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            result.get('product_grade', ''),
            result.get('production_tons', 0),
            result.get('scope1_total', 0),
            result.get('scope2_total', 0),
            result.get('scope3_total', 0),
            result.get('total_tco2e', 0),
            result.get('co2e_per_ton', 0),
            json.dumps(result),
        ))
        self.conn.commit()
        self._log('save_result', 'carbon_results', result.get('product_grade', ''))

    def get_results_history(self, limit: int = 100,
                            product: Optional[str] = None) -> List[Dict]:
        """Retrieve historical calculation results."""
        cursor = self.conn.cursor()
        if product:
            cursor.execute(
                "SELECT * FROM carbon_results WHERE product_grade=? ORDER BY timestamp DESC LIMIT ?",
                (product, limit))
        else:
            cursor.execute(
                "SELECT * FROM carbon_results ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # --- Credit Results ---
    def save_credit(self, result: Dict[str, Any]):
        """Save a carbon credit estimate."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO credit_results
            (timestamp, project_name, baseline_tco2e, current_tco2e,
             savings_tco2e, credit_tons, credit_value_usd, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            result.get('project_name', ''),
            result.get('baseline_tco2e', 0),
            result.get('current_tco2e', 0),
            result.get('savings_tco2e', 0),
            result.get('credit_tons', 0),
            result.get('credit_value_usd', 0),
            json.dumps(result),
        ))
        self.conn.commit()

    # --- Custom Factors ---
    def save_factor(self, category: str, name: str, value: float,
                    source: str = '', notes: str = ''):
        """Save a custom emission factor."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO custom_factors (timestamp, category, factor_name, factor_value, source, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), category, name, value, source, notes))
        self.conn.commit()
        self._log('save_factor', 'custom_factors', f'{category}/{name}={value}')

    def get_custom_factors(self, category: Optional[str] = None) -> List[Dict]:
        """Retrieve custom factors."""
        cursor = self.conn.cursor()
        if category:
            cursor.execute(
                "SELECT * FROM custom_factors WHERE category=? ORDER BY timestamp DESC",
                (category,))
        else:
            cursor.execute("SELECT * FROM custom_factors ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]

    # --- Audit Log ---
    def _log(self, action: str, entity: str, details: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO audit_log (timestamp, action, entity, details) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), action, entity, details))
        self.conn.commit()

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()
