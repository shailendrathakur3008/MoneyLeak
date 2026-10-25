# -*- coding: utf-8 -*-
import sys
root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.services.catalogue.low_risk import LOW_RISK_SCHEMES
from app.services.catalogue.medium_risk import MEDIUM_RISK_SCHEMES
from app.services.catalogue.high_risk import HIGH_RISK_SCHEMES
from app.services.catalogue.stocks import STOCKS_CATALOGUE
from app.services.catalogue.mutual_funds import MUTUAL_FUNDS_CATALOGUE
from app.services.catalogue.gold import GOLD_CATALOGUE
from app.services.catalogue.schema import validate_catalogue_item

# Order matters: base new catalogues first, then curated risk tiers preserve their specific calibrated riskLevel & descriptions
master = {}
for s in STOCKS_CATALOGUE:
    master[s['id']] = s
for s in MUTUAL_FUNDS_CATALOGUE:
    master[s['id']] = s
for s in GOLD_CATALOGUE:
    master[s['id']] = s
for s in LOW_RISK_SCHEMES:
    master[s['id']] = s
for s in MEDIUM_RISK_SCHEMES:
    master[s['id']] = s
for s in HIGH_RISK_SCHEMES:
    master[s['id']] = s

items = list(master.values())
print(f"Total merged catalogue items: {len(items)}")

errors = []
for s in items:
    err = validate_catalogue_item(s)
    if err:
        errors.append((s['id'], err))

print(f"Validation errors count: {len(errors)}")
if errors:
    for item_id, err in errors[:10]:
        print(f"  {item_id}: {err}")

# Check breakdown by assetType
by_asset = {}
by_risk = {}
for s in items:
    by_asset[s['assetType']] = by_asset.get(s['assetType'], 0) + 1
    by_risk[s['riskLevel']] = by_risk.get(s['riskLevel'], 0) + 1

print("\nBreakdown by Asset Type:")
for k, v in sorted(by_asset.items()):
    print(f"  {k}: {v}")

print("\nBreakdown by Risk Level:")
for k, v in sorted(by_risk.items()):
    print(f"  {k}: {v}")
