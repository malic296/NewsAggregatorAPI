from typing import Optional
from .base_repository import BaseRepository
from app.interfaces.consumer_interface import ConsumerInterface
from app.models.enums.already_exists import AlreadyExistsEnum
from ..schemas.registration_dto import RegistrationDTO


class ConsumerRepository(BaseRepository, ConsumerInterface):
    def is_username_or_email_used(self, username, email) -> Optional[AlreadyExistsEnum]:
        query = "SELECT * FROM consumer WHERE username = %s"
        params = (username, )
        result = self._execute(query, params)
        if len(result) > 0:
            return AlreadyExistsEnum.USERNAME

        query = "SELECT * FROM consumer WHERE email = %s"
        params = (email,)
        result = self._execute(query, params)
        if len(result) > 0:
            return AlreadyExistsEnum.EMAIL

        return None

    def register_user(self, registration: RegistrationDTO) -> None:
        query = "INSERT INTO password(hash) VALUES (%s) RETURNING id"
        params = (registration.password,)
        result = self._execute(query, params)
        password_id = result[0]["id"]

        query = "INSERT INTO consumer(username, email, password_id) VALUES (%s, %s, %s)"
        params = (registration.username, registration.email, password_id)
        self._execute(query, params)