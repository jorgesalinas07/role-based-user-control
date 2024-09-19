class NotActiveAccountError(Exception):
    def __init__(self):
        message = "Account is not active yet"
        super().__init__(message)
