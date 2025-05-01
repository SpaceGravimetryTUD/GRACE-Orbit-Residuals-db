from sqlalchemy import text

def test_timescaledb_extension_installed(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb';")).fetchone()
        assert result is not None, "TimescaleDB extension is not installed."


def test_timescaledb_is_active(engine):
    with engine.connect() as conn:
        restoring_status = conn.execute(text("SHOW timescaledb.restoring;")).fetchone()
        assert restoring_status is not None, "Could not fetch timescaledb.restoring status."
        assert restoring_status[0] == 'off', "TimescaleDB is still restoring or not active."


def test_create_hypertable(engine):
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS test_timescale_check;"))
        conn.execute(text("""
            CREATE TABLE test_timescale_check (
                time TIMESTAMPTZ NOT NULL,
                value DOUBLE PRECISION
            );
        """))
        conn.execute(text("SELECT create_hypertable('test_timescale_check', 'time', if_not_exists => TRUE);"))
        result = conn.execute(text("""
            SELECT hypertable_name 
            FROM timescaledb_information.hypertables 
            WHERE hypertable_name = 'test_timescale_check';
        """)).fetchone()
        assert result is not None, "Hypertable creation failed — TimescaleDB might not be working properly."
