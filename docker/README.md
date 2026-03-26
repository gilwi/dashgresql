# 🐘 PostgreSQL Docker Setup

Three independent PostgreSQL 16 databases, each pre-seeded with realistic data,
ready to be used by the Flet dashboard project.

---

## 🚀 Start / Stop

```bash
# Start all services (detached)
docker compose up -d

# Stop everything
docker compose down

# Reset everything (wipe volumes)
docker compose down -v
```

---

## 🗄️ Databases

| Service        | Container      | Port   | DB Name    | User  | Password |
|----------------|---------------|--------|------------|-------|----------|
| E-Commerce     | pg_ecommerce  | 5433   | ecommerce  | admin | admin123 |
| HR             | pg_hr         | 5434   | hr         | admin | admin123 |
| Analytics      | pg_analytics  | 5435   | analytics  | admin | admin123 |

All databases are accessible on `localhost` from the host machine.

### Connection strings

```
postgresql://admin:admin123@localhost:5433/ecommerce
postgresql://admin:admin123@localhost:5434/hr
postgresql://admin:admin123@localhost:5435/analytics
```

---

## 📦 Database Schemas

### 1. `ecommerce`
| Table         | Description                        |
|---------------|------------------------------------|
| categories    | Product categories (5 rows)        |
| products      | Products with SKU, price, stock (13)|
| customers     | Customers from various countries (10)|
| orders        | Orders with status and total (13)  |
| order_items   | Line items per order               |

### 2. `hr`
| Table               | Description                          |
|---------------------|--------------------------------------|
| departments         | 5 departments with budgets           |
| employees           | 15 employees with salaries, managers |
| leave_requests      | Vacation/sick leave requests         |
| performance_reviews | Quarterly review scores              |

### 3. `analytics`
| Table          | Description                               |
|----------------|-------------------------------------------|
| apps           | 3 tracked apps (web + iOS + admin portal) |
| daily_metrics  | 30 days of DAU, sessions, revenue per app |
| events         | 500 random events (page_view, purchase…)  |
| funnels        | Signup funnel steps with conversion data  |

---

## 🖥️ pgAdmin (optional)

Available at **http://localhost:5050**

```
Email:    admin@local.dev
Password: admin123
```

To add a server in pgAdmin:
- Host: `pg_ecommerce` (or `pg_hr` / `pg_analytics`)
- Port: `5432`  ← use the internal port inside Docker network
- Username: `admin`
- Password: `admin123`

---

## 🐍 Python connection example (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="ecommerce",
    user="admin",
    password="admin123"
)
```

Or with `asyncpg`:

```python
import asyncpg

conn = await asyncpg.connect(
    "postgresql://admin:admin123@localhost:5433/ecommerce"
)
```
