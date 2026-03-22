from app.models import Article, Consumer, Channel
from datetime import datetime
import pytest
from fastapi import status
from app.core.errors import InternalError

def test_get_articles(mocker, db_service):
    articles = [Article(1, "1", "test", "test", "test", datetime.now(), "https://test", 10, True)]
    mocker.patch.object(db_service.articles, "get_articles", return_value=articles)

    result = db_service.get_articles(Consumer(1, "1", "consumer", "email"))

    assert result == articles
    db_service.articles.get_articles.assert_called_once()

def test_get_channels(mocker, db_service):
    channels = [Channel(1, "1", "title", "link")]
    mocker.patch.object(db_service.channels, "get_channels", return_value=channels)

    result = db_service.get_channels()

    assert result == channels
    db_service.channels.get_channels.assert_called_once()

@pytest.mark.parametrize(
    "email_consumer, username_consumer, error, email, username",
    [
        (Consumer(1, "", "", ""), None, InternalError(public_message=f"Email already used: e.",status_code=status.HTTP_400_BAD_REQUEST), "e", "u"),
        (None, Consumer(1, "", "", ""), InternalError(public_message=f"Username already used: u.",status_code=status.HTTP_400_BAD_REQUEST), "e", "u"),
        (None, None, None, "", "")
    ]
    
)
def test_username_or_email_used(db_service, mocker, email_consumer, username_consumer, error, email, username):
    mocker.patch.object(db_service.consumers, "get_consumer_by_email", return_value=email_consumer)
    mocker.patch.object(db_service.consumers, "get_consumer_by_username", return_value=username_consumer)
    if error:
        with pytest.raises(InternalError) as e:
            db_service.is_username_or_email_used(email=email, username=username)

        raised_error = e.value
        assert type(raised_error) == type(error)
        assert raised_error.public_message == error.public_message
        assert raised_error.status_code == error.status_code

    else:
        result = db_service.is_username_or_email_used(email=email, username=username)
        assert result == None

def test_register_consumer(mocker, db_service, registration_dto):
    consumer: Consumer = Consumer(1, "1", registration_dto.username, registration_dto.email)
    mocker.patch.object(db_service.consumers, "register_consumer", return_value=consumer)

    returned_consumer = db_service.register_consumer(registration_dto)

    assert returned_consumer == consumer
    db_service.consumers.register_consumer.assert_called_once()

@pytest.mark.parametrize(
    "credential, email_consumer, username_consumer, error",
    [
        ("", Consumer(1, "", "", ""), None, None),
        ("", None, Consumer(1, "", "", ""), None),
        ("", None, None, InternalError(public_message=f"No consumer found with provided credential: .", status_code=status.HTTP_400_BAD_REQUEST))
    ]
)
def test_get_consumer_by_credential(mocker, db_service, credential, email_consumer, username_consumer, error):
    mocker.patch.object(db_service.consumers, "get_consumer_by_username", return_value=username_consumer)
    mocker.patch.object(db_service.consumers, "get_consumer_by_email", return_value=email_consumer)
    if error:
        with pytest.raises(InternalError) as e:
            db_service.get_consumer_by_credential(credential)

        assert type(e.value) == type(error)
        assert e.value.public_message == error.public_message
        assert e.value.status_code == error.status_code

    else:
        result = db_service.get_consumer_by_credential(credential)
        assert result == email_consumer or result == username_consumer

@pytest.mark.parametrize(
    "hash, error, id",
    [
        (None, InternalError(internal_message=f"No hash found for consumers id: {1}"), 1),
        ("hash", None, 1)
    ]
)
def test_get_consumers_hash(mocker, db_service, hash, error, id):
    mocker.patch.object(db_service.consumers, "get_consumers_hash", return_value=hash)
    if error:
        with pytest.raises(InternalError) as e:
            db_service.get_consumers_hash(id)

        assert type(e.value) == type(error)
        assert e.value.internal_message == error.internal_message
        assert e.value.status_code == error.status_code

    else:
        result = db_service.get_consumers_hash(id)
        assert result == hash

@pytest.mark.parametrize(
    "id, error, uuid",
    [
        (1, None, "###"), 
        (None, InternalError(public_message=f"No article found for provided uuid: ###",status_code=status.HTTP_400_BAD_REQUEST), "###")
    ]
)
def test_like_article(mocker, db_service, id, error, uuid):
    mocker.patch.object(db_service.articles, "article_uuid_to_id", return_value= id)
    mocker.patch.object(db_service.articles, "like_article", return_value= True)
    consumer: Consumer = Consumer(1, "", "", "")

    if error: 
        with pytest.raises(InternalError) as e:
            db_service.like_article(uuid, consumer)

        assert type(e.value) == type(error)
        assert e.value.public_message == error.public_message
        assert e.value.status_code == error.status_code
        db_service.articles.like_article.assert_not_called()

    else:
        result = db_service.like_article(uuid, consumer)
        assert result == True
        db_service.articles.like_article.assert_called_once_with(article_id=id, consumer_id=consumer.id)
