from .base_exceptions import NOWEXException

class ExternalServiceError(NOWEXException):
    def __init__(self, message: str = "External service error", service: str = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502)
        self.service = service

class APIRateLimitError(ExternalServiceError):
    def __init__(self, message: str = "API rate limit exceeded", service: str = None):
        super().__init__(message, service)
        self.code = "RATE_LIMIT_EXCEEDED"
        self.status_code = 429

class ServiceTimeoutError(ExternalServiceError):
    def __init__(self, message: str = "Service timeout", service: str = None):
        super().__init__(message, service)
        self.code = "SERVICE_TIMEOUT"
        self.status_code = 504