from sqlalchemy import select, create_engine, and_
import os
from src.models import KBRGravimetry
from scripts.populate_db import load_config
from sqlalchemy.orm import Session

# Query db using environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)



def run_firstquery() -> None:

    config=load_config()

    with Session(engine) as session:
        results = session.query(KBRGravimetry).limit(5).all()

        print('\t'.join(config['SATELLITE_FIELDS']))
        for row in results:
            for f in config['SATELLITE_FIELDS']:
                print(getattr(row,f), end='\t', flush=True)
            print('\b', flush=True)
