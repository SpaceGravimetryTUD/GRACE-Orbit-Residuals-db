import argparse
import pandas as pd
from src.machinery import getenv
from sqlalchemy import create_engine, text
from src.utils.utils import check_polygon_validity
import xarray as xr 

# Setup the database connection
engine = create_engine(getenv('DATABASE_URL'))

def query_satellite_data_by_time(start_time, end_time):
    """Query the TABLE_NAME table for records within a time window."""
    query = text(f"""
        SELECT id, datetime, "latitude_A", "longitude_A", postfit, up_combined
        FROM {getenv("TABLE_NAME")}
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
        FROM {getenv("TABLE_NAME")}
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
        FROM {getenv("TABLE_NAME")}
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

def save_data(df, output_format, filename_prefix):
    if output_format == 'csv':
        df.to_csv(f"{filename_prefix}.csv", index=False)
    elif output_format == 'netcdf':
        ds = df.set_index('datetime').to_xarray()
        ds.to_netcdf(f"{filename_prefix}.nc")
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def main():
    parser = argparse.ArgumentParser(description="Query KBR Gravimetry Data within polygon and time bounds.")
    parser.add_argument("--start_time", type=str, help="Start time (e.g. '2017-01-01T00:00:00')")
    parser.add_argument("--end_time", type=str, help="End time (e.g. '2017-02-01T00:00:00')")
    parser.add_argument("--polygon", type=str, help="Polygon coordinates as 'lon1 lat1,lon2 lat2,...,lonN latN'")
    parser.add_argument("--output_format", type=str, choices=['csv', 'netcdf'], help="Output format (csv or netcdf)")
    args = parser.parse_args()

    if args.start_time:
        start_time = pd.to_datetime(args.start_time)
        st_print = " from " + args.start_time
    else:
        start_time = pd.to_datetime("2010-02-28T22:00:00")
        st_print = ""
    
    if args.end_time:
        end_time = pd.to_datetime(args.end_time)
        et_print = " up to " + args.end_time
    else:
        end_time = pd.to_datetime("2012-10-01T00:00:00")
        et_print = ""
    
    if args.polygon:
        polygon_coordinates = [(float(lon), float(lat)) for lon, lat in (pair.split() for pair in args.polygon.split(","))]
        pc_min = (float(min([pair[0] for pair in polygon_coordinates])), float(min([pair[1] for pair in polygon_coordinates])))
        pc_max = (float(max([pair[0] for pair in polygon_coordinates])), float(max([pair[1] for pair in polygon_coordinates])))
        pc_print = " ranging the coordinates " + str(pc_min) + " to " + str(pc_max)

    else:
        polygon_coordinates = [
            (71.44, 20.25),
            (71.44, 20.91),
            (71.48, 20.91),
            (71.48, 20.25),
            (71.44, 20.25)
        ]
        pc_print = " using default small polygon for test."


    if args.start_time or args.end_time or args.polygon:
        print(str("\u26a0\ufe0f Filtering data" + st_print + et_print + pc_print + "."))
    else:
        print("\u26a0\ufe0f No parameters provided, using default small polygon for test.")
        

    print("\n--- Time Filter Only ---")
    df_time = query_satellite_data_by_time(start_time, end_time)
    print(df_time)
    if args.output_format and not df_time.empty:
        save_data(df_time, args.output_format, "time_filter_output")

    print("\n--- Space Filter Only (Polygon) ---")
    df_space = query_satellite_data_by_polygon(polygon_coordinates)
    print(df_space)
    if args.output_format and not df_space.empty:
        save_data(df_space, args.output_format, "space_filter_output")

    print("\n--- Time + Space Filter (Combined) ---")
    df_both = query_satellite_data_within_polygon(start_time, end_time, polygon_coordinates)
    print(df_both)
    if args.output_format and not df_both.empty:
        save_data(df_both, args.output_format, "combined_filter_output")

if __name__ == "__main__":
    main()
