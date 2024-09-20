class InvalidCredentialsError(Exception):
    def __init__(self, message: str = None):
        message = f"Invalid credentials provided {message}"
        super().__init__(message)
