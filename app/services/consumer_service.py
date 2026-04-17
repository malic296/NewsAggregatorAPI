from typing import Optional
from app.models import Consumer
from app.schemas import RegistrationDTO, UpdateCredentialsDTO
from app.repositories import ConsumerRepository
from app.core.errors import RegistrationExpiredError, EmailAlreadyUsedError, UsernameAlreadyUsedError
from .cache_service import CacheService

class ConsumerService:
    def __init__(self, consumers: ConsumerRepository, cache: CacheService):
        self.consumers = consumers
        self.cache = cache

    def is_email_used(self, email: str) -> bool:
        consumer = self.consumers.get_consumer_by_email(email)
        if consumer:
            return True

        return False

    def is_username_used(self, username: str) -> bool:
        consumer = self.consumers.get_consumer_by_username(username)
        if consumer:
            return True

        return False

    def validate_new_registration(self, registration: RegistrationDTO) -> None:
        consumer = self.consumers.get_consumer_by_email(email=registration.email)
        if consumer:
            raise EmailAlreadyUsedError()

        consumer = self.consumers.get_consumer_by_username(username=registration.username)
        if consumer:
            raise UsernameAlreadyUsedError()

    def create_new_registration(self, registration: RegistrationDTO, code: int) -> None:
        is_pending = self.cache.is_registration_pending(registration)
        if is_pending:
            self.cache.delete_registration_from_pending(registration)

        self.cache.create_pending_registration(registration, code)

    def register_consumer(self, email: str, code: int) -> Consumer:
        registration = self.cache.provided_code_correct(email=email, code=code)
        if registration:
            return self.consumers.register_consumer(registration)
        else:
            raise RegistrationExpiredError()

    def get_consumer_by_credential(self, credential: str) -> Optional[Consumer]:
        consumer = self.consumers.get_consumer_by_username(credential)
        if not consumer:
            consumer = self.consumers.get_consumer_by_email(credential)

        return consumer

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        return self.consumers.get_consumer_by_username(username)

    def get_consumers_hash(self, id: int) -> Optional[str]:
        return self.consumers.get_consumers_hash(id)

    def update_credentials(self, request: UpdateCredentialsDTO, user: Consumer):
        if request.new_username:
            self.consumers.update_consumers_username(user_id=user.id, new_username=request.new_username)
            user.username = request.new_username

        if request.new_password:
            self.consumers.update_consumers_password(user_id=user.id, new_hash=request.new_password)

        return user

