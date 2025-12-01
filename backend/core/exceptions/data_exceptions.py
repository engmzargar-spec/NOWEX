from .base_exceptions import NOWEXException

class DatabaseError(NOWEXException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR", 500)

class ValidationError(NOWEXException):
    def __init__(self, message: str = "Validation failed", field: str = None):
        super().__init__(message, "VALIDATION_ERROR", 400)
        self.field = field

class NotFoundError(NOWEXException):
    def __init__(self, resource: str = "Resource", id: str = None):
        message = f"{resource} not found" + (f" with id: {id}" if id else "")
        super().__init__(message, "NOT_FOUND", 404)
        self.resource = resource
        self.id = id

class DuplicateError(NOWEXException):
    def __init__(self, resource: str = "Resource", field: str = None):
        message = f"{resource} already exists" + (f" with this {field}" if field else "")
        super().__init__(message, "DUPLICATE_ENTRY", 409)
        self.resource = resource
        self.field = field