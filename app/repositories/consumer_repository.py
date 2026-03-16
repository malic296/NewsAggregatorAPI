from typing import Optional
from .base_repository import BaseRepository
from app.interfaces.consumer_interface import ConsumerInterface
from app.models.enums.already_exists import AlreadyExistsEnum
from ..models.consumer import Consumer
from ..schemas.registration_dto import RegistrationDTO
import uuid

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

        query = "INSERT INTO consumer(username, email, password_id, uuid) VALUES (%s, %s, %s, %s) RETURNING id"
        params = (registration.username, registration.email, password_id, str(uuid.uuid4()))
        result = self._execute(query, params)
        if not result.success:
            raise Exception(f"Failed inserting consumer to db because: {result.error_message}")
        consumer_id = result.data[0]["id"]

        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email, p.hash AS password FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.id = %s"
        params = (consumer_id,)
        result = self._execute(query, params)
        if not result.success:
            raise Exception(f"Failed selecting consumer from db after creation because: {result.error_message}")
        return Consumer(**result.data[0])

    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.email = %s"
        params = (email,)
        result = self._execute(query, params)
        if not result.success: 
            raise Exception(f"Failed getting consumer from DB by email because: {result.error_message}")
        
        if result.data:
            return Consumer(**result.data[0])
        return None

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.username = %s"
        params = (username,)
        result = self._execute(query, params)
        if not result.success: 
            raise Exception(f"Failed getting consumer from DB by email because: {result.error_message}")
        if result.data:
            return Consumer(**result.data[0])

        return None
    
    def get_consumer_by_credential(self, credential: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.username = %s OR c.email = %s"
        params = (credential, credential, )

        result = self._execute(query, params)
        if not result.success: 
            raise Exception(f"Failed getting consumer from DB by credential {credential} because: {result.error_message}")
        if result.data:
            return Consumer(**result.data[0])

        return None
    
    def get_consumer_by_uuid(self, consumer_uuid: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.uuid = %s"
        params = (consumer_uuid, )

        result = self._execute(query, params)
        if not result.success: 
            raise Exception(f"Failed getting consumer from DB by public ID {consumer_uuid} because: {result.error_message}")
        if result.data:
            return Consumer(**result.data[0])

        return None
    
    def get_consumers_hash(self, uuid: str) -> str:
        query = """
            SELECT p.hash AS password from 
            consumer AS c 
            JOIN 
            password AS p 
            ON
            c.password_id = p.id
            WHERE 
            c.uuid = %s
        """
        params = (uuid, )

        result = self._execute(query=query, params=params)
        if not result.success: 
            raise Exception(f"Failed getting saved hash from DB by users public ID {uuid} because: {result.error_message}")
        if result.data:
            return result.data[0]["password"]

        return None