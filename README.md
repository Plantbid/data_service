# Landscape Supply Data Service - Interview Seed Project

This is the seed project for the Senior Data Engineer coding interview.

## Quick Start

### 1. Start the Services

Start the FastAPI service and MongoDB using Docker Compose:

```bash
docker compose up --build
```

This will start:
- FastAPI service on http://localhost:8000
- MongoDB on port 27017

### 2. Verify the Service is Running

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

You should see: `{"status":"ok"}`

### 3. Seed the Database

In a separate terminal, run the seed script to populate sample products:

```bash
docker compose exec api python scripts/seed_data.py
```

This will create 10 sample products in MongoDB.

### 4. Verify Database Contents

You can connect to MongoDB to inspect the data:

```bash
docker compose exec mongodb mongosh landscape_supply
```

Then run:
```javascript
db.products.find().pretty()
```

## Project Structure

```
.
├── database/          # Database connection setup
│   └── mongodb.py     # MongoDB connection management
├── models/            # Pydantic data models
│   ├── product.py     # Product schemas
│   └── quote.py       # Quote schemas with denormalized data
├── routes/            # API route handlers
│   ├── health.py      # Health check endpoint
│   ├── products.py    # Product endpoints (TO BE IMPLEMENTED)
│   └── quotes.py      # Quote endpoints (TO BE IMPLEMENTED)
├── scripts/           # Utility scripts
│   └── seed_data.py   # Database seeding script
├── main.py            # FastAPI application entry point
└── docker-compose.yml # Docker services configuration
```

## Development

### Installing Dependencies Locally (Optional)

If you want to run the service locally without Docker:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Locally (Optional)

Make sure MongoDB is running, then:

```bash
export MONGODB_URL="mongodb://localhost:27017"
export MONGODB_DB_NAME="landscape_supply"
uvicorn main:app --reload
```

### Running Tests

```bash
venv/bin/pytest tests/ -v
```

Or if you have pytest installed globally:
```bash
pytest
```

## Stopping the Services

Press `Ctrl+C` in the terminal running Docker Compose, then run:

```bash
docker compose down
```

To remove volumes (database data):

```bash
docker compose down -v
```
