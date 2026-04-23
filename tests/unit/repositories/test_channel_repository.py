import pytest

from app.core.errors import DatabaseError, MappingError
from app.models import DBResult


def test_get_channels_success(channel_repository, mocker, db_result_channels):
    mocker.patch.object(channel_repository, "_execute", return_value=db_result_channels)

    channels = channel_repository.get_channels(user_id=1)

    assert len(channels) == 1
    assert channels[0].uuid == db_result_channels.data[0]["uuid"]


def test_get_channels_failure(channel_repository, mocker):
    mocker.patch.object(channel_repository, "_execute", return_value=DBResult(success=False, error_message="db failed"))

    with pytest.raises(DatabaseError) as exc:
        channel_repository.get_channels(user_id=1)

    assert exc.value.internal_message == "Query execution failed for method: get_channels. Error message: db failed"


def test_get_channels_mapping_error(channel_repository, mocker):
    mocker.patch.object(
        channel_repository,
        "_execute",
        return_value=DBResult(success=True, data=[{"uuid": "id-only"}], row_count=1),
    )

    with pytest.raises(MappingError) as exc:
        channel_repository.get_channels(user_id=1)

    assert "get_channels" in exc.value.internal_message


def test_set_disabled_channels_failure(channel_repository, mocker):
    mocker.patch.object(
        channel_repository,
        "_execute_transaction",
        return_value=DBResult(success=False, error_message="db failed"),
    )

    with pytest.raises(DatabaseError) as exc:
        channel_repository.set_disabled_channels_by_uuids(1, ["channel-uuid"])

    assert "set_disabled_channels_by_uuids" in exc.value.internal_message
