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

### 1️⃣ Prerequisites

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

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/SpaceGravimetryTUD/GRACE-Orbit-Residuals-db
cd GRACE-Orbit-Residuals-db
```

---

### Step 5 comes here

---

### Update /etc/containers/registries.conf

---

### update sub[gu]id

echo "$USER:100000:65536" >> /etc/subuid
echo "$USER:100000:65536" >> /etc/subgid

---

### 3️⃣ Start the Database

```bash
podman-compose -f docker-compose.yml up -d
```

Verify it's running:

```bash
podman ps
```

---

### 4️⃣ Install Python Dependencies

```bash
poetry install
```

If you get the error:

```
 Installing psycopg2 (2.9.10): Failed

PEP517 build of a dependency failed

Backend subprocess exited when trying to invoke get_requires_for_build_wheel
```

Then:

```
 sudo apt install libpq-dev gcc
```

From now on, run all Python commands via:

```bash
poetry run <your-command>
```

ISSUE: Poetry doesn't like pyenv: removing it from PATH works

---

### 5️⃣ Environment Configuration
Make sure to have a data directory where you store your data.

> ⚠️ Security Note on Pickle Files
> Warning: This application loads data using pandas.read_pickle(), which internally uses Python's pickle module.

While this format is convenient for fast internal data loading, it is not secure against untrusted input.Never upload or load .pkl files from unverified or external sources, as they can execute arbitrary code on your system.



Create a `.env` file at the project root:

```ini
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/geospatial_db
DATA_PATH=data/flat-data-test.pkl
EXTERNAL_PORT=XXXX #Replace with XXXX with available external port
```

Ensure the database is running (`podman-compose up -d`) before using scripts.

---

### 6️⃣ Initialize the Database Schema

This will create the tables and prepare the schema:

```bash
poetry run python scripts/init_db.py --use_batches --filepath <path to flat data file>
```

If you get the error:

```
Failed to initialize database: No module named 'src'
````

Then:


(Optional) Verify schema from inside the container:

```bash
podman exec -it postgis_container psql -U user -d geospatial_db -c "\d kbr_gravimetry;"
```

---

### 7️⃣ Insert & Query Example Data

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

### 8️⃣ (Optional) Enable PostGIS Extension

Manually enable PostGIS (only once):

```sql
CREATE EXTENSION postgis;
```

---

### 9️⃣ Restart or Clean the Database (Optional)

To completely uninstall:

```bash
podman-compose down
podman volume rm grace-orbit-residuals-db_postgres_data
```

> ⚠️ Warning: This will **permanently delete all data** inside the database.

---

## 📊 Running Tests

Tests rely on a running local database and valid `.env` configuration.

```bash
poetry run pytest
```

> ✅ Ensure:
> - `geospatial_db` is running.
> - `kbr_gravimetry` table exists.
> - Sample data is loaded.

---

## 📁 Project Structure (simplified overview)

```text
.
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

