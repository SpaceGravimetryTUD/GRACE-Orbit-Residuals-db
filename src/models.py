import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# If you want spatial queries later, you can reintroduce geoalchemy2
# from geoalchemy2 import Geometry  

# Load environment variables
load_dotenv()

Base = declarative_base()

class KBRGravimetry(Base):
    __tablename__ = 'kbr_gravimetry'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, nullable=False, index=True)  # seconds since 2000-01-01
    postfit = Column(Float)  # Post-fit residuals (m/s)
    observation_vector = Column(Float)  # Pre-fit residuals (m/s)
    up_combined = Column(Float)  # Updated total fit (m/s)
    up_local = Column(Float)  # Local component (m/s)
    up_common = Column(Float)  # Common component (m/s)
    up_global = Column(Float)  # Geo-fit component (m/s)

    latitude_A = Column(Float, nullable=False)  # degrees
    longitude_A = Column(Float, nullable=False)  # degrees
    altitude_A = Column(Float)  # km
    shadow_A = Column(Integer)  # 0/1
    adtrack_A = Column(Integer)  # 0 = descending, 1 = ascending

    latitude_B = Column(Float, nullable=False)  # degrees
    longitude_B = Column(Float, nullable=False)  # degrees
    altitude_B = Column(Float)  # km
    shadow_B = Column(Integer)  # 0/1
    adtrack_B = Column(Integer)  # 0 = descending, 1 = ascending

    datetime = Column(DateTime, nullable=True)  # optional: datetime for convenience

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in environment variables.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
