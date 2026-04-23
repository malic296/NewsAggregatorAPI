def test_login_and_read_current_user(client):
    response = client.post("/v1/consumers/login", data={"username": "username", "password": "password"})
    assert response.status_code == 200

    token = response.json()["access_token"]
    response = client.get("/v1/consumers/me", headers={"Authorization": f"Bearer {token}"})
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["consumer"]["username"] == "username"
    assert json_response["consumer"]["email"] == "user@example.com"


def test_read_channels(client, auth_headers):
    response = client.get("/v1/channels/", headers=auth_headers)
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["success"] is True
    assert len(json_response["channels"]) == 1


def test_read_articles_and_like(client, auth_headers):
    response = client.get("/v1/articles/", headers=auth_headers, params={"hours": 1})
    json_response = response.json()

    assert response.status_code == 200
    assert len(json_response["articles"]) == 1

    response = client.post("/v1/articles/article-uuid/like", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["liked"] is True
