import os
import pytest
from sqlalchemy import create_engine, text
from src.machinery import getenv
from scripts.populate_db import add_test_row, load_config, return_test_row
from src.models import init_db  # Make sure this points to your correct init_db function

@pytest.fixture(scope="session", autouse=True)
def setup_database(engine):
    """Ensure the database schema is created before any tests run."""
    init_db()


@pytest.fixture
def clear_test_row(engine):
    """Ensure no test row remains before and after the test."""

    test_file = getenv("DATA_PATH")  # e.g., data/flat-data-test.pkl
    assert test_file and os.path.exists(test_file), "Missing or invalid DATA_PATH"

    test_row = return_test_row(test_file, load_config())

    test_timestamp = float(test_row.loc[0, 'timestamp'])  # for example: corresponds to 2002-04-01 in epoch seconds
    yield
    with engine.connect() as conn:
        conn.execute(text(f"DELETE FROM {getenv('TABLE_NAME')} WHERE timestamp = :ts"), {"ts": test_timestamp})
        conn.commit()


def test_add_test_row(engine, clear_test_row):
    test_file = getenv("DATA_PATH")  # e.g., data/flat-data-test.pkl
    assert test_file and os.path.exists(test_file), "Missing or invalid DATA_PATH"

    # Insert one row
    add_test_row(test_file, engine, load_config())

    # Check it exists
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {getenv('TABLE_NAME')}")).scalar()
        assert result >= 1
