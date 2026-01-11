import os
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, DATABASE_URL

def test_config_values():
    assert SECRET_KEY is not None
    assert isinstance(SECRET_KEY, str)
    assert len(SECRET_KEY) > 0
    assert ALGORITHM == "HS256"
    assert ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert DATABASE_URL is not None
    assert isinstance(DATABASE_URL, str)

def test_database_url_default():
    os.environ.pop("DATABASE_URL", None)
    from app.core import config
    assert config.DATABASE_URL == "sqlite:///./sql_app.db"
