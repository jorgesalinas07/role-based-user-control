import json
import os
import typing

HEADERS = os.getenv("HEADERS", "application/json")
ORIGIN = os.getenv("ALLOWED_ORIGIN", "")
METHODS = os.getenv("METHODS", "")


class ControllerResponse:
    def __init__(self, status_code: int, body: typing.Union[dict, str]):
        self.status_code = status_code
        self.body = json.dumps(body, default=str)
        self.headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": f"{HEADERS}",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PATCH,DELETE",
        }

    def __str__(self):
        return str(
            {
                "statusCode": self.status_code,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Headers": f"{HEADERS}",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PATCH,DELETE",
                },
                "body": self.body,
            }
        )

    def __eq__(self, other):
        return self.status_code == other.status_code
