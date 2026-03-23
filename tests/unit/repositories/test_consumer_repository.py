import pytest
from app.core.errors import InternalError
from app.schemas import RegistrationDTO
from app.models import Consumer

def test_register_consumer_success(consumer_repository, mocker, db_result_consumer):
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_consumer)

    registered_consumer = consumer_repository.register_consumer(RegistrationDTO(username="", email="", password=""))
    assert registered_consumer == Consumer(**db_result_consumer.data[0])

def test_register_consumer_error(consumer_repository, mocker, invalid_db_result):
    mocker.patch.object(consumer_repository, '_execute', return_value=invalid_db_result)

    with pytest.raises(InternalError) as e:
        consumer_repository.register_consumer(RegistrationDTO(username="", email="", password=""))

    assert str(e.value) == "Register query failed in register_consumer because: INVALID_DB_RESULT_MESSAGE"

def test_register_consumer_invalid_format(consumer_repository, mocker, db_result_none):
    db_result_none.data = [{"TEST_INVALID_KEY": 1}]
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_none)

    with pytest.raises(InternalError) as e:
        consumer_repository.register_consumer(RegistrationDTO(username="", email="", password=""))

    assert "TEST_INVALID_KEY" in str(e.value)

def test_get_consumer_by_email_success(consumer_repository, mocker, db_result_consumer):
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_consumer)

    registered_consumer = consumer_repository.get_consumer_by_email("")
    assert registered_consumer == Consumer(**db_result_consumer.data[0])

def test_get_consumer_by_email_error(consumer_repository, mocker, invalid_db_result):
    mocker.patch.object(consumer_repository, '_execute', return_value=invalid_db_result)

    with pytest.raises(InternalError) as e:
        consumer_repository.get_consumer_by_email("")

    assert str(e.value) == "Method get_consumer_by_email failed because: INVALID_DB_RESULT_MESSAGE"

def test_get_consumer_by_email_invalid_format(consumer_repository, mocker, db_result_none):
    db_result_none.data = [{"TEST_INVALID_KEY": 1}]
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_none)

    with pytest.raises(InternalError) as e:
        consumer_repository.get_consumer_by_email("")

    assert "TEST_INVALID_KEY" in str(e.value)

def test_get_consumer_by_username_success(consumer_repository, mocker, db_result_consumer):
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_consumer)

    registered_consumer = consumer_repository.get_consumer_by_username("")
    assert registered_consumer == Consumer(**db_result_consumer.data[0])

def test_get_consumer_by_username_error(consumer_repository, mocker, invalid_db_result):
    mocker.patch.object(consumer_repository, '_execute', return_value=invalid_db_result)

    with pytest.raises(InternalError) as e:
        consumer_repository.get_consumer_by_username("")

    assert str(e.value) == "Method get_consumer_by_username failed because: INVALID_DB_RESULT_MESSAGE"

def test_get_consumer_by_username_invalid_format(consumer_repository, mocker, db_result_none):
    db_result_none.data = [{"TEST_INVALID_KEY": 1}]
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_none)

    with pytest.raises(InternalError) as e:
        registered_consumer = consumer_repository.get_consumer_by_username("")

    assert "TEST_INVALID_KEY" in str(e.value)

def test_get_consumer_by_uuid_success(consumer_repository, mocker, db_result_consumer):
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_consumer)

    registered_consumer = consumer_repository.get_consumer_by_uuid("")
    assert registered_consumer == Consumer(**db_result_consumer.data[0])

def test_get_consumer_by_uuid_error(consumer_repository, mocker, invalid_db_result):
    mocker.patch.object(consumer_repository, '_execute', return_value=invalid_db_result)

    with pytest.raises(InternalError) as e:
        consumer_repository.get_consumer_by_uuid("")

    assert str(e.value) == "Method get_consumer_by_uuid failed because: INVALID_DB_RESULT_MESSAGE"

def test_get_consumer_by_uuid_invalid_format(consumer_repository, mocker, db_result_none):
    db_result_none.data = [{"TEST_INVALID_KEY": 1}]
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_none)

    with pytest.raises(InternalError) as e:
        consumer_repository.get_consumer_by_uuid("")

    assert "TEST_INVALID_KEY" in str(e.value)

def test_get_consumers_hash_success(consumer_repository, mocker, db_result_none):
    db_result_none.data = [{"hash": "1"}]
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_none)

    result = consumer_repository.get_consumers_hash(1)
    assert result == "1"

def test_get_consumers_hash_error(consumer_repository, mocker, invalid_db_result):
    mocker.patch.object(consumer_repository, '_execute', return_value=invalid_db_result)

    with pytest.raises(InternalError) as e:
        consumer_repository.get_consumers_hash(1)

    assert "Failed getting saved hash from DB by users ID 1 because: " + invalid_db_result.error_message == str(e.value)

def test_get_consumers_hash_invalid_format(consumer_repository, mocker, db_result_none):
    db_result_none.data = [{"TEST_INVALID_KEY": 1}]
    mocker.patch.object(consumer_repository, '_execute', return_value=db_result_none)

    with pytest.raises(InternalError) as e:
        consumer_repository.get_consumers_hash(1)

    assert "hash" in str(e.value)