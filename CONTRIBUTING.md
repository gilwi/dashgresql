# Dashgresql — Architecture & Contribution Guide

> This document explains how the project is structured, how the frontend and backend communicate, and how to contribute new features.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Authentication](#3-authentication)
4. [API Design](#4-api-design)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Adding a New Feature](#6-adding-a-new-feature)
7. [Security Rules](#7-security-rules)
8. [Common Pitfalls](#8-common-pitfalls)

---

## 1. Project Overview

Dashgresql is a self-hosted PostgreSQL management dashboard. Users log in, register external PostgreSQL servers (with encrypted credentials), and inspect their schemas, tables, columns, indexes, constraints, and live connection stats.

```
dashgresql/
├── dashgresql-back/    # Flask REST API
├── dashgresql-front/   # Vue 3 + Vite SPA
└── docker/             # Docker Compose setup
```

The frontend and backend are fully decoupled. The Vue app talks exclusively to the Flask API over HTTP — there is no server-side rendering.

---

## 2. Tech Stack

### Backend
| Layer | Tool |
|---|---|
| Framework | Flask (app factory pattern with blueprints) |
| Auth | flask-jwt-extended (JWT Bearer tokens) |
| CORS | flask-cors (origin whitelist via env var) |
| ORM | Flask-SQLAlchemy + Flask-Migrate |
| PostgreSQL driver | psycopg2-binary |
| Credential encryption | cryptography (Fernet symmetric encryption) |
| Password hashing | werkzeug (pbkdf2) |
| Package manager | uv |

### Frontend
| Layer | Tool |
|---|---|
| Framework | Vue 3 (Composition API + `<script setup>`) |
| Router | Vue Router 4 |
| State | Pinia |
| HTTP | Axios (centralised instance with interceptors) |
| Styling | Tailwind CSS (custom Material Design token theme) |
| Build | Vite |
| Package manager | pnpm |

---

## 3. Authentication

Authentication uses **JWT Bearer tokens**. There are no cookies or sessions.

### Flow

```
POST /api/auth/login  { username, password }
  └── Flask verifies password with check_password_hash()
  └── Returns { access_token }
  └── Vue stores token in sessionStorage
  └── Vue calls GET /api/auth/me to populate auth store

Every subsequent request:
  └── Axios interceptor attaches Authorization: Bearer <token>

On 401 response:
  └── Axios interceptor clears token + redirects to /login
```

### Key files

| File | Role |
|---|---|
| `app/auth.py` | `/api/auth/login`, `/api/auth/me`, `/api/auth/logout` endpoints |
| `src/stores/auth.js` | Pinia store — holds token, user, isAuthenticated |
| `src/api/index.js` | Axios instance — attaches token, handles 401 globally |
| `src/router/index.js` | Route guards — protects pages, rehydrates user on refresh |

### Route guard logic

```javascript
// On every navigation:
// 1. If token exists but user is null (page refresh) → fetch user from /api/auth/me
//    If that fails → logout + redirect to /login
// 2. If route requires auth and not authenticated → redirect to /login
// 3. If already authenticated and navigating to /login → redirect to /
```

### Passwords

- **User passwords** — hashed with `werkzeug.security.generate_password_hash` (one-way, never decryptable)
- **PostgreSQL connection passwords** — encrypted with `cryptography.fernet` (reversible, needed to open connections)

These are fundamentally different problems — never use hashing for connection credentials.

---

## 4. API Design

All endpoints are prefixed with `/api/` and require a valid JWT unless stated otherwise.

### Auth — `/api/auth/`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/login` | ❌ | Returns a JWT token |
| GET | `/me` | ✅ | Returns current user info |
| POST | `/logout` | ✅ | Client-side logout signal |

### Databases — `/api/databases/`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | ✅ | List all databases for current user |
| POST | `/` | ✅ | Register a new external database |
| GET | `/{id}/check` | ✅ | Check single DB connection + live stats |
| GET | `/check-all` | ✅ | Check all DBs at once |
| GET | `/{id}/schemas` | ✅ | List schemas, tables, row counts, sizes |
| GET | `/{id}/schemas/{s}/tables/{t}` | ✅ | Full table detail (columns, constraints, indexes) |

### Blueprint registration

Blueprints are registered in `create_app()` inside `app/__init__.py`:

```python
from .auth import auth_bp
from .databases import databases_bp

app.register_blueprint(auth_bp,       url_prefix='/api/auth')
app.register_blueprint(databases_bp,  url_prefix='/api/databases')
```

### Adding a new blueprint

1. Create `app/your_feature.py`
2. Define `your_feature_bp = Blueprint('your_feature', __name__)`
3. Add routes with `@your_feature_bp.route(...)`
4. Import and register in `create_app()`

---

## 5. Frontend Architecture

### Directory structure

```
src/
├── api/
│   └── index.js          # Axios instance — single point of contact with API
├── stores/
│   └── auth.js           # Pinia auth store (token, user, login, logout)
├── router/
│   └── index.js          # Routes + navigation guards
├── views/
│   ├── LoginView.vue     # Public — login form
│   ├── HomeView.vue      # Protected — database dashboard
│   ├── AboutView.vue     # Protected — schema explorer
│   └── ErrorView.vue     # Reusable 4xx error page
├── layouts/
│   └── DashboardLayout.vue  # Wraps all protected views (sidebar + mobile nav)
└── components/
    └── BaseModal.vue     # Reusable modal component
```

### Axios instance (`src/api/index.js`)

All API calls go through a single Axios instance. Never use `fetch` or create a second Axios instance.

```javascript
import api from '@/api'

// Usage in any component or store
const res = await api.get('/api/databases/')
const res = await api.post('/api/databases/', { name, host, ... })
```

The instance automatically:
- Attaches `Authorization: Bearer <token>` to every request
- Redirects to `/login` on any `401` response
- Reads `VITE_API_URL` from `.env` as the base URL

### Pinia auth store (`src/stores/auth.js`)

```javascript
const auth = useAuthStore()

auth.isAuthenticated  // computed — true if token exists
auth.user             // { id, username } or null
await auth.login(username, password)
await auth.logout()
await auth.fetchUser()
```

### Dev proxy (Vite)

In development, Vite proxies `/api/*` to `http://localhost:5000` so the browser never makes a direct cross-origin request. This is configured in `vite.config.js` and means CORS issues only surface in Docker or production.

### CORS (Flask)

Allowed origins are controlled entirely by the `CORS_ORIGINS` environment variable — never hardcoded. Multiple origins are comma-separated:

```dotenv
# Local dev
CORS_ORIGINS=http://localhost:5173

# Docker
CORS_ORIGINS=http://localhost:5173,http://dashgresql_front:5173

# Production
CORS_ORIGINS=https://yourdomain.com
```

---

## 6. Adding a New Feature

### Full-stack feature checklist

#### Backend

- [ ] Add or update a model in `app/models.py` — always implement `to_dict()`, never expose `_password`
- [ ] If the model stores sensitive data, use Fernet encryption from `app/crypto.py`
- [ ] Create or update a blueprint in `app/`
- [ ] Protect every endpoint with `@jwt_required()`
- [ ] Validate all request inputs — return `400` with a clear `{ error }` message for missing/invalid fields
- [ ] Register the blueprint in `create_app()` if new
- [ ] Run `flask db migrate -m "description"` and `flask db upgrade` for model changes

#### Frontend

- [ ] Add API calls in the relevant view using `api` from `@/api` — never inline `fetch`
- [ ] Add loading and error states to every async operation
- [ ] If state is shared across views, add it to a Pinia store
- [ ] Add `meta: { requiresAuth: true }` to any new protected route
- [ ] Handle errors from `err.response?.data?.error` for API errors

### Example: adding a new protected page

**Backend** — new blueprint `app/stats.py`:
```python
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/', methods=['GET'])
@jwt_required()
def get_stats():
    return jsonify({ 'uptime': '99.99%' }), 200
```

**Frontend** — new view `src/views/StatsView.vue`:
```vue
<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const stats = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/api/stats/')
    stats.value = res.data
  } catch (err) {
    error.value = err.response?.data?.error ?? 'Failed to load stats'
  }
})
</script>
```

**Router** — add the route:
```javascript
{
  path: '/stats',
  component: () => import('@/views/StatsView.vue'),
  meta: { requiresAuth: true },
}
```

---

## 7. Security Rules

These are non-negotiable across the entire codebase.

| Rule | Detail |
|---|---|
| **Never store plain-text passwords** | User passwords → `werkzeug` hash. Connection passwords → Fernet encryption |
| **Never expose `_password`** | `to_dict()` must never include the encrypted password field |
| **Never hardcode secrets** | All keys, tokens, and credentials live in `.env` files only |
| **Never commit `.env`** | `.gitignore` and `.dockerignore` must always exclude `.env` |
| **Always validate inputs** | Check for missing fields before touching the database |
| **Use the same error for bad credentials** | `"Invalid credentials"` for both wrong username and wrong password — never reveal which one failed |

---

## 8. Common Pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| Row counts never update | `pg_class.reltuples` is a stale estimate | Use `COUNT(*)` for small tables, `pg_stat_user_tables` for large ones |
| `AssertionError: overwriting endpoint` | Duplicate function names across blueprint routes | Add `endpoint='unique_name'` to `@route()` decorators |
| Token lost on page refresh | Token only in memory | Token is in `sessionStorage` — rehydration runs in `router.beforeEach` via `auth.fetchUser()` |
| `quote_ident` TypeError | Missing `conn` argument | Always call `quote_ident(value, conn)` — it requires the connection as second argument |
