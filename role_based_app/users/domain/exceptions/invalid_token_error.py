class InvalidTokenError(Exception):
    def __init__(self):
        message = "Invalid token provided"
        super().__init__(message)
