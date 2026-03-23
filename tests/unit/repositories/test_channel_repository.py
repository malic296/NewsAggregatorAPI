import pytest
from app.core.errors import InternalError
from app.models import DBResult, Channel

@pytest.mark.parametrize(
    "db_result, expected_error",
    [
        (DBResult(True, None, None, 0), InternalError(internal_message="Query created by get_channels failed because: There are no saved channels in DB.")),
        (DBResult(False, "NONE", [], 0), InternalError(internal_message="Query created by get_channels failed because: NONE."))
    ]
)
def test_get_channels_fail(db_result, expected_error, mocker, channel_repository):
    mocker.patch.object(channel_repository, "_execute", return_value=db_result)

    with pytest.raises(type(expected_error)) as e:
        channel_repository.get_channels()

    assert str(e.value) == str(expected_error)

def test_get_channels_invalid_format(channel_repository, mocker):
    mocker.patch.object(channel_repository, "_execute", return_value=DBResult(True, None, [{"TEST_INVALID_KEY": 1}], 0))

    with pytest.raises(InternalError) as e:
        channel_repository.get_channels()

    assert "TEST_INVALID_KEY" in str(e.value)

def test_get_channels_success(channel_repository, mocker, db_result_channels):
    mocker.patch.object(channel_repository, "_execute", return_value=db_result_channels)

    channels: list[Channel] = channel_repository.get_channels()

    assert len(channels) == len(db_result_channels.data)
    assert channels == [Channel(**channel) for channel in db_result_channels.data]
