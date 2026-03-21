import pytest
from app.core.errors import InternalError
from fastapi import status

def test_password_hashing(security_service, monkeypatch):
    monkeypatch.setenv("PEPPER", "test")
    monkeypatch.setenv("JWT_SECRET", "test")

    password = "test_password"
    hash = security_service.get_password_hash(password)

    random_password = "random_password"

    security_service.verify_password(hash, password)

    with pytest.raises(InternalError) as e:
        security_service.verify_password(hash, random_password)

    assert e.value.public_message == "Invalid login credentials."
    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_jwt_encoding(security_service, monkeypatch):
    monkeypatch.setenv("PEPPER", "test")
    monkeypatch.setenv("JWT_SECRET", "test")

    claims = {
        "test1": 1,
        "test2": 2
    }

    token = security_service.create_access_token(claims)

    decoded_claims = security_service.decode_access_token(token)

    for key, value in claims.items():
        assert value == decoded_claims[key]

    assert "exp" in decoded_claims.keys()