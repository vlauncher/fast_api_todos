import datetime
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    generate_otp
)

def test_password_hashing():
    password = "test_password_123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_generate_otp():
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()
    
    otp_custom = generate_otp(length=8)
    assert len(otp_custom) == 8
    assert otp_custom.isdigit()

def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Test with custom expiry
    from datetime import timedelta
    token_custom = create_access_token(data, expires_delta=timedelta(minutes=60))
    assert isinstance(token_custom, str)
    assert token_custom != token

def test_create_refresh_token():
    data = {"sub": "test@example.com"}
    token = create_refresh_token(data)
    assert isinstance(token, str)
    assert len(token) > 0

def test_token_decoding():
    from jose import jwt
    from app.core.config import SECRET_KEY, ALGORITHM
    
    data = {"sub": "test@example.com"}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    
    # Decode access token
    access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert access_payload["sub"] == "test@example.com"
    assert access_payload["type"] == "access"
    
    # Decode refresh token
    refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert refresh_payload["sub"] == "test@example.com"
    assert refresh_payload["type"] == "refresh"
