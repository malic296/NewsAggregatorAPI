from app.models.channel import Channel
from app.schemas import ChannelDTO
from dataclasses import asdict

def test_get_channels(test_client, mock_services):
    test_channel = Channel(id=1, uuid="1", title="TITLE_1", link="LINK_1")
    mock_services.cache.get_available_channels.return_value = []
    mock_services.db.get_channels.return_value = [test_channel]

    response = test_client.get("/latest/channels/")
    json_data = response.json()

    mock_services.cache.set_available_channels.assert_called_once_with([test_channel])

    assert response.status_code == 200
    assert json_data["message"] == "Channels fetched correctly"
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert ChannelDTO(**asdict(test_channel)) == ChannelDTO(**json_data["data"][0])
