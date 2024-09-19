import os
import typing
import requests

FACEBOOK_API_TOKEN = os.environ.get("FACEBOOK_API_TOKEN")
FACEBOOK_API_ID = os.environ.get("FACEBOOK_API_ID")
FACEBOOK_API_VERSION = os.environ.get("FACEBOOK_API_VERSION")
FACEBOOK_API_HOST = os.environ.get("FACEBOOK_API_HOST")


class WhatsappClient():
    """
    Client to interact with whatsapp
    """

    def __init__(self):
        self._creds = {
            "api_token": FACEBOOK_API_TOKEN,
            "api_id": FACEBOOK_API_ID,
            "api_version": FACEBOOK_API_VERSION,
            "api_host": FACEBOOK_API_HOST
        }
        self.base_uri = (
            f'https://{self._creds.get("api_host", "0")}/'
            f'{self._creds.get("api_version", "0")}/'
            f'{self._creds.get("api_id", "0")}'
        )

    def request(self, payload, method, url):
        if not url.startswith("/"):
            raise ValueError("Must specify url as the relative path starting with /")
        self._ensure_logged_in()
        response = self._request(
            method,
            f"{self.base_uri}{url}",
            payload,
            headers=self._whatsapp_http_header(),
        )
        return response

    def _whatsapp_http_header(self) -> typing.Dict[str, str]:
        header = {
            "Content-Type": "application/json",
            "Authorization": 'Bearer ' + f'{self._creds.get("api_token", "")}',
        }
        return header

    def _request(self, method, url, payload, headers):
        if not url.startswith(self.base_uri):
            raise ValueError(
                f"Whatsapp requests must be made to paths at {self.base_uri}"
            )
        if method == "POST":
            return requests.post(url=url, json=payload, headers=headers)
        raise NotImplementedError(method)

    def _ensure_logged_in(self):
        # Logic to confirm token and id
        pass
