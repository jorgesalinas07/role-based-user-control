def whatsapp_api_successful_response():
    return {
        "messaging_product": "whatsapp",
        "contacts": [{"input": "570000000000", "wa_id": "570000000000"}],
        "messages": [{"id": "wamid.HBgMNTczMTU4ODYzMTE3FQIAERgSQzRBNjIyQTNEQTUxMzYxQTBCAA=="}],
    }


def whatsapp_api_id_error_response():
    return {
        "error": {
            "message": (
                "Unsupported post request. Object with ID '10217' does not exist,"
                "cannot be loaded due to missing "
                "permissions, or does not support this operation. "
                "Please read the Graph API documentation at "
                "https://developers.facebook.com/docs/graph-api"
            ),
            "type": "GraphMethodException",
            "code": 100,
            "error_subcode": 33,
            "fbtrace_id": "AdwFX9dbomdfT9Cj2tkSEoz",
        }
    }


def whatsapp_api_token_error_response():
    return {
        "error": {
            "message": "Invalid OAuth access token - Cannot parse access token",
            "type": "OAuthException",
            "code": 190,
            "fbtrace_id": "ABO7E5yYbQ2V1ffOa68W-Mf",
        }
    }
