from role_based_app.users.domain.entities.user import UserDtoOut, UserRole
from role_based_app.users.infrastructure.adapters.user_schema import User as UserModel


def parse_user_model_to_user_dto(user: UserModel):
    return UserDtoOut(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        roles=UserRole(**user.roles),
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_verified=user.is_verified,
        is_enabled=user.is_enabled,
        unable_at=user.unable_at,
        is_admin=user.is_admin,
    )


def authentication_phone_message_template(phone_number: str, otp: str):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "authentication_token",
            "language": {
                "code": "en_US"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": otp
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": otp
                        }
                    ]
                }
            ]
        }
    }
