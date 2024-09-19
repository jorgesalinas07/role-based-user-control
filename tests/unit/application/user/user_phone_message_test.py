from role_based_app.users.application.user_phone_message import UserPhoneMessage


def test__user_phone_message__was_called_correctly(mocker, user_factory):
    user_service = mocker.Mock()
    user_phone_message = UserPhoneMessage(user_service=user_service)
    user = user_factory()

    user_phone_message.execute(user)

    user_phone_message.user_service.send_phone_message_code.assert_called_with(user)
