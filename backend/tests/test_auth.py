from datetime import timedelta
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password

def test_password_hashing():
    password = "secretpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_generation_and_validation():
    subject = "user@example.com"
    token = create_access_token(subject=subject, expires_delta=timedelta(minutes=15))
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded_subject = decode_access_token(token)
    assert decoded_subject == subject

def test_invalid_jwt_token_returns_none():
    invalid_token = "invalid.jwt.token.string"
    assert decode_access_token(invalid_token) is None
