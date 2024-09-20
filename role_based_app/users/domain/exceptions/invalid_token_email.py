class InvalidTokenEmail(Exception):
    def __init__(self):
        message = "Invalid token: "
        super().__init__(message)
