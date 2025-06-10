# Supabase Integration Package

A reusable Supabase integration package for FastAPI applications.

## Installation

1. Copy the `supabase_integration` folder to your project
2. Add the following dependencies to your `requirements.txt`:
```
supabase>=2.0.0
fastapi>=0.109.0
pydantic-settings>=2.0.0
```

## Environment Variables

Create a `.env` file with your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_JWT_SECRET=your_jwt_secret  # Optional
```

## Usage

### Basic Authentication

```python
from fastapi import FastAPI, Depends
from supabase_integration import auth

app = FastAPI()

@app.get("/protected-route")
async def protected_route(user = Depends(auth.get_current_user)):
    return {"message": f"Hello {user.user.email}"}
```

### Using Supabase Client

```python
from supabase_integration import get_supabase_client

# Get the Supabase client
supabase = get_supabase_client()

# Use the client
data = supabase.table('your_table').select("*").execute()
```

## Features

- Cached Supabase client
- JWT token verification
- Environment-based configuration
- FastAPI integration
- Type hints and documentation 