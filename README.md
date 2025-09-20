<!--

#This style only renders in standard markdown, it does not in github markdown. The main motivation was to add numbering to the headings.

<style>
.titlesize{
  font-size: xx-large;
}

body {
    counter-reset: h1
}

h1 {
    counter-reset: h2
}

h2 {
    counter-reset: h3
}

h3 {
    counter-reset: h4
}

h1:before {
    counter-increment: h1;
    content: counter(h1) ". "
}

h2:before {
    counter-increment: h2;
    content: counter(h1) "." counter(h2) ". "
}

h3:before {
    counter-increment: h3;
    content: counter(h1) "." counter(h2) "." counter(h3) ". "
}

h4:before {
    counter-increment: h4;
    content: counter(h1) "." counter(h2) "." counter(h3) "." counter(h4) ". "
}
</style> -->

# GRACE Geospatial Data Processing Stack

This project sets up a scalable geospatial data pipeline using **PostgreSQL + PostGIS + TimescaleDB** , **SQLAlchemy**, and **Podman Compose**. It facilitates efficient ingestion, validation, and querying of high-frequency satellite data from the GRACE mission.

---

# 🌍 Context & Background

We work with high-frequency geospatial time-series data from the GRACE satellite mission, specifically Level-1B range-rate residuals derived from inter-satellite K-band observations. These residuals may contain unexploited high-frequency geophysical signals used for scientific applications.

## Key dataset characteristics:

- **Temporal resolution**: 5-second intervals
- **Spatial attributes**: Latitude, longitude, altitude for GRACE-A & GRACE-B
- **Data volume**: 2002–2017, approx. \~95 million records
- **Target queries**: Time-span filtering, spatial bounding, and signal-based statistical analysis

---

# 🚀 Quick Start

## Prerequisites

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


## Ubuntu

NB: These instructions were written after the fact. YMMV

Install prerequisites:

```bash
sudo apt install podman pipx postgresql-client-common postgresql-client
pip3 install podman-compose
```

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

These steps can be run with `op.sh install`.

---

## Clone the Repository

```bash
git clone https://github.com/SpaceGravimetryTUD/GRACE-Orbit-Residuals-db
cd GRACE-Orbit-Residuals-db
```

Switch to the appropriate branch, e.g.:

```bash
git branch v1-flat-data-test
```

---

## Environment Configuration

Make sure to have a data directory where you store your data.

> ⚠️ Security Note on Pickle Files
> Warning: This application loads data using pandas.read_pickle(), which internally uses Python's pickle module.
>
> While this format is convenient for fast internal data loading, it is not secure against untrusted input. Never upload or load .pkl files from unverified or external sources, as they can execute arbitrary code on your system.

Create a `.env` file at the project root:

```ini
# .env
TABLE_NAME=kbr_gravimetry_v2
EXTERNAL_PORT=XXXX #Replace with XXXX with available external port; in grace-cube.lr.tudelft.nl, port 3306 is open
DATABASE_USER=user
DATABASE_PASSWORD=password
DATABASE_HOSTNAME=localhost
DATABASE_NAME=geospatial_db
DATABASE_URL="postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOSTNAME}:${EXTERNAL_PORT}/${DATABASE_NAME}"
DATA_PATH=/mnt/GRACEcube/Data/L1B_res/CSR_latlon_data/flat-data/v2/flat-data-2003.v2.pkl
```

To load environmental variables in `.env` run:

```bash
source .env
```

This is alwways done when the `op.sh` script is run.

---

## Update `/etc/containers/registries.conf`

If error is triggered when running timescaledb image, add the following line to `/etc/containers/registries.conf`:

```
   unqualified-search-registries=["docker.io"]
```

## Update sub[gu]id

```bash
echo "$USER:100000:65536" >> /etc/subuid
echo "$USER:100000:65536" >> /etc/subgid
```

---

### (Optional) Enable PostGIS Extension

If needed, you can manually enable PostGIS (only once):

```sql
CREATE EXTENSION postgis;
```

These steps can be run with `op.sh postgis`.

---

## Start the Database

```bash
podman-compose -f docker-compose.yml up -d
```

or 

```bash
./op.sh up
```

Verify it's running:

```bash
podman ps
```

or 

```bash
./op.sh ps
```

---

## Create credentials for easy database access

The `~/.pgpass` can hold the credentials for accessing the database with various CLI tools, such as `psql`. To create an entry that allows passwordless access:

```bash
./op.sh .pgpass
```

Check access with:

```bash
./op.sh -l
```

You should get something like:

