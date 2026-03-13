from typing import Optional
from .base_repository import BaseRepository
from app.interfaces.consumer_interface import ConsumerInterface
from app.models.enums.already_exists import AlreadyExistsEnum
from ..models.consumer import Consumer
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

    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        query = "INSERT INTO password(hash) VALUES (%s) RETURNING id"
        params = (registration.password,)
        result = self._execute(query, params)
        password_id = result[0]["id"]

        query = "INSERT INTO consumer(username, email, password_id) VALUES (%s, %s, %s) RETURNING *"
        params = (registration.username, registration.email, password_id)
        result = self._execute(query, params)
        return Consumer(**result[0])

    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        query = "SELECT c.id, c.username, c.email, p.password FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.email = %s"
        params = (email,)
        result = self._execute(query, params)
        if result:
            return Consumer(**result[0])

        return None

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        query = "SELECT c.id, c.username, c.email, p.password FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.username = %s"
        params = (username,)
        result = self._execute(query, params)
        if result:
            return Consumer(**result[0])

        return None