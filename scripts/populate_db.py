import argparse         # Library for parsing command-line arguments
import pandas as pd     # Library for handling tabular data (tables like Excel)
from sqlalchemy import create_engine, text, inspect  # Library for talking to databases
import os               # Library for system operations, like reading environment variables
import sys
import yaml             # Library for reading YAML-formated files
from tqdm import tqdm   # Library to make progress bars
from pickle import Unpickler
from pathlib import Path
from src.machinery import inspect_df, getenv
import warnings

_PRIMARY_KEY_="id"

def load_config(config_file: str = 'scripts/config.yaml') -> dict:
  """
  Returns the dictionary stored in 'config_file'. There is no test for this function because it is always called when loading the 'Test' class.
  """
  # load config file
  with open(config_file, 'r') as file:
    config = yaml.safe_load(file)
  # return dict with config details
  return config

#https://stackoverflow.com/a/62236766
class TQDMBytesReader(object):

    def __init__(self, fd, **kwargs):
        self.fd = fd
        from tqdm import tqdm
        self.tqdm = tqdm(**kwargs)

    def read(self, size=-1):
        bytes = self.fd.read(size)
        self.tqdm.update(len(bytes))
        return bytes

    def readline(self):
        bytes = self.fd.readline()
        self.tqdm.update(len(bytes))
        return bytes

    def __enter__(self):
        self.tqdm.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        return self.tqdm.__exit__(*args, **kwargs)

#https://stackoverflow.com/a/39495229
def chunker(seq, size):
    # from http://stackoverflow.com/a/434328
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def insert_with_progress(df,engine,chunksize):
    chunks = [df.iloc[i:i+chunksize] for i in range(0, len(df), chunksize)]
    with tqdm(total=len(df)) as pbar:
        for i, cdf in enumerate(chunks):
            # Use pandas built-in batching via chunksize if batching is enabled
            cdf.to_sql(
                index=False,               # Don't save the DataFrame index as a column
                if_exists="append",        # Append to the table instead of replacing it
                name=getenv("TABLE_NAME"), # Target table name in the database
                con=engine,                # Database connection
                method="multi",            # Insert using efficient multi-insert method
                chunksize=chunksize, #batch_size if use_batches else None  # Control batching
            )
            pbar.update(chunksize)


def intersect_config_fields(df, config: dict = load_config()):

    # Try keeping only the satellite fields we're interested in. If does not succeed reset index to prevent first collumn from being dataframe index column
    try:
        df = df[config['SATELLITE_FIELDS']]
    except:
        intersec_satfields = sorted(set(config['SATELLITE_FIELDS']).intersection(list(df.columns)) ,key=lambda x:config['SATELLITE_FIELDS'].index(x))
        
        if len(set(df.columns) - set(config['SATELLITE_FIELDS'])) > 0:
            warnings.warn("Fields " + ", ".join(set(df.columns) - set(config['SATELLITE_FIELDS'])) + " could not be found in `scripts/config.yaml`. These fields will be ignored.", UserWarning)
        
        if len(set(config['SATELLITE_FIELDS']) - set(df.columns)) > 0:
            warnings.warn("Fields " + ", ".join(set(config['SATELLITE_FIELDS']) - set(df.columns)) + " stated in `scripts/config.yaml` but not found in uploaded data. These fields will be ignored.", UserWarning)
        
        df = df[intersec_satfields]

    return df

def get_sql_columns(engine) -> list:

    try:
        inspector = inspect(engine)
        sqlcols = [col["name"] for col in inspector.get_columns(os.getenv("TABLE_NAME"))]
    except:
        with engine.connect() as conn:
            sqlcols = list(pd.read_sql_query(text(f"""SELECT * FROM {os.getenv("TABLE_NAME")}"""), conn).columns)


    return sqlcols

def intersect_sqltable_fields(df, engine):

    with engine.connect() as conn:
        sql_columns = get_sql_columns(engine)
        sql_columns.remove(_PRIMARY_KEY_)

        intersec_satfields = sorted(set(list(df.columns)).intersection(list(sql_columns)) ,key=lambda x:list(df.columns).index(x))

        if len(set(df.columns) - set(sql_columns)) > 0:
            warnings.warn("Fields " + ", ".join(set(df.columns) - set(sql_columns)) + " could not be found in SQL table `" + os.getenv("TABLE_NAME") + "`. These fields will be ignored.", UserWarning)
        
        if len(set(sql_columns) - set(df.columns)) > 0:
            raise ValueError("Fields " + ", ".join(set(sql_columns) - set(df.columns)) + " required by SQL table `" + os.getenv("TABLE_NAME") + "`. Populating Database cannot proceed.")
        
        df = df[intersec_satfields]

    return df


