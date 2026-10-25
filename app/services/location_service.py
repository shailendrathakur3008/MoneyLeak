"""
Comprehensive Indian Location Dataset and Regional Budget Recommendation Service.

Includes:
- All 28 States and 8 Union Territories (ISO-3166-2:IN standard)
- Administrative districts across all 36 states and UTs (788 official districts)
- Major cities, municipal corporations, towns, and district headquarters (4,250+ places) with Tier classifications:
    * METRO: Major Metropolitan Area (Tier-X / population > 5 million / MMR, NCR, etc.)
    * URBAN: Other Urban Area (Tier-Y / Tier-2 growth hubs)
    * TOWN: Smaller City or Town (Tier-Z / district headquarters)
    * RURAL: Rural or Semi-Urban locality
    * UNCLASSIFIED: Other / Not Listed or unverified locality
- Alternate spellings and transliterations (e.g. Bangalore -> Bengaluru, Bombay -> Mumbai, Gurgaon -> Gurugram)
- 6-digit Indian PIN code validation and postal circle matching
- India-Adaptive 50/30/20 budget presets & actual expense refinement
"""

import re
from typing import Dict, Any, List, Optional, Tuple

# -----------------------------------------------------------------------------
# 1. COMPREHENSIVE OFFICIAL DATASET IMPORT
# -----------------------------------------------------------------------------
from app.services.india_geo_data import (
    DATASET_METADATA,
    INDIAN_STATES_AND_UTS,
    STATE_BY_ID,
    DISTRICTS_BY_STATE,
    DISTRICT_BY_ID,
    CITIES_DATA,
    CITIES_BY_DISTRICT
)

CITY_BY_ID = {c["id"]: c for c in CITIES_DATA}


# -----------------------------------------------------------------------------
# 2. LOCATION CLASSIFICATION METADATA & PRESET LABELS
# -----------------------------------------------------------------------------
CLASSIFICATION_LABELS = {
    "METRO": {
        "title": "Major Metropolitan Area",
        "description": "High essential cost benchmark (Tier-X Urban Agglomeration, population > 5M). Typical rental and transit commitments require tailored budgeting.",
        "badge": "Metro Tier-1"
    },
    "URBAN": {
        "title": "Other Urban Area",
        "description": "Fast-growing commercial and economic hub (Tier-Y Urban Agglomeration). Balanced essential and lifestyle cost structures.",
        "badge": "Urban Tier-2"
    },
    "TOWN": {
        "title": "Smaller City or Town",
        "description": "Regional district headquarters or commercial market center (Tier-Z). Moderate rental and everyday living costs.",
        "badge": "Town Tier-3"
    },
    "RURAL": {
        "title": "Rural or Semi-Urban",
        "description": "Semi-urban or rural locality with lower essential baseline overheads.",
        "badge": "Rural / Semi-Urban"
    },
    "UNCLASSIFIED": {
        "title": "Standard / Unclassified",
        "description": "Custom or international locality. Calibrated using standard 50/30/20 baseline guidelines.",
        "badge": "General Baseline"
    }
}

BUDGET_PRESETS = {
    "standard": {
        "id": "standard",
        "title": "Standard 50/30/20 Preset",
        "subtitle": "Classic balanced wealth allocation",
        "needs": 50.0,
        "wants": 30.0,
        "savings": 20.0,
        "recommended_for": ["URBAN", "UNCLASSIFIED"]
    },
    "metro": {
        "id": "metro",
        "title": "Metropolitan Starting Preset",
        "subtitle": "Disciplined lifestyle spending with aggressive 25% savings",
        "needs": 50.0,
        "wants": 25.0,
        "savings": 25.0,
        "recommended_for": ["METRO"]
    },
    "high_essential": {
        "id": "high_essential",
        "title": "High Essential-Cost Preset",
        "subtitle": "Realistic accommodation for high rent, family support, or loan EMIs",
        "needs": 60.0,
        "wants": 20.0,
        "savings": 20.0,
        "recommended_for": ["METRO", "URBAN"]
    },
    "lower_cost": {
        "id": "lower_cost",
        "title": "Lower-Cost Starting Preset",
        "subtitle": "Leverage low living expenses to maximize wealth building",
        "needs": 45.0,
        "wants": 30.0,
        "savings": 25.0,
        "recommended_for": ["TOWN", "RURAL"]
    }
}


# -----------------------------------------------------------------------------
# 3. CORE QUERY APIS
# -----------------------------------------------------------------------------

def get_dataset_metadata() -> Dict[str, Any]:
    """Returns official geographical dataset metadata and urban coverage details."""
    return DATASET_METADATA.copy()


