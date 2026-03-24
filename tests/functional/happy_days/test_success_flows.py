import json
from app.main import app
from fastapi.testclient import TestClient
from app.schemas import RegistrationDTO

def test_successful_registration(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/latest/consumers/register/request_new_registration", json=RegistrationDTO(username="user", email="em", password="").model_dump())
    assert response.status_code == 200

    created_registration = cache_client.get("reg:em")
    data = json.loads(created_registration)
    code = int(data["code"])

    response = client.post("/latest/consumers/register/verify_email", params={"email": "em", "code": code})
    json_response = response.json()
    assert response.status_code == 200

    token = json_response["access_token"]
    token_type = json_response["token_type"]

    headers = {
        "Authorization": f"{token_type} {token}"
    }

    response = client.get("/latest/consumers/get_currently_logged_consumer", headers = headers)
    json_response = response.json()
    assert response.status_code == 200
    assert len(json_response["data"]) == 3
    assert json_response["data"]["username"] == "user"
    assert json_response["data"]["email"] == "em"

def test_reading_channels(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/latest/consumers/login", data={"username": "username", "password": "password"})
    json_response = response.json()
    assert response.status_code == 200

    token = json_response["access_token"]
    token_type = json_response["token_type"]

    headers = {
        "Authorization": f"{token_type} {token}"
    }

    response = client.get("/latest/channels/", headers=headers)
    json_response = response.json()
    assert response.status_code == 200
    assert len(json_response["data"]) == 2

def test_reading_articles(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/latest/consumers/login", data={"username": "username", "password": "password"})
    json_response = response.json()
    assert response.status_code == 200

    token = json_response["access_token"]
    token_type = json_response["token_type"]

    headers = {
        "Authorization": f"{token_type} {token}"
    }

    response = client.get("/latest/articles/", headers=headers, params={"hours": 1})
    json_response = response.json()
    assert response.status_code == 200
    assert len(json_response["data"]) == 2

    response = client.get("/latest/articles/", headers=headers, params={"hours": 15})
    json_response = response.json()
    assert response.status_code == 200
    assert len(json_response["data"]) == 3

    response = client.get("/latest/articles/", headers=headers, params={"channel_ids": [1]})
    json_response = response.json()
    assert response.status_code == 200
    assert len(json_response["data"]) == 1

def test_like_article(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/latest/consumers/login", data={"username": "username", "password": "password"})
    json_response = response.json()
    assert response.status_code == 200

    token = json_response["access_token"]
    token_type = json_response["token_type"]

    headers = {
        "Authorization": f"{token_type} {token}"
    }

    response = client.post("/latest/likes/like_article", headers=headers, params={"article_uuid": "ARTICLE_1"})
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["data"] == True

    response = client.get("/latest/articles/", headers=headers, params={"hours": 15})
    json_response = response.json()
    assert response.status_code == 200
    for article in json_response["data"]:
        if article["uuid"] == "ARTICLE_1":
            assert article["likes"] == 1
            assert article["liked_by_user"] is True
        else:
            assert article["likes"] == 0
            assert article["liked_by_user"] is not True