def populate_db(filepath: str, engine, use_batches: bool = False, batch_size: int = 1000, config: dict = load_config()) -> None:
    """
    Loads a .pkl file and populates the TABLE_NAME table in the database.
    Allows full load or batched inserts based on user choice.

    Args:
        filepath: Path to the .pkl file containing the satellite data.
        engine: SQLAlchemy engine for database connection.
        use_batches: If True, insert in batches. If False, insert all at once.
        batch_size: Number of rows per batch (only relevant if use_batches=True).
    """

    print(f"Loading data from {filepath}...")

    # Safety check: only allow .pkl files
    if not filepath.endswith('.pkl'):
        raise ValueError("File type not recognized. Please select a .pkl file")

    # Load the .pkl file with progress bar
    with open(filepath, "rb") as fd:
        total = os.path.getsize(filepath)
        with TQDMBytesReader(fd, total=total) as pbfd:
            up = Unpickler(pbfd)
            df = up.load()
        print(f"Loaded {filepath}")

    # make sure all columns (e.gh. timestamp) are defined as such
    df = df.reset_index()

    # Try keeping only the satellite fields we're interested in. If does not succeed reset index to prevent first collumn from being dataframe index column
    
    df = intersect_config_fields(df, config)

    df = intersect_sqltable_fields(df, engine)

    inspect_df(df)

    print(f"Populating database...")

    insert_with_progress(df,engine,batch_size)

    print("Database populated successfully.")

def add_test_row(filepath: str, engine, config: dict) -> None:
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
    df = intersect_config_fields(df, config)

    df = intersect_sqltable_fields(df, engine)

    df = df[df['timestamp']==df['timestamp'].min()].head(1)

    df.loc[0,"timestamp"] = df.loc[0,"timestamp"] - 0.05 * df.loc[0,"timestamp"]

    # Insert this single test row into the database
    df.to_sql(
        index=False,              # Don't save the DataFrame index as a column
        if_exists="append",       # Append to the table instead of replacing it
        name=getenv("TABLE_NAME"),# Target table name
        con=engine,               # Database connection
        method="multi",           # Insert using efficient multi-insert method
        chunksize=1               # Only one row
    )

def return_test_row(filepath: str, engine, config: dict) -> pd.core.frame.DataFrame:
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
    df = intersect_config_fields(df, config)

    df = intersect_sqltable_fields(df, engine)

    df = df[df['timestamp']==df['timestamp'].min()].head(1)

    df.loc[0,"timestamp"] = df.loc[0,"timestamp"] - 0.05 * df.loc[0,"timestamp"]

    return df

    

# ------------------ #
# Command-Line Setup #
# ------------------ #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate the KBR Gravimety Data table from a .pkl file.")
    parser.add_argument("--filepath", type=str, help="Path to the .pkl data file.")
    parser.add_argument("--use_batches", action="store_true", help="Use batch inserts (default: False).")
    parser.add_argument("--batch_size", type=int, default=1000, help="Batch size to use when batching (default: 1000).")
    args = parser.parse_args()

    # Database connection

    # Determine the data file to use
    if args.filepath:
        data_file = Path(args.filepath)
        if not data_file.exists():
            print(f"Specified file {data_file} does not exist.")
            sys.exit(1)
    else:
        # Try to find a .pkl file in 'data/' folder
        DATA_DIR = Path("data")
        data_files = list(DATA_DIR.glob("*.pkl"))
        if data_files:
            data_file = data_files[0]
            print(f"Found data file(s): {[f.name for f in data_files]}")
        else:
            print("No data file found in 'data/' folder. Skipping population.")
            sys.exit(0)


    print(f"Populating database with {data_file}...")

    try:
        engine = create_engine(getenv('DATABASE_URL'))

        populate_db(
            filepath=str(data_file),
            engine=engine,
            use_batches=args.use_batches,
            batch_size=args.batch_size
        )
    
        print("Database population completed successfully.")

    except Exception as e:
        print(f"Failed to populate database: {e}")
        sys.exit(1)
