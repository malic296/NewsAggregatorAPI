import pytest

from app.core.errors import DatabaseError, MappingError
from app.models import DBResult


def test_register_consumer_success(consumer_repository, mocker, db_result_consumer, registration_dto):
    mocker.patch.object(consumer_repository, "_execute", return_value=db_result_consumer)

    consumer = consumer_repository.register_consumer(registration_dto)

    assert consumer.uuid == db_result_consumer.data[0]["uuid"]


def test_get_consumer_by_email_returns_none(consumer_repository, mocker):
    mocker.patch.object(consumer_repository, "_execute", return_value=DBResult(success=True, data=[], row_count=0))

    assert consumer_repository.get_consumer_by_email("missing@example.com") is None


def test_get_consumer_by_username_failure(consumer_repository, mocker):
    mocker.patch.object(consumer_repository, "_execute", return_value=DBResult(success=False, error_message="db failed"))

    with pytest.raises(DatabaseError) as exc:
        consumer_repository.get_consumer_by_username("username")

    assert exc.value.internal_message == "Query execution failed for method: get_consumer_by_username. Error message: db failed"


def test_get_consumer_by_uuid_mapping_error(consumer_repository, mocker):
    mocker.patch.object(
        consumer_repository,
        "_execute",
        return_value=DBResult(success=True, data=[{"uuid": "consumer-uuid"}], row_count=1),
    )

    with pytest.raises(MappingError) as exc:
        consumer_repository.get_consumer_by_uuid("consumer-uuid")

    assert "get_consumer_by_uuid" in exc.value.internal_message


def test_get_consumers_hash_returns_none(consumer_repository, mocker):
    mocker.patch.object(consumer_repository, "_execute", return_value=DBResult(success=True, data=[], row_count=0))

    assert consumer_repository.get_consumers_hash(1) is None


def test_update_consumers_password_failure(consumer_repository, mocker):
    mocker.patch.object(consumer_repository, "_execute", return_value=DBResult(success=True, data=None, row_count=0))

    with pytest.raises(DatabaseError) as exc:
        consumer_repository.update_consumers_password(1, "new-hash")

    assert "update_consumers_password" in exc.value.internal_message
