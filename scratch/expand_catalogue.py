"""
Builder script to generate expanded Indian Investment Catalogue modules:
- app/services/catalogue/stocks.py (90+ stocks across 9 sectors)
- app/services/catalogue/mutual_funds.py (45+ mutual funds across 11 categories)
- app/services/catalogue/gold.py (12+ gold products across 4 vehicles)
- updates to app/services/catalogue/__init__.py and app/services/market_data_service.py
"""
import os
import sys

# Ensure MoneyLeak root in sys.path
root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.services.catalogue.schema import validate_catalogue_item

print("Schema validator loaded successfully.")
