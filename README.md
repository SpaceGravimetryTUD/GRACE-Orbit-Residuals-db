# Geospatial Data Processing Stack

This project sets up a scalable geospatial data processing pipeline using **PostgreSQL + PostGIS**, **SQLAlchemy**, and **Docker Compose**. It allows for efficient ingestion, validation, and querying of geospatial satellite data.

## 🚀 Quick Start

### 1️⃣ Prerequisites

For this project we work on Unix environment. In case of using a Windows machine, we recommend you to [install the Windows Subsystem for Linux (WLS2)](https://learn.microsoft.com/en-us/windows/wsl/install) and follow the steps recommended for Linux/Ubuntu.

Further, ensure you have the following installed in you Unix environment:
- **Docker & Docker Compose**
	- Installation Guide for [Docker Engine on Ubuntu](https://docs.docker.com/compose/install/)
	- Installation Guide for [Docker Compose standalone on Linux](https://docs.docker.com/compose/install/standalone/#on-linux)
- **Python 3.8+**
- **pip** package manager

Note: In the [Docker website](https://docs.docker.com/) you may see mentioned that WSL users should install Docker Desktop instead of following installation guides for Docker Engine & Docker Compose on Linux/Ubuntu system. For this project we opt for **not** following this advice. By following the Linux/Ubuntu installation guides we succeed to reproduce the steps bellow, even when using WSL2. By using Docker Desktop instead, we cannot guarantee that the same reproduction will be successful.

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

### 3️⃣ Start the Database with Docker Compose

```bash
docker-compose up -d
```

This starts a PostGIS-powered PostgreSQL database.

Verify the container is running:

```bash
docker ps
```

### 4️⃣ Install Python Dependencies

```bash
poetry install
```

### 5️⃣ Initialize the Database

Run the following to create tables:

```bash
poetry run python
>>> import src.models
>>> src.models.init_db()
>>> exit()
 ```

Verify inside PostgreSQL the sattelite_data:

```
docker exec -it postgis_container psql -U user -d geospatial_db -c "\d satellite_data;"
```

### 6️⃣ (Optional) Connect to PostgreSQL

```bash
docker exec -it postgis_container psql -U user -d geospatial_db
```

