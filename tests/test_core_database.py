from app.core.database import engine, SessionLocal, Base, get_db

def test_engine_created():
    assert engine is not None

def test_session_local_created():
    assert SessionLocal is not None

def test_base_created():
    assert Base is not None

def test_get_db_generator():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    try:
        next(db_gen)
    except StopIteration:
        pass
