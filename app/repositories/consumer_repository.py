from typing import Optional
from .base_repository import BaseRepository
from app.interfaces import ConsumerInterface
from app.models import Consumer
from app.core.errors import InternalError
from app.schemas import RegistrationDTO
import uuid

class ConsumerRepository(BaseRepository, ConsumerInterface):
    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        query = """
            WITH 
            new_password AS (
                INSERT INTO password(hash) VALUES (%s) RETURNING id, hash
            ),
            new_consumer AS (
                INSERT INTO consumer(username, email, password_id, uuid)
                SELECT %s, %s, id, %s FROM new_password
                RETURNING id, uuid, username, email, password_id
            )
            SELECT nc.id, nc.uuid, nc.username, nc.email
            FROM new_consumer nc
            JOIN new_password np ON nc.password_id = np.id;
        """
        params = (
            registration.password,
            registration.username,
            registration.email,
            str(uuid.uuid4())
        )
        result = self._execute(query, params)
        if not result.success:
            raise InternalError(
                internal_message=f"Register query failed in register_consumer because: {result.error_message}"
            )
        try:
            consumer: Consumer = Consumer(**result.data[0])
        except Exception as e:
            raise InternalError(
                internal_message=f"Failed mapping of db result data to consumer object in method register_consumer because: {e}"
            )
        return consumer

    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.email = %s"
        params = (email,)
        result = self._execute(query, params)
        if not result.success: 
            raise InternalError(
                internal_message=f"Method get_consumer_by_email failed because: {result.error_message}"
            )
        
        if result.data:
            try:
                consumer: Consumer = Consumer(**result.data[0])
            except Exception as e:
                raise InternalError(
                    internal_message=f"Failed mapping of db result data to consumer object in method get_consumer_by_email because: {e}"
                )
            return consumer
        return None

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.username = %s"
        params = (username,)
        result = self._execute(query, params)
        if not result.success: 
            raise InternalError(
                internal_message=f"Method get_consumer_by_username failed because: {result.error_message}"
            )
        if result.data:
            try:
                consumer: Consumer = Consumer(**result.data[0])
            except Exception as e:
                raise InternalError(
                    internal_message=f"Failed mapping of db result data to consumer object in method get_consumer_by_email because: {e}"
                )
            return consumer

        return None
    
    def get_consumer_by_uuid(self, consumer_uuid: str) -> Consumer:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.uuid = %s"
        params = (consumer_uuid, )

        result = self._execute(query, params)
        if not result.success: 
            raise InternalError(
                internal_message=f"Method get_consumer_by_uuid failed because: {result.error_message}"
            )

        try:
            consumer: Consumer = Consumer(**result.data[0])
        except Exception as e:
            raise InternalError(
                internal_message=f"Failed mapping of db result data to consumer object in method get_consumer_by_email because: {e}"
            )
        return consumer
    
    def get_consumers_hash(self, id: int) -> Optional[str]:
        query = """
            SELECT p.hash AS hash from 
            consumer AS c 
            JOIN 
            password AS p 
            ON
            c.password_id = p.id
            WHERE 
            c.id = %s
        """
        params = (id, )

        result = self._execute(query=query, params=params)
        if not result.success: 
            raise InternalError(
                internal_message=f"Failed getting saved hash from DB by users ID {id} because: {result.error_message}"
            )

        if not result.data:
            return None

        try:
            hash: str = result.data[0]["hash"]
        except Exception as e:
            raise InternalError(
                internal_message=f"Method get_consumers_hash returned unexpected DB result. {e}."
            )
        return hash
