# FastAPI Todo API

A well-structured FastAPI application with user authentication, todo management, and comprehensive test coverage.

## Project Structure

```
app/
├── core/              # Core functionality (config, database, security)
├── models/            # SQLAlchemy database models
├── schemas/           # Pydantic schemas
├── services/          # Business logic layer
├── api/               # API routes and dependencies
│   ├── deps.py        # Dependency injection
│   └── v1/            # API v1 endpoints
└── main.py            # Application entry point

tests/                 # Comprehensive test suite
├── conftest.py        # Test fixtures
├── test_core_*.py     # Core module tests
├── test_models.py     # Model tests
├── test_schemas.py    # Schema tests
├── test_services_*.py # Service layer tests
└── test_api_*.py      # API endpoint tests
```

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the server:
```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

Run all tests with coverage:
```bash
pytest
```

Run tests with detailed output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_api_auth.py
```

Generate HTML coverage report:
```bash
pytest --cov=app --cov-report=html
```

## Test Coverage

This project has 100% test coverage across:
- Core modules (config, security, database)
- Database models
- Pydantic schemas
- Service layer (user, todo, auth services)
- API endpoints (auth, users, verification, todos)

## API Endpoints

### Authentication
- `POST /api/v1/register` - Register new user
- `POST /api/v1/login` - Login with email and password
- `POST /api/v1/verify-otp` - Verify email with OTP
- `POST /api/v1/resend-otp` - Resend verification OTP
- `POST /api/v1/refresh` - Refresh access token
- `POST /api/v1/change-password` - Change password
- `POST /api/v1/forgot-password` - Request password reset
- `POST /api/v1/reset-password` - Reset password with OTP

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user

### Todos
- `POST /api/v1/todos/` - Create todo
- `GET /api/v1/todos/` - List todos (with pagination and filters)
- `GET /api/v1/todos/{id}` - Get single todo
- `PUT /api/v1/todos/{id}` - Update todo
- `PATCH /api/v1/todos/{id}/complete` - Toggle completion
- `PATCH /api/v1/todos/{id}/archive` - Toggle archive
- `DELETE /api/v1/todos/{id}` - Delete todo

## Environment Variables

Create a `.env` file:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./sql_app.db
```

## Features

- User registration with email verification (OTP)
- JWT-based authentication with access and refresh tokens
- Password change and reset functionality
- CRUD operations for todos
- Todo completion and archiving
- Pagination and filtering for todos
- Comprehensive test coverage (100%)
- Clean, modular architecture with service layer