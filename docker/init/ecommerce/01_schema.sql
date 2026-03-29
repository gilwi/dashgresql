-- ============================================================
-- E-COMMERCE DATABASE
-- ============================================================
CREATE SCHEMA app;

CREATE TABLE app.categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE app.products (
    id          SERIAL PRIMARY KEY,
    category_id INT REFERENCES app.categories(id),
    name        VARCHAR(200) NOT NULL,
    sku         VARCHAR(50) UNIQUE NOT NULL,
    price       NUMERIC(10,2) NOT NULL,
    stock       INT DEFAULT 0,
    active      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE app.customers (
    id         SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(200) UNIQUE NOT NULL,
    country    VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE app.orders (
    id          SERIAL PRIMARY KEY,
    customer_id INT REFERENCES app.customers(id),
    status      VARCHAR(50) DEFAULT 'pending',
    total       NUMERIC(10,2),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE app.order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INT REFERENCES app.orders(id),
    product_id INT REFERENCES app.products(id),
    quantity   INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL
);

-- ── Seed data ────────────────────────────────────────────────

INSERT INTO app.categories (name, description) VALUES
    ('Electronics',   'Gadgets and devices'),
    ('Clothing',      'Apparel and accessories'),
    ('Books',         'Physical and digital books'),
    ('Home & Garden', 'Furniture and décor'),
    ('Sports',        'Fitness and outdoor gear');

INSERT INTO app.products (category_id, name, sku, price, stock) VALUES
    (1, 'Wireless Headphones Pro',  'EL-001', 149.99, 230),
    (1, '4K Smart TV 55"',          'EL-002', 799.00,  45),
    (1, 'Mechanical Keyboard RGB',  'EL-003',  89.99, 310),
    (1, 'USB-C Hub 7-in-1',         'EL-004',  39.99, 520),
    (2, 'Classic Denim Jacket',     'CL-001',  69.99, 180),
    (2, 'Running Shoes V3',         'CL-002', 119.99, 400),
    (2, 'Wool Winter Coat',         'CL-003', 199.99,  90),
    (3, 'Python Crash Course',      'BK-001',  29.99, 600),
    (3, 'The Art of SQL',           'BK-002',  34.99, 280),
    (4, 'Ergonomic Office Chair',   'HG-001', 349.00,  55),
    (4, 'Standing Desk Converter',  'HG-002', 229.99,  70),
    (5, 'Yoga Mat Premium',         'SP-001',  49.99, 350),
    (5, 'Resistance Bands Set',     'SP-002',  24.99, 700);

INSERT INTO app.customers (first_name, last_name, email, country) VALUES
    ('Alice',   'Martin',   'alice@example.com',   'France'),
    ('Bob',     'Smith',    'bob@example.com',     'USA'),
    ('Clara',   'Dupont',   'clara@example.com',   'France'),
    ('David',   'Lee',      'david@example.com',   'UK'),
    ('Emma',    'Müller',   'emma@example.com',    'Germany'),
    ('Fabio',   'Rossi',    'fabio@example.com',   'Italy'),
    ('Grace',   'Kim',      'grace@example.com',   'South Korea'),
    ('Héctor',  'Lopez',    'hector@example.com',  'Spain'),
    ('Ingrid',  'Svensson', 'ingrid@example.com',  'Sweden'),
    ('James',   'Brown',    'james@example.com',   'USA');

INSERT INTO app.orders (customer_id, status, total, created_at) VALUES
    (1,  'completed', 239.98, NOW() - INTERVAL '30 days'),
    (2,  'completed', 799.00, NOW() - INTERVAL '25 days'),
    (3,  'shipped',    89.99, NOW() - INTERVAL '20 days'),
    (4,  'completed', 349.00, NOW() - INTERVAL '18 days'),
    (5,  'completed', 189.98, NOW() - INTERVAL '15 days'),
    (6,  'pending',    64.98, NOW() - INTERVAL '10 days'),
    (7,  'completed', 229.99, NOW() - INTERVAL '8 days'),
    (8,  'shipped',   149.99, NOW() - INTERVAL '5 days'),
    (9,  'completed',  74.98, NOW() - INTERVAL '3 days'),
    (10, 'pending',   119.99, NOW() - INTERVAL '1 day'),
    (1,  'completed', 199.99, NOW() - INTERVAL '60 days'),
    (2,  'completed',  39.99, NOW() - INTERVAL '45 days'),
    (3,  'cancelled',  69.99, NOW() - INTERVAL '50 days');

INSERT INTO app.order_items (order_id, product_id, quantity, unit_price) VALUES
    (1,  1, 1, 149.99), (1,  3, 1, 89.99),
    (2,  2, 1, 799.00),
    (3,  3, 1, 89.99),
    (4,  10,1, 349.00),
    (5,  5, 1, 69.99),  (5,  6, 1, 119.99),
    (6,  8, 1, 29.99),  (6,  9, 1, 34.99),
    (7,  11,1, 229.99),
    (8,  1, 1, 149.99),
    (9,  12,1, 49.99),  (9,  13,1, 24.99),
    (10, 6, 1, 119.99),
    (11, 7, 1, 199.99),
    (12, 4, 1, 39.99),
    (13, 5, 1, 69.99);