def get_supported_countries() -> List[Dict[str, str]]:
    """Returns supported onboarding countries with India prioritized."""
    return [
        {"code": "IN", "name": "India", "currency": "INR", "is_primary": True},
        {"code": "US", "name": "United States", "currency": "USD", "is_primary": False},
        {"code": "GB", "name": "United Kingdom", "currency": "GBP", "is_primary": False},
        {"code": "AE", "name": "United Arab Emirates", "currency": "AED", "is_primary": False},
        {"code": "SG", "name": "Singapore", "currency": "SGD", "is_primary": False},
        {"code": "CA", "name": "Canada", "currency": "CAD", "is_primary": False},
        {"code": "OTHER", "name": "Other Country", "currency": "USD", "is_primary": False}
    ]


def get_all_states(query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns list of all 28 States and 8 Union Territories.
    Supports case-insensitive partial search.
    """
    states = INDIAN_STATES_AND_UTS
    if query:
        clean_q = query.strip().lower()
        states = [s for s in states if clean_q in s["name"].lower() or clean_q in s["code"].lower()]
    return sorted(states, key=lambda s: (0 if s["type"] == "State" else 1, s["name"]))


def get_districts_for_state(state_id: str, query: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Returns authoritative administrative districts for the given state ID.
    Supports case-insensitive search by name or code.
    """
    districts = DISTRICTS_BY_STATE.get(state_id, [])
    if query:
        clean_q = query.strip().lower()
        districts = [d for d in districts if clean_q in d["name"].lower() or clean_q in d.get("code", "").lower()]
    
    # Always guarantee an 'Other District' option if custom
    has_other = any(d["name"].startswith("Other") for d in districts)
    if not has_other and not query:
        districts = districts + [{"id": f"{state_id}-OTH", "name": "Other District", "state_id": state_id, "code": "OTH"}]
    return sorted(districts, key=lambda d: (d["name"].startswith("Other"), d["name"]))


def search_cities_for_state(
    state_id: str,
    district_id: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Searches recognized cities and statutory/census towns within a state and optional district.
    Strictly excludes villages.
    Handles transliterations, aliases (e.g. Bombay -> Mumbai, Gurgaon -> Gurugram),
    and displays parent district/state clearly for disambiguation: 'City/Town Name — District, State'.
    """
    clean_q = (query or "").strip().lower()

    # 1. If district_id is provided, use district-specific index for speed
    if district_id and district_id != f"{state_id}-OTH" and district_id in CITIES_BY_DISTRICT:
        pool = CITIES_BY_DISTRICT[district_id]
    else:
        # State-level pool
        pool = [c for c in CITIES_DATA if c["state_id"] == state_id]

    matched = []
    state_obj = STATE_BY_ID.get(state_id, {})
    state_name = state_obj.get("name", state_id)

    for c in pool:
        # STRICT REQUIREMENT: Exclude villages from city/town directory
        if c.get("is_village", False):
            continue

        if clean_q:
            name_match = clean_q in c["name"].lower()
            alias_match = any(clean_q in a.lower() for a in c.get("aliases", []))
            if not (name_match or alias_match):
                continue

        # Look up district name for disambiguation
        dist_obj = DISTRICT_BY_ID.get(c["district_id"], {})
        dist_name = dist_obj.get("name", "District")

        tier = c.get("tier", "TOWN")
        tier_meta = CLASSIFICATION_LABELS.get(tier, CLASSIFICATION_LABELS["UNCLASSIFIED"])
        settlement_type = c.get("settlement_type", "Statutory Town (Municipality)")

        matched.append({
            "id": c["id"],
            "name": c["name"],
            "district_id": c["district_id"],
            "district_name": dist_name,
            "state_id": state_id,
            "state_name": state_name,
            "settlement_type": settlement_type,
            "settlement_category": c.get("settlement_category", "STATUTORY_TOWN"),
            "official_code": c.get("official_code", ""),
            "is_village": False,
            "tier": tier,
            "tier_label": tier_meta.get("title", tier),
            "badge": settlement_type,
            "location_type": c.get("location_type", "Town"),
            "display_label": f"{c['name']} — {dist_name}, {state_name}",
            "data_source": c.get("data_source", DATASET_METADATA.get("data_source")),
            "dataset_version": c.get("dataset_version", DATASET_METADATA.get("dataset_version"))
        })

    # Sort matched cities: Metros first, then Urban, then Town, then Alphabetical
    tier_order = {"METRO": 1, "URBAN": 2, "TOWN": 3, "RURAL": 4, "UNCLASSIFIED": 5}
    matched.sort(key=lambda x: (tier_order.get(x["tier"], 99), x["name"]))

    return matched[:limit]


def validate_location_combination(
    state_id: Optional[str],
    district_id: Optional[str] = None,
    city_id: Optional[str] = None,
    is_custom_city: bool = False,
    city_name: Optional[str] = None,
    country: str = "India"
) -> Dict[str, Any]:
    """
    Validates hierarchical geographical dependency:
    Country -> State/UT -> District -> City/Town
    Rejects invalid cross-state or cross-district combinations and village classifications.
    Handles manual location requests transparently without fabricating false verified matches.
    """
    if country != "India":
        return {
            "valid": True,
            "is_indian": False,
            "country": country,
            "location_tier": "UNCLASSIFIED",
            "tier": "UNCLASSIFIED"
        }

    if not state_id:
        return {"valid": False, "error": "State or Union Territory selection is required."}

    state_obj = STATE_BY_ID.get(state_id)
    if not state_obj:
        return {"valid": False, "error": f"Invalid State or Union Territory identifier: '{state_id}'."}

    # Verify district belongs to state if provided
    district_obj = None
    if district_id:
        valid_districts = DISTRICTS_BY_STATE.get(state_id, [])
        valid_dist_ids = {d["id"] for d in valid_districts} | {f"{state_id}-OTH"}
        if district_id not in valid_dist_ids:
            return {
                "valid": False,
                "error": f"Selected district '{district_id}' does not belong to {state_obj['name']}."
            }
        district_obj = DISTRICT_BY_ID.get(district_id)

    # Verify city/town
    resolved_tier = "UNCLASSIFIED"
    resolved_city_name = city_name
    settlement_type = None
    settlement_category = None
    official_code = None

    if city_id and city_id not in ("OTHER", "CUSTOM_REQUEST") and not is_custom_city:
        city_obj = CITY_BY_ID.get(city_id)
        if city_obj:
            if city_obj.get("is_village", False):
                return {
                    "valid": False,
                    "error": "Villages are excluded from the recognized cities and towns directory."
                }
            if city_obj["state_id"] != state_id:
                return {
                    "valid": False,
                    "error": f"Selected city '{city_obj['name']}' does not belong to {state_obj['name']}."
                }
            if district_id and district_id != f"{state_id}-OTH" and city_obj["district_id"] != district_id:
                return {
                    "valid": False,
                    "error": f"Selected city '{city_obj['name']}' belongs to a different district."
                }
            resolved_tier = city_obj.get("tier", "TOWN")
            resolved_city_name = city_obj["name"]
            settlement_type = city_obj.get("settlement_type")
            settlement_category = city_obj.get("settlement_category")
            official_code = city_obj.get("official_code")
        else:
            # City ID not in official directory; treat as manual location request fallback
            is_custom_city = True
            resolved_tier = "UNCLASSIFIED"
            settlement_type = "Unverified Manual Request"
    elif is_custom_city or city_id in ("OTHER", "CUSTOM_REQUEST"):
        is_custom_city = True
        resolved_tier = "UNCLASSIFIED"
        settlement_type = "Unverified Manual Request"

    return {
        "valid": True,
        "is_indian": True,
        "state_id": state_id,
        "state_name": state_obj["name"],
        "state_type": state_obj["type"],
        "district_id": district_id,
        "district_name": district_obj["name"] if district_obj else None,
        "city_id": "CUSTOM_REQUEST" if is_custom_city else city_id,
        "city_name": resolved_city_name,
        "is_custom_city": is_custom_city,
        "settlement_type": settlement_type,
        "settlement_category": settlement_category,
        "official_code": official_code,
        "is_village": False,
        "location_tier": resolved_tier
    }


# -----------------------------------------------------------------------------
# 4. PIN CODE VERIFICATION LOGIC
# -----------------------------------------------------------------------------

def validate_indian_pincode(pincode: str, state_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates a 6-digit Indian PIN code and checks if it matches the selected state.
    Indian PIN code format: 6 digits, first digit 1-9 (cannot begin with 0).
    """
    clean_pin = (pincode or "").strip()

    if not clean_pin:
        return {"valid": False, "error": "PIN code cannot be empty.", "matches_state": True}

    if not re.match(r"^[1-9][0-9]{5}$", clean_pin):
        return {
            "valid": False,
            "error": "Indian PIN codes must be exactly 6 digits and cannot start with 0.",
            "matches_state": False
        }

    # If state_id provided, check postal circle
    if state_id and state_id in STATE_BY_ID:
        state_obj = STATE_BY_ID[state_id]
        prefixes = state_obj.get("postal_prefix", [])

        is_matching = any(clean_pin.startswith(p) for p in prefixes)
        if not is_matching:
            return {
                "valid": True,
                "clean_pincode": clean_pin,
                "matches_state": False,
                "warning": (
                    f"PIN code '{clean_pin}' usually belongs to a postal circle outside {state_obj['name']}. "
                    "Please double check if this is your intended PIN code."
                )
            }

    return {
        "valid": True,
        "clean_pincode": clean_pin,
        "matches_state": True,
        "message": "PIN code format verified."
    }


# -----------------------------------------------------------------------------
# 5. INDIA-ADAPTIVE 50/30/20 BUDGET RECOMMENDATION ENGINE
# -----------------------------------------------------------------------------

def calculate_adaptive_budget_recommendation(
    location_tier: str,
    monthly_income_minor: int,
    rent_minor: int = 0,
    essentials_minor: int = 0,
    debt_minor: int = 0,
    dependants_count: int = 0,
    currency: str = "INR"
) -> Dict[str, Any]:
    """
    Generates intelligent, transparent 50/30/20 recommendations based on location
    and user's actual contractual household commitments.
    Never forces an unrealistic allocation if essentials exceed 50%.
    """
    tier = location_tier or "UNCLASSIFIED"
    tier_info = CLASSIFICATION_LABELS.get(tier, CLASSIFICATION_LABELS["UNCLASSIFIED"])

    # Baseline total essential outflow
    total_essential_minor = (rent_minor or 0) + (essentials_minor or 0) + (debt_minor or 0)

    # If income is known and greater than zero, compute actual essential percentage
    if monthly_income_minor > 0:
        actual_needs_pct = round((total_essential_minor / monthly_income_minor) * 100, 1)
    else:
        actual_needs_pct = 0.0

    # Determine recommended preset
    recommended_preset_key = "standard"
    explanation = ""

    # CASE A: High contractual essential overhead (Essentials exceed 50%)
    if actual_needs_pct > 50.0:
        recommended_preset_key = "high_essential"
        calibrated_needs = min(max(round(actual_needs_pct / 5) * 5, 55.0), 75.0)
        remaining_pct = 100.0 - calibrated_needs
        calibrated_wants = round(remaining_pct * 0.45, 1)
        calibrated_savings = round(remaining_pct - calibrated_wants, 1)

        explanation = (
            f"Based on your recorded essential commitments (Rent/EMI, groceries, transit, debt), "
            f"your baseline essentials total {actual_needs_pct}% of take-home income. "
            f"Rather than enforcing an unrealistic 50% cap, we recommend our High Essential-Cost preset "
            f"({int(calibrated_needs)}% Needs, {int(calibrated_wants)}% Wants, {int(calibrated_savings)}% Savings) "
            f"to protect essential bills while preserving a consistent wealth-building habit."
        )
        recommended_preset = {
            "id": "high_essential",
            "title": "High Essential-Cost Preset",
            "needs": calibrated_needs,
            "wants": calibrated_wants,
            "savings": calibrated_savings,
            "is_calibrated": True
        }

    # CASE B: Low essential costs (Essentials <= 45% and not major metro, or Tier-Z / Rural)
    elif actual_needs_pct > 0 and actual_needs_pct <= 45.0 and tier in ("TOWN", "RURAL", "UNCLASSIFIED"):
        recommended_preset_key = "lower_cost"
        recommended_preset = BUDGET_PRESETS["lower_cost"].copy()
        explanation = (
            f"Your recorded essential commitments represent {actual_needs_pct}% of income. "
            "Living in a lower-cost regional hub creates significant headroom. "
            "We suggest our Lower-Cost Preset (45% Needs, 30% Wants, 25% Savings) to accelerate investments."
        )

    # CASE C: Major Metropolitan Area with standard or disciplined expenses
    elif tier == "METRO":
        recommended_preset_key = "metro"
        recommended_preset = BUDGET_PRESETS["metro"].copy()
        explanation = (
            "In major metropolitan areas (Mumbai, Delhi NCR, Bengaluru, Hyderabad, Chennai, etc.), "
            "lifestyle and discretionary leakages (frequent dining out, delivery apps, shopping) often dilute wealth. "
            "We recommend the Metropolitan Starting Preset (50% Needs, 25% Wants, 25% Savings) to maintain disciplined lifestyle spending."
        )

    # CASE D: Default standard 50/30/20
    else:
        recommended_preset_key = "standard"
        recommended_preset = BUDGET_PRESETS["standard"].copy()
        explanation = (
            "The classic 50/30/20 framework divides your income into 50% essential Needs, "
            "30% discretionary lifestyle Wants, and 20% automated Savings & Debt reduction."
        )

    return {
        "location_tier": tier,
        "tier_title": tier_info["title"],
        "tier_badge": tier_info["badge"],
        "tier_description": tier_info["description"],
        "monthly_income_minor_units": monthly_income_minor,
        "total_essential_minor_units": total_essential_minor,
        "actual_needs_pct": actual_needs_pct,
        "recommended_preset_key": recommended_preset_key,
        "recommended_preset": recommended_preset,
        "explanation": explanation,
        "available_presets": [
            BUDGET_PRESETS["standard"],
            BUDGET_PRESETS["metro"],
            BUDGET_PRESETS["high_essential"],
            BUDGET_PRESETS["lower_cost"]
        ]
    }
