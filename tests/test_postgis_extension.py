import pytest
from sqlalchemy import text
from src.models import engine

def test_postgis_extension_active():
    """Ensure PostGIS extension is installed and available."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'postgis';")
        ).scalar()

    assert result == "postgis", (
        "❌ PostGIS extension is not installed or not activated! "
        "👉 Run: CREATE EXTENSION IF NOT EXISTS postgis;"
    )
    print("✅ PostGIS extension is active.")