from fastapi import HTTPException


def check_error(response: dict):
    if response["statusCode"] >= 400:
        raise HTTPException(response["statusCode"], response["error"])
