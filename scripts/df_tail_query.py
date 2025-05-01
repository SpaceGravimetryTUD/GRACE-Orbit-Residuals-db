from sqlalchemy import create_engine, text
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup the database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in environment variables.")
engine = create_engine(DATABASE_URL)

def query_get_df_tail(N) -> None:
    """Query the kbr_gravimetry table for the last N records."""
    query = text("""
        SELECT *
        FROM kbr_gravimetry
        ORDER BY id DESC
        FETCH FIRST :N ROWS ONLY;
    """)

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params={"N": N})

    return df