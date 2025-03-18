from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry

import pandas as pd

Base = declarative_base()

class SatelliteData(Base):
    __tablename__ = 'satellite_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, nullable=False, index=True)
    #month_label = Column(String, nullable=True)
    #source = Column(String, nullable=True)  # 'original' or 'borrowed'
    latitude_A = Column(Float, nullable=False)
    longitude_A = Column(Float, nullable=False)
    altitude_A = Column(Float)
    latitude_B = Column(Float, nullable=False)
    longitude_B = Column(Float, nullable=False)
    altitude_B = Column(Float)
    #geom_A = Column(Geometry('POINT', srid=4326), nullable=True)
    #geom_B = Column(Geometry('POINT', srid=4326), nullable=True)

# Database setup
DATABASE_URL = "postgresql://user:password@localhost:5432/geospatial_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def populate_db(filepath: str):

    if filepath.endswith('.pkl'):
        df = pd.read_pickle(r"{}".format(filepath))
        df = df.reset_index()
        df = df[["timestamp", "latitude_A", "longitude_A", "altitude_A", "latitude_B", "longitude_B", "altitude_B"]]
        df.to_sql(index=False, if_exists="append", name='satellite_data',
                  con=engine,  method="multi", chunksize=5)
    else:
        raise ValueError("File type not recognized. Please select a file of one of the following types: '.pkl'")