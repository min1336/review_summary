"""Custom exception classes for the application."""

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500, detail: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource} with id '{resource_id}' not found",
            status_code=404,
        )


class ValidationException(AppException):
    """Validation error."""

    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(message=message, status_code=422, detail=detail)


class AuthenticationException(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message, status_code=401)


class AuthorizationException(AppException):
    """Authorization failed."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, status_code=403)


class AIServiceException(AppException):
    """AI service error."""

    def __init__(self, message: str = "AI service temporarily unavailable") -> None:
        super().__init__(message=message, status_code=503)
