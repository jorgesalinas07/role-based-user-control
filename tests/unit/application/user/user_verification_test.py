from role_based_app.users.application.user_verification import UserVerification


def test__user_verification__was_called_correctly(mocker, user_factory):
    user_service = mocker.Mock()
    user_verification = UserVerification(user_service=user_service)
    data = {
        "user": "user.username",
        "type": "email_confirmation",
    }

    user_verification.execute(data)

    user_verification.user_service.verification.assert_called_with(data)
