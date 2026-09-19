
class AuthError(Exception):

    pass


class UserAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):

    pass


class UserNotFoundError(AuthError):

    pass


class UserNotVerifiedError(AuthError):

    pass


class TokenError(AuthError):

    pass


class InvalidTokenError(TokenError):

    pass


class TokenExpiredError(TokenError):

    pass


class TokenAlreadyUsedError(TokenError):

    pass