import pandas as pd

# Shared list of fields
SATELLITE_FIELDS = [
    "timestamp",
    "latitude_A", "longitude_A", "altitude_A",
    "latitude_B", "longitude_B", "altitude_B"
]

def populate_db(filepath: str, engine) -> None:
    """Populates the satellite_data table with the full file content.
    engine: SQLAlchemy engine
    filepath: Path to the .pkl"""
    if not filepath.endswith('.pkl'):
        raise ValueError("File type not recognized. Please select a .pkl file")

    df = pd.read_pickle(filepath).reset_index()
    df = df[SATELLITE_FIELDS]
    df.to_sql(index=False, if_exists="append", name='satellite_data',
              con=engine, method="multi")


def add_test_row(filepath: str, engine) -> None:
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
