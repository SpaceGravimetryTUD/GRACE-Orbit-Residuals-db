#!/bin/bash
set -e

DIR=$(cd $(dirname $BASH_SOURCE)/..; pwd)

if [ ! -s $DIR/.env ]
then
  echo "ERROR: cannot find $DIR/.env file"
  exit 3
fi

source $DIR/.env


# Wait for PostgreSQL to be ready inside the container
echo "Waiting for PostgreSQL to be ready..."
until psql -p $EXTERNAL_PORT -h 127.0.0.1  -U user -d $DATABASE_NAME -c '\q' 2>/dev/null; do
  sleep 1
done

# Truncate all tables
echo "Truncating all tables in the public schema..."
psql -p $EXTERNAL_PORT -h 127.0.0.1 -U user -d $DATABASE_NAME -c "
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
