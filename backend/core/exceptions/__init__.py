# Exception classes for NOWEX Platform
from .base_exceptions import NOWEXException
from .auth_exceptions import AuthenticationError, AuthorizationError, TokenExpiredError, InvalidTokenError
from .business_exceptions import ScoringError, ReferralError, KYCError, TradingError, WalletError
from .data_exceptions import DatabaseError, ValidationError, NotFoundError, DuplicateError
from .service_exceptions import ExternalServiceError, APIRateLimitError, ServiceTimeoutError

__all__ = [
    'NOWEXException',
    'AuthenticationError',
    'AuthorizationError',
    'TokenExpiredError', 
    'InvalidTokenError',
    'ScoringError',
    'ReferralError',
    'KYCError',
    'TradingError',
    'WalletError',
    'DatabaseError',
    'ValidationError',
    'NotFoundError',
    'DuplicateError',
    'ExternalServiceError',
    'APIRateLimitError',
    'ServiceTimeoutError'
]