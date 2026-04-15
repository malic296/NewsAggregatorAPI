from typing import Optional
from fastapi import status

class AppError(Exception):
    def __init__(self, *, status_code: int, public_message: str, internal_message: Optional[str] = None):
        self.status_code = status_code
        self.internal_message = internal_message
        self.public_message = public_message if public_message else "Internal Server Error."

class AuthenticationRequiredError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            public_message="You need to login or register first.",
            internal_message="Someone without authentication tried to call authenticated endpoint."
        )

class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            public_message="Invalid login details."
        )

class EmailAlreadyUsedError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            public_message="Email already used."
        )

class UsernameAlreadyUsedError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            public_message="Username already used."
        )

class ArticleNotFoundError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            public_message="Article not found."
        )

class InvalidVerificationCodeError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            public_message="Invalid verification code."
        )

class RegistrationExpiredError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_410_GONE,
            public_message="Registration expired."
        )

class InvalidCurrentPasswordError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            public_message="Invalid current password."
        )

class PasswordReuseError(AppError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            public_message="Cannot change password to current password."
        )

class DependencyUnavailableError(AppError):
    def __init__(self, dependency: str = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            internal_message=f"Dependency {dependency if dependency else ""} unavailable.",
            public_message="Server failed because of external error. Try again later."
        )

