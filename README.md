# Geospatial Data Processing Stack

This project sets up a scalable geospatial data processing pipeline using **PostgreSQL + PostGIS**, **SQLAlchemy**, and **Docker Compose**. It allows for efficient ingestion, validation, and querying of geospatial satellite data.

## 🚀 Quick Start

### 1️⃣ Prerequisites
Ensure you have the following installed:
- **Docker & Docker Compose**
	- Installation Guide for [Docker Engine on Ubuntu](https://docs.docker.com/compose/install/)
	- Installation Guide for [Docker Compose standalone on Linux](https://docs.docker.com/compose/install/standalone/#on-linux)
- **Python 3.8+**
- **pip** package manager

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

