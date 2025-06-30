import os
import argparse
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from src.utils.utils import check_polygon_validity

# Load environment variables
load_dotenv()

# Setup the database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in environment variables.")
engine = create_engine(DATABASE_URL)

def query_satellite_data_by_time(start_time, end_time):
    """Query the TABLE_NAME table for records within a time window."""
    query = text(f"""
        SELECT id, datetime, "latitude_A", "longitude_A", postfit, up_combined
        FROM {os.getenv("TABLE_NAME")}
        WHERE datetime BETWEEN :start_time AND :end_time
        ORDER BY datetime ASC
    """)

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params={"start_time": start_time, "end_time": end_time})

    return df

def query_satellite_data_by_polygon(polygon_coordinates):
    """Query the TABLE_NAME table for records within a spatial polygon."""
    # Check if the polygon is valid
    if not check_polygon_validity(polygon_coordinates):
        raise ValueError("Invalid polygon coordinates provided.")

    # Convert the polygon coordinates to WKT format
    polygon_wkt = f"POLYGON(({', '.join([f'{lon} {lat}' for lon, lat in polygon_coordinates])}))"

    query = text(f"""
        SELECT id, datetime, "latitude_A", "longitude_A", postfit, up_combined
        FROM {os.getenv("TABLE_NAME")}
        WHERE ST_Contains(
            ST_GeomFromText(:polygon, 4326),
            ST_SetSRID(ST_MakePoint("longitude_A", "latitude_A"), 4326)
        )
        ORDER BY datetime ASC
    """)

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params={"polygon": polygon_wkt})

    return df

def query_satellite_data_within_polygon(start_time, end_time, polygon_coordinates):
    """Query the TABLE_NAME table for records inside a polygon and time window."""
    # Check if the polygon is valid
    if not check_polygon_validity(polygon_coordinates):
        raise ValueError("Invalid polygon coordinates provided.")

    polygon_wkt = f"POLYGON(({', '.join([f'{lon} {lat}' for lon, lat in polygon_coordinates])}))"

    query = text(f"""
        SELECT id, datetime, "latitude_A", "longitude_A", postfit, up_combined
        FROM {os.getenv("TABLE_NAME")}
        WHERE datetime BETWEEN :start_time AND :end_time
        AND ST_Contains(
            ST_GeomFromText(:polygon, 4326),
            ST_SetSRID(ST_MakePoint("longitude_A", "latitude_A"), 4326)
        )
        ORDER BY datetime ASC
    """)

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params={"start_time": start_time, "end_time": end_time, "polygon": polygon_wkt})

    return df

def main():
    parser = argparse.ArgumentParser(description="Query KBR Gravimetry Data within polygon and time bounds.")
    parser.add_argument("--start_time", type=str, help="Start time (e.g. '2017-01-01T00:00:00')")
    parser.add_argument("--end_time", type=str, help="End time (e.g. '2017-02-01T00:00:00')")
    parser.add_argument("--polygon", type=str, help="Polygon coordinates as 'lon1 lat1,lon2 lat2,...,lonN latN'")
    args = parser.parse_args()

    if args.start_time and args.end_time and args.polygon:
        start_time = pd.to_datetime(args.start_time)
        end_time = pd.to_datetime(args.end_time)
        polygon_coordinates = [(float(lon), float(lat)) for lon, lat in (pair.split() for pair in args.polygon.split(","))]
    else:
        print("\u26a0\ufe0f No parameters provided, using default small polygon for test.")
        start_time = pd.to_datetime("2010-02-28T22:00:00")
        end_time = pd.to_datetime("2012-10-01T00:00:00")
        polygon_coordinates = [
            (71.44, 20.25),
            (71.44, 20.91),
            (71.48, 20.91),
            (71.48, 20.25),
            (71.44, 20.25)
        ]

    print("\n--- Time Filter Only ---")
    df_time = query_satellite_data_by_time(start_time, end_time)
    print(df_time)

    print("\n--- Space Filter Only (Polygon) ---")
    df_space = query_satellite_data_by_polygon(polygon_coordinates)
    print(df_space)

    print("\n--- Time + Space Filter (Combined) ---")
    df_both = query_satellite_data_within_polygon(start_time, end_time, polygon_coordinates)
    print(df_both)

if __name__ == "__main__":
    main()
