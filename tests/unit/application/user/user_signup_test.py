from role_based_app.users.application.user_signup import UserSignUp


def test__user_sign_up__was_called_correctly(mocker, user_factory):
    user_service = mocker.Mock()
    user_sign_up = UserSignUp(user_service=user_service)
    user = user_factory()

    user_sign_up.execute(user)

    user_sign_up.user_service.signup.assert_called_with(user)
