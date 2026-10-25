"""
Merchant Normalization and Automatic Categorization Engine.
Extracts clean merchant names, payment methods, transaction types,
and maps transactions to user categories with confidence ratings and user preference memory.
"""
import re
from typing import Dict, Any, Optional, Tuple
from app.models.category import Category
from app.models.sync import MerchantCategoryPreference


# Comprehensive pattern registry for Indian and Global merchants covering all 21 categories
MERCHANT_RULES = [
    # 1. Food & Dining
    {
        'pattern': r'(zomato|swiggy(?!\s*instamart)|mcdonald|starbucks|domino|pizza\s*hut|kfc|burger\s*king|haldiram|chai\s*point|blue\s*tokai|wow\s*momo|rebel\s*foods|behrouz|faasos|ovenstory|subway|barbeque\s*nation|cafe\s*coffee\s*day|eatfit|dining|restaurant|cafe)',
        'merchant': 'Food & Dining',
        'category_keywords': ['dining out', 'food', 'cafes', 'restaurants', 'meals', 'dining out & cafes', 'food delivery apps'],
        'default_group': 'WANTS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.95
    },
    # 2. Groceries
    {
        'pattern': r'(blinkit|zepto|bigbasket|bb\s*now|instamart|nature.?s\s*basket|dmart|d-mart|spencer|dunzo|milkbasket|country\s*delight|reliance\s*smart|jiomart|more\s*retail|grofer|fresh\s*to\s*home|licious|supermarket|grocery|groceries)',
        'merchant': 'Groceries',
        'category_keywords': ['essential groceries', 'groceries', 'supermarket', 'food'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.95
    },
    # 3. Shopping
    {
        'pattern': r'(amazon(?!\s*pay\s*recharge)|flipkart|myntra|ajio|meesho|zara|h&m|nykaa|tata\s*cliq|croma|reliance\s*digital|lenskart|decathlon|uniqlo|shoppers\s*stop|westside|lifestyle|snapdeal|urbanic|shopping|clothing|apparel)',
        'merchant': 'Shopping',
        'category_keywords': ['shopping & lifestyle', 'shopping', 'clothing', 'apparel', 'personal'],
        'default_group': 'WANTS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.92
    },
    # 4. Transport
    {
        'pattern': r'(uber|ola\s*cabs|ola(?!\s*electric)|rapido|namma\s*metro|dmrc|delhi\s*metro|mumbai\s*metro|chalo|blusmart|auto\s*stand|bus\s*pass|commute)',
        'merchant': 'Transport',
        'category_keywords': ['essential commute & fuel', 'transport', 'commute', 'metro', 'travel'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.90
    },
    # 5. Fuel
    {
        'pattern': r'(fuel|petrol|diesel|cng|hpcl|bpcl|iocl|indian\s*oil|bharat\s*petroleum|hindustan\s*petroleum|shell\s*petrol|gas\s*station)',
        'merchant': 'Fuel',
        'category_keywords': ['essential commute & fuel', 'fuel', 'petrol', 'transport'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.92
    },
    # 6. Bills & Utilities
    {
        'pattern': r'(bescom|tneb|tata\s*power|adani\s*electricity|mseb|bses|torrent\s*power|igl|mahanagar\s*gas|gujarat\s*gas|bwssb|delhi\s*jal|electricity|water\s*bill|gas\s*utility|airtel|jio|vodafone|vi\s*prepaid|vi\s*postpaid|act\s*fibernet|hathway|tata\s*play|broadband)',
        'merchant': 'Bills & Utilities',
        'category_keywords': ['utilities (power, water, gas)', 'utilities', 'basic internet & mobile', 'electricity', 'bills', 'water'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.95
    },
    # 7. Rent & Housing
    {
        'pattern': r'(nobroker|housing\.com|magicbricks|society\s*maintenance|flat\s*maintenance|house\s*rent|apartment\s*rent|pg\s*rent|landlord|nestaway|rent\s*payment)',
        'merchant': 'Rent & Housing',
        'category_keywords': ['housing & rent', 'rent', 'accommodation', 'housing'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.95
    },
    # 8. Healthcare
    {
        'pattern': r'(apollo\s*pharmacy|apollo|1mg|tata\s*1mg|pharmeasy|netmeds|medplus|practo|dr\s*lal|max\s*healthcare|fortis|hospital|clinic|pharmacy|diagnostic|thyrocare|metropolis)',
        'merchant': 'Healthcare',
        'category_keywords': ['healthcare & pharmacy', 'healthcare', 'medical', 'medicine', 'pharmacy', 'health'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.92
    },
    # 9. Education
    {
        'pattern': r'(byju|unacademy|coursera|udemy|edx|upgrad|simplilearn|school\s*fee|college\s*fee|tuition|exam\s*fee|university|coaching|allen|aakash|vedantu)',
        'merchant': 'Education',
        'category_keywords': ['education fees', 'books and stationery', 'education', 'tuition'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.92
    },
    # 10. Entertainment
    {
        'pattern': r'(netflix|spotify|prime\s*video|hotstar|disney|youtube\s*premium|apple\.com|apple\s*services|sonyliv|zee5|audible|chatgpt|openai|bookmyshow|pvr|inox|cinepolis|entertainment|movies)',
        'merchant': 'Entertainment',
        'category_keywords': ['entertainment & outings', 'subscriptions & streaming', 'entertainment', 'subscriptions'],
        'default_group': 'WANTS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.95
    },
    # 11. Travel
    {
        'pattern': r'(irctc|makemytrip|mmt|cleartrip|yatra|indigo|air\s*india|spicejet|vistara|goibibo|redbus|abhibus|oyo|airbnb|booking\.com|agoda|flights|hotel)',
        'merchant': 'Travel',
        'category_keywords': ['vacation & leisure travel', 'travel', 'vacation', 'trips', 'flights', 'hotels'],
        'default_group': 'WANTS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.92
    },
    # 12. Personal Care
    {
        'pattern': r'(urban\s*company|salon|spa|enrich|naturals\s*salon|geetanjali|jawed\s*habib|kaya\s*skin|barber|parlour|massage|grooming)',
        'merchant': 'Personal Care',
        'category_keywords': ['shopping & lifestyle', 'personal care', 'personal', 'lifestyle'],
        'default_group': 'WANTS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.90
    },
    # 13. Investments (Savings Contribution, NOT consumption!)
    {
        'pattern': r'(zerodha|groww|upstox|kuvera|smallcase|coin|indmoney|nippon\s*india|hdfc\s*mf|sbi\s*mutual|icici\s*pru|axis\s*mutual|mirae\s*asset|uti\s*mf|parag\s*parikh|ppfas|ppf|nps|mutual\s*fund|sip\s*debit|stocks|shares|investment)',
        'merchant': 'Investments',
        'category_keywords': ['mutual funds & stocks', 'investments', 'savings', 'mutual funds', 'sip', 'wealth'],
        'default_group': 'SAVINGS',
        'transaction_type': 'SAVINGS_CONTRIBUTION',
        'confidence': 0.95
    },
    # 14. Insurance
    {
        'pattern': r'(lic\s*of\s*india|lic\s*premium|hdfc\s*life|icici\s*prudential\s*life|icici\s*lombard|sbi\s*life|max\s*life|star\s*health|tata\s*aig|bajaj\s*allianz|care\s*health|policybazaar|insurance\s*premium|general\s*insurance)',
        'merchant': 'Insurance',
        'category_keywords': ['healthcare & pharmacy', 'insurance', 'life cover', 'medical insurance'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.93
    },
    # 15. Loan Payments
    {
        'pattern': r'(home\s*loan|auto\s*loan|car\s*loan|personal\s*loan|bajaj\s*finance|bajaj\s*finserv|hdb\s*financial|tata\s*capital|muthoot|manappuram|loan\s*emi|emi\s*debit|minimum\s*loan)',
        'merchant': 'Loan Payments',
        'category_keywords': ['minimum loan emis', 'additional debt prepayment', 'debt repayment', 'loan emi'],
        'default_group': 'NEEDS',
        'transaction_type': 'DEBT_REPAYMENT',
        'confidence': 0.94
    },
    # 16. ATM Withdrawals
    {
        'pattern': r'(atm\s*wdl|cash\s*wdl|nfs\s*atm|atm\s*cash|cash\s*withdrawal)',
        'merchant': 'ATM Cash Withdrawal',
        'category_keywords': ['shopping & lifestyle', 'atm withdrawals', 'cash', 'other'],
        'default_group': 'WANTS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.95
    },
    # 17. Bank Charges
    {
        'pattern': r'(imps\s*charge|sms\s*alert|min\s*bal|consolidated\s*charges|debit\s*card\s*annual\s*fee|cheque\s*return\s*charge|service\s*charge|bank\s*charge)',
        'merchant': 'Bank Charges',
        'category_keywords': ['utilities (power, water, gas)', 'bank charges', 'other'],
        'default_group': 'NEEDS',
        'transaction_type': 'EXPENSE',
        'confidence': 0.92
    },
    # 18. Transfers & CC Bill Payments
    {
        'pattern': r'(cred(?!\s*rent)|cheq|cc\s*payment|credit\s*card\s*bill|billdesk.*card|self\s*transfer|transfer\s*to\s*self|to\s*own\s*a/c|sweep\s*trf|account\s*transfer|inter\s*account)',
        'merchant': 'Account Transfer',
        'category_keywords': ['account transfer', 'transfers', 'self transfer'],
        'default_group': 'SAVINGS',
        'transaction_type': 'TRANSFER',
        'confidence': 0.90
    },
    # 19. Salary & Earnings (Income)
    {
        'pattern': r'(salary|payroll|stipend|wages|infosys|tcs|wipro|accenture|cognizant|google|amazon\s*dev|microsoft|hcl\s*tech|tech\s*mahindra|flipkart\s*internet|paycheck|monthly\s*salary)',
        'merchant': 'Salary / Employer',
        'category_keywords': ['salary', 'income', 'part-time income', 'earnings'],
        'default_group': 'SAVINGS',
        'transaction_type': 'INCOME',
        'confidence': 0.95
    },
    # 20. Refunds & Reversals
    {
        'pattern': r'(refund|reversal|cashback|cash\s*back|chargeback|reimbursement|return\s*credit)',
        'merchant': 'Refund / Cash Back',
        'category_keywords': ['refund & cashbacks', 'refund', 'reimbursement'],
        'default_group': 'NEEDS',
        'transaction_type': 'REFUND',
        'confidence': 0.92
    }
]


class MerchantCategorizer:
    """Intelligent normalizer and categorizer for Indian financial transactions."""

    @staticmethod
    def normalize_narration(raw_narration: str) -> Tuple[str, str, Optional[str]]:
        """
        Extract clean merchant name, payment method, and reference ID (UTR/RRN).
        Returns: (normalized_merchant, payment_method, ref_id)
        """
        if not raw_narration:
            return 'Unknown Merchant', 'OTHER', None

        narration = raw_narration.strip()
        payment_method = 'OTHER'
        ref_id = None
        merchant_candidate = narration

        # 1. UPI Narration Parsing (standard NPCI format: UPI/UTR/MERCHANT/HANDLE...)
        upi_match = re.search(r'UPI/([0-9]{9,15})/([^/]+)', narration, re.IGNORECASE)
        if upi_match:
            payment_method = 'UPI'
            ref_id = upi_match.group(1)
            merchant_candidate = upi_match.group(2).strip()
        elif 'UPI' in narration.upper():
            payment_method = 'UPI'
            utr_match = re.search(r'\b([0-9]{12})\b', narration)
            if utr_match:
                ref_id = utr_match.group(1)

        # 2. Card POS / E-COM Parsing
        card_match = re.search(r'(?:POS|E-?COM|MERCH)\s+([0-9X*]+)\s+([^/]+)', narration, re.IGNORECASE)
        if card_match:
            payment_method = 'CARD'
            merchant_candidate = card_match.group(2).strip()
        elif re.search(r'\b(?:VISA|MASTERCARD|RUPAY|DEBIT\s*CARD|CREDIT\s*CARD)\b', narration, re.IGNORECASE):
            payment_method = 'CARD'

        # 3. Net Banking / Payment Gateway
        if re.search(r'\b(?:BILLDESK|RAZORPAY|CCAVENUE|PAYU|PAYTM\s*PG|CASHFREE)\b', narration, re.IGNORECASE):
            payment_method = 'NET_BANKING'

        # 4. NEFT / IMPS / RTGS
        if re.search(r'\b(?:NEFT|IMPS|RTGS)\b', narration, re.IGNORECASE):
            payment_method = 'NEFT_RTGS'
            ref_match = re.search(r'(?:NEFT|IMPS|RTGS)[/-]([A-Z0-9]+)', narration, re.IGNORECASE)
            if ref_match:
                ref_id = ref_match.group(1)

        # 5. ATM Cash Withdrawal
        if re.search(r'\b(?:ATM\s*WDL|CASH\s*WDL|NFS\s*ATM)\b', narration, re.IGNORECASE):
            payment_method = 'ATM'
            merchant_candidate = 'ATM Cash Withdrawal'

        # Clean merchant candidate string
        clean_merchant = MerchantCategorizer._clean_merchant_text(merchant_candidate)
        return clean_merchant, payment_method, ref_id

    @staticmethod
    def _clean_merchant_text(text: str) -> str:
        """Strip UPI handle garbage, reference codes, branch names, and junk characters."""
        # Remove common bank/UPI suffixes
        t = re.sub(r'@[a-zA-Z0-9]+', '', text)
        t = re.sub(r'/(?:PAYTM|YESB|ICIC|HDFC|AXIS|SBIN|OKAXIS|OKHDFCBANK|OKSBI|BARODAMPAY).*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(?:PVT\s*LTD|PRIVATE\s*LIMITED|LTD|LLP|INDIA|SERVICES|SOLUTIONS|BANGALORE|MUMBAI|DELHI|PUNE|HYDERABAD|GURGAON)\b', '', t, flags=re.IGNORECASE)
        t = re.sub(r'[^a-zA-Z0-9\s&.-]', ' ', t)
        t = re.sub(r'\s+', ' ', t).strip()

        # Specific known name cleanup
        text_lower = t.lower()
        if 'zomato' in text_lower:
            return 'Zomato'
        if 'swiggy' in text_lower:
            return 'Swiggy Instamart' if 'instamart' in text_lower else 'Swiggy'
        if 'blinkit' in text_lower:
            return 'Blinkit'
        if 'zepto' in text_lower:
            return 'Zepto'
        if 'bigbasket' in text_lower or 'bb daily' in text_lower or 'bb now' in text_lower:
            return 'BigBasket'
        if 'amazon' in text_lower:
            return 'Amazon Pay' if 'pay' in text_lower else 'Amazon India'
        if 'flipkart' in text_lower:
            return 'Flipkart'
        if 'myntra' in text_lower:
            return 'Myntra'
        if 'ajio' in text_lower:
            return 'Ajio'
        if 'uber' in text_lower:
            return 'Uber'
        if 'ola' in text_lower:
            return 'Ola Cabs'
        if 'rapido' in text_lower:
            return 'Rapido'
        if 'netflix' in text_lower:
            return 'Netflix'
        if 'spotify' in text_lower:
            return 'Spotify'
        if 'zerodha' in text_lower:
            return 'Zerodha'
        if 'groww' in text_lower:
            return 'Groww'
        if 'cred' in text_lower:
            return 'CRED'
        if 'airtel' in text_lower:
            return 'Airtel'
        if 'jio' in text_lower:
            return 'Jio'
        if 'irctc' in text_lower:
            return 'IRCTC'

        # Title case if long enough, else upper case
        if len(t) <= 4:
            return t.upper() if t else 'Unknown Merchant'
        return t.title()

    @staticmethod
    def categorize_transaction(
        user_id: int,
        raw_narration: str,
        direction: str = 'DEBIT',
        amount_minor_units: int = 0
    ) -> Dict[str, Any]:
        """
        Determine category, transaction_type, confidence_score, and reasoning.
        Respects:
          1. User-specific learned merchant preferences.
          2. Rule pattern registry.
          3. Account direction (Credit vs Debit).
        """
        clean_merchant, payment_method, ref_id = MerchantCategorizer.normalize_narration(raw_narration)
        merchant_key = clean_merchant.lower().strip()

        # Step 1: Check user's saved merchant preference
        user_pref = MerchantCategoryPreference.query.filter_by(
            user_id=user_id,
            merchant_normalized=merchant_key
        ).first()

        if user_pref and user_pref.category:
            return {
                'normalized_merchant': clean_merchant,
                'payment_method': payment_method,
                'ref_id': ref_id,
                'category_id': user_pref.category_id,
                'category_name': user_pref.category.name,
                'budget_group': user_pref.category.budget_group,
                'transaction_type': user_pref.transaction_type,
                'confidence_score': 0.99,
                'confidence_level': 'HIGH',
                'reason': f"User-defined rule for '{clean_merchant}'"
            }

        # Step 2: Directional overrides (Credit check)
        # In Indian banking, a CREDIT is either Salary/Income, a Refund, or a Transfer
        is_credit = direction.upper() == 'CREDIT'
        text_to_search = f"{raw_narration} {clean_merchant}".lower()

        # Check for Refund explicitly
        is_refund = bool(re.search(r'\b(refund|reversal|cashback|cash\s*back|chargeback)\b', text_to_search))
        if is_credit and is_refund:
            matched_cat = MerchantCategorizer._find_matching_user_category(user_id, ['refund', 'dining out', 'shopping', 'groceries'])
            return {
                'normalized_merchant': clean_merchant,
                'payment_method': payment_method,
                'ref_id': ref_id,
                'category_id': matched_cat.id if matched_cat else None,
                'category_name': matched_cat.name if matched_cat else 'Refund',
                'budget_group': matched_cat.budget_group if matched_cat else 'WANTS',
                'transaction_type': 'REFUND',
                'confidence_score': 0.92,
                'confidence_level': 'HIGH',
                'reason': 'Refund narration detected; offsets consumption expense.'
            }

        # Step 3: Match against pattern registry
        for rule in MERCHANT_RULES:
            if re.search(rule['pattern'], text_to_search):
                rule_type = rule['transaction_type']
                
                # If it's a CREDIT and rule is EXPENSE, check if it's salary or refund
                if is_credit and rule_type == 'EXPENSE':
                    # E.g. Money received from Zomato or Swiggy -> likely refund
                    rule_type = 'REFUND'

                matched_cat = MerchantCategorizer._find_matching_user_category(
                    user_id,
                    rule['category_keywords'],
                    target_group=rule.get('default_group')
                )

                return {
                    'normalized_merchant': clean_merchant if clean_merchant != 'Unknown Merchant' else rule['merchant'],
                    'payment_method': payment_method,
                    'ref_id': ref_id,
                    'category_id': matched_cat.id if matched_cat else None,
                    'category_name': matched_cat.name if matched_cat else rule['merchant'],
                    'budget_group': matched_cat.budget_group if matched_cat else rule.get('default_group', 'WANTS'),
                    'transaction_type': rule_type,
                    'confidence_score': rule['confidence'],
                    'confidence_level': 'HIGH' if rule['confidence'] >= 0.85 else 'MEDIUM',
                    'reason': f"Matched merchant pattern for {rule['merchant']}"
                }

        # Step 4: Fallback for unmatched transactions
        if is_credit:
            # Check if large credit looks like income
            income_cat = MerchantCategorizer._find_matching_user_category(user_id, ['income', 'salary', 'other income'])
            return {
                'normalized_merchant': clean_merchant,
                'payment_method': payment_method,
                'ref_id': ref_id,
                'category_id': income_cat.id if income_cat else None,
                'category_name': income_cat.name if income_cat else 'Income / Credit',
                'budget_group': 'SAVINGS',
                'transaction_type': 'INCOME',
                'confidence_score': 0.60,
                'confidence_level': 'MEDIUM',
                'reason': 'Unidentified bank credit; suggested as potential income.'
            }

        # Unmatched Debit
        default_cat = Category.query.filter(
            (Category.user_id == user_id) | (Category.user_id.is_(None)),
            Category.is_active.is_(True),
            Category.budget_group == 'WANTS'
        ).first()

        return {
            'normalized_merchant': clean_merchant,
            'payment_method': payment_method,
            'ref_id': ref_id,
            'category_id': default_cat.id if default_cat else None,
            'category_name': default_cat.name if default_cat else 'Other / Uncategorized',
            'budget_group': default_cat.budget_group if default_cat else 'WANTS',
            'transaction_type': 'EXPENSE',
            'confidence_score': 0.40,
            'confidence_level': 'LOW',
            'reason': 'Unrecognized merchant; queued for user verification.'
        }

    @staticmethod
    def _find_matching_user_category(
        user_id: int,
        keywords: list,
        target_group: Optional[str] = None
    ) -> Optional[Category]:
        """Find the best user category matching a list of keywords."""
        query = Category.query.filter(
            (Category.user_id == user_id) | (Category.user_id.is_(None)),
            Category.is_active.is_(True),
            Category.is_archived.is_(False)
        )

        user_categories = query.all()
        # 1. Exact name match
        for cat in user_categories:
            name_lower = cat.name.lower()
            for kw in keywords:
                if kw.lower() == name_lower:
                    return cat

        # 2. Substring match
        for cat in user_categories:
            name_lower = cat.name.lower()
            for kw in keywords:
                if kw.lower() in name_lower or name_lower in kw.lower():
                    return cat

        # 3. Budget group fallback
        if target_group:
            for cat in user_categories:
                if cat.budget_group == target_group:
                    return cat

        return user_categories[0] if user_categories else None
