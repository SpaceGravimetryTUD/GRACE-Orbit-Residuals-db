import os
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from src.machinery import getenv

from src.models import Base, KBRGravimetry, create_engine, SessionLocal, init_db

def test_table_exists(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert getenv('TABLE_NAME') in tables
