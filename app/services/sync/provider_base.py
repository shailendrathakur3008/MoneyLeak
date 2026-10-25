"""
Provider-Agnostic Banking Interface for Indian Financial Institutions.
Defines abstract contracts for Account Aggregator (AA) and direct bank feed providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseBankingProvider(ABC):
    """Abstract base class that all banking data providers must implement."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the human-readable name of the provider."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if production or sandbox credentials are configured."""
        pass

    @abstractmethod
    def get_provider_status(self) -> Dict[str, Any]:
        """Return metadata regarding environment, configuration status, and health."""
        pass

    @abstractmethod
    def get_supported_institutions(self) -> List[Dict[str, Any]]:
        """Return the list of financial institutions supported by this provider."""
        pass

    @abstractmethod
    def create_consent_request(
        self,
        user_phone: str,
        fip_code: str,
        account_types: List[str] = None,
        redirect_url: str = None
    ) -> Dict[str, Any]:
        """
        Initiate an Account Aggregator consent artifact request.
        Returns:
          {
            'success': bool,
            'consent_id': str,
            'consent_handle': str,
            'url': str,  # Consent Webview URL for user authorization
            'status': str,
            'mode': str,
            'message': str
          }
        """
        pass

    @abstractmethod
    def get_consent_status(self, consent_id: str) -> Dict[str, Any]:
        """
        Poll or verify current consent status from the provider.
        Status transitions: PENDING, ACTIVE, REJECTED, EXPIRED, REVOKED.
        """
        pass

    @abstractmethod
    def fetch_accounts(self, consent_id: str) -> List[Dict[str, Any]]:
        """Retrieve linked bank accounts authorized under the given consent."""
        pass

    @abstractmethod
    def fetch_transactions(
        self,
        consent_id: str,
        fip_code: str,
        account_id: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch normalized financial transactions under authorized consent.
        Returns list of standardized transaction dictionaries.
        """
        pass

    @abstractmethod
    def revoke_consent(self, consent_id: str) -> Dict[str, Any]:
        """Revoke active consent artifact with the provider."""
        pass

    @abstractmethod
    def check_provider_health(self) -> Dict[str, Any]:
        """Ping or check provider endpoint reachability."""
        pass
