# GRACE Geospatial Data Processing Stack

This project sets up a scalable geospatial data pipeline using **PostgreSQL + PostGIS + TimescaleDB** , **SQLAlchemy**, and **Podman Compose**. It facilitates efficient ingestion, validation, and querying of high-frequency satellite data from the GRACE mission.

---

## 🌍 Context & Background

We work with high-frequency geospatial time-series data from the GRACE satellite mission, specifically Level-1B range-rate residuals derived from inter-satellite Ka-band observations. These residuals may contain unexploited high-frequency geophysical signals used for scientific applications.

### Key dataset characteristics:

- **Temporal resolution**: 5-second intervals
- **Spatial attributes**: Latitude, longitude, altitude for GRACE A & B
- **Data volume**: 2002–2017, approx. \~95 million records
- **Target queries**: Time-span filtering, spatial bounding, and signal-based statistical analysis

---

## 🚀 Quick Start

### Prerequisites

This project targets Unix-based systems. If you're on Windows, install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) and proceed as if on Ubuntu.

Install the following tools:

- **Podman & Podman Compose**
  - [Podman Install](https://podman.io/getting-started/installation)
  - [Podman Compose Install](https://github.com/containers/podman-compose)
- **Python 3.10+**
- **pip**
- **[Poetry 2.x](https://python-poetry.org/docs/#installation)**

> 🔐 **Security Note**: Podman is recommended over Docker for production due to rootless container support.

> 📅 **Docker Compatibility**: You can also use Docker for development or local testing if it's already installed on your system. Podman supports Docker CLI syntax, so most `docker` and `docker-compose` commands are interchangeable with `podman` and `podman-compose`.

---

### Ubuntu

NB: These instructions were written after the fact. YMMV

Install prerequisites:

```bash
sudo apt install podman pipx postgresql-client-common postgresql-client
pip3 install podman-compose
````

Check:

```bash
podman-compose -v
pipx ensurepath
```

Install and check poetry:

```bash
pipx install poetry
poetry -V
```

---

### Clone the Repository

```bash
git clone https://github.com/SpaceGravimetryTUD/GRACE-Orbit-Residuals-db
cd GRACE-Orbit-Residuals-db
```

Switch to the appropriate branch, e.g.:

```bash
git checkout v1-flat-data-test
```

---

### Environment Configuration

Make sure to have a data directory where you store your data.

> ⚠️ Security Note on Pickle Files
> Warning: This application loads data using pandas.read\_pickle(), which internally uses Python's pickle module.
> While this format is convenient for fast internal data loading, it is not secure against untrusted input. Never upload or load `.pkl` files from unverified or external sources, as they can execute arbitrary code on your system.

Create a `.env` file at the project root:

```ini
# .env
TABLE_NAME=kbr_gravimetry_v2
EXTERNAL_PORT=XXXX #Replace XXXX with available external port; in grace-cube.lr.tudelft.nl, port 3306 is open
DATABASE_NAME=geospatial_db
DATABASE_URL="postgresql://user:password@localhost:5432/${DATABASE_NAME}"
DATA_PATH=/mnt/GRACEcube/Data/L1B_res/CSR_latlon_data/flat-data/v2/flat-data-2003.v2.pkl
```

To load environmental variables in `.env` run:

```bash
source .env
```

---

### Update `/etc/containers/registries.conf`

If error is triggered when running timescaledb image, add the following line to `/etc/containers/registries.conf`:

```
   unqualified-search-registries=["docker.io"]
```

### Update sub\[gu]id

```bash
echo "$USER:100000:65536" >> /etc/subuid
echo "$USER:100000:65536" >> /etc/subgid
```

---

### Start the Database

```bash
podman-compose -f docker-compose.yml up -d
```

Verify it's running:

```bash
podman ps
```

---

### Enable PostGIS Extension

If needed, you can manually enable PostGIS (only once):


```bash
podman exec -it postgis_container psql -U user -d $DATABASE_NAME -c "CREATE EXTENSION postgis;"
```

---

### Install Python Dependencies

```bash
poetry install
```

> If you get the error:
>
> ```
> Installing psycopg2 (2.9.10): Failed
> PEP517 build of a dependency failed
> Backend subprocess exited when trying to invoke get_requires_for_build_wheel
> ```
>
> Then:
>
> ```
> sudo apt install libpq-dev gcc
> ```

From now on, run all Python commands via:

```bash
poetry run <your-command>
```

> ⚠️ ISSUE: Poetry doesn't like pyenv: removing it from PATH works

---

## 🛠️ Database Schema & Migrations

There are two ways to set up the database schema:

#### Initialize from scratch (recommended for new setups)

For a fresh install (new database, no existing data):

```bash
poetry run python scripts/init_db.py --use_batches --filepath <path to flat data file>
```

---

### Modify schema with Alembic (advanced use)

**Important:** Alembic is only meant for schema *migrations*.
Do **not** use Alembic for initial setup — it is only useful if you already have a running database with data and you want to change the schema without losing that data.

Workflow for maintainers:

```bash
# Generate migration from model changes
poetry run alembic revision --autogenerate -m "Describe schema change"

# ⚠️ IMPORTANT: Edit the generated migration file
# Alembic may try to drop PostGIS system tables.
# Remove or comment out any lines like:
# - op.drop_table('spatial_ref_sys')
# - op.drop_table('geometry_columns')
# - op.drop_table('geography_columns')

# Apply the migration
poetry run alembic upgrade head
```

Future Enhancement: The PostGIS system table issue could be resolved by implementing schema-based separation or improving the Alembic configuration to automatically exclude PostGIS system tables.

---

## Load Sample Data

This will create the tables and load initial data:

```bash
poetry run python scripts/init_db.py --use_batches --filepath data/flat-data-test.pkl
```

If you get the error:
`Failed to initialize database: No module named 'src'`
then you are in the wrong directory.

Optional: verify schema from inside the container:

```bash
podman exec -it postgis_container psql -U user -d $DATABASE_NAME -c "\d $TABLE_NAME;"
```

The variables \$DATABASE\_NAME and \$TABLE\_NAME are defined in .env.

---

### Insert & Query Example Data

Ensure `data/flat-data-test.pkl` exists:

```bash
ls data/flat-data-test.pkl
```

Run a sample query:

```bash
poetry run python
```

If you have not populated the databse yet, please run the following command:

```bash
poetry run python scripts/populate_db.py --use_batches
```

YOu can also do so be defining the size of each batch:

```bash
poetry run python scripts/populate_db.py --use_batches --batch_size=10000
```

Then in Python you can try your first simple query:

```python
from scripts.first_query import run_firstquery
run_firstquery()
```

or start running your own spatiotemporal queries using `space_time_query.py` from the command line. For example:

```bash
poetry run python scripts/space_time_query.py --start_time="2012-02-29T00:00:00" --end_time="2012-04-01T00:00:00"  --polygon='130 -10,240 -10,240 10,130 10,130 -10' --output_format='csv'
```

## Restart or Clean the Database (Optional)

To completely uninstall:

```bash
podman-compose down
podman volume rm grace-orbit-residuals-db_postgres_data
```

> ⚠️ Warning: This will **permanently delete all data** inside the database.

---

## 📊 Running Tests

Tests rely on a running local database and valid `.env` configuration. The PostGIS Extension should also be enabled (to get no failed tests).

```bash
poetry run pytest
```

> ✅ Ensure:
>
> * `$DATABASE_NAME` is running (defined in `.env`).
> * `$TABLE_NAME` table exists (defined in `.env`).
> * Sample data is loaded.

---

## 📁 Project Structure (simplified overview)

```text
.
├── alembic/          # Migration files along with env.py
├── scripts/          # Scripts to init DB, ingest data, and run spatial/temporal queries
├── src/              # Source code including SQLAlchemy models and utility functions
├── tests/            # Unit tests for ingestion, queries, and extension validation
├── docker-compose.yml
├── pyproject.toml    # Poetry project config
├── .env              # Local environment variables (not committed)
├── postgresql.conf   # Custom DB configuration (optional)
├── LICENSE
└── README.md
```

---

## 📜 Licensing & Waiver

Licensed under the MIT License.

**Technische Universiteit Delft** hereby disclaims all copyright
interest in the program "GRACE Geospatial Data Processing Stack" written by the Author(s).

— ***Prof. H.G.C. (Henri) Werij***, Dean of Aerospace Engineering at TU Delft




