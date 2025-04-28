import pandas as pd  # Library for handling tabular data (tables like Excel)
from sqlalchemy import create_engine  # Library for talking to databases
import os  # Library for system operations, like reading environment variables

# List of fields (columns) we want to keep from the satellite data
SATELLITE_FIELDS = [
    "datetime", "timestamp",
    "latitude_A", "longitude_A", "altitude_A",
    "latitude_B", "longitude_B", "altitude_B",
    "postfit", "observation_vector",
    "up_combined", "up_local", "up_common", "up_global",
    "shadow_A", "irrelevant_A", "adtrack_A",
    "shadow_B", "irrelevant_B", "adtrack_B"
]

def batch_generator(df: pd.DataFrame, batch_size: int = 1000) -> pd.DataFrame:
    """
    Generator that yields small batches of the DataFrame.
    Instead of processing the whole DataFrame at once, we split it into parts.

    Args:
        df: The pandas DataFrame loaded in memory.
        batch_size: How many rows per batch.
    
            Recommended Batch Size:
            Light data, small fields (e.g., satellite floats)	1000-5000
            Medium data, mixed types	500-2000
            Heavy rows, big blobs, large text fields	100-500
            Very slow internet connection to DB	100-500

    Yields:
        A small DataFrame slice of batch_size rows.
    """
    for start in range(0, len(df), batch_size): # range creates a sequence of starting points to iterate over
        # Select rows from 'start' up to 'start + batch_size' (not including)
        yield df.iloc[start:start+batch_size]

def populate_db(filepath: str, engine) -> None:
    """
    Loads a .pkl file and populates the 'kbr_gravimetry' table in the database
    using batches to optimize memory and performance.

    Args:
        engine: SQLAlchemy engine for database connection.
        filepath: Path to the .pkl file containing the satellite data.
    """
    # Safety check: only allow .pkl files
    if not filepath.endswith('.pkl'):
        raise ValueError("File type not recognized. Please select a .pkl file")

    # Load the entire .pkl file as a pandas DataFrame
    df = pd.read_pickle(filepath).reset_index()
    
    # Keep only the satellite fields we're interested in
    df = df[SATELLITE_FIELDS]

    # Insert data in small batches to avoid memory issues and database timeouts
    for batch in batch_generator(df, batch_size=5):
        batch.to_sql(
            index=False,             # Don't save the DataFrame index as a column
            if_exists="append",      # Append to the table instead of replacing it
            name='kbr_gravimetry',    # Target table name in the database
            con=engine,               # Database connection
            method="multi",          # Insert multiple rows per statement for efficiency
            chunksize=5               # How many rows per insert statement
        )

def add_test_row(filepath: str, engine) -> None:
    """
    Loads a .pkl file and inserts only one row into the 'kbr_gravimetry' table.
    Useful for testing purposes.

    Args:
        engine: SQLAlchemy engine to connect to the database.
        filepath: Path to the .pkl file containing the satellite data.
    """
    # Safety check: only allow .pkl files
    if not filepath.endswith('.pkl'):
        raise ValueError("File type not recognized. Please select a .pkl file")

    # Load the file as a pandas DataFrame
    df = pd.read_pickle(filepath).reset_index()

    # Keep only the satellite fields we're interested in and select the first row
    df = df[SATELLITE_FIELDS].head(1)

    # Insert this single test row into the database
    df.to_sql(
        index=False,             # Don't save the DataFrame index as a column
        if_exists="append",      # Append to the table instead of replacing it
        name='kbr_gravimetry',    # Target table name
        con=engine,               # Database connection
        method="multi",          # Insert using efficient multi-insert method
        chunksize=1               # Only one row
    )
