import os
import sys
from pathlib import Path

# Load your environment
from dotenv import load_dotenv
load_dotenv()

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
DATA_DIR = Path("data")
data_files = list(DATA_DIR.glob("*.pkl"))

if data_files:
    print(f"Found data file(s): {[f.name for f in data_files]}")
    # We'll use the first one found
    data_file = data_files[0]

    print(f"Populating database with {data_file}...")
    try:
        from scripts.populate_db import populate_db
        from sqlalchemy import create_engine

        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable not set.")

        engine = create_engine(DATABASE_URL)

        populate_db(str(data_file), engine)
        print("Database populated successfully.")
    except Exception as e:
        print(f"Failed to populate database: {e}")
        sys.exit(1)
else:
    print("No data file found in 'data/' folder. Skipping population.")
