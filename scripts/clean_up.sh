#!/bin/bash
set -e

# Wait for PostgreSQL to be ready inside the container
echo "Waiting for PostgreSQL to be ready..."
until psql -U user -d geospatial_db -c '\q' 2>/dev/null; do
  sleep 1
done

# Truncate all tables
echo "Truncating all tables in the public schema..."
psql -U user -d geospatial_db -c "
DO \$\$
DECLARE
    stmt TEXT;
BEGIN
    SELECT 'TRUNCATE TABLE ' || string_agg(format('%I.%I', schemaname, tablename), ', ') || ' CASCADE;'
    INTO stmt
    FROM pg_tables
    WHERE schemaname = 'public';

    IF stmt IS NOT NULL THEN
      EXECUTE stmt;
    END IF;
END
\$\$ LANGUAGE plpgsql;
"

# Optionally, you can also reinitialize schema if needed here
# Example: CREATE EXTENSIONS, etc.

echo "Finished database clean-up."
