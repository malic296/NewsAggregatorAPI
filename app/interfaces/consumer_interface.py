from abc import ABC, abstractmethod
from typing import Optional
from app.models import AlreadyExistsEnum, Consumer
from app.schemas import RegistrationDTO

class ConsumerInterface(ABC):
    @abstractmethod
    def is_username_or_email_used(self, username, email) -> Optional[AlreadyExistsEnum]:
        NotImplementedError("is_username_or_email_used method not implemented in consumer repository.")

    @abstractmethod
    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        NotImplementedError("register_consumer method not implemented in consumer repository.")

    @abstractmethod
    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        NotImplementedError("get_consumer_by_email method not implemented in consumer repository.")

    @abstractmethod
    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        NotImplementedError("get_consumer_by_username method not implemented in consumer repository.")

    @abstractmethod
    def get_consumer_by_credential(self, credential: str) -> Optional[Consumer]:
        NotImplementedError("get_consumer_by_credential method not implemented in consumer repository.")

    @abstractmethod
    def get_consumer_by_uuid(self, consumer_uuid: str) -> Optional[Consumer]:
        NotImplementedError("get_consumer_by_uuid method not implemented in consumer repository.")

    @abstractmethod
    def get_consumers_hash(self, uuid: str) -> str:
        NotImplementedError("get_consumers_hash method not implemented in consumer repository.")