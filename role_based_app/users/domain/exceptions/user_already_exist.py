class UserAlreadyExist(Exception):
    def __init__(self, msg):
        message = f"The following user already exists: <{msg}>"
        super().__init__(message)
