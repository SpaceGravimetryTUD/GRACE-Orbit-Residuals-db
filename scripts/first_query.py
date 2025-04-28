from sqlalchemy import select, create_engine, and_
import os
from src.models import KBRGravimetry
from scripts.populate_db import SATELLITE_FIELDS
from sqlalchemy.orm import Session

# Query db using environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)



def run_firstquery() -> None:

    with Session(engine) as session:
        results = session.query(KBRGravimetry).order_by(KBRGravimetry.id.desc()).limit(10).all()

        print('\t'.join(SATELLITE_FIELDS))
        for row in results:
            print('\t'.join([str(row.timestamp),
                             str(row.latitude_A),
                             str(row.longitude_A),
                             str(row.altitude_A),
                             str(row.latitude_B),
                             str(row.longitude_B),
                             str(row.altitude_B)]))
                             
        '''print(row.timestamp)
            print(row.latitude_A)
            print(row.longitude_A)
            print(row.altitude_A)
            print(row.latitude_B)
            print(row.longitude_B)
            print(row.altitude_B)'''