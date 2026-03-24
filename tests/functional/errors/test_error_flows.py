from starlette.testclient import TestClient
from app.main import app

def test_not_authorized(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    test_client = TestClient(app, raise_server_exceptions=False)

    response = test_client.get("/latest/articles/")
    assert response.status_code == 401

    response = test_client.get("/latest/channels/")
    assert response.status_code == 401

    response = test_client.get("/latest/consumers/get_currently_logged_consumer")
    assert response.status_code == 401

    response = test_client.post("/latest/likes/like_article", params={"article_uuid": "1"})
    assert response.status_code == 401

def test_invalid_article_uuid(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/latest/consumers/login", data={"username": "username", "password": "password"})
    json_response = response.json()
    assert response.status_code == 200

    token = json_response["access_token"]
    token_type = json_response["token_type"]

    headers = {
        "Authorization": f"{token_type} {token}"
    }

    invalid_uuid = "#####"
    response = client.post("/latest/likes/like_article", params={"article_uuid": invalid_uuid}, headers=headers)
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["message"] == f"No article found for provided uuid: {invalid_uuid}"

def test_invalid_login_credential(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    client = TestClient(app, raise_server_exceptions=False)

    invalid_username = "test"
    response = client.post("/latest/consumers/login", data={"username": invalid_username, "password": "password"})
    json_response = response.json()
    assert json_response["success"] == False
    assert json_response["message"] == f"No consumer found with provided credential: {invalid_username}."

def test_invalid_login_password(redis_container_setup, postgres_container_setup, db_connection, cache_client, email_mock):
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/latest/consumers/login", data={"username": "username", "password": "test"})
    json_response = response.json()
    assert json_response["success"] == False
    assert json_response["message"] == "Invalid login credentials."

