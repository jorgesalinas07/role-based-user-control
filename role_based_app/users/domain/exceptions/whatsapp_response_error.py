class WhatsappResponseError(Exception):
    def __init__(self, message: dict = None):
        message = f"Whatsapp response error {message}"
        super().__init__(message)
