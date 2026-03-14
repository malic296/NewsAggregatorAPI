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
        if not result.success:
            raise Exception(f"Failed getting consumer by username because: {result.error_message}")
        if len(result.data) > 0:
            return AlreadyExistsEnum.USERNAME

        query = "SELECT * FROM consumer WHERE email = %s"
        params = (email,)
        result = self._execute(query, params)
        if not result.success:
            raise Exception(f"Failed getting consumer by email because: {result.error_message}")
        if len(result.data) > 0:
            return AlreadyExistsEnum.EMAIL

        return None

    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        query = "INSERT INTO password(hash) VALUES (%s) RETURNING id"
        params = (registration.password,)
        result = self._execute(query, params)
        if not result.success:
            raise Exception(f"Failed saving password for consumer to db because: {result.error_message}")
        password_id = result.data[0]["id"]

        query = "INSERT INTO consumer(username, email, password_id) VALUES (%s, %s, %s) RETURNING id"
        params = (registration.username, registration.email, password_id)
        result = self._execute(query, params)
        if not result.success:
            raise Exception(f"Failed inserting consumer to db because: {result.error_message}")
        consumer_id = result.data[0]["id"]

        query = "SELECT c.id AS id, c.username AS username, c.email AS email, p.hash AS password FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.id = %s"
        params = (consumer_id,)
        result = self._execute(query, params)
        if not result.success:
            raise Exception(f"Failed selecting consumer from db after creation because: {result.error_message}")
        return Consumer(**result.data[0])

    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.username AS username, c.email AS email, p.hash AS password FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.email = %s"
        params = (email,)
        result = self._execute(query, params)
        if not result.success: 
            raise Exception(f"Failed getting consumer from DB by email because: {result.error_message}")
        
        if result.data:
            return Consumer(**result.data[0])
        return None

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.username AS username, c.email AS email, p.hash AS password FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.username = %s"
        params = (username,)
        result = self._execute(query, params)
        if not result.success: 
            raise Exception(f"Failed getting consumer from DB by email because: {result.error_message}")
        if result.data:
            return Consumer(**result.data[0])

        return None