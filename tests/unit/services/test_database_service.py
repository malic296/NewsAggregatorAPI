import pytest

from app.core.errors import (
    ArticleNotFoundError,
    EmailAlreadyUsedError,
    InvalidCredentialsError,
    InvalidCurrentPasswordError,
    PasswordReuseError,
    RegistrationExpiredError,
    UsernameAlreadyUsedError,
)
from app.services import ArticleService, ChannelService, ConsumerService


def test_article_service_reads_from_repository(mocker, consumer, article):
    articles_repo = mocker.Mock()
    cache = mocker.Mock()
    service = ArticleService(articles=articles_repo, cache=cache)
    articles_repo.get_articles.return_value = [article]

    result = service.get_articles(consumer=consumer, hours=2)

    assert result == [article]
    articles_repo.get_articles.assert_called_once_with(consumer=consumer, hours=2)


def test_article_service_caches_fetched_article(mocker, article):
    articles_repo = mocker.Mock()
    cache = mocker.Mock()
    cache.get_article.return_value = None
    articles_repo.get_article.return_value = article
    service = ArticleService(articles=articles_repo, cache=cache)

    result = service.get_article("article-uuid")

    assert result == article
    cache.set_article.assert_called_once_with(article=article)


def test_article_service_like_raises_for_missing_article(mocker, consumer):
    articles_repo = mocker.Mock()
    articles_repo.article_uuid_to_id.return_value = None
    service = ArticleService(articles=articles_repo, cache=mocker.Mock())

    with pytest.raises(ArticleNotFoundError):
        service.like_article("missing-uuid", consumer)


def test_channel_service_prefers_cache(mocker, channel):
    cache = mocker.Mock()
    cache.get_available_channels.return_value = [channel]
    repository = mocker.Mock()
    service = ChannelService(channels=repository, cache=cache, scraping_service=None)

    result = service.get_channels(user_id=1)

    assert result == [channel]
    repository.get_channels.assert_not_called()


def test_channel_service_updates_disabled_channels(mocker):
    cache = mocker.Mock()
    repository = mocker.Mock()
    service = ChannelService(channels=repository, cache=cache, scraping_service=None)
    disabled_channels = [mocker.Mock(uuid="channel-uuid")]

    service.set_disabled_channels(1, disabled_channels)

    cache.invalidate_cache_channels.assert_called_once_with(user_id=1)
    repository.set_disabled_channels_by_uuids.assert_called_once_with(1, ["channel-uuid"])


def test_consumer_service_validate_new_registration(mocker, registration_dto):
    consumers = mocker.Mock()
    consumers.get_consumer_by_email.return_value = None
    consumers.get_consumer_by_username.return_value = None
    service = ConsumerService(consumers=consumers, cache=mocker.Mock(), security=mocker.Mock(), email=mocker.Mock())

    service.validate_new_registration(registration_dto)


def test_consumer_service_rejects_duplicate_email(mocker, registration_dto, consumer):
    consumers = mocker.Mock()
    consumers.get_consumer_by_email.return_value = consumer
    service = ConsumerService(consumers=consumers, cache=mocker.Mock(), security=mocker.Mock(), email=mocker.Mock())

    with pytest.raises(EmailAlreadyUsedError):
        service.validate_new_registration(registration_dto)


def test_consumer_service_rejects_duplicate_username(mocker, registration_dto, consumer):
    consumers = mocker.Mock()
    consumers.get_consumer_by_email.return_value = None
    consumers.get_consumer_by_username.return_value = consumer
    service = ConsumerService(consumers=consumers, cache=mocker.Mock(), security=mocker.Mock(), email=mocker.Mock())

    with pytest.raises(UsernameAlreadyUsedError):
        service.validate_new_registration(registration_dto)


def test_consumer_service_registration_expired(mocker):
    cache = mocker.Mock()
    cache.provided_code_correct.return_value = None
    service = ConsumerService(consumers=mocker.Mock(), cache=cache, security=mocker.Mock(), email=mocker.Mock())

    with pytest.raises(RegistrationExpiredError):
        service.register_consumer("user@example.com", 111111)


def test_consumer_service_authenticate_invalid_credential(mocker):
    service = ConsumerService(consumers=mocker.Mock(), cache=mocker.Mock(), security=mocker.Mock(), email=mocker.Mock())
    service.get_consumer_by_credential = mocker.Mock(return_value=None)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate("username", "password")


def test_consumer_service_authenticate_invalid_password(mocker, consumer):
    security = mocker.Mock()
    security.verify_password.return_value = False
    service = ConsumerService(consumers=mocker.Mock(), cache=mocker.Mock(), security=security, email=mocker.Mock())
    service.get_consumer_by_credential = mocker.Mock(return_value=consumer)
    service.get_consumers_hash = mocker.Mock(return_value="saved-hash")

    with pytest.raises(InvalidCredentialsError):
        service.authenticate("username", "password")


def test_consumer_service_update_credentials_invalid_current_password(mocker, consumer, update_credentials_dto):
    security = mocker.Mock()
    security.verify_password.return_value = False
    service = ConsumerService(consumers=mocker.Mock(), cache=mocker.Mock(), security=security, email=mocker.Mock())
    service.get_consumers_hash = mocker.Mock(return_value="saved-hash")

    with pytest.raises(InvalidCurrentPasswordError):
        service.update_credentials_and_issue_token(update_credentials_dto, consumer)


def test_consumer_service_prevents_password_reuse(mocker, consumer, update_credentials_dto):
    security = mocker.Mock()
    security.verify_password.return_value = True
    security.is_password_identical_to_hash.return_value = True
    service = ConsumerService(consumers=mocker.Mock(), cache=mocker.Mock(), security=security, email=mocker.Mock())
    service.get_consumers_hash = mocker.Mock(return_value="saved-hash")

    with pytest.raises(PasswordReuseError):
        service.update_credentials_and_issue_token(update_credentials_dto, consumer)
