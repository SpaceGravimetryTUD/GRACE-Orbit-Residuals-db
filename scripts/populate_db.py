import argparse  # Library for parsing command-line arguments
import pandas as pd  # Library for handling tabular data (tables like Excel)
from sqlalchemy import create_engine  # Library for talking to databases
import os  # Library for system operations, like reading environment variables
from dotenv import load_dotenv

# List of fields (columns) we want to keep from the satellite data
SATELLITE_FIELDS = [
    "datetime", "timestamp",
    "latitude_A", "longitude_A", "altitude_A",
    "latitude_B", "longitude_B", "altitude_B",
    "postfit", "observation_vector",
    "up_combined", "up_local", "up_common", "up_global",
    "shadow_A", "adtrack_A",
    "shadow_B", "adtrack_B"
]

def populate_db(filepath: str, engine, use_batches: bool = False, batch_size: int = 1000) -> None:
    """
    Loads a .pkl file and populates the TABLE_NAME table in the database.
    Allows full load or batched inserts based on user choice.

    Args:
        filepath: Path to the .pkl file containing the satellite data.
        engine: SQLAlchemy engine for database connection.
        use_batches: If True, insert in batches. If False, insert all at once.
        batch_size: Number of rows per batch (only relevant if use_batches=True).
    """
    # Safety check: only allow .pkl files
    if not filepath.endswith('.pkl'):
        raise ValueError("File type not recognized. Please select a .pkl file")

    # Load the entire .pkl file as a pandas DataFrame
    df = pd.read_pickle(filepath).reset_index() # nosec

    # Keep only the satellite fields we're interested in
    df = df[SATELLITE_FIELDS]

    # Use pandas built-in batching via chunksize if batching is enabled
    df.to_sql(
        index=False,             # Don't save the DataFrame index as a column
        if_exists="append",      # Append to the table instead of replacing it
        name=os.getenv("TABLE_NAME"), # Target table name in the database
        con=engine,                # Database connection
        method="multi",          # Insert using efficient multi-insert method
        chunksize=batch_size if use_batches else None  # Control batching
    )

def add_test_row(filepath: str, engine) -> None:
    """
    Loads a .pkl file and inserts only one row into the TABLE_NAME table.
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
        name=os.getenv("TABLE_NAME"),# Target table name
        con=engine,               # Database connection
        method="multi",          # Insert using efficient multi-insert method
        chunksize=1               # Only one row
    )

# ------------------ #
# Command-Line Setup #
# ------------------ #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate the KBR Gravimety Data table from a .pkl file.")
    parser.add_argument("--filepath", type=str, required=True, help="Path to the .pkl data file.")
    parser.add_argument("--use_batches", action="store_true", help="Use batch inserts (default: False).")
    parser.add_argument("--batch_size", type=int, default=1000, help="Batch size to use when batching (default: 1000).")
    args = parser.parse_args()

    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise EnvironmentError("DATABASE_URL not found in environment variables.")
    engine = create_engine(DATABASE_URL)

    # Run population
    populate_db(
        filepath=args.filepath,
        engine=engine,
        use_batches=args.use_batches,
        batch_size=args.batch_size
    )
    print("Database population completed successfully.")
