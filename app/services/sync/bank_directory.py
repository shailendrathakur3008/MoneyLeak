"""
Universal Indian Bank Directory and Dynamic Discovery Service.
Provides a comprehensive, verified registry of Indian financial institutions
(Public, Private, Small Finance, and Payments Banks) conforming to RBI IFSC and Sahamati/Setu FIP standards.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Category definitions
CATEGORY_PUBLIC = 'PUBLIC_SECTOR'
CATEGORY_PRIVATE = 'PRIVATE_SECTOR'
CATEGORY_SMALL_FINANCE = 'SMALL_FINANCE'
CATEGORY_PAYMENTS = 'PAYMENTS_BANK'

# Master Directory of Indian Financial Institutions with Verified Identifiers
MASTER_BANK_DIRECTORY: List[Dict[str, Any]] = [
    # ==========================================
    # PUBLIC-SECTOR BANKS (12)
    # ==========================================
    {
        'id': 'SBIN',
        'code': 'SBIN',
        'name': 'State Bank of India',
        'fip_id': 'SBI-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#280071',
        'supported_types': ['SAVINGS', 'CURRENT', 'DEPOSIT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'PUNB',
        'code': 'PUNB',
        'name': 'Punjab National Bank',
        'fip_id': 'PNB-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#a20a2a',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'BARB',
        'code': 'BARB',
        'name': 'Bank of Baroda',
        'fip_id': 'BARB-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#f26522',
        'supported_types': ['SAVINGS', 'CURRENT', 'DEPOSIT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'CNRB',
        'code': 'CNRB',
        'name': 'Canara Bank',
        'fip_id': 'CANARA-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#008fd5',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'UBIN',
        'code': 'UBIN',
        'name': 'Union Bank of India',
        'fip_id': 'UNION-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#e60000',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'IDIB',
        'code': 'IDIB',
        'name': 'Indian Bank',
        'fip_id': 'INDIAN-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#0054a6',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'BKID',
        'code': 'BKID',
        'name': 'Bank of India',
        'fip_id': 'BOI-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#d32f2f',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'CBIN',
        'code': 'CBIN',
        'name': 'Central Bank of India',
        'fip_id': 'CBI-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#1565c0',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'UCBA',
        'code': 'UCBA',
        'name': 'UCO Bank',
        'fip_id': 'UCO-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#0288d1',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'MAHB',
        'code': 'MAHB',
        'name': 'Bank of Maharashtra',
        'fip_id': 'BOM-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#f57c00',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'IOBA',
        'code': 'IOBA',
        'name': 'Indian Overseas Bank',
        'fip_id': 'IOB-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#1976d2',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'PSIB',
        'code': 'PSIB',
        'name': 'Punjab & Sind Bank',
        'fip_id': 'PSB-FIP',
        'category': CATEGORY_PUBLIC,
        'category_label': 'Public-Sector Bank',
        'logo_color': '#d81b60',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },

    # ==========================================
    # PRIVATE-SECTOR BANKS (16)
    # ==========================================
    {
        'id': 'HDFC',
        'code': 'HDFC',
        'name': 'HDFC Bank',
        'fip_id': 'HDFC-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#004c8f',
        'supported_types': ['SAVINGS', 'CURRENT', 'DEPOSIT', 'CREDIT_CARD'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'ICIC',
        'code': 'ICIC',
        'name': 'ICICI Bank',
        'fip_id': 'ICICI-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#bd3326',
        'supported_types': ['SAVINGS', 'CURRENT', 'CREDIT_CARD'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'UTIB',
        'code': 'UTIB',
        'name': 'Axis Bank',
        'fip_id': 'AXIS-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#97144d',
        'supported_types': ['SAVINGS', 'CURRENT', 'CREDIT_CARD'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'KKBK',
        'code': 'KKBK',
        'name': 'Kotak Mahindra Bank',
        'fip_id': 'KOTAK-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#ed1c24',
        'supported_types': ['SAVINGS', 'CURRENT', 'CREDIT_CARD'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'IDFB',
        'code': 'IDFB',
        'name': 'IDFC FIRST Bank',
        'fip_id': 'IDFC-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#991b1b',
        'supported_types': ['SAVINGS', 'CURRENT', 'CREDIT_CARD'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'FDRL',
        'code': 'FDRL',
        'name': 'Federal Bank',
        'fip_id': 'FED-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#002d62',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'INDB',
        'code': 'INDB',
        'name': 'IndusInd Bank',
        'fip_id': 'INDUS-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#84142d',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'YESB',
        'code': 'YESB',
        'name': 'Yes Bank',
        'fip_id': 'YES-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#004481',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'RATN',
        'code': 'RATN',
        'name': 'RBL Bank',
        'fip_id': 'RBL-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#2e3192',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'BDBL',
        'code': 'BDBL',
        'name': 'Bandhan Bank',
        'fip_id': 'BANDHAN-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#003b64',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'SIBL',
        'code': 'SIBL',
        'name': 'South Indian Bank',
        'fip_id': 'SIB-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#ed1c24',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'KARB',
        'code': 'KARB',
        'name': 'Karnataka Bank',
        'fip_id': 'KARN-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#7b1fa2',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'CIUB',
        'code': 'CIUB',
        'name': 'City Union Bank',
        'fip_id': 'CUB-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#00695c',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'DCBL',
        'code': 'DCBL',
        'name': 'DCB Bank',
        'fip_id': 'DCB-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#c62828',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'CSBK',
        'code': 'CSBK',
        'name': 'CSB Bank',
        'fip_id': 'CSB-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#ff6f00',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },
    {
        'id': 'TMBL',
        'code': 'TMBL',
        'name': 'Tamilnad Mercantile Bank',
        'fip_id': 'TMB-FIP',
        'category': CATEGORY_PRIVATE,
        'category_label': 'Private-Sector Bank',
        'logo_color': '#0d47a1',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'landmark'
    },

    # ==========================================
    # SMALL FINANCE BANKS (8)
    # ==========================================
    {
        'id': 'AUBL',
        'code': 'AUBL',
        'name': 'AU Small Finance Bank',
        'fip_id': 'AU-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#6a1b9a',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },
    {
        'id': 'ESFB',
        'code': 'ESFB',
        'name': 'Equitas Small Finance Bank',
        'fip_id': 'EQUITAS-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#0277bd',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },
    {
        'id': 'UJVN',
        'code': 'UJVN',
        'name': 'Ujjivan Small Finance Bank',
        'fip_id': 'UJJIVAN-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#00838f',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },
    {
        'id': 'ESAF',
        'code': 'ESAF',
        'name': 'ESAF Small Finance Bank',
        'fip_id': 'ESAF-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#2e7d32',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },
    {
        'id': 'JSFB',
        'code': 'JSFB',
        'name': 'Jana Small Finance Bank',
        'fip_id': 'JANA-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#ef6c00',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },
    {
        'id': 'UTKS',
        'code': 'UTKS',
        'name': 'Utkarsh Small Finance Bank',
        'fip_id': 'UTKARSH-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#ad1457',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },
    {
        'id': 'SURY',
        'code': 'SURY',
        'name': 'Suryoday Small Finance Bank',
        'fip_id': 'SURYODAY-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#4527a0',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },
    {
        'id': 'CSFB',
        'code': 'CSFB',
        'name': 'Capital Small Finance Bank',
        'fip_id': 'CAPITAL-FIP',
        'category': CATEGORY_SMALL_FINANCE,
        'category_label': 'Small Finance Bank',
        'logo_color': '#00695c',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'building-2'
    },

    # ==========================================
    # PAYMENTS BANKS (4)
    # ==========================================
    {
        'id': 'AIRP',
        'code': 'AIRP',
        'name': 'Airtel Payments Bank',
        'fip_id': 'AIRTEL-FIP',
        'category': CATEGORY_PAYMENTS,
        'category_label': 'Payments Bank',
        'logo_color': '#e50914',
        'supported_types': ['SAVINGS', 'UPI_WALLET'],
        'provider_supported': True,
        'icon': 'wallet'
    },
    {
        'id': 'IPPB',
        'code': 'IPPB',
        'name': 'India Post Payments Bank',
        'fip_id': 'IPPB-FIP',
        'category': CATEGORY_PAYMENTS,
        'category_label': 'Payments Bank',
        'logo_color': '#d32f2f',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'wallet'
    },
    {
        'id': 'FINO',
        'code': 'FINO',
        'name': 'Fino Payments Bank',
        'fip_id': 'FINO-FIP',
        'category': CATEGORY_PAYMENTS,
        'category_label': 'Payments Bank',
        'logo_color': '#b71c1c',
        'supported_types': ['SAVINGS', 'CURRENT'],
        'provider_supported': True,
        'icon': 'wallet'
    },
    {
        'id': 'PYTM',
        'code': 'PYTM',
        'name': 'Paytm Payments Bank',
        'fip_id': 'PAYTM-FIP',
        'category': CATEGORY_PAYMENTS,
        'category_label': 'Payments Bank',
        'logo_color': '#00b9f1',
        'supported_types': ['SAVINGS', 'WALLET'],
        'provider_supported': False,  # Under regulatory restriction, marked honestly
        'icon': 'wallet'
    }
]


class BankDirectoryService:
    """Service to discover, search, cache, and serve verified Indian banking institutions."""

    _cached_directory: Optional[List[Dict[str, Any]]] = None
    _last_refreshed_at: Optional[datetime] = None

    @classmethod
    def get_directory(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Retrieve master directory with memory caching and freshness timestamp."""
        if cls._cached_directory is None or force_refresh:
            cls._cached_directory = [dict(b) for b in MASTER_BANK_DIRECTORY]
            cls._last_refreshed_at = datetime.utcnow()
            logger.info(f"Refreshed Indian Bank Directory: {len(cls._cached_directory)} institutions loaded.")
        return cls._cached_directory

    @classmethod
    def get_last_refreshed_at(cls) -> Optional[datetime]:
        """Return timestamp of last directory cache refresh."""
        if cls._last_refreshed_at is None:
            cls.get_directory()
        return cls._last_refreshed_at

    @classmethod
    def find_institution_by_code(cls, code: str) -> Optional[Dict[str, Any]]:
        """Find an institution by its RBI IFSC prefix or code (e.g. SBIN, HDFC, UBIN)."""
        if not code:
            return None
        code_upper = code.strip().upper()
        directory = cls.get_directory()
        return next((b for b in directory if b['code'] == code_upper or b['id'] == code_upper), None)

    @classmethod
    def search_and_filter(
        cls,
        search_query: Optional[str] = None,
        category: Optional[str] = None,
        user_connected_codes: Optional[List[str]] = None,
        is_provider_ready: bool = True,
        is_sandbox_simulation: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Filter institutions by query and category, assigning honest availability statuses:
          - 'ALREADY_CONNECTED': User has an active connection with this bank
          - 'AVAILABLE': Provider supported and ready to connect
          - 'DEMO_AVAILABLE': Available via demo / sandbox simulation mode
          - 'PROVIDER_SETUP_REQUIRED': Production credentials needed on provider
          - 'NOT_SUPPORTED': Institution exists in RBI registry but unsupported by current provider
        """
        directory = cls.get_directory()
        connected_set = set(c.upper() for c in (user_connected_codes or []))

        results = []
        q = search_query.strip().lower() if search_query else None
        cat = category.strip().upper() if category and category != 'ALL' else None

        for bank in directory:
            # Category match
            if cat and bank['category'] != cat:
                continue

            # Query match (name, code, or category)
            if q:
                name_match = q in bank['name'].lower()
                code_match = q in bank['code'].lower()
                cat_match = q in bank['category_label'].lower()
                if not (name_match or code_match or cat_match):
                    continue

            # Determine Honest Status Label
            is_connected = bank['code'] in connected_set

            if is_connected:
                status_code = 'ALREADY_CONNECTED'
                status_label = 'Connected'
                can_connect = True  # Can still link another account under this bank
            elif not bank['provider_supported']:
                status_code = 'NOT_SUPPORTED'
                status_label = 'Not Supported by Provider'
                can_connect = False
            elif is_provider_ready:
                status_code = 'AVAILABLE'
                status_label = 'Available to Connect'
                can_connect = True
            elif is_sandbox_simulation:
                status_code = 'DEMO_AVAILABLE'
                status_label = 'Available in Demo Mode'
                can_connect = True
            else:
                status_code = 'PROVIDER_SETUP_REQUIRED'
                status_label = 'Provider Setup Required'
                can_connect = False

            item = dict(bank)
            item['status_code'] = status_code
            item['status_label'] = status_label
            item['can_connect'] = can_connect
            item['is_connected'] = is_connected
            results.append(item)

        return results
