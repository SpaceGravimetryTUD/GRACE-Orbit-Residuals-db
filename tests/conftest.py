import os
import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
# from scripts.populate_db import add_test_row
# from src.models import init_db  # Make sure this points to your correct init_db function

load_dotenv()

@pytest.fixture(scope="session")
def engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not found in environment variables.")
    return create_engine(db_url)
