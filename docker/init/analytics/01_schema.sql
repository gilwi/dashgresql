-- ============================================================
-- ANALYTICS DATABASE
-- ============================================================

CREATE TABLE apps (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    platform   VARCHAR(50),  -- web, ios, android
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE events (
    id         BIGSERIAL PRIMARY KEY,
    app_id     INT REFERENCES apps(id),
    session_id UUID,
    event_type VARCHAR(100) NOT NULL,  -- page_view, click, purchase, signup…
    user_id    VARCHAR(100),
    properties JSONB,
    country    VARCHAR(100),
    device     VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE daily_metrics (
    id          SERIAL PRIMARY KEY,
    app_id      INT REFERENCES apps(id),
    date        DATE NOT NULL,
    dau         INT,      -- daily active users
    new_users   INT,
    sessions    INT,
    avg_session_duration_sec INT,
    revenue     NUMERIC(10,2)
);

CREATE TABLE funnels (
    id          SERIAL PRIMARY KEY,
    app_id      INT REFERENCES apps(id),
    name        VARCHAR(100) NOT NULL,
    step        INT NOT NULL,
    step_name   VARCHAR(100),
    users_count INT,
    date        DATE
);

-- ── Seed data ────────────────────────────────────────────────

INSERT INTO apps (name, platform) VALUES
    ('ShopApp',    'web'),
    ('ShopApp iOS','ios'),
    ('AdminPortal','web');

-- Daily metrics — last 30 days for each app
INSERT INTO daily_metrics (app_id, date, dau, new_users, sessions, avg_session_duration_sec, revenue)
SELECT
    app_id,
    CURRENT_DATE - (n || ' days')::INTERVAL AS date,
    (400 + random() * 600)::INT,
    (40  + random() * 80)::INT,
    (500 + random() * 800)::INT,
    (120 + random() * 240)::INT,
    (1000 + random() * 4000)::NUMERIC(10,2)
FROM generate_series(1, 30) AS n,
     (VALUES (1), (2), (3)) AS apps(app_id);

-- Funnel data — signup funnel
INSERT INTO funnels (app_id, name, step, step_name, users_count, date) VALUES
    (1, 'Signup Funnel', 1, 'Landing Page',      4800, CURRENT_DATE - 7),
    (1, 'Signup Funnel', 2, 'Registration Form',  2900, CURRENT_DATE - 7),
    (1, 'Signup Funnel', 3, 'Email Verified',     2100, CURRENT_DATE - 7),
    (1, 'Signup Funnel', 4, 'Profile Completed',  1500, CURRENT_DATE - 7),
    (1, 'Signup Funnel', 5, 'First Purchase',      620, CURRENT_DATE - 7),

    (2, 'Signup Funnel', 1, 'App Opened',         3200, CURRENT_DATE - 7),
    (2, 'Signup Funnel', 2, 'Registration Form',  1900, CURRENT_DATE - 7),
    (2, 'Signup Funnel', 3, 'Email Verified',     1400, CURRENT_DATE - 7),
    (2, 'Signup Funnel', 4, 'Profile Completed',   980, CURRENT_DATE - 7),
    (2, 'Signup Funnel', 5, 'First Purchase',      310, CURRENT_DATE - 7);

-- Events sample
INSERT INTO events (app_id, session_id, event_type, user_id, country, device, properties, created_at)
SELECT
    (1 + floor(random() * 2))::INT,
    gen_random_uuid(),
    (ARRAY['page_view','click','add_to_cart','purchase','signup','logout'])[floor(random()*6+1)],
    'user_' || floor(random() * 500 + 1)::TEXT,
    (ARRAY['France','USA','Germany','UK','Italy','Spain','Canada'])[floor(random()*7+1)],
    (ARRAY['desktop','mobile','tablet'])[floor(random()*3+1)],
    jsonb_build_object('value', (random()*200)::NUMERIC(6,2)),
    NOW() - (random() * INTERVAL '30 days')
FROM generate_series(1, 500);
