from typing import Optional
from .base_repository import BaseRepository
from app.interfaces import ConsumerInterface
from app.models import Consumer, InternalError
from app.schemas import RegistrationDTO
import uuid

class ConsumerRepository(BaseRepository, ConsumerInterface):
    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        query = "INSERT INTO password(hash) VALUES (%s) RETURNING id"
        params = (registration.password,)
        result = self._execute(query, params)
        if not result.success:
            raise InternalError(
                internal_message=f"Failed saving password for consumer to db in method register_consumer because: {result.error_message}",
                public_message="Could not finish registration because server error."
            )
        password_id = result.data[0]["id"]

        query = "INSERT INTO consumer(username, email, password_id, uuid) VALUES (%s, %s, %s, %s) RETURNING id"
        params = (registration.username, registration.email, password_id, str(uuid.uuid4()))
        result = self._execute(query, params)
        if not result.success:
            raise InternalError(
                internal_message=f"Failed inserting consumer to db in method register_consumer because: {result.error_message}",
                public_message="Could not finish registration because server error."
            )
        consumer_id = result.data[0]["id"]

        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email, p.hash AS password FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.id = %s"
        params = (consumer_id,)
        result = self._execute(query, params)
        if not result.success:
            raise InternalError(
                internal_message=f"Failed reading consumer from db after creation in method register_consumer because: {result.error_message}",
                public_message="Could not finish registration because server error."
            )
        try:
            consumer: Consumer = Consumer(**result.data[0])
        except Exception as e:
            raise InternalError(
                internal_message=f"Failed mapping of db result data to consumer object in method register_consumer because: {result.error_message}",
                public_message="Could not finish registration because server error."
            )
        return consumer

    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.email = %s"
        params = (email,)
        result = self._execute(query, params)
        if not result.success: 
            raise InternalError(
                internal_message=f"Method get_consumer_by_email failed because: {result.error_message}",
                public_message="Could not retrieve user because of server error."
            )
        
        if result.data:
            try:
                consumer: Consumer = Consumer(**result.data[0])
            except Exception as e:
                raise InternalError(
                    internal_message=f"Failed mapping of db result data to consumer object in method get_consumer_by_email because: {result.error_message}",
                    public_message="Could not retrieve user because of server error."
                )
            return consumer
        return None

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.username = %s"
        params = (username,)
        result = self._execute(query, params)
        if not result.success: 
            raise InternalError(
                internal_message=f"Method get_consumer_by_username failed because: {result.error_message}",
                public_message="Could not retrieve user because of server error."
            )
        if result.data:
            try:
                consumer: Consumer = Consumer(**result.data[0])
            except Exception as e:
                raise InternalError(
                    internal_message=f"Failed mapping of db result data to consumer object in method get_consumer_by_email because: {result.error_message}",
                    public_message="Could not retrieve user because of server error."
                )
            return consumer

        return None
    
    def get_consumer_by_uuid(self, consumer_uuid: str) -> Consumer:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.uuid = %s"
        params = (consumer_uuid, )

        result = self._execute(query, params)
        if not result.success: 
            raise InternalError(
                internal_message=f"Method get_consumer_by_uuid failed because: {result.error_message}",
                public_message="Could not retrieve user because of server error."
            )

        try:
            consumer: Consumer = Consumer(**result.data[0])
        except Exception as e:
            raise InternalError(
                internal_message=f"Failed mapping of db result data to consumer object in method get_consumer_by_email because: {result.error_message}",
                public_message="Could not retrieve user because of server error."
            )
        return consumer
    
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
            raise InternalError(
                internal_message=f"Failed getting saved hash from DB by users public ID {uuid} because: {result.error_message}",
                public_message="Failed due to inconsistent DB."
            )
        
        try:
            password: str = result.data[0]["password"]
        except Exception as e:
            raise InternalError(
                internal_message=f"Method get_consumers_hash returned unexpected DB result. {e}.",
                public_message="Could not retrieve users info because of server error."
            )
        return password
