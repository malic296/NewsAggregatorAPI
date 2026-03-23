from datetime import datetime, timezone
from app.models.article import Article

def test_get_articles(test_client, mock_services):
    mock_services.db.get_articles.return_value = [
        Article(
            id=1,
            uuid="1",
            title="TITLE_1",
            link="LINK_1",
            description="DESCRIPTION_1",
            pub_date=datetime.now(timezone.utc),
            channel_link="CHANNEL_LINK1",
            likes=1,
            liked_by_user=False
        )
    ]

    response = test_client.get("/latest/articles/", params={"hours": 2, "channel_ids": [1, 2]})
    json_data = response.json()

    assert response.status_code == 200
    assert json_data["message"] == "Articles fetched correctly"
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["title"] == "TITLE_1"
