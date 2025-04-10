import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry

# Load environment variables from .env file
load_dotenv()

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
# Database setup using environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in environment variables.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)