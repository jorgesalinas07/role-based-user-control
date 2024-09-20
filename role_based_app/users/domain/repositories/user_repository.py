from abc import ABC, abstractmethod
from typing import List, Optional

from role_based_app.users.domain.entities.user import UserDtoIn, UserDtoOut


class UserRepository(ABC):
    @abstractmethod
    def create(self, User: UserDtoIn) -> Optional[UserDtoOut]:
        pass

    @abstractmethod
    def create_many(self, user_list: List[UserDtoIn]) -> Optional[List[UserDtoOut]]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserDtoOut]:
        pass

    @abstractmethod
    def get_by_phone_number(self, phone_number: str) -> Optional[UserDtoOut]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[UserDtoOut]:
        pass

    @abstractmethod
    def update(self, user_id: str, user: UserDtoIn) -> Optional[UserDtoOut]:
        pass

    @abstractmethod
    def delete(self, user_id: str) -> Optional[UserDtoOut]:
        pass


class PhoneMessageRepository(ABC):
    @abstractmethod
    def send_phone_message_code(self, user: UserDtoIn):
        pass


class EmailMessageRepository(ABC):
    @abstractmethod
    def send_confirmation_email(self, user: UserDtoIn, token: str):
        pass


class TokenAuthenticationRepository(ABC):
    @abstractmethod
    def gen_verification_token(self, payload: dict) -> str:
        pass

    @abstractmethod
    def validate_code(self, token: str) -> Optional[dict]:
        pass


class OTPasswordRepository(ABC):
    @abstractmethod
    def get_otp(self, phone_number: str):
        pass
