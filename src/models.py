from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from src.machinery import getenv

# If you want spatial queries later, you can reintroduce geoalchemy2
# from geoalchemy2 import Geometry

Base = declarative_base()

class KBRGravimetry(Base):
    __tablename__ = getenv("TABLE_NAME")

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp   = Column(Float, nullable=False, index=True)  # seconds since 2000-01-01

    # post/pre fits
    postfit     = Column(Float)  # Post-fit residuals (m/s)
    observation_vector = Column(Float)  # Pre-fit residuals (m/s)

    # fits after LS
    up_combined = Column(Float)  # Updated total fit (m/s)
    up_local    = Column(Float)  # Local component (m/s)
    up_common   = Column(Float)  # Common component (m/s)
    up_global   = Column(Float)  # Geo-fit component (m/s)

    # GRACE-A
    latitude_A  = Column(Float, nullable=False)  # degrees
    longitude_A = Column(Float, nullable=False)  # degrees
    altitude_A  = Column(Float)  # km
    shadow_A    = Column(Integer)  # 0/1
    adtrack_A   = Column(Integer)  # 0 = descending, 1 = ascending

    # GRACE-B
    latitude_B  = Column(Float, nullable=False)  # degrees
    longitude_B = Column(Float, nullable=False)  # degrees
    altitude_B  = Column(Float)  # km
    shadow_B    = Column(Integer)  # 0/1
    adtrack_B   = Column(Integer)  # 0 = descending, 1 = ascending

    '''
    # "middle-point"
    longitude_MP = Column(Float, nullable=False)  # degrees
    latitude_MP  = Column(Float, nullable=False)  # degrees
    altitude_MP  = Column(Float)  # km

    #additional information
    source       = Column(String) # source filename (without redundant particles)
    variant      = Column(String) # processing variant (internal to CSR)
    label        = Column(String) # solution month
    release      = Column(String) # GRACE data processing version
    '''

    #derived quantities
    datetime = Column(DateTime, nullable=True)  # optional: datetime for convenience

# Database setup
engine = create_engine(getenv('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
