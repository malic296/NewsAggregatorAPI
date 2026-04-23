def test_password_hashing(security_service):
    password = "test_password"
    hashed = security_service.get_password_hash(password)

    assert security_service.verify_password(hashed, password) is True
    assert security_service.verify_password(hashed, "wrong-password") is False


def test_password_identity_check(security_service):
    hashed = security_service.get_password_hash("test_password")

    assert security_service.is_password_identical_to_hash(hashed, "test_password") is True
    assert security_service.is_password_identical_to_hash(hashed, "wrong-password") is False


def test_jwt_encoding_and_decoding(security_service, consumer):
    token = security_service.create_access_token(consumer)
    decoded_claims = security_service.decode_access_token(token)

    assert decoded_claims["uuid"] == consumer.uuid
    assert decoded_claims["username"] == consumer.username
    assert decoded_claims["email"] == consumer.email
    assert "exp" in decoded_claims
