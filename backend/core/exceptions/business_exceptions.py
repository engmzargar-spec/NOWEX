from .base_exceptions import NOWEXException

class ScoringError(NOWEXException):
    def __init__(self, message: str = "Scoring system error", details: dict = None):
        super().__init__(message, "SCORING_ERROR", 500)
        self.details = details or {}

class ReferralError(NOWEXException):
    def __init__(self, message: str = "Referral system error", details: dict = None):
        super().__init__(message, "REFERRAL_ERROR", 500)
        self.details = details or {}

class KYCError(NOWEXException):
    def __init__(self, message: str = "KYC verification error", details: dict = None):
        super().__init__(message, "KYC_ERROR", 400)
        self.details = details or {}

class TradingError(NOWEXException):
    def __init__(self, message: str = "Trading operation failed", details: dict = None):
        super().__init__(message, "TRADING_ERROR", 400)
        self.details = details or {}

class WalletError(NOWEXException):
    def __init__(self, message: str = "Wallet operation failed", details: dict = None):
        super().__init__(message, "WALLET_ERROR", 400)
        self.details = details or {}