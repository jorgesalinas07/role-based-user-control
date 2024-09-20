class UserNotFoundError(Exception):
    def __init__(self, message: str = None):
        message = f"User {message} not found"
        super().__init__(message)
