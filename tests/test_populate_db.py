import os
import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from scripts.populate_db import add_test_row
from src.models import init_db  # Make sure this points to your correct init_db function

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_database(engine):
    """Ensure the database schema is created before any tests run."""
    init_db()
    

@pytest.fixture
def clear_test_row(engine):
    """Ensure no test row remains before and after the test."""
    test_timestamp = 1017619200.0  # for example: corresponds to 2002-04-01 in epoch seconds
    yield
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM kbr_gravimetry WHERE timestamp = :ts"), {"ts": test_timestamp})
        conn.commit()


def test_add_test_row(engine, clear_test_row):
    test_file = os.getenv("DATA_PATH")  # e.g., data/flat-data-test.pkl
    assert test_file and os.path.exists(test_file), "Missing or invalid DATA_PATH"

    # Insert one row
    add_test_row(test_file, engine)

    # Check it exists
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM kbr_gravimetry")).scalar()
        assert result >= 1
        
