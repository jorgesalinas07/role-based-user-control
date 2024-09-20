class InvalidMessageParameter(Exception):
    def __init__(self, error_message):
        message = f"Invalid message parameter: {error_message}"
        super().__init__(message)
