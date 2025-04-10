import os
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

from src.models import Base, SatelliteData, create_engine, SessionLocal, init_db

# Load .env file
load_dotenv()

@pytest.fixture(scope="module")
def db_engine():
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        raise ValueError("DATABASE_URL is not set in the environment.")

    engine = create_engine(db_url)
    # Create tables
    Base.metadata.create_all(engine)
    yield engine
    # Drop tables after test
    Base.metadata.drop_all(engine)

def test_satellite_data_table_exists(db_engine):
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    assert 'satellite_data' in tables
