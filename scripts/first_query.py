from sqlalchemy import select, create_engine, and_
import os
from src.models import SatelliteData
from sqlalchemy.orm import Session

# Query db using environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

mean_timestamp = 389102383

def run_firstquery() -> None:

    query = select(SatelliteData).where(SatelliteData.timestamp == 383875185)

    with Session(engine) as session:
        for row in session.execute(query):
            print(row)