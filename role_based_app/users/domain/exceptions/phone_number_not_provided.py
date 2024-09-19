class PhoneNumberNotProvided(Exception):
    def __init__(self):
        message = "Phone number not provided"
        super().__init__(message)
