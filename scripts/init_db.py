import os
import sys
import argparse
from pathlib import Path
from src.machinery import getenv,showenv

# --- Command-line arguments ---
parser = argparse.ArgumentParser(description="Initialize and optionally populate the database.")
parser.add_argument("--filepath", type=str, help="Path to the .pkl file. If not provided, will look in 'data/' folder.")
parser.add_argument("--use_batches", action="store_true", help="Use batch inserts when populating the database.")
parser.add_argument("--batch_size", type=int, default=1000, help="Batch size for inserts (default: 1000).")
args = parser.parse_args()

# show the contents of the .env file
showenv

# --- Step 1: Initialize the database ---
print("Initializing database...")
try:
    from src.models import init_db
    init_db()
    print("Database initialized successfully.")
except Exception as e:
    print(f"Failed to initialize database: {e}")
    sys.exit(1)

# --- Step 2: Populate the database if data exists ---
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
    from scripts.populate_db import populate_db
    from sqlalchemy import create_engine

engine = create_engine(getenv('DATABASE_URL'))

    populate_db(
        filepath=str(data_file),
        engine=engine,
        use_batches=args.use_batches,
        batch_size=args.batch_size
    )
    print("Database populated successfully.")
except Exception as e:
    print(f"Failed to populate database: {e}")
    sys.exit(1)
