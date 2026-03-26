-- ============================================================
-- HR DATABASE
-- ============================================================

CREATE TABLE departments (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    location   VARCHAR(100),
    budget     NUMERIC(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE employees (
    id            SERIAL PRIMARY KEY,
    department_id INT REFERENCES departments(id),
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(200) UNIQUE NOT NULL,
    job_title     VARCHAR(150),
    salary        NUMERIC(10,2),
    hire_date     DATE,
    manager_id    INT REFERENCES employees(id),
    active        BOOLEAN DEFAULT TRUE
);

CREATE TABLE leave_requests (
    id          SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(id),
    leave_type  VARCHAR(50),  -- vacation, sick, parental
    start_date  DATE,
    end_date    DATE,
    status      VARCHAR(30) DEFAULT 'pending',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE performance_reviews (
    id          SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(id),
    reviewer_id INT REFERENCES employees(id),
    period      VARCHAR(20),  -- e.g. '2024-Q4'
    score       NUMERIC(3,1), -- 1.0 to 5.0
    notes       TEXT,
    reviewed_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Seed data ────────────────────────────────────────────────

INSERT INTO departments (name, location, budget) VALUES
    ('Engineering',  'Paris',    2500000.00),
    ('Marketing',    'Lyon',      800000.00),
    ('Sales',        'Paris',    1200000.00),
    ('HR',           'Bordeaux',  600000.00),
    ('Finance',      'Paris',     900000.00);

-- Managers first (no manager_id yet)
INSERT INTO employees (department_id, first_name, last_name, email, job_title, salary, hire_date) VALUES
    (1, 'Sophie',  'Bernard', 'sophie.bernard@corp.com',  'VP Engineering',    120000, '2018-03-01'),
    (2, 'Thomas',  'Leroy',   'thomas.leroy@corp.com',    'Marketing Director', 95000, '2019-06-15'),
    (3, 'Camille', 'Petit',   'camille.petit@corp.com',   'Sales Director',    105000, '2017-11-20'),
    (4, 'Marc',    'Dubois',  'marc.dubois@corp.com',     'HR Director',        88000, '2020-01-10'),
    (5, 'Léa',     'Moreau',  'lea.moreau@corp.com',      'CFO',               135000, '2016-09-05');

-- Team members
INSERT INTO employees (department_id, first_name, last_name, email, job_title, salary, hire_date, manager_id) VALUES
    (1, 'Antoine', 'Girard',  'antoine.girard@corp.com',  'Senior Engineer',    82000, '2020-04-01', 1),
    (1, 'Julie',   'Simon',   'julie.simon@corp.com',     'Backend Engineer',   72000, '2021-07-15', 1),
    (1, 'Maxime',  'Laurent', 'maxime.laurent@corp.com',  'Frontend Engineer',  70000, '2022-01-20', 1),
    (1, 'Nina',    'Robert',  'nina.robert@corp.com',     'DevOps Engineer',    78000, '2021-03-10', 1),
    (2, 'Chloé',   'Michel',  'chloe.michel@corp.com',    'Content Manager',    58000, '2021-09-01', 2),
    (2, 'Hugo',    'Garcia',  'hugo.garcia@corp.com',     'SEO Specialist',     54000, '2022-05-15', 2),
    (3, 'Laura',   'Fontaine','laura.fontaine@corp.com',  'Account Executive',  65000, '2020-11-01', 3),
    (3, 'Pierre',  'Blanc',   'pierre.blanc@corp.com',    'Sales Rep',          55000, '2023-02-01', 3),
    (4, 'Sarah',   'Adam',    'sarah.adam@corp.com',      'HR Business Partner',60000, '2022-08-10', 4),
    (5, 'Kevin',   'Roux',    'kevin.roux@corp.com',      'Financial Analyst',  67000, '2021-06-01', 5);

INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, status) VALUES
    (6,  'vacation', '2025-07-01', '2025-07-14', 'approved'),
    (7,  'sick',     '2025-03-10', '2025-03-12', 'approved'),
    (8,  'vacation', '2025-08-04', '2025-08-15', 'pending'),
    (11, 'parental', '2025-05-01', '2025-07-31', 'approved'),
    (13, 'vacation', '2025-06-16', '2025-06-20', 'pending'),
    (14, 'sick',     '2025-03-05', '2025-03-06', 'approved');

INSERT INTO performance_reviews (employee_id, reviewer_id, period, score, notes) VALUES
    (6,  1, '2024-Q4', 4.5, 'Excellent technical leadership.'),
    (7,  1, '2024-Q4', 4.0, 'Great delivery on API project.'),
    (8,  1, '2024-Q4', 3.8, 'Improved UI performance notably.'),
    (9,  1, '2024-Q4', 4.2, 'Solid CI/CD improvements.'),
    (10, 2, '2024-Q4', 3.5, 'Good content output, needs strategy work.'),
    (11, 2, '2024-Q4', 4.0, 'Strong SEO results this quarter.'),
    (12, 3, '2024-Q4', 4.7, 'Top performing AE in the team.'),
    (13, 3, '2024-Q4', 3.2, 'Needs to improve closing rate.'),
    (15, 5, '2024-Q4', 4.1, 'Accurate forecasting, very reliable.');
