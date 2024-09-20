import logging
from role_based_app.shared.commons.constants.error import ERROR_400_ACTION
from role_based_app.users.infrastructure import user_controller


def lambda_handler(event, context):
    action = event.get("action")
    if action == "create_user":
        return user_controller.create_user(event)
    if action == "get_user":
        return user_controller.get_user(event)
    if action == "login":
        return user_controller.login(event)
    if action == "delete_user":
        return user_controller.delete_user(event)
    logging.error(msg=ERROR_400_ACTION)
    return ERROR_400_ACTION
