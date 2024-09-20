from http import HTTPStatus

ERROR_400_FORMAT = {
    "statusCode": HTTPStatus.BAD_REQUEST,
    "error": "The request has an invalid format",
}

ERROR_400_ACTION = {
    "statusCode": HTTPStatus.BAD_REQUEST,
    "error": "No valid action defined",
}

ERROR_400_EVENT = {
    "statusCode": HTTPStatus.BAD_REQUEST,
    "error": "No valid event defined",
}
