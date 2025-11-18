# Knowledge Management Backend

A FastAPI-based backend for a personal knowledge management system with SQLAlchemy for database integration.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **Pydantic**: Data validation using Python type annotations
- **Environment Configuration**: Separate settings for development and production
- **Unit Tests**: Comprehensive test suite with pytest
- **Linting**: Code quality checks with ruff

## Project Structure

```
knowledge-management-backend/
├── app/
│   ├── api/              # API routes
│   │   ├── knowledge_items.py
│   │   └── router.py
│   ├── core/             # Core configuration
│   │   └── config.py
│   ├── db/               # Database configuration
│   │   └── base.py
│   ├── models/           # SQLAlchemy models
│   │   └── knowledge_item.py
│   ├── schemas/          # Pydantic schemas
│   │   └── knowledge_item.py
│   ├── __init__.py
│   └── main.py           # FastAPI application entry point
├── tests/                # Test files
│   ├── conftest.py
│   ├── test_knowledge_items.py
│   └── test_main.py
├── scripts/              # Utility scripts
│   ├── lint.sh
│   ├── test.sh
│   └── lint-and-test.sh
├── requirements.txt      # Python dependencies
├── pytest.ini           # Pytest configuration
├── ruff.toml            # Ruff linting configuration
└── README.md

```

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- git

## Setup Instructions

### 1. Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
# Navigate to the project directory
cd knowledge-management-backend

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

Once the virtual environment is activated, install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Configuration

The application uses environment variables for configuration. You can create a `.env` file in the project root (it's already in `.gitignore`):

```bash
# Copy the example (if you created one) or create a new .env file
# For development, the defaults in config.py are sufficient
```

Example `.env` file:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./knowledge_management.db
API_V1_PREFIX=/api/v1
PROJECT_NAME=Knowledge Management API
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

For production, you might want to use PostgreSQL:

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:password@localhost/knowledge_management
```

### 4. Initialize the Database

The database will be automatically created when you first run the application. For SQLite, the database file will be created in the project root.

### 5. Run the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

### 6. Run Tests

Run the test suite:

```bash
# Using pytest directly
pytest

# Or using the test script
./scripts/test.sh
```

### 7. Run Linter

Check code quality:

```bash
# Using ruff directly
ruff check app tests

# Or using the lint script
./scripts/lint.sh
```

### 8. Run Both Linter and Tests

```bash
./scripts/lint-and-test.sh
```

## API Endpoints

### Knowledge Items

- `POST /api/v1/knowledge-items/` - Create a new knowledge item
- `GET /api/v1/knowledge-items/` - List all knowledge items (supports `skip`, `limit`, `category` query params)
- `GET /api/v1/knowledge-items/{item_id}` - Get a specific knowledge item
- `PUT /api/v1/knowledge-items/{item_id}` - Update a knowledge item
- `DELETE /api/v1/knowledge-items/{item_id}` - Delete a knowledge item

### Other Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Example API Usage

### Create a Knowledge Item

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge-items/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Best Practices",
    "content": "Always use type hints and virtual environments",
    "tags": "python, best-practices",
    "category": "programming"
  }'
```

### List All Knowledge Items

```bash
curl "http://localhost:8000/api/v1/knowledge-items/"
```

### Get a Specific Item

```bash
curl "http://localhost:8000/api/v1/knowledge-items/1"
```

### Update an Item

```bash
curl -X PUT "http://localhost:8000/api/v1/knowledge-items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content"
  }'
```

### Delete an Item

```bash
curl -X DELETE "http://localhost:8000/api/v1/knowledge-items/1"
```

## Database Models

### KnowledgeItem

- `id` (Integer, Primary Key)
- `title` (String, Required)
- `content` (Text, Optional)
- `tags` (String, Optional) - Comma-separated tags
- `category` (String, Optional)
- `created_at` (DateTime, Auto-generated)
- `updated_at` (DateTime, Auto-updated)

## Development

### Running in Development Mode

The application runs with auto-reload enabled by default:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running in Production

For production, use a production ASGI server like Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or use Uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

The test suite includes:

- Unit tests for all API endpoints
- Tests for CRUD operations
- Validation tests
- Error handling tests

Run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

## Linting

The project uses `ruff` for linting. Configuration is in `ruff.toml`.

To auto-fix issues:

```bash
ruff check --fix app tests
```

## Database Migrations (Optional)

For production use, consider using Alembic for database migrations:

```bash
# Initialize Alembic (already in requirements.txt)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run linter and tests: `./scripts/lint-and-test.sh`
4. Commit your changes
5. Push to the branch
6. Create a pull request

## License

This project is open source and available under the MIT License.

