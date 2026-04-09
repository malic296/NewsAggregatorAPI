from abc import ABC, abstractmethod
from typing import Optional
from app.models import Consumer
from app.schemas import RegistrationDTO

class ConsumerInterface(ABC):
    @abstractmethod
    def register_consumer(self, registration: RegistrationDTO) -> Consumer:
        ...

    @abstractmethod
    def get_consumer_by_email(self, email: str) -> Optional[Consumer]:
        ...

    @abstractmethod
    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        ...

    @abstractmethod
    def get_consumer_by_uuid(self, consumer_uuid: str) -> Consumer:
        ...

    @abstractmethod
    def get_consumers_hash(self, uuid: str) -> str:
        ...

    @abstractmethod
    def update_consumers_username(self, user_id: int, new_username: str) -> Consumer:
        ...

    @abstractmethod
    def update_consumers_password(self, user_id: int, new_hash: str) -> Consumer:
        ...
