class InvalidPasswordError(Exception):
    def __init__(self):
        message = "Passwords do not match"
        super().__init__(message)
