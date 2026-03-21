import redis
from app.services import CacheService
from app.models import Channel
import json
from dataclasses import asdict

def test_set_channels(mocker, mocked_redis):
    channels: list[Channel] = [
        Channel(1, "1", "title1", "link1"),
        Channel(2, "2", "title2", "link2")
    ]

    json_channels = json.dumps([asdict(channel) for channel in channels])

    service = CacheService()

    service.set_available_channels(channels)

    mocked_redis.setex.assert_called_once_with("data:available_channels", 1800, json_channels)

def test_get_channels(mocker, mocked_redis):
    channels: list[Channel] = [
        Channel(1, "1", "title1", "link1"),
        Channel(2, "2", "title2", "link2")
    ]

    json_channels = json.dumps([asdict(channel) for channel in channels])

    mocked_redis.get.return_value = json_channels

    service = CacheService()

    fetched_channels: list[Channel] = service.get_available_channels()

    assert fetched_channels == channels

    