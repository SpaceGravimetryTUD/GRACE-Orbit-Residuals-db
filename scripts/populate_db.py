import pandas as pd
from sqlalchemy import create_engine
import os

# Shared list of fields
SATELLITE_FIELDS = [
    "datetime", "timestamp",
    "latitude_A", "longitude_A", "altitude_A",
    "latitude_B", "longitude_B", "altitude_B"
]

# Test and populate db using environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def populate_db(filepath: str) -> None:
    """Populates the satellite_data table with the full file content.
    engine: SQLAlchemy engine
    filepath: Path to the .pkl"""
    if not filepath.endswith('.pkl'):
        raise ValueError("File type not recognized. Please select a .pkl file")

    df = pd.read_pickle(filepath).reset_index()
    df = df[SATELLITE_FIELDS]
    df.to_sql(index=False, if_exists="append", name='satellite_data',
              con=engine, method="multi", chunksize = 5)


def add_test_row(filepath: str) -> None:
    """Inserts a single row from the dataset for test purposes.
    engine: SQLAlchemy engine
    filepath: Path to the .pkl file
    """
    if not filepath.endswith('.pkl'):
        raise ValueError("File type not recognized. Please select a .pkl file")

    df = pd.read_pickle(filepath).reset_index()
    df = df[SATELLITE_FIELDS].head(1)
    df.to_sql(index=False, if_exists="append", name='satellite_data',
              con=engine, method="multi", chunksize=1)
