# Database Setup Guide

## Option 1: Local PostgreSQL (Development)

### Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@17
brew services start postgresql@17
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE weather_insight;
CREATE USER weatheruser WITH ENCRYPTED PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE weather_insight TO weatheruser;
\q
```

### Update .env

```bash
DATABASE_URL=postgresql://weatheruser:yourpassword@localhost:5432/weather_insight
```

## Option 2: Free Cloud PostgreSQL (Recommended)

### Neon

1. Go to: https://neon.tech
2. Create account (free)
3. Create new project
4. Copy connection string
5. Add to `.env`

### Supabase

1. Go to: https://supabase.com
2. Create account (free)
3. Create new project
4. Get connection string from Settings → Database
5. Add to `.env`:

```bash
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
```

## Run Migrations

### Create Initial Migration

```bash
cd backend
source venv/bin/activate  # Or venv\Scripts\activate on Windows

# Generate migration from models
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Common Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# See migration history
alembic history

# Check current version
alembic current
```

## Verify Database

```python
# Test connection
python -c "from app.database import engine; print(engine.connect())"
```

## Troubleshooting

### Connection Refused
- Check PostgreSQL is running: `brew services list` (macOS)
- Check port is correct (default: 5432)
- Check firewall settings

### Authentication Failed
- Verify username/password in DATABASE_URL
- Check pg_hba.conf for authentication method

### Database Not Found
- Create database first: `createdb weather_insight`
- Or use `psql` commands above

## Production Considerations

- Use connection pooling (already configured in database.py)
- Enable SSL for cloud databases (add `?sslmode=require` to URL)
- Use strong passwords
- Never commit `.env` file
- Use environment variables in production
