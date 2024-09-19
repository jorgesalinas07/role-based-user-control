import logging
import typing
import requests
from role_based_app.users.domain.exceptions.whatsapp_response_error import WhatsappResponseError
from role_based_app.shared.infrastructure.facebook._client import WhatsappClient


ResponseDict = typing.Dict[
    str, typing.Union[str, bool, int]
]


def parse_send_whatsapp_message_response(response: requests.Response) -> ResponseDict:
    return (
        _handle_success_transaction(
            content=response.json(),
        )
        if response.ok
        else _handle_failure(response)
    )


def _handle_success_transaction(
    content: typing.Dict[str, str],
) -> ResponseDict:
    logging.info('Phone message sent!')
    return dict(
        is_success=True,
        content=content,
    )


def _handle_failure(response: requests.Response) -> typing.Optional[ResponseDict]:
    message = "Error while communicating with Whatsapp API."
    content = response.json()
    status_code = response.status_code
    log_info = {
        "internal_message": message,
        "url": response.url,
        "content": content,
        "code": status_code,
        "message": response.text,
    }
    logging.error(log_info)
    raise WhatsappResponseError(log_info)


def make_request(payload: typing.Dict, method, url) -> typing.Optional[requests.Response]:
    http_client = WhatsappClient()
    return http_client.request(payload, method, url)
