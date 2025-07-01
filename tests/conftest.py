import os
import pytest
from sqlalchemy import create_engine, text
from src.machinery import getenv
# from scripts.populate_db import add_test_row
# from src.models import init_db  # Make sure this points to your correct init_db function

@pytest.fixture(scope="session")
def engine():
    return create_engine(getenv("DATABASE_URL"))
