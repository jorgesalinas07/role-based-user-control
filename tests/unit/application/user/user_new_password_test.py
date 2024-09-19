from role_based_app.users.application.user_new_password import UserNewPassword


def test__user_new_password__was_called_correctly(mocker, user_new_password_factory):
    user_service = mocker.Mock()
    user_new_password_use_case = UserNewPassword(user_service=user_service)
    user_new_password = user_new_password_factory()
    user_new_password_use_case.execute(user_new_password)
    user_new_password_use_case.user_service.save_new_password.assert_called_with(
        user_new_password
    )
