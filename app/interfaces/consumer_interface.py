from abc import ABC, abstractmethod
from typing import Optional
from app.models import AlreadyExistsEnum, Consumer
from app.schemas import RegistrationDTO

class ConsumerInterface(ABC):
    @abstractmethod
    def is_username_or_email_used(self, username, email) -> Optional[AlreadyExistsEnum]:
        ...

    @abstractmethod
    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        ...

    @abstractmethod
    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        ...

    @abstractmethod
    def get_consumer_by_email(self, username: str) -> Optional[Consumer]:
        ...

    @abstractmethod
    def get_consumer_by_credential(self, credential: str) -> Optional[Consumer]:
        ...

    @abstractmethod
    def get_consumer_by_uuid(self, consumer_uuid: str) -> Optional[Consumer]:
        ...

    @abstractmethod
    def get_consumers_hash(self, uuid: str) -> Optional[str]:
        ...