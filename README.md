# GRACE Geospatial Data Processing Stack

This project sets up a scalable geospatial data processing pipeline using **PostgreSQL + PostGIS**, **SQLAlchemy**, and **Docker Compose**. It facilitates efficient ingestion, validation, and querying of high-frequency satellite data from the GRACE mission. 

## 🌍 Context & Background

We work with high-frequency geospatial time-series data from the GRACE satellite mission, specifically Level-1B range-rate residuals derived from inter-satellite Ka-band observations. These residuals may contain unexploited high-frequency geophysical signals used for scientific applications.

### Key dataset characteristics:

- Temporal resolution: 5-second intervals
- Geospatial attributes: Latitude, longitude, altitude for two satellites (GRACE A & B)
- Data volume: 2002–2017, \~6.3 million records per year (\~95 million total)
- Queries of interest: Filtering by time span, spatial regions, and signal characteristics (statistical analysis)

## 🚀 Quick Start

### 1️⃣ Prerequisites

This project is designed to run in a Unix environment. If you are using a Windows machine, we recommend installing the [Windows Subsystem for Linux (WSL2)](https://learn.microsoft.com/en-us/windows/wsl/install) and following the steps recommended for Linux/Ubuntu.

Ensure the following dependencies are installed:

- **Docker & Docker Compose** (for development; see note below on production use)
  - [Docker Engine on Ubuntu](https://docs.docker.com/compose/install/)
  - [Docker Compose standalone on Linux](https://docs.docker.com/compose/install/standalone/#on-linux)
- **Python 3.8+**
- **pip** package manager

> **Note:** We recommend installing Docker Engine & Docker Compose using the Linux/Ubuntu installation guides, if you are in a windows machine we recommend you use WSL2 (Windows Linux Subsystem).

#### Production Use

We recommend using **Podman** instead of Docker for production environments, as it is compatible with Docker commands and provides better security and rootless containerization. We plan to migrate fully to Podman in the future.

Ensure the following dependencies are installed:

 - **Podman** via `sudo apt -y install podman`
 - **Python 3.8+**
 - **pip** package manager
 - **podman-compose** via pip

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/SpaceGravimetryTUD/GRACE-Orbit-Residuals-db/tree/main
cd GRACE-Orbit-Residuals-db
```

### 3️⃣ Install Python Dependencies

```bash
poetry install
```

### 4️⃣ Start the Database with Podman Compose

```bash
podman-compose -f ./docker-compose.yml up -d
```

This launches a PostgreSQL database with PostGIS support.

Verify the container is running:

```bash
podman ps
```

### 5️⃣ Set file location for data to be uploaded into the database

For demonstration purposes we are going to use the following file:

'''bash
data/flat-data-test.pkl
''' 

### ⚙️ Environment Configuration

To run the project locally — including the tests — you need to create a `.env` file in the project root directory. This file should define the necessary environment variables for database access and test data.

### Required variables:

- `DATABASE_URL`: the full SQLAlchemy connection string to the PostGIS-enabled PostgreSQL instance
- `TEST_DATA_PATH`: path to the `.pkl` file used for inserting sample satellite data during testing

### 📄 Example `.env` file

```ini
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/geospatial_db
TEST_DATA_PATH=data/flat-data-test.pkl
```

Make sure the database container is running (e.g., via `podman-compose -f ./docker-compose.yml up -d`) before running any scripts or tests.

### 6️⃣ Initialize the Database

To create and populate tables, run:

```bash
# Import the functions from their correct locations
from src.models import init_db
from scripts.populate_db import populate_db

# Call the functions
init_db()
populate_db('data/flat-data-test.pkl')
```

Verify the database schema inside PostgreSQL:

```bash
podman exec -it postgis_container psql -U user -d geospatial_db -c "\d satellite_data;"
```

To display data uploaded into the table satellite_data:

```bash
podman exec -it postgis_container psql -U user -d geospatial_db -c "TABLE satellite_data"
```

### 7 (Optional) Connect to PostgreSQL

```bash
podman exec -it postgis_container psql -U user -d geospatial_db
```

### 🧪 Running Tests (Requires Local Database)

Before running the test suite, you **must ensure that the PostgreSQL + PostGIS database is running locally** and properly initialized.

The tests are designed to validate the data ingestion, model behavior, and query logic against a real database backend, not mocks or in-memory databases.

Follow these steps:

1. **Start the database with Docker Compose (if not already running):**

   ```bash
   docker-compose up -d
   ```

2. **Initialize the database with schema and sample data:**

```bash
# Import the functions from their correct locations
from src.models import init_db
from scripts.populate_db import populate_db

# Call the functions
init_db()
populate_db('data/flat-data-test.pkl')
```

3. **Run the tests using Poetry:**

   ```bash
   poetry run pytest
   ```

> ⚠️ **Important:** Tests will fail if the database is not running or not properly initialized. Ensure the `satellite_data` table exists and is populated with test data.


## 📜 Licensing & Waiver

Licensed under MIT, subject to the following waiver:

**Technische Universiteit Delft** hereby disclaims all copyright interest in the program "GRACE Geospatial Data Processing Stack" written by the Author(s).

***Prof. H.G.C. (Henri) Werij***, Dean of Aerospace Engineering at TU Delft**

Copyright (c) 2025 .

