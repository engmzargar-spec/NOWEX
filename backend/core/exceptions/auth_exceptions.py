from .base_exceptions import NOWEXException

class AuthenticationError(NOWEXException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR", 401)

class AuthorizationError(NOWEXException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "FORBIDDEN", 403)

class TokenExpiredError(AuthenticationError):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)
        self.code = "TOKEN_EXPIRED"

class InvalidTokenError(AuthenticationError):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)
        self.code = "INVALID_TOKEN"