```
                            List of databases
     Name      | Owner | Encoding | Collate |  Ctype  | Access privileges
---------------+-------+----------+---------+---------+-------------------
 geospatial_db | user  | UTF8     | C.UTF-8 | C.UTF-8 |
 postgres      | user  | UTF8     | C.UTF-8 | C.UTF-8 |
 template0     | user  | UTF8     | C.UTF-8 | C.UTF-8 | =c/user          +
               |       |          |         |         | user=CTc/user
 template1     | user  | UTF8     | C.UTF-8 | C.UTF-8 | =c/user          +
               |       |          |         |         | user=CTc/user
(4 rows)
```

---

## Install Python Dependencies

```bash
poetry install
```

or:

```bash
./op.sh poetry-install
```

> ⚠️ ISSUE: Poetry doesn't like pyenv: removing it from PATH works. You case **source** the script `clean-pyenv-from-path.sh` to accomplish this:
> 
>```bash
> . ./clean-pyenv-from-path.sh
>```

> ⚠️ ISSUE: If you get the error:
>
>```
> Installing psycopg2 (2.9.10): Failed
> 
> PEP517 build of a dependency failed
>
>Backend subprocess exited when trying to invoke get_requires_for_build_wheel
>```
> 
> Then:
>
>```
>sudo apt install libpq-dev gcc
>```

From now on, run all Python commands via:

```bash
poetry run <your-command>
```

or:

```bash
./op.sh run <your-command>
```

---

## Initialize the Database Schema with Alembic

This project uses [Alembic](https://alembic.sqlalchemy.org/en/latest/) for [database migration](https://en.wikipedia.org/wiki/Data_migration#Database_migration). 

To initialize the schema:

```bash
# Generate initial migration
poetry run alembic revision --autogenerate -m "Initial migration"
```

This step can be run with `op.sh alembic-init`.

You should get something like:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'kbr_gravimetry_v2'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_kbr_gravimetry_v2_timestamp' on '('timestamp',)'
  Generating /home/teixeira/projects/GRACE-Orbit-Residuals-db/alembic/versions/519a7da74bee_initial_migration.py ...  done
```

If you get the following error:

```
ERROR [alembic.util.messaging] Target database is not up to date.
  FAILED: Target database is not up to date.
```

... it's because this command was already run (and the result added to the repository). To forcefully re-initialize the schema, you need to delete (or backup) all migration files with name `./alembic/versions/*_initial_migration.py`.

This can be achieved with `op.sh alembic-reinit`, which will also call `op.sh alembic-init`.

> ⚠️ IMPORTANT: Edit the generated migration file in `./alembic/versions/`.

>
> The migration may include `op.drop_table('spatial_ref_sys')` due to PostGIS system tables.
> Comment out or remove any lines that drop PostGIS system tables like:
> - spatial_ref_sys
> - geography_columns  
> - geometry_columns
> 
> 
Future Enhancement: The PostGIS system table issue could be resolved by implementing schema-based separation or improving the Alembic configuration to automatically exclude PostGIS system tables.

## Apply the migration

```bash
poetry run alembic upgrade head
```

or:

```bash
./op.sh alembic-upgrade
```

You should get something like:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 519a7da74bee, Initial migration
```

---

## Load Sample Data

This will create the tables and load initial data:

```bash
poetry run python scripts/init_db.py --use_batches --filepath <path to flat data file>
```

or:

```bash
./op.sh load <path to flat data file 1> [ <path to flat data file 2> [ ... <path to flat data file N> ]]
```


If you get the error: `Failed to initialize database: No module named 'src'` then you are in the wrong directory.

## Optional: verify schema from inside the container:

```bash
podman exec -it postgis_container psql -U user -d $DATABASE_NAME -c "\d $TABLE_NAME;"
```

The variables $DATABASE_NAME and $TABLE_NAME are defined in .env.
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

Then in Python:

```python
from scripts.first_query import run_firstquery
run_firstquery()
```
---

## Restart or Clean the Database (Optional)

To completely uninstall:

```bash
podman-compose down
podman volume rm grace-orbit-residuals-db_postgres_data
```

> ⚠️ Warning: This will **permanently delete all data** inside the database.

---

# 📊 Running Tests

Tests rely on a running local database and valid `.env` configuration. The PostGIS Extension should also be enabled (to get no failed tests).

```bash
poetry run pytest
```

> ✅ Ensure:
>
> - `$DATABASE_NAME` is running (defined in `.env`).
> - `$TABLE_NAME table exists (defined in `.env`).
> - Sample data is loaded.

---

# 📁 Project Structure (simplified overview)

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

# 📜 Licensing & Waiver

Licensed under the MIT License.

**Technische Universiteit Delft** hereby disclaims all copyright 
interest in the program "GRACE Geospatial Data Processing Stack" written by the Author(s).

— ***Prof. H.G.C. (Henri) Werij***, Dean of Aerospace Engineering at TU Delft
