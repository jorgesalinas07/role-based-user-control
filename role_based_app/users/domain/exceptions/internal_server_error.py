class InternalServerError(Exception):
    def __init__(self, message):
        message = f"Something went wrong: {message}"
        super().__init__(message)
