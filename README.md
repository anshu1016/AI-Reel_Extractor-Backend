# Reel Intelligence - Backend API

AI-powered video extraction platform for real estate professionals.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (via Supabase)
- **Background Jobs:** Huey
- **Authentication:** JWT
- **Cloud Storage:** Cloudinary
- **Email:** SendGrid
- **AI:** Claude API (Anthropic), Sarvam API

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 2. Setup Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 3. Setup Database

```bash
# Run migrations
alembic upgrade head

# (Optional) Seed test data
python scripts/seed_db.py
```

### 4. Run Development Server

```bash
# Start API server
uvicorn app.main:app --reload --port 5000

# In another terminal, start Huey worker
huey_consumer app.tasks.huey_config.huey --workers 2
```

### 5. Access API Documentation

Open <http://localhost:5000/docs> for interactive Swagger UI

## Project Structure

See ARCHITECTURE.md for detailed structure explanation.

## Deployment

See DEPLOYMENT.md for Railway deployment instructions.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## License

Proprietary
