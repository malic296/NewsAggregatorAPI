import pytest
from fastapi.security import OAuth2PasswordRequestForm
from starlette.testclient import TestClient

from app.core.errors import InternalError
from app.schemas import RegistrationDTO
from dataclasses import asdict

def test_request_new_registration(test_client, mock_services):
    registration_dto = RegistrationDTO(username="username", email="email", password="password")
    mock_services.cache.is_registration_pending.return_value = False

    response = test_client.post("/latest/consumers/register/request_new_registration", json=registration_dto.model_dump())
    json_response = response.json()

    mock_services.cache.delete_registration_from_pending.assert_not_called()

    assert response.status_code == 200
    assert json_response["message"] == "New pending registration created."
    assert json_response["success"] == True

def test_request_pending_registration(test_client, mock_services):
    registration_dto = RegistrationDTO(username="username", email="email", password="password")
    mock_services.cache.is_registration_pending.return_value = True

    response = test_client.post("/latest/consumers/register/request_new_registration", json=registration_dto.model_dump())
    json_response = response.json()

    mock_services.cache.delete_registration_from_pending.assert_called_once()

    assert response.status_code == 200
    assert json_response["message"] == "New pending registration created."
    assert json_response["success"] == True

def test_verify_email_correct(test_client, mock_services):
    mock_services.cache.provided_code_correct.return_value = RegistrationDTO(username="username", email="email", password="password")
    mock_services.security.create_access_token.return_value = "#####"

    response = test_client.post("/latest/consumers/register/verify_email", params={"email": "email", "code": 123456})
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["token_type"] == "Bearer"
    assert json_response["access_token"] == "#####"

def test_verify_email_invalid(test_client, mock_services):
    mock_services.cache.provided_code_correct.return_value = None

    response = test_client.post("/latest/consumers/register/verify_email", params={"email": "email", "code": 123456})
    json_response = response.json()

    assert response.status_code == 400
    assert json_response["success"] == False
    assert json_response["message"] == "Expired registration request or Invalid code."

def test_login(test_client_without_jwt, mock_services, mocked_consumer):
    mock_services.db.get_consumer_by_credential.return_value = mocked_consumer
    mock_services.security.create_access_token.return_value = "#####"

    response = test_client_without_jwt.post("/latest/consumers/login", data={"username": mocked_consumer.username,"password": "test_password"})
    json_response = response.json()

    mock_services.security.create_access_token.assert_called_once_with({"uuid": mocked_consumer.uuid, "username": mocked_consumer.username, "email": mocked_consumer.email})
    assert response.status_code == 200
    assert json_response["token_type"] == "Bearer"
    assert json_response["access_token"] == "#####"

def test_get_currently_logged_consumer(test_client):
    response = test_client.get("/latest/consumers/get_currently_logged_consumer")
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["success"] == True
    assert json_response["message"] == "Current user fetched successfully."
    assert json_response["data"] == {
        "uuid": "1",
        "email": "email",
        "username": "username"
    }

def test_get_currently_logged_consumer_no_token(test_client_without_jwt):
    response = test_client_without_jwt.get("/latest/consumers/get_currently_logged_consumer", headers={"Authorization": "BEARER"})
    json_response = response.json()

    assert response.status_code == 401
    assert json_response["success"] == False
    assert json_response["message"] == "You need to login or register first to use this endpoint."