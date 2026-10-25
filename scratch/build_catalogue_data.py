# coding: utf-8
"""
Constructs:
1. app/services/catalogue/stocks.py
2. app/services/catalogue/mutual_funds.py
3. app/services/catalogue/gold.py
4. updates app/services/catalogue/__init__.py
5. updates app/services/market_data_service.py with verified instrument mappings
"""
import sys
import os

root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.services.catalogue.schema import validate_catalogue_item

print("Writing generator logic...")
