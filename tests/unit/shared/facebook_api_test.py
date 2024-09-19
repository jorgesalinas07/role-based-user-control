import pytest
from unittest.mock import patch
import requests
from dotenv import load_dotenv
import os
from os.path import join, dirname
from role_based_app.users.domain.exceptions.whatsapp_response_error import (
    WhatsappResponseError,
)
from role_based_app.shared.infrastructure.facebook._parser import (
    parse_send_whatsapp_message_response,
)
from tests.integration.infrastructure.sample_response import (
    whatsapp_api_successful_response,
    whatsapp_api_id_error_response,
    whatsapp_api_token_error_response,
)
from role_based_app.shared.infrastructure.facebook._client import WhatsappClient

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), ".env")
FACEBOOK_API_ID = os.environ.get("FACEBOOK_API_ID")
FACEBOOK_API_VERSION = os.environ.get("FACEBOOK_API_VERSION")
FACEBOOK_API_HOST = os.environ.get("FACEBOOK_API_HOST")


def test__parse_send_whatsapp_message_when_response_success(mocker):
    mock_response = {"is_success": True, "content": whatsapp_api_successful_response()}

    response = mocker.create_autospec(requests.Response)
    response.ok = True
    response.status_code = 200
    response.url = (
        f"https://{FACEBOOK_API_HOST}/{FACEBOOK_API_VERSION}/{FACEBOOK_API_ID}/messages"
    )
    response.text = "error"
    mocker.patch("requests.Response.json").return_value = mock_response

    response = parse_send_whatsapp_message_response(response)

    assert response["is_success"] is True


def test_parse_send_whatsapp_message_response_raises_whatsapp_response_error_when_invalid_token(
    mocker,
):
    mock_response = {
        "is_success": False,
        "content": whatsapp_api_token_error_response(),
    }

    response = mocker.create_autospec(requests.Response)
    response.ok = False
    response.status_code = 400
    response.url = (
        f"https://{FACEBOOK_API_HOST}/{FACEBOOK_API_VERSION}/{FACEBOOK_API_ID}/messages"
    )
    response.text = "error"
    mocker.patch("requests.Response.json").return_value = mock_response

    with pytest.raises(WhatsappResponseError):
        response = parse_send_whatsapp_message_response(response)
        assert response["is_success"] is False
        assert "code" in response.get("error", {}) and response["error"]["code"] == 190


def test_parse_send_whatsapp_message_response_raises_whatsapp_response_error_when_invalid_id(
    mocker,
):
    mock_response = {"is_success": False, "content": whatsapp_api_id_error_response()}
    response = mocker.create_autospec(requests.Response)
    response.ok = False
    response.status_code = 400
    response.url = (
        f"https://{FACEBOOK_API_HOST}/{FACEBOOK_API_VERSION}/{FACEBOOK_API_ID}/messages"
    )
    response.text = "error"
    mocker.patch("requests.Response.json").return_value = mock_response
    with pytest.raises(WhatsappResponseError):
        response = parse_send_whatsapp_message_response(response)
        assert response["is_success"] is False
        assert "code" in response.get("error", {}) and response["error"]["code"] == 100


@patch('requests.post')
def test_request_post(mock_post):
    mock_post.return_value.json.return_value = {'success': True}
    client = WhatsappClient()
    payload = {'key': 'value'}
    method = 'POST'
    url = '/test'

    response = client.request(payload, method, url)

    mock_post.assert_called_once_with(
        url=client.base_uri + url,
        json=payload,
        headers=client._whatsapp_http_header()
    )
    assert response.json() == {'success': True}


def test_request_not_post():
    client = WhatsappClient()
    payload = {'key': 'value'}
    method = 'GET'
    url = '/test'

    with pytest.raises(NotImplementedError):
        client.request(payload, method, url)


@patch('requests.post')
def test_request_post_invalid_url(mock_post, monkeypatch):
    monkeypatch.setenv("api_token", "test_token")
    mock_post.return_value.json.return_value = {'success': True}
    client = WhatsappClient()
    payload = {'key': 'value'}
    method = 'POST'
    url = 'http://invalid_url.com/test'

    with pytest.raises(ValueError):
        client.request(payload, method, url)


@patch('requests.post')
def test_request_post_headers(mock_post, monkeypatch):
    monkeypatch.setenv("api_token", "test_token")
    mock_post.return_value.json.return_value = {'success': True}
    client = WhatsappClient()
    payload = {'key': 'value'}
    method = 'POST'
    url = '/test'

    response = client.request(payload, method, url)

    headers = client._whatsapp_http_header()
    mock_post.assert_called_once_with(url=client.base_uri + url, json=payload, headers=headers)
    assert response.json() == {'success': True}
