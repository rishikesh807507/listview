import logging
import json
import csv
import io
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.data_providers.base_provider import BaseProvider

logger = logging.getLogger("FinancialProvider")

class FinancialProvider(BaseProvider):
    """
    Company fundamentals and financial statements provider.
    Zero paid API requirement.
    Supports manual CSV/JSON import for easy user-driven updates without third-party fees.
    """
    def __init__(self):
        super().__init__("Public Filings & Local Fundamental Storage")

    def health_check(self) -> bool:
        return True

    def parse_csv_financials(self, file_content: str) -> List[Dict[str, Any]]:
        """Parse user-uploaded CSV file for financial data."""
        reader = csv.DictReader(io.StringIO(file_content))
        rows = []
        for r in reader:
            rows.append(r)
        return rows

    def parse_json_financials(self, file_content: str) -> List[Dict[str, Any]]:
        """Parse user-uploaded JSON file for financial data."""
        data = json.loads(file_content)
        if isinstance(data, list):
            return data
        return [data]
