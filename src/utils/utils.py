def check_polygon_validity(polygon_coordinates: list) -> bool:
    """
    Validate the polygon:
    - It must have at least 4 points (minimum to form an area)
    - The first and last points must be the same (closed polygon)
    - Longitude must be between -180 and 180
    - Latitude must be between -90 and 90
    
    Args:
        polygon_coordinates: List of tuples containing (longitude, latitude) pairs.
        Example: [(lon1, lat1), (lon2, lat2), (lon3, lat3), (lon1, lat1)]
    Returns:    
        True if the polygon is valid.


    """
    if len(polygon_coordinates) < 4:
        raise ValueError("A polygon must have at least 4 points.")

    if polygon_coordinates[0] != polygon_coordinates[-1]:
        raise ValueError("The first and last points must be the same to close the polygon.")

    for lon, lat in polygon_coordinates:
        if not (-180 <= lon <= 180) and not (0 <= lon <= 360):
            raise ValueError(f"Invalid longitude {lon}. Must be between -180 and 180 or between 0 and 360..")
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude {lat}. Must be between -90 and 90.")

    return True
