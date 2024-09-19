class PermissionsError(Exception):
    def __init__(self, msg):
        message = f"You don't have permissions: <{msg}>"
        super().__init__(message)
