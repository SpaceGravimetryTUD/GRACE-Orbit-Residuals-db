# GRACE Geospatial Data Processing Stack

This project sets up a scalable geospatial data pipeline using **PostgreSQL + PostGIS + TimescaleDB** , **SQLAlchemy**, and **Podman Compose**. It facilitates efficient ingestion, validation, and querying of high-frequency satellite data from the GRACE mission.

**📖 Available on 4TU.ResearchData** - This software package is published on 4TU.ResearchData for academic citation and long-term preservation. See the `CITATION.cff` file for proper citation format.

---

## 🌍 Context & Background

We work with high-frequen## 👥 Contributors

This project was developed by the Space Gravimetry research group at Delft University of Technology:

- **Jose Carlos Urra Llanusa** - Research Software Engineer
- **Joao De Teixeira da Encarnacao** - Research Scientist  
- **Selin Kubilay** - Research Engineer
- **João Guimarães** - Software Developer
- **Miguel Cuadrat-Grzybowski** - Research Engineer

## 📜 Licensing & Waiverial time-series data from the GRACE satellite mission, specifically Level-1B range-rate residuals derived from inter-satellite Ka-band observations. These residuals may contain unexploited high-frequency geophysical signals used for scientific applications.

### Key dataset characteristics:

- **Temporal resolution**: 5-second intervals
- **Spatial attributes**: Latitude, longitude, altitude for GRACE A & B
- **Data volume**: 2002–2017, approx. \~95 million records
- **Target queries**: Time-span filtering, spatial bounding, and signal-based statistical analysis

---

## 🚀 Quick Start

### 📋 Setup Overview

This setup involves the following key steps:
1. **Install Prerequisites** (Podman, Poetry, etc.)
2. **Initialize Podman Machine** (macOS/Windows only)
3. **Clone Repository** and configure environment
4. **Start Database Containers** with Podman Compose
5. **Install Python Dependencies** and run setup scripts

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

> 🖥️ **Platform Notes**: 
> - **macOS/Windows**: Requires Podman machine (VM) - see setup instructions below
> - **Linux**: Runs natively without VM requirement

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

### 🔧 Podman Machine Setup

**Important**: On macOS and Windows, Podman requires a virtual machine to run containers. Follow these steps to initialize and start the Podman machine:
**On Linux**: Podman runs natively without a machine, so you can skip the machine initialization steps below.

#### 1. Initialize Podman Machine

```bash
# Initialize a new Podman machine (only needed once)
podman machine init

# Alternative: Initialize with custom settings
# podman machine init --memory 4096 --cpus 2 --disk-size 50
```

#### 2. Start Podman Machine

```bash
# Start the Podman machine
podman machine start

# Verify the machine is running
podman machine list
```

You should see output similar to:
```
NAME                     VM TYPE     CREATED      LAST UP            CPUS        MEMORY      DISK SIZE
podman-machine-default*  qemu        2 weeks ago  Currently running  2           2.147GB     107.4GB
```

#### 3. Verify Podman Installation

```bash
# Test that Podman is working
podman --version
podman info

# Test that you can run containers
podman run hello-world
```

---

### Clone the Repository

```bash
git clone https://github.com/SpaceGravimetryTUD/GRACE-Orbit-Residuals-db
cd GRACE-Orbit-Residuals-db
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
(THIS SHOULD GO INTO TROUBLE SHOOTING)
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

### Enable PostGIS Extension

If needed, you can manually enable PostGIS (only once):


```sh
podman exec -it postgis_container psql -U user -d $DATABASE_NAME -c "CREATE EXTENSION postgis;"
```

---

### 🗄️ Start the Database

**Prerequisites**: Ensure your Podman machine is running (see Podman Machine Setup section above).

```bash
# Verify Podman machine is running (macOS/Windows)
podman machine list

# Start the database containers
podman-compose -f docker-compose.yml up -d
```

**Expected output:**
```
[+] Running 2/2
 ✔ Container postgis_container   Started
 ✔ Container timescaledb_container   Started  
```

#### Verify Database is Running

```bash
# Check container status
podman ps

