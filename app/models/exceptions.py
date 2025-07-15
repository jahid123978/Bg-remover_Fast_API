class APIException(Exception):
    """Base API exception class."""
    def __init__(self, message: str, error_code: str, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(APIException):
    """Exception for validation errors."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)

class ProcessingException(APIException):
    """Exception for processing errors."""
    def __init__(self, message: str):
        super().__init__(message, "PROCESSING_ERROR", 500)

class AuthenticationException(APIException):
    """Exception for authentication errors."""
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)