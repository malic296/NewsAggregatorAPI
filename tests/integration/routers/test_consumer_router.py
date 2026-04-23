def test_request_registration(test_client, mock_services):
    payload = {"username": "username", "email": "user@example.com", "password": "password"}

    response = test_client.post("/v1/consumers/register", json=payload)
    json_response = response.json()

    mock_services.consumer_service.request_registration.assert_called_once()
    assert response.status_code == 200
    assert json_response == {
        "success": True,
        "message": "New pending registration created.",
    }


def test_verify_registration(test_client, mock_services):
    mock_services.consumer_service.verify_registration.return_value = "token"

    response = test_client.post("/v1/consumers/verification", params={"email": "user@example.com", "code": 123456})
    json_response = response.json()

    mock_services.consumer_service.verify_registration.assert_called_once_with(
        email="user@example.com",
        code=123456,
    )
    assert response.status_code == 200
    assert json_response == {"access_token": "token", "token_type": "Bearer"}


def test_login(unauthenticated_client, mock_services):
    mock_services.consumer_service.authenticate.return_value = "token"

    response = unauthenticated_client.post(
        "/v1/consumers/login",
        data={"username": "username", "password": "password"},
    )
    json_response = response.json()

    mock_services.consumer_service.authenticate.assert_called_once_with("username", "password")
    assert response.status_code == 200
    assert json_response == {"access_token": "token", "token_type": "Bearer"}


def test_get_current_user(test_client):
    response = test_client.get("/v1/consumers/me")
    json_response = response.json()

    assert response.status_code == 200
    assert json_response == {
        "success": True,
        "message": "Current user fetched successfully.",
        "consumer": {
            "uuid": "consumer-uuid",
            "username": "username",
            "email": "user@example.com",
        },
    }


def test_update_credentials(test_client, mock_services):
    mock_services.consumer_service.update_credentials_and_issue_token.return_value = "new-token"

    response = test_client.put(
        "/v1/consumers/credentials",
        json={"old_password": "old-password", "new_password": "new-password", "new_username": "new-username"},
    )
    json_response = response.json()

    mock_services.consumer_service.update_credentials_and_issue_token.assert_called_once()
    assert response.status_code == 200
    assert json_response == {"access_token": "new-token", "token_type": "Bearer"}