# You should see containers similar to:
# CONTAINER ID  IMAGE                     COMMAND     CREATED      STATUS      PORTS                   NAMES
# abc123def456  postgis/postgis:latest    postgres    2 mins ago   Up 2 mins   0.0.0.0:5432->5432/tcp  postgis_container
```

#### Test Database Connection

```bash
# Test connection to the database
podman exec -it postgis_container psql -U user -d $DATABASE_NAME -c "SELECT version();"
```

#### 🔧 Troubleshooting Database Startup

If containers fail to start:

```bash
# Check logs
podman-compose logs

# Stop and remove containers
podman-compose down

# Restart with verbose output
podman-compose -f docker-compose.yml up -d --force-recreate
```

If you see permission errors:
```bash
# Ensure proper subuid/subgid setup (Linux)
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid

# Restart Podman machine (macOS/Windows)
podman machine stop
podman machine start
```

```bash
podman ps
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

## Container Management

### Stopping Services

```bash
# Stop all containers
podman-compose down

# Stop containers and remove volumes (⚠️ destroys data)
podman-compose down -v
```

### Managing Podman Machine

```bash
# Stop Podman machine (will stop all containers)
podman machine stop

# Start Podman machine
podman machine start

# Check machine status
podman machine list

# View machine details
podman machine info
```

### Monitoring and Logs

```bash
# View logs for all services
podman-compose logs

# View logs for specific service
podman-compose logs postgis_container

# Follow logs in real-time
podman-compose logs -f

# Check container resource usage
podman stats
```

### Cleanup Commands

```bash
# Remove stopped containers
podman container prune

# Remove unused images
podman image prune

# Remove unused volumes (⚠️ may delete data)
podman volume prune

# Complete cleanup (⚠️ removes everything)
podman system prune -a
```

---

## 🚨 Common Troubleshooting

### Podman Machine Issues

**Problem**: `Error: cannot connect to Podman socket`
```bash
# Solution: Start Podman machine
podman machine start
```

**Problem**: `Error: VM already exists`
```bash
# Solution: Remove and recreate machine
podman machine rm podman-machine-default
podman machine init
podman machine start
```

**Problem**: Container ports not accessible
```bash
# Solution: Check port forwarding and firewall
podman machine ssh
# Inside VM, check if ports are bound:
ss -tlnp | grep 5432
```

### Database Connection Issues

**Problem**: `Connection refused` to database
```bash
# Check container is running
podman ps

# Check database logs
podman logs postgis_container

# Test internal connectivity
podman exec postgis_container pg_isready -U user
```

**Problem**: Permission denied errors
```bash
# Linux: Update subuid/subgid
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid

# macOS/Windows: Restart machine
podman machine stop && podman machine start
```

### Registry Issues

**Problem**: `Error: unable to pull image`
```bash
# Add to /etc/containers/registries.conf (Linux):
echo 'unqualified-search-registries=["docker.io"]' | sudo tee -a /etc/containers/registries.conf

# Or use fully qualified image names:
podman pull docker.io/postgis/postgis:latest
```

### Performance Issues

**Problem**: Slow database performance
```bash
# Increase machine resources
podman machine rm podman-machine-default
podman machine init --memory 8192 --cpus 4 --disk-size 100
podman machine start
```

### Backup Database

```bash
# Create database backup
podman exec postgis_container pg_dump -U user $DATABASE_NAME > backup.sql

# Restore from backup
podman exec -i postgis_container psql -U user $DATABASE_NAME < backup.sql
```

---

## � Contributors

This project was developed by the Space Gravimetry research group at Delft University of Technology:

- **Jose Carlos Urra Llanusa** - Research Software Engineer
- **Joao De Teixeira da Encarnacao** - Research Scientist  
- **Selin Kubilay** - Research Engineer
- **João Guimarães** - Software Developer

## �📜 Licensing & Waiver

Licensed under the MIT License.

**Technische Universiteit Delft** hereby disclaims all copyright
interest in the program "GRACE Geospatial Data Processing Stack" written by the Author(s).

— ***Prof. H.G.C. (Henri) Werij***, Dean of Aerospace Engineering at TU Delft




