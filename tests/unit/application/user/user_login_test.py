from role_based_app.users.application.user_login import UserLogin


def test__user_login__was_called_correctly(mocker, user_login_factory):
    user_service = mocker.Mock()
    user_login_use_case = UserLogin(user_service=user_service)
    user_login = user_login_factory()

    user_login_use_case.execute(user_login)

    user_login_use_case.user_service.login.assert_called_with(user_login)
