from app.models import Channel
import json
from dataclasses import asdict

def test_is_registration_pending(mocked_redis, cache_service, registration_dto):
    mocked_redis.exists.return_value = 0
    is_pending = cache_service.is_registration_pending(registration_dto)
    assert not is_pending

    mocked_redis.exists.return_value = 1
    is_pending = cache_service.is_registration_pending(registration_dto)
    assert is_pending

def test_delete_registration_from_pending(mocked_redis, cache_service, registration_dto):
    mocked_redis.exists.return_value = 0
    cache_service.delete_registration_from_pending(registration_dto)
    mocked_redis.delete.assert_not_called()

    mocked_redis.exists.return_value = 1
    cache_service.delete_registration_from_pending(registration_dto)
    mocked_redis.delete.assert_called_once_with("reg:" + registration_dto.email)

def test_create_pending_registration(mocked_redis, cache_service, registration_dto):
    code = 111111
    dict_data: dict = {
        "code": code,
        "data": registration_dto.model_dump()
    }

    mocked_redis.exists.return_value = 0
    
    cache_service.create_pending_registration(registration=registration_dto, code=code)

    mocked_redis.setex.assert_called_once_with("reg:" + registration_dto.email, 120, json.dumps(dict_data))

def test_provided_code_correct(mocked_redis, cache_service, registration_dto):
    code = 111111
    dict_data: dict = {
        "code": code,
        "data": registration_dto.model_dump()
    }

    mocked_redis.get.return_value = json.dumps(dict_data)

    result = cache_service.provided_code_correct("", 111111)
    assert result == registration_dto

    result = cache_service.provided_code_correct("", 222222)
    assert result == None


def test_set_channels(mocked_redis, cache_service):
    channels: list[Channel] = [
        Channel(1, "1", "title1", "link1"),
        Channel(2, "2", "title2", "link2")
    ]

    json_channels = json.dumps([asdict(channel) for channel in channels])

    cache_service.set_available_channels(channels)

    mocked_redis.setex.assert_called_once_with("data:available_channels", 1800, json_channels)

def test_get_channels(mocked_redis, cache_service):
    channels: list[Channel] = [
        Channel(1, "1", "title1", "link1"),
        Channel(2, "2", "title2", "link2")
    ]

    json_channels = json.dumps([asdict(channel) for channel in channels])

    mocked_redis.get.return_value = json_channels

    fetched_channels: list[Channel] = cache_service.get_available_channels()

    assert fetched_channels == channels


    