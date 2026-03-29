# dashgresql

> **The Data Architect** — A self-hosted PostgreSQL management dashboard with a Vue.js frontend and a Flask REST API backend.

---

## Project Structure

```
dashgresql/
├── dashgresql-back/       # Flask REST API
│   ├── app/               # Application package (blueprints, models, utils)
│   ├── config.py          # Configuration (env-based)
│   ├── dashgresql.py      # App entry point
│   ├── migrations/        # Flask-Migrate database migrations
│   └── requirements.txt   # Python dependencies
├── dashgresql-front/      # Vue 3 + Vite frontend
│   ├── src/               # Source (views, components, stores, router, api)
│   ├── public/            # Static assets
│   └── vite.config.js     # Vite config (includes API proxy)
├── docker/                # Docker Compose setup
│   ├── docker-compose.yml
│   └── init/              # DB init scripts
└── README.md
```

---

## Prerequisites

| Tool | Tested version | Purpose |
|---|---|---|
| [uv](https://github.com/astral-sh/uv) | 0.11.2 | Python package & venv management |
| Python | 3.14.3 | Backend runtime (managed by uv) |
| [pnpm](https://pnpm.io) | 10.33.0 | Node package management |
| Node.js | >= 20 | Frontend runtime |
| PostgreSQL | >= 14 | Target databases (external) |

Install `uv` (also installs and manages Python for you):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install `pnpm`:
```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

---

## Environment Setup

### Backend (`dashgresql-back/`)

Copy the example env file and fill in your values:

```bash
cp dashgresql-back/.env.example dashgresql-back/.env
```

```dotenv
# dashgresql-back/.env

FLASK_APP=dashgresql.py
FLASK_ENV=development

# Encryption key for stored PostgreSQL credentials
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
SECRET_KEY=change-me-use-a-random-string
JWT_SECRET_KEY=change-me-use-another-random-string

# Internal app database (SQLite for dev, PostgreSQL recommended for prod)
DATABASE_URL=sqlite:///app.db
```

> ⚠️ Never commit `.env` to version control. All secrets must stay out of source code.

### Frontend (`dashgresql-front/`)

```bash
cp dashgresql-front/.env.example dashgresql-front/.env
```

```dotenv
# dashgresql-front/.env
VITE_API_URL=/api
```

---

## Installation

### Backend

```bash
cd dashgresql-back

# Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# Apply database migrations
uv run flask db upgrade
```

### Frontend

```bash
cd dashgresql-front
pnpm install
```

---

## Running in Development

### Backend

```bash
cd dashgresql-back
uv run flask run
# API available at http://localhost:5000
```

### Frontend

```bash
cd dashgresql-front
pnpm dev
# App available at http://localhost:5173
# API calls proxied to http://localhost:5000 via Vite
```

> Run both simultaneously — the Vite dev server proxies `/api/*` requests to Flask automatically, so no CORS issues during development.

---

## Building for Production

### Frontend

```bash
cd dashgresql-front
pnpm build
# Output in dashgresql-front/dist/
```

### Backend

Run with a production WSGI server (Gunicorn recommended):

```bash
cd dashgresql-back
uv pip install gunicorn
uv run gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## Docker

A Docker Compose setup is available for a fully containerised deployment:

```bash
cd docker
docker compose up --build
```

See [`docker/README.md`](docker/README.md) for configuration details.

---

## Helper Scripts

Save these at the project root for convenience.

### `scripts/setup.sh` — Full first-time setup

```bash
#!/usr/bin/env bash
set -e

echo "→ Setting up backend..."
cd dashgresql-back
uv venv
uv pip install -r requirements.txt
uv run flask db upgrade
cd ..

echo "→ Setting up frontend..."
cd dashgresql-front
pnpm install
cd ..

echo "✓ Setup complete. Copy .env.example files and fill in your secrets before running."
```

### `scripts/dev.sh` — Start both servers in development

```bash
#!/usr/bin/env bash
set -e

# Start Flask in background
echo "→ Starting backend..."
cd dashgresql-back
uv run flask run &
BACK_PID=$!
cd ..

# Start Vite
echo "→ Starting frontend..."
cd dashgresql-front
pnpm dev &
FRONT_PID=$!
cd ..

echo "✓ Backend: http://localhost:5000"
echo "✓ Frontend: http://localhost:5173"
echo "  Press Ctrl+C to stop both servers."

# Kill both on exit
trap "kill $BACK_PID $FRONT_PID" EXIT
wait
```

### `scripts/build.sh` — Build frontend for production

```bash
#!/usr/bin/env bash
set -e

echo "→ Building frontend..."
cd dashgresql-front
pnpm build
cd ..

echo "✓ Build output: dashgresql-front/dist/"
```

Make the scripts executable:

```bash
chmod +x scripts/setup.sh scripts/dev.sh scripts/build.sh
```

---

## Key Dependencies

### Backend

| Package | Purpose |
|---|---|
| Flask | Web framework |
| Flask-JWT-Extended | JWT authentication |
| Flask-CORS | Cross-origin request handling |
| Flask-SQLAlchemy | ORM |
| Flask-Migrate | Database migrations |
| psycopg2-binary | PostgreSQL driver |
| cryptography | Fernet encryption for stored credentials |
| python-dotenv | Environment variable loading |

### Frontend

| Package | Purpose |
|---|---|
| Vue 3 | UI framework |
| Vue Router | Client-side routing |
| Pinia | State management |
| Axios | HTTP client with interceptors |
| Tailwind CSS | Utility-first styling |
| Vite | Dev server & bundler |

---

## Authentication Flow

```
POST /api/auth/login  →  returns JWT access token
                          stored in sessionStorage

All subsequent requests  →  Authorization: Bearer <token>
                             attached automatically via Axios interceptor

401 response  →  token cleared, redirect to /login
```

---

## License

Private — All rights reserved.
