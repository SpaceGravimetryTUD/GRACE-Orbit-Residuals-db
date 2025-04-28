import os
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

from src.models import Base, KBRGravimetry, create_engine, SessionLocal, init_db

# Load .env file
load_dotenv()

def test_kbr_gravimetry_table_exists(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert 'kbr_gravimetry' in tables
