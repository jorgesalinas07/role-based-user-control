class TokenExpiredError(Exception):
    def __init__(self):
        message = "Token Expired: "
        super().__init__(message)
