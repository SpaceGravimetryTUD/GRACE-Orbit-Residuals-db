import pytest
from src.models import SessionLocal, KBRGravimetry
from sqlalchemy import text

def test_fetch_first_satellite_row(engine):
    session = SessionLocal()
    try:
        first_row = session.query(KBRGravimetry).first()
        assert first_row is not None, f"No data found in {os.getenv('TABLE_NAME')} table!"
        print(
            f"First row fetched: "
            f"timestamp={first_row.timestamp}, "
            f"lat_A={first_row.latitude_A}, lon_A={first_row.longitude_A}, "
            f"lat_B={first_row.latitude_B}, lon_B={first_row.longitude_B}"
        )
    finally:
        session.close()


def test_postgis_extension(engine):
    with engine.connect() as connection:
        # First, activate PostGIS
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        
        # Then, you can use PostGIS functions safely
        result = connection.execute(
            text("SELECT ST_AsText(ST_Point(30.0, 10.0));")
        ).scalar()
        print("PostGIS ST_AsText(ST_Point(30.0, 10.0)) result:", result)

        assert result == "POINT(30 10)"

def test_timescaledb_extension(engine):
    session = SessionLocal()
    try:
        # Fetch the first datetime from your data
        first_row = session.query(KBRGravimetry.datetime).first()
        assert first_row is not None, f"No datetime data found in {os.getenv('TABLE_NAME')} table!"

        real_datetime = first_row.datetime  # Now it's already a proper datetime

        # Use TimescaleDB time_bucket function
        result = session.execute(
            text("""
                SELECT time_bucket('1 day', TIMESTAMP :dt)
            """),
            {"dt": real_datetime}
        ).scalar()

        print(f"TimescaleDB time_bucket result: {result}")

        assert result is not None, "TimescaleDB time_bucket did not return a valid result!"

    finally:
        session.close()
