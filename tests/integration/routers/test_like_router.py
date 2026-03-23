def test_like_article(test_client, mock_services, mocked_consumer):
    mock_services.db.like_article.return_value = True

    response = test_client.post("/latest/likes/like_article/", params={"article_uuid": "article"})
    json_response = response.json()

    mock_services.db.like_article.assert_called_once_with("article", mocked_consumer)

    assert json_response["status_code"] == 200
    assert json_response["message"] == "Article with uuid article has been liked."
    assert json_response["data"] == True
