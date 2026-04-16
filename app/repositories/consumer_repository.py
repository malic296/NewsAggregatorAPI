from typing import Optional
from .base_repository import BaseRepository
from app.interfaces import ConsumerInterface
from app.models import Consumer
from app.core.errors import DatabaseError, MappingError
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
        db_result = self._execute(query, params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="register_consumer"
            )
        try:
            return Consumer(**db_result.data[0])
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="register_consumer")

    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.email = %s"
        params = (email,)
        db_result = self._execute(query, params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_consumer_by_email"
            )
        
        if db_result.data:
            try:
                return Consumer(**db_result.data[0])
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="get_consumer_by_email")
        return None

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.username = %s"
        params = (username,)
        db_result = self._execute(query, params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_consumer_by_username"
            )
        if db_result.data:
            try:
                return Consumer(**db_result.data[0])
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="get_consumer_by_username")

        return None
    
    def get_consumer_by_uuid(self, consumer_uuid: str) -> Consumer:
        query = "SELECT c.id AS id, c.uuid AS uuid, c.username AS username, c.email AS email FROM consumer AS c JOIN password as p ON c.password_id = p.id WHERE c.uuid = %s"
        params = (consumer_uuid, )

        db_result = self._execute(query, params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_consumer_by_uuid"
            )

        try:
            return Consumer(**db_result.data[0])
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_consumer_by_uuid")
    
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

        db_result = self._execute(query=query, params=params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_consumers_hash"
            )

        if not db_result.data:
            return None

        try:
            return db_result.data[0]["hash"]
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_consumers_hash")

    def update_consumers_username(self, user_id: int, new_username: str) -> None:
        sql = """
            UPDATE consumer
            SET username = %s
            WHERE consumer.id = %s
        """
        params = (new_username, user_id, )

        db_result = self._execute(query=sql, params=params)

        if not db_result.success or db_result.row_count != 1:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Username has not been changed.",
                method="update_consumers_username"
            )

    def update_consumers_password(self, user_id: int, new_hash: str) -> None:
        sql = """
              UPDATE password
              SET hash = %s
              WHERE password.id = (SELECT password_id FROM consumer WHERE id = %s)
        """
        params = (new_hash, user_id, )

        db_result = self._execute(query=sql, params=params)

        if not db_result.success or db_result.row_count != 1:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Password has not been updated.",
                method="update_consumers_password"
            )